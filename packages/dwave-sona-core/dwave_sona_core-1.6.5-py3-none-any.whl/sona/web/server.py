from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
from sona.settings import settings

from .http.routes import add_routes as add_http_routes
from .messages import SonaResponse
from .webrtc.routes import add_routes as add_webrtc_routes

INFERENCER_CLASS = settings.SONA_INFERENCER_CLASS
STREAM_INFERENCER_CLASS = settings.SONA_STREAM_INFERENCER_CLASS


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, err: RequestValidationError):
    logger.warning(f"Client Error: {request}, {err.errors()}")
    resp = SonaResponse(code="400", message=str(err.errors()))
    return JSONResponse(status_code=400, content=resp.model_dump())


@app.exception_handler(Exception)
async def unicorn_exception_handler(request: Request, err: Exception):
    logger.exception(f"Server Error: {request}")
    resp = SonaResponse(code="500", message=str(err))
    return JSONResponse(status_code=500, content=resp.model_dump())


@app.get("/ping")
async def ping():
    return SonaResponse(message="pong")


if INFERENCER_CLASS:
    add_http_routes(app)


if STREAM_INFERENCER_CLASS:
    add_webrtc_routes(app)
