import re
from pathlib import Path
from google.cloud import storage
from google.oauth2 import service_account
from sona.settings import settings

from .base import SourceBase


class GCSSource(SourceBase):
    credential = settings.SONA_STORAGE_GOOGLE_CREDENTIAL

    @classmethod
    def client(cls):
        credentials = service_account.Credentials.from_service_account_info(
            cls.credential
        )
        return storage.Client(credentials=credentials)

    @classmethod
    def download(cls, file):
        match = re.match(r"gcs://([-_\w]+)/(.+)", file.path)
        bucket = match.group(1)
        obj_key = match.group(2)

        filename = Path(obj_key).name
        tmp_path = cls.tmp_dir / filename

        bucket = cls.client().bucket(bucket)
        blob = bucket.blob(obj_key)
        blob.download_to_filename(tmp_path)

        return file.mutate(path=str(tmp_path))

    @classmethod
    def verify(cls, file):
        return file.path and file.path.startswith("gcs://")
