"""REST client handling, including PlanetScaleAPIStream base class."""

from __future__ import annotations

import abc
import sys
import typing as t

from singer_sdk import OpenAPISchema, StreamSchema
from singer_sdk.authenticators import APIKeyAuthenticator
from singer_sdk.pagination import BasePageNumberPaginator
from singer_sdk.streams import RESTStream
from toolz.dicttoolz import get_in

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override

if t.TYPE_CHECKING:
    from singer_sdk.helpers.types import Context

OPENAPI_URL = "https://api.planetscale.com/v1/openapi-spec"


class StreamKey(t.NamedTuple):
    """A key for a stream in the OpenAPI spec."""

    path: str
    method: str
    expected_status: int = 200


class PlanetScaleOpenAPISource(OpenAPISchema[StreamKey]):
    """OpenAPI source for PlanetScale API."""

    @override
    def get_unresolved_schema(self, key: StreamKey) -> dict[str, t.Any]:
        return get_in(
            [
                "paths",
                key.path,
                key.method,
                "responses",
                str(key.expected_status),
                "schema",
            ],
            self.spec,
        )

    @override
    def fetch_schema(self, key: StreamKey) -> dict[str, t.Any]:
        schema = super().fetch_schema(key)
        return schema["properties"]["data"]["items"]


class SchemaFromPath(StreamSchema[StreamKey]):
    """A stream schema from a path in the OpenAPI spec."""

    @override
    def get_stream_schema(
        self,
        stream: PlanetScaleAPIStream,  # type: ignore[override]
        stream_class: type[PlanetScaleAPIStream],  # type: ignore[override]
    ) -> dict[str, t.Any]:
        key = StreamKey(
            path=stream.spec_path or stream.path,
            method=stream.http_method.lower(),
            expected_status=200,
        )
        return self.schema_source.get_schema(key)


class PlanetScaleAPIStream(RESTStream[int], metaclass=abc.ABCMeta):
    """PlanetScaleAPI stream class."""

    # Class properties
    PAGE_SIZE = 100
    records_jsonpath = "$.data[*]"

    #: The endpoint for this resource in the OpenAPI spec. If not provided, the
    #: `path` attribute is used.
    spec_path: str | None = None

    schema = SchemaFromPath(PlanetScaleOpenAPISource(OPENAPI_URL))  # type: ignore[assignment]

    @property
    @override
    def url_base(self) -> str:
        return "https://api.planetscale.com/v1"

    @property
    @override
    def authenticator(self) -> APIKeyAuthenticator:
        token_id = self.config["service_token_id"]
        token = self.config["service_token"]
        return APIKeyAuthenticator.create_for_stream(
            self,
            key="Authorization",
            value=f"{token_id}:{token}",
            location="header",
        )

    @property
    @override
    def http_headers(self) -> dict:
        return {
            "accept": "application/json",
        }

    @override
    def get_new_paginator(self) -> BasePageNumberPaginator:
        return BasePageNumberPaginator(1)

    @override
    def get_url_params(
        self,
        context: Context | None,
        next_page_token: t.Any | None,
    ) -> dict[str, t.Any]:
        params: dict[str, t.Any] = {"per_page": self.PAGE_SIZE}
        if next_page_token:
            params["page"] = next_page_token

        return params
