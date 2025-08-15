from enum import IntEnum
from typing import Any, Dict

from sona.core.messages import MessageBase


class EvtType(IntEnum):
    DICT = 0
    RAW = 1
    RAW_AUDIO = 2
    RAW_VIDEO = 3
    AV_AUDIO = 4


class StreamContext(MessageBase):
    event_type: int
    header: Dict = {}
    payload: Any = None
