"""Stream type classes for tap-planetscaleapi."""

from __future__ import annotations

import sys
import typing as t

from tap_planetscaleapi.client import PlanetScaleAPIStream

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override

if t.TYPE_CHECKING:
    from singer_sdk.helpers.types import Context


class OrganizationsStream(PlanetScaleAPIStream):
    """Organizations."""

    name = "organizations"
    path = "/organizations"
    primary_keys = ("id",)
    replication_key = None

    @override
    def get_child_context(self, record: dict, context: Context | None) -> dict | None:
        return {
            "organization_id": record["id"],
            "organization_name": record["name"],
        }

    @override
    def post_process(self, row: dict, context: Context | None = None) -> dict | None:
        row["invoice_budget_amount"] = float(row["invoice_budget_amount"])
        return row


class OrganizationRegionsStream(PlanetScaleAPIStream):
    """Organization regions."""

    parent_stream_type = OrganizationsStream

    name = "organization_regions"
    path = "/organizations/{organization_name}/regions"
    primary_keys = ("id",)
    replication_key = None
    spec_path = "/organizations/{name}/regions"


class DatabasesStream(PlanetScaleAPIStream):
    """Databases."""

    parent_stream_type = OrganizationsStream

    name = "databases"
    path = "/organizations/{organization_name}/databases"
    primary_keys = ("id",)
    replication_key = None
    spec_path = "/organizations/{organization}/databases"

    @override
    def get_child_context(self, record: dict, context: Context | None) -> dict | None:
        return {
            "database_id": record["id"],
            "database_name": record["name"],
            "organization_id": context["organization_id"] if context else None,
            "organization_name": context["organization_name"] if context else None,
        }


class DatabaseReadOnlyRegionsStream(PlanetScaleAPIStream):
    """Database read-only regions."""

    parent_stream_type = DatabasesStream

    name = "database_read_only_regions"
    path = "/organizations/{organization_name}/databases/{database_name}/read-only-regions"
    primary_keys = ("id",)
    replication_key = None
    spec_path = "/organizations/{organization}/databases/{name}/read-only-regions"


class DatabaseRegionsStream(PlanetScaleAPIStream):
    """Database regions."""

    parent_stream_type = DatabasesStream

    name = "database_regions"
    path = "/organizations/{organization_name}/databases/{database_name}/regions"
    primary_keys = ("id",)
    replication_key = None
    spec_path = "/organizations/{organization}/databases/{name}/regions"


class BranchesStream(PlanetScaleAPIStream):
    """Branches."""

    parent_stream_type = DatabasesStream

    name = "branches"
    path = "/organizations/{organization_name}/databases/{database_name}/branches"
    primary_keys = ("id",)
    replication_key = None
    spec_path = "/organizations/{organization}/databases/{database}/branches"

    @override
    def get_child_context(self, record: dict, context: Context | None) -> dict | None:
        return {
            "branch_id": record["id"],
            "branch_name": record["name"],
            "database_id": context["database_id"] if context else None,
            "database_name": context["database_name"] if context else None,
            "organization_id": context["organization_id"] if context else None,
            "organization_name": context["organization_name"] if context else None,
        }


class BranchSchemaStream(PlanetScaleAPIStream):
    """Branch schema."""

    parent_stream_type = BranchesStream

    name = "branch_schema"
    path = "/organizations/{organization_name}/databases/{database_name}/branches/{branch_name}/schema"
    primary_keys = ("id",)
    replication_key = None
    spec_path = "/organizations/{organization}/databases/{database}/branches/{name}/schema"


class BackupsStream(PlanetScaleAPIStream):
    """Backups."""

    parent_stream_type = BranchesStream

    name = "backups"
    path = "/organizations/{organization_name}/databases/{database_name}/branches/{branch_name}/backups"
    primary_keys = ("id",)
    replication_key = None
    spec_path = "/organizations/{organization}/databases/{database}/branches/{branch}/backups"


class PasswordsStream(PlanetScaleAPIStream):
    """Passwords."""

    parent_stream_type = BranchesStream

    name = "passwords"
    path = "/organizations/{organization_name}/databases/{database_name}/branches/{branch_name}/passwords"
    primary_keys = ("id",)
    replication_key = None
    spec_path = "/organizations/{organization}/databases/{database}/branches/{branch}/passwords"


class DeployRequestsStream(PlanetScaleAPIStream):
    """Deploy requests."""

    parent_stream_type = BranchesStream

    name = "deploy_requests"
    path = "/organizations/{organization_name}/databases/{database_name}/deploy-requests"
    primary_keys = ("id",)
    replication_key = None
    spec_path = "/organizations/{organization}/databases/{database}/deploy-requests"

    @override
    def get_child_context(self, record: dict, context: Context | None) -> dict | None:
        return {
            "deploy_request_id": record["id"],
            "deploy_request_number": record["number"],
            "branch_id": context["branch_id"] if context else None,
            "branch_name": context["branch_name"] if context else None,
            "database_id": context["database_id"] if context else None,
            "database_name": context["database_name"] if context else None,
            "organization_id": context["organization_id"] if context else None,
            "organization_name": context["organization_name"] if context else None,
        }


class DeployOperationsStream(PlanetScaleAPIStream):
    """Deploy operations."""

    parent_stream_type = DeployRequestsStream

    name = "deploy_operations"
    path = "/organizations/{organization_name}/databases/{database_name}/deploy-requests/{deploy_request_number}/operations"
    primary_keys = ("id",)
    replication_key = None
    spec_path = "/organizations/{organization}/databases/{database}/deploy-requests/{number}/operations"


class DeployRequestReviewsStreams(PlanetScaleAPIStream):
    """Deploy request reviews."""

    parent_stream_type = DeployRequestsStream

    name = "deploy_request_reviews"
    path = "/organizations/{organization_name}/databases/{database_name}/deploy-requests/{deploy_request_number}/reviews"
    primary_keys = ("id",)
    replication_key = None
    spec_path = "/organizations/{organization}/databases/{database}/deploy-requests/{number}/reviews"


class OAuthApplicationsStream(PlanetScaleAPIStream):
    """OAuth applications."""

    parent_stream_type = OrganizationsStream

    name = "oauth_applications"
    path = "/organizations/{organization_id}/oauth-applications"
    primary_keys = ("id",)
    replication_key = None
    spec_path = "/organizations/{organization}/oauth-applications"


class RegionsStream(PlanetScaleAPIStream):
    """Regions."""

    name = "regions"
    path = "/regions"
    primary_keys = ("id",)
    replication_key = None
