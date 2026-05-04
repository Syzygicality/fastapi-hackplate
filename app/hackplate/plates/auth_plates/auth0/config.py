from __future__ import annotations
from typing import TYPE_CHECKING
from collections.abc import Callable
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.hackplate.plates.abstract_plates import AuthPlate
from app.hackplate.toml_settings import AuthSettings

if TYPE_CHECKING:
    from app.hackplate.hackplate_types import Hackplate


class Auth0Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_prefix="AUTH0_", extra="ignore"
    )

    domain: str
    client_id: str
    client_secret: str
    audience: str


class Auth0Plate(AuthPlate):
    def __init__(self, toml_settings: AuthSettings, db_name: str):
        pass

    async def register_auth_routes(self, app: Hackplate) -> None:
        pass

    def get_current_user(self) -> Callable:
        pass
