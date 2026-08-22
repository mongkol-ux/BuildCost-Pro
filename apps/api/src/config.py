"""Runtime configuration for the authentication boundary."""
import os
from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="BUILD_COST_", extra="ignore")

    app_name: str = "BuildCost Pro API"
    environment: str = "development"
    database_url: str = "postgresql+psycopg://buildcost:buildcost@localhost:5432/buildcost"
    jwt_secret: str = Field(default="dev-only-change-this-secret-before-production-32", min_length=32)
    jwt_issuer: str = "buildcost-pro"
    access_token_minutes: int = 15
    refresh_token_days: int = 30
    verification_token_minutes: int = 30
    reset_token_minutes: int = 30
    login_max_attempts: int = 5
    login_lock_minutes: int = 15
    cookie_secure: bool = True
    # Railway healthchecks originate from healthcheck.railway.app.
    # In production, these mandatory Railway hosts are always retained even
    # when BUILD_COST_ALLOWED_HOSTS is supplied as an override.
    allowed_hosts: str = "localhost,127.0.0.1,testserver,healthcheck.railway.app,*.up.railway.app"
    cors_origins: str = "http://localhost:3000"

    def get_allowed_hosts(self) -> list[str]:
        hosts = {h.strip() for h in self.allowed_hosts.split(",") if h.strip()}
        if self.environment == "production":
            hosts.update({"healthcheck.railway.app", "*.up.railway.app"})
            railway_public_domain = os.getenv("RAILWAY_PUBLIC_DOMAIN", "").strip()
            if railway_public_domain:
                hosts.add(railway_public_domain)
        return sorted(hosts)

    def validate_production_secrets(self) -> None:
        if self.environment == "production":
            if self.jwt_secret.startswith("dev-only-"):
                raise ValueError("BUILD_COST_JWT_SECRET must be replaced in production")
            if len(self.jwt_secret) < 32:
                raise ValueError("BUILD_COST_JWT_SECRET must be at least 32 characters in production")
            if not self.cookie_secure:
                raise ValueError("BUILD_COST_COOKIE_SECURE must remain enabled in production")


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.validate_production_secrets()
    return settings
