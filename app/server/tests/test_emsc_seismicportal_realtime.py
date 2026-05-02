from __future__ import annotations

import os
from pathlib import Path

from fastapi.testclient import TestClient

from src.app import create_application
from src.config.settings import get_settings


def _client(fixture_path: Path) -> TestClient:
    os.environ["APP_ENV"] = "test"
    os.environ["EMSC_SEISMICPORTAL_SOURCE_MODE"] = "fixture"
    os.environ["EMSC_SEISMICPORTAL_FIXTURE_PATH"] = str(fixture_path)
    os.environ["WEBCAM_WORKER_ENABLED"] = "false"
    os.environ["WEBCAM_WORKER_RUN_ON_STARTUP"] = "false"
    get_settings.cache_clear()
    return TestClient(create_application())


def test_emsc_fixture_parsing_and_provenance() -> None:
    fixture = Path(__file__).resolve().parents[1] / "data" / "emsc_seismicportal_realtime_fixture.json"
    client = _client(fixture)

    response = client.get("/api/events/emsc-seismicportal/recent")
    payload = response.json()

    assert response.status_code == 200
    assert payload["count"] == 3
    assert payload["metadata"]["source"] == "emsc-seismicportal-realtime"
    assert payload["metadata"]["streamUrl"] == "wss://www.seismicportal.eu/standing_order/websocket"
    assert payload["metadata"]["documentationUrl"] == "https://www.seismicportal.eu/realtime.html"
    assert payload["metadata"]["fdsnEventUrl"] == "https://www.seismicportal.eu/fdsnws/event/1/"
    assert payload["metadata"]["sourceMode"] == "fixture"
    assert payload["sourceHealth"]["health"] == "loaded"
    assert payload["events"][0]["evidenceBasis"] == "source-reported"


def test_emsc_filters_limit_and_sort() -> None:
    fixture = Path(__file__).resolve().parents[1] / "data" / "emsc_seismicportal_realtime_fixture.json"
    client = _client(fixture)

    payload = client.get(
        "/api/events/emsc-seismicportal/recent",
        params={"action": "create", "min_magnitude": 4.0, "limit": 1, "sort": "magnitude"},
    ).json()

    assert payload["count"] == 1
    assert payload["events"][0]["externalId"] == "20260502_001"
    assert payload["events"][0]["magnitude"] >= 4.0


def test_emsc_bbox_filter_and_no_match() -> None:
    fixture = Path(__file__).resolve().parents[1] / "data" / "emsc_seismicportal_realtime_fixture.json"
    client = _client(fixture)

    bounded = client.get(
        "/api/events/emsc-seismicportal/recent",
        params={"bbox": "8,43,13,46"},
    ).json()
    assert bounded["count"] == 1
    assert bounded["events"][0]["externalId"] == "20260502_003"

    no_match = client.get(
        "/api/events/emsc-seismicportal/recent",
        params={"min_magnitude": 9.9},
    ).json()
    assert no_match["count"] == 0
    assert no_match["events"] == []
    assert no_match["sourceHealth"]["health"] == "empty"


def test_emsc_sanitizes_free_text_and_preserves_inertness() -> None:
    fixture = Path(__file__).resolve().parents[1] / "data" / "emsc_seismicportal_realtime_fixture.json"
    client = _client(fixture)

    payload = client.get("/api/events/emsc-seismicportal/recent").json()
    export_blob = " ".join(payload["caveats"] + [event["title"] for event in payload["events"]] + [event.get("region") or "" for event in payload["events"]])

    assert "<script" not in export_blob.lower()
    assert "workflow behavior" in " ".join(payload["caveats"]).lower()
    assert "damage" in payload["metadata"]["caveat"].lower()


def test_emsc_invalid_params_return_400() -> None:
    fixture = Path(__file__).resolve().parents[1] / "data" / "emsc_seismicportal_realtime_fixture.json"
    client = _client(fixture)

    bad_bbox = client.get("/api/events/emsc-seismicportal/recent", params={"bbox": "1,2,3"})
    assert bad_bbox.status_code == 400

    bad_sort = client.get("/api/events/emsc-seismicportal/recent", params={"sort": "bad"})
    assert bad_sort.status_code == 400

    bad_action = client.get("/api/events/emsc-seismicportal/recent", params={"action": "bad"})
    assert bad_action.status_code == 400
