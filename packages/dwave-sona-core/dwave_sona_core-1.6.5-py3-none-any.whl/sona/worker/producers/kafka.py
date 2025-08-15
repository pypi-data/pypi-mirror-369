from sona.settings import settings

from .base import ProducerBase

try:
    from confluent_kafka import Producer
except ImportError:
    pass

PRODUCER_SETTING = settings.SONA_WORKER_PRODUCER_KAFKA_SETTING


class KafkaProducer(ProducerBase):
    def __init__(self, configs=PRODUCER_SETTING):
        self.producer = Producer(configs)

    def emit(self, topic, message):
        self.producer.poll(0)
        self.producer.produce(
            topic, message.encode("utf-8"), callback=self.__delivery_report
        )
        self.producer.flush()

    def __delivery_report(self, err, msg):
        if err:
            raise Exception(msg.error())
