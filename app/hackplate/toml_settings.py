from typing import Any

from pydantic_settings import (
    BaseSettings,
    PyprojectTomlConfigSettingsSource,
    SettingsConfigDict,
)


class BaseTOMLSettings(BaseSettings):
    model_config = SettingsConfigDict(
        pyproject_toml_table_header=("tool", "hackplate"),
        extra="ignore",
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        **kwargs: Any,
    ) -> tuple[PyprojectTomlConfigSettingsSource]:
        return (PyprojectTomlConfigSettingsSource(settings_cls),)


class ProjectDetails(BaseTOMLSettings):
    model_config = SettingsConfigDict(
        pyproject_toml_table_header=("project",),
        extra="ignore",
    )

    name: str = "fastapi-hackplate"
    version: str = "0.1.0"
    description: str = ""


class GeneralSettings(BaseTOMLSettings):
    auth_user_model: str = "app.hackplate.user.models.User"
    redis_enabled: bool = False


class DatabaseSettings(BaseTOMLSettings):
    model_config = SettingsConfigDict(
        pyproject_toml_table_header=("tool", "hackplate", "db"),
        extra="ignore",
    )

    alembic: bool = False


class AuthSettings(BaseTOMLSettings):
    model_config = SettingsConfigDict(
        pyproject_toml_table_header=("tool", "hackplate", "auth"),
        extra="ignore",
    )


class CacheSettings(BaseTOMLSettings):
    """Response-cache (fastapi-cache2) options from [tool.hackplate.cache]."""

    model_config = SettingsConfigDict(
        pyproject_toml_table_header=("tool", "hackplate", "cache"),
        extra="ignore",
    )

    prefix: str = "hackplate-cache"  # key namespace (matters for shared Redis)
    expire: int = 60  # default TTL (seconds) applied by the @cache() decorator


class BackendTOMLSettings:
    def __init__(self):
        self.project = GeneralSettings()
        self.db = DatabaseSettings()
        self.auth = AuthSettings()
        self.cache = CacheSettings()
