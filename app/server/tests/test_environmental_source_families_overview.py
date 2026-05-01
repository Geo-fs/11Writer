from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from src.app import create_application
from src.config.settings import Settings, get_settings


def _fixture(name: str) -> str:
    return str(Path(__file__).resolve().parents[1] / "data" / name)


def _settings() -> Settings:
    return Settings(
        EARTHQUAKE_SOURCE_MODE="fixture",
        EARTHQUAKE_FIXTURE_PATH=_fixture("usgs_earthquakes_fixture.geojson"),
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
        NOAA_GLOBAL_VOLCANO_SOURCE_MODE="fixture",
        NOAA_GLOBAL_VOLCANO_FIXTURE_PATH=_fixture("noaa_global_volcano_locations_fixture.json"),
        TAIWAN_CWA_SOURCE_MODE="fixture",
        TAIWAN_CWA_FIXTURE_PATH=_fixture("taiwan_cwa_current_weather_fixture.json"),
        NRC_EVENT_NOTIFICATIONS_SOURCE_MODE="fixture",
        NRC_EVENT_NOTIFICATIONS_FIXTURE_PATH=_fixture("nrc_event_notifications_fixture.xml"),
        BMKG_EARTHQUAKES_SOURCE_MODE="fixture",
        BMKG_EARTHQUAKES_FIXTURE_PATH=_fixture("bmkg_earthquakes_fixture.json"),
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
    )


def _client(settings_factory=_settings) -> TestClient:
    app = create_application()
    app.dependency_overrides[get_settings] = settings_factory
    return TestClient(app)


def test_environmental_source_families_overview_shape_and_family_grouping() -> None:
    client = _client()

    response = client.get("/api/context/environmental/source-families-overview")
    payload = response.json()

    assert response.status_code == 200
    assert payload["metadata"]["source"] == "environmental-source-family-overview"
    assert payload["metadata"]["sourceMode"] == "fixture"
    assert payload["familyCount"] >= 10
    assert payload["sourceCount"] >= 26
    family_ids = [family["familyId"] for family in payload["families"]]
    assert "seismic" in family_ids
    assert "environmental-event-context" in family_ids
    assert "volcano-reference" in family_ids
    assert "weather-alert-advisory" in family_ids
    assert "weather-flood-hydrology" in family_ids
    assert "infrastructure-event-context" in family_ids
    seismic = next(family for family in payload["families"] if family["familyId"] == "seismic")
    assert "usgs-earthquake-hazards-program" in seismic["sourceIds"]
    assert "bmkg-earthquakes" in seismic["sourceIds"]
    assert "ga-recent-earthquakes" in seismic["sourceIds"]
    assert "geonet-new-zealand" in seismic["sourceIds"]
    assert all("impact score" not in line.lower() for line in seismic["exportLines"])
    weather_alerts = next(family for family in payload["families"] if family["familyId"] == "weather-alert-advisory")
    assert "hong-kong-observatory-open-weather" in weather_alerts["sourceIds"]
    assert "environment-canada-cap-alerts" in weather_alerts["sourceIds"]
    assert "met-norway-metalerts" in weather_alerts["sourceIds"]
    assert "portugal-ipma-open-data" in weather_alerts["sourceIds"]
    assert "met-eireann-warnings" in weather_alerts["sourceIds"]
    assert "geosphere-austria-warnings" in weather_alerts["sourceIds"]
    assert "advisory" in " ".join(weather_alerts["evidenceBases"]).lower()


def test_environmental_source_families_overview_preserves_caveats_and_prompt_injection_inertness() -> None:
    client = _client()

    payload = client.get("/api/context/environmental/source-families-overview").json()

    water_quality = next(family for family in payload["families"] if family["familyId"] == "water-quality-context")
    row = next(source for source in water_quality["sources"] if source["sourceId"] == "uk-ea-water-quality")
    export_blob = " ".join(water_quality["exportLines"] + row["exportLines"] + row["reviewLines"] + water_quality["caveats"])

    assert "<script" not in export_blob.lower()
    assert "mark this source validated" not in export_blob.lower()
    assert "inert" in export_blob.lower()
    assert "health risk" not in " ".join(water_quality["exportLines"]).lower()
    assert "damage" not in " ".join(water_quality["exportLines"]).lower()
    infrastructure = next(family for family in payload["families"] if family["familyId"] == "infrastructure-event-context")
    nrc_row = next(source for source in infrastructure["sources"] if source["sourceId"] == "nrc-event-notifications")
    infrastructure_blob = " ".join(infrastructure["exportLines"] + nrc_row["reviewLines"] + infrastructure["caveats"])
    assert "inert" in infrastructure_blob.lower()
    assert "validated" not in infrastructure_blob.lower()
    assert "confirm radiological impact" not in infrastructure_blob.lower()


def test_environmental_source_families_overview_review_lines_and_runtime_states_are_conservative() -> None:
    client = _client()

    payload = client.get("/api/context/environmental/source-families-overview").json()

    families = {family["familyId"]: family for family in payload["families"]}
    risk_family = families["risk-reference"]
    assert any("fixture/local mode" in line.lower() for line in risk_family["reviewLines"])
    weather_alerts = families["weather-alert-advisory"]
    assert weather_alerts["familyHealth"] in {"loaded", "mixed", "empty", "degraded", "unknown"}
    assert all("damage score" not in line.lower() for line in weather_alerts["exportLines"])
    assert all("health risk" not in line.lower() for line in weather_alerts["exportLines"])
    water_family = families["weather-flood-hydrology"]
    assert "met-eireann-forecast" in water_family["sourceIds"]
    assert water_family["familyHealth"] in {"loaded", "mixed", "empty", "degraded", "unknown"}
    assert all("hazard score" not in line.lower() for line in water_family["exportLines"])


def test_environmental_source_families_export_bundle_supports_family_filters() -> None:
    client = _client()

    response = client.get(
        "/api/context/environmental/source-families-export",
        params=[("family", "seismic"), ("family", "weather-alert-advisory")],
    )
    payload = response.json()

    assert response.status_code == 200
    assert payload["metadata"]["profile"] == "compact"
    assert payload["metadata"]["requestedFamilyIds"] == ["seismic", "weather-alert-advisory"]
    assert payload["metadata"]["includedFamilyIds"] == ["seismic", "weather-alert-advisory"]
    assert payload["metadata"]["missingFamilyIds"] == []
    assert payload["familyCount"] == 2
    family_ids = [family["familyId"] for family in payload["families"]]
    assert family_ids == ["seismic", "weather-alert-advisory"]
    assert all("damage score" not in " ".join(family["exportLines"]).lower() for family in payload["families"])
    assert all("health risk score" not in " ".join(family["exportLines"]).lower() for family in payload["families"])


def test_environmental_source_families_export_bundle_reports_missing_family_ids_and_preserves_guardrails() -> None:
    client = _client()

    response = client.get(
        "/api/context/environmental/source-families-export",
        params=[("family", "water-quality-context"), ("family", "not-a-family")],
    )
    payload = response.json()

    assert response.status_code == 200
    assert payload["metadata"]["includedFamilyIds"] == ["water-quality-context"]
    assert payload["metadata"]["missingFamilyIds"] == ["not-a-family"]
    assert payload["familyCount"] == 1
    assert payload["sourceCount"] >= 1
    export_blob = " ".join(payload["caveats"] + payload["families"][0]["caveats"] + payload["families"][0]["exportLines"])
    assert "impact score" not in export_blob.lower()
    assert "damage score" not in export_blob.lower()
    assert "health-risk score" not in export_blob.lower()
    assert "review context only" in " ".join(payload["caveats"]).lower()


def test_environmental_context_export_package_supports_filtered_snapshot_metadata() -> None:
    client = _client()

    response = client.get(
        "/api/context/environmental/context-export-package",
        params=[("family", "seismic"), ("family", "weather-alert-advisory")],
    )
    payload = response.json()

    assert response.status_code == 200
    assert payload["metadata"]["source"] == "environmental-context-export-package"
    assert payload["metadata"]["profile"] == "compact"
    assert payload["snapshotMetadata"]["snapshotType"] == "environmental-context-export"
    assert payload["snapshotMetadata"]["requestedFamilyIds"] == ["seismic", "weather-alert-advisory"]
    assert payload["snapshotMetadata"]["includedFamilyIds"] == ["seismic", "weather-alert-advisory"]
    assert payload["snapshotMetadata"]["missingFamilyIds"] == []
    assert payload["familyIds"] == ["seismic", "weather-alert-advisory"]
    assert "usgs-earthquake-hazards-program" in payload["sourceIds"]
    assert "hong-kong-observatory-open-weather" in payload["sourceIds"]
    assert "not a common situation ui" in " ".join(payload["caveats"]).lower()


def test_environmental_context_export_package_reports_missing_families_and_preserves_no_scoring_guardrails() -> None:
    client = _client()

    response = client.get(
        "/api/context/environmental/context-export-package",
        params=[("family", "water-quality-context"), ("family", "unknown-family")],
    )
    payload = response.json()

    assert response.status_code == 200
    assert payload["snapshotMetadata"]["includedFamilyIds"] == ["water-quality-context"]
    assert payload["snapshotMetadata"]["missingFamilyIds"] == ["unknown-family"]
    assert payload["familyCount"] == 1
    assert payload["sourceCount"] >= 1
    assert "observed" in payload["metadata"]["evidenceBases"]
    export_blob = " ".join(payload["exportLines"] + payload["reviewLines"] + payload["caveats"])
    assert "hazard score" not in export_blob.lower()
    assert "damage score" not in export_blob.lower()
    assert "health-risk score" not in export_blob.lower()


def test_environmental_source_health_issue_queue_supports_filtered_output_and_snapshot_metadata() -> None:
    client = _client()

    response = client.get(
        "/api/context/environmental/source-health-issue-queue",
        params=[("family", "seismic"), ("family", "weather-alert-advisory")],
    )
    payload = response.json()

    assert response.status_code == 200
    assert payload["metadata"]["source"] == "environmental-source-health-issue-queue"
    assert payload["snapshotMetadata"]["requestedFamilyIds"] == ["seismic", "weather-alert-advisory"]
    assert payload["snapshotMetadata"]["includedFamilyIds"] == ["seismic", "weather-alert-advisory"]
    assert payload["snapshotMetadata"]["missingFamilyIds"] == []
    assert payload["issueCount"] >= 1
    issue_types = {issue["issueType"] for issue in payload["issues"]}
    assert "fixture-only" in issue_types
    assert "count-only-health" in issue_types
    assert "advisory-only" in issue_types or "contextual-only" in issue_types
    export_blob = " ".join(payload["exportLines"] + payload["reviewLines"] + payload["caveats"])
    assert "threat score" not in export_blob.lower()
    assert "target score" not in export_blob.lower()
    assert "damage score" not in export_blob.lower()


def test_environmental_source_health_issue_queue_reports_missing_family_ids_and_inert_prompt_like_text() -> None:
    client = _client()

    response = client.get(
        "/api/context/environmental/source-health-issue-queue",
        params=[("family", "water-quality-context"), ("family", "unknown-family")],
    )
    payload = response.json()

    assert response.status_code == 200
    assert payload["snapshotMetadata"]["includedFamilyIds"] == ["water-quality-context"]
    assert payload["snapshotMetadata"]["missingFamilyIds"] == ["unknown-family"]
    missing_issue = next(issue for issue in payload["issues"] if issue["issueType"] == "missing-family")
    assert missing_issue["familyId"] == "unknown-family"
    water_issue_blob = " ".join(
        line
        for issue in payload["issues"]
        if issue.get("sourceId") == "uk-ea-water-quality"
        for line in (issue["reviewLines"] + issue["exportLines"] + issue["caveats"])
    )
    assert "<script" not in water_issue_blob.lower()
    assert "mark this source validated" not in water_issue_blob.lower()
    assert "inert" in water_issue_blob.lower()


def test_environmental_source_health_issue_queue_preserves_source_health_mode_and_evidence_limits() -> None:
    client = _client()

    payload = client.get("/api/context/environmental/source-health-issue-queue").json()

    fixture_issue = next(issue for issue in payload["issues"] if issue["issueType"] == "fixture-only")
    assert fixture_issue["sourceMode"] == "fixture"
    assert fixture_issue["allowedReviewPosture"] in {"document-and-monitor", "source-health-review-only"}

    advisory_issue = next(issue for issue in payload["issues"] if issue["issueType"] == "advisory-only")
    assert advisory_issue["evidenceBasis"] == "advisory"

    count_only_issue = next(issue for issue in payload["issues"] if issue["issueType"] == "count-only-health")
    assert count_only_issue["sourceHealth"] in {"loaded", "empty", "stale", "error", "disabled", "unknown"}
    assert "richer source-health state is not asserted" in count_only_issue["summaryLine"].lower()


def test_environmental_situation_snapshot_package_supports_filtered_output_and_default_profile() -> None:
    client = _client()

    response = client.get(
        "/api/context/environmental/situation-snapshot-package",
        params=[("family", "seismic"), ("family", "weather-alert-advisory"), ("profile", "default")],
    )
    payload = response.json()

    assert response.status_code == 200
    assert payload["metadata"]["source"] == "environmental-situation-snapshot-package"
    assert payload["metadata"]["profile"] == "default"
    assert payload["snapshotMetadata"]["includedFamilyIds"] == ["seismic", "weather-alert-advisory"]
    assert payload["familyCount"] == 2
    assert payload["issueCount"] >= 1
    assert len(payload["families"]) == 2
    assert len(payload["issues"]) >= 1
    assert any("default profile" in line.lower() for line in payload["reviewLines"])


def test_environmental_situation_snapshot_package_profile_behavior_and_missing_family_ids() -> None:
    client = _client()

    chokepoint = client.get(
        "/api/context/environmental/situation-snapshot-package",
        params=[("family", "water-quality-context"), ("family", "unknown-family"), ("profile", "chokepoint-context")],
    ).json()
    source_health = client.get(
        "/api/context/environmental/situation-snapshot-package",
        params=[("family", "water-quality-context"), ("profile", "source-health-review")],
    ).json()

    assert chokepoint["metadata"]["profile"] == "chokepoint-context"
    assert chokepoint["snapshotMetadata"]["missingFamilyIds"] == ["unknown-family"]
    assert any("does not prove impact" in line.lower() or "does not prove" in line.lower() for line in chokepoint["caveats"])

    assert source_health["metadata"]["profile"] == "source-health-review"
    assert any("availability" in line.lower() for line in source_health["reviewLines"])
    assert any("not event significance scoring" in line.lower() for line in source_health["caveats"])


def test_environmental_situation_snapshot_package_preserves_issue_queue_and_no_global_scoring() -> None:
    client = _client()

    payload = client.get("/api/context/environmental/situation-snapshot-package").json()

    assert payload["issueCount"] == len(payload["issues"])
    assert payload["metadata"]["issueCount"] == payload["issueCount"]
    assert "observed" in payload["metadata"]["evidenceBases"]
    export_blob = " ".join(payload["exportLines"] + payload["reviewLines"] + payload["caveats"])
    assert "hazard score" not in export_blob.lower()
    assert "threat score" not in export_blob.lower()
    assert "target score" not in export_blob.lower()
    assert "damage score" not in export_blob.lower()
