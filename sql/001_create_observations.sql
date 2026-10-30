-- Environmental Telemetry Platform
-- Migration 001: Initial observations schema

-- Enable PostGIS for geographic data types and functions.
CREATE EXTENSION IF NOT EXISTS postgis;

-- Store normalized environmental observations.
CREATE TABLE observations (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    -- Data source and measurement identifiers
    source TEXT NOT NULL,
    source_series_id TEXT NOT NULL,
    station_id TEXT NOT NULL,

    -- Measurement data
    metric TEXT NOT NULL,
    value NUMERIC,
    unit TEXT NOT NULL,

    -- Observation and ingestion timestamps
    observed_at TIMESTAMPTZ NOT NULL,
    ingested_at TIMESTAMPTZ NOT NULL,

    -- Geographic location (WGS84)
    location GEOGRAPHY(Point, 4326) NOT NULL,

    -- Source-specific quality metadata
    source_quality JSONB NOT NULL DEFAULT '{}'::jsonb,

    -- Prevent duplicate observations from repeated ingestion.
    CONSTRAINT observations_unique_measurement
        UNIQUE (source, source_series_id, observed_at)
);

-- Support retrieval of recent observations for a station.
CREATE INDEX observations_station_time_idx
    ON observations (station_id, observed_at DESC);