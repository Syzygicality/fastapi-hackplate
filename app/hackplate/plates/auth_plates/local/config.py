from __future__ import annotations
from typing import TYPE_CHECKING

from app.hackplate.plates.abstract_plates import AuthPlate
from app.hackplate.toml_settings import AuthSettings

if TYPE_CHECKING:
    from app.hackplate.hackplate_types import Hackplate


class LocalPlate(AuthPlate):
    def __init__(self, toml_settings: AuthSettings):
        pass

    async def register_auth_routes(self, app: Hackplate) -> None:
        pass

    async def get_current_user(self) -> callable:
        pass
