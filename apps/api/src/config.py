"""Runtime configuration for the authentication boundary."""
from functools import lru_cache
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="BUILD_COST_", extra="ignore")

    app_name: str = "BuildCost Pro API"
    environment: str = "development"
    database_url: str = "postgresql+psycopg://buildcost:buildcost@localhost:5432/buildcost"
    jwt_secret: str = Field(min_length=32)
    jwt_issuer: str = "buildcost-pro"
    access_token_minutes: int = 15
    refresh_token_days: int = 30
    verification_token_minutes: int = 30
    reset_token_minutes: int = 30
    login_max_attempts: int = 5
    login_lock_minutes: int = 15
    cookie_secure: bool = True


@lru_cache
def get_settings() -> Settings:
    return Settings()
