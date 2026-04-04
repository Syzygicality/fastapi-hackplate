from sqlalchemy.ext.asyncio import AsyncSession

from app.config.config import HackplateRequest


def get_session(request: HackplateRequest) -> AsyncSession:
    return request.app.state.config.db.get_session()
