from azure.storage.queue import QueueClient
from sona.settings import settings

from .base import ProducerBase


class AzuerStorageQueueProducer(ProducerBase):
    def __init__(
        self,
        endpoint=settings.SONA_WORKER_PRODUCER_AZURE_ENDPOINT,
        account_name=settings.SONA_WORKER_PRODUCER_AZURE_ACCOUNT_NAME,
        account_key=settings.SONA_WORKER_PRODUCER_AZURE_ACCOUNT_KEY,
    ):
        self.queue = None
        self.endpoint = endpoint
        self.account_name = account_name
        self.account_key = account_key

    def emit(self, topic, message):
        queue = QueueClient(
            account_url=self.endpoint,
            credential={
                "account_name": self.account_name,
                "account_key": self.account_key,
            },
            queue_name=topic,
        )
        queue.send_message(message)
