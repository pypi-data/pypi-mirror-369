import asyncio
import json
from typing import Dict

from aiortc import MediaStreamTrack, RTCPeerConnection
from sona.core.stream.messages.context import EvtType

from .sessions import MediaInferencerSession


class MediaInferencerHandler:
    def __init__(self) -> None:
        self.state = "running"
        self.sessions: Dict[str, MediaInferencerSession] = {}
        self.queue = asyncio.Queue()

    def addTrack(
        self, track: MediaStreamTrack, peer: RTCPeerConnection, options: dict = None
    ):
        session = MediaInferencerSession(track, peer, options)
        session.inferencer.on_reply = lambda ctx: self.queue.put_nowait((track.id, ctx))
        self.sessions[track.id] = session

    @property
    def live_sessions(self):
        return [session for session in self.sessions.values() if not session.is_stop]

    async def start(self):
        self.task = asyncio.create_task(self.on_reply())
        for session in self.sessions.values():
            await session.start()

    async def stop(self, track_id: str):
        await self.sessions[track_id].stop()

    async def stop_all(self):
        for session in self.sessions.values():
            await session.stop()

    async def close(self):
        self.state = "close"

    async def on_reply(self):
        while self.state == "running":
            track_id, ctx = await self.queue.get()
            session = self.sessions[track_id]
            if ctx.event_type == EvtType.AV_AUDIO.value:
                await session.send_audio(ctx.payload)
            elif ctx.event_type == EvtType.DICT.value:
                await session.send_data(json.dumps(ctx.payload))
            else:
                raise Exception(
                    "Only support AVAudioStreamData / DictStreamData for now"
                )
