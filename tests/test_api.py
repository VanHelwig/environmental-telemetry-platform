from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from telemetry.api import app

client = TestClient(app)


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_stations():
    expected_stations = [
        {"station_id": "USGS-08019200", "observation_count": 2},
        {"station_id": "USGS-08080700", "observation_count": 1},
    ]

    connection = MagicMock()

    with (
        patch("telemetry.api.get_connection") as mock_connection,
        patch("telemetry.api.get_stations") as mock_get_stations,
    ):
        mock_connection.return_value.__enter__.return_value = connection
        mock_get_stations.return_value = expected_stations

        response = client.get("/stations")

        mock_get_stations.assert_called_once_with(connection)

    assert response.status_code == 200
    assert response.json() == expected_stations


def test_stations_empty():
    with (
        patch("telemetry.api.get_connection"),
        patch("telemetry.api.get_stations", return_value=[]),
    ):
        response = client.get("/stations")

    assert response.status_code == 200
    assert response.json() == []
