from collections.abc import AsyncGenerator

from sqlmodel.ext.asyncio.session import AsyncSession
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.hackplate.hackplate_types import HackplateRequest


async def get_session(request: HackplateRequest) -> AsyncGenerator[AsyncSession, None]:
    async with request.app.state.config.db.get_session() as session:
        yield session


async def get_client(request: HackplateRequest) -> AsyncIOMotorDatabase:
    return request.app.state.config.db.get_session()


async def get_db(request: HackplateRequest):
    if request.app.state.config.db_name == "mongodb":
        get_client(request)
    else:
        get_session(request)
