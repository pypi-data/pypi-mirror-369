"""Test record limit configuration."""

from tap_canvas.client import CanvasStream
from tap_canvas.tap import TapCanvas
from singer_sdk import typing as th


class DummyStream(CanvasStream):
    name = "dummy"
    path = "/dummy"
    primary_keys = ["id"]
    schema = th.PropertiesList(th.Property("id", th.IntegerType)).to_dict()


class DummyResponse:
    """Simple response stub with JSON payload."""

    def __init__(self, record_count=3):
        self.links = {}
        self._json = [{"id": i} for i in range(1, record_count + 1)]

    def json(self):
        return self._json


def test_record_limit_applied():
    """Test that record limit is properly applied."""
    tap = TapCanvas(config={"base_url": "http://example", "api_key": "x", "record_limit": 2})
    stream = DummyStream(tap=tap, config=tap.config)

    response = DummyResponse(record_count=3)
    records = list(stream.parse_response(response))

    assert len(records) == 2
    assert records[0]["id"] == 1
    assert records[1]["id"] == 2


def test_no_record_limit():
    """Test behavior when no record limit is set."""
    tap = TapCanvas(config={"base_url": "http://example", "api_key": "x"})
    stream = DummyStream(tap=tap, config=tap.config)

    response = DummyResponse(record_count=3)
    records = list(stream.parse_response(response))

    assert len(records) == 3
    assert records[0]["id"] == 1
    assert records[1]["id"] == 2
    assert records[2]["id"] == 3


def test_record_limit_zero():
    """Test behavior when record limit is 0."""
    tap = TapCanvas(config={"base_url": "http://example", "api_key": "x", "record_limit": 0})
    stream = DummyStream(tap=tap, config=tap.config)

    response = DummyResponse(record_count=3)
    records = list(stream.parse_response(response))

    assert len(records) == 0
