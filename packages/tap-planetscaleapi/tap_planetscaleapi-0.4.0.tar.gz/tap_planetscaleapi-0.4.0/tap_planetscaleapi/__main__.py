"""PlanetScaleAPI entry point."""

from __future__ import annotations

from tap_planetscaleapi.tap import TapPlanetScaleAPI

TapPlanetScaleAPI.cli()
