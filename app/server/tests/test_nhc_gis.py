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
            "nhc_gis_source_mode": "fixture",
            "nhc_gis_fixture_path": str(fixture_path),
        }
    )
    return TestClient(app)


def _client_with_disabled_mode() -> TestClient:
    app = FastAPI()
    app.include_router(events_router)
    app.dependency_overrides[get_settings] = lambda: get_settings().model_copy(
        update={
            "nhc_gis_source_mode": "disabled",
        }
    )
    return TestClient(app)


def test_nhc_gis_fixture_parsing_and_provenance() -> None:
    fixture = Path(__file__).resolve().parents[1] / "data" / "nhc_gis_atlantic_fixture.xml"
    client = _client_with_fixture(fixture)

    payload = client.get("/api/events/nhc-gis/recent").json()
    assert payload["metadata"]["source"] == "noaa-nhc-gis-atlantic"
    assert payload["metadata"]["sourceMode"] == "fixture"
    assert payload["metadata"]["basin"] == "atlantic"
    assert payload["metadata"]["experimentalFeed"] is True
    assert payload["sourceHealth"]["health"] == "loaded"
    assert payload["count"] == 4
    assert payload["advisories"][0]["basin"] == "atlantic"


def test_nhc_gis_filters_sorting_and_geometry_handling() -> None:
    fixture = Path(__file__).resolve().parents[1] / "data" / "nhc_gis_atlantic_fixture.xml"
    client = _client_with_fixture(fixture)

    summary = client.get("/api/events/nhc-gis/recent", params={"product_type": "summary"}).json()
    assert summary["count"] == 1
    assert summary["advisories"][0]["productType"] == "summary"
    assert summary["advisories"][0]["latitude"] is not None
    assert summary["advisories"][0]["longitude"] is not None

    beta = client.get("/api/events/nhc-gis/recent", params={"storm_name": "beta"}).json()
    assert beta["count"] == 1
    assert beta["advisories"][0]["stormName"] == "BETA"
    assert beta["advisories"][0]["latitude"] is None
    assert beta["advisories"][0]["longitude"] is None

    product_sorted = client.get("/api/events/nhc-gis/recent", params={"sort": "product_type"}).json()
    assert product_sorted["advisories"][0]["productType"] == "atcf-xml"


def test_nhc_gis_inert_text_empty_disabled_and_invalid_params() -> None:
    fixture = Path(__file__).resolve().parents[1] / "data" / "nhc_gis_atlantic_fixture.xml"
    client = _client_with_fixture(fixture)

    payload = client.get("/api/events/nhc-gis/recent").json()
    blob = " ".join(
        payload["caveats"]
        + [item.get("description") or "" for item in payload["advisories"]]
        + [item.get("headline") or "" for item in payload["advisories"]]
    )
    assert "<script" not in blob.lower()
    assert "workflow behavior" in blob.lower()

    empty = client.get("/api/events/nhc-gis/recent", params={"storm_name": "gamma"}).json()
    assert empty["count"] == 0
    assert empty["sourceHealth"]["health"] == "empty"

    bad_type = client.get("/api/events/nhc-gis/recent", params={"product_type": "bad"})
    assert bad_type.status_code == 400

    bad_sort = client.get("/api/events/nhc-gis/recent", params={"sort": "bad"})
    assert bad_sort.status_code == 400

    disabled_client = _client_with_disabled_mode()
    disabled = disabled_client.get("/api/events/nhc-gis/recent").json()
    assert disabled["count"] == 0
    assert disabled["sourceHealth"]["health"] == "disabled"
