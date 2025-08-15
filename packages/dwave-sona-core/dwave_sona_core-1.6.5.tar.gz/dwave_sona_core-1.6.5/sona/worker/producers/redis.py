from sona.settings import settings

from .base import ProducerBase

try:
    import redis
except ImportError:
    pass

REDIS_URL = settings.SONA_WORKER_PRODUCER_REDIS_URL


class RedisProducer(ProducerBase):
    def __init__(self, url=REDIS_URL):
        self.redis = redis.from_url(url)

    def emit(self, topic, message):
        self.redis.xadd(topic, {"data": message}, maxlen=20)
