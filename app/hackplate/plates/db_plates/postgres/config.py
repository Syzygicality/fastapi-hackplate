import logging
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.hackplate.plates.abstract_plates import DatabasePlate

logger = logging.getLogger(__name__)


class PostgresSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="POSTGRES_", env_file=".env", extra="ignore"
    )

    url: str | None = None

    name: str
    username: str
    password: str
    host: str = "localhost"
    port: int = 5432


class PostgresPlate(DatabasePlate):
    def __init__(self):
        self.settings = PostgresSettings()
        self.engine = None
        self._session_factory: async_sessionmaker[AsyncSession] | None = None

    async def connect(self) -> None:
        logger.info("Connecting to postgres...")
        s = self.settings
        url = (
            f"postgresql+asyncpg://{s.username}:{s.password}@{s.host}:{s.port}/{s.name}"
            if not self.settings.url
            else self.settings.url
        )
        self.engine = create_async_engine(url)
        self._session_factory = async_sessionmaker(self.engine, expire_on_commit=False)

    async def disconnect(self) -> None:
        if self.engine:
            logger.info("Disconnecting from postgres...")
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
