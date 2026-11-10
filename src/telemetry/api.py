from fastapi import FastAPI

from telemetry.db import get_connection, get_stations

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
