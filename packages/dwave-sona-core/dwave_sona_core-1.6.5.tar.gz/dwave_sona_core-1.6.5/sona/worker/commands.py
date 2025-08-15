import asyncio

import typer
from loguru import logger
from sona.core.inferencer import InferencerBase
from sona.core.messages.context import Context
from sona.settings import settings
from sona.worker.consumers import create_consumer
from sona.worker.producers import create_producer
from sona.worker.workers import InferencerWorker, WorkerBase

INFERENCER_CLASS: str = settings.SONA_INFERENCER_CLASS
WORKER_CLASS: str = settings.SONA_WORKER_CLASS

app = typer.Typer()


@app.command()
def run():
    try:
        worker_cls = WorkerBase.load_class(WORKER_CLASS)
        if worker_cls == InferencerWorker:
            inferencer: InferencerBase = InferencerBase.load_class(INFERENCER_CLASS)()
            worker: WorkerBase = worker_cls(inferencer)
        else:
            worker: WorkerBase = worker_cls()
        worker.set_producer(create_producer())
        worker.set_consumer(create_consumer())
        asyncio.run(worker.start())
    except Exception as e:
        logger.exception(e)


@app.command()
def test_produce(queue_name):
    producer = create_producer()
    producer.emit(queue_name, Context(jobs=[]).to_message())


@app.command()
def test_consume(queue_name):
    asyncio.run(test_consume_task(queue_name))


async def test_consume_task(queue_name):
    consumer = create_consumer()
    consumer.subscribe(queue_name)
    async for message in consumer.consume():
        print(Context.model_validate_json(message))
