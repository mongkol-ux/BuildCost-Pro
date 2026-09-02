"""Central SQLAlchemy engine, sessions, and safe startup bootstrap."""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from .auth_models import Base
from .config import get_settings

settings = get_settings()
engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


def bootstrap_database() -> None:
    """Validate or initialize the database according to explicit configuration.

    Production defaults to connection validation only. Metadata auto-creation
    is available for development/test environments through
    BUILD_COST_DATABASE_BOOTSTRAP=create_all and is rejected in production.
    Checked-in SQL migrations remain the authoritative production schema path.
    """
    if settings.database_bootstrap == "none":
        return

    with engine.begin() as connection:
        connection.execute(text("SELECT 1"))
        if settings.database_bootstrap == "create_all":
            Base.metadata.create_all(bind=connection)
