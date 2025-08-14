"""REST client handling, including canvasStream base class."""

import requests
from urllib import parse
from pathlib import Path
from typing import Any, Dict, Optional, Union, List, Iterable

from memoization import cached
from singer_sdk.helpers.jsonpath import extract_jsonpath
from singer_sdk.pagination import BaseAPIPaginator
from singer_sdk.streams import RESTStream
from singer_sdk.authenticators import BearerTokenAuthenticator

SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")


class CanvasPaginator(BaseAPIPaginator):
    """Paginator for Canvas API using link headers."""

    def __init__(self, record_limit: Optional[int] = None):
        # Canvas API pagination starts at page 1
        super().__init__(start_value=1)
        self.record_limit = record_limit
        self.record_count = 0

    def get_next(self, response: requests.Response) -> Optional[str]:
        # Update record count based on the current response
        if hasattr(response, 'json'):
            try:
                current_records = len(response.json())
                self.record_count += current_records
            except:
                pass

        if self.record_limit is not None and self.record_count >= self.record_limit:
            return None

        next_link = response.links.get("next", {}).get("url")
        if next_link:
            query = dict(parse.parse_qsl(parse.urlsplit(next_link).query))
            next_page_token = query.get("page")
            return next_page_token
        return None


class CanvasStream(RESTStream):
    """Canvas stream class."""

    def __init__(self, tap=None, name=None, schema=None, path=None, **kwargs):
        """Initialize stream with record limit tracking."""
        # Handle the config parameter that some tests use
        self._direct_config = kwargs.pop("config", None)
        super().__init__(tap=tap, name=name, schema=schema, path=path, **kwargs)
        # Access record_limit after super().__init__ when config is properly set up
        self._record_limit = self.config.get("record_limit")
        self._records_count = 0

    @property
    def config(self) -> dict:
        """Get configuration, handling both direct config and tap config."""
        # If direct config was provided (for testing), use it
        if self._direct_config is not None:
            return self._direct_config
        # Otherwise use the standard Singer SDK config access
        return super().config

    @property
    def url_base(self) -> str:
        """Return the base URL for the Canvas API."""
        return self.config["base_url"]

    records_jsonpath = "$[*]"

    @property
    def authenticator(self) -> BearerTokenAuthenticator:
        """Return a new authenticator object."""
        return BearerTokenAuthenticator.create_for_stream(
            self, token=self.config.get("api_key")
        )

    @property
    def http_headers(self) -> dict:
        """Return the http headers needed."""
        headers = {}
        if "user_agent" in self.config:
            headers["User-Agent"] = self.config["user_agent"]
        return headers

    def get_new_paginator(self) -> BaseAPIPaginator:
        """Return a paginator instance for this stream."""
        return CanvasPaginator(record_limit=self._record_limit)

    def get_url_params(
        self, context: Optional[dict], next_page_token: Optional[Any]
    ) -> Dict[str, Any]:
        """Get URL query parameters."""
        params: dict = {}
        
        # Add pagination
        if next_page_token:
            params["page"] = next_page_token
        
        # Add sorting for incremental streams
        if self.replication_key:
            params["sort"] = "asc"
            params["order_by"] = self.replication_key

        # Add include fields from config
        include_fields = self.config.get("include")
        if include_fields:
            params["include"] = include_fields

        # Add per_page parameter
        params["per_page"] = 100
        
        return params

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result rows."""
        for row in extract_jsonpath(self.records_jsonpath, input=response.json()):
            if (
                self._record_limit is not None
                and self._records_count >= self._record_limit
            ):
                break
            self._records_count += 1
            yield row