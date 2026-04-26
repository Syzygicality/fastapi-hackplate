import logging
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlmodel import SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.hackplate.plates.abstract_plates import DatabasePlate
from app.hackplate.toml_settings import DatabaseSettings

logger = logging.getLogger(__name__)


class SupabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="SUPABASE_", env_file=".env", extra="ignore"
    )

    url: str | None = None

    db_name: str = "postgres"
    db_user: str = "postgres"
    db_password: str
    db_host: str
    db_port: int = 5432

    ssl_required: bool = True


class SupabasePlate(DatabasePlate):
    def __init__(self, toml_settings: DatabaseSettings):
        self.env_settings = SupabaseSettings()
        self.toml_settings = toml_settings
        self.engine = None
        self._session_factory: async_sessionmaker[AsyncSession] | None = None

    async def connect(self) -> None:
        logger.info("Connecting to Supabase...")
        s = self.env_settings
        if s.url:
            url = s.url
        else:
            base = f"postgresql+asyncpg://{s.db_user}:{s.db_password}@{s.db_host}:{s.db_port}/{s.db_name}"
            url = f"{base}?ssl=require" if s.ssl_required else base
        self.engine = create_async_engine(url)
        self._session_factory = async_sessionmaker(self.engine, expire_on_commit=False)
        if not self.toml_settings.alembic:
            logger.info(
                "Alembic disabled, using SQLModel metadata to create database models..."
            )
            async with self.engine.begin() as conn:
                await conn.run_sync(SQLModel.metadata.create_all)
            logger.info("Success!")

    async def disconnect(self) -> None:
        if self.engine:
            logger.info("Disconnecting from Supabase...")
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

    async def get_db(self) -> AsyncSession:
        return self._session_factory()
