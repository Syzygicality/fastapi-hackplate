from fastapi import FastAPI, Request
from starlette.datastructures import State
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator
from typing import Self

from app.db.sqlite.config import SQLitePlate
from app.db.abstract_plate import DatabasePlate
from app.auth.local.config import LocalPlate
from app.auth.abstract_plate import AuthPlate

database_plates = {"sqlite": SQLitePlate, "postgres": None, "mongo": None}

auth_plates = {"local": LocalPlate, "auth0": None, "keycloak": None}


class BackendSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="HACKPLATE_")

    db: str = "sqlite"
    auth: str = "local"

    @model_validator(mode="after")
    def validate_plates(self) -> Self:
        if self.db not in database_plates:
            raise ValueError(
                f"Database plate {self.db} defined in .env is not a valid plate."
            )
        if self.auth not in auth_plates:
            raise ValueError(
                f"Auth plate {self.auth} defined in .env is not a valid plate."
            )
        if not database_plates[self.db]:
            raise NotImplementedError(
                f"Database plate {self.db} defined in .env is not implemented yet."
            )
        if not auth_plates[self.auth]:
            raise NotImplementedError(
                f"Auth plate {self.auth} defined in .env is not implemented yet."
            )
        return self


class BackendConfig:
    def __init__(self):
        config = BackendSettings()

        self.db: DatabasePlate = database_plates[config.db]()
        self.db_name = config.db
        self.auth: AuthPlate = auth_plates[config.auth]()
        self.auth_name = config.auth


class AppState(State):
    config: BackendConfig


class Hackplate(FastAPI):
    state: AppState


class HackplateRequest(Request):
    app: Hackplate
