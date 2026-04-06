from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from app.hackplate.types import Hackplate


@asynccontextmanager
async def lifespan(app: Hackplate) -> AsyncGenerator[None, None]:
    yield
