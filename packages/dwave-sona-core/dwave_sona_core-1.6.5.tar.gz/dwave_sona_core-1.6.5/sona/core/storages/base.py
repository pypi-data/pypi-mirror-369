import datetime
from pathlib import Path
from typing import Dict, List, Set

from sona.core.messages import Context, File
from sona.utils import md5_content_hex, md5_hex

from .filters.audio import AudioNormalizer
from .sources import *

normalizer = AudioNormalizer()


class StorageBase:
    def __init__(self):
        self.cached_path: Dict[str, Set] = {}

    def pull_all(self, context_id, files: List[File]) -> List[File]:
        pulled_files = [self.pull(context_id, file) for file in files]
        pulled_files = [normalizer.decode(file) for file in pulled_files]
        if self.cached_path.get(context_id):
            self.cached_path[context_id].update(set(file.path for file in pulled_files))
        return pulled_files

    def pull(self, context_id: str, file: File) -> File:
        for kls in SourceBase.__subclasses__():
            if kls.verify(file):
                kls.tmp_dir.mkdir(parents=True, exist_ok=True)
                local_file = kls.download(file)
                break
        else:
            raise Exception("Invalid sona file path")
        cached_path = self.cached_path.get(context_id, set())
        cached_path.add(local_file.path)
        self.cached_path[context_id] = cached_path
        return local_file

    def push_all(
        self, context: Context, files: List[File], metadata=None
    ) -> List[File]:
        pushed_files = [normalizer.encode(file) for file in files]
        return [self.push(context, file, metadata) for file in pushed_files]

    def push(self, context: Context, file: File, metadata=None) -> File:
        metadata = metadata or {}
        if not Path(file.path).is_file():
            raise Exception(f"Missing file: {file}")
        file = file.mutate(metadata={**metadata, **file.metadata})
        filename = md5_content_hex(file.path)
        filename = md5_hex(filename + str(metadata))
        filename = f"{filename}{''.join(Path(file.path).suffixes)}"

        today = datetime.date.today().strftime("%Y%m%d")
        application = context.application
        remote_path = str(Path("storage") / application / today / filename)
        cached_path = self.cached_path.get(context.id, set())
        cached_path.add(file.path)
        self.cached_path[context.id] = cached_path

        return self.on_push(file, remote_path)

    def clean_all(self) -> None:
        for context_id in self.cached_path:
            self.clean(context_id)

    def clean(self, context_id) -> None:
        for path in self.cached_path.get(context_id, set()):
            file_path = Path(path)
            if file_path.exists():
                file_path.unlink()

    # Callbacks
    def on_push(self, file: File, remote_path: str) -> File:
        return NotImplemented
