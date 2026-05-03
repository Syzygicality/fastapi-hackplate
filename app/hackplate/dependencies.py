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


async def hackplate_get_current_user():
    """
    Returns the current authenticated user from the configured auth plate.

    This is a placeholder overridden via app.dependency_overrides during the hackplate
    lifespan with the auth plate's get_current_user() callable. Use as
    Depends(hackplate_get_current_user) in route definitions.
    """
    ...
