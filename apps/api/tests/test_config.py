import pytest

from src.config import Settings


def test_database_url_uses_railway_database_url_for_unresolved_reference(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@postgres.internal:5432/buildcost")

    settings = Settings(database_url="${{Postgres.DATABASE_URL}}")

    assert settings.database_url == "postgresql+psycopg://user:pass@postgres.internal:5432/buildcost"


def test_database_url_normalizes_postgres_scheme() -> None:
    settings = Settings(database_url="postgres://user:pass@localhost:5432/buildcost")

    assert settings.database_url == "postgresql+psycopg://user:pass@localhost:5432/buildcost"


def test_unresolved_database_reference_fails_without_railway_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)

    with pytest.raises(ValueError, match="unresolved reference"):
        Settings(database_url="${{Postgres.DATABASE_URL}}")
