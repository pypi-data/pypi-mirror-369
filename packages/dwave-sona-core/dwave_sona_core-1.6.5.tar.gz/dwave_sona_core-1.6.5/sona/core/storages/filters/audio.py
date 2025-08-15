from pathlib import Path

from sona.core.messages import File


class AudioNormalizer:
    audio_fomats = [
        ".wav",
        ".mp3",
        ".flac",
        ".aac",
        ".opus",
        ".wma",
        ".amr",
        ".m4a",
    ]
    video_formats = [".mp4", ".mkv", ".mov", ".avi", "wmv"]

    def decode(self, file: File):
        filepath = Path(file.path)
        if filepath.suffix in self.audio_fomats + self.video_formats:
            return file.to_wav()
        return file

    def encode(self, file: File):
        filepath = Path(file.path)
        if filepath.suffix in [".wav"]:
            return file.to_flac()
        return file
