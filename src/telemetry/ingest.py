"""Fetch, normalize, and persist USGS observations."""

from telemetry.db import get_connection, insert_observations
from telemetry.usgs import (
    get_latest_usgs_observations,
    normalize_usgs_collection,
)


def main() -> None:
    collection = get_latest_usgs_observations(
        parameter_code="00060",
        state_code="48",
        limit=5,
    )

    observations = normalize_usgs_collection(collection)

    with get_connection() as conn:
        inserted = insert_observations(conn, observations)

    print(f"Retrieved {len(observations)} USGS observations")
    print(f"Inserted {inserted} new observations")


if __name__ == "__main__":
    main()