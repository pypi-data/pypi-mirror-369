from google.cloud import storage
from google.oauth2 import service_account
from sona.settings import settings

from .base import StorageBase


class GCSStorage(StorageBase):
    def __init__(
        self,
        bucket=settings.SONA_STORAGE_GOOGLE_BUCKET,
        credential=settings.SONA_STORAGE_GOOGLE_CREDENTIAL,
    ):
        super().__init__()
        self.bucket = bucket
        self.credential = credential

    @property
    def client(self):
        credentials = service_account.Credentials.from_service_account_info(self.credential)
        return storage.Client(credentials=credentials)

    def on_push(self, file, remote_path):
        bucket = self.client.bucket(self.bucket)
        blob = bucket.blob(remote_path)
        blob.upload_from_filename(file.path)
        return file.mutate(path=f"gcs://{self.bucket}/{remote_path}")
