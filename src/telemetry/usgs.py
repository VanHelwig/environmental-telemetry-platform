from datetime import UTC, datetime
from decimal import Decimal

import httpx

from telemetry.models import Observation

USGS_API_URL = (
    "https://api.waterdata.usgs.gov/ogcapi/v1/collections/latest-continuous/items"
)

USGS_METRICS = {
    "00060": "streamflow",
}


def get_latest_usgs_observations(
    parameter_code: str, state_code: str, limit: int = 5
) -> dict:
    """Fetch the latest USGS observations for a parameter and state."""
    params = {
        "parameter_code": parameter_code,
        "state_code": state_code,
        "limit": limit,
    }
    r = httpx.get(USGS_API_URL, params=params)
    r.raise_for_status()
    return r.json()


def normalize_usgs_observation(feature: dict) -> Observation:
    """Convert one USGS GeoJSON Feature into a platform Observation."""
    properties = feature["properties"]
    coordinates = feature["geometry"]["coordinates"]
    parameter_code = properties["parameter_code"]
    if parameter_code not in USGS_METRICS:
        raise ValueError(f"Unsupported USGS parameter code: {parameter_code}")
    raw_value = properties["value"]
    value = Decimal(raw_value) if raw_value is not None else None
    observed_at = datetime.fromisoformat(properties["time"])
    if observed_at.utcoffset() is None:
        raise ValueError("USGS observation timestamp must include a timezone")
    return Observation(
        source="usgs",
        source_series_id=properties["time_series_id"],
        station_id=properties["monitoring_location_id"],
        metric=USGS_METRICS[parameter_code],
        value=value,
        unit=properties["unit_of_measure"],
        observed_at=observed_at,
        ingested_at=datetime.now(UTC),
        latitude=coordinates[1],
        longitude=coordinates[0],
        source_quality={
            "approval_status": properties.get("approval_status"),
            "qualifier": properties.get("qualifier"),
        },
    )


def normalize_usgs_collection(collection: dict) -> list[Observation]:
    """Normalize all Features in a USGS GeoJSON FeatureCollection."""
    if collection["type"] != "FeatureCollection":
        raise ValueError("Expected a GeoJSON FeatureCollection")
    return [normalize_usgs_observation(feature) for feature in collection["features"]]
