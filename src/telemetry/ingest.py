"""Fetch, normalize, and persist USGS observations."""

import argparse

from telemetry.db import get_connection, insert_observations
from telemetry.usgs import (
    USGS_METRICS,
    get_latest_usgs_observations,
    normalize_usgs_collection,
)


def positive_int(value: str) -> int:
    """Validate a positive integer CLI argument."""
    number = int(value)

    if number < 1:
        raise argparse.ArgumentTypeError("Value must be greater than zero")

    return number


def parse_args() -> argparse.Namespace:
    """Parse ingestion configuration from command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Ingest USGS observations into PostgreSQL."
    )

    parser.add_argument(
        "--parameter",
        default="00060",
        choices=USGS_METRICS.keys(),
        help="USGS parameter code (default: 00060)",
    )

    parser.add_argument(
        "--state",
        default="48",
        help="Two-digit state FIPS code (default: 48)",
    )

    parser.add_argument(
        "--limit",
        type=positive_int,
        default=5,
        help="Maximum observations to retrieve (default: 5)",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    collection = get_latest_usgs_observations(
        parameter_code=args.parameter,
        state_code=args.state,
        limit=args.limit,
    )

    observations = normalize_usgs_collection(collection)

    with get_connection() as conn:
        inserted = insert_observations(conn, observations)

    print(f"Retrieved {len(observations)} USGS observations")
    print(f"Inserted {inserted} new observations")


if __name__ == "__main__":
    main()
