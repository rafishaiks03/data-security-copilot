from collections.abc import Generator

import psycopg
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from backend.app.core.config import get_settings

settings = get_settings()


# ============================================================
# SQLAlchemy
# ============================================================

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
)


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


def get_db() -> Generator[Session, None, None]:
    """
    Provide a SQLAlchemy database session.
    """

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# ============================================================
# Psycopg
# ============================================================


def get_database_connection():
    """
    Create a direct psycopg connection.

    Used by API endpoints that execute
    parameterized SQL directly.
    """

    return psycopg.connect(
        host=settings.postgres_host,
        port=settings.postgres_port,
        dbname=settings.postgres_db,
        user=settings.postgres_user,
        password=settings.postgres_password,
    )


# ============================================================
# Database health check
# ============================================================


def check_database_connection() -> bool:
    """
    Verify PostgreSQL connectivity.
    """

    db = SessionLocal()

    try:
        db.execute(text("SELECT 1"))
        return True

    except Exception:
        return False

    finally:
        db.close()
