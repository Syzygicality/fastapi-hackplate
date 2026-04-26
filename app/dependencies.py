from collections.abc import AsyncGenerator

from sqlmodel.ext.asyncio.session import AsyncSession
from pymongo.asynchronous.database import AsyncDatabase

from app.hackplate.hackplate_types import HackplateRequest
from app.hackplate.dependencies import hackplate_get_session, hackplate_get_client


async def get_session(request: HackplateRequest) -> AsyncGenerator[AsyncSession, None]:
    async for session in hackplate_get_session(request):
        yield session


async def get_client(request: HackplateRequest) -> AsyncDatabase:
    return await hackplate_get_client(request)
