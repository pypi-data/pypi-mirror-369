"""Test core functionality - basic tests only."""

import pytest
from tap_canvas.tap import TapCanvas

SAMPLE_CONFIG = {
    "api_key": "test_key",
    "base_url": "https://test.canvas.instructure.com/api/v1",
    "account_id": "123"
}


def test_tap_initialization():
    """Test that the tap initializes correctly."""
    tap = TapCanvas(config=SAMPLE_CONFIG)
    assert tap.name == "tap-canvas"
    assert tap.config["api_key"] == "test_key"
    assert tap.config["base_url"] == "https://test.canvas.instructure.com/api/v1"


def test_stream_discovery():
    """Test that streams are discovered correctly."""
    tap = TapCanvas(config=SAMPLE_CONFIG)
    streams = tap.discover_streams()
    assert len(streams) > 0
    
    stream_names = [stream.name for stream in streams]
    print(f"Found streams: {stream_names}")
    
    assert len(stream_names) > 0, "Should discover at least one stream"


def test_capabilities():
    """Test that capabilities are properly defined."""
    tap = TapCanvas(config=SAMPLE_CONFIG)
    capabilities = tap.capabilities
    
    assert isinstance(capabilities, list), "Capabilities should be a list"
    assert len(capabilities) > 0, "Should have at least one capability"
    
    print(f"Found capabilities: {capabilities}")


def test_config_schema():
    """Test that config schema is properly defined."""
    tap = TapCanvas(config=SAMPLE_CONFIG)
    schema = tap.config_jsonschema
    
    assert isinstance(schema, dict), "Config schema should be a dict"
    assert "properties" in schema, "Config schema should have properties"
    
    properties = schema["properties"]
    assert "api_key" in properties, "Should have api_key property"
    assert "base_url" in properties, "Should have base_url property"
    assert "account_id" in properties, "Should have account_id property"