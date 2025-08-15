from .base import SourceBase
import re

try:
    import yt_dlp
except ImportError:
    pass


class YoutubeSource(SourceBase):
    ydl_opts = {
        "quiet": True,
        "outtmpl": f"{str(SourceBase.tmp_dir)}/%(title)s",
        "format": "bestaudio/best",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "lossless",
            }
        ],
    }

    @classmethod
    def download(cls, file):
        with yt_dlp.YoutubeDL(cls.ydl_opts) as ydl:
            info = ydl.extract_info(file.path, download=True)
            filepath = ydl.prepare_filename(info)
            return file.mutate(path=filepath + ".wav")

    @classmethod
    def verify(cls, file):
        return re.fullmatch(
            r"^((?:https?:)?\/\/)?((?:www|m)\.)?((?:youtube(-nocookie)?\.com|youtu.be))(\/(?:[\w\-]+\?v=|embed\/|live\/|shorts\/|v\/)?)([\w\-]+)(\S+)?$",
            file.path,
        )
