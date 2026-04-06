from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from app.hackplate.config import BackendConfig
from app.hackplate.logging import setup_logging
from app.hackplate.types import Hackplate


@asynccontextmanager
async def lifespan(app: Hackplate) -> AsyncGenerator[None, None]:
    setup_logging()
    config = BackendConfig()
    app.state.config = config
    await config.db.connect()
    yield
    await config.db.disconnect()
