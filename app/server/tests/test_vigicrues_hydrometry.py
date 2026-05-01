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
from src.services.marine_context_service import MarineVigicruesHydrometryService


def _client(tmp_path: Path, *, env: dict[str, str] | None = None) -> TestClient:
    db_url = f"sqlite:///{tmp_path / 'vigicrues_test.db'}"
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
        if env:
            for key, value in env.items():
                os.environ[key] = value
        return Settings(_env_file=None)

    app.dependency_overrides[get_settings] = _settings_override
    return TestClient(app)


def test_vigicrues_hydrometry_contract_loaded(tmp_path: Path) -> None:
    client = _client(tmp_path)

    response = client.get(
        "/api/marine/context/vigicrues-hydrometry",
        params={"lat": 49.3, "lon": 1.24, "radius_km": 300, "parameter": "all", "limit": 5},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["sourceHealth"]["sourceId"] == "france-vigicrues-hydrometry"
    assert payload["sourceHealth"]["sourceMode"] == "fixture"
    assert payload["sourceHealth"]["health"] in {"loaded", "empty", "degraded"}
    assert payload["sourceHealth"]["loadedCount"] == payload["count"]
    assert "hydrometry observations are river-condition context only" in payload["sourceHealth"]["caveat"].lower()
    assert payload["caveats"]
    assert payload["count"] >= 1
    station = payload["stations"][0]
    assert station["stationId"]
    assert station["stationName"]
    assert station["distanceKm"] >= 0
    assert station["statusLine"]
    assert station["stationSourceUrl"] == "https://hubeau.eaufrance.fr/api/v2/hydrometrie/referentiel/stations"
    assert station["latestObservation"]["observedBasis"] == "observed"
    assert station["latestObservation"]["parameter"] in {"water-height", "flow"}
    assert station["latestObservation"]["unit"]
    assert station["latestObservation"]["sourceUrl"] == "https://hubeau.eaufrance.fr/api/v2/hydrometrie/observations_tr"


def test_vigicrues_hydrometry_empty_is_not_error(tmp_path: Path) -> None:
    client = _client(tmp_path)

    response = client.get(
        "/api/marine/context/vigicrues-hydrometry",
        params={"lat": 0.0, "lon": 0.0, "radius_km": 50, "parameter": "all", "limit": 5},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] == 0
    assert payload["stations"] == []
    assert payload["sourceHealth"]["health"] == "empty"
    assert payload["sourceHealth"]["sourceMode"] == "fixture"
    assert payload["caveats"]


def test_vigicrues_hydrometry_parameter_filter_keeps_height_and_flow_distinct(tmp_path: Path) -> None:
    client = _client(tmp_path)

    height_payload = client.get(
        "/api/marine/context/vigicrues-hydrometry",
        params={"lat": 44.84, "lon": -0.58, "radius_km": 700, "parameter": "water-height", "limit": 10},
    ).json()
    assert height_payload["parameterFilter"] == "water-height"
    assert height_payload["count"] >= 1
    assert all(
        station["latestObservation"]["parameter"] == "water-height"
        for station in height_payload["stations"]
        if station.get("latestObservation")
    )

    flow_payload = client.get(
        "/api/marine/context/vigicrues-hydrometry",
        params={"lat": 43.81, "lon": 4.64, "radius_km": 700, "parameter": "flow", "limit": 10},
    ).json()
    assert flow_payload["parameterFilter"] == "flow"
    assert flow_payload["count"] >= 1
    assert all(
        station["latestObservation"]["parameter"] == "flow"
        for station in flow_payload["stations"]
        if station.get("latestObservation")
    )


def test_vigicrues_hydrometry_partial_metadata_case_is_preserved(tmp_path: Path) -> None:
    client = _client(tmp_path)

    payload = client.get(
        "/api/marine/context/vigicrues-hydrometry",
        params={"lat": 44.84, "lon": -0.58, "radius_km": 100, "parameter": "all", "limit": 10},
    ).json()

    station = next(item for item in payload["stations"] if item["stationId"] == "Q001001001")
    assert station["riverBasin"] is None
    assert station["caveats"]


def test_vigicrues_hydrometry_disabled_outside_fixture_mode(tmp_path: Path) -> None:
    client = _client(tmp_path, env={"VIGICRUES_HYDROMETRY_MODE": "live"})

    payload = client.get(
        "/api/marine/context/vigicrues-hydrometry",
        params={"lat": 49.3, "lon": 1.24, "radius_km": 300, "parameter": "all", "limit": 5},
    ).json()

    assert payload["count"] == 0
    assert payload["stations"] == []
    assert payload["sourceHealth"]["health"] == "disabled"
    assert payload["sourceHealth"]["sourceMode"] == "live"
    assert payload["sourceHealth"]["enabled"] is False
    assert payload["caveats"]


def test_vigicrues_hydrometry_fixture_mode_does_not_fabricate_stale_or_unavailable(tmp_path: Path) -> None:
    client = _client(tmp_path)

    payload = client.get(
        "/api/marine/context/vigicrues-hydrometry",
        params={"lat": 49.3, "lon": 1.24, "radius_km": 300, "parameter": "all", "limit": 5},
    ).json()

    assert payload["sourceHealth"]["health"] in {"loaded", "empty", "degraded"}
    assert payload["sourceHealth"]["health"] not in {"stale", "error", "unknown", "unavailable"}


def test_vigicrues_hydrometry_unknown_mode_normalizes_to_disabled(tmp_path: Path) -> None:
    client = _client(tmp_path, env={"VIGICRUES_HYDROMETRY_MODE": "bogus-mode"})

    payload = client.get(
        "/api/marine/context/vigicrues-hydrometry",
        params={"lat": 49.3, "lon": 1.24, "radius_km": 300, "parameter": "all", "limit": 5},
    ).json()

    assert payload["count"] == 0
    assert payload["stations"] == []
    assert payload["sourceHealth"]["sourceMode"] == "unknown"
    assert payload["sourceHealth"]["health"] == "disabled"
    assert payload["sourceHealth"]["enabled"] is False
    assert payload["caveats"]


def test_vigicrues_hydrometry_can_honestly_emit_stale_from_old_observation_timestamps(
    tmp_path: Path, monkeypatch
) -> None:
    original_fixture = MarineVigicruesHydrometryService._fixture_stations

    def stale_fixture(self: MarineVigicruesHydrometryService, now: datetime):
        stations = original_fixture(self, now)
        stale_at = (now - timedelta(hours=3)).isoformat()
        return [
            replace(
                station,
                latest_observation=station.latest_observation.model_copy(update={"observed_at": stale_at})
                if station.latest_observation
                else None,
            )
            for station in stations
        ]

    monkeypatch.setattr(MarineVigicruesHydrometryService, "_fixture_stations", stale_fixture)
    client = _client(tmp_path)

    payload = client.get(
        "/api/marine/context/vigicrues-hydrometry",
        params={"lat": 49.3, "lon": 1.24, "radius_km": 300, "parameter": "all", "limit": 5},
    ).json()

    assert payload["count"] >= 1
    assert payload["sourceHealth"]["health"] == "stale"
    assert "freshness threshold" in (payload["sourceHealth"]["detail"] or "").lower()
    assert "freshness threshold" in (payload["sourceHealth"]["caveat"] or "").lower()


def test_vigicrues_hydrometry_can_honestly_emit_degraded_from_partial_metadata(tmp_path: Path) -> None:
    client = _client(tmp_path)

    payload = client.get(
        "/api/marine/context/vigicrues-hydrometry",
        params={"lat": 44.84, "lon": -0.58, "radius_km": 100, "parameter": "all", "limit": 10},
    ).json()

    assert payload["count"] >= 1
    assert payload["sourceHealth"]["health"] == "degraded"
    assert "partial metadata" in (payload["sourceHealth"]["detail"] or "").lower()
    assert "partial metadata" in (payload["sourceHealth"]["caveat"] or "").lower()


def test_vigicrues_hydrometry_can_honestly_emit_unavailable_from_retrieval_failure(
    tmp_path: Path, monkeypatch
) -> None:
    def broken_fixture(self: MarineVigicruesHydrometryService, now: datetime):
        raise TimeoutError("fixture vigicrues unavailable")

    monkeypatch.setattr(MarineVigicruesHydrometryService, "_fixture_stations", broken_fixture)
    client = _client(tmp_path)

    payload = client.get(
        "/api/marine/context/vigicrues-hydrometry",
        params={"lat": 49.3, "lon": 1.24, "radius_km": 300, "parameter": "all", "limit": 5},
    ).json()

    assert payload["count"] == 0
    assert payload["sourceHealth"]["health"] == "unavailable"
    assert payload["sourceHealth"]["errorSummary"]
    assert "retrieval failed" in (payload["sourceHealth"]["detail"] or "").lower()


def test_vigicrues_hydrometry_route_validation(tmp_path: Path) -> None:
    client = _client(tmp_path)

    invalid_radius = client.get(
        "/api/marine/context/vigicrues-hydrometry",
        params={"lat": 49.3, "lon": 1.24, "radius_km": 0.5},
    )
    assert invalid_radius.status_code == 422

    invalid_coordinates = client.get(
        "/api/marine/context/vigicrues-hydrometry",
        params={"lat": 91.0, "lon": 1.24, "radius_km": 50},
    )
    assert invalid_coordinates.status_code == 422

    invalid_parameter = client.get(
        "/api/marine/context/vigicrues-hydrometry",
        params={"lat": 49.3, "lon": 1.24, "radius_km": 50, "parameter": "stage-and-flow"},
    )
    assert invalid_parameter.status_code == 422
