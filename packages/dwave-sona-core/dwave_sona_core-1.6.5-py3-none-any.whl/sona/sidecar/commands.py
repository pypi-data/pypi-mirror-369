import asyncio

import typer
from sona.core.storages import create_storage
from sona.worker.producers import create_producer

from .sidecars import Scanner

app = typer.Typer()


@app.command()
def run():
    producer = create_producer()
    storage = create_storage()
    scanner = Scanner(producer=producer, storage=storage)
    asyncio.run(scanner.scan_files())
