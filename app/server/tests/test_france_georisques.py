from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from src.app import create_application
from src.config.settings import Settings, get_settings


def _settings() -> Settings:
    return Settings(
        FRANCE_GEORISQUES_SOURCE_MODE="fixture",
        FRANCE_GEORISQUES_FIXTURE_PATH=str(
            Path(__file__).resolve().parents[1] / "data" / "france_georisques_fixture.json"
        ),
    )


def _client(settings_factory=_settings) -> TestClient:
    app = create_application()
    app.dependency_overrides[get_settings] = settings_factory
    return TestClient(app)


def test_france_georisques_code_insee_parsing_and_provenance() -> None:
    client = _client()

    response = client.get("/api/context/risk/france-georisques", params={"code_insee": "06088"})
    payload = response.json()

    assert response.status_code == 200
    assert payload["metadata"]["source"] == "france-georisques"
    assert payload["metadata"]["sourceMode"] == "fixture"
    assert payload["metadata"]["sourceUrl"] == "https://www.georisques.gouv.fr/api/v1/zonage_sismique"
    assert payload["metadata"]["requestUrl"] == "https://www.georisques.gouv.fr/api/v1/zonage_sismique?code_insee=06088"
    assert payload["metadata"]["requestBasis"] == "code_insee"
    assert payload["metadata"]["territoryId"] == "06088"
    assert payload["count"] == 1
    assert payload["sourceHealth"]["health"] == "loaded"
    assert payload["records"][0]["territoryName"] == "NICE"
    assert payload["records"][0]["riskLevelCode"] == "4"
    assert payload["records"][0]["riskLevelLabel"] == "4 - MOYENNE"
    assert "reference/context only" in payload["metadata"]["caveat"]


def test_france_georisques_latlon_and_empty_behavior() -> None:
    client = _client()

    loaded = client.get(
        "/api/context/risk/france-georisques",
        params={"latitude": 43.7102, "longitude": 7.2620},
    ).json()
    empty = client.get(
        "/api/context/risk/france-georisques",
        params={"code_insee": "75056"},
    ).json()

    assert loaded["metadata"]["requestBasis"] == "latlon"
    assert loaded["records"][0]["territoryId"] == "06088"
    assert empty["count"] == 0
    assert empty["sourceHealth"]["health"] == "empty"


def test_france_georisques_invalid_param_combinations_return_400() -> None:
    client = _client()

    missing = client.get("/api/context/risk/france-georisques")
    mixed = client.get(
        "/api/context/risk/france-georisques",
        params={"code_insee": "06088", "latitude": 43.7102, "longitude": 7.2620},
    )

    assert missing.status_code == 400
    assert mixed.status_code == 400
