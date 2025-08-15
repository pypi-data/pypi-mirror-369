import asyncio

from loguru import logger
from sona.settings import settings

from .base import ConsumerBase

try:
    from confluent_kafka import Consumer, TopicPartition
except ImportError:
    pass

CONSUMER_SETTING = settings.SONA_WORKER_CONSUMER_KAFKA_SETTING


class KafkaConsumer(ConsumerBase):
    def __init__(self, configs=CONSUMER_SETTING):
        self.consumer = Consumer(configs)

    def subscribe(self, topic):
        self.consumer.subscribe([topic])

    async def consume(self):
        loop = asyncio.get_running_loop()
        while True:
            msg = await loop.run_in_executor(None, self.consumer.poll, 1)
            if not msg:
                continue
            if msg.error():
                logger.warning(f"kafka error: {msg.error()}")
                continue
            self.consumer.pause(
                [TopicPartition(msg.topic(), msg.partition(), msg.offset())]
            )
            self.consumer.commit()
            self.consumer.resume(
                [TopicPartition(msg.topic(), msg.partition(), msg.offset())]
            )
            yield msg.value()
