from .base import SourceBase
from .youtube import YoutubeSource

try:
    import wget
except ImportError:
    pass


class HttpSource(SourceBase):
    @classmethod
    def download(cls, file):
        return file.mutate(path=wget.download(file.path, out=str(cls.tmp_dir)))

    @classmethod
    def verify(cls, file):
        if not file.path:
            return False

        is_youtube_link = YoutubeSource.verify(file)
        if is_youtube_link:
            return False

        is_http = file.path.startswith("http://")
        is_https = file.path.startswith("https://")
        if_ftp = file.path.startswith("ftp://")
        return is_http or is_https or if_ftp
