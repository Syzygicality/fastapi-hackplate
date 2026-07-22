from pydantic_settings import BaseSettings, SettingsConfigDict


class RedisSettings(BaseSettings):
    """
    Loads Redis connection settings from the environment (REDIS_* variables).

    Provide either REDIS_URL or the individual connection fields below.
    """

    model_config = SettingsConfigDict(
        env_prefix="REDIS_",
        env_file=".env",
        extra="ignore",
        env_ignore_empty=True,
    )

    url: str | None = None

    host: str = "localhost"
    port: int = 6379
    db: int = 0
    username: str
    password: str
    ssl_required: bool = False

    @property
    def connection_url(self) -> str:
        """Builds a redis:// (or rediss://) URL from the configured settings."""
        if self.url:
            return self.url
        scheme = "rediss" if self.ssl_required else "redis"
        if self.username and self.password:
            auth = f"{self.username}:{self.password}@"
        elif self.password:
            auth = f":{self.password}@"
        else:
            auth = ""
        return f"{scheme}://{auth}{self.host}:{self.port}/{self.db}"
