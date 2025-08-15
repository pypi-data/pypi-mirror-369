import asyncio
import datetime
import time
from pathlib import Path

from filelock import FileLock
from loguru import logger
from sona.core.messages import Context, File, Job, Result, State
from sona.core.storages import StorageBase
from sona.settings import settings
from sona.utils import get_audio_metadata
from sona.web.webrtc.sessions import MediaInferencerSessionState
from sona.worker.producers import ProducerBase

SHARED_PATH = settings.SONA_STREAM_SIDECAR_SHARED_PATH
SUPERVISOR_TOPICS = settings.SONA_STREAM_SIDECAR_SUPERVISOR_TOPICS


class Scanner:
    def __init__(self, producer: ProducerBase, storage: StorageBase):
        self.today = datetime.date.today().strftime("%Y%m%d")
        self.producer = producer
        self.storage = storage

    async def scan_files(self):
        logger.info(f"Scan shared path: {SHARED_PATH}")
        while True:
            try:
                for file in Path(SHARED_PATH).glob("*.json"):
                    lock = FileLock(f"{file}.lock")
                    with lock:
                        if file.exists():
                            await self.on_process_file(file)
                    Path(f"{file}.lock").unlink(missing_ok=True)
                await asyncio.sleep(60)
            except Exception as e:
                logger.exception(e)

    async def on_process_file(self, file):
        with open(file, "r") as f:
            state = MediaInferencerSessionState.model_validate_json(f.read())
            if state.is_expired():
                await self.on_expired(file, state)
            elif state.is_stop():
                await self.on_stop(file, state)
            elif state.is_timeout():
                await self.on_failed(file, state)
            else:
                await self.on_running(file, state)

    async def on_expired(self, file: Path, state: MediaInferencerSessionState):
        logger.info(f"[{file.name}] Session expired: {state}")
        Path(state.media_path).unlink(missing_ok=True)
        file.unlink(missing_ok=True)

    async def on_running(self, file: Path, state: MediaInferencerSessionState):
        logger.info(f"[{file.name}] Session running: {state}")

        # Avoid pass `None` value from gateway
        application = state.options.get("application", "common") or "common"
        ctx = Context(
            id=state.track_id,
            headers=state.options,
            application=application,
            supervisors=SUPERVISOR_TOPICS,
            jobs=[Job(name=state.job_name, params=state.options)],
            states=[
                State(
                    job_name=state.job_name,
                    node_name=state.node_name,
                    timestamp=state.create_time,
                    exec_time=time.time_ns() - state.create_time,
                )
            ],
        )
        for topic in ctx.supervisors:
            self.producer.emit(topic, ctx.to_message())

    async def on_stop(self, file: Path, state: MediaInferencerSessionState):
        logger.info(f"[{file.name}] Session stop: {state}")

        # Avoid pass `None` value from gateway
        application = state.options.get("application", "common") or "common"
        if Path(state.media_path).exists():
            media_file = File(label="raw", path=state.media_path)
            ctx = Context(
                id=state.track_id,
                headers=state.options,
                application=application,
                supervisors=SUPERVISOR_TOPICS,
                jobs=[Job(name=state.job_name, params=state.options)],
                states=[
                    State(
                        job_name=state.job_name,
                        node_name=state.node_name,
                        timestamp=state.create_time,
                        exec_time=state.update_time - state.create_time,
                    )
                ],
            )
            metadata = get_audio_metadata(media_file.path)
            media_file = self.storage.push(ctx, media_file, metadata)
            ctx = ctx.mutate(results={state.job_name: Result(files=[media_file])})
            for topic in ctx.supervisors:
                self.producer.emit(topic, ctx.to_message())

            Path(state.media_path).unlink(missing_ok=True)
        else:
            logger.warning(f"[{file.name}] media missing: {state.media_path}")
        file.unlink(missing_ok=True)

    async def on_failed(self, file: Path, state: MediaInferencerSessionState):
        logger.info(f"[{file.name}] Session failed: {state}")

        # Avoid pass `None` value from gateway
        application = state.options.get("application", "common") or "common"
        ctx = Context(
            id=state.track_id,
            headers=state.options,
            application=application,
            supervisors=SUPERVISOR_TOPICS,
            jobs=[Job(name=state.job_name, params=state.options)],
            states=[
                State(
                    job_name=state.job_name,
                    node_name=state.node_name,
                    timestamp=state.create_time,
                    exec_time=state.update_time - state.create_time,
                    exception={
                        "message": "Process timeout with unknown error",
                        "traceback": "",
                    },
                )
            ],
        )
        for topic in ctx.supervisors:
            self.producer.emit(topic, ctx.to_message())

        Path(state.media_path).unlink(missing_ok=True)
        file.unlink(missing_ok=True)
