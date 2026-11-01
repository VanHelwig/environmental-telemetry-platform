from datetime import UTC, datetime
from decimal import Decimal

import httpx
import pytest

from telemetry.usgs import (
    get_latest_usgs_observations,
    normalize_usgs_collection,
    normalize_usgs_observation,
)


def sample_feature(value="49.5", parameter_code="00060"):
    return {
        "type": "Feature",
        "properties": {
            "time_series_id": "series-1",
            "monitoring_location_id": "USGS-08080700",
            "parameter_code": parameter_code,
            "value": value,
            "unit_of_measure": "ft^3/s",
            "time": "2026-09-17T19:15:00+00:00",
            "approval_status": "Provisional",
            "qualifier": None,
        },
        "geometry": {"type": "Point", "coordinates": [-101.70267, 34.17896]},
    }


def test_get_latest_usgs_observations(monkeypatch):
    expected_data = {"type": "FeatureCollection", "features": [], "numberReturned": 0}

    def mock_get(url, params):
        return httpx.Response(
            200,
            json=expected_data,
            request=httpx.Request("GET", url, params=params),
        )

    monkeypatch.setattr(httpx, "get", mock_get)
    assert get_latest_usgs_observations("00060", "48", 5) == expected_data


def test_normalize_usgs_observation():
    observation = normalize_usgs_observation(sample_feature())
    assert observation.source == "usgs"
    assert observation.source_series_id == "series-1"
    assert observation.station_id == "USGS-08080700"
    assert observation.metric == "streamflow"
    assert observation.value == Decimal("49.5")
    assert observation.unit == "ft^3/s"
    assert observation.observed_at == datetime(2026, 9, 17, 19, 15, tzinfo=UTC)
    assert observation.ingested_at.tzinfo is not None
    assert observation.latitude == 34.17896
    assert observation.longitude == -101.70267
    assert observation.source_quality == {
        "approval_status": "Provisional",
        "qualifier": None,
    }


def test_missing_value():
    assert normalize_usgs_observation(sample_feature(value=None)).value is None


def test_unsupported_parameter():
    with pytest.raises(ValueError, match="Unsupported USGS parameter code"):
        normalize_usgs_observation(sample_feature(parameter_code="99999"))


def test_collection_normalization():
    collection = {
        "type": "FeatureCollection",
        "features": [sample_feature(), sample_feature(value=None)],
    }
    observations = normalize_usgs_collection(collection)
    assert len(observations) == 2
    assert observations[0].value == Decimal("49.5")
    assert observations[1].value is None


def test_collection_rejects_wrong_type():
    with pytest.raises(ValueError, match="FeatureCollection"):
        normalize_usgs_collection({"type": "Feature", "features": []})


def test_empty_collection():
    collection = {"type": "FeatureCollection", "features": []}
    assert normalize_usgs_collection(collection) == []


def test_naive_timestamp():
    feature = sample_feature()
    feature["properties"]["time"] = "2026-09-17T19:15:00"
    with pytest.raises(ValueError, match="timezone"):
        normalize_usgs_observation(feature)


def test_invalid_numeric_value():
    from decimal import InvalidOperation

    with pytest.raises(InvalidOperation):
        normalize_usgs_observation(sample_feature(value="not-a-number"))
