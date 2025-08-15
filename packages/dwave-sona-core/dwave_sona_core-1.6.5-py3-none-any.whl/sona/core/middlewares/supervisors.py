import datetime
import queue
import threading

import av
import boto3
from loguru import logger
from sona.core.messages.context import Context
from sona.settings import settings

from .base import MiddlewareBase

try:
    from confluent_kafka import Producer
except ImportError:
    Producer = None


MIN_PART_SIZE = 5 * 1024**2
KAFKA_SETTING = settings.SONA_MIDDLEWARE_SUPERVISOR_KAFKA_SETTING
SQS_SETTING = settings.SONA_MIDDLEWARE_SUPERVISOR_SQS_SETTING


class KafkaSupervisor(MiddlewareBase):
    def __init__(self, configs=KAFKA_SETTING):
        if Producer:
            self.producer = Producer(configs)
        else:
            logger.warning(
                "Missing SONA_MIDDLEWARE_SUPERVISOR_KAFKA_SETTING, KafkaSupervisor will be ignored."
            )
            self.producer = None

    def on_context(self, ctx: Context, on_context):
        for topic in ctx.supervisors:
            self._emit(topic, ctx.to_message())
        next_ctx: Context = on_context(ctx)
        for topic in next_ctx.supervisors:
            self._emit(topic, next_ctx.to_message())
        return next_ctx

    def _emit(self, topic, message):
        try:
            if self.producer:
                self.producer.poll(0)
                self.producer.produce(
                    topic, message.encode("utf-8"), callback=self.__delivery_report
                )
                self.producer.flush()
        except Exception as e:
            logger.warning(f"Supervisor emit error occur {e}, ignore message {message}")

    def __delivery_report(self, err, msg):
        if err:
            raise Exception(msg.error())


class SQSSupervisor(MiddlewareBase):
    def __init__(self, setting=SQS_SETTING):
        self.sqs = boto3.resource("sqs", **setting)

    def on_context(self, ctx: Context, on_context):
        for topic in ctx.supervisors:
            self._emit(topic, ctx.to_message())
        next_ctx: Context = on_context(ctx)
        for topic in next_ctx.supervisors:
            self._emit(topic, next_ctx.to_message())
        return next_ctx

    def _emit(self, topic, message):
        try:
            queue = self.sqs.get_queue_by_name(QueueName=topic)
            queue.send_message(MessageBody=message)
        except Exception as e:
            logger.warning(f"Supervisor emit error occur {e}, ignore message {message}")
