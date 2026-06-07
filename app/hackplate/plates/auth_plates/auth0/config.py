from __future__ import annotations

from typing import TYPE_CHECKING, Any

from auth0.authentication.async_token_verifier import (
    AsyncAsymmetricSignatureVerifier,
    AsyncTokenVerifier,
)
from auth0.management import AsyncManagementClient
from fastapi import status
from fastapi.exceptions import HTTPException

from app.hackplate.plates.abstract_plates import AuthPlate
from app.hackplate.plates.auth_plates.auth0.env_settings import Auth0Settings
from app.hackplate.plates.auth_plates.auth0.helpers import (
    auth_backend,
    Auth0SyncMixin,
    get_auth0_beanie_user_manager,
    get_auth0_sqlmodel_user_manager,
)
from app.hackplate.plates.auth_plates.auth0.routes import auth0_router_factory
from app.hackplate.toml_settings import AuthSettings
from app.hackplate.user.adapters import (
    BeanieUserDatabaseAsync,
    SQLModelUserDatabaseAsync,
)
from app.hackplate.user.schemas import UserDocumentRead, UserRead, UserUpdate
from app.hackplate.user.utils import get_user_model, make_fastapi_users

if TYPE_CHECKING:
    from app.hackplate.hackplate_types import Hackplate, HackplateRequest


class Auth0Plate(AuthPlate):
    def __init__(self, toml_settings: AuthSettings, db_name: str):
        self.db_name = db_name
        self.env_settings = Auth0Settings()

        Auth0SyncMixin.mgmt_client = AsyncManagementClient(
            domain=self.env_settings.domain,
            client_id=self.env_settings.m2m_client_id,
            client_secret=self.env_settings.m2m_client_secret,
        )

        self.manager_dependency = (
            get_auth0_beanie_user_manager
            if db_name == "mongo"
            else get_auth0_sqlmodel_user_manager
        )
        self.read_schema = UserDocumentRead if db_name == "mongo" else UserRead
        self.fastapi_users = make_fastapi_users(auth_backend, self.manager_dependency)
        sv = AsyncAsymmetricSignatureVerifier(
            f"https://{self.env_settings.domain}/.well-known/jwks.json"
        )
        self.token_verifier = AsyncTokenVerifier(
            signature_verifier=sv,
            issuer=f"https://{self.env_settings.domain}/",
            audience=self.env_settings.audience,
        )

    async def register_auth_routes(self, app: Hackplate) -> None:
        app.include_router(
            auth0_router_factory(self.env_settings, self.manager_dependency),
            tags=["auth"],
        )
        app.include_router(
            self.fastapi_users.get_users_router(self.read_schema, UserUpdate),
            prefix="/users",
            tags=["users"],
        )

    async def authenticate(self, request: HackplateRequest) -> None:
        id_token = request.cookies.get("id_token")
        if not id_token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        try:
            await self.token_verifier.verify(id_token)
        except Exception:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    async def get_current_user(self, request: HackplateRequest) -> Any:
        id_token = request.cookies.get("id_token")
        if not id_token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        try:
            payload = await self.token_verifier.verify(id_token)
        except Exception:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        if self.db_name == "mongo":
            user_db = BeanieUserDatabaseAsync(get_user_model())
            user = await user_db.get_by_sub(payload["sub"])
        else:
            async with request.app.state.config.db.get_db() as session:
                user_db = SQLModelUserDatabaseAsync(session, get_user_model())
                user = await user_db.get_by_sub(payload["sub"])

        if not user or not user.is_active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        return user
