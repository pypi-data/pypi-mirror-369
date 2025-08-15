import re
from pathlib import Path

import boto3
from botocore.client import Config
from sona.settings import settings

from .base import SourceBase


class S3Source(SourceBase):
    setting = settings.SONA_STORAGE_S3_SETTING

    @classmethod
    def get_client(cls):
        configs = cls.setting or {}
        configs.update({"config": Config(signature_version="s3v4")})
        s3 = boto3.resource("s3", **configs)

        return s3.meta.client

    @classmethod
    def download(cls, file):
        match = re.match(r"[Ss]3://([-_\w]+)/(.+)", file.path)
        bucket = match.group(1)
        obj_key = match.group(2)

        filename = Path(obj_key).name
        tmp_path = cls.tmp_dir / filename

        s3client = cls.get_client()
        s3client.download_file(bucket, obj_key, str(tmp_path))
        metadata = s3client.head_object(Bucket=bucket, Key=obj_key).get("Metadata", {})
        return file.mutate(
            path=str(tmp_path), metadata={"s3": metadata, **file.metadata}
        )

    @classmethod
    def verify(cls, file):
        return (
            file.path and file.path.startswith("s3://") or file.path.startswith("S3://")
        )
