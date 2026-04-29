from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from src.services.planet_imagery_service import build_planet_config

def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat()


NOW = datetime(2026, 4, 4, 12, 0, tzinfo=timezone.utc)
CLIENT_DIST = Path(__file__).resolve().parents[2] / "client" / "dist"


def _aircraft_entities() -> list[dict[str, Any]]:
    return [
        {
            "id": "aircraft:test-abc123",
            "type": "aircraft",
            "source": "opensky-network",
            "label": "DAL123",
            "latitude": 30.2672,
            "longitude": -97.7431,
            "altitude": 3200.0,
            "heading": 184.0,
            "speed": 210.0,
            "timestamp": _iso(NOW - timedelta(seconds=20)),
            "observedAt": _iso(NOW - timedelta(seconds=20)),
            "fetchedAt": _iso(NOW),
            "status": "airborne",
            "sourceDetail": "OpenSky Network state vectors",
            "externalUrl": "https://opensky-network.org/aircraft-profile?icao24=abc123",
            "confidence": 0.82,
            "historyAvailable": True,
            "canonicalIds": {"icao24": "abc123", "callsign": "DAL123"},
            "rawIdentifiers": {"origin_country": "United States"},
            "quality": {
                "score": 0.82,
                "label": "estimated",
                "sourceFreshnessSeconds": 20,
                "notes": ["Fixture aircraft provenance"],
            },
            "derivedFields": [
                {
                    "name": "observation_age_seconds",
                    "value": "20",
                    "unit": "seconds",
                    "derivedFrom": "observed_at",
                    "method": "fixture",
                }
            ],
            "historySummary": {
                "kind": "live-polled",
                "pointCount": 3,
                "windowMinutes": 30,
                "lastPointAt": _iso(NOW - timedelta(seconds=20)),
                "partial": False,
                "detail": "Fixture live trail.",
            },
            "linkTargets": ["airport:KAUS"],
            "metadata": {"positionSource": 0},
            "callsign": "DAL123",
            "squawk": "1200",
            "originCountry": "United States",
            "onGround": False,
            "verticalRate": 0.0,
        },
        {
            "id": "aircraft:test-def456",
            "type": "aircraft",
            "source": "opensky-network",
            "label": "UAL456",
            "latitude": 30.295,
            "longitude": -97.71,
            "altitude": 800.0,
            "heading": 92.0,
            "speed": 160.0,
            "timestamp": _iso(NOW - timedelta(seconds=75)),
            "observedAt": _iso(NOW - timedelta(seconds=75)),
            "fetchedAt": _iso(NOW),
            "status": "on-ground",
            "sourceDetail": "OpenSky Network state vectors",
            "externalUrl": "https://opensky-network.org/aircraft-profile?icao24=def456",
            "confidence": 0.64,
            "historyAvailable": True,
            "canonicalIds": {"icao24": "def456", "callsign": "UAL456"},
            "rawIdentifiers": {"origin_country": "United States"},
            "quality": {
                "score": 0.64,
                "label": "estimated",
                "sourceFreshnessSeconds": 75,
                "notes": ["Fixture aircraft provenance"],
            },
            "derivedFields": [],
            "historySummary": {
                "kind": "live-polled",
                "pointCount": 1,
                "windowMinutes": 30,
                "lastPointAt": _iso(NOW - timedelta(seconds=75)),
                "partial": True,
                "detail": "Initial point only.",
            },
            "linkTargets": [],
            "metadata": {"positionSource": 1},
            "callsign": "UAL456",
            "squawk": None,
            "originCountry": "United States",
            "onGround": True,
            "verticalRate": None,
        },
    ]


def _satellite_entities() -> tuple[list[dict[str, Any]], dict[str, list[dict[str, Any]]], dict[str, dict[str, Any]]]:
    sat_id = "satellite:25544"
    path = [
        {
            "latitude": 29.9,
            "longitude": -98.1,
            "altitude": 408000.0,
            "timestamp": _iso(NOW - timedelta(minutes=15)),
        },
        {
            "latitude": 30.2672,
            "longitude": -97.7431,
            "altitude": 409000.0,
            "timestamp": _iso(NOW),
        },
        {
            "latitude": 30.8,
            "longitude": -97.1,
            "altitude": 408500.0,
            "timestamp": _iso(NOW + timedelta(minutes=15)),
        },
    ]
    return (
        [
            {
                "id": sat_id,
                "type": "satellite",
                "source": "celestrak-active",
                "label": "ISS (ZARYA)",
                "latitude": 30.2672,
                "longitude": -97.7431,
                "altitude": 409000.0,
                "heading": 91.0,
                "speed": 7660.0,
                "timestamp": _iso(NOW),
                "observedAt": _iso(NOW),
                "fetchedAt": _iso(NOW),
                "status": "active",
                "sourceDetail": "CelesTrak active catalog via GP data",
                "externalUrl": "https://celestrak.org/satcat/search.php?CATNR=25544",
                "confidence": 0.91,
                "historyAvailable": True,
                "canonicalIds": {"norad_id": "25544", "object_id": "1998-067A"},
                "rawIdentifiers": {"object_name": "ISS (ZARYA)"},
                "quality": {
                    "score": 0.91,
                    "label": "propagated",
                    "sourceFreshnessSeconds": 120,
                    "notes": ["Fixture satellite provenance"],
                },
                "derivedFields": [
                    {
                        "name": "orbit_class",
                        "value": "leo",
                        "derivedFrom": "mean_motion",
                        "method": "fixture",
                    }
                ],
                "historySummary": {
                    "kind": "propagated",
                    "pointCount": 3,
                    "windowMinutes": 90,
                    "lastPointAt": _iso(NOW + timedelta(minutes=15)),
                    "partial": False,
                    "detail": "Fixture propagated orbit path.",
                },
                "linkTargets": ["airport:KAUS"],
                "metadata": {"raan": 10.2},
                "noradId": 25544,
                "orbitClass": "leo",
                "inclination": 51.6,
                "period": 92.7,
                "tleTimestamp": _iso(NOW - timedelta(hours=2)),
            }
        ],
        {sat_id: path},
        {
            sat_id: {
                "riseAt": _iso(NOW - timedelta(minutes=10)),
                "peakAt": _iso(NOW),
                "setAt": _iso(NOW + timedelta(minutes=10)),
                "detail": "Fixture pass window derived from orbit path.",
            }
        },
    )


def _camera_entities() -> list[dict[str, Any]]:
    return [
        {
            "id": "camera:usgs-ashcam:akutan-north",
            "type": "camera",
            "source": "usgs-ashcam",
            "label": "Akutan North",
            "latitude": 54.1332,
            "longitude": -165.9871,
            "altitude": 0.0,
            "heading": 41.0,
            "speed": None,
            "timestamp": _iso(NOW - timedelta(seconds=45)),
            "observedAt": _iso(NOW - timedelta(seconds=45)),
            "fetchedAt": _iso(NOW),
            "status": "active",
            "sourceDetail": "USGS AshCam official webcam catalog",
            "externalUrl": "https://www.avo.alaska.edu/webcam/akutan.php",
            "confidence": 0.98,
            "historyAvailable": False,
            "canonicalIds": {"camera_id": "akutan-north"},
            "rawIdentifiers": {"volcano": "Akutan"},
            "quality": {
                "score": 0.98,
                "label": "official",
                "sourceFreshnessSeconds": 45,
                "notes": ["Fixture Ashcam direct-image camera"],
            },
            "derivedFields": [],
            "historySummary": None,
            "linkTargets": [],
            "metadata": {"catalogSource": "fixture-ashcam"},
            "cameraId": "akutan-north",
            "sourceCameraId": "akutan-north",
            "owner": "U.S. Geological Survey",
            "state": "AK",
            "county": "Aleutians East Borough",
            "region": "Aleutians",
            "roadway": None,
            "direction": "NE",
            "locationDescription": "Akutan Volcano north-facing summit view",
            "feedType": "snapshot",
            "accessPolicy": "public",
            "position": {
                "kind": "exact",
                "confidence": 1.0,
                "source": "official",
                "notes": [],
            },
            "orientation": {
                "kind": "exact",
                "degrees": 41.0,
                "cardinalDirection": "NE",
                "confidence": 1.0,
                "source": "official",
                "isPtz": False,
                "notes": [],
            },
            "frame": {
                "status": "live",
                "refreshIntervalSeconds": 60,
                "lastFrameAt": _iso(NOW - timedelta(seconds=30)),
                "ageSeconds": 30,
                "imageUrl": "https://avo.alaska.edu/images/ashcam/akutan/latest.jpg",
                "thumbnailUrl": None,
                "streamUrl": None,
                "viewerUrl": "https://www.avo.alaska.edu/webcam/akutan.php",
                "width": 1280,
                "height": 720,
            },
            "compliance": {
                "attributionText": "USGS Alaska Volcano Observatory",
                "attributionUrl": "https://www.avo.alaska.edu/webcam/akutan.php",
                "termsUrl": "https://www.usgs.gov/laws/policies_notices.html",
                "licenseSummary": "Public federal webcam imagery with attribution",
                "requiresAuthentication": False,
                "supportsEmbedding": False,
                "supportsFrameStorage": True,
                "reviewRequired": False,
                "provenanceNotes": ["Official federal webcam source."],
                "notes": ["Direct image URL is present in the official source feed."],
            },
            "review": {
                "status": "verified",
                "reason": None,
                "requiredActions": [],
                "issueCategories": [],
            },
            "healthState": "healthy",
            "degradedReason": None,
            "lastMetadataRefreshAt": _iso(NOW - timedelta(seconds=55)),
            "nextFrameRefreshAt": _iso(NOW + timedelta(seconds=30)),
            "backoffUntil": None,
            "retryCount": 0,
            "lastHttpStatus": 200,
            "nearestReferenceRefId": None,
            "referenceLinkStatus": "hinted",
            "linkCandidateCount": 1,
            "referenceHintText": "Akutan Volcano",
            "facilityCodeHint": "PAUT",
        },
        {
            "id": "camera:usgs-ashcam:spurr-overlook",
            "type": "camera",
            "source": "usgs-ashcam",
            "label": "Spurr Overlook",
            "latitude": 61.2994,
            "longitude": -152.2511,
            "altitude": 0.0,
            "heading": None,
            "speed": None,
            "timestamp": _iso(NOW - timedelta(minutes=4)),
            "observedAt": _iso(NOW - timedelta(minutes=4)),
            "fetchedAt": _iso(NOW),
            "status": "active",
            "sourceDetail": "USGS AshCam official webcam catalog",
            "externalUrl": "https://www.avo.alaska.edu/webcam/spurr.php",
            "confidence": 0.76,
            "historyAvailable": False,
            "canonicalIds": {"camera_id": "spurr-overlook"},
            "rawIdentifiers": {"volcano": "Spurr"},
            "quality": {
                "score": 0.76,
                "label": "viewer-only",
                "sourceFreshnessSeconds": 240,
                "notes": ["Fixture Ashcam viewer-only camera"],
            },
            "derivedFields": [],
            "historySummary": None,
            "linkTargets": [],
            "metadata": {"catalogSource": "fixture-ashcam"},
            "cameraId": "spurr-overlook",
            "sourceCameraId": "spurr-overlook",
            "owner": "U.S. Geological Survey",
            "state": "AK",
            "county": "Matanuska-Susitna Borough",
            "region": "Cook Inlet",
            "roadway": None,
            "direction": None,
            "locationDescription": "Mount Spurr panorama viewer page",
            "feedType": "page",
            "accessPolicy": "public",
            "position": {
                "kind": "exact",
                "confidence": 1.0,
                "source": "official",
                "notes": [],
            },
            "orientation": {
                "kind": "unknown",
                "degrees": None,
                "cardinalDirection": None,
                "confidence": None,
                "source": "official",
                "isPtz": False,
                "notes": ["Orientation not exposed by source catalog."],
            },
            "frame": {
                "status": "viewer-page-only",
                "refreshIntervalSeconds": 300,
                "lastFrameAt": None,
                "ageSeconds": None,
                "imageUrl": None,
                "thumbnailUrl": None,
                "streamUrl": None,
                "viewerUrl": "https://www.avo.alaska.edu/webcam/spurr.php",
                "width": None,
                "height": None,
            },
            "compliance": {
                "attributionText": "USGS Alaska Volcano Observatory",
                "attributionUrl": "https://www.avo.alaska.edu/webcam/spurr.php",
                "termsUrl": "https://www.usgs.gov/laws/policies_notices.html",
                "licenseSummary": "Public federal webcam imagery with attribution",
                "requiresAuthentication": False,
                "supportsEmbedding": False,
                "supportsFrameStorage": True,
                "reviewRequired": True,
                "provenanceNotes": ["Viewer link only in current source payload."],
                "notes": ["Do not treat viewer-only camera as direct-image."],
            },
            "review": {
                "status": "needs-review",
                "reason": "Viewer-only feed needs image-path verification.",
                "requiredActions": ["Confirm whether a direct snapshot path exists."],
                "issueCategories": ["viewer-feed"],
            },
            "healthState": "degraded",
            "degradedReason": "Viewer page available but no trusted direct snapshot URL.",
            "lastMetadataRefreshAt": _iso(NOW - timedelta(minutes=5)),
            "nextFrameRefreshAt": _iso(NOW + timedelta(minutes=5)),
            "backoffUntil": None,
            "retryCount": 0,
            "lastHttpStatus": 200,
            "nearestReferenceRefId": None,
            "referenceLinkStatus": "hinted",
            "linkCandidateCount": 1,
            "referenceHintText": "Mount Spurr",
            "facilityCodeHint": "PASP",
        },
    ]


def _camera_source_status() -> list[dict[str, Any]]:
    return [
        {
            "name": "usgs-ashcam",
            "state": "healthy",
            "enabled": True,
            "healthy": True,
            "freshnessSeconds": 45,
            "staleAfterSeconds": 600,
            "lastSuccessAt": _iso(NOW - timedelta(seconds=45)),
            "degradedReason": None,
            "rateLimited": False,
            "hiddenReason": None,
            "detail": "Validated no-auth official webcam source.",
            "credentialsConfigured": True,
            "blockedReason": None,
            "reviewRequired": True,
            "lastAttemptAt": _iso(NOW - timedelta(seconds=55)),
            "lastFailureAt": None,
            "successCount": 12,
            "failureCount": 0,
            "warningCount": 1,
            "nextRefreshAt": _iso(NOW + timedelta(seconds=30)),
            "backoffUntil": None,
            "retryCount": 0,
            "lastHttpStatus": 200,
            "lastStartedAt": _iso(NOW - timedelta(seconds=55)),
            "lastCompletedAt": _iso(NOW - timedelta(seconds=50)),
            "cadenceSeconds": 300,
            "cadenceReason": "Validated official source baseline",
            "lastRunMode": "worker",
            "lastValidationAt": _iso(NOW - timedelta(days=1)),
            "lastFrameProbeCount": 2,
            "lastFrameStatusSummary": {"live": 1, "viewer-page-only": 1},
            "lastMetadataUncertaintyCount": 1,
            "lastCadenceObservation": "No-auth official source validated at conservative baseline cadence.",
        },
        {
            "name": "wsdot-cameras",
            "state": "credentials-missing",
            "enabled": False,
            "healthy": False,
            "freshnessSeconds": None,
            "staleAfterSeconds": 300,
            "lastSuccessAt": None,
            "degradedReason": None,
            "rateLimited": False,
            "hiddenReason": "disabled-by-configuration",
            "detail": "Structured official source is blocked only by missing credentials.",
            "credentialsConfigured": False,
            "blockedReason": None,
            "reviewRequired": False,
            "lastAttemptAt": None,
            "lastFailureAt": None,
            "successCount": 0,
            "failureCount": 0,
            "warningCount": 0,
            "nextRefreshAt": None,
            "backoffUntil": None,
            "retryCount": 0,
            "lastHttpStatus": None,
            "lastStartedAt": None,
            "lastCompletedAt": None,
            "cadenceSeconds": 300,
            "cadenceReason": "Official DOT baseline pending credentials",
            "lastRunMode": None,
            "lastValidationAt": None,
            "lastFrameProbeCount": 0,
            "lastFrameStatusSummary": {},
            "lastMetadataUncertaintyCount": 0,
            "lastCadenceObservation": None,
        },
    ]


def _camera_sources() -> list[dict[str, Any]]:
    return [
        {
            "key": "usgs-ashcam",
            "displayName": "USGS AshCam",
            "owner": "U.S. Geological Survey",
            "sourceType": "public-webcam",
            "coverage": "Alaska volcano observatories",
            "priority": 20,
            "enabled": True,
            "authentication": "none",
            "defaultRefreshIntervalSeconds": 300,
            "notes": ["Validated no-auth official webcam source."],
            "compliance": _camera_entities()[0]["compliance"],
            "status": "healthy",
            "detail": "Validated no-auth official webcam source.",
            "credentialsConfigured": True,
            "blockedReason": None,
            "reviewRequired": True,
            "degradedReason": None,
            "lastAttemptAt": _iso(NOW - timedelta(seconds=55)),
            "lastSuccessAt": _iso(NOW - timedelta(seconds=45)),
            "lastFailureAt": None,
            "successCount": 12,
            "failureCount": 0,
            "warningCount": 1,
            "lastCameraCount": 425,
            "nextRefreshAt": _iso(NOW + timedelta(seconds=30)),
            "backoffUntil": None,
            "retryCount": 0,
            "lastHttpStatus": 200,
            "lastStartedAt": _iso(NOW - timedelta(seconds=55)),
            "lastCompletedAt": _iso(NOW - timedelta(seconds=50)),
            "cadenceSeconds": 300,
            "cadenceReason": "Validated official source baseline",
            "lastRunMode": "worker",
            "lastValidationAt": _iso(NOW - timedelta(days=1)),
            "lastFrameProbeCount": 2,
            "lastFrameStatusSummary": {"live": 1, "viewer-page-only": 1},
            "lastMetadataUncertaintyCount": 1,
            "lastCadenceObservation": "Validated no-auth cadence retained.",
            "inventorySourceType": "public-webcam-api",
            "accessMethod": "json-api",
            "onboardingState": "active",
            "coverageStates": ["AK"],
            "coverageRegions": ["Alaska volcano observatories"],
            "providesExactCoordinates": True,
            "providesDirectionText": False,
            "providesNumericHeading": True,
            "providesDirectImage": True,
            "providesViewerOnly": True,
            "supportsEmbed": False,
            "supportsStorage": True,
            "approximateCameraCount": 425,
            "importReadiness": "validated",
            "discoveredCameraCount": 425,
            "usableCameraCount": 356,
            "directImageCameraCount": 268,
            "viewerOnlyCameraCount": 88,
            "missingCoordinateCameraCount": 0,
            "uncertainOrientationCameraCount": 0,
            "reviewQueueCount": 88,
            "lastImportOutcome": "needs-review",
            "sourceQualityNotes": ["Strong no-auth structured source."],
            "sourceStabilityNotes": ["Official federal webcam catalog."],
            "pageStructure": None,
            "likelyCameraCount": None,
            "complianceRisk": None,
            "extractionFeasibility": None,
        },
        {
            "key": "wsdot-cameras",
            "displayName": "Washington State DOT Cameras",
            "owner": "Washington State Department of Transportation",
            "sourceType": "official-dot",
            "coverage": "Washington state highways",
            "priority": 10,
            "enabled": False,
            "authentication": "access-code",
            "defaultRefreshIntervalSeconds": 300,
            "notes": ["Official structured source blocked on credentials in fixture mode."],
            "compliance": _camera_entities()[0]["compliance"],
            "status": "credentials-missing",
            "detail": "Credential-blocked but potentially high-value source.",
            "credentialsConfigured": False,
            "blockedReason": None,
            "reviewRequired": False,
            "degradedReason": None,
            "lastAttemptAt": None,
            "lastSuccessAt": None,
            "lastFailureAt": None,
            "successCount": 0,
            "failureCount": 0,
            "warningCount": 0,
            "lastCameraCount": 0,
            "nextRefreshAt": None,
            "backoffUntil": None,
            "retryCount": 0,
            "lastHttpStatus": None,
            "lastStartedAt": None,
            "lastCompletedAt": None,
            "cadenceSeconds": 300,
            "cadenceReason": "Official DOT baseline pending credentials",
            "lastRunMode": None,
            "lastValidationAt": None,
            "lastFrameProbeCount": 0,
            "lastFrameStatusSummary": {},
            "lastMetadataUncertaintyCount": 0,
            "lastCadenceObservation": None,
            "inventorySourceType": "official-dot-api",
            "accessMethod": "json-api",
            "onboardingState": "approved",
            "coverageStates": ["WA"],
            "coverageRegions": ["Washington"],
            "providesExactCoordinates": True,
            "providesDirectionText": True,
            "providesNumericHeading": False,
            "providesDirectImage": True,
            "providesViewerOnly": False,
            "supportsEmbed": False,
            "supportsStorage": True,
            "approximateCameraCount": 0,
            "importReadiness": "approved-unvalidated",
            "discoveredCameraCount": 0,
            "usableCameraCount": 0,
            "directImageCameraCount": 0,
            "viewerOnlyCameraCount": 0,
            "missingCoordinateCameraCount": 0,
            "uncertainOrientationCameraCount": 0,
            "reviewQueueCount": 0,
            "lastImportOutcome": None,
            "sourceQualityNotes": ["Blocked by credentials, not by quality."],
            "sourceStabilityNotes": ["Official DOT feed."],
            "pageStructure": None,
            "likelyCameraCount": None,
            "complianceRisk": None,
            "extractionFeasibility": None,
        },
    ]


def _camera_source_inventory() -> dict[str, Any]:
    return {
        "fetchedAt": _iso(NOW),
        "count": 3,
        "summary": {
            "totalSources": 3,
            "activeSources": 1,
            "credentialedSources": 1,
            "credentiallessSources": 2,
            "directImageSources": 2,
            "viewerOnlySources": 1,
            "validatedSources": 1,
            "lowYieldSources": 0,
            "poorQualitySources": 0,
            "sourcesByType": {
                "public-webcam-api": 1,
                "official-dot-api": 1,
                "public-camera-page": 1,
            },
        },
        "sources": [
            {
                "key": "usgs-ashcam",
                "sourceName": "USGS AshCam",
                "sourceFamily": "federal-webcams",
                "sourceType": "public-webcam-api",
                "accessMethod": "json-api",
                "onboardingState": "active",
                "owner": "U.S. Geological Survey",
                "authentication": "none",
                "credentialsConfigured": True,
                "rateLimitNotes": ["No-auth official source; keep conservative cadence."],
                "coverageGeography": "Alaska volcano observatories",
                "coverageStates": ["AK"],
                "coverageRegions": ["Aleutians", "Cook Inlet"],
                "providesExactCoordinates": True,
                "providesDirectionText": False,
                "providesNumericHeading": True,
                "providesDirectImage": True,
                "providesViewerOnly": True,
                "supportsEmbed": False,
                "supportsStorage": True,
                "compliance": _camera_entities()[0]["compliance"],
                "sourceQualityNotes": ["Validated official structured source."],
                "sourceStabilityNotes": ["Real no-auth source already exercised."],
                "blockedReason": None,
                "approximateCameraCount": 425,
                "importReadiness": "validated",
                "discoveredCameraCount": 425,
                "usableCameraCount": 356,
                "directImageCameraCount": 268,
                "viewerOnlyCameraCount": 88,
                "missingCoordinateCameraCount": 0,
                "uncertainOrientationCameraCount": 0,
                "reviewQueueCount": 88,
                "lastCatalogImportAt": _iso(NOW - timedelta(minutes=5)),
                "lastCatalogImportStatus": "success",
                "lastCatalogImportDetail": "Fixture AshCam catalog import succeeded.",
                "lastImportOutcome": "needs-review",
                "pageStructure": None,
                "likelyCameraCount": None,
                "complianceRisk": None,
                "extractionFeasibility": None,
            },
            {
                "key": "wsdot-cameras",
                "sourceName": "Washington State DOT Cameras",
                "sourceFamily": "official-dot",
                "sourceType": "official-dot-api",
                "accessMethod": "json-api",
                "onboardingState": "approved",
                "owner": "Washington State Department of Transportation",
                "authentication": "access-code",
                "credentialsConfigured": False,
                "rateLimitNotes": ["Blocked pending access code."],
                "coverageGeography": "Washington state highways",
                "coverageStates": ["WA"],
                "coverageRegions": ["Washington"],
                "providesExactCoordinates": True,
                "providesDirectionText": True,
                "providesNumericHeading": False,
                "providesDirectImage": True,
                "providesViewerOnly": False,
                "supportsEmbed": False,
                "supportsStorage": True,
                "compliance": _camera_entities()[0]["compliance"],
                "sourceQualityNotes": ["Potentially high-value once credentials are configured."],
                "sourceStabilityNotes": ["Official structured source."],
                "blockedReason": "Credentials are required before import can run.",
                "approximateCameraCount": 0,
                "importReadiness": "approved-unvalidated",
                "discoveredCameraCount": 0,
                "usableCameraCount": 0,
                "directImageCameraCount": 0,
                "viewerOnlyCameraCount": 0,
                "missingCoordinateCameraCount": 0,
                "uncertainOrientationCameraCount": 0,
                "reviewQueueCount": 0,
                "lastCatalogImportAt": None,
                "lastCatalogImportStatus": None,
                "lastCatalogImportDetail": "No import attempted in fixture mode.",
                "lastImportOutcome": None,
                "pageStructure": None,
                "likelyCameraCount": None,
                "complianceRisk": None,
                "extractionFeasibility": None,
            },
            {
                "key": "faa-weather-cameras-page",
                "sourceName": "FAA Weather Cameras",
                "sourceFamily": "official-page-candidate",
                "sourceType": "public-camera-page",
                "accessMethod": "html-index",
                "onboardingState": "candidate",
                "owner": "Federal Aviation Administration",
                "authentication": "none",
                "credentialsConfigured": True,
                "rateLimitNotes": ["Candidate only; no automated import."],
                "coverageGeography": "U.S. aviation weather camera pages",
                "coverageStates": ["AK"],
                "coverageRegions": ["FAA weather camera network"],
                "providesExactCoordinates": False,
                "providesDirectionText": False,
                "providesNumericHeading": False,
                "providesDirectImage": False,
                "providesViewerOnly": True,
                "supportsEmbed": False,
                "supportsStorage": False,
                "compliance": _camera_entities()[1]["compliance"],
                "sourceQualityNotes": ["High likely value if review passes."],
                "sourceStabilityNotes": ["Still candidate-only; page extraction not implemented."],
                "blockedReason": "Review gated until compliance and extraction review complete.",
                "approximateCameraCount": 299,
                "importReadiness": "inventory-only",
                "discoveredCameraCount": None,
                "usableCameraCount": None,
                "directImageCameraCount": None,
                "viewerOnlyCameraCount": None,
                "missingCoordinateCameraCount": None,
                "uncertainOrientationCameraCount": None,
                "reviewQueueCount": None,
                "lastCatalogImportAt": None,
                "lastCatalogImportStatus": None,
                "lastCatalogImportDetail": "Candidate metadata only. No import path is active.",
                "lastImportOutcome": None,
                "pageStructure": "interactive-map-html",
                "likelyCameraCount": 299,
                "complianceRisk": "medium",
                "extractionFeasibility": "medium",
            },
        ],
    }


def _camera_review_queue() -> list[dict[str, Any]]:
    viewer_only_camera = _camera_entities()[1]
    return [
        {
            "queueId": "review:usgs-ashcam:spurr-overlook",
            "priority": "medium",
            "sourceKey": "usgs-ashcam",
            "camera": viewer_only_camera,
            "issues": [
                {
                    "category": "viewer-feed",
                    "reason": "Viewer-only feed needs image-path verification.",
                    "requiredAction": "Confirm whether the source exposes a direct snapshot URL.",
                }
            ],
            "context": {
                "frameStatus": "viewer-page-only",
                "orientationKind": "unknown",
                "referenceHint": "Mount Spurr",
                "facilityCodeHint": "PASP",
            },
        }
    ]


def _reference_airport_summary() -> dict[str, Any]:
    return {
        "refId": "airport:KAUS",
        "objectType": "airport",
        "canonicalName": "Austin-Bergstrom International Airport",
        "primaryCode": "KAUS",
        "sourceDataset": "ourairports",
        "status": "active",
        "countryCode": "US",
        "admin1Code": "US-TX",
        "centroidLat": 30.1944,
        "centroidLon": -97.6699,
        "coverageTier": "authoritative",
        "objectDisplayLabel": "KAUS",
        "codeContext": "ICAO",
        "aliases": ["AUS", "KAUS", "Austin-Bergstrom"],
    }


def _reference_runway_summary() -> dict[str, Any]:
    return {
        "refId": "runway:KAUS:17R-35L",
        "objectType": "runway",
        "canonicalName": "KAUS runway 17R-35L",
        "primaryCode": "17R/35L",
        "sourceDataset": "ourairports",
        "status": "active",
        "countryCode": "US",
        "admin1Code": "US-TX",
        "centroidLat": 30.1961,
        "centroidLon": -97.6662,
        "coverageTier": "authoritative",
        "objectDisplayLabel": "17R/35L",
        "codeContext": "Runway threshold pair",
        "aliases": ["17R", "35L"],
    }


def _reference_region_summary() -> dict[str, Any]:
    return {
        "refId": "region:city:austin-tx",
        "objectType": "region",
        "canonicalName": "Austin, Texas",
        "primaryCode": "Austin",
        "sourceDataset": "places",
        "status": "active",
        "countryCode": "US",
        "admin1Code": "US-TX",
        "centroidLat": 30.2672,
        "centroidLon": -97.7431,
        "coverageTier": "curated",
        "objectDisplayLabel": "Austin",
        "codeContext": "city",
        "aliases": ["Austin", "Austin, TX"],
    }


def _parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _matches_aircraft(entity: dict[str, Any], **filters: Any) -> bool:
    observed_at = _parse_iso(entity["observedAt"])
    if filters["q"]:
        needle = filters["q"].lower()
        if not any(needle in str(v).lower() for v in [entity["label"], entity["canonicalIds"].get("icao24", ""), entity.get("callsign", "")]):
            return False
    if filters["callsign"] and filters["callsign"].lower() not in str(entity.get("callsign", "")).lower():
        return False
    if filters["icao24"] and filters["icao24"].lower() != str(entity["canonicalIds"].get("icao24", "")).lower():
        return False
    if filters["source"] and filters["source"] != entity["source"]:
        return False
    if filters["status"] and filters["status"] != entity["status"]:
        return False
    if filters["min_altitude"] is not None and entity["altitude"] < filters["min_altitude"]:
        return False
    if filters["max_altitude"] is not None and entity["altitude"] > filters["max_altitude"]:
        return False
    if filters["observed_after"] and observed_at and observed_at < _parse_iso(filters["observed_after"]):
        return False
    if filters["observed_before"] and observed_at and observed_at > _parse_iso(filters["observed_before"]):
        return False
    if filters["recency_seconds"] is not None and observed_at and observed_at < NOW - timedelta(seconds=filters["recency_seconds"]):
        return False
    return True


def _matches_satellite(entity: dict[str, Any], **filters: Any) -> bool:
    observed_at = _parse_iso(entity["observedAt"])
    if filters["q"]:
        needle = filters["q"].lower()
        if not any(needle in str(v).lower() for v in [entity["label"], entity["canonicalIds"].get("norad_id", ""), entity["canonicalIds"].get("object_id", "")]):
            return False
    if filters["norad_id"] is not None and entity.get("noradId") != filters["norad_id"]:
        return False
    if filters["source"] and filters["source"] != entity["source"]:
        return False
    if filters["orbit_class"] and filters["orbit_class"] != entity.get("orbitClass"):
        return False
    if filters["observed_after"] and observed_at and observed_at < _parse_iso(filters["observed_after"]):
        return False
    if filters["observed_before"] and observed_at and observed_at > _parse_iso(filters["observed_before"]):
        return False
    return True


def _earthquake_events() -> list[dict[str, Any]]:
    return [
        {
            "eventId": "us6000fixture1",
            "source": "usgs-earthquake-hazards-program",
            "sourceUrl": "https://earthquake.usgs.gov/earthquakes/eventpage/us6000fixture1",
            "title": "M 5.2 - 110 km SE of Hachijo-jima, Japan",
            "place": "110 km SE of Hachijo-jima, Japan",
            "magnitude": 5.2,
            "magnitudeType": "mww",
            "time": _iso(NOW - timedelta(minutes=12)),
            "updated": _iso(NOW - timedelta(minutes=8)),
            "longitude": 140.826,
            "latitude": 32.273,
            "depthKm": 34.5,
            "status": "reviewed",
            "tsunami": 0,
            "significance": 420,
            "alert": None,
            "felt": 12,
            "cdi": 4.1,
            "mmi": 3.2,
            "eventType": "earthquake",
            "rawProperties": {"fixture": True},
        },
        {
            "eventId": "us6000fixture2",
            "source": "usgs-earthquake-hazards-program",
            "sourceUrl": "https://earthquake.usgs.gov/earthquakes/eventpage/us6000fixture2",
            "title": "M 3.1 - 8 km NE of Pahala, Hawaii",
            "place": "8 km NE of Pahala, Hawaii",
            "magnitude": 3.1,
            "magnitudeType": "ml",
            "time": _iso(NOW - timedelta(minutes=28)),
            "updated": _iso(NOW - timedelta(minutes=20)),
            "longitude": -155.439,
            "latitude": 19.246,
            "depthKm": 31.2,
            "status": "automatic",
            "tsunami": 0,
            "significance": 148,
            "alert": None,
            "felt": 2,
            "cdi": None,
            "mmi": None,
            "eventType": "earthquake",
            "rawProperties": {"fixture": True},
        },
        {
            "eventId": "us6000fixture3",
            "source": "usgs-earthquake-hazards-program",
            "sourceUrl": "https://earthquake.usgs.gov/earthquakes/eventpage/us6000fixture3",
            "title": "M 6.0 - South Sandwich Islands region",
            "place": "South Sandwich Islands region",
            "magnitude": 6.0,
            "magnitudeType": "mww",
            "time": _iso(NOW - timedelta(minutes=45)),
            "updated": _iso(NOW - timedelta(minutes=37)),
            "longitude": -26.731,
            "latitude": -57.892,
            "depthKm": 10.0,
            "status": "reviewed",
            "tsunami": 1,
            "significance": 556,
            "alert": "green",
            "felt": None,
            "cdi": None,
            "mmi": None,
            "eventType": "earthquake",
            "rawProperties": {"fixture": True},
        },
    ]


app = FastAPI(title="Aircraft/Satellite Smoke Fixture API")

if (CLIENT_DIST / "assets").exists():
    app.mount("/assets", StaticFiles(directory=CLIENT_DIST / "assets"), name="assets")
if (CLIENT_DIST / "cesium").exists():
    app.mount("/cesium", StaticFiles(directory=CLIENT_DIST / "cesium"), name="cesium")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/config/public")
async def public_config() -> dict[str, Any]:
    return {
        "appName": "WorldView Spatial Console",
        "environment": "smoke-fixture",
        "tiles": {
            "provider": "cesium-world-terrain",
            "googleTilesEnabled": False,
            "fallbackEnabled": True,
            "googleMapsApiKey": None,
        },
        "features": {
            "aircraft": True,
            "satellites": True,
            "cameras": True,
            "marine": True,
            "visualModes": True,
        },
        "planet": build_planet_config().model_dump(by_alias=True),
    }


@app.get("/api/status/sources")
async def source_status() -> dict[str, Any]:
    return {
        "sources": [
            {
                "name": "terrain",
                "state": "healthy",
                "enabled": True,
                "healthy": True,
                "freshnessSeconds": None,
                "staleAfterSeconds": None,
                "lastSuccessAt": None,
                "degradedReason": None,
                "rateLimited": False,
                "hiddenReason": None,
                "detail": "Fixture terrain ready.",
                "credentialsConfigured": True,
                "blockedReason": None,
                "reviewRequired": False,
                "lastAttemptAt": None,
                "lastFailureAt": None,
                "successCount": 1,
                "failureCount": 0,
                "warningCount": 0,
            },
            {
                "name": "aircraft",
                "state": "stale",
                "enabled": True,
                "healthy": False,
                "freshnessSeconds": 15,
                "staleAfterSeconds": 120,
                "lastSuccessAt": _iso(NOW - timedelta(minutes=4)),
                "degradedReason": "Fixture stale aircraft source for banner validation.",
                "rateLimited": False,
                "hiddenReason": None,
                "detail": "Aircraft source is intentionally stale in smoke mode.",
                "credentialsConfigured": True,
                "blockedReason": None,
                "reviewRequired": False,
                "lastAttemptAt": _iso(NOW - timedelta(minutes=1)),
                "lastFailureAt": _iso(NOW - timedelta(minutes=1)),
                "successCount": 3,
                "failureCount": 1,
                "warningCount": 1,
            },
            {
                "name": "satellites",
                "state": "healthy",
                "enabled": True,
                "healthy": True,
                "freshnessSeconds": 900,
                "staleAfterSeconds": 43200,
                "lastSuccessAt": _iso(NOW),
                "degradedReason": None,
                "rateLimited": False,
                "hiddenReason": None,
                "detail": "Satellite source healthy in fixture mode.",
                "credentialsConfigured": True,
                "blockedReason": None,
                "reviewRequired": False,
                "lastAttemptAt": _iso(NOW),
                "lastFailureAt": None,
                "successCount": 4,
                "failureCount": 0,
                "warningCount": 0,
            },
            {
                "name": "google-photorealistic-3d",
                "state": "disabled",
                "enabled": False,
                "healthy": False,
                "freshnessSeconds": None,
                "staleAfterSeconds": None,
                "lastSuccessAt": None,
                "degradedReason": "Google tiles are not configured.",
                "rateLimited": False,
                "hiddenReason": "disabled-by-configuration",
                "detail": "Fixture disables Google tiles.",
                "credentialsConfigured": False,
                "blockedReason": None,
                "reviewRequired": False,
                "lastAttemptAt": None,
                "lastFailureAt": None,
                "successCount": 0,
                "failureCount": 0,
                "warningCount": 0,
            },
            {
                "name": "earthquakes",
                "state": "healthy",
                "enabled": True,
                "healthy": True,
                "freshnessSeconds": 60,
                "staleAfterSeconds": 300,
                "lastSuccessAt": _iso(NOW - timedelta(seconds=30)),
                "degradedReason": None,
                "rateLimited": False,
                "hiddenReason": None,
                "detail": "USGS earthquake fixture feed.",
                "credentialsConfigured": True,
                "blockedReason": None,
                "reviewRequired": False,
                "lastAttemptAt": _iso(NOW - timedelta(seconds=35)),
                "lastFailureAt": None,
                "successCount": 5,
                "failureCount": 0,
                "warningCount": 0,
            },
            *_camera_source_status(),
        ]
    }


@app.get("/api/events/earthquakes/recent")
async def events_earthquakes_recent(
    min_magnitude: float | None = Query(default=None),
    limit: int = Query(default=300),
    sort: str = Query(default="newest"),
    window: str = Query(default="day"),
) -> dict[str, Any]:
    del window
    events = _earthquake_events()
    if min_magnitude is not None:
        events = [event for event in events if event["magnitude"] is not None and event["magnitude"] >= min_magnitude]
    if sort == "magnitude":
        events.sort(key=lambda event: event["magnitude"] or -999, reverse=True)
    else:
        events.sort(key=lambda event: event["time"], reverse=True)
    events = events[:limit]
    return {
        "metadata": {
            "source": "usgs-earthquake-hazards-program",
            "feedName": "all_day",
            "feedUrl": "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson",
            "generatedAt": _iso(NOW - timedelta(seconds=40)),
            "fetchedAt": _iso(NOW),
            "count": len(events),
            "caveat": "USGS magnitude and location are source-reported metadata; marker styling is visual prioritization only and does not imply damage."
        },
        "count": len(events),
        "events": events,
    }


@app.get("/api/cameras")
async def cameras(
    limit: int = Query(default=500),
    q: str | None = Query(default=None),
    source: str | None = Query(default=None),
    review_status: str | None = Query(default=None),
    coordinate_kind: str | None = Query(default=None),
    active_only: bool = Query(default=True),
) -> dict[str, Any]:
    cameras = _camera_entities()
    filtered: list[dict[str, Any]] = []
    for camera in cameras:
        if active_only and camera["status"] != "active":
            continue
        if source and camera["source"] != source:
            continue
        if review_status and camera["review"]["status"] != review_status:
            continue
        if coordinate_kind and camera["position"]["kind"] != coordinate_kind:
            continue
        if q:
            needle = q.lower()
            haystacks = [
                camera["label"],
                camera.get("sourceCameraId", ""),
                camera.get("locationDescription", ""),
                camera.get("referenceHintText", ""),
                camera.get("facilityCodeHint", ""),
            ]
            if not any(needle in str(value).lower() for value in haystacks):
                continue
        filtered.append(camera)
    filtered = filtered[:limit]
    return {
        "fetchedAt": _iso(NOW),
        "source": "camera-fixture",
        "count": len(filtered),
        "summary": {
            "activeFilters": {
                key: str(value)
                for key, value in {
                    "q": q,
                    "source": source,
                    "review_status": review_status,
                    "coordinate_kind": coordinate_kind,
                }.items()
                if value not in (None, "")
            },
            "filteredCount": len(filtered),
            "totalCandidates": len(cameras),
            "stalenessWarning": None,
        },
        "cameras": filtered,
        "sources": _camera_sources(),
    }


@app.get("/api/cameras/sources")
async def camera_sources() -> dict[str, Any]:
    return {"sources": _camera_sources()}


@app.get("/api/cameras/source-inventory")
async def camera_source_inventory() -> dict[str, Any]:
    return _camera_source_inventory()


@app.get("/api/cameras/review-queue")
async def camera_review_queue(limit: int = Query(default=50)) -> dict[str, Any]:
    items = _camera_review_queue()[:limit]
    return {
        "fetchedAt": _iso(NOW),
        "count": len(items),
        "items": items,
    }


@app.get("/api/aircraft")
async def aircraft(
    lamin: float = Query(...),
    lamax: float = Query(...),
    lomin: float = Query(...),
    lomax: float = Query(...),
    limit: int = Query(default=100),
    q: str | None = Query(default=None),
    callsign: str | None = Query(default=None),
    icao24: str | None = Query(default=None),
    source: str | None = Query(default=None),
    status: str | None = Query(default=None),
    observed_after: str | None = Query(default=None),
    observed_before: str | None = Query(default=None),
    recency_seconds: int | None = Query(default=None),
    min_altitude: float | None = Query(default=None),
    max_altitude: float | None = Query(default=None),
) -> dict[str, Any]:
    all_entities = _aircraft_entities()
    filtered = [
        entity
        for entity in all_entities
        if _matches_aircraft(
            entity,
            q=q,
            callsign=callsign,
            icao24=icao24,
            source=source,
            status=status,
            observed_after=observed_after,
            observed_before=observed_before,
            recency_seconds=recency_seconds,
            min_altitude=min_altitude,
            max_altitude=max_altitude,
        )
    ][:limit]
    return {
        "fetchedAt": _iso(NOW),
        "source": "opensky-network",
        "count": len(filtered),
        "summary": {
            "activeFilters": {
                key: str(value)
                for key, value in {
                    "viewport": f"{min(lamin, lamax):.4f},{max(lamin, lamax):.4f},{min(lomin, lomax):.4f},{max(lomin, lomax):.4f}",
                    "q": q,
                    "callsign": callsign,
                    "icao24": icao24,
                    "source": source,
                    "status": status,
                    "observed_after": observed_after,
                    "observed_before": observed_before,
                    "recency_seconds": recency_seconds,
                    "min_altitude": min_altitude,
                    "max_altitude": max_altitude,
                }.items()
                if value not in (None, "")
            },
            "totalCandidates": len(all_entities),
            "filteredCount": len(filtered),
            "stalenessWarning": "Aircraft source intentionally stale in fixture mode.",
        },
        "aircraft": filtered,
    }


@app.get("/api/satellites")
async def satellites(
    limit: int = Query(default=40),
    q: str | None = Query(default=None),
    norad_id: int | None = Query(default=None),
    source: str | None = Query(default=None),
    observed_after: str | None = Query(default=None),
    observed_before: str | None = Query(default=None),
    orbit_class: str | None = Query(default=None),
    include_paths: bool = Query(default=True),
    include_pass_window: bool = Query(default=False),
) -> dict[str, Any]:
    entities, orbit_paths, pass_windows = _satellite_entities()
    filtered = [
        entity
        for entity in entities
        if _matches_satellite(
            entity,
            q=q,
            norad_id=norad_id,
            source=source,
            observed_after=observed_after,
            observed_before=observed_before,
            orbit_class=orbit_class,
        )
    ][:limit]
    filtered_orbits = {entity["id"]: orbit_paths[entity["id"]] for entity in filtered if include_paths}
    filtered_pass = {entity["id"]: pass_windows[entity["id"]] for entity in filtered if include_pass_window}
    return {
        "fetchedAt": _iso(NOW),
        "source": "celestrak-active",
        "count": len(filtered),
        "summary": {
            "activeFilters": {
                key: str(value)
                for key, value in {
                    "q": q,
                    "norad_id": norad_id,
                    "source": source,
                    "observed_after": observed_after,
                    "observed_before": observed_before,
                    "orbit_class": orbit_class,
                    "include_paths": include_paths,
                    "include_pass_window": include_pass_window,
                }.items()
                if value not in (None, "")
            },
            "totalCandidates": len(entities),
            "filteredCount": len(filtered),
            "stalenessWarning": None,
        },
        "satellites": filtered,
        "orbitPaths": filtered_orbits,
        "passWindows": filtered_pass,
    }


@app.get("/api/marine/vessels")
async def marine_vessels(limit: int = Query(default=50)) -> dict[str, Any]:
    vessels = [
        {
            "id": "vessel:mmsi:123456789",
            "type": "marine-vessel",
            "source": "ais-fixture-global",
            "label": "SUSPECT RUNNER",
            "latitude": 1.2,
            "longitude": 103.8,
            "altitude": 0.0,
            "heading": 89.0,
            "speed": 12.4,
            "timestamp": _iso(NOW),
            "observedAt": _iso(NOW),
            "fetchedAt": _iso(NOW),
            "status": "under-way-using-engine",
            "sourceDetail": "Fixture marine feed",
            "externalUrl": None,
            "confidence": 0.82,
            "historyAvailable": True,
            "canonicalIds": {"mmsi": "123456789", "vesselId": "vessel:mmsi:123456789"},
            "rawIdentifiers": {"imo": "", "callsign": ""},
            "quality": {"score": 0.82, "label": "estimated", "sourceFreshnessSeconds": 60, "notes": []},
            "derivedFields": [],
            "historySummary": None,
            "linkTargets": [],
            "metadata": {},
            "mmsi": "123456789",
            "imo": None,
            "callsign": None,
            "vesselName": "SUSPECT RUNNER",
            "flagState": "PA",
            "vesselClass": "cargo",
            "course": 88.0,
            "navStatus": "under-way-using-engine",
            "destination": "SGSIN",
            "eta": None,
            "stale": False,
            "degraded": False,
            "degradedReason": None,
            "sourceHealth": "healthy",
            "observedVsDerived": "observed",
            "geometryProvenance": "raw_observed",
            "referenceRefId": None,
        }
    ][:limit]
    return {
        "fetchedAt": _iso(NOW),
        "source": "ais-fixture-global",
        "count": len(vessels),
        "summary": {"activeFilters": {}, "totalCandidates": len(vessels), "filteredCount": len(vessels), "stalenessWarning": None},
        "vessels": vessels,
        "sources": [
            {
                "sourceKey": "ais-fixture-global",
                "displayName": "AIS Fixture Global",
                "enabled": True,
                "state": "healthy",
                "detail": "Fixture marine source.",
                "providerKind": "fixture",
                "coverageScope": "regional",
                "globalCoverageClaimed": False,
                "assumptions": ["Fixture only"],
                "limitations": ["Not real-time global AIS"],
            }
        ],
    }


@app.get("/api/marine/vessels/{vessel_id}/summary")
async def marine_vessel_summary(vessel_id: str) -> dict[str, Any]:
    sparse = "sparse" in vessel_id.lower()
    degraded = "degraded" in vessel_id.lower()
    return {
        "fetchedAt": _iso(NOW),
        "vesselId": vessel_id,
        "window": {"startAt": _iso(NOW - timedelta(hours=6)), "endAt": _iso(NOW), "observedPointCount": 6},
        "latestObserved": None,
        "movement": {
            "observedPointCount": 6,
            "distanceMovedM": 120000.0 if not sparse else 1200.0,
            "averageSpeedKts": 12.1 if not sparse else 0.4,
            "observedStartAt": _iso(NOW - timedelta(hours=6)),
            "observedEndAt": _iso(NOW),
        },
        "observedGapEventCount": 3 if not sparse else 1,
        "suspiciousGapEventCount": 2 if not sparse else 0,
        "longestGapSeconds": 7200 if not sparse else 300,
        "mostRecentResumedObservation": None,
        "sourceStatus": {"sourceKey": "ais-fixture-global", "displayName": "AIS Fixture", "enabled": True, "state": "degraded" if degraded else "healthy", "detail": "fixture"},
        "anomaly": {
            "score": 74.0 if not sparse and not degraded else (28.0 if sparse else 52.0),
            "level": "high" if not sparse and not degraded else ("low" if sparse else "medium"),
            "priorityRank": 1 if not sparse else 3,
            "displayLabel": "Notable activity",
            "reasons": ["suspicious gap intervals observed"] if not sparse else ["sparse reporting plausible"],
            "caveats": ["source health degraded/stale; anomaly confidence reduced"] if degraded else (["sparse reporting plausibility reduced anomaly priority"] if sparse else []),
            "observedSignals": ["observed-signal-gap-start", "resumed-observation"],
            "inferredSignals": ["possible-transponder-silence-interval"],
            "scoredSignals": ["suspicious_gap_count", "source_health_penalty"],
        },
        "observedFields": ["observedGapEventCount"],
        "inferredFields": ["suspiciousGapEventCount"],
    }


@app.get("/api/marine/replay/viewport/summary")
async def marine_viewport_summary() -> dict[str, Any]:
    return {
        "fetchedAt": _iso(NOW),
        "atOrBefore": _iso(NOW),
        "window": {"startAt": _iso(NOW - timedelta(hours=1)), "endAt": _iso(NOW), "observedPointCount": 4},
        "vesselCount": 4,
        "activeVesselCount": 3,
        "observedGapEventCount": 5,
        "suspiciousGapEventCount": 2,
        "viewportEntryCount": 2,
        "viewportExitCount": 1,
        "anomaly": {
            "score": 63.0,
            "level": "medium",
            "priorityRank": None,
            "displayLabel": "Attention priority",
            "reasons": ["suspicious-gap density 0.50 per vessel"],
            "caveats": ["low-sample viewport window"],
            "observedSignals": ["observed_gap_event_count", "viewport_entry_count"],
            "inferredSignals": ["suspicious_gap_density"],
            "scoredSignals": ["suspicious_gap_density", "entry_exit_churn"],
        },
        "observedFields": ["vesselCount", "observedGapEventCount"],
        "inferredFields": ["suspiciousGapEventCount"],
    }


@app.get("/api/marine/replay/chokepoint/summary")
async def marine_chokepoint_summary() -> dict[str, Any]:
    slices = [
        {
            "sliceStartAt": _iso(NOW - timedelta(minutes=60)),
            "sliceEndAt": _iso(NOW - timedelta(minutes=40)),
            "vesselCount": 6,
            "activeVesselCount": 5,
            "observedGapEventCount": 4,
            "suspiciousGapEventCount": 3,
            "anomaly": {
                "score": 78.0,
                "level": "high",
                "priorityRank": 1,
                "displayLabel": "High slice anomaly",
                "reasons": ["suspicious-gap density 0.50"],
                "caveats": [],
                "observedSignals": ["observed_gap_event_count"],
                "inferredSignals": ["suspicious_gap_density"],
                "scoredSignals": ["suspicious_gap_density"],
            },
        },
        {
            "sliceStartAt": _iso(NOW - timedelta(minutes=40)),
            "sliceEndAt": _iso(NOW - timedelta(minutes=20)),
            "vesselCount": 5,
            "activeVesselCount": 3,
            "observedGapEventCount": 2,
            "suspiciousGapEventCount": 1,
            "anomaly": {
                "score": 51.0,
                "level": "medium",
                "priorityRank": 2,
                "displayLabel": "Medium slice anomaly",
                "reasons": ["observed gap concentration increased"],
                "caveats": [],
                "observedSignals": ["observed_gap_event_count"],
                "inferredSignals": ["suspicious_gap_density"],
                "scoredSignals": ["observed_gap_count"],
            },
        },
    ]
    return {
        "fetchedAt": _iso(NOW),
        "startAt": _iso(NOW - timedelta(hours=2)),
        "endAt": _iso(NOW),
        "sliceMinutes": 20,
        "sliceCount": len(slices),
        "totalVesselObservations": 11,
        "totalObservedGapEvents": 6,
        "totalSuspiciousGapEvents": 4,
        "anomaly": {
            "score": 69.0,
            "level": "high",
            "priorityRank": None,
            "displayLabel": "High chokepoint anomaly",
            "reasons": ["total suspicious-gap events: 4"],
            "caveats": [],
            "observedSignals": ["total_observed_gap_events"],
            "inferredSignals": ["total_suspicious_gap_events"],
            "scoredSignals": ["suspicious_gap_density"],
        },
        "slices": slices,
        "observedFields": ["totalObservedGapEvents"],
        "inferredFields": ["totalSuspiciousGapEvents"],
    }


@app.get("/api/reference/link/aircraft")
async def reference_link_aircraft(
    lat: float = Query(...),
    lon: float = Query(...),
    heading_deg: float | None = Query(default=None),
    q: str | None = Query(default=None),
    external_system: str | None = Query(default=None),
    external_object_id: str | None = Query(default=None),
    limit: int = Query(default=5),
) -> dict[str, Any]:
    del lat, lon, heading_deg, q, external_system, external_object_id, limit
    return {
        "externalObjectType": "aircraft",
        "count": 1,
        "primary": {
            "summary": _reference_airport_summary(),
            "confidence": 0.91,
            "method": "fixture-spatial-match",
            "reason": "Within airport influence radius of KAUS.",
            "score": 0.91,
            "confidenceBreakdown": {"spatial": 0.72, "heading": 0.19},
        },
        "alternatives": [],
        "persistedLinks": [],
        "context": {
            "containingRegions": [_reference_region_summary()],
            "nearestAirport": _reference_airport_summary(),
            "nearestPlace": _reference_region_summary(),
        },
        "results": [
            {
                "summary": _reference_airport_summary(),
                "confidence": 0.91,
                "method": "fixture-spatial-match",
                "reason": "Within airport influence radius of KAUS.",
                "score": 0.91,
                "confidenceBreakdown": {"spatial": 0.72, "heading": 0.19},
            }
        ],
    }


@app.get("/api/reference/nearest/airport")
async def reference_nearest_airport(
    lat: float = Query(...),
    lon: float = Query(...),
    country: str | None = Query(default=None),
    limit: int = Query(default=1),
) -> dict[str, Any]:
    del lat, lon, country, limit
    return {
        "latitude": 30.2672,
        "longitude": -97.7431,
        "radiusM": 50000,
        "count": 1,
        "results": [
            {
                "summary": _reference_airport_summary(),
                "distanceM": 9230.0,
                "bearingDeg": 102.0,
                "geometryMethod": "centroid",
            }
        ],
    }


@app.get("/api/reference/nearest/runway-threshold")
async def reference_nearest_runway(
    lat: float = Query(...),
    lon: float = Query(...),
    heading_deg: float | None = Query(default=None),
    airport_ref_id: str | None = Query(default=None),
    limit: int = Query(default=1),
) -> dict[str, Any]:
    del lat, lon, heading_deg, airport_ref_id, limit
    return {
        "latitude": 30.2672,
        "longitude": -97.7431,
        "radiusM": 8000,
        "count": 1,
        "results": [
            {
                "summary": _reference_runway_summary(),
                "distanceM": 7810.0,
                "bearingDeg": 109.0,
                "geometryMethod": "segment",
            }
        ],
    }


@app.get("/")
async def app_index() -> FileResponse:
    return FileResponse(CLIENT_DIST / "index.html")


@app.get("/{full_path:path}")
async def app_routes(full_path: str) -> FileResponse:
    candidate = (CLIENT_DIST / full_path).resolve()
    if candidate.is_file() and CLIENT_DIST in candidate.parents:
        return FileResponse(candidate)
    return FileResponse(CLIENT_DIST / "index.html")
