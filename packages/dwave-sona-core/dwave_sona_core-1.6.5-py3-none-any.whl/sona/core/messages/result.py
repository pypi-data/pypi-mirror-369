from __future__ import annotations

from typing import Dict, List

from .base import MessageBase
from .file import File


class Result(MessageBase):
    files: List[File] = []
    data: Dict = {}

    def find_file(self, label) -> File:
        for file in self.files:
            if file.label == label:
                return file
        return None
