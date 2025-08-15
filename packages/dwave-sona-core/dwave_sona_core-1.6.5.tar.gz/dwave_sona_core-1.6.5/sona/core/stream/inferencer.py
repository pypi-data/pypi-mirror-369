import abc
from typing import Dict

from sona.core.middlewares import middlewares
from sona.core.stream.parsers.audio import AudioStreamParser
from sona.utils import import_class

from .messages import DictStreamData, RawStreamData, StreamContext, StreamData
from .messages.context import EvtType


class StreamInferencerBase:
    name: str = "base"

    def set_audio_input_spec(
        self, samples=3200, sample_rate=16000, layout="mono", format="s16"
    ):
        self.audio_parser = AudioStreamParser(samples, sample_rate, layout, format)

    def setup(self):
        self.audio_parser = AudioStreamParser()
        for middleware in reversed(middlewares):
            middleware.setup(self)

    def reply(self, streamdata: StreamData, header: Dict = None):
        header = header or dict()
        ctx = StreamContext(
            event_type=streamdata._type, header=header, payload=streamdata.payload
        )
        self.on_reply(ctx)

    def on_load(self) -> None:
        return

    def on_context(self, ctx: StreamContext):
        _type = ctx.event_type
        if _type == EvtType.AV_AUDIO.value:
            for streamdata in self.audio_parser.parse_frame(ctx.payload):
                self.on_inference(ctx.header, streamdata)
        elif _type == EvtType.RAW_AUDIO.value:
            for streamdata in self.audio_parser.parse_raw(ctx.header["c"], ctx.payload):
                self.on_inference(ctx.header, streamdata)
        elif _type == EvtType.DICT.value:
            self.on_inference(ctx.header, DictStreamData(data=ctx.payload))
        elif _type == EvtType.RAW.value:
            self.on_inference(ctx.header, RawStreamData(data=ctx.payload))

    @abc.abstractmethod
    def on_inference(self, header: Dict, streamdata: StreamData):
        return NotImplemented

    def on_reply(self, ctx):
        print(ctx)

    def on_stop(self):
        return

    @classmethod
    def load_class(cls, import_str):
        _cls = import_class(import_str)
        if _cls not in cls.__subclasses__():
            raise Exception(f"Unknown inferencer class: {import_str}")
        return _cls
