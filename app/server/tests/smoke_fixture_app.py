from __future__ import annotations

import json
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
SERVER_DATA = Path(__file__).resolve().parents[1] / "data"


def _load_json_fixture(name: str) -> dict[str, Any]:
    return json.loads((SERVER_DATA / name).read_text(encoding="utf-8"))


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
            "nearestReferenceRefId": "volcano:akutan",
            "referenceLinkStatus": "reviewed",
            "linkCandidateCount": 1,
            "referenceHintText": "Akutan Volcano",
            "facilityCodeHint": "PAUT",
        },
        {
            "id": "camera:usgs-ashcam:akutan-ridge",
            "type": "camera",
            "source": "usgs-ashcam",
            "label": "Akutan Ridge",
            "latitude": 54.1418,
            "longitude": -165.9812,
            "altitude": 0.0,
            "heading": 58.0,
            "speed": None,
            "timestamp": _iso(NOW - timedelta(seconds=52)),
            "observedAt": _iso(NOW - timedelta(seconds=52)),
            "fetchedAt": _iso(NOW),
            "status": "active",
            "sourceDetail": "USGS AshCam official webcam catalog",
            "externalUrl": "https://www.avo.alaska.edu/webcam/akutan.php",
            "confidence": 0.95,
            "historyAvailable": False,
            "canonicalIds": {"camera_id": "akutan-ridge"},
            "rawIdentifiers": {"volcano": "Akutan"},
            "quality": {
                "score": 0.95,
                "label": "official",
                "sourceFreshnessSeconds": 52,
                "notes": ["Fixture Ashcam direct-image cluster member"],
            },
            "derivedFields": [],
            "historySummary": None,
            "linkTargets": [],
            "metadata": {"catalogSource": "fixture-ashcam"},
            "cameraId": "akutan-ridge",
            "sourceCameraId": "akutan-ridge",
            "owner": "U.S. Geological Survey",
            "state": "AK",
            "county": "Aleutians East Borough",
            "region": "Aleutians",
            "roadway": None,
            "direction": "ENE",
            "locationDescription": "Akutan summit ridge view",
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
                "degrees": 58.0,
                "cardinalDirection": "ENE",
                "confidence": 1.0,
                "source": "official",
                "isPtz": False,
                "notes": [],
            },
            "frame": {
                "status": "live",
                "refreshIntervalSeconds": 60,
                "lastFrameAt": _iso(NOW - timedelta(seconds=40)),
                "ageSeconds": 40,
                "imageUrl": "https://avo.alaska.edu/images/ashcam/akutan/ridge.jpg",
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
            "lastMetadataRefreshAt": _iso(NOW - timedelta(seconds=58)),
            "nextFrameRefreshAt": _iso(NOW + timedelta(seconds=22)),
            "backoffUntil": None,
            "retryCount": 0,
            "lastHttpStatus": 200,
            "nearestReferenceRefId": None,
            "referenceLinkStatus": "suggested",
            "linkCandidateCount": 2,
            "referenceHintText": "Akutan Volcano",
            "facilityCodeHint": "PAUT",
        },
        {
            "id": "camera:usgs-ashcam:akutan-harbor",
            "type": "camera",
            "source": "usgs-ashcam",
            "label": "Akutan Harbor",
            "latitude": 54.1399,
            "longitude": -165.9759,
            "altitude": 0.0,
            "heading": None,
            "speed": None,
            "timestamp": _iso(NOW - timedelta(minutes=3)),
            "observedAt": _iso(NOW - timedelta(minutes=3)),
            "fetchedAt": _iso(NOW),
            "status": "active",
            "sourceDetail": "USGS AshCam official webcam catalog",
            "externalUrl": "https://www.avo.alaska.edu/webcam/akutan.php",
            "confidence": 0.74,
            "historyAvailable": False,
            "canonicalIds": {"camera_id": "akutan-harbor"},
            "rawIdentifiers": {"volcano": "Akutan"},
            "quality": {
                "score": 0.74,
                "label": "viewer-only",
                "sourceFreshnessSeconds": 180,
                "notes": ["Fixture Ashcam clustered viewer-only camera"],
            },
            "derivedFields": [],
            "historySummary": None,
            "linkTargets": [],
            "metadata": {"catalogSource": "fixture-ashcam"},
            "cameraId": "akutan-harbor",
            "sourceCameraId": "akutan-harbor",
            "owner": "U.S. Geological Survey",
            "state": "AK",
            "county": "Aleutians East Borough",
            "region": "Aleutians",
            "roadway": None,
            "direction": None,
            "locationDescription": "Akutan harbor overlook viewer page",
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
                "viewerUrl": "https://www.avo.alaska.edu/webcam/akutan.php",
                "width": None,
                "height": None,
            },
            "compliance": {
                "attributionText": "USGS Alaska Volcano Observatory",
                "attributionUrl": "https://www.avo.alaska.edu/webcam/akutan.php",
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
                "requiredActions": ["Confirm whether the source exposes a direct snapshot URL."],
                "issueCategories": ["viewer-feed"],
            },
            "healthState": "degraded",
            "degradedReason": "Viewer page available but no trusted direct snapshot URL.",
            "lastMetadataRefreshAt": _iso(NOW - timedelta(minutes=4)),
            "nextFrameRefreshAt": _iso(NOW + timedelta(minutes=5)),
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
            "referenceLinkStatus": None,
            "linkCandidateCount": None,
            "referenceHintText": None,
            "facilityCodeHint": None,
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
        "count": 5,
        "summary": {
            "totalSources": 5,
            "activeSources": 1,
            "credentialedSources": 1,
            "credentiallessSources": 4,
            "directImageSources": 3,
            "viewerOnlySources": 1,
            "validatedSources": 1,
            "lowYieldSources": 0,
            "poorQualitySources": 0,
            "sourcesByType": {
                "public-webcam-api": 1,
                "official-dot-api": 2,
                "public-camera-page": 2,
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
                "endpointVerificationStatus": "machine-readable-confirmed",
                "candidateEndpointUrl": "https://volcview.wr.usgs.gov/ashcam-api/webcamApi/webcams",
                "machineReadableEndpointUrl": "https://volcview.wr.usgs.gov/ashcam-api/webcamApi/webcams",
                "lastEndpointCheckAt": _iso(NOW - timedelta(days=1)),
                "lastEndpointHttpStatus": 200,
                "lastEndpointContentType": "application/json",
                "lastEndpointResult": "Official public JSON endpoint confirmed.",
                "lastEndpointNotes": ["Structured no-auth API verified."],
                "verificationCaveat": "Machine-readable endpoint status does not expand frame-storage rights.",
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
                "endpointVerificationStatus": "blocked",
                "candidateEndpointUrl": "https://wsdot.com/traffic/api/",
                "machineReadableEndpointUrl": None,
                "lastEndpointCheckAt": None,
                "lastEndpointHttpStatus": None,
                "lastEndpointContentType": None,
                "lastEndpointResult": "Endpoint family is known, but credentials are required in fixture mode.",
                "lastEndpointNotes": ["Credentialed official API; no no-auth candidate workflow applies."],
                "verificationCaveat": None,
            },
            {
                "key": "finland-digitraffic-road-cameras",
                "sourceName": "Finland Digitraffic Road Weather Cameras",
                "sourceFamily": "official-dot-candidate",
                "sourceType": "official-dot-api",
                "accessMethod": "json-api",
                "onboardingState": "candidate",
                "owner": "Fintraffic / Digitraffic",
                "authentication": "none",
                "credentialsConfigured": True,
                "rateLimitNotes": ["Fixture-first sandbox connector only. No scheduled ingest."],
                "coverageGeography": "Finland road weather camera stations",
                "coverageStates": [],
                "coverageRegions": ["Finland"],
                "providesExactCoordinates": True,
                "providesDirectionText": False,
                "providesNumericHeading": False,
                "providesDirectImage": True,
                "providesViewerOnly": False,
                "supportsEmbed": False,
                "supportsStorage": False,
                "compliance": _camera_entities()[1]["compliance"],
                "sourceQualityNotes": ["Machine-readable endpoint verified; fixture-first connector implemented."],
                "sourceStabilityNotes": ["Sandbox connector proves mapping only and remains candidate-only."],
                "blockedReason": "Candidate only until fixture mapping, source-health review, and compliance review are completed.",
                "approximateCameraCount": 470,
                "importReadiness": "inventory-only",
                "discoveredCameraCount": 2,
                "usableCameraCount": 1,
                "directImageCameraCount": 1,
                "viewerOnlyCameraCount": 0,
                "missingCoordinateCameraCount": 0,
                "uncertainOrientationCameraCount": 2,
                "reviewQueueCount": 2,
                "lastCatalogImportAt": _iso(NOW - timedelta(minutes=20)),
                "lastCatalogImportStatus": "needs-review",
                "lastCatalogImportDetail": "Sandbox fixture import completed through explicit validation-style refresh.",
                "lastImportOutcome": "needs-review",
                "pageStructure": None,
                "likelyCameraCount": 470,
                "complianceRisk": "low",
                "extractionFeasibility": "high",
                "endpointVerificationStatus": "machine-readable-confirmed",
                "candidateEndpointUrl": "https://tie.digitraffic.fi/api/weathercam/v1/stations",
                "machineReadableEndpointUrl": "https://tie.digitraffic.fi/api/weathercam/v1/stations",
                "lastEndpointCheckAt": _iso(NOW - timedelta(days=1)),
                "lastEndpointHttpStatus": 200,
                "lastEndpointContentType": "application/json",
                "lastEndpointResult": "Official Digitraffic weather camera station API confirmed as machine-readable JSON.",
                "lastEndpointNotes": ["Machine-readable endpoint confirmed from official docs."],
                "verificationCaveat": "Machine-readable endpoint status alone does not validate the source for production ingest.",
                "sandboxImportAvailable": True,
                "sandboxImportMode": "fixture",
                "sandboxConnectorId": "FinlandDigitrafficWeatherCamConnector",
                "lastSandboxImportAt": _iso(NOW - timedelta(minutes=20)),
                "lastSandboxImportOutcome": "needs-review",
                "sandboxDiscoveredCount": 2,
                "sandboxUsableCount": 1,
                "sandboxReviewQueueCount": 2,
                "sandboxValidationCaveat": "Sandbox fixture import proves mapping only. It does not mark the source validated or enable scheduled ingestion.",
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
                "endpointVerificationStatus": "needs-review",
                "candidateEndpointUrl": "https://weathercams.faa.gov/",
                "machineReadableEndpointUrl": None,
                "lastEndpointCheckAt": _iso(NOW - timedelta(days=1)),
                "lastEndpointHttpStatus": 200,
                "lastEndpointContentType": "text/html",
                "lastEndpointResult": "Public FAA site is reachable, but no stable machine-readable endpoint is verified.",
                "lastEndpointNotes": [
                    "Candidate URL only.",
                    "Do not scrape the interactive app."
                ],
                "verificationCaveat": "Candidate URL reachability does not imply a compliant ingest path.",
            },
            {
                "key": "minnesota-511-public-arcgis",
                "sourceName": "Minnesota 511 Public Endpoint Candidate",
                "sourceFamily": "511-public-endpoint-candidate",
                "sourceType": "public-camera-page",
                "accessMethod": "html-index",
                "onboardingState": "candidate",
                "owner": "Minnesota DOT / 511MN",
                "authentication": "none",
                "credentialsConfigured": True,
                "rateLimitNotes": ["Candidate only; do not poll the interactive app."],
                "coverageGeography": "Minnesota statewide 511 cameras and weather operations candidate",
                "coverageStates": ["MN"],
                "coverageRegions": ["Minnesota"],
                "providesExactCoordinates": False,
                "providesDirectionText": False,
                "providesNumericHeading": False,
                "providesDirectImage": False,
                "providesViewerOnly": False,
                "supportsEmbed": False,
                "supportsStorage": False,
                "compliance": _camera_entities()[1]["compliance"],
                "sourceQualityNotes": ["Potentially high-value if a stable public endpoint is verified."],
                "sourceStabilityNotes": ["Interactive public app is not treated as an API."],
                "blockedReason": "Needs verification. Gather registry did not confirm a stable public no-auth machine endpoint. Do not scrape the interactive web app.",
                "approximateCameraCount": None,
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
                "lastCatalogImportDetail": "Endpoint verification metadata only. No import path is active.",
                "lastImportOutcome": None,
                "pageStructure": "interactive-map-html",
                "likelyCameraCount": None,
                "complianceRisk": "medium",
                "extractionFeasibility": "low",
                "endpointVerificationStatus": "needs-review",
                "candidateEndpointUrl": "https://511mn.org/",
                "machineReadableEndpointUrl": None,
                "lastEndpointCheckAt": _iso(NOW - timedelta(days=1)),
                "lastEndpointHttpStatus": 200,
                "lastEndpointContentType": "text/html",
                "lastEndpointResult": "Only the public site URL is verified. No stable public no-auth machine endpoint is confirmed.",
                "lastEndpointNotes": [
                    "Candidate URL only.",
                    "Do not scrape the interactive app."
                ],
                "verificationCaveat": "Interactive web app availability is not evidence of a stable backend endpoint.",
            },
        ],
    }


def _camera_review_queue() -> list[dict[str, Any]]:
    viewer_only_camera = _camera_entities()[2]
    return [
        {
            "queueId": "review:usgs-ashcam:akutan-harbor",
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
                "referenceHint": "Akutan Volcano",
                "facilityCodeHint": "PAUT",
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


def _aviation_weather_context() -> dict[str, Any]:
    return {
        "fetchedAt": _iso(NOW),
        "source": "noaa-awc",
        "sourceDetail": "NOAA Aviation Weather Center Data API",
        "contextType": "nearest-airport",
        "airportCode": "KAUS",
        "airportName": "Austin-Bergstrom International Airport",
        "airportRefId": "airport:KAUS",
        "metar": {
            "stationId": "KAUS",
            "stationName": "Austin Bergstrom Intl",
            "receiptTime": _iso(NOW - timedelta(minutes=2)),
            "observedAt": _iso(NOW - timedelta(minutes=7)),
            "reportAt": _iso(NOW - timedelta(minutes=5)),
            "rawText": "METAR KAUS 041155Z 17008KT 10SM FEW035 SCT120 22/16 A3008 RMK AO2",
            "flightCategory": "VFR",
            "visibility": "10",
            "windDirection": "170",
            "windSpeedKt": 8,
            "temperatureC": 22.0,
            "dewpointC": 16.0,
            "altimeterHpa": 1018.0,
            "latitude": 30.1945,
            "longitude": -97.6699,
            "cloudLayers": [
                {"cover": "FEW", "baseFtAgl": 3500, "cloudType": None},
                {"cover": "SCT", "baseFtAgl": 12000, "cloudType": None},
            ],
        },
        "taf": {
            "stationId": "KAUS",
            "stationName": "Austin Bergstrom Intl",
            "issueTime": _iso(NOW - timedelta(hours=1)),
            "bulletinTime": _iso(NOW - timedelta(hours=1)),
            "validFrom": _iso(NOW),
            "validTo": _iso(NOW + timedelta(hours=24)),
            "rawText": "TAF KAUS 041120Z 0412/0512 16008KT P6SM SCT040 FM041800 17012KT P6SM BKN050 PROB30 0502/0506 4SM TSRA BKN035CB",
            "forecastPeriods": [
                {
                    "validFrom": _iso(NOW),
                    "validTo": _iso(NOW + timedelta(hours=6)),
                    "changeIndicator": None,
                    "probabilityPercent": None,
                    "windDirection": "160",
                    "windSpeedKt": 8,
                    "visibility": "6+",
                    "weather": None,
                    "cloudLayers": [{"cover": "SCT", "baseFtAgl": 4000, "cloudType": None}],
                },
                {
                    "validFrom": _iso(NOW + timedelta(hours=6)),
                    "validTo": _iso(NOW + timedelta(hours=14)),
                    "changeIndicator": "FM",
                    "probabilityPercent": None,
                    "windDirection": "170",
                    "windSpeedKt": 12,
                    "visibility": "6+",
                    "weather": None,
                    "cloudLayers": [{"cover": "BKN", "baseFtAgl": 5000, "cloudType": None}],
                },
                {
                    "validFrom": _iso(NOW + timedelta(hours=14)),
                    "validTo": _iso(NOW + timedelta(hours=18)),
                    "changeIndicator": "PROB",
                    "probabilityPercent": 30,
                    "windDirection": None,
                    "windSpeedKt": None,
                    "visibility": "4",
                    "weather": "TSRA",
                    "cloudLayers": [{"cover": "BKN", "baseFtAgl": 3500, "cloudType": "CB"}],
                },
            ],
        },
        "caveats": [
            "Airport-area weather context is read-only situational evidence and does not by itself describe airborne conditions at the target position.",
            "Do not infer flight intent from METAR or TAF alone.",
        ],
    }


def _faa_nas_airport_status(airport_code: str, airport_name: str | None = None) -> dict[str, Any]:
    normalized = airport_code.strip().upper()
    records = {
        "KAUS": {
            "airportCode": "KAUS",
            "airportName": airport_name or "Austin-Bergstrom International Airport",
            "statusType": "ground delay",
            "reason": "low ceilings",
            "category": "Ground Delay Programs",
            "summary": "low ceilings | Average delay 38 minutes | Maximum delay 1 hour and 12 minutes",
            "issuedAt": None,
            "updatedAt": "Sat Apr 04 12:00:00 2026 GMT",
            "sourceUrl": "https://nasstatus.faa.gov/api/airport-status-information",
            "sourceMode": "fixture",
            "health": "normal",
            "caveats": [],
            "evidenceBasis": "advisory",
        },
        "KBOS": {
            "airportCode": "KBOS",
            "airportName": airport_name or "Boston Logan International Airport",
            "statusType": "ground stop",
            "reason": None,
            "category": "Ground Stops",
            "summary": "Ground Stops advisory active.",
            "issuedAt": None,
            "updatedAt": "Sat Apr 04 12:00:00 2026 GMT",
            "sourceUrl": "https://nasstatus.faa.gov/api/airport-status-information",
            "sourceMode": "fixture",
            "health": "normal",
            "caveats": ["FAA NAS record did not include a reason field."],
            "evidenceBasis": "advisory",
        },
    }
    record = records.get(normalized) or {
        "airportCode": normalized,
        "airportName": airport_name,
        "statusType": "normal",
        "reason": None,
        "category": None,
        "summary": "No active FAA NAS airport-status event is present for this airport in the current fixture feed.",
        "issuedAt": None,
        "updatedAt": "Sat Apr 04 12:00:00 2026 GMT",
        "sourceUrl": "https://nasstatus.faa.gov/api/airport-status-information",
        "sourceMode": "fixture",
        "health": "normal",
        "caveats": [],
        "evidenceBasis": "contextual",
    }
    return {
        "fetchedAt": _iso(NOW),
        "source": "faa-nas-status",
        "airportCode": normalized,
        "airportName": record.get("airportName"),
        "record": record,
        "sourceHealth": {
            "sourceName": "faa-nas-status",
            "sourceMode": "fixture",
            "health": "normal",
            "detail": "FAA NAS status fixture parsed successfully.",
            "sourceUrl": "https://nasstatus.faa.gov/api/airport-status-information",
            "lastUpdatedAt": "Sat Apr 04 12:00:00 2026 GMT",
            "state": "healthy",
            "caveats": [
                "FAA NAS airport status is general airport-condition context and is not flight-specific.",
                "Do not infer aircraft intent from airport status alone.",
            ],
        },
        "caveats": [
            "FAA NAS airport status is contextual/advisory airport information and is not flight-specific.",
            "Do not infer aircraft intent from airport status alone.",
            *record.get("caveats", []),
        ],
    }


def _opensky_states_context(
    *,
    lamin: float | None = None,
    lamax: float | None = None,
    lomin: float | None = None,
    lomax: float | None = None,
    limit: int = 25,
    callsign: str | None = None,
    icao24: str | None = None,
) -> dict[str, Any]:
    states = [
        {
            "icao24": "abc123",
            "callsign": "DAL123",
            "originCountry": "United States",
            "timePosition": _iso(NOW - timedelta(seconds=20)),
            "lastContact": _iso(NOW - timedelta(seconds=15)),
            "longitude": -97.7431,
            "latitude": 30.2672,
            "baroAltitude": 975.4,
            "onGround": False,
            "velocity": 210.0,
            "trueTrack": 184.0,
            "verticalRate": -2.5,
            "geoAltitude": 980.0,
            "squawk": "1200",
            "spi": False,
            "positionSource": 0,
            "sourceMode": "fixture",
            "caveats": [],
            "evidenceBasis": "source-reported",
        },
        {
            "icao24": "def456",
            "callsign": "UAL456",
            "originCountry": "United States",
            "timePosition": _iso(NOW - timedelta(seconds=80)),
            "lastContact": _iso(NOW - timedelta(seconds=75)),
            "longitude": None,
            "latitude": None,
            "baroAltitude": 300.0,
            "onGround": True,
            "velocity": 0.0,
            "trueTrack": 92.0,
            "verticalRate": 0.0,
            "geoAltitude": 305.0,
            "squawk": None,
            "spi": False,
            "positionSource": 1,
            "sourceMode": "fixture",
            "caveats": ["Position is unavailable in this source-reported state vector."],
            "evidenceBasis": "source-reported",
        },
        {
            "icao24": "ghi789",
            "callsign": "AAL789",
            "originCountry": "United States",
            "timePosition": _iso(NOW - timedelta(seconds=10)),
            "lastContact": _iso(NOW - timedelta(seconds=5)),
            "longitude": -97.65,
            "latitude": 30.31,
            "baroAltitude": 2500.0,
            "onGround": False,
            "velocity": 175.0,
            "trueTrack": 140.0,
            "verticalRate": 3.0,
            "geoAltitude": 2600.0,
            "squawk": "4451",
            "spi": False,
            "positionSource": 0,
            "sourceMode": "fixture",
            "caveats": [],
            "evidenceBasis": "source-reported",
        },
    ]
    if callsign:
        states = [state for state in states if (state["callsign"] or "").upper() == callsign.strip().upper()]
    if icao24:
        states = [state for state in states if state["icao24"] == icao24.strip().lower()]
    if None not in (lamin, lamax, lomin, lomax):
        states = [
            state
            for state in states
            if state["latitude"] is not None
            and state["longitude"] is not None
            and lamin <= state["latitude"] <= lamax
            and lomin <= state["longitude"] <= lomax
        ]
    states = states[:limit]
    return {
        "fetchedAt": _iso(NOW),
        "source": "opensky-anonymous-states",
        "count": len(states),
        "states": states,
        "sourceHealth": {
            "sourceName": "opensky-anonymous-states",
            "sourceMode": "fixture",
            "health": "normal",
            "detail": "OpenSky anonymous fixture parsed successfully.",
            "sourceUrl": "fixture:opensky",
            "lastUpdatedAt": _iso(NOW - timedelta(seconds=5)),
            "state": "healthy",
            "caveats": [
                "OpenSky anonymous access is rate-limited and may expose current state vectors only.",
                "Coverage is source-reported and not guaranteed to be complete or authoritative.",
            ],
        },
        "caveats": [
            "OpenSky anonymous access is rate-limited and may expose current state vectors only.",
            "Coverage is source-reported and not guaranteed to be complete or authoritative.",
            "This optional context does not replace the primary aircraft workflow.",
        ],
    }


def _ourairports_reference_context(
    q: str | None = None,
    airport_code: str | None = None,
    region_code: str | None = None,
    include_runways: bool = True,
    limit: int = 3,
) -> dict[str, Any]:
    normalized_code = airport_code.strip().upper() if airport_code else None
    normalized_query = q.strip().upper() if q else None
    normalized_region = region_code.strip().upper() if region_code else None
    airports = [
        {
            "referenceId": "ourairports:airport:KAUS",
            "externalId": "ourairports-airport-KAUS",
            "airportCode": "KAUS",
            "iataCode": "AUS",
            "localCode": "AUS",
            "name": "Austin-Bergstrom International Airport",
            "airportType": "large_airport",
            "latitude": 30.1945,
            "longitude": -97.6699,
            "countryCode": "US",
            "regionCode": "US-TX",
            "municipality": "Austin",
            "elevationFt": 542.0,
            "runwayCount": 2,
            "longestRunwayFt": 12250.0,
            "sourceUrl": "https://ourairports.com/airports/KAUS/",
            "sourceMode": "fixture",
            "health": "normal",
            "caveats": [
                "OurAirports reference rows are baseline facility metadata only and are not live airport-status or runway-availability evidence."
            ],
            "evidenceBasis": "reference",
        },
        {
            "referenceId": "ourairports:airport:KTEST",
            "externalId": "ourairports-airport-KTEST",
            "airportCode": "KTEST",
            "iataCode": None,
            "localCode": "TST",
            "name": "Test Regional Airport",
            "airportType": "small_airport",
            "latitude": 30.21,
            "longitude": -97.64,
            "countryCode": "US",
            "regionCode": "US-TX",
            "municipality": "Austin",
            "elevationFt": 530.0,
            "runwayCount": 1,
            "longestRunwayFt": 5600.0,
            "sourceUrl": "https://ourairports.com/airports/KTEST/",
            "sourceMode": "fixture",
            "health": "normal",
            "caveats": [
                "Fixture test airport is baseline reference metadata only."
            ],
            "evidenceBasis": "reference",
        },
        {
            "referenceId": "ourairports:airport:KVOID",
            "externalId": "ourairports-airport-KVOID",
            "airportCode": "KVOID",
            "iataCode": None,
            "localCode": None,
            "name": "Void Field",
            "airportType": "closed",
            "latitude": None,
            "longitude": None,
            "countryCode": "US",
            "regionCode": "US-TX",
            "municipality": None,
            "elevationFt": None,
            "runwayCount": 0,
            "longestRunwayFt": None,
            "sourceUrl": "https://ourairports.com/airports/KVOID/",
            "sourceMode": "fixture",
            "health": "degraded",
            "caveats": [
                "Fixture partial record lacks usable coordinates and must not be treated as map-precise facility geometry."
            ],
            "evidenceBasis": "reference",
        },
    ]
    runways = [
        {
            "referenceId": "ourairports:runway:KAUS:17R-35L",
            "externalId": "ourairports-runway-KAUS-17R-35L",
            "airportRefId": "ourairports:airport:KAUS",
            "airportCode": "KAUS",
            "leIdent": "17R",
            "heIdent": "35L",
            "lengthFt": 12250.0,
            "widthFt": 150.0,
            "surface": "ASP",
            "surfaceCategory": "paved",
            "centerLatitude": 30.1961,
            "centerLongitude": -97.6662,
            "sourceUrl": "https://ourairports.com/airports/KAUS/runways.html",
            "sourceMode": "fixture",
            "health": "normal",
            "caveats": [
                "Runway rows are baseline geometry only and do not prove runway availability or airport access."
            ],
            "evidenceBasis": "reference",
        },
        {
            "referenceId": "ourairports:runway:KTEST:18-36",
            "externalId": "ourairports-runway-KTEST-18-36",
            "airportRefId": "ourairports:airport:KTEST",
            "airportCode": "KTEST",
            "leIdent": "18",
            "heIdent": "36",
            "lengthFt": 5600.0,
            "widthFt": 100.0,
            "surface": "ASP",
            "surfaceCategory": "paved",
            "centerLatitude": 30.211,
            "centerLongitude": -97.639,
            "sourceUrl": "https://ourairports.com/airports/KTEST/runways.html",
            "sourceMode": "fixture",
            "health": "normal",
            "caveats": [
                "Fixture runway row is baseline geometry only."
            ],
            "evidenceBasis": "reference",
        },
    ]

    filtered_airports = airports
    if normalized_code:
        filtered_airports = [
            airport
            for airport in filtered_airports
            if normalized_code
            in {
                (airport["airportCode"] or "").upper(),
                (airport["iataCode"] or "").upper(),
                (airport["localCode"] or "").upper(),
            }
        ]
    elif normalized_query:
        filtered_airports = [
            airport
            for airport in filtered_airports
            if normalized_query in airport["name"].upper()
        ]
    if normalized_region:
        filtered_airports = [
            airport
            for airport in filtered_airports
            if (airport["regionCode"] or "").upper() == normalized_region
        ]
    filtered_airports = filtered_airports[:limit]
    airport_ref_ids = {airport["referenceId"] for airport in filtered_airports}
    filtered_runways = (
        [runway for runway in runways if runway["airportRefId"] in airport_ref_ids][:limit]
        if include_runways
        else []
    )

    caveats = [
        "OurAirports reference data is public baseline facility metadata, not live airport status or runway availability.",
        "Baseline reference matches do not validate aircraft identity, route, intent, or operational state.",
        "OurAirports reference context must not overwrite live selected-target evidence or shared aviation context.",
    ]

    return {
        "fetchedAt": _iso(NOW),
        "source": "ourairports-reference",
        "airportCount": len(filtered_airports),
        "runwayCount": len(filtered_runways),
        "airports": filtered_airports,
        "runways": filtered_runways,
        "sourceHealth": {
            "sourceName": "ourairports-reference",
            "sourceMode": "fixture",
            "health": "normal",
            "detail": "OurAirports fixture baseline airport/runway reference loaded successfully for aerospace comparison-only context.",
            "airportsSourceUrl": "fixture:ourairports_reference_fixture/airports.csv",
            "runwaysSourceUrl": "fixture:ourairports_reference_fixture/runways.csv",
            "lastUpdatedAt": _iso(NOW - timedelta(days=1)),
            "state": "healthy",
            "caveats": caveats,
        },
        "exportMetadata": {
            "sourceId": "ourairports-reference",
            "sourceMode": "fixture",
            "health": "normal",
            "airportCount": len(filtered_airports),
            "runwayCount": len(filtered_runways),
            "includeRunways": include_runways,
            "filters": {
                key: value
                for key, value in {
                    "airportCode": normalized_code,
                    "q": normalized_query,
                    "regionCode": normalized_region,
                }.items()
                if value
            },
            "caveat": "OurAirports export metadata is baseline/reference-only and must not be treated as live airport operational truth.",
        },
        "caveats": caveats,
    }


def _cneos_space_context(
    event_type: str = "all",
    limit: int = 3,
) -> dict[str, Any]:
    close_approaches = [
        {
            "objectDesignation": "2026 FH7",
            "objectName": "2026 FH7",
            "closeApproachAt": "2026-04-08T14:12:00+00:00",
            "distanceLunar": 4.21,
            "distanceAu": 0.0108,
            "distanceKm": 1617924.0,
            "velocityKmS": 11.8,
            "estimatedDiameterM": 82.0,
            "orbitingBody": "Earth",
            "sourceUrl": "https://ssd-api.jpl.nasa.gov/cad.api",
            "caveats": [],
            "evidenceBasis": "source-reported",
        },
        {
            "objectDesignation": "2026 GP",
            "objectName": "2026 GP",
            "closeApproachAt": "2026-04-12T02:45:00+00:00",
            "distanceLunar": 7.84,
            "distanceAu": 0.0201,
            "distanceKm": 3013696.0,
            "velocityKmS": 6.4,
            "estimatedDiameterM": 34.0,
            "orbitingBody": "Earth",
            "sourceUrl": "https://ssd-api.jpl.nasa.gov/cad.api",
            "caveats": [],
            "evidenceBasis": "source-reported",
        },
        {
            "objectDesignation": "2026 HX",
            "objectName": "2026 HX",
            "closeApproachAt": "2026-04-19T19:30:00+00:00",
            "distanceLunar": 9.61,
            "distanceAu": 0.0246,
            "distanceKm": 3690084.0,
            "velocityKmS": 9.1,
            "estimatedDiameterM": None,
            "orbitingBody": "Earth",
            "sourceUrl": "https://ssd-api.jpl.nasa.gov/cad.api",
            "caveats": ["Estimated diameter is unavailable in this source record."],
            "evidenceBasis": "source-reported",
        },
    ]
    fireballs = [
        {
            "eventTime": "2026-04-03T06:22:00+00:00",
            "latitude": 19.4,
            "longitude": -155.3,
            "altitudeKm": 31.0,
            "energyTenGigajoules": 12.4,
            "impactEnergyKt": 0.3,
            "velocityKmS": 17.2,
            "sourceUrl": "https://ssd-api.jpl.nasa.gov/fireball.api",
            "caveats": [],
            "evidenceBasis": "source-reported",
        },
        {
            "eventTime": "2026-03-29T11:08:00+00:00",
            "latitude": -7.8,
            "longitude": 124.6,
            "altitudeKm": 26.0,
            "energyTenGigajoules": 4.8,
            "impactEnergyKt": 0.1,
            "velocityKmS": 13.7,
            "sourceUrl": "https://ssd-api.jpl.nasa.gov/fireball.api",
            "caveats": [],
            "evidenceBasis": "source-reported",
        },
        {
            "eventTime": "2026-03-11T20:40:00+00:00",
            "latitude": None,
            "longitude": None,
            "altitudeKm": 28.0,
            "energyTenGigajoules": 2.9,
            "impactEnergyKt": 0.07,
            "velocityKmS": 12.1,
            "sourceUrl": "https://ssd-api.jpl.nasa.gov/fireball.api",
            "caveats": ["Location is unavailable in this source record."],
            "evidenceBasis": "source-reported",
        },
    ]
    normalized_type = event_type if event_type in {"all", "close-approach", "fireball"} else "all"
    selected_close = close_approaches[:limit] if normalized_type in {"all", "close-approach"} else []
    selected_fireballs = fireballs[:limit] if normalized_type in {"all", "fireball"} else []
    return {
        "fetchedAt": _iso(NOW),
        "source": "cneos-space-events",
        "eventType": normalized_type,
        "closeApproaches": selected_close,
        "fireballs": selected_fireballs,
        "sourceHealth": {
            "sourceName": "cneos-space-events",
            "sourceMode": "fixture",
            "health": "normal",
            "detail": "NASA/JPL CNEOS close-approach and fireball fixture parsed successfully.",
            "closeApproachSourceUrl": "https://ssd-api.jpl.nasa.gov/cad.api",
            "fireballSourceUrl": "https://ssd-api.jpl.nasa.gov/fireball.api",
            "lastUpdatedAt": "2026-04-08T14:12:00+00:00",
            "state": "healthy",
            "caveats": [
                "NASA/JPL CNEOS close approaches and fireballs are source-reported space-event context only.",
                "Do not infer impact risk or imminent threat from this summary alone.",
            ],
        },
        "caveats": [
            "NASA/JPL CNEOS close approaches and fireballs are contextual space-event records and are not impact predictions.",
            "Do not infer imminent threat or operational hazard from this summary alone.",
        ],
    }


def _swpc_space_weather_context(
    product_type: str = "all",
    limit: int = 3,
) -> dict[str, Any]:
    summaries = [
        {
            "productId": "swpc-r-current",
            "productType": "scale-summary",
            "issuedAt": None,
            "observedAt": "2026-04-29T18:00:00+00:00",
            "updatedAt": "2026-04-29T18:00:00+00:00",
            "scaleCategory": "R1",
            "headline": "R1 minor",
            "description": "Radio blackout scale: R1 minor",
            "affectedContext": ["radio", "gps"],
            "sourceUrl": "https://services.swpc.noaa.gov/products/noaa-scales.json",
            "sourceMode": "fixture",
            "health": "normal",
            "caveats": [],
            "evidenceBasis": "contextual",
        },
        {
            "productId": "swpc-s-current",
            "productType": "scale-summary",
            "issuedAt": None,
            "observedAt": "2026-04-29T18:00:00+00:00",
            "updatedAt": "2026-04-29T18:00:00+00:00",
            "scaleCategory": "S0",
            "headline": "S0 none",
            "description": "Solar radiation scale: S0 none",
            "affectedContext": ["satellite", "gps"],
            "sourceUrl": "https://services.swpc.noaa.gov/products/noaa-scales.json",
            "sourceMode": "fixture",
            "health": "normal",
            "caveats": [],
            "evidenceBasis": "contextual",
        },
        {
            "productId": "swpc-g-current",
            "productType": "scale-summary",
            "issuedAt": None,
            "observedAt": "2026-04-29T18:00:00+00:00",
            "updatedAt": "2026-04-29T18:00:00+00:00",
            "scaleCategory": "G2",
            "headline": "G2 moderate",
            "description": "Geomagnetic storm scale: G2 moderate",
            "affectedContext": ["geomagnetic", "satellite", "gps"],
            "sourceUrl": "https://services.swpc.noaa.gov/products/noaa-scales.json",
            "sourceMode": "fixture",
            "health": "normal",
            "caveats": [],
            "evidenceBasis": "contextual",
        },
    ]
    alerts = [
        {
            "productId": "G2W",
            "productType": "watch",
            "issuedAt": "2026-04-28T17:40:00+00:00",
            "updatedAt": "2026-04-28T17:40:00+00:00",
            "scaleCategory": "G2",
            "headline": "WATCH: G2 Moderate Geomagnetic Storm conditions expected.",
            "description": "WATCH: G2 Moderate Geomagnetic Storm conditions expected. Potential impacts include possible satellite orientation irregularities and intermittent navigation effects at high latitudes.",
            "affectedContext": ["geomagnetic", "satellite", "gps"],
            "sourceUrl": "https://services.swpc.noaa.gov/products/alerts.json",
            "sourceMode": "fixture",
            "health": "normal",
            "caveats": [],
            "evidenceBasis": "advisory",
        },
        {
            "productId": "R1A",
            "productType": "alert",
            "issuedAt": "2026-04-28T13:15:00+00:00",
            "updatedAt": "2026-04-28T13:15:00+00:00",
            "scaleCategory": "R1",
            "headline": "ALERT: R1 Minor Radio Blackout observed.",
            "description": "ALERT: R1 Minor Radio Blackout observed. Potential impacts include weak or minor degradation of HF radio communication on the sunlit side and degraded low-frequency navigation signals for brief intervals.",
            "affectedContext": ["radio", "gps"],
            "sourceUrl": "https://services.swpc.noaa.gov/products/alerts.json",
            "sourceMode": "fixture",
            "health": "normal",
            "caveats": [],
            "evidenceBasis": "advisory",
        },
    ]
    normalized_type = product_type if product_type in {"all", "summary", "alerts"} else "all"
    return {
        "fetchedAt": _iso(NOW),
        "source": "noaa-swpc",
        "productType": normalized_type,
        "summaries": summaries[:limit] if normalized_type in {"all", "summary"} else [],
        "alerts": alerts[:limit] if normalized_type in {"all", "alerts"} else [],
        "sourceHealth": {
            "sourceName": "noaa-swpc",
            "sourceMode": "fixture",
            "health": "normal",
            "detail": "NOAA SWPC alerts and scale summaries fixture parsed successfully.",
            "summarySourceUrl": "https://services.swpc.noaa.gov/products/noaa-scales.json",
            "alertsSourceUrl": "https://services.swpc.noaa.gov/products/alerts.json",
            "lastUpdatedAt": "2026-04-29T18:00:00+00:00",
            "state": "healthy",
            "caveats": [
                "NOAA SWPC space-weather context is advisory/contextual and does not by itself prove operational impact.",
                "Do not infer satellite, GPS, or radio failure unless the source explicitly states that impact.",
            ],
        },
        "caveats": [
            "NOAA SWPC summaries and alerts are advisory/contextual space-weather records.",
            "Do not infer actual satellite, GPS, or radio failure unless the source explicitly states that impact.",
        ],
    }


def _usgs_geomagnetism_context(
    observatory_id: str = "BOU",
    elements: str | None = None,
) -> dict[str, Any]:
    requested_observatory = observatory_id.strip().upper()
    requested_elements = [part.strip().upper() for part in (elements or "").split(",") if part.strip()]
    allowed_elements = {"X", "Y", "Z", "F"}
    if requested_elements:
        requested_elements = [part for part in requested_elements if part in allowed_elements]

    fixtures: dict[str, dict[str, Any]] = {
        "BOU": {
            "metadata": {
                "source": "usgs-geomagnetism",
                "sourceName": "USGS Geomagnetism Data Web Service",
                "sourceUrl": "https://geomag.usgs.gov/ws/data/",
                "observatoryId": "BOU",
                "observatoryName": "Boulder",
                "latitude": 40.137,
                "longitude": -105.237,
                "elevationM": 1682.0,
                "sourceMode": "fixture",
                "generatedAt": "2026-04-30T19:31:26Z",
                "samplingPeriodSeconds": 60.0,
                "samples": [
                    ("2026-04-30T00:00:00.000Z", {"X": 20518.812, "Y": 2802.936, "Z": 52015.4, "F": 55979.1}),
                    ("2026-04-30T00:01:00.000Z", {"X": 20519.302, "Y": 2803.16, "Z": 52015.8, "F": 55979.5}),
                    ("2026-04-30T00:02:00.000Z", {"X": 20518.875, "Y": 2803.466, "Z": 52016.1, "F": None}),
                    ("2026-04-30T00:03:00.000Z", {"X": 20517.704, "Y": 2803.625, "Z": 52015.7, "F": 55978.8}),
                ],
            },
        },
        "EMPT": {
            "metadata": {
                "source": "usgs-geomagnetism",
                "sourceName": "USGS Geomagnetism Data Web Service",
                "sourceUrl": "https://geomag.usgs.gov/ws/data/",
                "observatoryId": "EMPT",
                "observatoryName": "Fixture Empty Observatory",
                "latitude": None,
                "longitude": None,
                "elevationM": None,
                "sourceMode": "fixture",
                "generatedAt": "2026-04-30T19:31:26Z",
                "samplingPeriodSeconds": 60.0,
                "samples": [],
            },
        },
    }
    fixture = fixtures.get(requested_observatory, fixtures["EMPT"])
    base_metadata = fixture["metadata"]
    sample_rows = base_metadata["samples"]
    selected_elements = requested_elements or ["X", "Y", "Z", "F"]
    request_url = "https://geomag.usgs.gov/ws/data/?id=" + requested_observatory + "&format=json"
    if requested_elements:
        request_url += "&elements=" + "%2C".join(selected_elements)

    samples = [
        {
            "observedAt": observed_at,
            "values": {element: values.get(element) for element in selected_elements},
            "evidenceBasis": "observed",
        }
        for observed_at, values in sample_rows
    ]
    base_caveat = (
        "USGS geomagnetism values are observatory magnetic-field context only. "
        "Do not infer power-grid, communications, GPS, radio, or aviation impacts from field values alone."
    )
    fetched_at = _iso(NOW)
    generated_at = base_metadata["generatedAt"]
    health = "loaded" if samples else "empty"
    return {
        "metadata": {
            "source": "usgs-geomagnetism",
            "sourceName": "USGS Geomagnetism Data Web Service",
            "sourceUrl": "https://geomag.usgs.gov/ws/data/",
            "requestUrl": request_url,
            "observatoryId": requested_observatory,
            "observatoryName": base_metadata["observatoryName"],
            "latitude": base_metadata["latitude"],
            "longitude": base_metadata["longitude"],
            "elevationM": base_metadata["elevationM"],
            "sourceMode": "fixture",
            "fetchedAt": fetched_at,
            "generatedAt": generated_at,
            "startTime": samples[0]["observedAt"] if samples else None,
            "endTime": samples[-1]["observedAt"] if samples else None,
            "samplingPeriodSeconds": base_metadata["samplingPeriodSeconds"],
            "elements": selected_elements,
            "count": len(samples),
            "caveat": base_caveat,
        },
        "count": len(samples),
        "sourceHealth": {
            "sourceId": "usgs-geomagnetism",
            "sourceLabel": "USGS Geomagnetism",
            "enabled": True,
            "sourceMode": "fixture",
            "health": health,
            "loadedCount": len(samples),
            "lastFetchedAt": fetched_at,
            "sourceGeneratedAt": generated_at,
            "detail": (
                "USGS geomagnetism observatory samples parsed successfully."
                if samples
                else "No geomagnetism samples matched the current observatory payload."
            ),
            "errorSummary": None,
            "caveat": base_caveat,
        },
        "samples": samples,
        "caveats": [base_caveat],
    }


def _vaac_fixture_response(
    fixture_name: str,
    source_name: str,
    volcano: str | None,
    limit: int,
) -> dict[str, Any]:
    payload = _load_json_fixture(fixture_name)
    advisories = payload.get("advisories", [])
    if volcano:
        normalized = volcano.strip().lower()
        advisories = [
            advisory
            for advisory in advisories
            if str(advisory.get("volcano_name", "")).strip().lower() == normalized
        ]

    advisories = advisories[: max(limit, 0)]
    return {
        "fetched_at": _iso(NOW),
        "source": source_name,
        "volcano": volcano,
        "count": len(advisories),
        "advisories": advisories,
        "source_health": {
            "source_name": source_name,
            "source_mode": "fixture",
            "health": "normal",
            "detail": f"{source_name} fixture smoke response.",
            "listing_source_url": payload["listing_source_url"],
            "last_updated_at": payload.get("last_updated_at"),
            "state": "healthy",
            "caveats": payload.get("caveats", []),
        },
        "caveats": payload.get("caveats", []),
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


def _eonet_events() -> list[dict[str, Any]]:
    return [
        {
            "eventId": "EONET_SMOKE_001",
            "source": "nasa-eonet",
            "sourceUrl": "https://eonet.gsfc.nasa.gov/api/v3/events/EONET_SMOKE_001",
            "title": "Smoke Wildfire Cluster",
            "description": "Smoke fixture event",
            "categories": ["Wildfires"],
            "categoryIds": ["wildfires"],
            "categoryTitles": ["Wildfires"],
            "eventDate": _iso(NOW - timedelta(hours=3)),
            "updated": _iso(NOW - timedelta(hours=2)),
            "isClosed": False,
            "closed": None,
            "status": "open",
            "geometryType": "Point",
            "longitude": -120.2,
            "latitude": 46.7,
            "coordinatesSummary": "Point geometry.",
            "magnitudeValue": None,
            "magnitudeUnit": None,
            "rawGeometryCount": 1,
            "caveat": "NASA EONET source-reported environmental context only."
        },
        {
            "eventId": "EONET_SMOKE_002",
            "source": "nasa-eonet",
            "sourceUrl": "https://eonet.gsfc.nasa.gov/api/v3/events/EONET_SMOKE_002",
            "title": "Volcanic Activity Context",
            "description": "Volcano fixture event",
            "categories": ["Volcanoes"],
            "categoryIds": ["volcanoes"],
            "categoryTitles": ["Volcanoes"],
            "eventDate": _iso(NOW - timedelta(days=1, hours=2)),
            "updated": _iso(NOW - timedelta(days=1)),
            "isClosed": False,
            "closed": None,
            "status": "open",
            "geometryType": "Point",
            "longitude": 15.004,
            "latitude": 37.734,
            "coordinatesSummary": "Point geometry.",
            "magnitudeValue": None,
            "magnitudeUnit": None,
            "rawGeometryCount": 1,
            "caveat": "NASA EONET source-reported environmental context only."
        },
        {
            "eventId": "EONET_SMOKE_003",
            "source": "nasa-eonet",
            "sourceUrl": "https://eonet.gsfc.nasa.gov/api/v3/events/EONET_SMOKE_003",
            "title": "Tropical Storm Archive",
            "description": "Closed storm fixture",
            "categories": ["Severe Storms"],
            "categoryIds": ["severeStorms"],
            "categoryTitles": ["Severe Storms"],
            "eventDate": _iso(NOW - timedelta(days=2)),
            "updated": _iso(NOW - timedelta(days=2)),
            "isClosed": True,
            "closed": _iso(NOW - timedelta(days=1, hours=12)),
            "status": "closed",
            "geometryType": "Point",
            "longitude": 68.1,
            "latitude": -22.2,
            "coordinatesSummary": "Representative point from latest geometry; event may include multiple geometries.",
            "magnitudeValue": None,
            "magnitudeUnit": None,
            "rawGeometryCount": 3,
            "caveat": "NASA EONET source-reported environmental context only."
        }
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
                "name": "opensky-anonymous-states",
                "state": "healthy",
                "enabled": True,
                "healthy": True,
                "freshnessSeconds": 60,
                "staleAfterSeconds": 300,
                "lastSuccessAt": _iso(NOW - timedelta(seconds=15)),
                "degradedReason": None,
                "rateLimited": False,
                "hiddenReason": None,
                "detail": "Optional OpenSky anonymous fixture provides rate-limited source-reported state-vector context for selected aircraft.",
                "credentialsConfigured": True,
                "blockedReason": None,
                "reviewRequired": False,
                "lastAttemptAt": _iso(NOW - timedelta(seconds=15)),
                "lastFailureAt": None,
                "successCount": 2,
                "failureCount": 0,
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
                "name": "noaa-awc",
                "state": "healthy",
                "enabled": True,
                "healthy": True,
                "freshnessSeconds": 300,
                "staleAfterSeconds": 1800,
                "lastSuccessAt": _iso(NOW - timedelta(minutes=5)),
                "degradedReason": None,
                "rateLimited": False,
                "hiddenReason": None,
                "detail": "NOAA AWC fixture provides airport-context METAR/TAF for selected aerospace targets.",
                "credentialsConfigured": True,
                "blockedReason": None,
                "reviewRequired": False,
                "lastAttemptAt": _iso(NOW - timedelta(minutes=5)),
                "lastFailureAt": None,
                "successCount": 2,
                "failureCount": 0,
                "warningCount": 0,
            },
            {
                "name": "faa-nas-status",
                "state": "healthy",
                "enabled": True,
                "healthy": True,
                "freshnessSeconds": 60,
                "staleAfterSeconds": 300,
                "lastSuccessAt": _iso(NOW - timedelta(seconds=50)),
                "degradedReason": None,
                "rateLimited": False,
                "hiddenReason": None,
                "detail": "FAA NAS airport-status fixture provides airport operational advisory context for selected aerospace targets.",
                "credentialsConfigured": True,
                "blockedReason": None,
                "reviewRequired": False,
                "lastAttemptAt": _iso(NOW - timedelta(seconds=55)),
                "lastFailureAt": None,
                "successCount": 2,
                "failureCount": 0,
                "warningCount": 0,
            },
            {
                "name": "ourairports-reference",
                "state": "healthy",
                "enabled": True,
                "healthy": True,
                "freshnessSeconds": 86400,
                "staleAfterSeconds": 604800,
                "lastSuccessAt": _iso(NOW - timedelta(hours=6)),
                "degradedReason": None,
                "rateLimited": False,
                "hiddenReason": None,
                "detail": "OurAirports fixture provides baseline airport and runway reference context for aerospace comparison-only review.",
                "credentialsConfigured": True,
                "blockedReason": None,
                "reviewRequired": False,
                "lastAttemptAt": _iso(NOW - timedelta(hours=6)),
                "lastFailureAt": None,
                "successCount": 2,
                "failureCount": 0,
                "warningCount": 0,
            },
            {
                "name": "cneos-space-events",
                "state": "healthy",
                "enabled": True,
                "healthy": True,
                "freshnessSeconds": 3600,
                "staleAfterSeconds": 86400,
                "lastSuccessAt": _iso(NOW - timedelta(minutes=10)),
                "degradedReason": None,
                "rateLimited": False,
                "hiddenReason": None,
                "detail": "NASA/JPL CNEOS fixture provides close-approach and fireball context for aerospace review.",
                "credentialsConfigured": True,
                "blockedReason": None,
                "reviewRequired": False,
                "lastAttemptAt": _iso(NOW - timedelta(minutes=10)),
                "lastFailureAt": None,
                "successCount": 2,
                "failureCount": 0,
                "warningCount": 0,
            },
            {
                "name": "noaa-swpc",
                "state": "healthy",
                "enabled": True,
                "healthy": True,
                "freshnessSeconds": 1800,
                "staleAfterSeconds": 21600,
                "lastSuccessAt": _iso(NOW - timedelta(minutes=20)),
                "degradedReason": None,
                "rateLimited": False,
                "hiddenReason": None,
                "detail": "NOAA SWPC fixture provides advisory/contextual space-weather summaries for aerospace situational awareness.",
                "credentialsConfigured": True,
                "blockedReason": None,
                "reviewRequired": False,
                "lastAttemptAt": _iso(NOW - timedelta(minutes=20)),
                "lastFailureAt": None,
                "successCount": 2,
                "failureCount": 0,
                "warningCount": 0,
            },
            {
                "name": "washington-vaac",
                "state": "healthy",
                "enabled": True,
                "healthy": True,
                "freshnessSeconds": 3600,
                "staleAfterSeconds": 21600,
                "lastSuccessAt": _iso(NOW - timedelta(minutes=15)),
                "degradedReason": None,
                "rateLimited": False,
                "hiddenReason": None,
                "detail": "Washington VAAC fixture provides bounded volcanic-ash advisory context for aerospace review.",
                "credentialsConfigured": True,
                "blockedReason": None,
                "reviewRequired": False,
                "lastAttemptAt": _iso(NOW - timedelta(minutes=15)),
                "lastFailureAt": None,
                "successCount": 2,
                "failureCount": 0,
                "warningCount": 0,
            },
            {
                "name": "noaa-ncei-space-weather-portal",
                "state": "healthy",
                "enabled": True,
                "healthy": True,
                "freshnessSeconds": 86400,
                "staleAfterSeconds": 604800,
                "lastSuccessAt": _iso(NOW - timedelta(hours=6)),
                "degradedReason": None,
                "rateLimited": False,
                "hiddenReason": None,
                "detail": "NOAA NCEI fixture provides archival space-weather collection metadata for aerospace review.",
                "credentialsConfigured": True,
                "blockedReason": None,
                "reviewRequired": False,
                "lastAttemptAt": _iso(NOW - timedelta(hours=6)),
                "lastFailureAt": None,
                "successCount": 2,
                "failureCount": 0,
                "warningCount": 1,
            },
            {
                "name": "anchorage-vaac",
                "state": "healthy",
                "enabled": True,
                "healthy": True,
                "freshnessSeconds": 3600,
                "staleAfterSeconds": 21600,
                "lastSuccessAt": _iso(NOW - timedelta(minutes=18)),
                "degradedReason": None,
                "rateLimited": False,
                "hiddenReason": None,
                "detail": "Anchorage VAAC fixture provides bounded volcanic-ash advisory context for aerospace review.",
                "credentialsConfigured": True,
                "blockedReason": None,
                "reviewRequired": False,
                "lastAttemptAt": _iso(NOW - timedelta(minutes=18)),
                "lastFailureAt": None,
                "successCount": 2,
                "failureCount": 0,
                "warningCount": 0,
            },
            {
                "name": "tokyo-vaac",
                "state": "healthy",
                "enabled": True,
                "healthy": True,
                "freshnessSeconds": 3600,
                "staleAfterSeconds": 21600,
                "lastSuccessAt": _iso(NOW - timedelta(minutes=21)),
                "degradedReason": None,
                "rateLimited": False,
                "hiddenReason": None,
                "detail": "Tokyo VAAC fixture provides bounded volcanic-ash advisory context for aerospace review.",
                "credentialsConfigured": True,
                "blockedReason": None,
                "reviewRequired": False,
                "lastAttemptAt": _iso(NOW - timedelta(minutes=21)),
                "lastFailureAt": None,
                "successCount": 2,
                "failureCount": 0,
                "warningCount": 0,
            },
            {
                "name": "usgs-geomagnetism",
                "state": "healthy",
                "enabled": True,
                "healthy": True,
                "freshnessSeconds": 3600,
                "staleAfterSeconds": 86400,
                "lastSuccessAt": _iso(NOW - timedelta(minutes=30)),
                "degradedReason": None,
                "rateLimited": False,
                "hiddenReason": None,
                "detail": "USGS geomagnetism fixture provides observatory magnetic-field context for aerospace review.",
                "credentialsConfigured": True,
                "blockedReason": None,
                "reviewRequired": False,
                "lastAttemptAt": _iso(NOW - timedelta(minutes=30)),
                "lastFailureAt": None,
                "successCount": 2,
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
            {
                "name": "eonet",
                "state": "healthy",
                "enabled": True,
                "healthy": True,
                "freshnessSeconds": 120,
                "staleAfterSeconds": 600,
                "lastSuccessAt": _iso(NOW - timedelta(minutes=2)),
                "degradedReason": None,
                "rateLimited": False,
                "hiddenReason": None,
                "detail": "NASA EONET fixture feed.",
                "credentialsConfigured": True,
                "blockedReason": None,
                "reviewRequired": False,
                "lastAttemptAt": _iso(NOW - timedelta(minutes=2, seconds=10)),
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
            "sourceMode": "fixture",
            "generatedAt": _iso(NOW - timedelta(seconds=40)),
            "fetchedAt": _iso(NOW),
            "count": len(events),
            "caveat": "USGS magnitude and location are source-reported metadata; marker styling is visual prioritization only and does not imply damage."
        },
        "count": len(events),
        "events": events,
    }


@app.get("/api/events/eonet/recent")
async def events_eonet_recent(
    category: str | None = Query(default=None),
    status: str = Query(default="open"),
    limit: int = Query(default=200),
    sort: str = Query(default="newest"),
) -> dict[str, Any]:
    events = _eonet_events()
    if category:
        needle = category.lower()
        events = [event for event in events if any(needle in value.lower() for value in event["categoryTitles"])]
    if status != "all":
        events = [event for event in events if event["status"] == status]
    if sort == "category":
        events.sort(key=lambda event: (event["categoryTitles"][0], event["eventDate"]))
    else:
        events.sort(key=lambda event: event["eventDate"], reverse=True)
    events = events[:limit]
    return {
        "metadata": {
            "source": "nasa-eonet",
            "feedName": "events",
            "feedUrl": "https://eonet.gsfc.nasa.gov/api/v3/events",
            "sourceMode": "fixture",
            "generatedAt": _iso(NOW - timedelta(minutes=2)),
            "fetchedAt": _iso(NOW),
            "count": len(events),
            "caveat": "NASA EONET natural events are source-reported context; marker location may be representative for multi-geometry events."
        },
        "count": len(events),
        "events": events
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


@app.get("/api/marine/context/noaa-coops")
async def marine_noaa_coops_context() -> dict[str, Any]:
    return {
        "fetchedAt": _iso(NOW),
        "contextKind": "chokepoint",
        "centerLat": 29.76,
        "centerLon": -95.36,
        "radiusKm": 400.0,
        "count": 2,
        "sourceHealth": {
            "sourceId": "noaa-coops-tides-currents",
            "sourceLabel": "NOAA CO-OPS Tides & Currents",
            "enabled": True,
            "sourceMode": "fixture",
            "health": "loaded",
            "loadedCount": 2,
            "lastFetchedAt": _iso(NOW),
            "sourceGeneratedAt": _iso(NOW - timedelta(minutes=4)),
            "detail": "Fixture NOAA CO-OPS marine context.",
            "errorSummary": None,
            "caveat": "Fixture/local mode. NOAA CO-OPS is coastal context only and does not prove vessel behavior.",
        },
        "stations": [
            {
                "stationId": "8771450",
                "stationName": "Galveston Pier 21",
                "stationType": "water-level",
                "latitude": 29.31,
                "longitude": -94.7933,
                "distanceKm": 78.4,
                "productsAvailable": ["water_level"],
                "statusLine": "water level 0.74 m",
                "externalUrl": "https://tidesandcurrents.noaa.gov/stationhome.html?id=8771450",
                "latestWaterLevel": {
                    "observedAt": _iso(NOW - timedelta(minutes=6)),
                    "valueM": 0.74,
                    "units": "m",
                    "datum": "MLLW",
                    "trend": "falling",
                    "sourceDetail": "Fixture latest water level observation near Galveston harbor.",
                    "externalUrl": "https://tidesandcurrents.noaa.gov/stationhome.html?id=8771450",
                    "observedBasis": "observed",
                },
                "latestCurrent": None,
                "caveats": ["Water level reflects station observation only, not harbor-wide conditions."],
            },
            {
                "stationId": "8771341",
                "stationName": "Galveston Bay Entrance North Jetty",
                "stationType": "currents",
                "latitude": 29.3583,
                "longitude": -94.7242,
                "distanceKm": 84.9,
                "productsAvailable": ["currents"],
                "statusLine": "current 1.6 kts",
                "externalUrl": "https://tidesandcurrents.noaa.gov/stationhome.html?id=8771341",
                "latestWaterLevel": None,
                "latestCurrent": {
                    "observedAt": _iso(NOW - timedelta(minutes=8)),
                    "speedKts": 1.6,
                    "directionDeg": 126.0,
                    "directionCardinal": "SE",
                    "binDepthM": 5.0,
                    "units": "kts",
                    "sourceDetail": "Fixture latest current observation near Galveston Bay entrance.",
                    "externalUrl": "https://tidesandcurrents.noaa.gov/stationhome.html?id=8771341",
                    "observedBasis": "observed",
                },
                "caveats": ["Currents are channel-local and should not be generalized beyond the station area."],
            },
        ],
        "caveats": [
            "NOAA CO-OPS observations are environmental context only; do not infer vessel intent from tides or currents alone.",
            "Fixture/local mode is explicit in this first slice and should not be mistaken for live national coverage.",
        ],
    }


@app.get("/api/marine/context/ndbc")
async def marine_ndbc_context() -> dict[str, Any]:
    return {
        "fetchedAt": _iso(NOW),
        "contextKind": "chokepoint",
        "centerLat": 29.76,
        "centerLon": -95.36,
        "radiusKm": 500.0,
        "count": 1,
        "sourceHealth": {
            "sourceId": "noaa-ndbc-realtime",
            "sourceLabel": "NOAA NDBC Realtime Buoys",
            "enabled": True,
            "sourceMode": "fixture",
            "health": "loaded",
            "loadedCount": 1,
            "lastFetchedAt": _iso(NOW),
            "sourceGeneratedAt": _iso(NOW - timedelta(minutes=12)),
            "detail": "Fixture NOAA NDBC marine context.",
            "errorSummary": None,
            "caveat": "Fixture/local mode. NOAA NDBC is environmental context only and does not prove vessel behavior.",
        },
        "stations": [
            {
                "stationId": "42035",
                "stationName": "Galveston - 22 NM East of Galveston, TX",
                "latitude": 29.235,
                "longitude": -94.413,
                "distanceKm": 93.1,
                "stationType": "buoy",
                "statusLine": "wind 17.0 kts | waves 1.8 m | pressure 1012 hPa",
                "externalUrl": "https://www.ndbc.noaa.gov/station_page.php?station=42035",
                "latestObservation": {
                    "observedAt": _iso(NOW - timedelta(minutes=14)),
                    "windDirectionDeg": 140.0,
                    "windDirectionCardinal": "SE",
                    "windSpeedKts": 17.0,
                    "windGustKts": 22.0,
                    "waveHeightM": 1.8,
                    "dominantPeriodS": 6.0,
                    "pressureHpa": 1012.4,
                    "airTemperatureC": 24.6,
                    "waterTemperatureC": 25.1,
                    "sourceDetail": "Fixture latest buoy meteorological and wave observation for upper Texas coast context.",
                    "externalUrl": "https://www.ndbc.noaa.gov/station_page.php?station=42035",
                    "observedBasis": "observed",
                },
                "caveats": ["Buoy observations are offshore point samples and may not represent harbor conditions."],
            }
        ],
        "caveats": [
            "NOAA NDBC buoy observations are environmental context only; do not infer vessel intent from weather or wave conditions alone.",
            "Fixture/local mode is explicit in this first slice and should not be mistaken for live offshore coverage.",
        ],
    }


@app.get("/api/marine/context/scottish-water-overflows")
async def marine_scottish_water_overflows_context() -> dict[str, Any]:
    return {
        "fetchedAt": _iso(NOW),
        "centerLat": 55.95,
        "centerLon": -3.10,
        "radiusKm": 400.0,
        "statusFilter": "all",
        "count": 3,
        "activeCount": 1,
        "sourceHealth": {
            "sourceId": "scottish-water-overflows",
            "sourceLabel": "Scottish Water Overflows",
            "enabled": True,
            "sourceMode": "fixture",
            "health": "degraded",
            "loadedCount": 3,
            "lastFetchedAt": _iso(NOW),
            "sourceGeneratedAt": _iso(NOW - timedelta(minutes=9)),
            "detail": "Fixture Scottish Water overflow context includes partial metadata and should be treated as degraded source health.",
            "errorSummary": None,
            "caveat": "Fixture/local mode. Overflow monitor activation is source-reported infrastructure context only and does not confirm pollution impact or vessel behavior. Partial metadata degrades source-health confidence for this review.",
        },
        "events": [
            {
                "eventId": "sw-overflow-edinburgh-active",
                "monitorId": "EDM-1001",
                "assetId": "SWO-NE-1001",
                "siteName": "Portobello East Overflow",
                "waterBody": "Firth of Forth",
                "outfallLabel": "Portobello East",
                "locationLabel": "Edinburgh coast",
                "latitude": 55.9505,
                "longitude": -3.1072,
                "distanceKm": 0.6,
                "status": "active",
                "startedAt": _iso(NOW - timedelta(hours=2, minutes=15)),
                "endedAt": None,
                "lastUpdatedAt": _iso(NOW - timedelta(minutes=6)),
                "durationMinutes": 135,
                "sourceUrl": "https://api.scottishwater.co.uk/overflow-event-monitoring/v1/near-real-time",
                "sourceDetail": "Fixture near-real-time overflow monitor activation for Edinburgh coastal context.",
                "evidenceBasis": "source-reported",
                "caveats": ["Activation indicates source-reported overflow monitoring status only."],
            },
            {
                "eventId": "sw-overflow-partial-metadata",
                "monitorId": "EDM-NULL-77",
                "assetId": None,
                "siteName": "North Coast Overflow Monitor",
                "waterBody": "Unknown coastal water body",
                "outfallLabel": None,
                "locationLabel": "Partial metadata fixture",
                "latitude": None,
                "longitude": None,
                "distanceKm": None,
                "status": "unknown",
                "startedAt": None,
                "endedAt": None,
                "lastUpdatedAt": _iso(NOW - timedelta(minutes=25)),
                "durationMinutes": None,
                "sourceUrl": "https://api.scottishwater.co.uk/overflow-event-monitoring/v1/near-real-time",
                "sourceDetail": "Fixture partial metadata record without public coordinates.",
                "evidenceBasis": "source-reported",
                "caveats": ["Missing coordinates limit nearby filtering and map placement for this record."],
            },
            {
                "eventId": "sw-overflow-glasgow-ended",
                "monitorId": "EDM-2044",
                "assetId": "SWO-WC-2044",
                "siteName": "Greenock Esplanade Overflow",
                "waterBody": "Firth of Clyde",
                "outfallLabel": "Greenock Esplanade",
                "locationLabel": "Greenock waterfront",
                "latitude": 55.9470,
                "longitude": -4.7712,
                "distanceKm": 113.8,
                "status": "inactive",
                "startedAt": _iso(NOW - timedelta(hours=9)),
                "endedAt": _iso(NOW - timedelta(hours=7, minutes=40)),
                "lastUpdatedAt": _iso(NOW - timedelta(minutes=18)),
                "durationMinutes": 80,
                "sourceUrl": "https://api.scottishwater.co.uk/overflow-event-monitoring/v1/near-real-time",
                "sourceDetail": "Fixture recently ended overflow monitor event for Clyde coastal context.",
                "evidenceBasis": "source-reported",
                "caveats": ["Recently ended status does not describe downstream impact or current water quality."],
            },
        ],
        "caveats": [
            "Scottish Water overflow monitor activations are source-reported contextual infrastructure status only.",
            "Partial metadata degrades source-health confidence for this fixture review path.",
            "Do not infer pollution impact, health risk, or vessel intent from overflow activation status alone.",
        ],
    }


@app.get("/api/marine/context/vigicrues-hydrometry")
async def marine_vigicrues_hydrometry_context() -> dict[str, Any]:
    return {
        "fetchedAt": _iso(NOW),
        "centerLat": 49.30,
        "centerLon": 1.24,
        "radiusKm": 300.0,
        "parameterFilter": "all",
        "count": 0,
        "sourceHealth": {
            "sourceId": "france-vigicrues-hydrometry",
            "sourceLabel": "France Vigicrues Hydrometry",
            "enabled": True,
            "sourceMode": "fixture",
            "health": "unavailable",
            "loadedCount": 0,
            "lastFetchedAt": _iso(NOW),
            "sourceGeneratedAt": None,
            "detail": "Fixture Vigicrues hydrometry context is unavailable because source retrieval failed.",
            "errorSummary": "TimeoutError: fixture vigicrues unavailable",
            "caveat": "Fixture/local mode. Vigicrues retrieval failed, so current hydrology context is unavailable and should not be treated as negative vessel evidence.",
        },
        "stations": [],
        "caveats": [
            "Vigicrues hydrometry context is currently unavailable because source retrieval failed in fixture mode.",
            "Hydrometry observations are contextual river-condition data only; do not infer inundation, damage, or vessel intent from station values alone.",
            "Missing hydrology context is not evidence of flood impact, vessel intent, or anomaly cause.",
        ],
    }


@app.get("/api/marine/context/ireland-opw-waterlevel")
async def marine_ireland_opw_waterlevel_context() -> dict[str, Any]:
    return {
        "fetchedAt": _iso(NOW),
        "centerLat": 52.45,
        "centerLon": -9.66,
        "radiusKm": 250.0,
        "count": 2,
        "sourceHealth": {
            "sourceId": "ireland-opw-waterlevel",
            "sourceLabel": "Ireland OPW Water Level",
            "enabled": True,
            "sourceMode": "fixture",
            "health": "degraded",
            "loadedCount": 2,
            "lastFetchedAt": _iso(NOW),
            "sourceGeneratedAt": _iso(NOW - timedelta(minutes=7)),
            "detail": "Fixture Ireland OPW water-level context includes partial metadata and should be treated as degraded source health.",
            "errorSummary": None,
            "caveat": "Fixture/local mode. OPW water-level readings are provisional hydrometric context only and do not confirm flood impact or vessel behavior. Partial metadata degrades source-health confidence for this review.",
        },
        "stations": [
            {
                "stationId": "25017_0001",
                "stationName": "Ballyduff",
                "latitude": 52.4558,
                "longitude": -9.6635,
                "distanceKm": 0.7,
                "waterbody": "River Feale",
                "hydrometricArea": "Shannon Estuary South",
                "statusLine": "water level 1.42 m",
                "stationSourceUrl": "https://waterlevel.ie/geojson/",
                "latestReading": {
                    "readingAt": _iso(NOW - timedelta(minutes=18)),
                    "waterLevelM": 1.42,
                    "sourceDetail": "Fixture latest OPW GeoJSON water-level reading for lower River Feale context review.",
                    "sourceUrl": "https://waterlevel.ie/geojson/latest/",
                    "observedBasis": "observed",
                },
                "caveats": ["Provisional reading only; station height does not confirm flood impact beyond the gauge location."],
            },
            {
                "stationId": "19006_0001",
                "stationName": "Limerick City",
                "latitude": 52.6613,
                "longitude": -8.6267,
                "distanceKm": 87.4,
                "waterbody": None,
                "hydrometricArea": "Shannon Lower",
                "statusLine": "water level 2.17 m",
                "stationSourceUrl": "https://waterlevel.ie/geojson/",
                "latestReading": {
                    "readingAt": _iso(NOW - timedelta(minutes=31)),
                    "waterLevelM": 2.17,
                    "sourceDetail": "Fixture latest OPW GeoJSON water-level reading for lower Shannon estuary-adjacent context.",
                    "sourceUrl": "https://waterlevel.ie/geojson/latest/",
                    "observedBasis": "observed",
                },
                "caveats": ["Waterbody metadata is intentionally missing in this fixture to preserve partial-metadata contract coverage."],
            },
        ],
        "caveats": [
            "OPW water-level readings are provisional hydrometric observations only; do not infer flooding, damage, contamination, or vessel intent from station values alone.",
            "Partial metadata degrades source-health confidence for this fixture review path.",
            "Reading timestamps and fetch time should remain distinct because provisional source updates may lag publication timing.",
            "Fixture/local mode is explicit in this first slice and should not be mistaken for live national water-level coverage.",
        ],
    }


@app.get("/api/marine/context/netherlands-rws-waterinfo")
async def marine_netherlands_rws_waterinfo_context() -> dict[str, Any]:
    return {
        "fetchedAt": _iso(NOW),
        "centerLat": 51.98,
        "centerLon": 4.12,
        "radiusKm": 250.0,
        "count": 2,
        "sourceHealth": {
            "sourceId": "netherlands-rws-waterinfo",
            "sourceLabel": "Netherlands RWS Waterinfo",
            "enabled": True,
            "sourceMode": "fixture",
            "health": "degraded",
            "loadedCount": 2,
            "lastFetchedAt": _iso(NOW),
            "sourceGeneratedAt": _iso(NOW - timedelta(minutes=6)),
            "detail": "Fixture Netherlands RWS Waterinfo context includes partial metadata and should be treated as degraded source health.",
            "errorSummary": None,
            "caveat": "Fixture/local mode. Waterinfo remains bounded to metadata plus latest water-level observations and does not confirm flood impact, navigation safety, or vessel behavior. Partial metadata degrades source-health confidence for this review.",
        },
        "stations": [
            {
                "stationId": "HOEKVHLD",
                "stationName": "Hoek van Holland",
                "latitude": 51.9775,
                "longitude": 4.1208,
                "distanceKm": 0.9,
                "waterBody": "Nieuwe Waterweg",
                "statusLine": "water level 126.0 centimeter",
                "stationSourceUrl": "https://waterwebservices.apps.rijkswaterstaat.nl/ddapi20-waterwebservices/api/METADATASERVICES_DBO/OphalenCatalogus",
                "latestObservation": {
                    "observedAt": _iso(NOW - timedelta(minutes=19)),
                    "waterLevelValue": 126.0,
                    "unitCode": "cm",
                    "unitLabel": "centimeter",
                    "parameterCode": "WATHTE",
                    "parameterLabel": "Waterhoogte",
                    "sourceDetail": "Fixture latest Waterinfo water-level observation for Nieuwe Waterweg context review.",
                    "sourceUrl": "https://waterwebservices.apps.rijkswaterstaat.nl/ddapi20-waterwebservices/api/ONLINEWAARNEMINGENSERVICES_DBO/OphalenLaatsteWaarnemingen",
                    "observedBasis": "observed",
                },
                "caveats": [
                    "Waterinfo water-level observations are hydrology context only and do not prove flood impact, navigation safety, or vessel intent."
                ],
            },
            {
                "stationId": "DORDT",
                "stationName": "Dordrecht",
                "latitude": 51.8133,
                "longitude": 4.6901,
                "distanceKm": 61.4,
                "waterBody": None,
                "statusLine": "water level 118.0 centimeter",
                "stationSourceUrl": "https://waterwebservices.apps.rijkswaterstaat.nl/ddapi20-waterwebservices/api/METADATASERVICES_DBO/OphalenCatalogus",
                "latestObservation": {
                    "observedAt": _iso(NOW - timedelta(minutes=26)),
                    "waterLevelValue": 118.0,
                    "unitCode": "cm",
                    "unitLabel": None,
                    "parameterCode": "WATHTE",
                    "parameterLabel": "Waterhoogte",
                    "sourceDetail": "Fixture latest Waterinfo water-level observation with intentionally partial metadata for contract and smoke coverage.",
                    "sourceUrl": "https://waterwebservices.apps.rijkswaterstaat.nl/ddapi20-waterwebservices/api/ONLINEWAARNEMINGENSERVICES_DBO/OphalenLaatsteWaarnemingen",
                    "observedBasis": "observed",
                },
                "caveats": [
                    "Water body and unit label metadata are intentionally partial in this fixture to preserve degraded-source contract coverage."
                ],
            },
        ],
        "caveats": [
            "Waterinfo latest observations are contextual hydrology data only; do not infer flood impact, navigation safety, anomaly cause, or vessel intent from station values alone.",
            "Partial metadata degrades source-health confidence for this fixture review path.",
            "Fixture/local mode is explicit in this first slice and should not be mistaken for live national Waterinfo coverage.",
        ],
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


@app.get("/api/aviation-weather/airport-context")
async def aviation_weather_airport_context(
    airport_code: str = Query(...),
    airport_name: str | None = Query(default=None),
    airport_ref_id: str | None = Query(default=None),
    context_type: str = Query(default="nearest-airport"),
) -> dict[str, Any]:
    payload = _aviation_weather_context()
    payload["airportCode"] = airport_code.strip().upper()
    if airport_name:
        payload["airportName"] = airport_name
    if airport_ref_id:
        payload["airportRefId"] = airport_ref_id
    payload["contextType"] = context_type
    return payload


@app.get("/api/aerospace/airports/{airport_code}/faa-nas-status")
async def faa_nas_airport_status(
    airport_code: str,
    airport_name: str | None = Query(default=None),
) -> dict[str, Any]:
    return _faa_nas_airport_status(airport_code, airport_name)


@app.get("/api/aerospace/reference/ourairports")
async def ourairports_reference(
    q: str | None = Query(default=None),
    airport_code: str | None = Query(default=None),
    region_code: str | None = Query(default=None),
    include_runways: bool = Query(default=True),
    limit: int = Query(default=10),
) -> dict[str, Any]:
    return _ourairports_reference_context(
        q=q,
        airport_code=airport_code,
        region_code=region_code,
        include_runways=include_runways,
        limit=limit,
    )


@app.get("/api/aerospace/aircraft/opensky/states")
async def opensky_states(
    lamin: float | None = Query(default=None),
    lamax: float | None = Query(default=None),
    lomin: float | None = Query(default=None),
    lomax: float | None = Query(default=None),
    limit: int = Query(default=25),
    callsign: str | None = Query(default=None),
    icao24: str | None = Query(default=None),
) -> dict[str, Any]:
    return _opensky_states_context(
        lamin=lamin,
        lamax=lamax,
        lomin=lomin,
        lomax=lomax,
        limit=limit,
        callsign=callsign,
        icao24=icao24,
    )


@app.get("/api/aerospace/space/cneos-events")
async def cneos_space_events(
    event_type: str = Query(default="all"),
    limit: int = Query(default=3),
) -> dict[str, Any]:
    return _cneos_space_context(event_type=event_type, limit=limit)


@app.get("/api/aerospace/space/swpc-context")
async def swpc_space_weather_context(
    product_type: str = Query(default="all"),
    limit: int = Query(default=3),
) -> dict[str, Any]:
    return _swpc_space_weather_context(product_type=product_type, limit=limit)


@app.get("/api/aerospace/space/ncei-space-weather-archive")
async def ncei_space_weather_archive() -> dict[str, Any]:
    return {
        "fetchedAt": _iso(NOW),
        "source": "noaa-ncei-space-weather-portal",
        "count": 1,
        "records": [
            {
                "collectionId": "gov.noaa.ngdc.stp.swx:space_weather_products",
                "datasetIdentifier": "solarFeatures",
                "title": "Space Weather Products",
                "summary": "Collection includes a variety of archived space weather datasets from NOAA and the World Data Service for Geophysics, Boulder.",
                "temporalStart": "1818-01-01",
                "temporalEnd": "2009-12-30",
                "metadataUpdatedAt": "2015-10-02",
                "progressStatus": "underDevelopment",
                "updateFrequency": "annually",
                "sourceUrl": "https://www.ncei.noaa.gov/access/metadata/landing-page/bin/iso?id=gov.noaa.ngdc.stp.swx:space_weather_products;view=xml;responseType=text/xml",
                "landingPageUrl": "https://www.ncei.noaa.gov/access/metadata/landing-page/bin/iso?id=gov.noaa.ngdc.stp.swx:space_weather_products",
                "sourceMode": "fixture",
                "health": "normal",
                "caveats": [
                    "This record describes archived space-weather products and collection coverage, not current SWPC warning state.",
                    "Coverage dates and update cadence describe the archived collection metadata, not current operational conditions.",
                ],
                "evidenceBasis": "archival",
            }
        ],
        "sourceHealth": {
            "sourceName": "noaa-ncei-space-weather-portal",
            "sourceMode": "fixture",
            "health": "normal",
            "detail": "NOAA NCEI space-weather portal archival metadata parsed successfully.",
            "metadataSourceUrl": "https://www.ncei.noaa.gov/access/metadata/landing-page/bin/iso?id=gov.noaa.ngdc.stp.swx:space_weather_products;view=xml;responseType=text/xml",
            "landingPageUrl": "https://www.ncei.noaa.gov/access/metadata/landing-page/bin/iso?id=gov.noaa.ngdc.stp.swx:space_weather_products",
            "lastUpdatedAt": "2015-10-02",
            "state": "healthy",
            "caveats": [
                "NOAA NCEI space-weather portal metadata is archival/contextual collection metadata, not current operational SWPC alerting.",
                "Do not infer current GPS, radio, aircraft, or satellite failure from archival catalog metadata alone.",
            ],
        },
        "caveats": [
            "NOAA NCEI space-weather portal context is archival/catalog metadata and is separate from current NOAA SWPC advisory context.",
            "Do not infer current GPS, radio, aircraft, or satellite failure from archival catalog metadata alone.",
        ],
    }


@app.get("/api/aerospace/space/washington-vaac-advisories")
async def washington_vaac_advisories(
    volcano: str | None = Query(default=None),
    limit: int = Query(default=2),
) -> dict[str, Any]:
    return _vaac_fixture_response(
        "washington_vaac_advisories_fixture.json",
        "washington-vaac",
        volcano,
        limit,
    )


@app.get("/api/aerospace/space/anchorage-vaac-advisories")
async def anchorage_vaac_advisories(
    volcano: str | None = Query(default=None),
    limit: int = Query(default=2),
) -> dict[str, Any]:
    return _vaac_fixture_response(
        "anchorage_vaac_advisories_fixture.json",
        "anchorage-vaac",
        volcano,
        limit,
    )


@app.get("/api/aerospace/space/tokyo-vaac-advisories")
async def tokyo_vaac_advisories(
    volcano: str | None = Query(default=None),
    limit: int = Query(default=2),
) -> dict[str, Any]:
    return _vaac_fixture_response(
        "tokyo_vaac_advisories_fixture.json",
        "tokyo-vaac",
        volcano,
        limit,
    )


@app.get("/api/context/geomagnetism/usgs")
async def usgs_geomagnetism_context(
    observatory_id: str = Query(default="BOU"),
    elements: str | None = Query(default=None),
) -> dict[str, Any]:
    return _usgs_geomagnetism_context(observatory_id=observatory_id, elements=elements)


@app.get("/")
async def app_index() -> FileResponse:
    return FileResponse(CLIENT_DIST / "index.html")


@app.get("/{full_path:path}")
async def app_routes(full_path: str) -> FileResponse:
    candidate = (CLIENT_DIST / full_path).resolve()
    if candidate.is_file() and CLIENT_DIST in candidate.parents:
        return FileResponse(candidate)
    return FileResponse(CLIENT_DIST / "index.html")
