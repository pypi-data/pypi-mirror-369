"""Integration tests using environment variables."""

import os
import pytest
from tap_canvas.tap import TapCanvas

def get_config_from_env():
    """Get configuration from environment variables."""
    return {
        "api_key": os.getenv("TAP_CANVAS_API_KEY"),
        "base_url": os.getenv("TAP_CANVAS_BASE_URL"),
        "record_limit": int(os.getenv("TAP_CANVAS_RECORD_LIMIT", "0")) or None,
        "account_id": os.getenv("TAP_CANVAS_ACCOUNT_ID", "1"),
    }


@pytest.fixture
def config():
    """Config fixture from environment."""
    config = get_config_from_env()
    if not config["api_key"] or not config["base_url"]:
        pytest.skip("Environment variables TAP_CANVAS_API_KEY and TAP_CANVAS_BASE_URL are required for integration tests.")
    return config


def get_test_stream(tap) -> object:
    """Utility to get a testable stream."""
    for stream in tap.discover_streams():
        if stream.name in ["courses", "users", "terms"]:
            return stream
    return None


def test_tap_can_connect(config):
    """Test that the tap can connect to Canvas API."""
    tap = TapCanvas(config=config)
    stream = get_test_stream(tap)
    assert stream is not None, "No suitable test stream found"

    try:
        record = next(stream.get_records(context=None))
        assert record is not None
    except Exception as e:
        pytest.fail(f"Failed to connect and fetch records: {e}")


def test_record_limit_functionality(config):
    """Test that record limiting works with real API calls."""
    config["record_limit"] = 3
    tap = TapCanvas(config=config)
    stream = get_test_stream(tap)
    assert stream is not None, "No suitable test stream found"

    records = list(stream.get_records(context=None))
    assert len(records) <= 3, f"Expected ≤3 records, got {len(records)}"


def test_no_record_limit(config):
    """Test behavior when no record limit is configured."""
    config.pop("record_limit", None)
    tap = TapCanvas(config=config)
    stream = get_test_stream(tap)
    assert stream is not None, "No suitable test stream found"

    count = 0
    for _ in stream.get_records(context=None):
        count += 1
        if count >= 5:
            break
    assert count == 5, "Expected to retrieve at least 5 records when no limit is set"


@pytest.mark.parametrize("limit", [1, 2, 5])
def test_various_record_limits(config, limit):
    """Test that different record limits are respected."""
    config["record_limit"] = limit
    tap = TapCanvas(config=config)
    stream = get_test_stream(tap)
    if stream is None:
        pytest.skip("No suitable test stream found")

    records = list(stream.get_records(context=None))
    assert len(records) <= limit, f"Expected ≤{limit} records, got {len(records)}"

def test_include_fields_affect_response(config):
    """Test that include[] results in enriched records (not a full validation, just sanity)."""
    config = config.copy()
    config["include"] = ["enrollments", "syllabus_body"]
    config["record_limit"] = 3

    tap = TapCanvas(config=config)
    streams = tap.discover_streams()
    
    course_stream = next((s for s in streams if s.name == "courses"), None)
    if not course_stream:
        pytest.skip("Courses stream not available")

    records = list(course_stream.get_records(context=None))

    assert len(records) > 0
    enriched_keys = [k for k in records[0].keys() if k not in ["id", "name"]]
    assert len(enriched_keys) > 0, "Include fields should add extra fields to the response"

    print(f"Include test passed: Got enriched keys {enriched_keys}")

def test_enrollments_includes_grades_object(config):
    local_config = config.copy()

    tap = TapCanvas(config=local_config)
    streams = {s.name: s for s in tap.discover_streams()}
    assert "enrollments" in streams, "Enrollments stream must be discoverable"

    enrollments = streams["enrollments"]
    props = enrollments.schema["properties"]

    assert "grades" in props, "Expected 'grades' object in enrollments schema"
    grades = props["grades"]

    grades_type = grades.get("type")
    if isinstance(grades_type, list):
        assert "object" in grades_type, "'grades' should include 'object' in its type list"
    else:
        assert grades_type == "object", "'grades' should be an object"

    grade_props = grades["properties"]
    for k in ["current_score", "current_grade", "final_score", "final_grade"]:
        assert k in grade_props, f"Missing '{k}' in grades object"

def test_enrollments_grades_has_data(config):
    """Verify that at least one enrollment record contains non empty grades data."""
    local_config = config.copy()
    local_config["record_limit"] = 5

    tap = TapCanvas(config=local_config)
    streams = {s.name: s for s in tap.discover_streams()}

    courses_stream = streams.get("courses")
    enrollments_stream = streams.get("enrollments")
    if not courses_stream or not enrollments_stream:
        pytest.skip("Required streams not available")

    found_with_grades = False
    checked_courses = 0
    max_courses_to_check = 5

    for course in courses_stream.get_records(context=None):
        ctx = courses_stream.get_child_context(course, None) or {}
        if "course_id" not in ctx:
            continue

        try:
            for enr in enrollments_stream.get_records(context=ctx):
                grades = enr.get("grades")
                if isinstance(grades, dict) and any(v is not None for v in grades.values()):
                    found_with_grades = True
                    break
        except Exception:
            pass

        checked_courses += 1
        if found_with_grades or checked_courses >= max_courses_to_check:
            break

    assert found_with_grades, "No enrollment records contained non empty grades data in sampled courses"

