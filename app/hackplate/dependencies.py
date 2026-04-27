from __future__ import annotations
from collections.abc import AsyncGenerator

from sqlmodel.ext.asyncio.session import AsyncSession
from pymongo.asynchronous.database import AsyncDatabase

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.hackplate.hackplate_types import HackplateRequest


async def hackplate_get_session(
    request: HackplateRequest,
) -> AsyncGenerator[AsyncSession, None]:
    async with request.app.state.config.db.get_db() as session:
        yield session


async def hackplate_get_client(request: HackplateRequest) -> AsyncDatabase:
    """Returns the raw pymongo async database. Prefer using Beanie Document models directly."""
    return await request.app.state.config.db.get_db()
