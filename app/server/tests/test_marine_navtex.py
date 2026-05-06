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
from src.services.marine_context_service import MarineNavtexService


def _client(tmp_path: Path, *, env: dict[str, str] | None = None) -> TestClient:
    db_url = f"sqlite:///{tmp_path / 'marine_navtex_test.db'}"
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
        os.environ["NETHERLANDS_RWS_WATERINFO_MODE"] = "fixture"
        os.environ["MARINE_NAVTEX_MODE"] = "fixture"
        if env:
            for key, value in env.items():
                os.environ[key] = value
        return Settings(_env_file=None)

    app.dependency_overrides[get_settings] = _settings_override
    return TestClient(app)


def test_marine_navtex_contract_loaded(tmp_path: Path) -> None:
    client = _client(tmp_path)

    response = client.get(
        "/api/marine/context/navtex",
        params={"lat": 25.76, "lon": -80.19, "radius_km": 800, "limit": 5},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["sourceHealth"]["sourceId"] == "uscg-navtex-broadcast-notices"
    assert payload["sourceHealth"]["sourceMode"] == "fixture"
    assert payload["sourceHealth"]["health"] in {"loaded", "degraded", "empty"}
    assert payload["sourceHealth"]["loadedCount"] == payload["count"]
    assert "advisory context only" in payload["sourceHealth"]["caveat"].lower()
    assert payload["caveats"]
    assert payload["count"] >= 1
    broadcast = payload["broadcasts"][0]
    assert broadcast["messageId"]
    assert broadcast["stationId"]
    assert broadcast["stationName"]
    assert broadcast["transmitterCharacter"]
    assert broadcast["distanceKm"] >= 0
    assert broadcast["evidenceBasis"] == "advisory"
    assert broadcast["sourceUrl"].startswith("https://public.govdelivery.com/topics/")


def test_marine_navtex_message_type_filter_separates_warning_families(tmp_path: Path) -> None:
    client = _client(tmp_path)

    payload = client.get(
        "/api/marine/context/navtex",
        params={
            "lat": 25.76,
            "lon": -80.19,
            "radius_km": 2500,
            "limit": 10,
            "message_type": "meteorological-warning",
        },
    ).json()

    assert payload["count"] >= 1
    assert all(broadcast["subjectIndicator"] == "B" for broadcast in payload["broadcasts"])


def test_marine_navtex_empty_is_not_error(tmp_path: Path) -> None:
    client = _client(tmp_path)

    payload = client.get(
        "/api/marine/context/navtex",
        params={"lat": 0.0, "lon": 0.0, "radius_km": 50, "limit": 5},
    ).json()

    assert payload["count"] == 0
    assert payload["broadcasts"] == []
    assert payload["sourceHealth"]["health"] == "empty"
    assert payload["sourceHealth"]["sourceMode"] == "fixture"
    assert payload["caveats"]


def test_marine_navtex_partial_subject_metadata_degrades_source_health(tmp_path: Path) -> None:
    client = _client(tmp_path)

    payload = client.get(
        "/api/marine/context/navtex",
        params={"lat": 21.30, "lon": -157.86, "radius_km": 400, "limit": 10},
    ).json()

    assert payload["count"] >= 1
    assert payload["sourceHealth"]["health"] == "degraded"
    assert payload["broadcasts"][0]["subjectLabel"] is None
    assert "partial subject classification" in (payload["sourceHealth"]["detail"] or "").lower()


def test_marine_navtex_disabled_outside_fixture_mode(tmp_path: Path) -> None:
    client = _client(tmp_path, env={"MARINE_NAVTEX_MODE": "live"})

    payload = client.get(
        "/api/marine/context/navtex",
        params={"lat": 25.76, "lon": -80.19, "radius_km": 800, "limit": 5},
    ).json()

    assert payload["count"] == 0
    assert payload["broadcasts"] == []
    assert payload["sourceHealth"]["health"] == "disabled"
    assert payload["sourceHealth"]["sourceMode"] == "live"
    assert payload["sourceHealth"]["enabled"] is False


def test_marine_navtex_fixture_mode_does_not_fabricate_unavailable_or_unknown(tmp_path: Path) -> None:
    client = _client(tmp_path)

    payload = client.get(
        "/api/marine/context/navtex",
        params={"lat": 25.76, "lon": -80.19, "radius_km": 800, "limit": 5},
    ).json()

    assert payload["sourceHealth"]["health"] in {"loaded", "degraded", "empty"}
    assert payload["sourceHealth"]["health"] not in {"error", "unknown", "unavailable", "disabled"}


def test_marine_navtex_can_honestly_emit_stale_from_old_issue_timestamps(tmp_path: Path, monkeypatch) -> None:
    original_fixture = MarineNavtexService._fixture_broadcasts

    def stale_fixture(self: MarineNavtexService, now: datetime):
        broadcasts = original_fixture(self, now)
        stale_at = (now - timedelta(days=2)).isoformat()
        return [replace(broadcast, issued_at=stale_at) for broadcast in broadcasts]

    monkeypatch.setattr(MarineNavtexService, "_fixture_broadcasts", stale_fixture)
    client = _client(tmp_path)

    payload = client.get(
        "/api/marine/context/navtex",
        params={"lat": 25.76, "lon": -80.19, "radius_km": 800, "limit": 5},
    ).json()

    assert payload["count"] >= 1
    assert payload["sourceHealth"]["health"] == "stale"
    assert "freshness threshold" in (payload["sourceHealth"]["detail"] or "").lower()


def test_marine_navtex_can_honestly_emit_unavailable_from_retrieval_failure(tmp_path: Path, monkeypatch) -> None:
    def broken_fixture(self: MarineNavtexService, now: datetime):
        raise TimeoutError("fixture navtex unavailable")

    monkeypatch.setattr(MarineNavtexService, "_fixture_broadcasts", broken_fixture)
    client = _client(tmp_path)

    payload = client.get(
        "/api/marine/context/navtex",
        params={"lat": 25.76, "lon": -80.19, "radius_km": 800, "limit": 5},
    ).json()

    assert payload["count"] == 0
    assert payload["sourceHealth"]["health"] == "unavailable"
    assert payload["sourceHealth"]["errorSummary"]
    assert "retrieval failed" in (payload["sourceHealth"]["detail"] or "").lower()


def test_marine_navtex_route_validation(tmp_path: Path) -> None:
    client = _client(tmp_path)

    invalid_radius = client.get(
        "/api/marine/context/navtex",
        params={"lat": 25.76, "lon": -80.19, "radius_km": 0.5},
    )
    assert invalid_radius.status_code == 422

    invalid_coordinates = client.get(
        "/api/marine/context/navtex",
        params={"lat": 91.0, "lon": -80.19, "radius_km": 100},
    )
    assert invalid_coordinates.status_code == 422

    invalid_message_type = client.get(
        "/api/marine/context/navtex",
        params={"lat": 25.76, "lon": -80.19, "radius_km": 100, "message_type": "bad"},
    )
    assert invalid_message_type.status_code == 422
