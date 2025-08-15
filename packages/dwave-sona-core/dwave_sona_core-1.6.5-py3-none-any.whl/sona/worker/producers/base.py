import abc


class ProducerBase:
    @abc.abstractmethod
    def emit(self, topic, message) -> None:
        return NotImplemented
