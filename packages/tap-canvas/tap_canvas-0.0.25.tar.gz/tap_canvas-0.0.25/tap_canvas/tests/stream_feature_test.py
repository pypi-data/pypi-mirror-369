import os
import pytest
from typing import Dict, Any, List
from tap_canvas.tap import TapCanvas

def get_config_from_env():
    return {
        "api_key": os.getenv("TAP_CANVAS_API_KEY"),
        "base_url": os.getenv("TAP_CANVAS_BASE_URL"),
        "record_limit": int(os.getenv("TAP_CANVAS_RECORD_LIMIT", "5")) or 5,
    }

@pytest.fixture
def config():
    config = get_config_from_env()
    if not config["api_key"] or not config["base_url"]:
        pytest.skip("Environment variables TAP_CANVAS_API_KEY and TAP_CANVAS_BASE_URL required")
    return config

@pytest.fixture
def tap(config):
    return TapCanvas(config=config)

@pytest.fixture
def streams(tap):
    return {stream.name: stream for stream in tap.discover_streams()}

@pytest.fixture
def sample_course_context(streams):
    """Get a sample course context for child stream testing."""
    if "courses" not in streams:
        return None
    
    courses_stream = streams["courses"]
    try:
        # Get the first course record
        for course_record in courses_stream.get_records(context=None):
            return courses_stream.get_child_context(course_record, None)
    except Exception:
        return None
    return None

class TestStreamFeatures:
    def test_all_streams_discovered(self, streams):
        expected_streams = [
            "terms", "courses", "users", "enrollments", "outcome_results", "sections", "assignments"
        ]
        discovered_stream_names = list(streams.keys())
        missing_streams = [stream for stream in expected_streams if stream not in discovered_stream_names]
        assert len(missing_streams) == 0, f"Missing expected streams: {missing_streams}"

    def test_stream_schemas_valid(self, streams):
        for stream_name, stream in streams.items():
            schema = stream.schema
            assert isinstance(schema, dict)
            assert "type" in schema
            assert "properties" in schema
            properties = schema["properties"]
            assert isinstance(properties, dict)
            assert len(properties) > 0

    def test_stream_primary_keys(self, streams):
        expected_primary_keys = {
            "terms": ["id"], "courses": ["id"], "users": ["id"],
            "enrollments": ["id"], "outcome_results": ["id"],
            "sections": ["id"], "assignments": ["id"]
        }
        for stream_name, expected_keys in expected_primary_keys.items():
            if stream_name in streams:
                stream = streams[stream_name]
                actual_keys = stream.primary_keys
                assert actual_keys == expected_keys

    def test_stream_urls_generation(self, streams):
        for stream_name, stream in streams.items():
            try:
                url = stream.get_url({})
                assert url.startswith("http")
                assert "/api/v1" in url
            except Exception as e:
                pytest.fail(f"Stream {stream_name} failed to generate URL: {e}")

    @pytest.mark.parametrize("stream_name", [
        "terms", "courses", "users"
    ])
    def test_individual_stream_data_retrieval_standalone(self, streams, stream_name):
        """Test streams that don't require context."""
        if stream_name not in streams:
            pytest.skip(f"Stream {stream_name} not available")
        
        stream = streams[stream_name]
        try:
            records = []
            record_count = 0
            for record in stream.get_records(context=None):
                records.append(record)
                record_count += 1
                if record_count == 1:
                    assert isinstance(record, dict)
                    assert len(record) > 0
                    if "id" in stream.primary_keys:
                        assert "id" in record
                        assert record["id"] is not None
                if record_count >= 3:
                    break
            assert len(records) <= 5
        except Exception as e:
            pytest.fail(f"Stream {stream_name} failed to retrieve data: {e}")

    @pytest.mark.parametrize("stream_name", [
        "enrollments", "sections", "assignments", "outcome_results"
    ])
    def test_individual_stream_data_retrieval_with_context(self, streams, stream_name, sample_course_context):
        """Test streams that require context (child streams)."""
        if stream_name not in streams:
            pytest.skip(f"Stream {stream_name} not available")
        
        if sample_course_context is None:
            pytest.skip(f"No course context available for testing {stream_name}")
        
        stream = streams[stream_name]
        try:
            records = []
            record_count = 0
            for record in stream.get_records(context=sample_course_context):
                records.append(record)
                record_count += 1
                if record_count == 1:
                    assert isinstance(record, dict)
                    assert len(record) > 0
                    if "id" in stream.primary_keys:
                        assert "id" in record
                        assert record["id"] is not None
                if record_count >= 3:
                    break
            # Note: Child streams may have 0 records for a given course, which is valid
            print(f"Stream {stream_name}: Retrieved {len(records)} records with course context")
        except Exception as e:
            pytest.fail(f"Stream {stream_name} failed to retrieve data with context: {e}")

    @pytest.mark.parametrize("parent_stream_name,child_stream_names", [
        ("courses", ["enrollments", "sections", "assignments", "outcome_results"])
    ])
    def test_stream_data_retrieval_with_context(self, streams, parent_stream_name, child_stream_names):
        if parent_stream_name not in streams:
            pytest.skip(f"Parent stream {parent_stream_name} not available")
        parent_stream = streams[parent_stream_name]
        parent_records = list(parent_stream.get_records(context=None))
        if not parent_records:
            pytest.skip(f"No records found in parent stream {parent_stream_name}")
        parent_record = parent_records[0]
        parent_context = parent_stream.get_child_context(parent_record, None)
        for child_name in child_stream_names:
            if child_name not in streams:
                continue
            child_stream = streams[child_name]
            records = []
            record_count = 0
            try:
                for record in child_stream.get_records(context=parent_context):
                    records.append(record)
                    record_count += 1
                    if record_count >= 3:
                        break
                if records:
                    print(f"{child_name}: Retrieved {len(records)} records from {parent_stream_name} context")
                    print(f"   Sample fields: {list(records[0].keys())[:5]}")
                else:
                    print(f"{child_name}: No data found for context {parent_record.get('id')}")
            except Exception as e:
                pytest.fail(f"Stream {child_name} failed to retrieve data with context: {e}")

    def test_stream_authentication(self, streams):
        for stream_name, stream in streams.items():
            authenticator = stream.authenticator
            assert authenticator is not None
            if hasattr(authenticator, 'token'):
                assert authenticator.token is not None
                assert len(authenticator.token) > 10

    def test_stream_pagination_support(self, streams):
        for stream_name, stream in streams.items():
            assert hasattr(stream, 'get_new_paginator')
            params = stream.get_url_params(context=None, next_page_token=None)
            assert isinstance(params, dict)
            if 'per_page' in params:
                assert params['per_page'] > 0

    def test_canvas_specific_features(self, streams, config):
        if "course_ends_after" in config:
            courses_stream = streams.get("courses")
            if courses_stream:
                _ = courses_stream.get_url_params(context=None, next_page_token=None)
        for stream_name, stream in streams.items():
            if hasattr(stream, '_record_limit'):
                expected_limit = config.get("record_limit")
                actual_limit = stream._record_limit
                if expected_limit:
                    assert actual_limit == expected_limit

    def test_error_handling(self, streams):
        for stream_name, stream in streams.items():
            try:
                invalid_context = {"invalid_parent": {"id": "nonexistent"}}
                _ = list(stream.get_records(context=invalid_context))
            except Exception as e:
                error_msg = str(e).lower()
                assert any(word in error_msg for word in ['not found', 'invalid', 'error', 'unauthorized'])

    def test_submissions_stream_is_discovered(self, streams):
        assert "submissions" in streams, (
            "Expected 'submissions' stream to be discoverable. "
            "Add a SubmissionsStream to STREAM_TYPES."
        )

    def test_submissions_stream_parent_and_path(self, streams, sample_course_context):
        if "submissions" not in streams:
            pytest.skip("Submissions stream not available yet")

        from tap_canvas.streams import CourseStream
        submissions = streams["submissions"]

        assert getattr(submissions, "parent_stream_type", None) is CourseStream

        ctx = sample_course_context or {"course_id": 123}

        url = submissions.get_url(ctx)
        assert url.startswith("http")
        assert "/api/v1" in url
        if ctx.get("course_id") == 123:
            assert "/courses/123/students/submissions" in url

    def test_submissions_stream_schema_minimal_fields(self, streams):
        if "submissions" not in streams:
            pytest.skip("Submissions stream not available yet")

        submissions = streams["submissions"]
        props = submissions.schema["properties"]

        for key in ["id", "assignment_id", "user_id", "score", "grade", "submitted_at", "workflow_state"]:
            assert key in props, f"Missing expected submissions field: {key}"

        assert "id" in submissions.primary_keys
