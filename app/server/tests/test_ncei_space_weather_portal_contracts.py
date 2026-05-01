from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.adapters.ncei_space_weather_portal import (
    NceiSpaceWeatherPortalAdapter,
    NceiSpaceWeatherPortalFetchResult,
)
from src.config.settings import Settings, get_settings
from src.routes.ncei_space_weather_portal import router as ncei_space_weather_portal_router
from src.routes.status import router as status_router
from src.services.ncei_space_weather_portal_service import NceiSpaceWeatherPortalService
from src.services.source_registry import record_source_failure, reset_source_registry


def _client() -> TestClient:
    NceiSpaceWeatherPortalService._cache_by_ttl = {}
    reset_source_registry()
    get_settings.cache_clear()
    application = FastAPI()
    application.include_router(ncei_space_weather_portal_router)
    application.include_router(status_router)
    return TestClient(application)


def test_ncei_space_weather_portal_fixture_serialization() -> None:
    client = _client()
    response = client.get("/api/aerospace/space/ncei-space-weather-archive")
    assert response.status_code == 200
    payload = response.json()
    assert payload["source"] == "noaa-ncei-space-weather-portal"
    assert payload["count"] == 1
    assert payload["records"][0]["collectionId"] == "gov.noaa.ngdc.stp.swx:space_weather_products"
    assert payload["records"][0]["datasetIdentifier"] == "solarFeatures"
    assert payload["records"][0]["sourceMode"] == "fixture"
    assert payload["records"][0]["evidenceBasis"] == "archival"
    assert payload["sourceHealth"]["sourceMode"] == "fixture"
    assert "archival" in " ".join(payload["caveats"]).lower()
    assert "swpc" in " ".join(payload["caveats"]).lower()


def test_ncei_space_weather_portal_empty_result_is_explicit(monkeypatch) -> None:
    async def fake_load_payload(self):
        return NceiSpaceWeatherPortalFetchResult(
            records=[],
            source_mode="fixture",
            metadata_source_url="fixture.xml",
            landing_page_url="https://www.ncei.noaa.gov/access/metadata/landing-page/bin/iso?id=fixture",
            last_updated_at=None,
            caveats=[
                "NOAA NCEI space-weather portal metadata is archival/contextual collection metadata, not current operational SWPC alerting.",
            ],
        )

    monkeypatch.setattr(
        "src.services.ncei_space_weather_portal_service.NceiSpaceWeatherPortalService._load_payload",
        fake_load_payload,
    )

    client = _client()
    response = client.get("/api/aerospace/space/ncei-space-weather-archive")
    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] == 0
    assert payload["records"] == []
    assert payload["sourceHealth"]["sourceMode"] == "fixture"
    assert "archival" in " ".join(payload["caveats"]).lower()


def test_ncei_space_weather_portal_status_reports_degraded_runtime() -> None:
    client = _client()
    record_source_failure(
        "noaa-ncei-space-weather-portal",
        degraded_reason="NOAA NCEI space-weather portal metadata returned HTTP 503.",
        freshness_seconds=86400,
        stale_after_seconds=604800,
    )
    response = client.get("/api/status/sources")
    assert response.status_code == 200
    payload = response.json()
    status = next(source for source in payload["sources"] if source["name"] == "noaa-ncei-space-weather-portal")
    assert status["state"] == "degraded"
    assert status["freshnessSeconds"] == 86400


def test_ncei_space_weather_portal_sanitizes_untrusted_free_text() -> None:
    adapter = NceiSpaceWeatherPortalAdapter(Settings())
    payload = adapter.parse_xml(
        """<?xml version="1.0" encoding="UTF-8"?>
        <gmi:MI_Metadata xmlns:gmi="http://www.isotc211.org/2005/gmi" xmlns:gco="http://www.isotc211.org/2005/gco" xmlns:gmd="http://www.isotc211.org/2005/gmd">
          <gmd:fileIdentifier><gco:CharacterString>fixture-collection</gco:CharacterString></gmd:fileIdentifier>
          <gmd:dateStamp><gco:Date>2016-01-01</gco:Date></gmd:dateStamp>
          <gmd:identificationInfo>
            <gmd:MD_DataIdentification>
              <gmd:citation>
                <gmd:CI_Citation>
                  <gmd:title><gco:CharacterString>Archive &lt;script&gt;alert(1)&lt;/script&gt; Title</gco:CharacterString></gmd:title>
                  <gmd:identifier><gco:CharacterString>fixture-id</gco:CharacterString></gmd:identifier>
                </gmd:CI_Citation>
              </gmd:citation>
              <gmd:abstract>
                <gco:CharacterString>Historical metadata &lt;img src=x onerror=alert(1)&gt; summary.</gco:CharacterString>
              </gmd:abstract>
            </gmd:MD_DataIdentification>
          </gmd:identificationInfo>
        </gmi:MI_Metadata>""",
        source_mode="fixture",
        metadata_source_url="fixture.xml",
    )
    record = payload.records[0]
    assert "<script>" not in record.title.lower()
    assert "<img" not in (record.summary or "").lower()
    assert "alert(1)" in record.title


def test_ncei_space_weather_portal_handles_missing_optional_fields() -> None:
    adapter = NceiSpaceWeatherPortalAdapter(Settings())
    payload = adapter.parse_xml(
        """<?xml version="1.0" encoding="UTF-8"?>
        <gmi:MI_Metadata xmlns:gmi="http://www.isotc211.org/2005/gmi" xmlns:gco="http://www.isotc211.org/2005/gco" xmlns:gmd="http://www.isotc211.org/2005/gmd">
          <gmd:fileIdentifier><gco:CharacterString>fixture-collection</gco:CharacterString></gmd:fileIdentifier>
          <gmd:identificationInfo>
            <gmd:MD_DataIdentification>
              <gmd:citation>
                <gmd:CI_Citation>
                  <gmd:title><gco:CharacterString>Archive Title</gco:CharacterString></gmd:title>
                </gmd:CI_Citation>
              </gmd:citation>
            </gmd:MD_DataIdentification>
          </gmd:identificationInfo>
        </gmi:MI_Metadata>""",
        source_mode="fixture",
        metadata_source_url="fixture.xml",
    )
    record = payload.records[0]
    assert record.dataset_identifier is None
    assert record.summary is None
    assert record.temporal_start is None
    assert record.temporal_end is None
