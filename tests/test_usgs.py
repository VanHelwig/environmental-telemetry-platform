import httpx

from telemetry.usgs import get_latest_usgs_observations


def test_get_latest_usgs_observations(monkeypatch):
    expected_data = {
        "type": "FeatureCollection",
        "features": [],
        "numberReturned": 0,
    }

    def mock_get(url, params):
        return httpx.Response(
            200,
            json=expected_data,
            request=httpx.Request("GET", url, params=params),
        )

    monkeypatch.setattr(httpx, "get", mock_get)

    result = get_latest_usgs_observations("00060", "48", 5)

    assert result == expected_data