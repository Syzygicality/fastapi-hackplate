from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from app.hackplate.hackplate_types import Hackplate


@asynccontextmanager
async def lifespan(app: Hackplate) -> AsyncGenerator[None, None]:
    """
    Lifespan handler designated for user modification.

    Args:
        app: initialized Hackplate object originating from main.py
    """
    yield
