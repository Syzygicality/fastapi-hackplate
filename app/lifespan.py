from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from app.config.config import BackendConfig
from app.config.logging import setup_logging
from app.types import Hackplate


@asynccontextmanager
async def lifespan(app: Hackplate) -> AsyncGenerator[None, None]:
    setup_logging()
    config = BackendConfig()
    app.state.config = config
    await config.db.connect()
    yield
    await config.db.disconnect()
