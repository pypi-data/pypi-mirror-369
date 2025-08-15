import asyncio
import socket
import time
from pathlib import Path

from aiortc import MediaStreamTrack, RTCDataChannel, RTCPeerConnection, RTCSctpTransport
from aiortc.contrib.media import MediaBlackhole, MediaRecorder, MediaRelay
from aiortc.mediastreams import MediaStreamError
from loguru import logger
from pydantic import BaseModel, Field
from sona.core.stream.inferencer import StreamInferencerBase
from sona.core.stream.messages.context import EvtType, StreamContext
from sona.settings import settings
from sona.web.webrtc.tracks import AudioInferencerTrack

DEBUG = settings.SONA_DEBUG
STREAM_INFERENCER_CLASS = settings.SONA_STREAM_INFERENCER_CLASS
SHARED_PATH = settings.SONA_STREAM_SIDECAR_SHARED_PATH

relay = MediaRelay()


class MediaInferencerSessionState(BaseModel):
    track_id: str
    options: dict
    node_name: str = socket.gethostname()
    job_name: str = ""
    media_path: str = None
    status: str = "pending"
    create_time: int = Field(default_factory=time.time_ns)
    update_time: int = Field(default_factory=time.time_ns)

    def is_expired(self):
        return (
            self.status == "pending"
            and self.update_time + 1 * 60 * (10**9) < time.time_ns()
        )

    def is_timeout(self):
        return (
            self.status == "running"
            and self.update_time + 4 * 60 * 60 * (10**9) < time.time_ns()
        )

    def is_failed(self, system_setup_time):
        return self.status == "running" and self.update_time < system_setup_time

    def is_stop(self):
        return self.status == "stop"

    def change_state(self, status):
        if self.status == "running":
            if status in ["pending"]:
                return
        if self.status == "stop":
            if status in ["pending", "running"]:
                return
        self.status = status
        self.update_time = time.time_ns()
        if SHARED_PATH:
            with open(str(Path(SHARED_PATH) / f"{self.track_id}.json"), "w") as f:
                f.write(self.model_dump_json())


class MediaInferencerSession:
    track: MediaStreamTrack
    recorder: MediaRecorder = MediaBlackhole()
    inferencer: StreamInferencerBase = None
    reply_track: AudioInferencerTrack = None
    datachannel: RTCDataChannel = None
    runner_task: asyncio.Task = None
    state: MediaInferencerSessionState = None

    def __init__(
        self, track: MediaStreamTrack, peer: RTCPeerConnection, options: dict = None
    ):
        self.track = track
        self.state = MediaInferencerSessionState(
            track_id=self.track.id,
            options=options or {},
        )
        if SHARED_PATH:
            self.state.media_path = str(Path(SHARED_PATH) / f"{self.track.id}.mp3")
            self.recorder = MediaRecorder(self.state.media_path)
            self.recorder.addTrack(relay.subscribe(self.track))

        self.inferencer = StreamInferencerBase.load_class(STREAM_INFERENCER_CLASS)(
            **options
        )
        self.inferencer.setup()
        self.inferencer.on_load()
        self.state.job_name = f"{self.inferencer.name}_stream"

        self.track = relay.subscribe(self.track)
        self.datachannel = peer.createDataChannel(f"{self.track.id}")

        self.reply_track = AudioInferencerTrack()
        peer.addTrack(self.reply_track)
        self.state.change_state("pending")

    @property
    def is_stop(self):
        return self.state.is_stop()

    async def start(self):
        self.runner_task = asyncio.create_task(self.run_track())
        await self.recorder.start()
        self.state.change_state("running")

    async def run_track(self):
        try:
            while self.track.readyState != "ended":
                headers = self.state.options
                frame = await asyncio.wait_for(self.track.recv(), timeout=60.0)
                if DEBUG:
                    logger.info(f"{headers}, {frame}")
                ctx = StreamContext(
                    event_type=EvtType.AV_AUDIO, payload=frame, header=headers
                )
                self.inferencer.on_context(ctx)
        except MediaStreamError as e:
            logger.warning(e)
            await self.stop()
        except Exception as e:
            logger.exception(e)
            await self.stop()

    async def stop(self):
        self.inferencer.on_stop()
        await self.recorder.stop()
        self.state.change_state("stop")

    async def send_audio(self, data):
        self.reply_track.reply(data)

    async def send_data(self, data):
        if self.datachannel.readyState not in ["closing", "closed"]:
            self.datachannel.send(data)
            transport: RTCSctpTransport = self.datachannel.transport
            await transport._data_channel_flush()
            await transport._transmit()
