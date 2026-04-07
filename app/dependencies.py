from collections.abc import AsyncGenerator

from sqlmodel.ext.asyncio.session import AsyncSession

from app.hackplate.types import HackplateRequest


async def get_session(request: HackplateRequest) -> AsyncGenerator[AsyncSession, None]:
    async with request.app.state.config.db.get_session() as session:
        yield session
