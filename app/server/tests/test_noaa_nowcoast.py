from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.config.settings import get_settings
from src.routes.weather_context import router as weather_context_router


def _client_with_fixture(fixture_path: Path) -> TestClient:
    app = FastAPI()
    app.include_router(weather_context_router)
    app.dependency_overrides[get_settings] = lambda: get_settings().model_copy(
        update={
            "noaa_nowcoast_source_mode": "fixture",
            "noaa_nowcoast_fixture_path": str(fixture_path),
        }
    )
    return TestClient(app)


def _client_with_disabled_mode() -> TestClient:
    app = FastAPI()
    app.include_router(weather_context_router)
    app.dependency_overrides[get_settings] = lambda: get_settings().model_copy(
        update={
            "noaa_nowcoast_source_mode": "disabled",
        }
    )
    return TestClient(app)


def test_noaa_nowcoast_fixture_parsing_and_provenance() -> None:
    fixture = Path(__file__).resolve().parents[1] / "data" / "noaa_nowcoast_layer_catalog_fixture.json"
    client = _client_with_fixture(fixture)

    payload = client.get("/api/context/weather/nowcoast/layer-catalog").json()
    assert payload["metadata"]["source"] == "noaa-nowcoast-ogc"
    assert payload["metadata"]["sourceMode"] == "fixture"
    assert payload["sourceHealth"]["health"] == "loaded"
    assert payload["count"] == 3
    assert payload["layers"][0]["layerGroup"] == "hazards"


def test_noaa_nowcoast_group_query_and_limit_filters() -> None:
    fixture = Path(__file__).resolve().parents[1] / "data" / "noaa_nowcoast_layer_catalog_fixture.json"
    client = _client_with_fixture(fixture)

    hazards = client.get("/api/context/weather/nowcoast/layer-catalog", params={"group": "hazards"}).json()
    assert hazards["count"] == 2
    assert all(layer["layerGroup"] == "hazards" for layer in hazards["layers"])

    imagery = client.get("/api/context/weather/nowcoast/layer-catalog", params={"q": "Radar"}).json()
    assert imagery["count"] == 1
    assert imagery["layers"][0]["layerId"] == "nowcoast-radar"

    limited = client.get("/api/context/weather/nowcoast/layer-catalog", params={"limit": 1}).json()
    assert limited["count"] == 1


def test_noaa_nowcoast_inert_text_empty_and_disabled_mode() -> None:
    fixture = Path(__file__).resolve().parents[1] / "data" / "noaa_nowcoast_layer_catalog_fixture.json"
    client = _client_with_fixture(fixture)

    payload = client.get("/api/context/weather/nowcoast/layer-catalog").json()
    blob = " ".join(
        payload["caveats"]
        + [layer.get("description") or "" for layer in payload["layers"]]
        + [layer.get("extentSummary") or "" for layer in payload["layers"]]
    )
    assert "<script" not in blob.lower()
    assert "workflow behavior" in blob.lower()

    empty = client.get("/api/context/weather/nowcoast/layer-catalog", params={"group": "observations"}).json()
    assert empty["count"] == 0
    assert empty["sourceHealth"]["health"] == "empty"

    disabled_client = _client_with_disabled_mode()
    disabled = disabled_client.get("/api/context/weather/nowcoast/layer-catalog").json()
    assert disabled["count"] == 0
    assert disabled["sourceHealth"]["health"] == "disabled"


def test_noaa_nowcoast_invalid_group_param() -> None:
    fixture = Path(__file__).resolve().parents[1] / "data" / "noaa_nowcoast_layer_catalog_fixture.json"
    client = _client_with_fixture(fixture)

    bad = client.get("/api/context/weather/nowcoast/layer-catalog", params={"group": "bad"})
    assert bad.status_code == 400
