import pytest

from src.config import Settings


def test_database_url_uses_railway_database_url_for_unresolved_reference(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@postgres.internal:5432/buildcost")

    settings = Settings(database_url="${{Postgres.DATABASE_URL}}")

    assert settings.database_url == "postgresql+psycopg://user:pass@postgres.internal:5432/buildcost"


def test_database_url_falls_back_when_primary_value_is_malformed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgres://user:pass@postgres.internal:5432/buildcost")

    settings = Settings(database_url="Postgres -> DATABASE_URL")

    assert settings.database_url == "postgresql+psycopg://user:pass@postgres.internal:5432/buildcost"


def test_database_url_normalizes_postgres_scheme() -> None:
    settings = Settings(database_url="postgres://user:pass@localhost:5432/buildcost")

    assert settings.database_url == "postgresql+psycopg://user:pass@localhost:5432/buildcost"


def test_database_url_strips_accidental_quotes() -> None:
    settings = Settings(database_url='"postgresql://user:pass@localhost:5432/buildcost"')

    assert settings.database_url == "postgresql+psycopg://user:pass@localhost:5432/buildcost"


def test_database_url_rejects_non_postgresql_scheme() -> None:
    with pytest.raises(ValueError, match="must be a PostgreSQL URL"):
        Settings(database_url="mysql://user:pass@localhost:3306/buildcost", _env_file=None)


def test_unresolved_database_reference_fails_without_railway_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)

    with pytest.raises(ValueError, match="unresolved reference"):
        Settings(database_url="${{Postgres.DATABASE_URL}}")


def test_production_defaults_to_connection_validation() -> None:
    settings = Settings(
        environment="production",
        jwt_secret="production-test-secret-0123456789-abcdefghijklmnopqrstuvwxyz",
        database_url="postgresql+psycopg://user:pass@localhost:5432/buildcost",
    )

    assert settings.database_bootstrap == "validate"


def test_production_rejects_create_all_bootstrap() -> None:
    with pytest.raises(ValueError, match="create_all is not allowed"):
        settings = Settings(
            environment="production",
            jwt_secret="production-test-secret-0123456789-abcdefghijklmnopqrstuvwxyz",
            database_url="postgresql+psycopg://user:pass@localhost:5432/buildcost",
            database_bootstrap="create_all",
        )
        settings.validate_production_secrets()
