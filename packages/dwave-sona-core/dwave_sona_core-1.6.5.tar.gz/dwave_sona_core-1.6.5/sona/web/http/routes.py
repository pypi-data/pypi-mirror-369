import asyncio
import os

from sona.core.inferencer import InferencerBase
from sona.core.messages import Context
from sona.settings import settings
from sona.web.messages import SonaResponse

INFERENCER_CLASS = settings.SONA_INFERENCER_CLASS


def add_routes(app):
    inferencer = InferencerBase.load_class(INFERENCER_CLASS)()
    inferencer.setup()
    inferencer.on_load()

    @app.post("/inference")
    async def inference(ctx: Context):
        loop = asyncio.get_running_loop()
        next_ctx: Context = await loop.run_in_executor(None, inferencer.on_context, ctx)
        if next_ctx.is_failed:
            raise Exception("Internal Server Error")
        return SonaResponse(result=list(next_ctx.results.values())[0])
