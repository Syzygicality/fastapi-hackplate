import httpx
import jwt
import secrets
from collections.abc import Callable
from fastapi import APIRouter, status, Depends
from fastapi.responses import RedirectResponse
from fastapi.exceptions import HTTPException
from urllib.parse import urlencode
from fastapi_users import BaseUserManager

from app.hackplate.hackplate_types import HackplateRequest
from app.hackplate.plates.auth_plates.keycloak.config import KeycloakSettings
from app.hackplate.user.schemas import UserCreate


def keycloak_router_factory(
    settings: KeycloakSettings, manager_dependency: Callable
) -> APIRouter:
    jwks_client = jwt.PyJWKClient(
        f"{settings.host}/realms/{settings.realm}/protocol/openid-connect/certs"
    )

    keycloak_router = APIRouter()

    @keycloak_router.get("/auth/login")
    async def login():
        params = urlencode(
            {
                "client_id": settings.client_id,
                "response_type": "code",
                "scope": "openid profile email",
                "redirect_uri": settings.callback_url,
            }
        )
        url = f"{settings.external_url}/realms/{settings.realm}/protocol/openid-connect/auth?{params}"
        return RedirectResponse(url)

    @keycloak_router.get("/auth/callback")
    async def callback(
        code: str, user_manager: BaseUserManager = Depends(manager_dependency)
    ):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{settings.host}/realms/{settings.realm}/protocol/openid-connect/token",
                    data={
                        "grant_type": "authorization_code",
                        "client_id": settings.client_id,
                        "client_secret": settings.client_secret,
                        "code": code,
                        "redirect_uri": settings.callback_url,
                    },
                )
            response.raise_for_status()
            tokens = response.json()
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token exchange failed. Try again later.",
            )

        if "error" in tokens:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Authentication service error. Try again later.",
            )

        try:
            signing_key = jwks_client.get_signing_key_from_jwt(tokens["id_token"])
            user_info = jwt.decode(
                tokens["id_token"],
                signing_key.key,
                algorithms=["RS256"],
                audience=settings.client_id,
            )
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token."
            )

        email = user_info["email"]
        existing_user = await user_manager.user_db.get_by_email(email)

        if not existing_user:
            await user_manager.create(
                UserCreate(
                    email=email,
                    password=secrets.token_urlsafe(32),
                    is_verified=True,
                    is_active=True,
                    is_superuser=False,
                    sub=user_info["sub"],
                )
            )
        elif not existing_user.sub:
            await user_manager.user_db.update(existing_user, {"sub": user_info["sub"]})

        response = RedirectResponse(url=settings.redirect_uri)
        response.set_cookie(
            "id_token",
            tokens["id_token"],
            httponly=True,
            secure=settings.secure_cookies,
            samesite="lax",
        )
        response.set_cookie(
            "access_token",
            tokens["access_token"],
            httponly=True,
            secure=settings.secure_cookies,
            samesite="lax",
        )
        return response

    @keycloak_router.get("/auth/logout")
    async def logout(request: HackplateRequest):
        id_token = request.cookies.get("id_token")
        if not id_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Not logged in."
            )

        params = urlencode(
            {
                "client_id": settings.client_id,
                "post_logout_redirect_uri": settings.redirect_uri,
                "id_token_hint": id_token,
            }
        )
        url = f"{settings.external_url}/realms/{settings.realm}/protocol/openid-connect/logout?{params}"
        response = RedirectResponse(url)
        response.delete_cookie("id_token")
        response.delete_cookie("access_token")
        return response

    return keycloak_router
