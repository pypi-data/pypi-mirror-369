import typer
import asyncio
from hypercorn.config import Config
from hypercorn.asyncio import serve

from .server import app as webapp

app = typer.Typer()


@app.command()
def run(host: str = "0.0.0.0", port: int = 8080):
    config = Config()
    config.bind = [f"{host}:{port}"]
    asyncio.run(serve(webapp, config))
