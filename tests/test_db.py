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


@pytest.fixture
def sample_observation():
    """Provide a normalized observation for persistence tests."""
    return Observation(
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


def test_insert_observation(db_conn, sample_observation):
    """Verify that an observation is persisted correctly."""

    observation = sample_observation

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


def test_duplicate_observation(db_conn, sample_observation):
    """Verify that repeated ingestion does not create duplicate rows."""
    first_insert = insert_observations(db_conn, [sample_observation])
    second_insert = insert_observations(db_conn, [sample_observation])

    assert first_insert == 1
    assert second_insert == 0

    count = db_conn.execute(
        """
        SELECT COUNT(*)
        FROM observations
        WHERE source = %s
          AND source_series_id = %s
          AND observed_at = %s
        """,
        (
            sample_observation.source,
            sample_observation.source_series_id,
            sample_observation.observed_at,
        ),
    ).fetchone()[0]

    assert count == 1


def test_insert_empty_batch(db_conn):
    assert insert_observations(db_conn, []) == 0


def test_distinct_observation_timestamps(db_conn, sample_observation):
    from dataclasses import replace
    from datetime import timedelta

    later = replace(
        sample_observation,
        observed_at=sample_observation.observed_at + timedelta(minutes=15),
    )
    assert insert_observations(db_conn, [sample_observation, later]) == 2


def test_mixed_duplicate_and_new_batch(db_conn, sample_observation):
    from dataclasses import replace
    from datetime import timedelta

    later = replace(
        sample_observation,
        observed_at=sample_observation.observed_at + timedelta(minutes=15),
    )
    assert insert_observations(db_conn, [sample_observation]) == 1
    assert insert_observations(db_conn, [sample_observation, later]) == 1


def test_insert_null_observation_value(db_conn, sample_observation):
    """Verify that a missing measurement persists as SQL NULL."""
    from dataclasses import replace

    observation = replace(
        sample_observation,
        source_series_id="test-series-null-value",
        value=None,
    )

    assert insert_observations(db_conn, [observation]) == 1

    row = db_conn.execute(
        """
        SELECT value
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
    assert row[0] is None
