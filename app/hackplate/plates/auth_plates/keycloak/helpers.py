from __future__ import annotations
import logging
from fastapi import Depends
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from keycloak import KeycloakAdmin, KeycloakOpenIDConnection
from typing import Generic, TypeVar

from app.hackplate.user.managers import UserManager, UserDocumentManager
from app.hackplate.user.models import AbstractUser, AbstractUserDocument
from app.hackplate.user.dependencies import get_sqlmodel_user_db, get_beanie_user_db
from app.hackplate.plates.auth_plates.keycloak.env_settings import KeycloakSettings


logger = logging.getLogger(__name__)

auth_backend = AuthenticationBackend(
    name="keycloak",
    transport=BearerTransport(tokenUrl=""),
    get_strategy=lambda: JWTStrategy(secret="unused", lifetime_seconds=0),
)


settings = KeycloakSettings()

keycloak_connection = KeycloakOpenIDConnection(
    server_url=settings.host,
    realm_name=settings.realm,
    username=settings.admin_username,
    password=settings.admin_password,
    client_id=settings.client_id,
    client_secret_key=settings.client_secret,
    verify=True,
)
keycloak_admin = KeycloakAdmin(connection=keycloak_connection)

UP = TypeVar("UP", AbstractUser, AbstractUserDocument)


class KeycloakSyncMixin(Generic[UP]):
    async def on_after_update(self, user: UP, update_dict: dict, request=None):
        if not user.sub:
            return
        await keycloak_admin.a_update_user(
            user_id=user.sub,
            payload={
                k: v
                for k, v in {
                    "email": update_dict.get("email"),
                    "enabled": update_dict.get("is_active"),
                }.items()
                if v is not None
            },
        )
        logger.info(f"User {user.id} synced to Keycloak.")

    async def on_after_delete(self, user: UP, request=None):
        if not user.sub:
            return
        await keycloak_admin.a_delete_user(user_id=user.sub)
        logger.info(f"User {user.id} deleted from Keycloak.")


class KeycloakUserManager(KeycloakSyncMixin[AbstractUser], UserManager): ...


class KeycloakUserDocumentManager(
    KeycloakSyncMixin[AbstractUserDocument], UserDocumentManager
): ...


async def get_keycloak_sqlmodel_user_manager(user_db=Depends(get_sqlmodel_user_db)):
    yield KeycloakUserManager(user_db)


async def get_keycloak_beanie_user_manager(user_db=Depends(get_beanie_user_db)):
    yield KeycloakUserDocumentManager(user_db)
