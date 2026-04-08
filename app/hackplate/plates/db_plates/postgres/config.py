from pydantic_settings import BaseSettings, SettingsConfigDict

from app.hackplate.plates.abstract_plates import DatabasePlate


class PostgresSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="POSTGRES_")

    name: str
    username: str
    password: str


class PostgresConfig(DatabasePlate):
    def __init__(self):
        self.config = PostgresSettings()

    async def connect(self) -> None:
        pass

    async def disconnect(self) -> None:
        pass

    async def ping(self) -> bool:
        pass

    async def get_session(self):
        pass
