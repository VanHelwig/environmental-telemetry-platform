"""Unit tests for ingestion CLI and orchestration."""

import argparse
from types import SimpleNamespace

import pytest

from telemetry import ingest


def test_positive_int_accepts_valid_number():
    assert ingest.positive_int("5") == 5
