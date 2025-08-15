"""canvas tap class."""

from typing import List

from singer_sdk import Tap, Stream
from singer_sdk import typing as th
from tap_canvas import __version__

from tap_canvas.streams import (
    EnrollmentTermStream,
    CourseStream,
    OutcomeResultStream,
    EnrollmentsStream,
    UsersStream,
    SectionsStream,
    AssignmentsStream,
    SubmissionsStream
)


STREAM_TYPES = [
    EnrollmentTermStream,
    CourseStream,
    OutcomeResultStream,
    EnrollmentsStream,
    UsersStream,
    SectionsStream,
    AssignmentsStream,
    SubmissionsStream 
]


class TapCanvas(Tap):
    """Canvas tap class."""

    name = "tap-canvas"

    disable_default_logging_config_file = True

    __version__ = __version__

    config_jsonschema = th.PropertiesList(
        th.Property(
            "api_key",
            th.StringType,
            required=True,
            description="The token to authenticate against the API service",
        ),
        th.Property(
            "base_url",
            th.StringType,
            required=True,
            description="The base URL for the Canvas API (e.g., https://canvas.instructure.com/api/v1)",
        ),
        th.Property(
            "account_id",
            th.StringType,
            description="Canvas account ID to use when querying /accounts/{account_id}/courses. Default is 1.",
        ),
        th.Property(
            "course_ends_after",
            th.DateTimeType,
            description="Limit courses queried to courses that end after this date.",
        ),
        th.Property(
            "start_date", 
            th.DateTimeType, 
            description="Start date for incremental syncs. If set, will be used to filter records based on the replication key.",
        ),
        th.Property(
            "record_limit",
            th.IntegerType,
            description="Maximum number of records to return per stream",
        ),
        th.Property(
            "include", 
            th.ArrayType(th.StringType),
            description="List of additional fields to include in the API response, e.g., ['total_scores', 'sections']"
        ),
    ).to_dict()


    def discover_streams(self) -> List[Stream]:
        """Return a list of discovered streams."""
        return [stream_class(tap=self) for stream_class in STREAM_TYPES]
