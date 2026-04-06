from sqlalchemy.ext.asyncio import AsyncSession

from app.hackplate.types import HackplateRequest


def get_session(request: HackplateRequest) -> AsyncSession:
    return request.app.state.config.db.get_session()
