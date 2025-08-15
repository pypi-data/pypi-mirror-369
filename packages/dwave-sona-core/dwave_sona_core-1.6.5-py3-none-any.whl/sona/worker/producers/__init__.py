from sona.settings import settings

from .azure import AzuerStorageQueueProducer
from .base import ProducerBase
from .kafka import KafkaProducer
from .redis import RedisProducer
from .sqs import SQSProducer


def create_producer():
    if settings.SONA_WORKER_PRODUCER_AZURE_ENDPOINT:
        return AzuerStorageQueueProducer()
    if settings.SONA_WORKER_PRODUCER_SQS_SETTING:
        return SQSProducer()
    if settings.SONA_WORKER_PRODUCER_KAFKA_SETTING:
        return KafkaProducer()
    if settings.SONA_WORKER_PRODUCER_REDIS_URL:
        return RedisProducer()
    raise Exception(
        "Producer settings not found, please set SONA_PRODUCER_KAFKA_SETTING or SONA_PRODUCER_REDIS_URL"
    )
