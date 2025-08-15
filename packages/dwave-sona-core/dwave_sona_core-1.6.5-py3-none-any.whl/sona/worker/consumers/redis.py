import uuid

from loguru import logger
from sona.settings import settings

from .base import ConsumerBase

try:
    import redis.asyncio as redis
    from redis.exceptions import ResponseError
except ImportError:
    pass

REDIS_URL = settings.SONA_WORKER_CONSUMER_REDIS_URL
CONSUMER_GROUP = settings.SONA_WORKER_CONSUMER_REDIS_GROUP


class RedisConsumer(ConsumerBase):
    def __init__(self, url=REDIS_URL):
        self.topics = []
        self.redis = redis.from_url(url)
        self.client_id = str(uuid.uuid4())

    def subscribe(self, topic):
        self.topics += [topic]

    async def consume(self):
        for topic in self.topics:
            try:
                await self.redis.xgroup_create(
                    topic, CONSUMER_GROUP, id="0", mkstream=True
                )
            except ResponseError as e:
                logger.warning(e)

        while True:
            stream_list = {topic: ">" for topic in self.topics}
            streams = await self.redis.xreadgroup(
                CONSUMER_GROUP, self.client_id, stream_list, block=1000 * 60, noack=True
            )
            for _stream_key, stream in streams:
                for _id, message in stream:
                    if message is not None:
                        yield message[b"data"].decode()
