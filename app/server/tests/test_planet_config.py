from __future__ import annotations

from fastapi.testclient import TestClient

from src.app import create_application
from src.config.settings import Settings, get_settings
from src.services.config_service import build_public_config


def test_build_public_config_includes_planet_registry() -> None:
    settings = Settings(
        APP_ENV="test",
        GOOGLE_MAPS_API_KEY=None,
        WEBCAM_WORKER_ENABLED=False,
        WEBCAM_WORKER_RUN_ON_STARTUP=False,
    )
    config = build_public_config(settings)

    assert config.planet.default_imagery_mode_id == "day-cloudless-default"
    assert any(mode.id == "night-lights" for mode in config.planet.imagery_modes)
    assert any(mode.id == "season-winter" for mode in config.planet.imagery_modes)
    assert any(mode.id == "false-color-vegetation" for mode in config.planet.imagery_modes)
    assert any(mode.id == "radar-sar-opera-rtc" for mode in config.planet.imagery_modes)
    assert any(mode.default_ready for mode in config.planet.imagery_modes)
    assert any(
        mode.id == config.planet.default_imagery_mode_id and mode.default_ready
        for mode in config.planet.imagery_modes
    )
    assert any(category.id == "analysis-friendly" for category in config.planet.categories)
    assert any(category.id == "radar-sar" for category in config.planet.categories)
    assert all(mode.short_description for mode in config.planet.imagery_modes)
    assert all(mode.short_caveat for mode in config.planet.imagery_modes)
    assert all(mode.display_tags for mode in config.planet.imagery_modes)
    assert all(mode.mode_role for mode in config.planet.imagery_modes)
    assert all(mode.sensor_family for mode in config.planet.imagery_modes)
    assert len({mode.id for mode in config.planet.imagery_modes}) == len(config.planet.imagery_modes)
    assert any(mode.mode_role == "default-basemap" for mode in config.planet.imagery_modes)
    assert any(mode.mode_role == "analysis-layer" for mode in config.planet.imagery_modes)
    assert any(mode.sensor_family == "radar" for mode in config.planet.imagery_modes)
    assert any(
        mode.id == "day-cloudless-default"
        and mode.mode_role == "default-basemap"
        and mode.sensor_family == "optical"
        and mode.historical_fidelity == "composite-reference"
        and "historical events over a non-historical composite" in mode.replay_short_note
        for mode in config.planet.imagery_modes
    )
    assert any(
        mode.id == "day-daily-true-color"
        and mode.historical_fidelity == "daily-approximate"
        for mode in config.planet.imagery_modes
    )
    assert any(
        mode.id == "radar-sar-opera-rtc"
        and mode.historical_fidelity == "multi-day-approximate"
        and "multi-day SAR backscatter context" in mode.replay_short_note
        for mode in config.planet.imagery_modes
    )


def test_public_config_route_exposes_imagery_modes(monkeypatch) -> None:
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.delenv("GOOGLE_MAPS_API_KEY", raising=False)
    monkeypatch.setenv("WEBCAM_WORKER_ENABLED", "false")
    monkeypatch.setenv("WEBCAM_WORKER_RUN_ON_STARTUP", "false")
    get_settings.cache_clear()

    client = TestClient(create_application())
    response = client.get("/api/config/public")

    get_settings.cache_clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["planet"]["defaultImageryModeId"] == "day-cloudless-default"
    assert payload["features"]["visualModes"] is True
    assert payload["planet"]["terrain"]["defaultProvider"] == "ellipsoid"
    assert any(mode["id"] == "day-daily-true-color" for mode in payload["planet"]["imageryModes"])
    assert any(mode["id"] == "snow-ice" for mode in payload["planet"]["imageryModes"])
    assert any(
        mode["id"] == "day-cloudless-default" and mode["cloudBehavior"] == "cloud-free"
        for mode in payload["planet"]["imageryModes"]
    )
    assert any(
        mode["id"] == "radar-sar-opera-rtc"
        and mode["cloudBehavior"] == "cloud-insensitive"
        and mode["temporalNature"] == "multi-day"
        and mode["modeRole"] == "analysis-layer"
        and mode["sensorFamily"] == "radar"
        for mode in payload["planet"]["imageryModes"]
    )
    assert any(
        mode["id"] == "day-cloudless-default"
        and mode["shortDescription"] == "Cloud-free global composite for the default Earth view."
        and "Composite" in mode["displayTags"]
        and mode["modeRole"] == "default-basemap"
        and mode["sensorFamily"] == "optical"
        for mode in payload["planet"]["imageryModes"]
    )
    assert any(
        mode["id"] == payload["planet"]["defaultImageryModeId"] and mode["defaultReady"] is True
        for mode in payload["planet"]["imageryModes"]
    )
    assert any(
        mode["id"] == "day-cloudless-default"
        and mode["historicalFidelity"] == "composite-reference"
        and "historical events over a non-historical composite" in mode["replayShortNote"]
        for mode in payload["planet"]["imageryModes"]
    )
    assert any(
        mode["id"] == "day-daily-true-color"
        and mode["historicalFidelity"] == "daily-approximate"
        for mode in payload["planet"]["imageryModes"]
    )
    assert any(
        mode["id"] == "radar-sar-opera-rtc"
        and mode["historicalFidelity"] == "multi-day-approximate"
        and "multi-day SAR backscatter context" in mode["replayShortNote"]
        for mode in payload["planet"]["imageryModes"]
    )
