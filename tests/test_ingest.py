"""Unit tests for ingestion CLI and orchestration."""

import argparse
from types import SimpleNamespace

import pytest

from telemetry import ingest


def test_positive_int_accepts_valid_number():
    assert ingest.positive_int("5") == 5


def test_positive_int_rejects_zero():
    with pytest.raises(argparse.ArgumentTypeError, match="greater than zero"):
        ingest.positive_int("0")


def test_positive_int_rejects_negative():
    with pytest.raises(argparse.ArgumentTypeError, match="greater than zero"):
        ingest.positive_int("-3")


def test_main_persists_and_reports_observations(monkeypatch, capsys):
    args = SimpleNamespace(parameter="00060", state="48", limit=5)
    collection = {"type": "FeatureCollection", "features": []}
    observations = [object(), object()]
    calls = []

    class FakeConnection:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            return False

    def fetch(parameter_code, state_code, limit):
        calls.append(("fetch", parameter_code, state_code, limit))
        return collection

    def normalize(payload):
        assert payload is collection
        calls.append(("normalize",))
        return observations

    def insert(conn, batch):
        assert isinstance(conn, FakeConnection)
        assert batch is observations
        calls.append(("insert",))
        return 1

    monkeypatch.setattr(ingest, "parse_args", lambda: args)
    monkeypatch.setattr(ingest, "get_latest_usgs_observations", fetch)
    monkeypatch.setattr(ingest, "normalize_usgs_collection", normalize)
    monkeypatch.setattr(ingest, "get_connection", FakeConnection)
    monkeypatch.setattr(ingest, "insert_observations", insert)

    ingest.main()

    assert calls == [("fetch", "00060", "48", 5), ("normalize",), ("insert",)]
    assert capsys.readouterr().out.splitlines() == [
        "Retrieved 2 USGS observations",
        "Inserted 1 new observations",
    ]
