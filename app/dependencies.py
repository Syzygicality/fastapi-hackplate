from collections.abc import AsyncGenerator

from sqlmodel.ext.asyncio.session import AsyncSession
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.hackplate.hackplate_types import HackplateRequest


async def get_session(request: HackplateRequest) -> AsyncGenerator[AsyncSession, None]:
    async with request.app.state.config.db.get_db() as session:
        yield session


async def get_client(request: HackplateRequest) -> AsyncIOMotorDatabase:
    return await request.app.state.config.db.get_db()
