"""Tests standard tap features using the built-in SDK tests library."""

from requests_cache import install_cache
from singer_sdk.testing import SuiteConfig, get_tap_test_class

from tap_planetscaleapi.tap import TapPlanetScaleAPI

SAMPLE_CONFIG = {}

install_cache(TapPlanetScaleAPI.name)

# Run standard built-in tap tests from the SDK:
TestTapPlanetScaleAPI = get_tap_test_class(
    tap_class=TapPlanetScaleAPI,
    config=SAMPLE_CONFIG,
    suite_config=SuiteConfig(
        ignore_no_records_for_streams=[
            "database_read_only_regions",
            "deploy_operations",
            "deploy_requests",
            "deploy_request_reviews",
        ],
    ),
)
