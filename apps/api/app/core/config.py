from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", hide_input_in_errors=True)

    app_env: Literal["local", "test", "production"] = "local"
    database_url: str = "sqlite:///./debug_ed.db"
    auth_mode: Literal["demo", "cognito"] = "cognito"
    cors_origins: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    cognito_region: str = ""
    cognito_user_pool_id: str = ""
    cognito_client_id: str = ""
    ai_provider: Literal["demo", "openrouter"] = "demo"
    openrouter_api_key: SecretStr = SecretStr("")
    openrouter_model: str = ""
    ai_max_output_tokens: int = Field(default=1000, ge=1, le=8192)

    @model_validator(mode="after")
    def validate_runtime(self):
        if self.app_env == "production":
            if self.auth_mode == "demo":
                raise ValueError("Demo authentication is forbidden in production")
            if not self.database_url.startswith("postgresql+psycopg://"):
                raise ValueError("Production requires PostgreSQL")
            if any(not origin.startswith("https://") for origin in self.cors_origins):
                raise ValueError("Production CORS origins must use HTTPS")
        if self.auth_mode == "cognito" and not all(
            [self.cognito_region, self.cognito_user_pool_id, self.cognito_client_id]
        ):
            raise ValueError("Configure Cognito or explicitly enable AUTH_MODE=demo locally")
        if self.ai_provider == "openrouter" and not all(
            [self.openrouter_api_key.get_secret_value(), self.openrouter_model]
        ):
            raise ValueError("OpenRouter requires an API key and an explicit model ID")
        return self

    @property
    def cognito_issuer(self) -> str:
        return (
            f"https://cognito-idp.{self.cognito_region}.amazonaws.com/{self.cognito_user_pool_id}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
