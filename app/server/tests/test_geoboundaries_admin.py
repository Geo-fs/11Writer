from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.config.settings import Settings, get_settings
from src.routes.base_earth_context import router as base_earth_context_router


def _fixture(name: str) -> str:
    return str(Path(__file__).resolve().parents[1] / "data" / name)


def _settings() -> Settings:
    return Settings(
        GEOBOUNDARIES_ADMIN_SOURCE_MODE="fixture",
        GEOBOUNDARIES_ADMIN_FIXTURE_PATH=_fixture("geoboundaries_admin_bel_adm1_fixture.json"),
    )


def _client(settings_factory=_settings) -> TestClient:
    app = FastAPI()
    app.include_router(base_earth_context_router)
    app.dependency_overrides[get_settings] = settings_factory
    return TestClient(app)


def test_geoboundaries_fixture_parsing_and_provenance() -> None:
    client = _client()

    payload = client.get("/api/context/reference/geoboundaries-admin").json()

    assert payload["metadata"]["source"] == "geoboundaries-admin"
    assert payload["metadata"]["requestUrl"] == "https://www.geoboundaries.org/api/current/gbOpen/BEL/ADM1/"
    assert payload["metadata"]["releaseType"] == "gbOpen"
    assert payload["metadata"]["countryIso"] == "BEL"
    assert payload["metadata"]["adminLevel"] == "ADM1"
    assert payload["metadata"]["boundaryCanonical"] == "Region"
    assert payload["metadata"]["boundaryLicense"] == "Creative Commons Attribution 4.0 (CC BY 4.0)"
    assert payload["metadata"]["sourceMode"] == "fixture"
    assert payload["count"] == 3
    assert payload["sourceHealth"]["health"] == "loaded"
    assert payload["records"][0]["evidenceBasis"] == "reference"


def test_geoboundaries_shape_iso_bbox_filter_and_limit() -> None:
    client = _client()

    shape_iso_payload = client.get(
        "/api/context/reference/geoboundaries-admin",
        params={"shape_iso": "VLG"},
    ).json()
    assert shape_iso_payload["count"] == 1
    assert shape_iso_payload["records"][0]["shapeIso"] == "VLG"

    bbox_payload = client.get(
        "/api/context/reference/geoboundaries-admin",
        params={"bbox": "4.2,50.7,4.5,50.95", "limit": 1},
    ).json()
    assert bbox_payload["count"] == 1
    assert bbox_payload["records"][0]["shapeIso"] == "BRU"


def test_geoboundaries_empty_fixture_invalid_bbox_and_inert_text(tmp_path: Path) -> None:
    empty_fixture = tmp_path / "geoboundaries_empty_fixture.json"
    empty_fixture.write_text('{"metadata":{"boundaryISO":"BEL","boundaryType":"ADM1","buildDate":"Dec 12, 2023"},"records":[]}', encoding="utf-8")

    def empty_settings() -> Settings:
        return Settings(
            GEOBOUNDARIES_ADMIN_SOURCE_MODE="fixture",
            GEOBOUNDARIES_ADMIN_FIXTURE_PATH=str(empty_fixture),
        )

    client = _client(empty_settings)
    payload = client.get("/api/context/reference/geoboundaries-admin").json()

    assert payload["count"] == 0
    assert payload["sourceHealth"]["health"] == "empty"

    response = client.get("/api/context/reference/geoboundaries-admin", params={"bbox": "1,2,3"})
    assert response.status_code == 400

    injected_fixture = tmp_path / "geoboundaries_injected_fixture.json"
    injected_fixture.write_text(
        """
        {
          "metadata": {
            "boundaryID": "BEL-ADM1-27649430",
            "boundaryName": "Belgium",
            "boundaryISO": "BEL",
            "boundaryType": "ADM1",
            "boundaryCanonical": "Region",
            "boundaryLicense": "Creative Commons Attribution 4.0 (CC BY 4.0)",
            "buildDate": "Dec 12, 2023"
          },
          "records": [
            {
              "record_id": "shape-001",
              "shape_name": "Brussels <script>alert(1)</script>",
              "shape_iso": "BRU",
              "shape_group": "BEL",
              "shape_type": "ADM1",
              "geometry_type": "Polygon",
              "center_longitude": 4.384081,
              "center_latitude": 50.829348,
              "bbox_min_lon": 4.283083,
              "bbox_min_lat": 50.759743,
              "bbox_max_lon": 4.485079,
              "bbox_max_lat": 50.898953,
              "source_url": "https://example.invalid/fixture.geojson"
            }
          ]
        }
        """.strip(),
        encoding="utf-8",
    )

    def injected_settings() -> Settings:
        return Settings(
            GEOBOUNDARIES_ADMIN_SOURCE_MODE="fixture",
            GEOBOUNDARIES_ADMIN_FIXTURE_PATH=str(injected_fixture),
        )

    injected_payload = _client(injected_settings).get("/api/context/reference/geoboundaries-admin").json()
    blob = " ".join(
        injected_payload["caveats"]
        + [record.get("shapeName") or "" for record in injected_payload["records"]]
    )

    assert "<script" not in blob.lower()
    assert "legal-jurisdiction truth" in " ".join(injected_payload["caveats"]).lower()
