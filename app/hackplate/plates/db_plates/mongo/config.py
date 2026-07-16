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
        env_prefix="MONGO_",
        env_file=".env",
        extra="ignore",
        env_ignore_empty=True,
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

    Feature Document models under app/<feature>/models.py are discovered
    automatically via migrations/register_models.py — no manual step needed.

    For Document models defined elsewhere (e.g. imported from a third-party
    package), append them before startup in the *pre*-hackplate hook, since
    that's the one guaranteed to run before connect()/init_beanie():

        # app/lifespan.py
        @asynccontextmanager
        async def pre_hackplate_lifespan(app: Hackplate):
            app.state.config.db.document_models.append(MyDocument)
            yield
    """

    def __init__(self, toml_settings: DatabaseSettings):
        self.env_settings = MongoSettings()
        self.toml_settings = toml_settings
        self.client: AsyncMongoClient | None = None
        self.db: AsyncDatabase | None = None
        self.document_models: list[Type[Document]] = []

    async def connect(self) -> None:
        logger.info("Connecting to MongoDB...")
        import migrations.register_models  # noqa: F401

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
        self.document_models.extend(self._discover_document_models())
        await init_beanie(database=self.db, document_models=self.document_models)

    def _discover_document_models(self) -> list[Type[Document]]:
        """
        Collect every concrete Beanie Document subclass pulled in by importing
        migrations.register_models. A class counts as "concrete" if nothing
        subclasses it further — this skips abstract intermediates like
        AbstractUserDocument while still catching UserDocument, a custom user
        model, or any feature-defined Document. Anything already in
        self.document_models (i.e. the active user model) is deduped out.
        """
        already = set(self.document_models)
        seen: set[Type[Document]] = set()

        def walk(cls: Type[Document]) -> None:
            for sub in cls.__subclasses__():
                if sub not in seen:
                    seen.add(sub)
                    walk(sub)

        walk(Document)
        return [cls for cls in seen if not cls.__subclasses__() and cls not in already]

    async def disconnect(self) -> None:
        if self.client:
            logger.info("Disconnecting from mongodb...")
            await self.client.close()
            self.client = None
            self.db = None

    async def ping(self) -> bool:
        if not self.client:
            logger.warning("Ping failed, client not found.")
            return False
        try:
            await self.client.admin.command("ping")
            return True
        except Exception:
            return False

    async def get_db(self) -> AsyncDatabase:
        return self.db
