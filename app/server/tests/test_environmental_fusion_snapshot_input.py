from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.config.settings import Settings, get_settings
from src.routes.environmental_context import router as environmental_context_router


def _fixture(name: str) -> str:
    return str(Path(__file__).resolve().parents[1] / "data" / name)


def _settings() -> Settings:
    return Settings(
        EARTHQUAKE_SOURCE_MODE="fixture",
        EARTHQUAKE_FIXTURE_PATH=_fixture("usgs_earthquakes_fixture.geojson"),
        EMSC_SEISMICPORTAL_SOURCE_MODE="fixture",
        EMSC_SEISMICPORTAL_FIXTURE_PATH=_fixture("emsc_seismicportal_realtime_fixture.json"),
        ORFEUS_EIDA_SOURCE_MODE="fixture",
        ORFEUS_EIDA_FIXTURE_PATH=_fixture("orfeus_eida_station_fixture.txt"),
        EONET_SOURCE_MODE="fixture",
        EONET_FIXTURE_PATH=_fixture("nasa_eonet_events_fixture.json"),
        VOLCANO_SOURCE_MODE="fixture",
        VOLCANO_FIXTURE_PATH=_fixture("usgs_volcano_status_fixture.json"),
        TSUNAMI_SOURCE_MODE="fixture",
        TSUNAMI_FIXTURE_PATH=_fixture("noaa_tsunami_alerts_fixture.json"),
        UK_EA_FLOOD_SOURCE_MODE="fixture",
        UK_EA_FLOOD_FIXTURE_PATH=_fixture("uk_ea_flood_monitoring_fixture.json"),
        GEONET_SOURCE_MODE="fixture",
        GEONET_FIXTURE_PATH=_fixture("geonet_hazards_fixture.json"),
        HKO_SOURCE_MODE="fixture",
        HKO_FIXTURE_PATH=_fixture("hko_weather_fixture.json"),
        METNO_METALERTS_SOURCE_MODE="fixture",
        METNO_METALERTS_FIXTURE_PATH=_fixture("metno_metalerts_fixture.json"),
        CANADA_CAP_SOURCE_MODE="fixture",
        CANADA_CAP_FIXTURE_PATH=_fixture("canada_cap_index_fixture.html"),
        DWD_CAP_SOURCE_MODE="fixture",
        DWD_CAP_FIXTURE_PATH=_fixture("dwd_cap_directory_fixture.html"),
        IPMA_SOURCE_MODE="fixture",
        IPMA_FIXTURE_PATH=_fixture("ipma_warnings_fixture.json"),
        MET_EIREANN_WARNINGS_SOURCE_MODE="fixture",
        MET_EIREANN_WARNINGS_FIXTURE_PATH=_fixture("met_eireann_warning_rss_fixture.xml"),
        MET_EIREANN_FORECAST_SOURCE_MODE="fixture",
        MET_EIREANN_FORECAST_FIXTURE_PATH=_fixture("met_eireann_forecast_fixture.xml"),
        GEOSPHERE_AUSTRIA_WARNINGS_SOURCE_MODE="fixture",
        GEOSPHERE_AUSTRIA_WARNINGS_FIXTURE_PATH=_fixture("geosphere_austria_warnings_fixture.json"),
        NATURAL_EARTH_PHYSICAL_SOURCE_MODE="fixture",
        NATURAL_EARTH_PHYSICAL_FIXTURE_PATH=_fixture("natural_earth_physical_land_fixture.json"),
        GSHHG_SHORELINES_SOURCE_MODE="fixture",
        GSHHG_SHORELINES_FIXTURE_PATH=_fixture("gshhg_shorelines_fixture.json"),
        PB2002_PLATE_BOUNDARIES_SOURCE_MODE="fixture",
        PB2002_PLATE_BOUNDARIES_FIXTURE_PATH=_fixture("pb2002_plate_boundaries_fixture.json"),
        NOAA_GLOBAL_VOLCANO_SOURCE_MODE="fixture",
        NOAA_GLOBAL_VOLCANO_FIXTURE_PATH=_fixture("noaa_global_volcano_locations_fixture.json"),
        TAIWAN_CWA_SOURCE_MODE="fixture",
        TAIWAN_CWA_FIXTURE_PATH=_fixture("taiwan_cwa_current_weather_fixture.json"),
        NRC_EVENT_NOTIFICATIONS_SOURCE_MODE="fixture",
        NRC_EVENT_NOTIFICATIONS_FIXTURE_PATH=_fixture("nrc_event_notifications_fixture.xml"),
        BMKG_EARTHQUAKES_SOURCE_MODE="fixture",
        BMKG_EARTHQUAKES_FIXTURE_PATH=_fixture("bmkg_earthquakes_fixture.json"),
        BC_WILDFIRE_DATAMART_SOURCE_MODE="fixture",
        BC_WILDFIRE_DATAMART_FIXTURE_PATH=_fixture("bc_wildfire_datamart_fixture.json"),
        METEOSWISS_OPEN_DATA_SOURCE_MODE="fixture",
        METEOSWISS_OPEN_DATA_FIXTURE_PATH=_fixture("meteoswiss_open_data_fixture.json"),
        CANADA_GEOMET_OGC_SOURCE_MODE="fixture",
        CANADA_GEOMET_OGC_FIXTURE_PATH=_fixture("canada_geomet_climate_stations_fixture.json"),
        GA_RECENT_EARTHQUAKES_SOURCE_MODE="fixture",
        GA_RECENT_EARTHQUAKES_FIXTURE_PATH=_fixture("ga_recent_earthquakes_fixture.kml"),
        DMI_FORECAST_SOURCE_MODE="fixture",
        DMI_FORECAST_FIXTURE_PATH=_fixture("dmi_forecast_fixture.json"),
        IRELAND_WFD_SOURCE_MODE="fixture",
        IRELAND_WFD_FIXTURE_PATH=_fixture("ireland_epa_wfd_catchments_fixture.json"),
        NASA_POWER_SOURCE_MODE="fixture",
        NASA_POWER_FIXTURE_PATH=_fixture("nasa_power_meteorology_solar_fixture.json"),
        FRANCE_GEORISQUES_SOURCE_MODE="fixture",
        FRANCE_GEORISQUES_FIXTURE_PATH=_fixture("france_georisques_fixture.json"),
        UK_EA_WATER_QUALITY_SOURCE_MODE="fixture",
        UK_EA_WATER_QUALITY_FIXTURE_PATH=_fixture("uk_ea_water_quality_fixture.json"),
        USGS_GEOMAGNETISM_SOURCE_MODE="fixture",
        USGS_GEOMAGNETISM_FIXTURE_PATH=_fixture("usgs_geomagnetism_fixture.json"),
        RGI_GLACIER_INVENTORY_SOURCE_MODE="fixture",
        RGI_GLACIER_INVENTORY_FIXTURE_PATH=_fixture("rgi_glacier_inventory_fixture.json"),
    )


def _client(settings_factory=_settings) -> TestClient:
    app = FastAPI()
    app.include_router(environmental_context_router)
    app.dependency_overrides[get_settings] = settings_factory
    return TestClient(app)


def test_environmental_fusion_snapshot_input_keeps_dynamic_and_static_context_separate() -> None:
    client = _client()

    payload = client.get("/api/context/environmental/fusion-snapshot-input").json()

    assert payload["metadata"]["source"] == "environmental-fusion-snapshot-input"
    assert payload["metadata"]["profile"] == "bounded-geospatial-domain-input"
    assert "base-earth-reference" not in payload["dynamicFamilyIds"]
    assert payload["dynamicEnvironmentalContext"]["metadata"]["profile"] == "source-health-review"
    assert "dwd-cap-alerts" in payload["dynamicSourceIds"]
    assert payload["canadaContext"]["metadata"]["source"] == "environmental-canada-context-export-package"
    assert payload["baseEarthReference"]["metadata"]["source"] == "environmental-base-earth-export-package"
    assert payload["glacierReference"]["sourceId"] == "rgi-glacier-inventory"
    assert payload["glacierReference"]["evidenceBasis"] == "reference"
    assert "rgi-glacier-inventory" in payload["staticReferenceSourceIds"]


def test_environmental_fusion_snapshot_input_reports_overlap_and_review_counts() -> None:
    client = _client()

    payload = client.get("/api/context/environmental/fusion-snapshot-input").json()

    assert "environment-canada-cap-alerts" in payload["overlapSourceIds"]
    assert "canada-geomet-ogc" in payload["overlapSourceIds"]
    expected_issue_count = (
        payload["dynamicEnvironmentalContext"]["issueCount"]
        + payload["canadaReview"]["issueCount"]
        + payload["baseEarthReview"]["issueCount"]
    )
    assert payload["reviewIssueCount"] == expected_issue_count
    assert payload["metadata"]["reviewIssueCount"] == expected_issue_count
    assert payload["metadata"]["totalSourceCount"] == len(payload["totalSourceIds"])


def test_environmental_fusion_snapshot_input_preserves_guardrails_and_no_flattened_hazard_claims() -> None:
    client = _client()

    payload = client.get("/api/context/environmental/fusion-snapshot-input").json()
    blob = " ".join(
        payload["reviewLines"]
        + payload["exportLines"]
        + payload["doesNotProveLines"]
        + payload["caveats"]
        + payload["dynamicEnvironmentalContext"]["reviewLines"]
        + payload["canadaContext"]["reviewLines"]
        + payload["baseEarthReference"]["reviewLines"]
        + payload["glacierReference"]["reviewLines"]
    )

    assert "live and advisory environmental context separately from static and snapshot reference context" in " ".join(payload["caveats"]).lower()
    assert "does not prove current glacier extent" in " ".join(payload["doesNotProveLines"]).lower()
    assert "hazard score" not in blob.lower()
    assert "damage score" not in blob.lower()
    assert "take action now" not in blob.lower()
    assert "<script" not in blob.lower()
