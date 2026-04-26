import logging
from typing import Type
from pydantic_settings import BaseSettings, SettingsConfigDict
from beanie import Document, init_beanie
from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase

from app.hackplate.plates.abstract_plates import DatabasePlate
from app.hackplate.toml_settings import DatabaseSettings
from app.hackplate.user.utils import get_user_model

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

    ssl_required: bool = False


class MongoPlate(DatabasePlate):
    """
    Database plate for MongoDB using Beanie ODM and pymongo async.

    Register Beanie Document models before app startup by appending to
    `document_models`, e.g. in app/lifespan.py:

        app.state.config.db.document_models.append(MyDocument)
    """

    def __init__(self, toml_settings: DatabaseSettings):
        self.env_settings = MongoSettings()
        self.toml_settings = toml_settings
        self.client: AsyncMongoClient | None = None
        self.db: AsyncDatabase | None = None
        self.document_models: list[Type[Document]] = []

    async def connect(self) -> None:
        logger.info("Connecting to mongodb...")
        s = self.env_settings
        url = (
            s.url
            if s.url
            else f"mongodb://{s.username}:{s.password}@{s.host}:{s.port}"
            if s.username and s.password
            else f"mongodb://{s.host}:{s.port}"
        )
        if s.ssl_required:
            url += "/?tls=true"
        self.client = AsyncMongoClient(url)
        self.db = self.client[s.name]
        self.document_models.append(get_user_model())
        await init_beanie(database=self.db, document_models=self.document_models)

    async def disconnect(self) -> None:
        if self.client:
            logger.info("Disconnecting from mongodb...")
            await self.client.close()
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

    async def get_db(self) -> AsyncDatabase:
        return self.db
