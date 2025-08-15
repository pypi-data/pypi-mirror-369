import socket
import time
import traceback
from typing import Dict

from pydantic import Field
from sona.core.messages import MessageBase


class State(MessageBase):
    job_name: str
    node_name: str = socket.gethostname()
    timestamp: int = Field(default_factory=time.time_ns)
    exec_time: float = 0
    exception: Dict = {}

    @property
    def duration(self):
        return float(time.time_ns() - self.timestamp) * (0.1**9)

    @classmethod
    def start(cls, job_name):
        return State(job_name=job_name)

    def complete(self):
        return self.mutate(exec_time=self.duration)

    def fail(self, exception):
        return self.mutate(
            exec_time=self.duration,
            exception={"message": str(exception), "traceback": traceback.format_exc()},
        )
