"""Runtime configuration for the authentication and security boundary."""
import os
from functools import lru_cache
from typing import Literal

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import make_url


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="BUILD_COST_", extra="ignore")

    app_name: str = "BuildCost Pro API"
    environment: str = "development"
    database_url: str = "postgresql+psycopg://buildcost:buildcost@localhost:5432/buildcost"
    database_bootstrap: Literal["none", "validate", "create_all"] = "none"
    jwt_secret: str = Field(default="dev-only-change-this-secret-before-production-32", min_length=32)
    jwt_issuer: str = "buildcost-pro"
    access_token_minutes: int = 15
    refresh_token_days: int = 30
    verification_token_minutes: int = 30
    reset_token_minutes: int = 30
    login_max_attempts: int = 5
    login_lock_minutes: int = 15
    cookie_secure: bool = True
    allowed_hosts: str = "localhost,127.0.0.1,testserver,healthcheck.railway.app,*.up.railway.app"
    cors_origins: str = "http://localhost:3000"

    @staticmethod
    def _normalize_database_candidate(value: str) -> str:
        candidate = value.strip().strip("\"'")
        if candidate.startswith("postgres://"):
            candidate = "postgresql+psycopg://" + candidate.removeprefix("postgres://")
        elif candidate.startswith("postgresql://"):
            candidate = "postgresql+psycopg://" + candidate.removeprefix("postgresql://")
        if not candidate.startswith("postgresql+psycopg://"):
            raise ValueError("not a PostgreSQL URL")
        make_url(candidate)
        return candidate

    @model_validator(mode="after")
    def normalize_and_validate_database(self) -> "Settings":
        """Resolve and normalize Railway Postgres URLs without exposing secrets."""
        primary = self.database_url.strip()
        candidates: list[str] = []

        # If BUILD_COST_DATABASE_URL was explicitly supplied, it is authoritative.
        # Otherwise prefer Railway's standard DATABASE_URL over the local-dev default.
        explicit_primary = os.getenv("BUILD_COST_DATABASE_URL", "").strip()
        railway_database_url = os.getenv("DATABASE_URL", "").strip()
        if explicit_primary:
            candidates.append(primary)
        elif railway_database_url:
            candidates.append(railway_database_url)
        else:
            candidates.append(primary)

        # If the explicit primary is unresolved or malformed, Railway's standard
        # DATABASE_URL is a safe fallback. Secrets are never included in errors.
        if railway_database_url and railway_database_url not in candidates:
            candidates.append(railway_database_url)

        normalized: str | None = None
        for candidate in candidates:
            if candidate.startswith("${{") and candidate.endswith("}}"):
                continue
            try:
                normalized = self._normalize_database_candidate(candidate)
                break
            except Exception:
                continue

        if normalized is None:
            if primary.startswith("${{") and primary.endswith("}}"):
                raise ValueError(
                    "BUILD_COST_DATABASE_URL contains an unresolved reference and DATABASE_URL is unavailable or invalid"
                )
            raise ValueError("BUILD_COST_DATABASE_URL is not a valid PostgreSQL URL")

        self.database_url = normalized
        if self.environment == "production" and self.database_bootstrap == "none":
            self.database_bootstrap = "validate"
        return self

    def get_allowed_hosts(self) -> list[str]:
        hosts = {h.strip() for h in self.allowed_hosts.split(",") if h.strip()}
        if self.environment == "production":
            hosts.update({"healthcheck.railway.app", "*.up.railway.app"})
            railway_public_domain = os.getenv("RAILWAY_PUBLIC_DOMAIN", "").strip()
            if railway_public_domain:
                hosts.add(railway_public_domain)
        return sorted(hosts)

    def get_cors_origins(self) -> list[str]:
        origins = {item.strip() for item in self.cors_origins.split(",") if item.strip()}
        if self.environment == "production":
            origins.add("https://buildcost-pro-production.up.railway.app")
        return sorted(origins)

    def validate_production_secrets(self) -> None:
        if self.environment == "production":
            if self.jwt_secret.startswith("dev-only-"):
                raise ValueError("BUILD_COST_JWT_SECRET must be replaced in production")
            if len(self.jwt_secret) < 32:
                raise ValueError("BUILD_COST_JWT_SECRET must be at least 32 characters in production")
            if not self.cookie_secure:
                raise ValueError("BUILD_COST_COOKIE_SECURE must remain enabled in production")
            if self.database_bootstrap == "create_all":
                raise ValueError("BUILD_COST_DATABASE_BOOTSTRAP=create_all is not allowed in production")
            origins = set(self.get_cors_origins())
            if "*" in origins or any(origin.startswith("http://localhost") for origin in origins):
                raise ValueError("BUILD_COST_CORS_ORIGINS must not allow wildcard or localhost in production")


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.validate_production_secrets()
    return settings
