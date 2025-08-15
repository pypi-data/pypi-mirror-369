import boto3
from sona.settings import settings

from .base import ProducerBase


class SQSProducer(ProducerBase):
    def __init__(self, setting=settings.SONA_WORKER_PRODUCER_SQS_SETTING):
        self.sqs = boto3.resource("sqs", **setting)

    def emit(self, topic, message):
        queue = self.sqs.get_queue_by_name(QueueName=topic)
        queue.send_message(MessageBody=message)
