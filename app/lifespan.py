from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from app.config.config import BackendConfig, Hackplate
from app.config.logging import setup_logging


@asynccontextmanager
async def lifespan(app: Hackplate) -> AsyncGenerator[None, None]:
    setup_logging()
    config = BackendConfig()
    app.state.config = config
    await config.db.connect()
    yield
    await config.db.disconnect()
