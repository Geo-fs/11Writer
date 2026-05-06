from __future__ import annotations

import os
from datetime import datetime, timedelta
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.config.settings import Settings, get_settings
from src.marine.models import MarineBase
from src.reference.db import get_engine
from src.routes.marine import router as marine_router
from src.services.marine_context_service import MarineGebcoBathymetryService


def _client(tmp_path: Path, *, env: dict[str, str] | None = None) -> TestClient:
    db_url = f"sqlite:///{tmp_path / 'marine_gebco_test.db'}"
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
        os.environ["MARINE_GEBCO_BATHYMETRY_MODE"] = "fixture"
        if env:
            for key, value in env.items():
                os.environ[key] = value
        return Settings(_env_file=None)

    app.dependency_overrides[get_settings] = _settings_override
    return TestClient(app)


def test_marine_gebco_contract_loaded(tmp_path: Path) -> None:
    client = _client(tmp_path)

    response = client.get(
        "/api/marine/context/gebco-bathymetry",
        params={"lat": 29.28, "lon": -94.76, "radius_km": 120, "limit": 5},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["sourceHealth"]["sourceId"] == "gebco-gridded-bathymetry"
    assert payload["sourceHealth"]["sourceMode"] == "fixture"
    assert payload["sourceHealth"]["health"] == "loaded"
    assert payload["gridVersion"] == "GEBCO_2026"
    assert payload["gridResolutionArcSeconds"] == 15
    assert payload["count"] >= 1
    assert payload["areaSummary"]["underseaSampleCount"] >= 1
    sample = payload["samples"][0]
    assert sample["evidenceBasis"] == "contextual"
    assert sample["elevationMeters"] < 0
    assert sample["depthMeters"] > 0
    assert payload["caveats"]


def test_marine_gebco_empty_is_not_error(tmp_path: Path) -> None:
    client = _client(tmp_path)

    payload = client.get(
        "/api/marine/context/gebco-bathymetry",
        params={"lat": 0.0, "lon": 0.0, "radius_km": 50, "limit": 5},
    ).json()

    assert payload["count"] == 0
    assert payload["samples"] == []
    assert payload["sourceHealth"]["health"] == "empty"
    assert payload["sourceHealth"]["sourceMode"] == "fixture"


def test_marine_gebco_disabled_outside_fixture_mode(tmp_path: Path) -> None:
    client = _client(tmp_path, env={"MARINE_GEBCO_BATHYMETRY_MODE": "live"})

    payload = client.get(
        "/api/marine/context/gebco-bathymetry",
        params={"lat": 29.28, "lon": -94.76, "radius_km": 120, "limit": 5},
    ).json()

    assert payload["count"] == 0
    assert payload["samples"] == []
    assert payload["sourceHealth"]["health"] == "disabled"
    assert payload["sourceHealth"]["sourceMode"] == "live"
    assert payload["sourceHealth"]["enabled"] is False


def test_marine_gebco_can_honestly_emit_stale_from_old_grid_release(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(
        MarineGebcoBathymetryService,
        "_source_generated_at",
        lambda self: (datetime.now().astimezone() - timedelta(days=800)).isoformat(),
    )
    client = _client(tmp_path)

    payload = client.get(
        "/api/marine/context/gebco-bathymetry",
        params={"lat": 29.28, "lon": -94.76, "radius_km": 120, "limit": 5},
    ).json()

    assert payload["count"] >= 1
    assert payload["sourceHealth"]["health"] == "stale"
    assert "freshness threshold" in (payload["sourceHealth"]["detail"] or "").lower()


def test_marine_gebco_can_honestly_emit_unavailable_from_retrieval_failure(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(MarineGebcoBathymetryService, "_fixture_samples", lambda self: (_ for _ in ()).throw(TimeoutError("fixture gebco unavailable")))
    client = _client(tmp_path)

    payload = client.get(
        "/api/marine/context/gebco-bathymetry",
        params={"lat": 29.28, "lon": -94.76, "radius_km": 120, "limit": 5},
    ).json()

    assert payload["count"] == 0
    assert payload["sourceHealth"]["health"] == "unavailable"
    assert payload["sourceHealth"]["errorSummary"]
    assert "retrieval failed" in (payload["sourceHealth"]["detail"] or "").lower()


def test_marine_gebco_route_validation(tmp_path: Path) -> None:
    client = _client(tmp_path)

    invalid_radius = client.get(
        "/api/marine/context/gebco-bathymetry",
        params={"lat": 29.28, "lon": -94.76, "radius_km": 0.5},
    )
    assert invalid_radius.status_code == 422

    invalid_coordinates = client.get(
        "/api/marine/context/gebco-bathymetry",
        params={"lat": 91.0, "lon": -94.76, "radius_km": 120},
    )
    assert invalid_coordinates.status_code == 422
