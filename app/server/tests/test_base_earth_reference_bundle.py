from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.config.settings import Settings, get_settings
from src.routes.base_earth_context import router as base_earth_context_router


def _settings() -> Settings:
    base = Path(__file__).resolve().parents[1] / "data"
    return Settings(
        NATURAL_EARTH_PHYSICAL_SOURCE_MODE="fixture",
        NATURAL_EARTH_PHYSICAL_FIXTURE_PATH=str(base / "natural_earth_physical_land_fixture.json"),
        GSHHG_SHORELINES_SOURCE_MODE="fixture",
        GSHHG_SHORELINES_FIXTURE_PATH=str(base / "gshhg_shorelines_fixture.json"),
        PB2002_PLATE_BOUNDARIES_SOURCE_MODE="fixture",
        PB2002_PLATE_BOUNDARIES_FIXTURE_PATH=str(base / "pb2002_plate_boundaries_fixture.json"),
        NOAA_GLOBAL_VOLCANO_SOURCE_MODE="fixture",
        NOAA_GLOBAL_VOLCANO_FIXTURE_PATH=str(base / "noaa_global_volcano_locations_fixture.json"),
    )


def _natural_earth_empty_settings() -> Settings:
    base = Path(__file__).resolve().parents[1] / "data"
    return Settings(
        NATURAL_EARTH_PHYSICAL_SOURCE_MODE="fixture",
        NATURAL_EARTH_PHYSICAL_FIXTURE_PATH=str(base / "natural_earth_physical_land_empty_fixture.json"),
        GSHHG_SHORELINES_SOURCE_MODE="fixture",
        GSHHG_SHORELINES_FIXTURE_PATH=str(base / "gshhg_shorelines_fixture.json"),
        PB2002_PLATE_BOUNDARIES_SOURCE_MODE="fixture",
        PB2002_PLATE_BOUNDARIES_FIXTURE_PATH=str(base / "pb2002_plate_boundaries_fixture.json"),
        NOAA_GLOBAL_VOLCANO_SOURCE_MODE="fixture",
        NOAA_GLOBAL_VOLCANO_FIXTURE_PATH=str(base / "noaa_global_volcano_locations_fixture.json"),
    )


def _noaa_volcano_empty_settings() -> Settings:
    base = Path(__file__).resolve().parents[1] / "data"
    return Settings(
        NATURAL_EARTH_PHYSICAL_SOURCE_MODE="fixture",
        NATURAL_EARTH_PHYSICAL_FIXTURE_PATH=str(base / "natural_earth_physical_land_fixture.json"),
        GSHHG_SHORELINES_SOURCE_MODE="fixture",
        GSHHG_SHORELINES_FIXTURE_PATH=str(base / "gshhg_shorelines_fixture.json"),
        PB2002_PLATE_BOUNDARIES_SOURCE_MODE="fixture",
        PB2002_PLATE_BOUNDARIES_FIXTURE_PATH=str(base / "pb2002_plate_boundaries_fixture.json"),
        NOAA_GLOBAL_VOLCANO_SOURCE_MODE="fixture",
        NOAA_GLOBAL_VOLCANO_FIXTURE_PATH=str(base / "noaa_global_volcano_locations_empty_fixture.json"),
    )


def _gshhg_empty_settings() -> Settings:
    base = Path(__file__).resolve().parents[1] / "data"
    return Settings(
        NATURAL_EARTH_PHYSICAL_SOURCE_MODE="fixture",
        NATURAL_EARTH_PHYSICAL_FIXTURE_PATH=str(base / "natural_earth_physical_land_fixture.json"),
        GSHHG_SHORELINES_SOURCE_MODE="fixture",
        GSHHG_SHORELINES_FIXTURE_PATH=str(base / "gshhg_shorelines_empty_fixture.json"),
        PB2002_PLATE_BOUNDARIES_SOURCE_MODE="fixture",
        PB2002_PLATE_BOUNDARIES_FIXTURE_PATH=str(base / "pb2002_plate_boundaries_fixture.json"),
        NOAA_GLOBAL_VOLCANO_SOURCE_MODE="fixture",
        NOAA_GLOBAL_VOLCANO_FIXTURE_PATH=str(base / "noaa_global_volcano_locations_fixture.json"),
    )


def _pb2002_empty_settings() -> Settings:
    base = Path(__file__).resolve().parents[1] / "data"
    return Settings(
        NATURAL_EARTH_PHYSICAL_SOURCE_MODE="fixture",
        NATURAL_EARTH_PHYSICAL_FIXTURE_PATH=str(base / "natural_earth_physical_land_fixture.json"),
        GSHHG_SHORELINES_SOURCE_MODE="fixture",
        GSHHG_SHORELINES_FIXTURE_PATH=str(base / "gshhg_shorelines_fixture.json"),
        PB2002_PLATE_BOUNDARIES_SOURCE_MODE="fixture",
        PB2002_PLATE_BOUNDARIES_FIXTURE_PATH=str(base / "pb2002_plate_boundaries_empty_fixture.json"),
        NOAA_GLOBAL_VOLCANO_SOURCE_MODE="fixture",
        NOAA_GLOBAL_VOLCANO_FIXTURE_PATH=str(base / "noaa_global_volcano_locations_fixture.json"),
    )


def _client(settings_factory=_settings) -> TestClient:
    app = FastAPI()
    app.include_router(base_earth_context_router)
    app.dependency_overrides[get_settings] = settings_factory
    return TestClient(app)


def test_natural_earth_physical_fixture_parsing_and_provenance() -> None:
    client = _client()

    payload = client.get("/api/context/reference/natural-earth/physical/land").json()

    assert payload["metadata"]["source"] == "natural-earth-physical"
    assert payload["metadata"]["theme"] == "land"
    assert payload["metadata"]["scale"] == "110m"
    assert payload["metadata"]["sourceFile"] == "ne_110m_land.zip"
    assert payload["metadata"]["sourceUrl"] == "https://naturalearth.s3.amazonaws.com/110m_physical/ne_110m_land.zip"
    assert payload["metadata"]["sourceMode"] == "fixture"
    assert payload["metadata"]["licenseName"] == "Public Domain"
    assert payload["count"] == 3
    assert payload["sourceHealth"]["health"] == "loaded"
    assert payload["features"][0]["evidenceBasis"] == "reference"


def test_natural_earth_physical_bbox_filter_and_limit() -> None:
    client = _client()

    payload = client.get(
        "/api/context/reference/natural-earth/physical/land",
        params={"bbox": "-90,-60,-30,0", "limit": 1},
    ).json()

    assert payload["count"] == 1
    assert payload["features"][0]["recordId"] == "land-002"


def test_natural_earth_empty_fixture_reports_empty_health() -> None:
    empty_fixture = Path(__file__).resolve().parents[1] / "data" / "natural_earth_physical_land_empty_fixture.json"
    empty_fixture.write_text('{"metadata":{"theme":"land","scale":"110m","source_file":"ne_110m_land.zip"},"features":[]}', encoding="utf-8")
    try:
        client = _client(_natural_earth_empty_settings)
        payload = client.get("/api/context/reference/natural-earth/physical/land").json()
    finally:
        empty_fixture.unlink(missing_ok=True)

    assert payload["count"] == 0
    assert payload["sourceHealth"]["health"] == "empty"


def test_natural_earth_invalid_bbox_returns_400() -> None:
    client = _client()

    response = client.get("/api/context/reference/natural-earth/physical/land", params={"bbox": "1,2,3"})
    assert response.status_code == 400


def test_gshhg_fixture_parsing_and_provenance() -> None:
    client = _client()

    payload = client.get("/api/context/reference/gshhg/shorelines").json()

    assert payload["metadata"]["source"] == "gshhg-shorelines"
    assert payload["metadata"]["sourceName"] == "GSHHG Shorelines"
    assert payload["metadata"]["resolution"] == "intermediate"
    assert payload["metadata"]["sourceFile"] == "gshhg-intermediate-shorelines"
    assert payload["metadata"]["sourceUrl"] == "https://www.ngdc.noaa.gov/mgg/shorelines/shorelines.html"
    assert payload["metadata"]["sourceMode"] == "fixture"
    assert payload["metadata"]["licenseName"] == "LGPL"
    assert payload["count"] == 3
    assert payload["sourceHealth"]["health"] == "loaded"
    assert payload["features"][0]["evidenceBasis"] == "reference"


def test_gshhg_bbox_filter_and_limit() -> None:
    client = _client()

    payload = client.get(
        "/api/context/reference/gshhg/shorelines",
        params={"bbox": "115,-15,155,0", "limit": 1},
    ).json()

    assert payload["count"] == 1
    assert payload["features"][0]["recordId"] == "gshhg-002"


def test_gshhg_empty_fixture_reports_empty_health() -> None:
    empty_fixture = Path(__file__).resolve().parents[1] / "data" / "gshhg_shorelines_empty_fixture.json"
    empty_fixture.write_text('{"metadata":{"resolution":"intermediate","source_file":"gshhg-intermediate-shorelines"},"features":[]}', encoding="utf-8")
    try:
        client = _client(_gshhg_empty_settings)
        payload = client.get("/api/context/reference/gshhg/shorelines").json()
    finally:
        empty_fixture.unlink(missing_ok=True)

    assert payload["count"] == 0
    assert payload["sourceHealth"]["health"] == "empty"


def test_gshhg_invalid_bbox_returns_400() -> None:
    client = _client()

    response = client.get("/api/context/reference/gshhg/shorelines", params={"bbox": "1,2,3"})
    assert response.status_code == 400


def test_pb2002_fixture_parsing_and_provenance() -> None:
    client = _client()

    payload = client.get("/api/context/reference/pb2002/plate-boundaries").json()

    assert payload["metadata"]["source"] == "pb2002-plate-boundaries"
    assert payload["metadata"]["sourceName"] == "PB2002 Plate Boundaries"
    assert payload["metadata"]["modelName"] == "PB2002"
    assert payload["metadata"]["modelVintage"] == "2003"
    assert payload["metadata"]["sourceFile"] == "pb2002-boundaries"
    assert payload["metadata"]["sourceUrl"] == "https://peterbird.name/publications/2003_pb2002/2003_pb2002.htm"
    assert payload["metadata"]["sourceMode"] == "fixture"
    assert payload["count"] == 3
    assert payload["sourceHealth"]["health"] == "loaded"
    assert payload["boundaries"][0]["evidenceBasis"] == "reference"


def test_pb2002_boundary_type_bbox_filter_and_limit() -> None:
    client = _client()

    payload = client.get(
        "/api/context/reference/pb2002/plate-boundaries",
        params={"boundary_type": "transform", "bbox": "110,-15,165,0", "limit": 1},
    ).json()

    assert payload["count"] == 1
    assert payload["boundaries"][0]["recordId"] == "pb2002-003"


def test_pb2002_empty_fixture_reports_empty_health() -> None:
    empty_fixture = Path(__file__).resolve().parents[1] / "data" / "pb2002_plate_boundaries_empty_fixture.json"
    empty_fixture.write_text('{"metadata":{"model_name":"PB2002","model_vintage":"2003","source_file":"pb2002-boundaries"},"boundaries":[]}', encoding="utf-8")
    try:
        client = _client(_pb2002_empty_settings)
        payload = client.get("/api/context/reference/pb2002/plate-boundaries").json()
    finally:
        empty_fixture.unlink(missing_ok=True)

    assert payload["count"] == 0
    assert payload["sourceHealth"]["health"] == "empty"


def test_pb2002_invalid_bbox_returns_400() -> None:
    client = _client()

    response = client.get("/api/context/reference/pb2002/plate-boundaries", params={"bbox": "1,2,3"})
    assert response.status_code == 400


def test_noaa_global_volcano_fixture_parsing_and_provenance() -> None:
    client = _client()

    payload = client.get("/api/context/reference/noaa-global-volcanoes").json()

    assert payload["metadata"]["source"] == "noaa-global-volcano-locations"
    assert payload["metadata"]["sourceName"] == "NOAA Global Volcano Locations Database"
    assert payload["metadata"]["sourceUrl"] == "https://www.ngdc.noaa.gov/hazel/hazard-service/api/v1/volcanolocs"
    assert payload["metadata"]["requestUrl"] == "https://www.ngdc.noaa.gov/hazel/hazard-service/api/v1/volcanolocs?itemsPerPage=2000&page=1"
    assert payload["metadata"]["sourceMode"] == "fixture"
    assert payload["count"] == 3
    assert payload["sourceHealth"]["health"] == "loaded"
    assert payload["volcanoes"][0]["volcanoName"] == "Crater Lake"
    assert payload["volcanoes"][0]["elevationM"] is None


def test_noaa_global_volcano_country_filter_limit_and_sort() -> None:
    client = _client()

    payload = client.get(
        "/api/context/reference/noaa-global-volcanoes",
        params={"country": "Italy", "limit": 1, "sort": "elevation"},
    ).json()

    assert payload["count"] == 1
    assert payload["volcanoes"][0]["volcanoName"] == "Vesuvius"


def test_noaa_global_volcano_query_matches_reference_text() -> None:
    client = _client()

    payload = client.get(
        "/api/context/reference/noaa-global-volcanoes",
        params={"q": "Historical"},
    ).json()

    assert payload["count"] == 2
    assert all(item["holoceneStatus"] == "Historical" for item in payload["volcanoes"])


def test_noaa_global_volcano_empty_fixture_reports_empty_health() -> None:
    empty_fixture = Path(__file__).resolve().parents[1] / "data" / "noaa_global_volcano_locations_empty_fixture.json"
    empty_fixture.write_text('{"items":[],"page":1,"totalPages":0,"itemsPerPage":0,"totalItems":0}', encoding="utf-8")
    try:
        client = _client(_noaa_volcano_empty_settings)
        payload = client.get("/api/context/reference/noaa-global-volcanoes").json()
    finally:
        empty_fixture.unlink(missing_ok=True)

    assert payload["count"] == 0
    assert payload["sourceHealth"]["health"] == "empty"


def test_noaa_global_volcano_invalid_sort_returns_400() -> None:
    client = _client()

    response = client.get("/api/context/reference/noaa-global-volcanoes", params={"sort": "bad"})
    assert response.status_code == 400
