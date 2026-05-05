from __future__ import annotations

import asyncio
import secrets
from collections.abc import Callable
from typing import TYPE_CHECKING
from urllib.parse import urlencode

from auth0.authentication import GetToken, Users
from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from fastapi.responses import RedirectResponse
from fastapi_users import BaseUserManager

from app.hackplate.user.schemas import UserCreate
from app.hackplate.plates.auth_plates.auth0.env_settings import Auth0Settings

if TYPE_CHECKING:
    from app.hackplate.hackplate_types import HackplateRequest


def auth0_router_factory(
    settings: Auth0Settings, manager_dependency: Callable
) -> APIRouter:
    get_token = GetToken(
        settings.domain, settings.client_id, client_secret=settings.client_secret
    )
    users_client = Users(settings.domain)
    auth0_router = APIRouter()

    @auth0_router.get("/auth/login")
    async def login():
        params = urlencode(
            {
                "client_id": settings.client_id,
                "response_type": "code",
                "scope": "openid profile email",
                "redirect_uri": settings.callback_url,
                "audience": settings.audience,
            }
        )
        return RedirectResponse(f"https://{settings.domain}/authorize?{params}")

    @auth0_router.get("/auth/callback")
    async def callback(
        code: str, user_manager: BaseUserManager = Depends(manager_dependency)
    ):
        try:
            tokens = await asyncio.to_thread(
                get_token.authorization_code, code, settings.callback_url
            )
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token exchange failed. Try again later.",
            )

        try:
            user_info = await asyncio.to_thread(
                users_client.userinfo, tokens["access_token"]
            )
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token."
            )

        email = user_info["email"]
        sub = user_info["sub"]
        existing_user = await user_manager.user_db.get_by_email(email)

        if not existing_user:
            await user_manager.create(
                UserCreate(
                    email=email,
                    password=secrets.token_urlsafe(32),
                    is_verified=True,
                    is_active=True,
                    is_superuser=False,
                    sub=sub,
                )
            )
        elif not existing_user.sub:
            await user_manager.user_db.update(existing_user, {"sub": sub})

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

    @auth0_router.get("/auth/logout")
    async def logout(request: HackplateRequest):
        id_token = request.cookies.get("id_token")
        if not id_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Not logged in."
            )

        params = urlencode(
            {
                "client_id": settings.client_id,
                "returnTo": settings.redirect_uri,
            }
        )
        response = RedirectResponse(f"https://{settings.domain}/v2/logout?{params}")
        response.delete_cookie("id_token")
        response.delete_cookie("access_token")
        return response

    return auth0_router
