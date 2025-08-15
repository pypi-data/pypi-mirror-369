import time

import av
import typer
from sona.core.inferencer import InferencerBase
from sona.core.messages.context import Context
from sona.core.messages.file import File
from sona.core.storages import create_storage
from sona.core.stream.inferencer import StreamInferencerBase
from sona.core.stream.messages.context import EvtType, StreamContext

app = typer.Typer()


@app.command()
def test(inferencer_cls: str):
    inferencer: InferencerBase = InferencerBase.load_class(inferencer_cls)()
    inferencer.setup()
    inferencer.on_load()
    ctx = (
        Context(jobs=[inferencer.job_example()])
        if inferencer.job_example()
        else inferencer.context_example()
    )
    next_ctx = inferencer.on_context(ctx)
    print(next_ctx.results)


@app.command()
def test_stream(inferencer_cls: str, file: str):
    inferencer: StreamInferencerBase = StreamInferencerBase.load_class(inferencer_cls)()
    inferencer.setup()
    inferencer.on_load()
    with av.open(file, "r") as in_av:
        for frame in in_av.decode(in_av.streams.audio[0]):
            ctx = StreamContext(event_type=EvtType.AV_AUDIO, payload=frame)
            inferencer.on_context(ctx)
            time.sleep(0.01)
    time.sleep(1)
    inferencer.on_stop()


@app.command()
def test_upload(filepath):
    storage = create_storage()
    print(storage.push(Context(jobs=[]), File(label="test", path=filepath)))


@app.command()
def test_download(remote_filepath):
    storage = create_storage()
    print(storage.pull(Context(jobs=[]).id, File(label="test", path=remote_filepath)))
