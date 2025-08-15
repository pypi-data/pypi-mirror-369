import wave
from pathlib import Path
from typing import Dict

from sona.utils import convert_audio

from .base import MessageBase


class File(MessageBase):
    label: str
    path: str
    metadata: Dict = {}

    def to_wav(self, *args, **kwargs):
        file_path = Path(self.path)
        if file_path.suffix == ".wav":
            return self
        file_path = convert_audio(file_path, "wav", format="s16")
        metadata = {}
        with wave.open(file_path, "rb") as w:
            metadata["OrigFilename"] = Path(self.path).name
            metadata["Channel"] = "stereo" if w.getnchannels() == 2 else "mono"
            metadata["Duration"] = float(w.getnframes()) / float(w.getframerate())
            metadata["Samplerate"] = w.getframerate()
        Path(self.path).unlink(missing_ok=True)
        return self.mutate(
            path=file_path, metadata={"audio": metadata, **self.metadata}
        )

    def to_flac(self, *args, **kwargs):
        file_path = Path(self.path)
        if file_path.suffix == ".flac":
            return self
        file_path = convert_audio(file_path, "flac")
        Path(self.path).unlink(missing_ok=True)
        return self.mutate(path=file_path)

    def delete(self):
        Path(self.path).unlink(missing_ok=True)
