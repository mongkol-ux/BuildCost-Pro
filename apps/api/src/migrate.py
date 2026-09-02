"""Apply checked-in SQL migrations in order for the deployed API."""
from pathlib import Path
from sqlalchemy import text
from .database import engine


def main() -> None:
    root = Path(__file__).resolve().parents[1] / "migrations"
    migrations = sorted(root.glob("*.sql"))
    with engine.begin() as connection:
        for migration in migrations:
            connection.execute(text(migration.read_text(encoding="utf-8")))
            print(f"APPLIED_MIGRATION={migration.name}")


if __name__ == "__main__":
    main()
