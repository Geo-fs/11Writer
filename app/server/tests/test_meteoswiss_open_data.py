from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.config.settings import Settings, get_settings
from src.routes.weather_context import router as weather_context_router


def _fixture_path(name: str) -> str:
    return str(Path(__file__).resolve().parents[1] / "data" / name)


def _settings() -> Settings:
    return Settings(
        METEOSWISS_OPEN_DATA_SOURCE_MODE="fixture",
        METEOSWISS_OPEN_DATA_FIXTURE_PATH=_fixture_path("meteoswiss_open_data_fixture.json"),
    )


def _empty_settings() -> Settings:
    return Settings(
        METEOSWISS_OPEN_DATA_SOURCE_MODE="fixture",
        METEOSWISS_OPEN_DATA_FIXTURE_PATH=_fixture_path("meteoswiss_open_data_empty_fixture.json"),
    )


def _client(settings_factory=_settings) -> TestClient:
    app = FastAPI()
    app.include_router(weather_context_router)
    app.dependency_overrides[get_settings] = settings_factory
    return TestClient(app)


def test_meteoswiss_fixture_parsing_provenance_and_metadata() -> None:
    client = _client()

    payload = client.get("/api/context/weather/meteoswiss").json()

    assert payload["metadata"]["source"] == "meteoswiss-open-data"
    assert payload["metadata"]["collectionId"] == "ch.meteoschweiz.ogd-smn"
    assert payload["metadata"]["assetFamily"] == "t_now"
    assert payload["metadata"]["sourceMode"] == "fixture"
    assert payload["count"] == 3
    assert payload["sourceHealth"]["health"] == "loaded"
    assert payload["stations"][0]["evidenceBasis"] == "observed"


def test_meteoswiss_filters_and_limit_behavior() -> None:
    client = _client()

    payload = client.get(
        "/api/context/weather/meteoswiss",
        params={"canton": "TI", "limit": 1},
    ).json()

    assert payload["count"] == 1
    assert payload["stations"][0]["stationAbbr"] == "LUG"
    assert payload["stations"][0]["stationCanton"] == "TI"


def test_meteoswiss_empty_no_match_behavior() -> None:
    client = _client()

    payload = client.get(
        "/api/context/weather/meteoswiss",
        params={"station_abbr": "XXX"},
    ).json()

    assert payload["count"] == 0
    assert payload["stations"] == []
    assert payload["sourceHealth"]["health"] == "empty"


def test_meteoswiss_prompt_injection_inertness_and_no_fake_coordinates() -> None:
    client = _client()

    payload = client.get("/api/context/weather/meteoswiss").json()
    lug = next(item for item in payload["stations"] if item["stationAbbr"] == "LUG")
    zer = next(item for item in payload["stations"] if item["stationAbbr"] == "ZER")
    blob = " ".join(payload["caveats"] + [item["stationName"] for item in payload["stations"]])

    assert "<script" not in blob.lower()
    assert "workflow behavior" in " ".join(payload["caveats"]).lower()
    assert lug["stationName"] == "Lugano"
    assert zer["latitude"] is None
    assert zer["longitude"] is None


def test_meteoswiss_empty_fixture_state() -> None:
    fixture_path = Path(_fixture_path("meteoswiss_open_data_empty_fixture.json"))
    fixture_path.write_text(
        json.dumps(
            {
                "collection": {
                    "id": "ch.meteoschweiz.ogd-smn",
                    "updated": "2026-05-02T13:33:58.048729Z",
                    "assets": {
                        "ogd-smn_meta_stations.csv": {
                            "href": "https://data.geo.admin.ch/ch.meteoschweiz.ogd-smn/ogd-smn_meta_stations.csv"
                        }
                    },
                },
                "station_meta_csv": "station_abbr;station_name;station_canton;station_wigos_id;station_type_en;station_dataowner;station_data_since;station_height_masl;station_height_barometer_masl;station_coordinates_lv95_east;station_coordinates_lv95_north;station_coordinates_wgs84_lat;station_coordinates_wgs84_lon;station_exposition_en;station_url_en\n",
                "observation_assets": [],
            }
        ),
        encoding="utf-8",
    )
    try:
        client = _client(_empty_settings)
        payload = client.get("/api/context/weather/meteoswiss").json()
        assert payload["count"] == 0
        assert payload["sourceHealth"]["health"] == "empty"
    finally:
        fixture_path.unlink(missing_ok=True)
