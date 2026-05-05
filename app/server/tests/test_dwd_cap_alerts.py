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
            "dwd_cap_source_mode": "fixture",
            "dwd_cap_fixture_path": str(fixture_path),
        }
    )
    return TestClient(app)


def _client_with_disabled_mode() -> TestClient:
    app = FastAPI()
    app.include_router(events_router)
    app.dependency_overrides[get_settings] = lambda: get_settings().model_copy(
        update={
            "dwd_cap_source_mode": "disabled",
        }
    )
    return TestClient(app)


def test_dwd_cap_fixture_parsing_and_provenance() -> None:
    fixture = Path(__file__).resolve().parents[1] / "data" / "dwd_cap_directory_fixture.html"
    client = _client_with_fixture(fixture)

    payload = client.get("/api/events/dwd-alerts/recent").json()
    assert payload["metadata"]["source"] == "dwd-cap-alerts"
    assert payload["metadata"]["sourceMode"] == "fixture"
    assert payload["metadata"]["snapshotFamily"] == "DISTRICT_DWD_STAT"
    assert payload["sourceHealth"]["health"] == "loaded"
    assert payload["count"] == 2
    assert payload["alerts"][0]["capId"] == "dwd-cap-001"
    assert payload["alerts"][0]["language"] == "de-DE"
    assert payload["alerts"][0]["productFamily"] == "DISTRICT_DWD_STAT"


def test_dwd_cap_severity_event_and_sort_filters() -> None:
    fixture = Path(__file__).resolve().parents[1] / "data" / "dwd_cap_directory_fixture.html"
    client = _client_with_fixture(fixture)

    severe = client.get("/api/events/dwd-alerts/recent", params={"severity": "severe"}).json()
    assert severe["count"] == 1
    assert severe["alerts"][0]["severity"] == "severe"

    frost = client.get("/api/events/dwd-alerts/recent", params={"event": "Frost"}).json()
    assert frost["count"] == 1
    assert "Frost" in frost["alerts"][0]["title"]

    sorted_payload = client.get("/api/events/dwd-alerts/recent", params={"sort": "severity"}).json()
    assert sorted_payload["alerts"][0]["severity"] == "severe"


def test_dwd_cap_preserves_optional_fields_and_event_codes() -> None:
    fixture = Path(__file__).resolve().parents[1] / "data" / "dwd_cap_directory_fixture.html"
    client = _client_with_fixture(fixture)

    payload = client.get("/api/events/dwd-alerts/recent", params={"event": "Frost"}).json()
    assert payload["count"] == 1
    alert = payload["alerts"][0]
    assert alert["instruction"] is None
    assert alert["web"] is None
    assert alert["eventCodes"]["II"] == "22"
    assert alert["areaDescription"] == "Landkreis Harz"


def test_dwd_cap_invalid_params_and_empty_case() -> None:
    fixture = Path(__file__).resolve().parents[1] / "data" / "dwd_cap_directory_fixture.html"
    client = _client_with_fixture(fixture)

    empty = client.get("/api/events/dwd-alerts/recent", params={"event": "Hagel"}).json()
    assert empty["count"] == 0
    assert empty["sourceHealth"]["health"] == "empty"

    bad_severity = client.get("/api/events/dwd-alerts/recent", params={"severity": "bad"})
    assert bad_severity.status_code == 400

    bad_sort = client.get("/api/events/dwd-alerts/recent", params={"sort": "bad"})
    assert bad_sort.status_code == 400


def test_dwd_cap_inert_text_and_disabled_mode() -> None:
    fixture = Path(__file__).resolve().parents[1] / "data" / "dwd_cap_directory_fixture.html"
    client = _client_with_fixture(fixture)
    payload = client.get("/api/events/dwd-alerts/recent").json()
    blob = " ".join(
        payload["caveats"]
        + [alert.get("instruction") or "" for alert in payload["alerts"]]
        + [alert.get("description") or "" for alert in payload["alerts"]]
        + [alert.get("title") or "" for alert in payload["alerts"]]
    )

    assert "<script" not in blob.lower()
    assert "workflow behavior" not in blob.lower()
    assert "action guidance" in " ".join(payload["caveats"]).lower()

    disabled_client = _client_with_disabled_mode()
    disabled_payload = disabled_client.get("/api/events/dwd-alerts/recent").json()
    assert disabled_payload["count"] == 0
    assert disabled_payload["sourceHealth"]["health"] == "disabled"
