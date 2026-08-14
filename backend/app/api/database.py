"""
Database connection utilities for the Data & Security Copilot API.
"""

from __future__ import annotations

import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv

# ============================================================
# Environment
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

ENV_FILE = PROJECT_ROOT / ".env"

load_dotenv(ENV_FILE)


# ============================================================
# PostgreSQL configuration
# ============================================================

DATABASE_HOST = os.getenv(
    "POSTGRES_HOST",
    "localhost",
)

DATABASE_PORT = int(
    os.getenv(
        "POSTGRES_PORT",
        "5432",
    )
)

DATABASE_NAME = os.getenv(
    "POSTGRES_DB",
    "banking",
)

DATABASE_USER = os.getenv(
    "POSTGRES_USER",
    "postgres",
)

DATABASE_PASSWORD = os.getenv(
    "POSTGRES_PASSWORD",
)


# ============================================================
# Connection
# ============================================================


def get_database_connection():
    """
    Create and return a PostgreSQL connection.

    The API opens a connection when it needs to talk to
    PostgreSQL and closes it after the request finishes.
    """

    if not DATABASE_PASSWORD:
        raise RuntimeError("POSTGRES_PASSWORD is not configured in " f"{ENV_FILE}")

    return psycopg.connect(
        host=DATABASE_HOST,
        port=DATABASE_PORT,
        dbname=DATABASE_NAME,
        user=DATABASE_USER,
        password=DATABASE_PASSWORD,
    )
