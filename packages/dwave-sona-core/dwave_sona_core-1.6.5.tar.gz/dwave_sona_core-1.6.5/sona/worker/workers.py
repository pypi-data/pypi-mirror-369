from __future__ import annotations

import abc
import asyncio

from loguru import logger
from sona.core.inferencer import InferencerBase
from sona.core.messages import Context
from sona.settings import settings
from sona.utils import import_class
from sona.worker.consumers import ConsumerBase
from sona.worker.producers import ProducerBase

TOPIC_PREFIX = settings.SONA_WORKER_TOPIC_PREFIX
TOPIC = settings.SONA_WORKER_TOPIC


class WorkerBase:
    name: str = None

    def set_consumer(self, consumer: ConsumerBase):
        self.consumer = consumer

    def set_producer(self, producer: ProducerBase):
        self.producer = producer

    async def start(self):
        await self.on_load()
        self.topic = self.get_topic()
        logger.info(f"Susbcribe on {self.topic}({self.consumer.__class__.__name__})")
        self.consumer.subscribe(self.topic)
        async for message in self.consumer.consume():
            try:
                context = Context.model_validate_json(message)
                await self.on_context(context)
            except Exception as e:
                logger.exception(f"[{self.topic}] error: {e}, msg: {message}")

    @classmethod
    def get_topic(cls) -> str:
        return TOPIC or f"{TOPIC_PREFIX}{cls.name}"

    @classmethod
    def load_class(cls, import_str):
        _cls = import_class(import_str)
        if _cls not in cls.__subclasses__():
            raise Exception(f"Unknown worker class: {import_str}")
        return _cls

    # Callbacks
    @abc.abstractmethod
    async def on_load(self) -> None:
        return NotImplemented

    @abc.abstractmethod
    async def on_context(self, message: Context) -> Context:
        return NotImplemented


class InferencerWorker(WorkerBase):
    def __init__(self, inferencer: InferencerBase):
        super().__init__()
        self.inferencer = inferencer
        inferencer.setup()

    async def on_load(self):
        logger.info(f"Loading inferencer: {self.inferencer.name}")
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, self.inferencer.on_load)

    async def on_context(self, ctx: Context):
        loop = asyncio.get_running_loop()
        next_ctx: Context = await loop.run_in_executor(
            None, self.inferencer.on_context, ctx
        )
        if next_ctx.is_failed:
            for topic in next_ctx.fallbacks:
                self.producer.emit(topic, next_ctx.to_message())
        else:
            next_job = next_ctx.current_job
            if next_job:
                self.producer.emit(next_job.topic, next_ctx.to_message())
            else:
                for topic in next_ctx.reporters:
                    self.producer.emit(topic, next_ctx.to_message())

    def get_topic(self):
        return TOPIC or f"{TOPIC_PREFIX}{self.inferencer.name}"
