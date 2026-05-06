from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.config.settings import get_settings
from src.routes.events import router as events_router


def _client_with_fixture(fixture_path: Path) -> TestClient:
    app = FastAPI()
    app.include_router(events_router)
    app.dependency_overrides[get_settings] = lambda: get_settings().model_copy(
        update={
            "nws_alerts_source_mode": "fixture",
            "nws_alerts_fixture_path": str(fixture_path),
        }
    )
    return TestClient(app)


def _client_with_disabled_mode() -> TestClient:
    app = FastAPI()
    app.include_router(events_router)
    app.dependency_overrides[get_settings] = lambda: get_settings().model_copy(
        update={
            "nws_alerts_source_mode": "disabled",
        }
    )
    return TestClient(app)


def test_nws_alerts_fixture_parsing_and_provenance() -> None:
    fixture = Path(__file__).resolve().parents[1] / "data" / "nws_alerts_fixture.json"
    client = _client_with_fixture(fixture)

    payload = client.get("/api/events/nws-alerts/recent").json()
    assert payload["metadata"]["source"] == "nws-alerts"
    assert payload["metadata"]["sourceMode"] == "fixture"
    assert payload["metadata"]["userAgentRequired"] is True
    assert payload["sourceHealth"]["health"] == "loaded"
    assert payload["count"] == 3
    assert payload["alerts"][0]["alertType"] == "warning"
    assert payload["alerts"][0]["areaCodes"] == ["KS"]
    assert "action" in " ".join(payload["caveats"]).lower()


def test_nws_alerts_filters_and_sorting() -> None:
    fixture = Path(__file__).resolve().parents[1] / "data" / "nws_alerts_fixture.json"
    client = _client_with_fixture(fixture)

    by_area = client.get("/api/events/nws-alerts/recent", params={"area": "KS"}).json()
    assert by_area["count"] == 1
    assert by_area["alerts"][0]["areaCodes"] == ["KS"]

    by_zone = client.get("/api/events/nws-alerts/recent", params={"zone": "PAZ029"}).json()
    assert by_zone["count"] == 1
    assert "PAZ029" in by_zone["alerts"][0]["zoneCodes"]

    by_severity = client.get("/api/events/nws-alerts/recent", params={"severity": "moderate"}).json()
    assert by_severity["count"] == 1
    assert by_severity["alerts"][0]["severity"] == "moderate"

    by_event = client.get("/api/events/nws-alerts/recent", params={"event": "Heat"}).json()
    assert by_event["count"] == 1
    assert by_event["alerts"][0]["alertType"] == "advisory"

    sorted_payload = client.get("/api/events/nws-alerts/recent", params={"sort": "severity"}).json()
    assert sorted_payload["alerts"][0]["severity"] == "severe"


def test_nws_alerts_geometry_and_inert_text_handling() -> None:
    fixture = Path(__file__).resolve().parents[1] / "data" / "nws_alerts_fixture.json"
    client = _client_with_fixture(fixture)

    payload = client.get("/api/events/nws-alerts/recent").json()
    warning = payload["alerts"][0]
    watch = next(alert for alert in payload["alerts"] if alert["alertType"] == "watch")

    assert warning["latitude"] is not None
    assert warning["longitude"] is not None
    assert warning["geometrySummary"] is not None
    assert watch["latitude"] is None
    assert watch["longitude"] is None

    blob = " ".join(
        payload["caveats"]
        + [alert.get("instruction") or "" for alert in payload["alerts"]]
        + [alert.get("description") or "" for alert in payload["alerts"]]
    )
    assert "<script" not in blob.lower()
    assert "workflow behavior" in blob.lower()


def test_nws_alerts_empty_disabled_and_invalid_params() -> None:
    fixture = Path(__file__).resolve().parents[1] / "data" / "nws_alerts_fixture.json"
    client = _client_with_fixture(fixture)

    empty = client.get("/api/events/nws-alerts/recent", params={"area": "AK"}).json()
    assert empty["count"] == 0
    assert empty["sourceHealth"]["health"] == "empty"

    bad_alert_type = client.get("/api/events/nws-alerts/recent", params={"alert_type": "bad"})
    assert bad_alert_type.status_code == 400

    bad_sort = client.get("/api/events/nws-alerts/recent", params={"sort": "bad"})
    assert bad_sort.status_code == 400

    disabled_client = _client_with_disabled_mode()
    disabled = disabled_client.get("/api/events/nws-alerts/recent").json()
    assert disabled["count"] == 0
    assert disabled["sourceHealth"]["health"] == "disabled"
