from fastapi import FastAPI, Query

from telemetry.db import (
    get_connection,
    get_station_observations,
    get_stations,
)

app = FastAPI(
    title="Environmental Telemetry Platform",
    version="0.1.0",
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/stations")
def stations() -> list[dict]:
    with get_connection() as conn:
        return get_stations(conn)


@app.get("/stations/{station_id}/observations")
def station_observations(
    station_id: str,
    limit: int = Query(default=100, ge=1, le=1000),
) -> list[dict]:
    with get_connection() as conn:
        return get_station_observations(conn, station_id, limit)
