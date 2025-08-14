"""Test core functionality."""

import pytest
from tap_canvas.tap import TapCanvas
from tap_canvas.streams import CourseStream

SAMPLE_CONFIG = {
    "api_key": "test_key",
    "base_url": "https://test.canvas.instructure.com/api/v1",
    "account_id": "123"
}

def test_tap_initialization():
    """Test that the tap initializes correctly."""
    tap = TapCanvas(config=SAMPLE_CONFIG, parse_env_config=False)
    assert tap.name == "tap-canvas"
    assert tap.config["api_key"] == "test_key"
    assert tap.config["base_url"] == "https://test.canvas.instructure.com/api/v1"

def test_stream_discovery():
    """Test that streams are discovered correctly."""
    tap = TapCanvas(config=SAMPLE_CONFIG, parse_env_config=False)
    streams = tap.discover_streams()
    assert len(streams) > 0

    stream_names = [stream.name for stream in streams]
    expected_streams = ["courses", "users", "enrollments"]

    found_streams = [name for name in expected_streams if name in stream_names]
    assert len(found_streams) > 0

def test_capabilities():
    """Test that capabilities are properly defined."""
    tap = TapCanvas(config=SAMPLE_CONFIG, parse_env_config=False)
    capabilities = tap.capabilities

    assert isinstance(capabilities, list), "Capabilities should be a list"
    assert len(capabilities) > 0, "Should have at least one capability"

    capability_strings = [str(cap) if hasattr(cap, 'value') else cap for cap in capabilities]
    expected_caps = ["about", "catalog", "discover"]

    found_caps = [cap for cap in expected_caps if cap in capability_strings]
    assert len(found_caps) > 0, f"Should have at least some expected capabilities. Found: {capability_strings}"

def test_get_url_params_includes_include_list():
    """Test that 'include' is added to URL params if present in config."""
    config = {
        "api_key": "test_key",
        "base_url": "https://canvas.test/api/v1",
        "account_id": "456",
        "include": ["total_scores", "sections"]
    }

    tap = TapCanvas(config=config, parse_env_config=False)
    stream = CourseStream(tap=tap)
    stream.replication_key = "updated_at"

    context = {"start_date": "2023-01-01T00:00:00Z"}
    params = stream.get_url_params(context=context, next_page_token=None)

    assert "include" in params
    assert sorted(params["include"]) == sorted(["total_scores", "sections"])

