from __future__ import annotations
from typing import TYPE_CHECKING
from collections.abc import Callable

from app.hackplate.plates.abstract_plates import AuthPlate
from app.hackplate.toml_settings import AuthSettings
from app.hackplate.user.utils import make_fastapi_users
from app.hackplate.user.dependencies import (
    get_sqlmodel_user_manager,
    get_beanie_user_manager,
)
from app.hackplate.plates.auth_plates.local.jwt import auth_backend
from app.hackplate.user.schemas import UserCreate, UserRead, UserUpdate

if TYPE_CHECKING:
    from app.hackplate.hackplate_types import Hackplate


class LocalPlate(AuthPlate):
    def __init__(self, toml_settings: AuthSettings, db_name: str):
        manager_dep = get_sqlmodel_user_manager
        if db_name == "mongo":
            manager_dep = get_beanie_user_manager

        self.fastapi_users = make_fastapi_users(auth_backend, manager_dep)
        self.current_active_user = self.fastapi_users.current_user(active=True)

    async def register_auth_routes(self, app: Hackplate) -> None:
        app.include_router(
            self.fastapi_users.get_auth_router(auth_backend),
            prefix="/auth/jwt",
            tags=["auth"],
        )
        app.include_router(
            self.fastapi_users.get_register_router(UserRead, UserCreate),
            prefix="/auth",
            tags=["auth"],
        )
        app.include_router(
            self.fastapi_users.get_reset_password_router(),
            prefix="/auth",
            tags=["auth"],
        )
        app.include_router(
            self.fastapi_users.get_verify_router(UserRead),
            prefix="/auth",
            tags=["auth"],
        )
        app.include_router(
            self.fastapi_users.get_users_router(UserRead, UserUpdate),
            prefix="/users",
            tags=["users"],
        )

    def get_current_user(self) -> Callable:
        return self.current_active_user
