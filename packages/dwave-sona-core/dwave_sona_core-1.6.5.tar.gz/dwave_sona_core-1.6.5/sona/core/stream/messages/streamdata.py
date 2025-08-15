from typing import Any, Dict

import av
from pydantic import BaseModel

from .context import EvtType


class StreamData(BaseModel):
    _type: int
    data: Any

    @property
    def payload(self):
        return self.data


class DictStreamData(StreamData):
    _type: int = EvtType.DICT.value
    data: Dict


class RawStreamData(StreamData):
    _type: int = EvtType.RAW.value
    data: bytes


class AVAudioStreamData(StreamData):
    _type: int = EvtType.AV_AUDIO.value
    data: Any  # av.AudioFrame

    @property
    def raw(self):
        return bytes(self.data.planes[0])

    @property
    def sample_rate(self):
        return self.data.rate

    @property
    def samples(self):
        return self.data.samples

    @property
    def bit_depth(self):
        return self.data.format.bits

    @property
    def channels(self):
        return len(self.data.layout.channels)

    @property
    def ndarray(self):
        return self.data.to_ndarray()

    @classmethod
    def from_ndarray(cls, ndarray, format="s16", layout="mono", rate=16000):
        frame = av.AudioFrame.from_ndarray(ndarray, format=format, layout=layout)
        frame.sample_rate = rate
        return cls(data=frame)
