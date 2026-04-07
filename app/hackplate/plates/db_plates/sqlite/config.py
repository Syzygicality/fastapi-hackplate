import logging
from pathlib import Path
from pydantic_settings import BaseSettings
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.hackplate.plates.abstract_plates import DatabasePlate

logger = logging.getLogger(__name__)


class SQLiteSettings(BaseSettings):
    db_path: str = "db.sqlite3"


class SQLitePlate(DatabasePlate):
    def __init__(self):
        self.config = SQLiteSettings()
        self.engine = None
        self._session_factory: async_sessionmaker[AsyncSession] | None = None

    async def connect(self) -> None:
        logger.info("Connecting to sqlite file...")
        resolved = str(Path(self.config.db_path).resolve())
        self.engine = create_async_engine(f"sqlite+aiosqlite:///{resolved}")
        self._session_factory = async_sessionmaker(self.engine, expire_on_commit=False)

    async def disconnect(self) -> None:
        if self.engine:
            logger.info("Disconnecting from sqlite file...")
            await self.engine.dispose()
            self.engine = None
            self._session_factory = None

    async def ping(self) -> bool:
        if not self._session_factory:
            logger.warning("Ping failed, session factory is None")
            return False
        try:
            async with self._session_factory() as session:
                await session.exec(select(1))
            logger.info("PONG")
            return True
        except Exception:
            logger.exception("Ping failed")
            return False

    async def get_session(self) -> AsyncSession:
        return self._session_factory()
