"""PostgreSQL connection management for the telemetry platform."""

import os
from collections.abc import Sequence

import psycopg
from psycopg import Connection
from psycopg.types.json import Jsonb

from telemetry.models import Observation


def get_connection() -> Connection:
    """Create a PostgreSQL connection using DATABASE_URL."""
    database_url = os.environ["DATABASE_URL"]
    return psycopg.connect(database_url)


def insert_observations(
    conn: psycopg.Connection,
    observations: Sequence[Observation],
) -> int:
    """Insert observations, skipping duplicates.

    Returns the number of newly inserted observations.
    The caller manages the transaction.
    """
    query = """
        INSERT INTO observations (
            source,
            source_series_id,
            station_id,
            metric,
            value,
            unit,
            observed_at,
            ingested_at,
            location,
            source_quality
        )
        VALUES (
            %s, %s, %s, %s, %s,
            %s, %s, %s,
            ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography,
            %s
        )
        ON CONFLICT (source, source_series_id, observed_at)
        DO NOTHING
    """

    inserted = 0

    with conn.cursor() as cur:
        for observation in observations:
            cur.execute(
                query,
                (
                    observation.source,
                    observation.source_series_id,
                    observation.station_id,
                    observation.metric,
                    observation.value,
                    observation.unit,
                    observation.observed_at,
                    observation.ingested_at,
                    observation.longitude,
                    observation.latitude,
                    Jsonb(observation.source_quality),
                ),
            )
            inserted += cur.rowcount

    return inserted


def get_stations(conn) -> list[dict]:
    """Return stations with stored observations."""
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT
                station_id,
                COUNT(*) AS observation_count
            FROM observations
            GROUP BY station_id
            ORDER BY station_id
            """
        )
        return [
            {
                "station_id": station_id,
                "observation_count": count,
            }
            for station_id, count in cur.fetchall()
        ]


def get_station_observations(
    conn: psycopg.Connection,
    station_id: str,
    limit: int = 100,
) -> list[dict]:
    """Return the latest observations for a station."""
    query = """
        SELECT
            source,
            source_series_id,
            station_id,
            metric,
            value,
            unit,
            observed_at,
            ST_Y(location::geometry) AS latitude,
            ST_X(location::geometry) AS longitude,
            source_quality
        FROM observations
        WHERE station_id = %s
        ORDER BY observed_at DESC, id DESC
        LIMIT %s
    """

    with conn.cursor() as cur:
        cur.execute(query, (station_id, limit))
        rows = cur.fetchall()

    return [
        {
            "source": row[0],
            "source_series_id": row[1],
            "station_id": row[2],
            "metric": row[3],
            "value": float(row[4]) if row[4] is not None else None,
            "unit": row[5],
            "observed_at": row[6].isoformat(),
            "latitude": row[7],
            "longitude": row[8],
            "source_quality": row[9],
        }
        for row in rows
    ]
