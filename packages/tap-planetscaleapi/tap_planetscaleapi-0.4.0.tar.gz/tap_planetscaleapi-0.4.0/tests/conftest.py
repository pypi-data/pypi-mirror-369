"""Pytest configuration."""

import pytest

XFAIL_NULLABLE = pytest.mark.xfail(reason="Null not documented in OpenAPI spec")
XFAIL_SCHEMA_MISMATCH = pytest.mark.xfail(reason="Schema mismatch against OpenAPI spec")

SCHEMA_MISMATCH = {
    "test_tap_stream_record_matches_stream_schema[backups]",
    "test_tap_stream_record_matches_stream_schema[branches]",
    "test_tap_stream_record_matches_stream_schema[databases]",
    "test_tap_stream_record_matches_stream_schema[passwords]",
    "test_tap_stream_record_matches_stream_schema[organizations]",
}
NULLABLE = {
    "test_tap_stream_attribute_not_null[backups.actor]",
    "test_tap_stream_attribute_not_null[branches.cluster_iops]",
    "test_tap_stream_attribute_not_null[branches.deleted_at]",
    "test_tap_stream_attribute_not_null[branches.parent_branch]",
    "test_tap_stream_attribute_not_null[branches.restore_checklist_completed_at]",
    "test_tap_stream_attribute_not_null[databases.automatic_migrations]",
    "test_tap_stream_attribute_not_null[databases.issues_count]",
    "test_tap_stream_attribute_not_null[databases.data_import]",
    "test_tap_stream_attribute_not_null[databases.migration_framework]",
    "test_tap_stream_attribute_not_null[databases.migration_table_name]",
    "test_tap_stream_attribute_not_null[organizations.has_past_due_invoices]",
    "test_tap_stream_attribute_not_null[organizations.sso_portal_url]",
    "test_tap_stream_attribute_not_null[passwords.cidrs]",
    "test_tap_stream_attribute_not_null[passwords.deleted_at]",
    "test_tap_stream_attribute_not_null[passwords.expires_at]",
    "test_tap_stream_attribute_not_null[passwords.plain_text]",
    "test_tap_stream_attribute_not_null[passwords.ttl_seconds]",
}


def pytest_runtest_setup(item: pytest.Item) -> None:
    """Skip tests that require a live API key."""
    test_name = item.name.split("::")[-1]

    if test_name in NULLABLE:
        item.add_marker(XFAIL_NULLABLE)

    if test_name in SCHEMA_MISMATCH:
        item.add_marker(XFAIL_SCHEMA_MISMATCH)
