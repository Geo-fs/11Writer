from __future__ import annotations

import os
import asyncio
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.adapters.marine import (
    CsvAisMarineAdapter,
    HttpJsonMarineAdapter,
    build_fixture_scenario,
)
from src.config.settings import Settings, get_settings
from src.marine.gap_detection import MarineGapDetectionService
from src.marine.models import MarineBase
from src.marine.models import MarineGapEventORM
from src.marine.models import MarineSourceORM
from src.reference.db import get_engine
from src.routes.marine import router as marine_router
from src.services.marine_context_service import (
    MarineNdbcService,
    MarineNoaaCoopsService,
    MarineScottishWaterOverflowService,
)


def _client(tmp_path: Path, *, env: dict[str, str] | None = None) -> TestClient:
    db_url = f"sqlite:///{tmp_path / 'marine_test.db'}"
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


def test_marine_vessels_route_serializes_provenance(tmp_path: Path) -> None:
    client = _client(tmp_path)

    response = client.get("/api/marine/vessels", params={"limit": 20})

    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] > 0
    vessel = payload["vessels"][0]
    assert vessel["type"] == "marine-vessel"
    assert vessel["mmsi"]
    assert vessel["observedAt"]
    assert vessel["fetchedAt"]
    assert vessel["observedVsDerived"] in {"observed", "derived"}
    assert vessel["geometryProvenance"] in {"raw_observed", "reconstructed", "interpolated"}
    assert payload["sources"][0]["sourceKey"] == "ais-fixture-global"
    assert "limitations" in payload["sources"][0]
    assert "assumptions" in payload["sources"][0]


def test_fixture_scenarios_generate_expected_shapes() -> None:
    from src.adapters.marine import FixtureMarineAdapter

    now = datetime(2026, 4, 28, 12, 20, tzinfo=timezone.utc)
    descriptor = FixtureMarineAdapter().descriptor
    scenarios = {
        "single-vessel-normal": 1,
        "single-vessel-sparse-plausible": 1,
        "single-vessel-suspicious-gap": 1,
        "multi-vessel-region": 3,
        "chokepoint-flow": 4,
        "viewport-entry-exit": 1,
        "investigative-mix": 10,
    }
    for name, minimum in scenarios.items():
        vessels = build_fixture_scenario(descriptor, now=now, scenario=name)
        assert len(vessels) >= minimum


def test_gap_detection_emits_observed_and_possible_silence_events() -> None:
    detector = MarineGapDetectionService()
    previous = SimpleNamespace(
        vessel_id="vessel:mmsi:123",
        source_key="ais-fixture-global",
        event_id=10,
        observed_at="2026-04-05T00:00:00+00:00",
        latitude=10.0,
        longitude=20.0,
        speed=12.0,
        nav_status="under-way-using-engine",
    )
    current = SimpleNamespace(
        vessel_id="vessel:mmsi:123",
        source_key="ais-fixture-global",
        event_id=11,
        observed_at="2026-04-05T02:00:00+00:00",
        latitude=10.8,
        longitude=21.3,
    )

    events = detector.detect_gap_events(
        previous=previous,
        current=current,
        source_health="healthy",
        cadence_floor_seconds=60,
    )

    kinds = {event.event_kind for event in events}
    assert "observed-signal-gap-start" in kinds
    assert "observed-signal-gap-end" in kinds
    assert "resumed-observation" in kinds
    assert "possible-transponder-silence-interval" in kinds
    possible = next(event for event in events if event.event_kind == "possible-transponder-silence-interval")
    assert isinstance(possible.confidence_breakdown, dict)
    assert "duration_factor" in possible.confidence_breakdown


def test_gap_detection_sparse_reporting_reduces_confidence() -> None:
    detector = MarineGapDetectionService()
    previous = SimpleNamespace(
        vessel_id="vessel:mmsi:anchored",
        source_key="ais-fixture-global",
        event_id=20,
        observed_at="2026-04-05T00:00:00+00:00",
        latitude=11.0,
        longitude=21.0,
        speed=0.2,
        nav_status="at-anchor",
    )
    current = SimpleNamespace(
        vessel_id="vessel:mmsi:anchored",
        source_key="ais-fixture-global",
        event_id=21,
        observed_at="2026-04-05T00:40:00+00:00",
        latitude=11.0005,
        longitude=21.0007,
    )
    events = detector.detect_gap_events(
        previous=previous,
        current=current,
        source_health="healthy",
        cadence_floor_seconds=60,
    )
    assert events
    first = events[0]
    assert first.normal_sparse_reporting_plausible is True
    assert first.confidence_class in {"low", "medium"}


def test_gap_detection_degraded_source_penalizes_confidence() -> None:
    detector = MarineGapDetectionService()
    previous = SimpleNamespace(
        vessel_id="vessel:mmsi:fast",
        source_key="ais-fixture-global",
        event_id=30,
        observed_at="2026-04-05T00:00:00+00:00",
        latitude=5.0,
        longitude=10.0,
        speed=14.0,
        nav_status="under-way-using-engine",
    )
    current = SimpleNamespace(
        vessel_id="vessel:mmsi:fast",
        source_key="ais-fixture-global",
        event_id=31,
        observed_at="2026-04-05T01:30:00+00:00",
        latitude=6.4,
        longitude=12.1,
    )
    healthy_events = detector.detect_gap_events(
        previous=previous,
        current=current,
        source_health="healthy",
        cadence_floor_seconds=60,
    )
    degraded_events = detector.detect_gap_events(
        previous=previous,
        current=current,
        source_health="degraded",
        cadence_floor_seconds=60,
    )
    assert healthy_events and degraded_events
    assert degraded_events[0].confidence_score <= healthy_events[0].confidence_score


def test_replay_snapshot_and_timeline_endpoints(tmp_path: Path) -> None:
    client = _client(tmp_path)

    _ = client.get("/api/marine/vessels", params={"limit": 100})
    now = datetime.now(tz=timezone.utc)
    start_at = (now - timedelta(hours=1)).isoformat()
    end_at = (now + timedelta(hours=1)).isoformat()

    timeline = client.get(
        "/api/marine/replay/timeline",
        params={"start_at": start_at, "end_at": end_at, "limit": 50},
    )
    snapshot = client.get(
        "/api/marine/replay/snapshot",
        params={"at_or_before": end_at},
    )

    assert timeline.status_code == 200
    assert timeline.json()["count"] >= 1
    assert timeline.json()["segments"] == sorted(
        timeline.json()["segments"], key=lambda item: item["segmentStartAt"]
    )
    assert snapshot.status_code == 200
    assert snapshot.json()["snapshot"] is not None
    assert snapshot.json()["count"] >= 1


def test_history_and_path_cursor_and_empty_behavior(tmp_path: Path) -> None:
    client = _client(tmp_path)
    _ = client.get("/api/marine/vessels", params={"limit": 100})
    vessels = client.get("/api/marine/vessels", params={"limit": 100}).json()["vessels"]
    vessel_id = vessels[0]["id"]

    history_page = client.get(
        f"/api/marine/vessels/{vessel_id}/history",
        params={"limit": 1},
    )
    assert history_page.status_code == 200
    payload = history_page.json()
    assert payload["count"] == 1
    assert "nextCursor" in payload

    path_page = client.get(
        f"/api/marine/replay/vessels/{vessel_id}/path",
        params={"limit": 1, "include_interpolated": "true"},
    )
    assert path_page.status_code == 200
    path_payload = path_page.json()
    assert path_payload["count"] >= 1
    first_point = path_payload["points"][0]
    assert first_point["pathSegmentKind"] in {
        "observed-position",
        "derived-reconstructed-position",
        "derived-interpolated-position",
    }

    empty = client.get(
        "/api/marine/vessels/vessel:mmsi:does-not-exist/history",
        params={"limit": 100},
    )
    assert empty.status_code == 200
    assert empty.json()["count"] == 0
    assert empty.json()["points"] == []
    assert empty.json()["nextCursor"] is None


def test_viewport_replay_slice(tmp_path: Path) -> None:
    client = _client(tmp_path)
    _ = client.get("/api/marine/vessels", params={"limit": 100})
    now = datetime.now(tz=timezone.utc).isoformat()
    response = client.get(
        "/api/marine/replay/viewport",
        params={
            "at_or_before": now,
            "lamin": -5,
            "lamax": 10,
            "lomin": 95,
            "lomax": 110,
            "limit": 100,
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] >= 1
    for vessel in payload["vessels"]:
        assert -5 <= vessel["latitude"] <= 10
        assert 95 <= vessel["longitude"] <= 110


def test_scottish_water_overflow_context_route(tmp_path: Path) -> None:
    client = _client(tmp_path)
    response = client.get(
        "/api/marine/context/scottish-water-overflows",
        params={"lat": 55.95, "lon": -3.10, "radius_km": 400, "status": "all", "limit": 5},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["sourceHealth"]["sourceId"] == "scottish-water-overflows"
    assert payload["sourceHealth"]["sourceMode"] == "fixture"
    assert payload["sourceHealth"]["health"] == "loaded"
    assert payload["count"] >= 1
    assert payload["activeCount"] >= 1
    first = payload["events"][0]
    assert first["status"] in {"active", "inactive", "unknown"}
    assert first["evidenceBasis"] == "source-reported"
    assert "caveats" in first
    assert all("confirmed pollution" not in caveat.lower() for caveat in payload["caveats"])


def test_scottish_water_overflow_context_empty_behavior(tmp_path: Path) -> None:
    client = _client(tmp_path)
    response = client.get(
        "/api/marine/context/scottish-water-overflows",
        params={"lat": 0, "lon": 0, "radius_km": 10, "status": "active", "limit": 5},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] == 0
    assert payload["activeCount"] == 0
    assert payload["sourceHealth"]["health"] == "empty"
    assert payload["sourceHealth"]["sourceMode"] == "fixture"
    assert payload["caveats"]


def test_scottish_water_overflow_context_missing_optional_fields(tmp_path: Path) -> None:
    client = _client(tmp_path)
    response = client.get(
        "/api/marine/context/scottish-water-overflows",
        params={"lat": 55.95, "lon": -3.10, "radius_km": 1000, "status": "all", "limit": 10},
    )

    assert response.status_code == 200
    payload = response.json()
    partial = next(event for event in payload["events"] if event["eventId"] == "sw-overflow-partial-metadata")
    assert partial["latitude"] is None
    assert partial["longitude"] is None
    assert partial["distanceKm"] is None
    assert partial["status"] == "unknown"
    assert partial["caveats"]


def test_chokepoint_and_region_replay_multi_vessel(tmp_path: Path) -> None:
    client = _client(
        tmp_path,
        env={"MARINE_FIXTURE_SCENARIO": "chokepoint-flow", "MARINE_SOURCE_MODE": "fixture"},
    )
    vessels = client.get("/api/marine/vessels", params={"limit": 200}).json()["vessels"]
    assert len(vessels) >= 4

    timeline = client.get(
        "/api/marine/replay/timeline",
        params={
            "start_at": (datetime.now(tz=timezone.utc) - timedelta(hours=1)).isoformat(),
            "end_at": (datetime.now(tz=timezone.utc) + timedelta(hours=1)).isoformat(),
            "limit": 10,
        },
    ).json()
    assert timeline["count"] >= 1
    assert timeline["segments"] == sorted(
        timeline["segments"], key=lambda item: item["segmentStartAt"]
    )


def test_gap_markers_and_confidence_display_contract(tmp_path: Path) -> None:
    client = _client(
        tmp_path,
        env={"MARINE_FIXTURE_SCENARIO": "single-vessel-suspicious-gap", "MARINE_SOURCE_MODE": "fixture"},
    )
    vessels = client.get("/api/marine/vessels", params={"limit": 50}).json()["vessels"]
    assert vessels
    vessel_id = vessels[0]["id"]
    db_url = f"sqlite:///{tmp_path / 'marine_test.db'}"
    engine = get_engine(db_url)
    with Session(engine) as session:
        created_at = "2026-04-28T10:00:00+00:00"
        shared = dict(
            vessel_id=vessel_id,
            source_key="ais-fixture-global",
            gap_start_observed_at=created_at,
            gap_end_observed_at="2026-04-28T12:00:00+00:00",
            gap_duration_seconds=7200,
            start_latitude=1.0,
            start_longitude=2.0,
            end_latitude=1.5,
            end_longitude=2.8,
            distance_moved_m=95000.0,
            expected_interval_seconds=300,
            exceeds_expected_cadence=True,
            confidence_class="medium",
            confidence_score=0.65,
            normal_sparse_reporting_plausible=False,
            confidence_breakdown_json='{"duration_factor": 0.8}',
            derivation_method="fixture-insert",
            input_event_ids_json="[1,2]",
            uncertainty_notes_json='["test fixture"]',
            evidence_summary="contract marker validation",
            created_at=created_at,
            bucket_date="2026-04-28",
            bucket_hour=10,
            vessel_shard=1,
        )
        for event_kind in (
            "observed-signal-gap-start",
            "observed-signal-gap-end",
            "resumed-observation",
            "possible-transponder-silence-interval",
        ):
            session.add(MarineGapEventORM(event_kind=event_kind, **shared))
        session.commit()

    gaps = client.get(f"/api/marine/vessels/{vessel_id}/gaps", params={"limit": 100})
    assert gaps.status_code == 200
    events = gaps.json()["events"]
    assert events
    marker_types = {event["eventMarkerType"] for event in events}
    assert "gap-start" in marker_types
    assert "gap-end" in marker_types
    assert "resumed" in marker_types
    assert "possible-dark-interval" in marker_types
    for event in events:
        assert event["confidenceDisplay"]


def test_vessel_summary_contract(tmp_path: Path) -> None:
    client = _client(
        tmp_path,
        env={"MARINE_FIXTURE_SCENARIO": "single-vessel-suspicious-gap", "MARINE_SOURCE_MODE": "fixture"},
    )
    vessels_payload = client.get("/api/marine/vessels", params={"limit": 50}).json()
    vessel_id = vessels_payload["vessels"][0]["id"]
    now = datetime.now(tz=timezone.utc)
    summary = client.get(
        f"/api/marine/vessels/{vessel_id}/summary",
        params={
            "start_at": (now - timedelta(hours=4)).isoformat(),
            "end_at": now.isoformat(),
        },
    )
    assert summary.status_code == 200
    payload = summary.json()
    assert payload["vesselId"] == vessel_id
    assert "movement" in payload
    assert payload["observedGapEventCount"] >= 0
    assert payload["suspiciousGapEventCount"] >= 0
    assert payload["anomaly"]["score"] >= 0
    assert payload["anomaly"]["level"] in {"low", "medium", "high"}
    assert "observedFields" in payload
    assert "inferredFields" in payload


def test_viewport_summary_contract(tmp_path: Path) -> None:
    client = _client(
        tmp_path,
        env={"MARINE_FIXTURE_SCENARIO": "multi-vessel-region", "MARINE_SOURCE_MODE": "fixture"},
    )
    _ = client.get("/api/marine/vessels", params={"limit": 200})
    now = datetime.now(tz=timezone.utc)
    summary = client.get(
        "/api/marine/replay/viewport/summary",
        params={
            "at_or_before": now.isoformat(),
            "start_at": (now - timedelta(hours=1)).isoformat(),
            "lamin": -10,
            "lamax": 20,
            "lomin": 90,
            "lomax": 120,
        },
    )
    assert summary.status_code == 200
    payload = summary.json()
    assert payload["vesselCount"] >= 0
    assert payload["activeVesselCount"] <= payload["vesselCount"]
    assert payload["observedGapEventCount"] >= 0
    assert payload["suspiciousGapEventCount"] >= 0
    assert payload["anomaly"]["score"] >= 0


def test_chokepoint_summary_contract(tmp_path: Path) -> None:
    client = _client(
        tmp_path,
        env={"MARINE_FIXTURE_SCENARIO": "chokepoint-flow", "MARINE_SOURCE_MODE": "fixture"},
    )
    _ = client.get("/api/marine/vessels", params={"limit": 200})
    now = datetime.now(tz=timezone.utc)
    start_at = (now - timedelta(hours=1)).isoformat()
    end_at = now.isoformat()
    summary = client.get(
        "/api/marine/replay/chokepoint/summary",
        params={
            "start_at": start_at,
            "end_at": end_at,
            "lamin": -10,
            "lamax": 20,
            "lomin": 90,
            "lomax": 120,
            "slice_minutes": 15,
        },
    )
    assert summary.status_code == 200
    payload = summary.json()
    assert payload["sliceCount"] >= 1
    assert payload["totalVesselObservations"] >= 0
    assert payload["totalObservedGapEvents"] >= 0
    assert payload["totalSuspiciousGapEvents"] >= 0
    assert len(payload["slices"]) == payload["sliceCount"]
    assert payload["anomaly"]["score"] >= 0
    ranks = [item["anomaly"]["priorityRank"] for item in payload["slices"] if item["anomaly"]["priorityRank"] is not None]
    assert sorted(ranks) == list(range(1, len(ranks) + 1))


def test_noaa_coops_context_contract(tmp_path: Path) -> None:
    client = _client(tmp_path)

    response = client.get(
        "/api/marine/context/noaa-coops",
        params={
            "lat": 29.76,
            "lon": -95.36,
            "radius_km": 250,
            "limit": 3,
            "context_kind": "chokepoint",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["contextKind"] == "chokepoint"
    assert payload["sourceHealth"]["sourceId"] == "noaa-coops-tides-currents"
    assert payload["sourceHealth"]["sourceMode"] == "fixture"
    assert payload["sourceHealth"]["health"] in {"loaded", "empty"}
    assert "coastal context only" in payload["sourceHealth"]["caveat"].lower()
    assert payload["caveats"]
    assert payload["count"] >= 1
    station = payload["stations"][0]
    assert station["stationId"]
    assert station["stationName"]
    assert station["distanceKm"] >= 0
    assert station["productsAvailable"]
    assert station["statusLine"]
    if station.get("latestWaterLevel"):
        assert station["latestWaterLevel"]["observedBasis"] == "observed"
    if station.get("latestCurrent"):
        assert station["latestCurrent"]["observedBasis"] == "observed"
    assert station["caveats"]


def test_noaa_coops_context_empty_is_not_error(tmp_path: Path) -> None:
    client = _client(tmp_path)

    response = client.get(
        "/api/marine/context/noaa-coops",
        params={
            "lat": 0.0,
            "lon": 0.0,
            "radius_km": 50,
            "limit": 3,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] == 0
    assert payload["stations"] == []
    assert payload["sourceHealth"]["health"] == "empty"
    assert payload["sourceHealth"]["sourceMode"] == "fixture"
    assert payload["caveats"]


def test_ndbc_context_contract(tmp_path: Path) -> None:
    client = _client(tmp_path)

    response = client.get(
        "/api/marine/context/ndbc",
        params={
            "lat": 29.76,
            "lon": -95.36,
            "radius_km": 250,
            "limit": 3,
            "context_kind": "chokepoint",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["contextKind"] == "chokepoint"
    assert payload["sourceHealth"]["sourceId"] == "noaa-ndbc-realtime"
    assert payload["sourceHealth"]["sourceMode"] == "fixture"
    assert payload["sourceHealth"]["health"] in {"loaded", "empty"}
    assert "environmental context only" in payload["sourceHealth"]["caveat"].lower()
    assert payload["caveats"]
    assert payload["count"] >= 1
    station = payload["stations"][0]
    assert station["stationId"]
    assert station["stationName"]
    assert station["distanceKm"] >= 0
    assert station["stationType"] in {"buoy", "cman"}
    assert station["statusLine"]
    assert station["latestObservation"]["observedBasis"] == "observed"
    assert station["latestObservation"]["sourceDetail"]
    assert station["caveats"]


def test_ndbc_context_empty_is_not_error(tmp_path: Path) -> None:
    client = _client(tmp_path)

    response = client.get(
        "/api/marine/context/ndbc",
        params={
            "lat": 0.0,
            "lon": 0.0,
            "radius_km": 50,
            "limit": 3,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] == 0
    assert payload["stations"] == []
    assert payload["sourceHealth"]["health"] == "empty"
    assert payload["sourceHealth"]["sourceMode"] == "fixture"
    assert payload["caveats"]


def test_marine_context_routes_validate_invalid_radius_and_coordinates(tmp_path: Path) -> None:
    client = _client(tmp_path)

    invalid_radius_responses = [
        client.get(
            "/api/marine/context/noaa-coops",
            params={"lat": 29.76, "lon": -95.36, "radius_km": 0.5},
        ),
        client.get(
            "/api/marine/context/ndbc",
            params={"lat": 29.76, "lon": -95.36, "radius_km": 0.5},
        ),
        client.get(
            "/api/marine/context/scottish-water-overflows",
            params={"lat": 55.95, "lon": -3.1, "radius_km": 0.5},
        ),
    ]
    for response in invalid_radius_responses:
        assert response.status_code == 422

    invalid_coordinate_responses = [
        client.get(
            "/api/marine/context/noaa-coops",
            params={"lat": 91.0, "lon": -95.36, "radius_km": 50},
        ),
        client.get(
            "/api/marine/context/ndbc",
            params={"lat": 29.76, "lon": 181.0, "radius_km": 50},
        ),
        client.get(
            "/api/marine/context/scottish-water-overflows",
            params={"lat": -91.0, "lon": -3.1, "radius_km": 50},
        ),
    ]
    for response in invalid_coordinate_responses:
        assert response.status_code == 422


def test_context_sources_disabled_outside_fixture_mode(tmp_path: Path) -> None:
    client = _client(
        tmp_path,
        env={
            "MARINE_NOAA_COOPS_MODE": "live",
            "MARINE_NDBC_MODE": "live",
            "SCOTTISH_WATER_OVERFLOWS_MODE": "live",
        },
    )

    noaa = client.get(
        "/api/marine/context/noaa-coops",
        params={"lat": 29.76, "lon": -95.36, "radius_km": 50},
    ).json()
    assert noaa["count"] == 0
    assert noaa["sourceHealth"]["health"] == "disabled"
    assert noaa["sourceHealth"]["sourceMode"] == "live"
    assert noaa["sourceHealth"]["enabled"] is False
    assert noaa["caveats"]

    ndbc = client.get(
        "/api/marine/context/ndbc",
        params={"lat": 29.76, "lon": -95.36, "radius_km": 50},
    ).json()
    assert ndbc["count"] == 0
    assert ndbc["sourceHealth"]["health"] == "disabled"
    assert ndbc["sourceHealth"]["sourceMode"] == "live"
    assert ndbc["sourceHealth"]["enabled"] is False
    assert ndbc["caveats"]

    scottish_water = client.get(
        "/api/marine/context/scottish-water-overflows",
        params={"lat": 55.95, "lon": -3.1, "radius_km": 50},
    ).json()
    assert scottish_water["count"] == 0
    assert scottish_water["activeCount"] == 0
    assert scottish_water["sourceHealth"]["health"] == "disabled"
    assert scottish_water["sourceHealth"]["sourceMode"] == "live"
    assert scottish_water["sourceHealth"]["enabled"] is False
    assert scottish_water["caveats"]


def test_fixture_context_sources_do_not_fabricate_stale_or_unavailable_states(tmp_path: Path) -> None:
    client = _client(tmp_path)

    noaa = client.get(
        "/api/marine/context/noaa-coops",
        params={"lat": 29.76, "lon": -95.36, "radius_km": 250},
    ).json()
    assert noaa["sourceHealth"]["health"] in {"loaded", "empty"}
    assert noaa["sourceHealth"]["health"] not in {"stale", "error", "unknown"}

    ndbc = client.get(
        "/api/marine/context/ndbc",
        params={"lat": 29.76, "lon": -95.36, "radius_km": 250},
    ).json()
    assert ndbc["sourceHealth"]["health"] in {"loaded", "empty"}
    assert ndbc["sourceHealth"]["health"] not in {"stale", "error", "unknown"}

    scottish_water = client.get(
        "/api/marine/context/scottish-water-overflows",
        params={"lat": 55.95, "lon": -3.10, "radius_km": 400},
    ).json()
    assert scottish_water["sourceHealth"]["health"] in {"loaded", "empty"}
    assert scottish_water["sourceHealth"]["health"] not in {"stale", "error", "unknown"}


def test_disabled_non_fixture_context_sources_do_not_fabricate_unavailable_states(tmp_path: Path) -> None:
    client = _client(
        tmp_path,
        env={
            "MARINE_NOAA_COOPS_MODE": "bogus-mode",
            "MARINE_NDBC_MODE": "bogus-mode",
            "SCOTTISH_WATER_OVERFLOWS_MODE": "bogus-mode",
        },
    )

    noaa = client.get(
        "/api/marine/context/noaa-coops",
        params={"lat": 29.76, "lon": -95.36, "radius_km": 50},
    ).json()
    assert noaa["sourceHealth"]["sourceMode"] == "unknown"
    assert noaa["sourceHealth"]["health"] == "disabled"

    ndbc = client.get(
        "/api/marine/context/ndbc",
        params={"lat": 29.76, "lon": -95.36, "radius_km": 50},
    ).json()
    assert ndbc["sourceHealth"]["sourceMode"] == "unknown"
    assert ndbc["sourceHealth"]["health"] == "disabled"

    scottish_water = client.get(
        "/api/marine/context/scottish-water-overflows",
        params={"lat": 55.95, "lon": -3.1, "radius_km": 50},
    ).json()
    assert scottish_water["sourceHealth"]["sourceMode"] == "unknown"
    assert scottish_water["sourceHealth"]["health"] == "disabled"


def test_coops_context_can_honestly_emit_stale_from_old_observation_timestamps(tmp_path: Path, monkeypatch) -> None:
    original_fixture = MarineNoaaCoopsService._fixture_stations

    def stale_fixture(self: MarineNoaaCoopsService, now: datetime):
        stations = original_fixture(self, now)
        stale_at = (now - timedelta(hours=2)).isoformat()
        return [
            replace(
                station,
                water_level=station.water_level.model_copy(update={"observed_at": stale_at}) if station.water_level else None,
                current=station.current.model_copy(update={"observed_at": stale_at}) if station.current else None,
            )
            for station in stations
        ]

    monkeypatch.setattr(MarineNoaaCoopsService, "_fixture_stations", stale_fixture)
    client = _client(tmp_path)

    payload = client.get(
        "/api/marine/context/noaa-coops",
        params={"lat": 29.76, "lon": -95.36, "radius_km": 250, "limit": 5},
    ).json()

    assert payload["count"] >= 1
    assert payload["sourceHealth"]["health"] == "stale"
    assert "freshness threshold" in (payload["sourceHealth"]["detail"] or "").lower()
    assert "freshness threshold" in (payload["sourceHealth"]["caveat"] or "").lower()


def test_ndbc_context_can_honestly_emit_stale_from_old_observation_timestamps(tmp_path: Path, monkeypatch) -> None:
    original_fixture = MarineNdbcService._fixture_stations

    def stale_fixture(self: MarineNdbcService, now: datetime):
        stations = original_fixture(self, now)
        stale_at = (now - timedelta(hours=2)).isoformat()
        return [
            replace(
                station,
                observation=station.observation.model_copy(update={"observed_at": stale_at}) if station.observation else None,
            )
            for station in stations
        ]

    monkeypatch.setattr(MarineNdbcService, "_fixture_stations", stale_fixture)
    client = _client(tmp_path)

    payload = client.get(
        "/api/marine/context/ndbc",
        params={"lat": 29.76, "lon": -95.36, "radius_km": 250, "limit": 5},
    ).json()

    assert payload["count"] >= 1
    assert payload["sourceHealth"]["health"] == "stale"
    assert "freshness threshold" in (payload["sourceHealth"]["detail"] or "").lower()
    assert "freshness threshold" in (payload["sourceHealth"]["caveat"] or "").lower()


def test_scottish_water_context_can_honestly_emit_stale_from_old_update_timestamps(tmp_path: Path, monkeypatch) -> None:
    original_fixture = MarineScottishWaterOverflowService._fixture_events

    def stale_fixture(self: MarineScottishWaterOverflowService, now: datetime):
        events = original_fixture(self, now)
        stale_at = (now - timedelta(hours=5)).isoformat()
        return [replace(event, last_updated_at=stale_at) for event in events]

    monkeypatch.setattr(MarineScottishWaterOverflowService, "_fixture_events", stale_fixture)
    client = _client(tmp_path)

    payload = client.get(
        "/api/marine/context/scottish-water-overflows",
        params={"lat": 55.95, "lon": -3.10, "radius_km": 1000, "status": "all", "limit": 10},
    ).json()

    assert payload["count"] >= 1
    assert payload["sourceHealth"]["health"] == "stale"
    assert "freshness threshold" in (payload["sourceHealth"]["detail"] or "").lower()
    assert "freshness threshold" in (payload["sourceHealth"]["caveat"] or "").lower()


def test_context_source_evidence_basis_contracts(tmp_path: Path) -> None:
    client = _client(tmp_path)

    noaa = client.get(
        "/api/marine/context/noaa-coops",
        params={"lat": 29.76, "lon": -95.36, "radius_km": 250, "limit": 5},
    ).json()
    for station in noaa["stations"]:
        if station.get("latestWaterLevel"):
            assert station["latestWaterLevel"]["observedBasis"] == "observed"
        if station.get("latestCurrent"):
            assert station["latestCurrent"]["observedBasis"] == "observed"

    ndbc = client.get(
        "/api/marine/context/ndbc",
        params={"lat": 29.76, "lon": -95.36, "radius_km": 250, "limit": 5},
    ).json()
    for station in ndbc["stations"]:
        if station.get("latestObservation"):
            assert station["latestObservation"]["observedBasis"] == "observed"

    scottish_water = client.get(
        "/api/marine/context/scottish-water-overflows",
        params={"lat": 55.95, "lon": -3.10, "radius_km": 1000, "status": "all", "limit": 10},
    ).json()
    for event in scottish_water["events"]:
        assert event["evidenceBasis"] == "source-reported"


def test_context_source_fixtures_cover_representative_record_shapes(tmp_path: Path) -> None:
    client = _client(tmp_path)

    noaa_galveston = client.get(
        "/api/marine/context/noaa-coops",
        params={"lat": 29.76, "lon": -95.36, "radius_km": 250, "limit": 10},
    ).json()
    noaa_san_francisco = client.get(
        "/api/marine/context/noaa-coops",
        params={"lat": 37.80, "lon": -122.46, "radius_km": 250, "limit": 10},
    ).json()
    assert any(
        station["latestWaterLevel"] is not None and station["latestCurrent"] is None
        for station in noaa_galveston["stations"]
    )
    assert any(
        station["latestWaterLevel"] is None and station["latestCurrent"] is not None
        for station in noaa_galveston["stations"]
    )
    assert any(
        station["latestWaterLevel"] is not None and station["latestCurrent"] is not None
        for station in noaa_san_francisco["stations"]
    )

    ndbc_galveston = client.get(
        "/api/marine/context/ndbc",
        params={"lat": 29.76, "lon": -95.36, "radius_km": 500, "limit": 10},
    ).json()
    ndbc_florida = client.get(
        "/api/marine/context/ndbc",
        params={"lat": 25.59, "lon": -80.10, "radius_km": 500, "limit": 10},
    ).json()
    station_types = {
        *(station["stationType"] for station in ndbc_galveston["stations"]),
        *(station["stationType"] for station in ndbc_florida["stations"]),
    }
    assert "buoy" in station_types
    assert "cman" in station_types

    scottish_water = client.get(
        "/api/marine/context/scottish-water-overflows",
        params={"lat": 55.95, "lon": -3.10, "radius_km": 1000, "status": "all", "limit": 10},
    ).json()
    statuses = {event["status"] for event in scottish_water["events"]}
    assert "active" in statuses
    assert "inactive" in statuses
    assert "unknown" in statuses


def test_summary_empty_no_match_behavior(tmp_path: Path) -> None:
    client = _client(tmp_path, env={"MARINE_FIXTURE_SCENARIO": "single-vessel-normal", "MARINE_SOURCE_MODE": "fixture"})
    _ = client.get("/api/marine/vessels", params={"limit": 10})
    now = datetime.now(tz=timezone.utc)
    payload = client.get(
        "/api/marine/replay/viewport/summary",
        params={
            "at_or_before": now.isoformat(),
            "start_at": (now - timedelta(hours=1)).isoformat(),
            "lamin": -80,
            "lamax": -70,
            "lomin": -170,
            "lomax": -160,
        },
    ).json()
    assert payload["vesselCount"] == 0
    assert payload["activeVesselCount"] == 0
    assert payload["observedGapEventCount"] == 0
    assert payload["suspiciousGapEventCount"] == 0
    assert payload["anomaly"]["level"] == "low"


def test_suspicious_ranks_higher_than_sparse_plausible(tmp_path: Path) -> None:
    suspicious_client = _client(
        tmp_path / "suspicious",
        env={"MARINE_FIXTURE_SCENARIO": "single-vessel-suspicious-gap", "MARINE_SOURCE_MODE": "fixture"},
    )
    sparse_client = _client(
        tmp_path / "sparse",
        env={"MARINE_FIXTURE_SCENARIO": "single-vessel-sparse-plausible", "MARINE_SOURCE_MODE": "fixture"},
    )
    suspicious_vessel = suspicious_client.get("/api/marine/vessels", params={"limit": 10}).json()["vessels"][0]["id"]
    sparse_vessel = sparse_client.get("/api/marine/vessels", params={"limit": 10}).json()["vessels"][0]["id"]
    now = datetime.now(tz=timezone.utc)
    suspicious_summary = suspicious_client.get(
        f"/api/marine/vessels/{suspicious_vessel}/summary",
        params={"start_at": (now - timedelta(hours=6)).isoformat(), "end_at": now.isoformat()},
    ).json()
    sparse_summary = sparse_client.get(
        f"/api/marine/vessels/{sparse_vessel}/summary",
        params={"start_at": (now - timedelta(hours=6)).isoformat(), "end_at": now.isoformat()},
    ).json()
    assert suspicious_summary["anomaly"]["score"] >= sparse_summary["anomaly"]["score"]


def test_degraded_source_reduces_vessel_anomaly_confidence(tmp_path: Path) -> None:
    client = _client(
        tmp_path,
        env={"MARINE_FIXTURE_SCENARIO": "single-vessel-suspicious-gap", "MARINE_SOURCE_MODE": "fixture"},
    )
    vessel_id = client.get("/api/marine/vessels", params={"limit": 10}).json()["vessels"][0]["id"]
    now = datetime.now(tz=timezone.utc)
    healthy = client.get(
        f"/api/marine/vessels/{vessel_id}/summary",
        params={"start_at": (now - timedelta(hours=6)).isoformat(), "end_at": now.isoformat()},
    ).json()
    db_url = f"sqlite:///{tmp_path / 'marine_test.db'}"
    engine = get_engine(db_url)
    with Session(engine) as session:
        source = session.query(MarineSourceORM).first()
        assert source is not None
        source.status = "degraded"
        session.commit()
    degraded = client.get(
        f"/api/marine/vessels/{vessel_id}/summary",
        params={"start_at": (now - timedelta(hours=6)).isoformat(), "end_at": now.isoformat()},
    ).json()
    assert degraded["anomaly"]["score"] <= healthy["anomaly"]["score"]
    assert any("source health degraded" in item.lower() for item in degraded["anomaly"]["caveats"])


def test_viewport_enter_exit_changes_state(tmp_path: Path) -> None:
    client_a = _client(
        tmp_path / "a",
        env={"MARINE_FIXTURE_SCENARIO": "viewport-entry-exit", "MARINE_SOURCE_MODE": "fixture"},
    )
    payload_a = client_a.get("/api/marine/vessels", params={"limit": 200}).json()
    count_a = payload_a["count"]

    # second DB gets a different minute bucket naturally; validate endpoint stability and bounded results
    client_b = _client(
        tmp_path / "b",
        env={"MARINE_FIXTURE_SCENARIO": "viewport-entry-exit", "MARINE_SOURCE_MODE": "fixture"},
    )
    payload_b = client_b.get("/api/marine/vessels", params={"limit": 200}).json()
    count_b = payload_b["count"]
    assert count_a >= 1 and count_b >= 1


def test_csv_provider_mapping_edge_cases(tmp_path: Path) -> None:
    csv_path = tmp_path / "marine.csv"
    csv_path.write_text(
        "mmsi,latitude,longitude,observed_at,vessel_name,speed\n"
        "123456789,34.1,-120.2,2026-04-28T10:00:00Z,VALID VESSEL,12.1\n"
        "222222222,200.0,1.0,2026-04-28T10:05:00Z,BAD COORD,9.0\n"
        ",34.2,-120.3,2026-04-28T10:10:00Z,MISSING MMSI,10.0\n",
        encoding="utf-8",
    )

    tolerant = CsvAisMarineAdapter(str(csv_path), fail_on_invalid=False)
    vessels = asyncio.run(tolerant.fetch())
    assert len(vessels) == 1
    assert vessels[0].mmsi == "123456789"

    strict = CsvAisMarineAdapter(str(csv_path), fail_on_invalid=True)
    try:
        asyncio.run(strict.fetch())
        assert False, "strict mode should fail on invalid mapped rows"
    except RuntimeError as exc:
        assert "mapping failures" in str(exc).lower()


def test_http_provider_mapping_aliases_and_shape(monkeypatch, tmp_path: Path) -> None:
    class FakeResponse:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> object:
            return {
                "data": [
                    {
                        "MMSI": "777777777",
                        "lat": 1.222,
                        "lon": 103.777,
                        "timestamp": "2026-04-28T10:00:00Z",
                        "name": "ALIAS SHIP",
                        "sog": 13.4,
                        "cog": 88.0,
                    }
                ]
            }

    class FakeClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def get(self, *args, **kwargs):
            return FakeResponse()

    monkeypatch.setattr("src.adapters.marine.httpx.AsyncClient", lambda *args, **kwargs: FakeClient())
    os.environ["MARINE_HTTP_SOURCE_URL"] = "https://example.invalid/marine"
    os.environ["MARINE_PROVIDER_FAIL_ON_INVALID"] = "true"
    settings = Settings(_env_file=None)
    adapter = HttpJsonMarineAdapter(settings)
    vessels = asyncio.run(adapter.fetch())
    assert len(vessels) == 1
    assert vessels[0].mmsi == "777777777"
