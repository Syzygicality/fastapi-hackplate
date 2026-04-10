from pydantic_settings import BaseSettings, SettingsConfigDict
from fastapi.middleware.cors import CORSMiddleware

from app.hackplate.hackplate_types import Hackplate


class CORSSettings(BaseSettings):
    """
    Pulls CORS configuration from .env
    """

    model_config = SettingsConfigDict(
        env_prefix="CORS_", env_file=".env", extra="ignore"
    )

    allow_origins: list[str] = ["http://localhost:5173"]
    allow_credentials: bool = True
    allow_methods: list[str] = ["*"]
    allow_headers: list[str] = ["*"]


def register_cors_middleware(app: Hackplate) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=app.state.config.cors_settings.allow_origins,
        allow_credentials=app.state.config.cors_settings.allow_credentials,
        allow_methods=app.state.config.cors_settings.allow_methods,
        allow_headers=app.state.config.cors_settings.allow_headers,
    )
