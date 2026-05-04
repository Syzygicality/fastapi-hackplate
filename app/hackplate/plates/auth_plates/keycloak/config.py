from __future__ import annotations
from typing import TYPE_CHECKING
from collections.abc import Callable
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.hackplate.plates.abstract_plates import AuthPlate
from app.hackplate.toml_settings import AuthSettings
from app.hackplate.plates.auth_plates.keycloak.routes import keycloak_router_factory
from app.hackplate.user.dependencies import (
    get_sqlmodel_user_manager,
    get_beanie_user_manager,
)

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
    external_url: str = "http://localhost:8080"
    client_id: str = "hackplate"
    client_secret: str
    callback_url: str = "http://localhost:8000/auth/callback"
    redirect_uri: str = "http://localhost:8000/docs"
    secure_cookies: bool = False


class KeycloakPlate(AuthPlate):
    def __init__(self, toml_settings: AuthSettings, db_name: str):
        self.env_settings = KeycloakSettings()
        self.manager_dependency = (
            get_beanie_user_manager if db_name == "mongo" else get_sqlmodel_user_manager
        )

    async def register_auth_routes(self, app: Hackplate) -> None:
        app.include_router(
            keycloak_router_factory(self.env_settings, self.manager_dependency),
            tags=["Auth"],
        )

    def get_current_user(self) -> Callable:
        pass
