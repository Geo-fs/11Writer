from __future__ import annotations

import os
from dataclasses import replace
from datetime import datetime, timedelta
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.config.settings import Settings, get_settings
from src.marine.models import MarineBase
from src.reference.db import get_engine
from src.routes.marine import router as marine_router
from src.services.marine_context_service import MarineIrelandOpwWaterLevelService


def _client(tmp_path: Path, *, env: dict[str, str] | None = None) -> TestClient:
    db_url = f"sqlite:///{tmp_path / 'ireland_opw_waterlevel_test.db'}"
    engine = get_engine(db_url)
    MarineBase.metadata.create_all(engine)

    app = FastAPI()
    app.include_router(marine_router)

    def _settings_override() -> Settings:
        os.environ["APP_ENV"] = "test"
        os.environ["REFERENCE_DATABASE_URL"] = db_url
        os.environ["MARINE_DATABASE_URL"] = db_url
        os.environ["WEBCAM_WORKER_ENABLED"] = "false"
        os.environ["WEBCAM_WORKER_RUN_ON_STARTUP"] = "false"
        os.environ["MARINE_SOURCE_MODE"] = "fixture"
        os.environ["MARINE_FIXTURE_SCENARIO"] = "investigative-mix"
        os.environ["MARINE_NOAA_COOPS_MODE"] = "fixture"
        os.environ["MARINE_NDBC_MODE"] = "fixture"
        os.environ["VIGICRUES_HYDROMETRY_MODE"] = "fixture"
        os.environ["SCOTTISH_WATER_OVERFLOWS_MODE"] = "fixture"
        os.environ["IRELAND_OPW_WATERLEVEL_MODE"] = "fixture"
        if env:
            for key, value in env.items():
                os.environ[key] = value
        return Settings(_env_file=None)

    app.dependency_overrides[get_settings] = _settings_override
    return TestClient(app)


def test_ireland_opw_waterlevel_contract_loaded(tmp_path: Path) -> None:
    client = _client(tmp_path)

    response = client.get(
        "/api/marine/context/ireland-opw-waterlevel",
        params={"lat": 52.45, "lon": -9.66, "radius_km": 250, "limit": 5},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["sourceHealth"]["sourceId"] == "ireland-opw-waterlevel"
    assert payload["sourceHealth"]["sourceMode"] == "fixture"
    assert payload["sourceHealth"]["health"] in {"loaded", "empty", "degraded"}
    assert payload["sourceHealth"]["loadedCount"] == payload["count"]
    assert "provisional hydrometric context only" in payload["sourceHealth"]["caveat"].lower()
    assert payload["caveats"]
    assert payload["count"] >= 1
    station = payload["stations"][0]
    assert station["stationId"]
    assert station["stationName"]
    assert station["distanceKm"] >= 0
    assert station["statusLine"]
    assert station["stationSourceUrl"] == "https://waterlevel.ie/geojson/"
    assert station["latestReading"]["observedBasis"] == "observed"
    assert station["latestReading"]["sourceUrl"] == "https://waterlevel.ie/geojson/latest/"


def test_ireland_opw_waterlevel_empty_is_not_error(tmp_path: Path) -> None:
    client = _client(tmp_path)

    response = client.get(
        "/api/marine/context/ireland-opw-waterlevel",
        params={"lat": 0.0, "lon": 0.0, "radius_km": 50, "limit": 5},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] == 0
    assert payload["stations"] == []
    assert payload["sourceHealth"]["health"] == "empty"
    assert payload["sourceHealth"]["sourceMode"] == "fixture"
    assert payload["caveats"]


def test_ireland_opw_waterlevel_partial_metadata_case_is_preserved(tmp_path: Path) -> None:
    client = _client(tmp_path)

    payload = client.get(
        "/api/marine/context/ireland-opw-waterlevel",
        params={"lat": 52.66, "lon": -8.62, "radius_km": 100, "limit": 10},
    ).json()

    station = next(item for item in payload["stations"] if item["stationId"] == "19006_0001")
    assert station["waterbody"] is None
    assert station["caveats"]


def test_ireland_opw_waterlevel_disabled_outside_fixture_mode(tmp_path: Path) -> None:
    client = _client(tmp_path, env={"IRELAND_OPW_WATERLEVEL_MODE": "live"})

    payload = client.get(
        "/api/marine/context/ireland-opw-waterlevel",
        params={"lat": 52.45, "lon": -9.66, "radius_km": 250, "limit": 5},
    ).json()

    assert payload["count"] == 0
    assert payload["stations"] == []
    assert payload["sourceHealth"]["health"] == "disabled"
    assert payload["sourceHealth"]["sourceMode"] == "live"
    assert payload["sourceHealth"]["enabled"] is False
    assert payload["caveats"]


def test_ireland_opw_waterlevel_fixture_mode_does_not_fabricate_stale_or_unavailable(tmp_path: Path) -> None:
    client = _client(tmp_path)

    payload = client.get(
        "/api/marine/context/ireland-opw-waterlevel",
        params={"lat": 52.45, "lon": -9.66, "radius_km": 250, "limit": 5},
    ).json()

    assert payload["sourceHealth"]["health"] in {"loaded", "empty", "degraded"}
    assert payload["sourceHealth"]["health"] not in {"stale", "error", "unknown", "unavailable"}


def test_ireland_opw_waterlevel_unknown_mode_normalizes_to_disabled(tmp_path: Path) -> None:
    client = _client(tmp_path, env={"IRELAND_OPW_WATERLEVEL_MODE": "bogus-mode"})

    payload = client.get(
        "/api/marine/context/ireland-opw-waterlevel",
        params={"lat": 52.45, "lon": -9.66, "radius_km": 250, "limit": 5},
    ).json()

    assert payload["count"] == 0
    assert payload["stations"] == []
    assert payload["sourceHealth"]["sourceMode"] == "unknown"
    assert payload["sourceHealth"]["health"] == "disabled"
    assert payload["sourceHealth"]["enabled"] is False
    assert payload["caveats"]


def test_ireland_opw_waterlevel_can_honestly_emit_stale_from_old_reading_timestamps(
    tmp_path: Path, monkeypatch
) -> None:
    original_fixture = MarineIrelandOpwWaterLevelService._fixture_stations

    def stale_fixture(self: MarineIrelandOpwWaterLevelService, now: datetime):
        stations = original_fixture(self, now)
        stale_at = (now - timedelta(hours=3)).isoformat()
        return [
            replace(
                station,
                latest_reading=station.latest_reading.model_copy(update={"reading_at": stale_at})
                if station.latest_reading
                else None,
            )
            for station in stations
        ]

    monkeypatch.setattr(MarineIrelandOpwWaterLevelService, "_fixture_stations", stale_fixture)
    client = _client(tmp_path)

    payload = client.get(
        "/api/marine/context/ireland-opw-waterlevel",
        params={"lat": 52.45, "lon": -9.66, "radius_km": 250, "limit": 5},
    ).json()

    assert payload["count"] >= 1
    assert payload["sourceHealth"]["health"] == "stale"
    assert "freshness threshold" in (payload["sourceHealth"]["detail"] or "").lower()
    assert "freshness threshold" in (payload["sourceHealth"]["caveat"] or "").lower()


def test_ireland_opw_waterlevel_can_honestly_emit_degraded_from_partial_metadata(tmp_path: Path) -> None:
    client = _client(tmp_path)

    payload = client.get(
        "/api/marine/context/ireland-opw-waterlevel",
        params={"lat": 52.66, "lon": -8.62, "radius_km": 100, "limit": 10},
    ).json()

    assert payload["count"] >= 1
    assert payload["sourceHealth"]["health"] == "degraded"
    assert "partial metadata" in (payload["sourceHealth"]["detail"] or "").lower()
    assert "partial metadata" in (payload["sourceHealth"]["caveat"] or "").lower()


def test_ireland_opw_waterlevel_can_honestly_emit_unavailable_from_retrieval_failure(
    tmp_path: Path, monkeypatch
) -> None:
    def broken_fixture(self: MarineIrelandOpwWaterLevelService, now: datetime):
        raise OSError("fixture opw unavailable")

    monkeypatch.setattr(MarineIrelandOpwWaterLevelService, "_fixture_stations", broken_fixture)
    client = _client(tmp_path)

    payload = client.get(
        "/api/marine/context/ireland-opw-waterlevel",
        params={"lat": 52.45, "lon": -9.66, "radius_km": 250, "limit": 5},
    ).json()

    assert payload["count"] == 0
    assert payload["sourceHealth"]["health"] == "unavailable"
    assert payload["sourceHealth"]["errorSummary"]
    assert "retrieval failed" in (payload["sourceHealth"]["detail"] or "").lower()


def test_ireland_opw_waterlevel_route_validation(tmp_path: Path) -> None:
    client = _client(tmp_path)

    invalid_radius = client.get(
        "/api/marine/context/ireland-opw-waterlevel",
        params={"lat": 52.45, "lon": -9.66, "radius_km": 0.5},
    )
    assert invalid_radius.status_code == 422

    invalid_coordinates = client.get(
        "/api/marine/context/ireland-opw-waterlevel",
        params={"lat": 91.0, "lon": -9.66, "radius_km": 50},
    )
    assert invalid_coordinates.status_code == 422
