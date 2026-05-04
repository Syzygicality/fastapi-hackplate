from __future__ import annotations
from typing import TYPE_CHECKING
from collections.abc import Callable
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.hackplate.plates.abstract_plates import AuthPlate
from app.hackplate.toml_settings import AuthSettings

if TYPE_CHECKING:
    from app.hackplate.hackplate_types import Hackplate


class KeycloakSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_prefix="KEYCLOAK_", extra="ignore"
    )

    admin_username: str = "admin"
    admin_password: str = "admin"
    realm: str = "hackplate"
    host: str = "http://keycloak:8080"
    localhost: str = "http://localhost:8080"
    client_id: str = "hackplate"
    client_secret: str


class KeycloakPlate(AuthPlate):
    def __init__(self, toml_settings: AuthSettings, db_name: str):
        pass

    async def register_auth_routes(self, app: Hackplate) -> None:
        pass

    def get_current_user(self) -> Callable:
        pass
