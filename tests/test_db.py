"""Integration tests for PostgreSQL observation persistence."""

import os

import psycopg
import pytest

pytestmark = pytest.mark.integration


@pytest.fixture
def db_conn():
    """Provide a database connection and roll back test changes."""
    database_url = os.environ.get("DATABASE_URL")

    if not database_url:
        pytest.skip("DATABASE_URL is not configured")

    conn = psycopg.connect(database_url)

    try:
        yield conn
    finally:
        conn.rollback()
        conn.close()
