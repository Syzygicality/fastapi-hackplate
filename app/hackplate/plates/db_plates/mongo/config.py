import logging
from pydantic_settings import BaseSettings, SettingsConfigDict
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.hackplate.plates.abstract_plates import DatabasePlate

logger = logging.getLogger(__name__)


class MongoSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="MONGO_", env_file=".env", extra="ignore"
    )

    url: str | None = None

    host: str = "localhost"
    port: int = 27017
    name: str = "hackplate"
    username: str | None = None
    password: str | None = None


class MongoPlate(DatabasePlate):
    def __init__(self):
        self.settings = MongoSettings()
        self.client: AsyncIOMotorClient | None = None
        self.db: AsyncIOMotorDatabase | None = None

    async def connect(self) -> None:
        logger.info("Connecting to mongo...")
        s = self.settings
        url = (
            s.url
            if s.url
            else f"mongodb://{s.username}:{s.password}@{s.host}:{s.port}"
            if s.username and s.password
            else f"mongodb://{s.host}:{s.port}"
        )
        self.client = AsyncIOMotorClient(url)
        self.db = self.client[s.name]

    async def disconnect(self) -> None:
        if self.client:
            logger.info("Disconnecting from mongo...")
            self.client.close()
            self.client = None
            self.db = None

    async def ping(self) -> bool:
        if not self.client:
            logger.warning("Ping failed, client is None")
            return False
        try:
            await self.client.admin.command("ping")
            logger.info("PONG")
            return True
        except Exception:
            logger.exception("Ping failed")
            return False

    async def get_db(self) -> AsyncIOMotorDatabase:
        return self.db
