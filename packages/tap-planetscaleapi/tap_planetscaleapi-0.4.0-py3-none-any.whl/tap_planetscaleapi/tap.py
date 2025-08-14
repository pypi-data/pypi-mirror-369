"""PlanetScaleAPI tap class."""

from __future__ import annotations

import sys
import typing as t

from singer_sdk import Tap
from singer_sdk import typing as th  # JSON schema typing helpers

from tap_planetscaleapi import streams

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override

if t.TYPE_CHECKING:
    from tap_planetscaleapi.client import PlanetScaleAPIStream


class TapPlanetScaleAPI(Tap):
    """PlanetScaleAPI tap class."""

    name = "tap-planetscaleapi"

    config_jsonschema = th.PropertiesList(
        th.Property(
            "service_token_id",
            th.StringType,
            required=True,
            description="The service token ID, visible on the service token page",
        ),
        th.Property(
            "service_token",
            th.StringType,
            required=True,
            secret=True,
            description="The service token value",
        ),
    ).to_dict()

    @override
    def discover_streams(self) -> list[PlanetScaleAPIStream]:
        return [
            streams.OrganizationsStream(tap=self),
            streams.OrganizationRegionsStream(tap=self),
            streams.DatabasesStream(tap=self),
            streams.DatabaseReadOnlyRegionsStream(tap=self),
            streams.DatabaseRegionsStream(tap=self),
            streams.BranchesStream(tap=self),
            # streams.BranchSchemaStream(tap=self),  # noqa: ERA001
            streams.BackupsStream(tap=self),
            streams.PasswordsStream(tap=self),
            streams.DeployRequestsStream(tap=self),
            streams.DeployOperationsStream(tap=self),
            streams.DeployRequestReviewsStreams(tap=self),
            # streams.OAuthApplicationsStream(tap=self),  # noqa: ERA001
            streams.RegionsStream(tap=self),
        ]


if __name__ == "__main__":
    TapPlanetScaleAPI.cli()
