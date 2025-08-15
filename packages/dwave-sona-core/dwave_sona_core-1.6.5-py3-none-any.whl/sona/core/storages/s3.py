import boto3
from botocore.client import Config
from sona.settings import settings

from .base import StorageBase


class S3Storage(StorageBase):
    def __init__(
        self,
        bucket=settings.SONA_STORAGE_S3_BUCKET,
        configs=settings.SONA_STORAGE_S3_SETTING,
    ):
        super().__init__()
        self.bucket = bucket
        self.configs = configs

    @property
    def client(self):
        configs = self.configs or {}
        configs.update({"config": Config(signature_version="s3v4")})
        return boto3.resource("s3", **configs).meta.client

    def on_push(self, file, remote_path):
        self.client.upload_file(
            file.path,
            self.bucket,
            remote_path,
            ExtraArgs={"Metadata": file.metadata.get("s3", {})},
        )
        return file.mutate(path=f"S3://{self.bucket}/{remote_path}")
