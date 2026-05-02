from __future__ import annotations

import os
from pathlib import Path

from fastapi.testclient import TestClient

from src.app import create_application
from src.config.settings import get_settings


def _client(fixture_path: Path) -> TestClient:
    os.environ["APP_ENV"] = "test"
    os.environ["ORFEUS_EIDA_SOURCE_MODE"] = "fixture"
    os.environ["ORFEUS_EIDA_FIXTURE_PATH"] = str(fixture_path)
    os.environ["WEBCAM_WORKER_ENABLED"] = "false"
    os.environ["WEBCAM_WORKER_RUN_ON_STARTUP"] = "false"
    get_settings.cache_clear()
    return TestClient(create_application())


def test_orfeus_fixture_parsing_and_provenance() -> None:
    fixture = Path(__file__).resolve().parents[1] / "data" / "orfeus_eida_station_fixture.txt"
    client = _client(fixture)

    response = client.get("/api/context/seismic/orfeus-eida")
    payload = response.json()

    assert response.status_code == 200
    assert payload["count"] == 3
    assert payload["metadata"]["source"] == "orfeus-eida-federator"
    assert payload["metadata"]["stationUrl"] == "https://federator.orfeus-eu.org/fdsnws/station/1/"
    assert payload["metadata"]["documentationUrl"] == "https://www.orfeus-eu.org/data/eida/nodes/FEDERATOR/"
    assert payload["metadata"]["sourceMode"] == "fixture"
    assert payload["sourceHealth"]["health"] == "loaded"
    assert payload["stations"][0]["evidenceBasis"] == "reference"


def test_orfeus_filters_limit_and_bbox() -> None:
    fixture = Path(__file__).resolve().parents[1] / "data" / "orfeus_eida_station_fixture.txt"
    client = _client(fixture)

    payload = client.get(
        "/api/context/seismic/orfeus-eida",
        params={"network": "IV", "bbox": "13,40,15,42", "limit": 1},
    ).json()

    assert payload["count"] == 1
    assert payload["stations"][0]["externalId"] == "IV.ACER"


def test_orfeus_no_match_and_empty_health() -> None:
    fixture = Path(__file__).resolve().parents[1] / "data" / "orfeus_eida_station_fixture.txt"
    client = _client(fixture)

    payload = client.get(
        "/api/context/seismic/orfeus-eida",
        params={"station": "ZZZZ"},
    ).json()

    assert payload["count"] == 0
    assert payload["stations"] == []
    assert payload["sourceHealth"]["health"] == "empty"


def test_orfeus_sanitizes_free_text_and_preserves_inertness() -> None:
    fixture = Path(__file__).resolve().parents[1] / "data" / "orfeus_eida_station_fixture.txt"
    client = _client(fixture)

    payload = client.get("/api/context/seismic/orfeus-eida").json()
    export_blob = " ".join(payload["caveats"] + [item.get("siteName") or "" for item in payload["stations"]])

    assert "<script" not in export_blob.lower()
    assert "workflow behavior" in " ".join(payload["caveats"]).lower()
    assert "hazard" in payload["metadata"]["caveat"].lower()


def test_orfeus_invalid_bbox_returns_400() -> None:
    fixture = Path(__file__).resolve().parents[1] / "data" / "orfeus_eida_station_fixture.txt"
    client = _client(fixture)

    response = client.get("/api/context/seismic/orfeus-eida", params={"bbox": "1,2,3"})
    assert response.status_code == 400
