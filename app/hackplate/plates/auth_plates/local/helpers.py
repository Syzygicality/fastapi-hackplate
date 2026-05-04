from fastapi_users.authentication import (
    BearerTransport,
    JWTStrategy,
    AuthenticationBackend,
)
from app.hackplate.user.managers import UserEnvSettings

bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")

SECRET_KEY = UserEnvSettings().secret_key


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET_KEY, lifetime_seconds=3600)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)
