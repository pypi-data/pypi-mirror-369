import shutil
from pathlib import Path

from sona.settings import settings

from .base import SourceBase


class LocalSource(SourceBase):
    root_dir = settings.SONA_STORAGE_LOCAL_PATH

    @classmethod
    def download(cls, file):
        filepath = Path(cls.root_dir) / file.path
        tmp_path = cls.tmp_dir / filepath.name

        with open(filepath, "rb") as f_in, open(tmp_path, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)
        return file.mutate(path=str(tmp_path))

    @classmethod
    def verify(cls, file):
        if not file.path:
            return False
        filepath = Path(cls.root_dir) / file.path
        return Path(filepath).is_file()
