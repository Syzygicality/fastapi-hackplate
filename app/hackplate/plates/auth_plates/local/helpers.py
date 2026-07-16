from fastapi_users.authentication import (
    BearerTransport,
    JWTStrategy,
    AuthenticationBackend,
)
from app.hackplate.plates.auth_plates.local.env_settings import LocalAuthSettings

bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")

SECRET_KEY = LocalAuthSettings().secret_key


class RevocableJWTStrategy(JWTStrategy):
    """
    JWTStrategy that actually implements destroy_token, so /auth/jwt/logout
    revokes the token instead of silently no-opping.

    _revoked is a CLASS attribute (not set in __init__) so it's shared across
    every RevocableJWTStrategy() instance within a process — get_jwt_strategy()
    below constructs a fresh instance per call/request, and a plain instance
    attribute would reset the set each time.

    Caveat: in-memory only. Fine for `hackplate run` (single process, dev or
    single-worker prod). Under `hackplate run -m prod` with HACKPLATE_WORKERS > 1,
    each uvicorn worker is a separate process with its own memory — a token
    revoked on one worker is still valid on the others. For real multi-worker
    revocation, swap this set for a DB table or Redis key checked here instead.
    """

    _revoked: set[str] = set()

    async def destroy_token(self, token: str, user) -> None:
        self._revoked.add(token)

    async def read_token(self, token, user_manager):
        if token in self._revoked:
            return None
        return await super().read_token(token, user_manager)


def get_jwt_strategy() -> RevocableJWTStrategy:
    return RevocableJWTStrategy(secret=SECRET_KEY, lifetime_seconds=3600)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)
