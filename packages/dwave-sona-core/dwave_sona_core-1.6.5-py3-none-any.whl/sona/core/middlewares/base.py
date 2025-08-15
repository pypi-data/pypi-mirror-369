from loguru import logger

from sona.utils import import_class


class MiddlewareBase:
    def setup(self, inferencer):
        logger.info(f"Setup middleware: {self.__class__.__name__}")
        inferencer.on_load = self.on_load_decorator(inferencer.on_load)
        inferencer.on_context = self.on_context_decorator(inferencer.on_context)
        inferencer.on_stop = self.on_stop_decorator(inferencer.on_stop)
        return inferencer

    # on_load
    def on_load_decorator(self, on_load):
        def func():
            return self.on_load(on_load)

        return func

    def on_load(self, on_load):
        return on_load()

    # on_context
    def on_context_decorator(self, on_context):
        def func(ctx):
            return self.on_context(ctx, on_context)

        return func

    def on_context(self, ctx, on_context):
        return on_context(ctx)

    # on_stop
    def on_stop_decorator(self, on_stop):
        def func():
            return self.on_stop(on_stop)

        return func

    def on_stop(self, on_stop):
        return on_stop()

    @classmethod
    def load_class(cls, import_str):
        _cls = import_class(import_str)
        if _cls not in cls.__subclasses__():
            raise Exception(f"Unknown middleware class: {import_str}")
        return _cls
