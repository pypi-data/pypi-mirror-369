import abc


class ConsumerBase:
    @abc.abstractmethod
    def subscribe(self, topic: str) -> None:
        return NotImplemented

    @abc.abstractmethod
    async def consume(self) -> str:
        return NotImplemented
