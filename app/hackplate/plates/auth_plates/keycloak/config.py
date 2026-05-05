from __future__ import annotations
from typing import TYPE_CHECKING
from collections.abc import Callable
from keycloak import KeycloakOpenID, KeycloakAdmin, KeycloakOpenIDConnection

from fastapi import Depends, status
from fastapi.exceptions import HTTPException
from fastapi_users import BaseUserManager

from app.hackplate.plates.abstract_plates import AuthPlate
from app.hackplate.toml_settings import AuthSettings
from app.hackplate.plates.auth_plates.keycloak.routes import keycloak_router_factory
from app.hackplate.plates.auth_plates.keycloak.env_settings import KeycloakSettings
from app.hackplate.plates.auth_plates.keycloak.helpers import (
    auth_backend,
    KeycloakSyncMixin,
    get_keycloak_sqlmodel_user_manager,
    get_keycloak_beanie_user_manager,
)
from app.hackplate.user.utils import make_fastapi_users
from app.hackplate.user.schemas import UserRead, UserUpdate, UserDocumentRead

if TYPE_CHECKING:
    from app.hackplate.hackplate_types import Hackplate, HackplateRequest


class KeycloakPlate(AuthPlate):
    def __init__(self, toml_settings: AuthSettings, db_name: str):
        self.env_settings = KeycloakSettings()

        KeycloakSyncMixin.keycloak_admin = KeycloakAdmin(
            connection=KeycloakOpenIDConnection(
                server_url=self.env_settings.host,
                realm_name=self.env_settings.realm,
                username=self.env_settings.admin_username,
                password=self.env_settings.admin_password,
                client_id=self.env_settings.client_id,
                client_secret_key=self.env_settings.client_secret,
                verify=True,
            )
        )

        self.manager_dependency = (
            get_keycloak_beanie_user_manager
            if db_name == "mongo"
            else get_keycloak_sqlmodel_user_manager
        )
        self.read_schema = UserDocumentRead if db_name == "mongo" else UserRead
        self.keycloak_openid = KeycloakOpenID(
            server_url=self.env_settings.host,
            realm_name=self.env_settings.realm,
            client_id=self.env_settings.client_id,
            client_secret_key=self.env_settings.client_secret,
        )
        self.fastapi_users = make_fastapi_users(auth_backend, self.manager_dependency)

    async def register_auth_routes(self, app: Hackplate) -> None:
        app.include_router(
            keycloak_router_factory(self.env_settings, self.manager_dependency),
            tags=["auth"],
        )
        app.include_router(
            self.fastapi_users.get_users_router(self.read_schema, UserUpdate),
            prefix="/users",
            tags=["users"],
        )

    def get_current_user(self) -> Callable:
        async def authenticate(
            request: HackplateRequest,
            user_manager: BaseUserManager = Depends(self.manager_dependency),
        ):
            token = request.cookies.get("access_token")
            if not token:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
            try:
                user_info = await self.keycloak_openid.a_decode_token(token)
            except Exception:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

            user = await user_manager.user_db.get_by_sub(user_info["sub"])
            if not user or not user.is_active:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
            return user

        return authenticate
