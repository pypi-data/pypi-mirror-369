import re
from pathlib import Path

from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
from sona.settings import settings

from .base import SourceBase


class AzureBlobSource(SourceBase):
    endpoint = settings.SONA_STORAGE_AZURE_ENDPOINT
    account_name = settings.SONA_STORAGE_AZURE_ACCOUNT_NAME
    account_key = settings.SONA_STORAGE_AZURE_ACCOUNT_KEY
    container = settings.SONA_STORAGE_AZURE_CONTAINER

    @classmethod
    def get_client(cls):
        return BlobServiceClient(
            account_url=cls.endpoint,
            credential={
                "account_name": cls.account_name,
                "account_key": cls.account_key,
            },
        )

    @classmethod
    def download(cls, file):
        match = re.match(r"azblob://([-_\w]+)/(.+)", file.path)
        container = match.group(1)
        obj_key = match.group(2)

        filename = Path(obj_key).name
        tmp_path = cls.tmp_dir / filename

        container_client = cls.get_client().get_container_client(container=container)
        with open(file=tmp_path, mode="wb") as download_file:
            download_file.write(container_client.download_blob(obj_key).readall())
        return file.mutate(path=str(tmp_path))

    @classmethod
    def verify(cls, file):
        return file.path and file.path.startswith("azblob://")
