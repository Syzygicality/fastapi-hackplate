import importlib
from functools import lru_cache
from uuid import UUID
from fastapi import APIRouter, Depends, Request, Response, status
from fastapi_users import BaseUserManager, FastAPIUsers

from app.hackplate.toml_settings import GeneralSettings
from app.hackplate.user.models import AbstractUser, AbstractUserDocument


@lru_cache(maxsize=1)
def get_user_model() -> type[AbstractUser] | type[AbstractUserDocument]:
    settings = GeneralSettings()
    module_path, class_name = settings.auth_user_model.rsplit(".", 1)
    module = importlib.import_module(module_path)
    model = getattr(module, class_name)
    if not issubclass(model, (AbstractUser, AbstractUserDocument)):
        raise ValueError(
            f"{settings.auth_user_model} must inherit from AbstractUser or AbstractUserDocument"
        )
    return model


def make_fastapi_users(auth_backend, manager_dependency):
    return FastAPIUsers[AbstractUser, UUID](
        manager_dependency,
        [auth_backend],
    )


def make_delete_me_router(fastapi_users: FastAPIUsers) -> APIRouter:
    """
    fastapi-users' generated /users router has no DELETE /me — only a
    superuser-gated DELETE /{id}. This adds self-account deletion using the
    same current_user()/get_user_manager() dependencies fastapi-users uses
    internally, so it goes through user_manager.delete() exactly like the
    superuser route does (firing on_after_delete — e.g. Auth0SyncMixin's
    Auth0 account cleanup).
    """
    router = APIRouter()
    get_current_active_user = fastapi_users.current_user(active=True)

    @router.delete(
        "/me",
        status_code=status.HTTP_204_NO_CONTENT,
        response_class=Response,
        name="users:delete_current_user",
        responses={
            status.HTTP_401_UNAUTHORIZED: {
                "description": "Missing token or inactive user.",
            },
        },
    )
    async def delete_me(
        request: Request,
        user=Depends(get_current_active_user),
        user_manager: BaseUserManager = Depends(fastapi_users.get_user_manager),
    ):
        await user_manager.delete(user, request=request)
        return None

    return router
