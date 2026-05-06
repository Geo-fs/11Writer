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
            "meteoalarm_atom_source_mode": "fixture",
            "meteoalarm_atom_fixture_path": str(fixture_path),
        }
    )
    return TestClient(app)


def _client_with_disabled_mode() -> TestClient:
    app = FastAPI()
    app.include_router(events_router)
    app.dependency_overrides[get_settings] = lambda: get_settings().model_copy(
        update={"meteoalarm_atom_source_mode": "disabled"}
    )
    return TestClient(app)


def test_meteoalarm_atom_fixture_parsing_and_provenance() -> None:
    fixture = Path(__file__).resolve().parents[1] / "data" / "meteoalarm_atom_norway_fixture.xml"
    client = _client_with_fixture(fixture)

    payload = client.get("/api/events/meteoalarm/country-warnings").json()

    assert payload["metadata"]["source"] == "meteoalarm-atom-feeds"
    assert payload["metadata"]["sourceMode"] == "fixture"
    assert payload["metadata"]["country"] == "Norway"
    assert payload["sourceHealth"]["health"] == "loaded"
    assert payload["count"] == 2
    assert payload["warnings"][0]["entryId"] == "meteoalarm-norway-001"
    assert payload["warnings"][0]["country"] == "Norway"
    assert payload["warnings"][0]["areaLabel"] == "Troms"


def test_meteoalarm_atom_query_filters_limit_and_sort() -> None:
    fixture = Path(__file__).resolve().parents[1] / "data" / "meteoalarm_atom_norway_fixture.xml"
    client = _client_with_fixture(fixture)

    filtered = client.get("/api/events/meteoalarm/country-warnings", params={"q": "wind"}).json()
    assert filtered["count"] == 1
    assert "wind" in filtered["warnings"][0]["title"].lower()

    limited = client.get("/api/events/meteoalarm/country-warnings", params={"limit": 1}).json()
    assert limited["count"] == 1

    sorted_payload = client.get("/api/events/meteoalarm/country-warnings", params={"sort": "title"}).json()
    titles = [item["title"] for item in sorted_payload["warnings"]]
    assert titles == sorted(titles)


def test_meteoalarm_atom_inert_text_empty_and_disabled_behaviour() -> None:
    fixture = Path(__file__).resolve().parents[1] / "data" / "meteoalarm_atom_norway_fixture.xml"
    client = _client_with_fixture(fixture)
    payload = client.get("/api/events/meteoalarm/country-warnings").json()
    blob = " ".join(
        payload["caveats"]
        + [warning.get("summary") or "" for warning in payload["warnings"]]
        + [warning.get("title") or "" for warning in payload["warnings"]]
    )

    assert "<script" not in blob.lower()
    assert "mark this source validated" in blob.lower()
    assert "workflow behavior" in " ".join(payload["caveats"]).lower()

    empty_fixture = Path(__file__).resolve().parents[1] / "data" / "meteoalarm_atom_norway_empty_fixture.xml"
    empty_client = _client_with_fixture(empty_fixture)
    empty_payload = empty_client.get("/api/events/meteoalarm/country-warnings").json()
    assert empty_payload["count"] == 0
    assert empty_payload["sourceHealth"]["health"] == "empty"

    disabled_client = _client_with_disabled_mode()
    disabled_payload = disabled_client.get("/api/events/meteoalarm/country-warnings").json()
    assert disabled_payload["count"] == 0
    assert disabled_payload["sourceHealth"]["health"] == "disabled"


def test_meteoalarm_atom_invalid_sort() -> None:
    fixture = Path(__file__).resolve().parents[1] / "data" / "meteoalarm_atom_norway_fixture.xml"
    client = _client_with_fixture(fixture)

    response = client.get("/api/events/meteoalarm/country-warnings", params={"sort": "bad"})
    assert response.status_code == 400
