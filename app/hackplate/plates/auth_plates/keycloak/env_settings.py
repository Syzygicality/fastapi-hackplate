from pydantic_settings import BaseSettings, SettingsConfigDict


class KeycloakSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_prefix="KEYCLOAK_", extra="ignore"
    )

    admin_username: str = "admin"
    admin_password: str = "admin"
    realm: str = "hackplate"
    host: str = "http://keycloak:8080"
    external_url: str = "http://localhost:8080"
    client_id: str = "hackplate"
    client_secret: str
    callback_url: str = "http://localhost:8000/auth/callback"
    redirect_uri: str = "http://localhost:8000/docs"
    secure_cookies: bool = False
