from azure.storage.queue.aio import QueueClient
from sona.settings import settings

from .base import ConsumerBase


class AzuerStorageQueueConsumer(ConsumerBase):
    def __init__(
        self,
        endpoint=settings.SONA_WORKER_CONSUMER_AZURE_ENDPOINT,
        account_name=settings.SONA_WORKER_CONSUMER_AZURE_ACCOUNT_NAME,
        account_key=settings.SONA_WORKER_CONSUMER_AZURE_ACCOUNT_KEY,
    ):
        self.queue = None
        self.endpoint = endpoint
        self.account_name = account_name
        self.account_key = account_key

    def subscribe(self, topic):
        self.queue = QueueClient(
            account_url=self.endpoint,
            credential={
                "account_name": self.account_name,
                "account_key": self.account_key,
            },
            queue_name=topic,
        )

    async def consume(self):
        while True:
            message = await self.queue.receive_message()
            if not message:
                continue
            yield message.content
            await self.queue.delete_message(message)
