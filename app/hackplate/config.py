from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator
from typing import Self

from app.hackplate.plates.db_plates.sqlite.config import SQLitePlate
from app.hackplate.plates.db_plates.postgres.config import PostgresPlate
from app.hackplate.plates.abstract_plates import DatabasePlate, AuthPlate
from app.hackplate.plates.auth_plates.local.config import LocalPlate
from app.hackplate.cors import CORSSettings

database_plates = {"sqlite": SQLitePlate, "postgres": PostgresPlate, "mongo": None}

auth_plates = {"local": LocalPlate, "auth0": None, "keycloak": None}


class BackendSettings(BaseSettings):
    """
    Pulls hackplate's configured authentication and database plates from .env
    """

    model_config = SettingsConfigDict(
        env_prefix="HACKPLATE_", env_file=".env", extra="ignore"
    )

    db: str | None = "sqlite"
    auth: str | None = "local"

    @model_validator(mode="after")
    def validate_plates(self) -> Self:
        """
        Validates .env variables to ensure that they align with usable plates
        """
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
    """
    Centralizes hackplate's configured authentication and database plates
    """

    def __init__(self):
        config = BackendSettings()

        self.db: DatabasePlate = database_plates[config.db]()
        self.db_name = config.db

        self.auth: AuthPlate = auth_plates[config.auth]()
        self.auth_name = config.auth

        self.cors_settings = CORSSettings()
