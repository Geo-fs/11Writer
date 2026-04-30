from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from src.app import create_application
from src.config.settings import Settings, get_settings


def _settings() -> Settings:
    return Settings(
        FINLAND_DIGITRAFFIC_SOURCE_MODE="fixture",
        FINLAND_DIGITRAFFIC_WEATHER_STATIONS_FIXTURE_PATH=str(
            Path(__file__).resolve().parents[1] / "data" / "digitraffic_weather_stations_fixture.json"
        ),
        FINLAND_DIGITRAFFIC_WEATHER_STATION_DATA_FIXTURE_PATH=str(
            Path(__file__).resolve().parents[1] / "data" / "digitraffic_weather_station_data_fixture.json"
        ),
    )


def _client() -> TestClient:
    app = create_application()
    app.dependency_overrides[get_settings] = _settings
    return TestClient(app)


def test_finland_digitraffic_fixture_parsing_and_provenance() -> None:
    client = _client()

    payload = client.get("/api/features/finland-road-weather/stations").json()

    assert payload["metadata"]["source"] == "finland-digitraffic"
    assert payload["metadata"]["sourceMode"] == "fixture"
    assert payload["metadata"]["count"] == 2
    assert payload["metadata"]["measurementCount"] == 4
    assert payload["metadata"]["metadataFeedUrl"] == "https://tie.digitraffic.fi/api/weather/v1/stations"
    assert payload["metadata"]["dataFeedUrl"] == "https://tie.digitraffic.fi/api/weather/v1/stations/data"
    assert payload["count"] == 2
    assert payload["sourceHealth"]["metadataEndpoint"]["health"] == "loaded"
    assert payload["sourceHealth"]["metadataEndpoint"]["loadedCount"] == 2
    assert payload["sourceHealth"]["metadataEndpoint"]["freshnessState"] == "current"
    assert "Metadata endpoint is current enough" in payload["sourceHealth"]["metadataEndpoint"]["interpretation"]
    assert payload["sourceHealth"]["stationDataEndpoint"]["health"] == "loaded"
    assert payload["sourceHealth"]["stationDataEndpoint"]["loadedCount"] == 2
    assert payload["sourceHealth"]["stationDataEndpoint"]["freshnessState"] == "stale"
    assert "looks stale" in payload["sourceHealth"]["stationDataEndpoint"]["interpretation"]

    first = payload["stations"][0]
    assert first["stationId"] == "1001"
    assert first["stationName"] == "vt1_Espoo_Nupuri"
    assert first["roadNumber"] == 1
    assert first["municipality"] == "Espoo"
    assert first["state"] == "OK"
    assert first["collectionStatus"] == "GATHERING"
    assert first["sourceUrl"] == "https://tie.digitraffic.fi/api/weather/v1/stations"
    assert first["freshness"]["freshnessState"] == "stale"
    assert first["freshness"]["sparseCoverage"] is False
    assert "stale" in first["freshness"]["interpretation"].lower()
    assert len(first["observations"]) == 3
    assert first["observations"][0]["sourceUrl"] == "https://tie.digitraffic.fi/api/weather/v1/stations/data"
    assert first["observations"][0]["observedVsDerived"] == "observed"


def test_finland_digitraffic_station_and_sensor_filters_preserve_sparse_coverage() -> None:
    client = _client()

    station_only = client.get(
        "/api/features/finland-road-weather/stations",
        params={"station_ids": "1002"},
    ).json()
    assert station_only["count"] == 1
    assert station_only["stations"][0]["stationId"] == "1002"
    assert len(station_only["stations"][0]["observations"]) == 1

    sensor_only = client.get(
        "/api/features/finland-road-weather/stations",
        params={"sensor_ids": "16"},
    ).json()
    assert sensor_only["count"] == 1
    assert sensor_only["stations"][0]["stationId"] == "1001"
    assert [item["sensorId"] for item in sensor_only["stations"][0]["observations"]] == [16]


def test_finland_digitraffic_bbox_limit_and_nullable_state() -> None:
    client = _client()

    payload = client.get(
        "/api/features/finland-road-weather/stations",
        params={"bbox": "24.8,60.1,25.0,60.2", "limit": 1},
    ).json()

    assert payload["count"] == 1
    assert payload["stations"][0]["stationId"] == "1002"
    assert payload["stations"][0]["state"] is None
    assert payload["stations"][0]["roadNumber"] == 51
    assert payload["stations"][0]["municipality"] == "Helsinki"
    assert payload["stations"][0]["freshness"]["sparseCoverage"] is True


def test_finland_digitraffic_invalid_params_and_no_match() -> None:
    client = _client()

    empty = client.get(
        "/api/features/finland-road-weather/stations",
        params={"station_ids": "9999"},
    ).json()
    assert empty["count"] == 0
    assert empty["stations"] == []

    bad_bbox = client.get(
        "/api/features/finland-road-weather/stations",
        params={"bbox": "1,2,3"},
    )
    assert bad_bbox.status_code == 400

    bad_sensor_ids = client.get(
        "/api/features/finland-road-weather/stations",
        params={"sensor_ids": "bad"},
    )
    assert bad_sensor_ids.status_code == 400


def test_finland_digitraffic_station_detail_summary_and_grouping() -> None:
    client = _client()

    payload = client.get("/api/features/finland-road-weather/stations/1001").json()

    assert payload["metadata"]["source"] == "finland-digitraffic"
    assert payload["metadata"]["sourceMode"] == "fixture"
    assert payload["metadata"]["count"] == 1
    assert payload["metadata"]["measurementCount"] == 3
    assert payload["station"]["stationId"] == "1001"
    assert payload["station"]["stationName"] == "vt1_Espoo_Nupuri"
    assert payload["summary"]["observationCount"] == 3
    assert payload["summary"]["sensorsWithValues"] == 3
    assert payload["summary"]["latestObservedAt"] == "2026-04-30T19:04:53Z"
    assert payload["summary"]["sensorUnits"][:2] == ["%", "m/s"]
    assert len(payload["summary"]["sensorUnits"]) == 3
    assert payload["summary"]["sensorUnits"][2].endswith("C")
    assert {group["groupKey"] for group in payload["summary"]["sensorGroups"]} == {
        "humidity",
        "temperature",
        "wind",
    }
    wind_group = next(
        group for group in payload["summary"]["sensorGroups"] if group["groupKey"] == "wind"
    )
    assert wind_group["sensorCount"] == 1
    assert wind_group["sensorIds"] == [16]
    assert payload["station"]["freshness"]["freshnessState"] == "stale"
    assert payload["station"]["freshness"]["stationDataUpdatedAt"] == "2026-04-30T19:05:43Z"


def test_finland_digitraffic_station_detail_sparse_station_and_not_found() -> None:
    client = _client()

    sparse = client.get("/api/features/finland-road-weather/stations/1002").json()
    assert sparse["station"]["stationId"] == "1002"
    assert sparse["station"]["state"] is None
    assert sparse["station"]["freshness"]["sparseCoverage"] is True
    assert "sparse" in sparse["station"]["freshness"]["interpretation"].lower()
    assert sparse["summary"]["observationCount"] == 1
    assert sparse["summary"]["sensorGroups"][0]["groupKey"] == "temperature"

    missing = client.get("/api/features/finland-road-weather/stations/9999")
    assert missing.status_code == 404
