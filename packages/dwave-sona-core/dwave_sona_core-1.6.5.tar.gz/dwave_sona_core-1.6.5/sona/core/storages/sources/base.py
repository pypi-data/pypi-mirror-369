import os
from pathlib import Path

from sona.core.messages import File


class SourceBase:
    tmp_dir = Path(os.getcwd()) / "_tmp"

    @classmethod
    def download(cls, file: File) -> File:
        return None

    @classmethod
    def verify(cls, file: File) -> bool:
        return False
