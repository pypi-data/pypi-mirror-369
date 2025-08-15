from __future__ import annotations

import time
import uuid
from typing import Dict, List

from pydantic import Field, field_validator

from .base import MessageBase
from .job import Job
from .result import Result
from .state import State


class Context(MessageBase):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    start_time: int = Field(default_factory=time.time_ns)
    application: str = "common"
    reporters: List[str] = []
    supervisors: List[str] = []
    fallbacks: List[str] = []
    headers: Dict = {}
    jobs: List[Job]
    results: Dict[str, Result] = {}
    states: List[State] = []

    @field_validator("jobs")
    def uuique_jobs(cls, v: List[Job]):
        job_names = set()
        for job in v:
            assert (
                job.name not in job_names
            ), f"job name must be uniuqe in list, {job.name}"
            job_names.add(job.name)
        return v

    @property
    def duration(self):
        return float(time.time_ns() - self.start_time) * (0.1**9)

    @property
    def current_job(self) -> Job:
        if len(self.states) == len(self.jobs):
            return None
        return self.jobs[len(self.states)]

    @property
    def current_state(self) -> State:
        if not self.states:
            return None
        return self.states[-1]

    @property
    def is_failed(self):
        if not self.states:
            return False
        return bool(self.states[-1].exception)

    def find_job(self, job_name):
        for job in self.jobs:
            if job.name == job_name:
                return job
        return None

    def next_context(self, state, result=None) -> Context:
        current_job = self.current_job
        context = self.mutate(states=self.states + [state])
        if result:
            context = context.mutate(results={**self.results, current_job.name: result})
        return context
