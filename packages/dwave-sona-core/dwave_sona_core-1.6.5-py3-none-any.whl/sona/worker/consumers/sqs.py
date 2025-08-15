import asyncio
import functools

import boto3
from sona.settings import settings

from .base import ConsumerBase


class SQSConsumer(ConsumerBase):
    def __init__(self, setting=settings.SONA_WORKER_CONSUMER_SQS_SETTING):
        self.sqs = boto3.resource("sqs", **setting)
        self.queue = None

    def subscribe(self, topic):
        self.queue = self.sqs.get_queue_by_name(QueueName=topic)

    async def consume(self):
        loop = asyncio.get_running_loop()
        while True:
            messages = await loop.run_in_executor(
                None,
                functools.partial(
                    self.queue.receive_messages,
                    AttributeNames=["ApproximateReceiveCount"],
                    MaxNumberOfMessages=1,
                    WaitTimeSeconds=20,
                ),
            )
            if len(messages) <= 0:
                continue
            for message in messages:
                body = message.body
                yield body
                message.delete()
