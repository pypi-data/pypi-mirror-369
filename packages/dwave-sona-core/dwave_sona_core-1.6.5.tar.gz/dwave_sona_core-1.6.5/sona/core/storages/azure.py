from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
from sona.settings import settings

from .base import StorageBase


class AzureBlobStorage(StorageBase):
    def __init__(
        self,
        endpoint=settings.SONA_STORAGE_AZURE_ENDPOINT,
        account_name=settings.SONA_STORAGE_AZURE_ACCOUNT_NAME,
        account_key=settings.SONA_STORAGE_AZURE_ACCOUNT_KEY,
        container=settings.SONA_STORAGE_AZURE_CONTAINER,
    ):
        super().__init__()
        self.endpoint = endpoint
        self.account_name = account_name
        self.account_key = account_key
        self.container = container

    @property
    def client(self):
        return BlobServiceClient(
            account_url=self.endpoint,
            credential={
                "account_name": self.account_name,
                "account_key": self.account_key,
            },
        )

    def on_push(self, file, remote_path):
        blob = self.client.get_blob_client(container=self.container, blob=remote_path)
        with open(file=file.path, mode="rb") as data:
            blob.upload_blob(data, overwrite=True)
        return file.mutate(path=f"azblob://{self.container}/{remote_path}")
