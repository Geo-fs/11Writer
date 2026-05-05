from __future__ import annotations

import json
import math
import time
from pathlib import Path
from typing import Any

from src.config.settings import Settings
from src.services.media_evidence_service import geolocate_media_artifact


class MediaGeolocationEvaluationService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def load_fixture_manifest(self, path: str | None = None) -> dict[str, Any]:
        manifest_path = Path(path or self._settings.source_discovery_media_geolocation_eval_fixture_path)
        if not manifest_path.exists():
            raise FileNotFoundError(f"Media geolocation evaluation manifest not found: {manifest_path}")
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("Media geolocation evaluation manifest must be a JSON object.")
        return payload

    def run_fixture_evaluation(self, path: str | None = None) -> dict[str, Any]:
        manifest = self.load_fixture_manifest(path)
        raw_cases = manifest.get("cases", [])
        if not isinstance(raw_cases, list):
            raise ValueError("Media geolocation evaluation manifest must include a list of cases.")
        results: list[dict[str, Any]] = []
        top1_hits = 0
        top5_hits = 0
        country_region_hits = 0
        coordinate_extraction_hits = 0
        disagreement_cases = 0
        unavailable_attempts = 0
        fallback_attempts = 0
        latency_ms_total = 0.0
        distance_bands = {"10km": 0, "25km": 0, "50km": 0, "200km": 0}
        clue_family_hits = {
            "coordinate": 0,
            "place_text": 0,
            "script_language": 0,
            "environment": 0,
            "time": 0,
        }

        for case in raw_cases:
            if not isinstance(case, dict):
                continue
            started = time.perf_counter()
            result = geolocate_media_artifact(
                self._settings,
                artifact_path=None,
                artifact_metadata=case.get("artifactMetadata", {}) if isinstance(case.get("artifactMetadata"), dict) else {},
                observed_latitude=_coerce_float(case.get("observedLatitude")),
                observed_longitude=_coerce_float(case.get("observedLongitude")),
                exif_timestamp=_coerce_optional_str(case.get("exifTimestamp")),
                ocr_text=_coerce_optional_str(case.get("ocrText")),
                captions=[str(item) for item in case.get("captions", []) if str(item).strip()] if isinstance(case.get("captions"), list) else [],
                engine=_coerce_optional_str(case.get("engine")) or "deterministic",
                analyst_adapter="none",
                model=None,
                analyst_model=None,
                allow_local_ai=False,
                fixture_result=None,
                candidate_labels=[str(item) for item in case.get("candidateLabels", []) if str(item).strip()] if isinstance(case.get("candidateLabels"), list) else [],
                prior_place_hypothesis=None,
                prior_place_confidence=None,
                prior_place_basis=None,
                prior_geolocation_hypothesis=None,
                prior_geolocation_confidence=None,
                prior_geolocation_basis=None,
                inherited_context=case.get("inheritedContext", {}) if isinstance(case.get("inheritedContext"), dict) else None,
            )
            elapsed_ms = round((time.perf_counter() - started) * 1000.0, 3)
            latency_ms_total += elapsed_ms
            expected = case.get("expected", {}) if isinstance(case.get("expected"), dict) else {}
            target_lat = _coerce_float(expected.get("latitude"))
            target_lon = _coerce_float(expected.get("longitude"))
            country_region = _coerce_optional_str(expected.get("countryOrRegion"))
            top_distance_km = _distance_km(result.top_latitude, result.top_longitude, target_lat, target_lon)
            top5_distance_km = _best_top5_distance_km(result.candidates, target_lat, target_lon)
            top1_hit = top_distance_km is not None and top_distance_km <= 25.0
            top5_hit = top5_distance_km is not None and top5_distance_km <= 25.0
            if top1_hit:
                top1_hits += 1
            if top5_hit:
                top5_hits += 1
            if top_distance_km is not None:
                if top_distance_km <= 10.0:
                    distance_bands["10km"] += 1
                if top_distance_km <= 25.0:
                    distance_bands["25km"] += 1
                if top_distance_km <= 50.0:
                    distance_bands["50km"] += 1
                if top_distance_km <= 200.0:
                    distance_bands["200km"] += 1
            if country_region and _matches_country_region(result, country_region):
                country_region_hits += 1
            if any(clue.latitude is not None and clue.longitude is not None for clue in result.clue_packet.coordinate_clues):
                coordinate_extraction_hits += 1
            if result.clue_packet.coordinate_clues:
                clue_family_hits["coordinate"] += 1
            if result.clue_packet.place_text_clues:
                clue_family_hits["place_text"] += 1
            if result.clue_packet.script_language_clues:
                clue_family_hits["script_language"] += 1
            if result.clue_packet.environment_clues:
                clue_family_hits["environment"] += 1
            if result.clue_packet.time_clues:
                clue_family_hits["time"] += 1
            if bool(result.engine_agreement.get("hasConflict")):
                disagreement_cases += 1
            unavailable_attempts += sum(1 for attempt in result.engine_attempts if attempt.status == "unavailable")
            fallback_attempts += sum(1 for attempt in result.engine_attempts if attempt.status in {"failed", "rejected"})
            results.append(
                {
                    "caseId": _coerce_optional_str(case.get("caseId")) or f"case-{len(results) + 1}",
                    "status": result.status,
                    "topLabel": result.top_label,
                    "topLatitude": result.top_latitude,
                    "topLongitude": result.top_longitude,
                    "topConfidence": result.top_confidence,
                    "topConfidenceCeiling": result.top_confidence_ceiling,
                    "topDistanceKm": top_distance_km,
                    "top5DistanceKm": top5_distance_km,
                    "top1Hit25Km": top1_hit,
                    "top5Hit25Km": top5_hit,
                    "countryRegionHit": _matches_country_region(result, country_region) if country_region else None,
                    "coordinateExtractionHit": any(clue.latitude is not None and clue.longitude is not None for clue in result.clue_packet.coordinate_clues),
                    "engineAttempts": [
                        {
                            "engine": attempt.engine,
                            "status": attempt.status,
                            "modelName": attempt.model_name,
                            "warmState": attempt.warm_state,
                        }
                        for attempt in result.engine_attempts
                    ],
                    "latencyMs": elapsed_ms,
                }
            )
        case_count = max(1, len(results))
        return {
            "metadata": {
                "manifestPath": str(Path(path or self._settings.source_discovery_media_geolocation_eval_fixture_path)),
                "caseCount": len(results),
                "mode": "fixture_eval",
            },
            "metrics": {
                "top1HitRate25Km": round(top1_hits / case_count, 4),
                "top5HitRate25Km": round(top5_hits / case_count, 4),
                "countryRegionAccuracy": round(country_region_hits / case_count, 4),
                "ocrCoordinateExtractionSuccess": round(coordinate_extraction_hits / case_count, 4),
                "clueFamilyRecall": {key: round(value / case_count, 4) for key, value in clue_family_hits.items()},
                "distanceBandAccuracy": {key: round(value / case_count, 4) for key, value in distance_bands.items()},
                "unavailableAttemptRate": round(unavailable_attempts / case_count, 4),
                "fallbackAttemptRate": round(fallback_attempts / case_count, 4),
                "disagreementRate": round(disagreement_cases / case_count, 4),
                "meanLatencyMs": round(latency_ms_total / case_count, 3),
            },
            "results": results,
        }


def _best_top5_distance_km(candidates: list[Any], target_lat: float | None, target_lon: float | None) -> float | None:
    if target_lat is None or target_lon is None:
        return None
    distances = [
        _distance_km(getattr(candidate, "latitude", None), getattr(candidate, "longitude", None), target_lat, target_lon)
        for candidate in candidates[:5]
    ]
    numeric = [value for value in distances if value is not None]
    if not numeric:
        return None
    return round(min(numeric), 3)


def _matches_country_region(result: Any, expected_country_region: str | None) -> bool:
    if not expected_country_region:
        return False
    expected = expected_country_region.casefold()
    if result.top_label and expected in result.top_label.casefold():
        return True
    for candidate in result.candidates:
        label = getattr(candidate, "label", None)
        if label and expected in label.casefold():
            return True
    return False


def _distance_km(
    latitude_a: float | None,
    longitude_a: float | None,
    latitude_b: float | None,
    longitude_b: float | None,
) -> float | None:
    if None in {latitude_a, longitude_a, latitude_b, longitude_b}:
        return None
    lat1 = math.radians(float(latitude_a))
    lon1 = math.radians(float(longitude_a))
    lat2 = math.radians(float(latitude_b))
    lon2 = math.radians(float(longitude_b))
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    hav = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return round(6371.0088 * 2 * math.asin(min(1.0, math.sqrt(hav))), 3)


def _coerce_float(value: object) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _coerce_optional_str(value: object) -> str | None:
    if value is None:
        return None
    normalized = str(value).strip()
    return normalized or None
