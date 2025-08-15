import shutil
from pathlib import Path

from sona.settings import settings

from .base import StorageBase


class LocalStorage(StorageBase):
    def __init__(
        self,
        local_path=settings.SONA_STORAGE_LOCAL_PATH,
    ):
        super().__init__()
        self.local_path = local_path

    def on_push(self, file, remote_path):
        local_path = Path(self.local_path) / remote_path
        local_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file.path, "rb") as f_in, open(local_path, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)
        return file.mutate(path=str(remote_path))
