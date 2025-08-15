from __future__ import annotations

import abc
from typing import Any, Dict, List

import click
from loguru import logger
from pydantic import BaseModel, Field
from sona.core.messages import Context, File, Job, Result, State
from sona.core.middlewares import middlewares
from sona.core.storages import create_storage
from sona.utils import import_class


class DefaultInputFilesSchema(BaseModel):
    default: str = Field(None, description="origin file")


class InferencerBase:
    name: str = "base"
    description: str = ""
    input_params_schema: BaseModel = None
    input_files_schema: BaseModel = DefaultInputFilesSchema

    def setup(self):
        for middleware in reversed(middlewares):
            middleware.setup(self)

    def on_context(self, ctx: Context) -> Context:
        storage = create_storage()
        try:
            logger.info(f"[{self.name}] recv: {ctx.to_message()}")

            # Prepare process data
            current_job: Job = ctx.current_job
            current_state: State = State.start(current_job.name)
            params = current_job.prepare_params(ctx.results)
            files = current_job.prepare_files(ctx.results)
            files = storage.pull_all(ctx.id, files)

            # Process
            result: Result = self.inference(params, files)

            # NOTE: special case for s3 storage
            s3meta = {}
            for file in files:
                s3meta.update(file.metadata.get("s3", {}))
            result = result.mutate(
                files=storage.push_all(ctx, result.files, metadata={"s3": s3meta})
            )

            # Create success context
            current_state = current_state.complete()
            next_ctx = ctx.next_context(current_state, result)
            logger.info(f"[{self.name}] success: {next_ctx.to_message()}")
            return next_ctx

        except Exception as e:
            # Create fail context
            current_state = current_state.fail(e)
            next_ctx = ctx.next_context(current_state)
            logger.exception(f"[{self.name}] error: {next_ctx.to_message()}")
            return next_ctx

        finally:
            storage.clean(ctx.id)

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        param_props, file_props = {}, {}
        if self.input_params_schema:
            schema = self.input_params_schema.model_json_schema()
            param_props = schema["properties"]
        if self.input_files_schema:
            schema = self.input_files_schema.model_json_schema()
            file_props = schema["properties"]

        def run(**kwargs):
            files = []
            for prop in file_props:
                val = kwargs.pop(prop)
                if val:
                    files.append(File(label=prop, path=val))
            if self.input_params_schema:
                kwargs = self.input_params_schema(**kwargs).model_dump()
            self.on_load()
            result = self.inference(params=kwargs, files=files)
            print(result.model_dump_json())

        func = run
        for name, prop in reversed(param_props.items()):
            option = click.option(
                f"--{name}", default=prop.get("default"), help=prop.get("description")
            )
            func = option(func)
        for name, prop in reversed(file_props.items()):
            option = click.argument(name, metavar=f"<filepath:{name}>")
            func = option(func)
        func.__doc__ = self.description
        click.command()(func)()

    @classmethod
    def load_class(cls, import_str):
        _cls = import_class(import_str)
        if _cls not in cls.__subclasses__():
            raise Exception(f"Unknown inferencer class: {import_str}")
        return _cls

    # Callbacks
    def on_load(self) -> None:
        return

    def on_stop(self):
        return

    @abc.abstractmethod
    def inference(self, params: Dict, files: List[File]) -> Result:
        return NotImplemented

    def context_example(self) -> Context:
        return None

    def job_example(self) -> Job:
        return None
