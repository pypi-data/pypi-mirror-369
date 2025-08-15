from __future__ import annotations

from typing import Dict, List

from .base import MessageBase
from .file import File
from .result import Result


class Job(MessageBase):
    name: str = ""
    topic: str = ""
    params: Dict = {}
    files: List[File] = []
    relation_result_files: Dict[str, str] = {}

    @property
    def required_params(self):
        return {}

    @property
    def required_files(self):
        return self.relation_result_files

    def prepare_params(self, results: Dict[str, Result]):
        params = {**self.params}
        for key, target in self.required_params.items():
            targets = target.split("__")
            job_name, keys = targets[0], targets[1:]
            params[key] = self.find_value_from_nested_keys(keys, results[job_name].data)
        return params

    def prepare_files(self, results: Dict[str, Result]):
        file_map = {file.label: file for file in self.files}
        for label, target in self.required_files.items():
            job, files_label = target.split("__")
            file = results[job].find_file(files_label).mutate(label=label)
            file_map[label] = file
        return list(file_map.values())

    def find_value_from_nested_keys(keys, dict_):
        dict_value = dict_
        for key in keys:
            dict_value = dict_value.get(key)
            if not dict_value:
                return None
        return dict_value
