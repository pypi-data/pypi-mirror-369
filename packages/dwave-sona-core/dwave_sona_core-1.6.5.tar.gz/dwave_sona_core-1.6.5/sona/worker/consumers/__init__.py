from sona.settings import settings
from sona.worker.consumers.azure import AzuerStorageQueueConsumer

from .base import ConsumerBase
from .kafka import KafkaConsumer
from .redis import RedisConsumer
from .sqs import SQSConsumer


def create_consumer():
    if settings.SONA_WORKER_CONSUMER_AZURE_ENDPOINT:
        return AzuerStorageQueueConsumer()
    if settings.SONA_WORKER_CONSUMER_SQS_SETTING:
        return SQSConsumer()
    if settings.SONA_WORKER_CONSUMER_KAFKA_SETTING:
        return KafkaConsumer()
    if settings.SONA_WORKER_CONSUMER_REDIS_URL:
        return RedisConsumer()
    raise Exception(
        "Consumer settings not found, please set SONA_CONSUMER_KAFKA_SETTING or SONA_CONSUMER_REDIS_URL"
    )
