from contextlib import asynccontextmanager, AsyncExitStack
from collections.abc import AsyncGenerator

from app.hackplate.config import BackendConfig
from app.hackplate.logging import setup_logging
from app.hackplate.types import Hackplate
from app.lifespan import lifespan


@asynccontextmanager
async def config_lifespan(app: Hackplate) -> AsyncGenerator[None, None]:
    setup_logging()
    config = BackendConfig()
    app.state.config = config
    await config.db.connect()
    yield
    await config.db.disconnect()


@asynccontextmanager
async def hackplate_lifespan(app: Hackplate) -> AsyncGenerator[None, None]:
    async with AsyncExitStack() as stack:
        await stack.enter_async_context(config_lifespan(app))
        await stack.enter_async_context(lifespan(app))
        yield
