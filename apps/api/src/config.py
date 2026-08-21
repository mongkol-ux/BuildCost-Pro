from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "BuildCost Pro API"
    app_version: str = "1.1.0"
    environment: str = "development"
    database_url: str = "sqlite:///./buildcost.db"
    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    model_config = SettingsConfigDict(env_file=".env", env_prefix="BUILD_COST_", extra="ignore")


settings = Settings()


def assert_secure_configuration() -> None:
    if settings.environment.lower() in {"production", "prod"} and settings.jwt_secret_key == "change-me-in-production":
        raise RuntimeError("BUILD_COST_JWT_SECRET_KEY must be changed in production")
