"""Run a small USGS ingestion sample without persistence."""

from telemetry.usgs import get_latest_usgs_observations, normalize_usgs_collection


def main() -> None:
    collection = get_latest_usgs_observations(
        parameter_code="00060", state_code="48", limit=5
    )
    observations = normalize_usgs_collection(collection)
    print(f"Normalized {len(observations)} USGS observations")
    for observation in observations:
        print(observation)


if __name__ == "__main__":
    main()
