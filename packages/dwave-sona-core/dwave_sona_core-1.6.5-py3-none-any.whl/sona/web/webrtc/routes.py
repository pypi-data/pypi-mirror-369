import os
import itertools
from pathlib import Path
from typing import Set

import aiohttp
from aiortc import (
    RTCConfiguration,
    RTCIceServer,
    RTCPeerConnection,
    RTCSessionDescription,
)
from fastapi import HTTPException
from fastapi.staticfiles import StaticFiles
from loguru import logger
from sona.core.messages.result import Result
from sona.settings import settings
from sona.web.messages import RPCOfferRequest, SonaResponse

from .handlers import MediaInferencerHandler

STATIC_ROOT = os.path.dirname(__file__)
PROCESS_LIMIT = settings.SONA_STREAM_PROCESS_LIMIT
SHARED_PATH = settings.SONA_STREAM_SIDECAR_SHARED_PATH

RTC_AUTH_URL = settings.SONA_STREAM_RTC_STUNNER_AUTH_URL
RTC_TURN_FDQN = settings.SONA_STREAM_RTC_TURN_FDQN
RTC_USER = settings.SONA_STREAM_RTC_USER
RTC_PASS = settings.SONA_STREAM_RTC_PASS


hendlers: Set[MediaInferencerHandler] = set()


async def retrieve_ice_servers():
    servers = [RTCIceServer("stun:stun.l.google:19302")]
    if RTC_AUTH_URL:
        async with aiohttp.request("GET", RTC_AUTH_URL) as resp:
            assert resp.status == 200
            result = await resp.json()
            servers += [
                RTCIceServer(**ice_server) for ice_server in result["iceServers"]
            ]
    if RTC_TURN_FDQN:
        servers += [RTCIceServer(RTC_TURN_FDQN, RTC_USER, RTC_PASS)]
    return servers


def get_live_session_count():
    if SHARED_PATH:
        return len(list(Path(SHARED_PATH).glob("*.json")))
    return len(list(itertools.chain(handler.sessions for handler in hendlers)))

def create_peer(ice_servers):
    live_session_count = get_live_session_count()
    logger.info(f"Current live sessions before creating peer: {live_session_count}")
    if live_session_count < PROCESS_LIMIT:
        peer = RTCPeerConnection(configuration=RTCConfiguration(ice_servers))
        return peer
    raise HTTPException(
        status_code=429,
        detail=f"Too many inference sessions (sessions: {live_session_count}, limit: {PROCESS_LIMIT})",
    )

def add_routes(app):
    if SHARED_PATH:
        Path(SHARED_PATH).mkdir(parents=True, exist_ok=True)

    app.mount("/static", StaticFiles(directory=f"{STATIC_ROOT}/static"), name="static")

    @app.post("/offer")
    async def offer(req: RPCOfferRequest):
        logger.info(f"Recive offer: {req}")
        ice_servers = await retrieve_ice_servers()
        peer = create_peer(ice_servers)

        handler = MediaInferencerHandler()
        hendlers.add(handler)

        @peer.on("datachannel")
        def on_datachannel(channel):
            @channel.on("message")
            def on_message(message):
                if isinstance(message, str) and message.startswith("ping"):
                    logger.info(f"Recive message: {message}")
                    channel.send("pong" + message[4:])

        @peer.on("connectionstatechange")
        async def on_connectionstatechange():
            logger.info(f"Connection state is {peer.connectionState}")
            if peer.connectionState in ["connected"]:
                await handler.start()
            if peer.connectionState in ["failed", "closed"]:
                logger.info(f"Close peer {peer}")
                hendlers.discard(handler)
                await handler.close()
                await peer.close()

        @peer.on("track")
        def on_track(track):
            logger.info(f"Track({track.kind}) {track.id} received")
            if track.kind == "audio":
                handler.addTrack(track, peer, req.options)
            elif track.kind == "video":
                pass

            @track.on("ended")
            async def on_ended():
                logger.info(f"Track({track.kind}) {track.id} ended")
                hendlers.discard(handler)
                await handler.stop(track.id)

        await peer.setRemoteDescription(
            RTCSessionDescription(sdp=req.sdp, type=req.type)
        )
        await peer.setLocalDescription(await peer.createAnswer())

        return SonaResponse(
            result=Result(
                data={
                    "sdp": peer.localDescription.sdp,
                    "type": peer.localDescription.type,
                    "ice_servers": ice_servers,
                }
            )
        )
