from contextlib import asynccontextmanager
from fastapi import FastAPI
from collections.abc import AsyncGenerator
from starlette.datastructures import State

from app.config.config import BackendConfig
from app.config.logging import setup_logging


class AppState(State):
    config: BackendConfig


class Hackplate(FastAPI):
    state: AppState


@asynccontextmanager
async def lifespan(app: Hackplate) -> AsyncGenerator[None, None]:
    setup_logging()
    config = BackendConfig()
    app.state.config = config
    await config.db.connect()
    yield
    await config.db.disconnect()
