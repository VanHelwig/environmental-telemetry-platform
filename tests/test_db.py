"""Integration tests for PostgreSQL observation persistence."""

import os
from datetime import UTC, datetime
from decimal import Decimal

import psycopg
import pytest

from telemetry.db import insert_observations
from telemetry.models import Observation

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


def test_insert_observation(db_conn):
    """Verify that an observation is persisted correctly."""

    observation = Observation(
        source="test",
        source_series_id="test-series-001",
        station_id="TEST-001",
        metric="streamflow",
        value=Decimal("42.75"),
        unit="ft^3/s",
        observed_at=datetime(2026, 1, 1, 12, 0, tzinfo=UTC),
        ingested_at=datetime(2026, 1, 1, 12, 5, tzinfo=UTC),
        latitude=30.2672,
        longitude=-97.7431,
        source_quality={"status": "approved", "test": True},
    )

    inserted = insert_observations(db_conn, [observation])

    assert inserted == 1

    row = db_conn.execute(
        """
        SELECT
            source,
            source_series_id,
            station_id,
            metric,
            value,
            unit,
            observed_at,
            ingested_at,
            ST_Y(location::geometry) AS latitude,
            ST_X(location::geometry) AS longitude,
            source_quality
        FROM observations
        WHERE source = %s
          AND source_series_id = %s
          AND observed_at = %s
        """,
        (
            observation.source,
            observation.source_series_id,
            observation.observed_at,
        ),
    ).fetchone()

    assert row is not None

    assert row[0] == observation.source
    assert row[1] == observation.source_series_id
    assert row[2] == observation.station_id
    assert row[3] == observation.metric
    assert row[4] == observation.value
    assert row[5] == observation.unit
    assert row[6] == observation.observed_at
    assert row[7] == observation.ingested_at
    assert row[8] == observation.latitude
    assert row[9] == observation.longitude
    assert row[10] == observation.source_quality
