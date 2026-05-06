from __future__ import annotations

import base64
import hashlib
import inspect
import json
import math
import os
import re
import shutil
import subprocess
import time
import zlib
from collections import OrderedDict
from dataclasses import dataclass, field
from datetime import datetime
from importlib import metadata as importlib_metadata
from io import BytesIO
from pathlib import Path
from threading import Lock
from typing import Any
from urllib.parse import parse_qsl, urlencode, urljoin, urlsplit, urlunsplit
from urllib.request import Request, urlopen

from src.config.settings import Settings
from src.services.runtime_paths import resolve_runtime_paths

try:
    from PIL import Image, ImageFilter, ImageOps, ImageStat, UnidentifiedImageError
except ImportError:  # pragma: no cover - optional local dependency
    Image = None  # type: ignore[assignment]
    ImageFilter = None  # type: ignore[assignment]
    ImageOps = None  # type: ignore[assignment]
    ImageStat = None  # type: ignore[assignment]

    class UnidentifiedImageError(Exception):
        pass

try:
    import cv2  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover - optional local dependency
    cv2 = None  # type: ignore[assignment]

try:
    from rapidocr_onnxruntime import RapidOCR  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover - optional local dependency
    RapidOCR = None  # type: ignore[assignment]

try:
    import torch  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover - optional local dependency
    torch = None  # type: ignore[assignment]

try:
    from transformers import AutoModel, AutoProcessor  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover - optional local dependency
    AutoModel = None  # type: ignore[assignment]
    AutoProcessor = None  # type: ignore[assignment]

try:
    from huggingface_hub import snapshot_download  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover - optional local dependency
    snapshot_download = None  # type: ignore[assignment]

try:
    from geoclip import GeoCLIP  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover - optional local dependency
    GeoCLIP = None  # type: ignore[assignment]


MEDIA_HTTP_USER_AGENT = "11Writer/MediaEvidence (+https://local.11writer.invalid; public-no-auth-media-evidence)"
_GEOCLIP_RUNTIME_LOCK = Lock()
_GEOCLIP_RUNTIME_CACHE: dict[str, Any] = {}
_GEOCLIP_PREDICTION_CACHE_LOCK = Lock()
_GEOCLIP_PREDICTION_CACHE: OrderedDict[str, dict[str, Any]] = OrderedDict()
_STREETCLIP_RUNTIME_LOCK = Lock()
_STREETCLIP_RUNTIME_CACHE: dict[str, Any] = {}
_PLACE_GAZETTEER_RUNTIME_LOCK = Lock()
_PLACE_GAZETTEER_RUNTIME_CACHE: dict[str, Any] = {}


@dataclass
class MediaArtifactInspection:
    canonical_url: str
    media_url: str
    parent_page_url: str | None
    mime_type: str | None
    media_kind: str
    width: int | None
    height: int | None
    byte_length: int
    content_hash: str
    perceptual_hash: str | None
    artifact_path: str | None
    acquisition_method: str
    evidence_basis: str
    observed_latitude: float | None = None
    observed_longitude: float | None = None
    exif_timestamp: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    caveats: list[str] = field(default_factory=list)


@dataclass
class MediaOcrBlock:
    block_index: int
    text: str
    confidence: float | None = None
    left: int | None = None
    top: int | None = None
    width: int | None = None
    height: int | None = None


@dataclass
class MediaOcrRunResult:
    status: str
    engine: str
    engine_version: str | None
    raw_text: str
    preprocessing: list[str]
    mean_confidence: float | None
    blocks: list[MediaOcrBlock]
    metadata: dict[str, Any] = field(default_factory=dict)
    caveats: list[str] = field(default_factory=list)
    selected_result: bool = False
    attempt_index: int = 0


@dataclass
class MediaInterpretationResult:
    status: str
    adapter: str
    model_name: str | None
    scene_labels: list[str]
    scene_summary: str | None
    uncertainty_ceiling: float | None
    place_hypothesis: str | None
    place_confidence: float | None
    place_basis: str | None
    time_of_day_guess: str | None
    time_of_day_confidence: float | None
    time_of_day_basis: str | None
    season_guess: str | None
    season_confidence: float | None
    season_basis: str | None
    geolocation_hypothesis: str | None
    geolocation_confidence: float | None
    geolocation_basis: str | None
    observed_latitude: float | None
    observed_longitude: float | None
    reasoning_lines: list[str]
    metadata: dict[str, Any] = field(default_factory=dict)
    caveats: list[str] = field(default_factory=list)


@dataclass
class MediaComparisonResult:
    status: str
    comparison_kind: str
    algorithm_version: str
    exact_hash_match: bool
    perceptual_hash_distance: int | None
    ssim_score: float | None
    histogram_similarity: float | None
    edge_similarity: float | None
    ocr_text_similarity: float | None
    time_delta_seconds: int | None
    confidence_score: float
    confidence_basis: list[str]
    auto_signal_kind: str | None
    metadata: dict[str, Any] = field(default_factory=dict)
    caveats: list[str] = field(default_factory=list)


@dataclass
class MediaFrameSampleResult:
    status: str
    sampler: str
    frames: list[bytes]
    sample_interval_seconds: int
    source_span_seconds: int
    metadata: dict[str, Any] = field(default_factory=dict)
    caveats: list[str] = field(default_factory=list)


@dataclass
class MediaGeolocationClue:
    clue_type: str
    text: str
    confidence: float | None = None
    normalized_value: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    reason: str | None = None
    inherited: bool = False
    inherited_from_artifact_id: str | None = None
    inherited_from_geolocation_run_id: str | None = None
    inherited_from_comparison_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class MediaGeolocationCluePacket:
    coordinate_clues: list[MediaGeolocationClue] = field(default_factory=list)
    place_text_clues: list[MediaGeolocationClue] = field(default_factory=list)
    script_language_clues: list[MediaGeolocationClue] = field(default_factory=list)
    environment_clues: list[MediaGeolocationClue] = field(default_factory=list)
    time_clues: list[MediaGeolocationClue] = field(default_factory=list)
    rejected_clues: list[MediaGeolocationClue] = field(default_factory=list)


@dataclass
class MediaGeolocationEngineAttempt:
    engine: str
    role: str
    status: str
    model_name: str | None = None
    warm_state: str | None = None
    availability_reason: str | None = None
    produced_candidate_count: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)
    caveats: list[str] = field(default_factory=list)


@dataclass
class MediaGeolocationCandidate:
    rank: int
    candidate_kind: str
    label: str | None
    latitude: float | None
    longitude: float | None
    confidence: float | None
    engine: str
    confidence_score: float | None = None
    confidence_ceiling: float | None = None
    basis: list[str] = field(default_factory=list)
    supporting_evidence: list[str] = field(default_factory=list)
    contradicting_evidence: list[str] = field(default_factory=list)
    engine_agreement: dict[str, Any] = field(default_factory=dict)
    provenance_chain: list[str] = field(default_factory=list)
    inherited: bool = False
    inherited_from_artifact_ids: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    caveats: list[str] = field(default_factory=list)


@dataclass
class MediaGeolocationAnalystResult:
    adapter: str
    model_name: str | None
    summary: str | None
    reasoning_lines: list[str]
    candidates: list[MediaGeolocationCandidate]
    negative_evidence: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    caveats: list[str] = field(default_factory=list)


@dataclass
class MediaGeolocationResult:
    status: str
    engine: str
    model_name: str | None
    analyst_adapter: str | None
    analyst_model_name: str | None
    candidate_count: int
    top_label: str | None
    top_latitude: float | None
    top_longitude: float | None
    top_confidence: float | None
    top_confidence_ceiling: float | None
    top_basis: str | None
    summary: str | None
    confidence_ceiling: float | None
    supporting_evidence: list[str]
    contradicting_evidence: list[str]
    engine_agreement: dict[str, Any]
    provenance_chain: list[str]
    inherited_from_artifact_ids: list[str]
    clue_packet: MediaGeolocationCluePacket
    engine_attempts: list[MediaGeolocationEngineAttempt]
    reasoning_lines: list[str]
    candidates: list[MediaGeolocationCandidate]
    metadata: dict[str, Any] = field(default_factory=dict)
    caveats: list[str] = field(default_factory=list)


@dataclass
class MediaGeolocationModelHealth:
    model_name: str
    role: str
    enabled: bool
    status: str
    install_ready: bool
    runtime_ready: bool
    warm_state: str
    summary: str | None
    installed_version: str | None = None
    expected_version: str | None = None
    model_id: str | None = None
    download_allowed: bool = False
    cache_dir: str | None = None
    local_dir: str | None = None
    weights_path: str | None = None
    clip_backbone_dir: str | None = None
    missing_components: list[str] = field(default_factory=list)
    present_components: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    caveats: list[str] = field(default_factory=list)


def fetch_media_artifact(
    settings: Settings,
    *,
    source_id: str,
    media_url: str,
    parent_page_url: str | None,
    fixture_bytes_base64: str | None,
    fixture_content_type: str | None,
    request_budget: int,
    max_bytes: int,
) -> tuple[MediaArtifactInspection, int]:
    used_requests = 0
    content_type = fixture_content_type
    if fixture_bytes_base64 is not None:
        body = base64.b64decode(fixture_bytes_base64.encode("utf-8"), validate=True)
        acquisition_method = "fixture_media"
    else:
        if request_budget <= 0:
            raise ValueError("Media artifact fetch needs fixture bytes or positive request_budget.")
        request = Request(media_url, headers={"User-Agent": MEDIA_HTTP_USER_AGENT}, method="GET")
        with urlopen(request, timeout=15) as response:
            raw = response.read(max_bytes + 1)
            if len(raw) > max_bytes:
                raise ValueError(f"Media artifact exceeded the configured byte limit of {max_bytes} bytes.")
            body = raw
            content_type = response.headers.get("content-type") or content_type
        used_requests = 1
        acquisition_method = "direct_media_fetch"
    canonical_url = canonicalize_url(media_url, base_url=parent_page_url)
    inspection = inspect_media_bytes(
        settings,
        source_id=source_id,
        media_url=canonical_url,
        parent_page_url=parent_page_url,
        payload=body,
        content_type=content_type,
        acquisition_method=acquisition_method,
    )
    return inspection, used_requests


def inspect_media_bytes(
    settings: Settings,
    *,
    source_id: str,
    media_url: str,
    parent_page_url: str | None,
    payload: bytes,
    content_type: str | None,
    acquisition_method: str,
) -> MediaArtifactInspection:
    mime_type = _sniff_mime_type(payload, content_type=content_type, url=media_url)
    media_kind = "image" if (mime_type or "").startswith("image/") else "unknown"
    metadata: dict[str, Any] = {
        "mimeTypeSniffed": mime_type,
        "contentTypeHeader": content_type,
    }
    caveats: list[str] = []
    width: int | None = None
    height: int | None = None
    observed_latitude: float | None = None
    observed_longitude: float | None = None
    exif_timestamp: str | None = None
    perceptual_hash: str | None = None

    artifact_root = Path(resolve_runtime_paths(settings)["user_data_dir"]) / "source-discovery" / "media" / _safe_id(source_id)
    artifact_root.mkdir(parents=True, exist_ok=True)
    content_hash = hashlib.sha256(payload).hexdigest()
    extension = _extension_for_mime(mime_type, media_url)
    artifact_path = artifact_root / f"{content_hash[:24]}{extension}"
    if not artifact_path.exists():
        artifact_path.write_bytes(payload)

    image_meta = inspect_image_metadata(payload, mime_type=mime_type)
    if image_meta is not None:
        width = image_meta["width"]
        height = image_meta["height"]
        perceptual_hash = image_meta.get("perceptual_hash")
        observed_latitude = image_meta.get("observed_latitude")
        observed_longitude = image_meta.get("observed_longitude")
        exif_timestamp = image_meta.get("exif_timestamp")
        metadata.update(image_meta["metadata"])
        caveats.extend(image_meta["caveats"])
    elif media_kind == "image":
        fallback_meta = _fallback_image_metadata(payload, mime_type=mime_type)
        if fallback_meta is not None:
            width = fallback_meta["width"]
            height = fallback_meta["height"]
            perceptual_hash = fallback_meta.get("perceptual_hash")
            metadata.update(fallback_meta["metadata"])
            caveats.extend(fallback_meta["caveats"])
        else:
            header_dims = _parse_image_dimensions(payload)
            width = header_dims[0]
            height = header_dims[1]
            caveats.append("Rich image analysis is limited because Pillow is unavailable or the image could not be decoded.")
    return MediaArtifactInspection(
        canonical_url=media_url,
        media_url=media_url,
        parent_page_url=parent_page_url,
        mime_type=mime_type,
        media_kind=media_kind,
        width=width,
        height=height,
        byte_length=len(payload),
        content_hash=content_hash,
        perceptual_hash=perceptual_hash,
        artifact_path=str(artifact_path),
        acquisition_method=acquisition_method,
        evidence_basis="observed",
        observed_latitude=observed_latitude,
        observed_longitude=observed_longitude,
        exif_timestamp=exif_timestamp,
        metadata=metadata,
        caveats=caveats,
    )


def inspect_image_metadata(payload: bytes, *, mime_type: str | None) -> dict[str, Any] | None:
    if Image is None:
        return None
    try:
        with Image.open(BytesIO(payload)) as image:
            rgb = image.convert("RGB")
            downsampled = ImageOps.exif_transpose(rgb).resize((64, 64)) if ImageOps is not None else rgb.resize((64, 64))
            width, height = image.size
            channel_stats = ImageStat.Stat(downsampled)
            red_mean = float(channel_stats.mean[0]) / 255.0
            green_mean = float(channel_stats.mean[1]) / 255.0
            blue_mean = float(channel_stats.mean[2]) / 255.0
            grayscale = downsampled.convert("L")
            brightness = float(ImageStat.Stat(grayscale).mean[0]) / 255.0
            seasonal = _seasonal_color_signals(downsampled)
            daypart = _daylight_signals(downsampled, brightness=brightness)
            metadata: dict[str, Any] = {
                "format": image.format,
                "mode": image.mode,
                "channelMeans": {
                    "red": round(red_mean, 4),
                    "green": round(green_mean, 4),
                    "blue": round(blue_mean, 4),
                    "brightness": round(brightness, 4),
                },
                "seasonalSignals": seasonal,
                "daylightSignals": daypart,
            }
            observed_latitude, observed_longitude, exif_timestamp, exif_caveats = _extract_exif_metadata(image)
            perceptual_hash = _average_hash(grayscale)
            if observed_latitude is not None:
                metadata["observedLatitude"] = observed_latitude
            if observed_longitude is not None:
                metadata["observedLongitude"] = observed_longitude
            if exif_timestamp is not None:
                metadata["exifTimestamp"] = exif_timestamp
            return {
                "width": width,
                "height": height,
                "perceptual_hash": perceptual_hash,
                "observed_latitude": observed_latitude,
                "observed_longitude": observed_longitude,
                "exif_timestamp": exif_timestamp,
                "metadata": metadata,
                "caveats": exif_caveats,
            }
    except (UnidentifiedImageError, OSError):
        return None


def run_media_ocr(
    settings: Settings,
    *,
    artifact_path: str | None,
    engine: str,
    preprocess_mode: str,
    fixture_text: str | None,
    fixture_blocks: list[dict[str, Any]] | None,
) -> MediaOcrRunResult:
    if fixture_text is not None or fixture_blocks:
        blocks = _fixture_ocr_blocks(fixture_text, fixture_blocks or [])
        return MediaOcrRunResult(
            status="completed",
            engine="fixture",
            engine_version="fixture-v1",
            raw_text=_normalize_text("\n".join(block.text for block in blocks)),
            preprocessing=["fixture"],
            mean_confidence=_mean_confidence(blocks),
            blocks=blocks,
            metadata={"fixture": True},
            caveats=["Fixture OCR is deterministic test input, not a real OCR engine result."],
            selected_result=True,
            attempt_index=0,
        )
    if artifact_path is None:
        return MediaOcrRunResult(
            status="rejected",
            engine="none",
            engine_version=None,
            raw_text="",
            preprocessing=[],
            mean_confidence=None,
            blocks=[],
            caveats=["OCR requires a locally stored media artifact path."],
        )
    chosen_engine = (settings.source_discovery_media_ocr_default_engine if engine == "auto" else engine).strip().lower()
    if chosen_engine == "tesseract":
        return _run_tesseract_ocr(settings, Path(artifact_path), preprocess_mode=preprocess_mode)
    if chosen_engine == "rapidocr_onnx":
        return _run_rapidocr(settings, Path(artifact_path), preprocess_mode=preprocess_mode)
    return MediaOcrRunResult(
        status="rejected",
        engine=chosen_engine,
        engine_version=None,
        raw_text="",
        preprocessing=[],
        mean_confidence=None,
        blocks=[],
        caveats=["Unsupported OCR engine. Supported engines are fixture, tesseract, and rapidocr_onnx."],
    )


def interpret_media_artifact(
    settings: Settings,
    *,
    artifact_path: str | None,
    artifact_metadata: dict[str, Any],
    observed_latitude: float | None,
    observed_longitude: float | None,
    exif_timestamp: str | None,
    ocr_text: str | None,
    captions: list[str],
    adapter: str,
    model: str | None,
    allow_local_ai: bool,
    fixture_result: dict[str, Any] | None,
) -> MediaInterpretationResult:
    if fixture_result is not None:
        return _fixture_interpretation(fixture_result, observed_latitude=observed_latitude, observed_longitude=observed_longitude)
    deterministic = _deterministic_interpretation(
        artifact_metadata=artifact_metadata,
        observed_latitude=observed_latitude,
        observed_longitude=observed_longitude,
        exif_timestamp=exif_timestamp,
        ocr_text=ocr_text,
        captions=captions,
    )
    resolved_adapter = adapter.strip().lower()
    if not allow_local_ai:
        return deterministic
    should_try_local = resolved_adapter in {"ollama", "openai_compat_local"} or (
        resolved_adapter == "auto" and _deterministic_result_needs_local_assist(deterministic)
    )
    if not should_try_local:
        return deterministic
    local_result: MediaInterpretationResult | None = None
    if resolved_adapter in {"auto", "ollama"}:
        local_result = _try_ollama_interpretation(
            settings,
            artifact_path=artifact_path,
            artifact_metadata=artifact_metadata,
            ocr_text=ocr_text,
            captions=captions,
            model=model,
        )
    if local_result is None and resolved_adapter in {"auto", "openai_compat_local"}:
        local_result = _try_openai_compat_local_interpretation(
            settings,
            artifact_path=artifact_path,
            artifact_metadata=artifact_metadata,
            ocr_text=ocr_text,
            captions=captions,
            model=model,
        )
    if local_result is None:
        if resolved_adapter in {"ollama", "openai_compat_local"}:
            deterministic.caveats.append("Requested local vision adapter was unavailable, so the system fell back to deterministic signals only.")
        elif resolved_adapter == "auto":
            deterministic.caveats.append("Deterministic interpretation stayed primary because no local vision adapter completed successfully.")
        return deterministic
    return _merge_local_interpretation_with_deterministic(local_result, deterministic)


def geolocate_media_artifact(
    settings: Settings,
    *,
    artifact_path: str | None,
    artifact_metadata: dict[str, Any],
    observed_latitude: float | None,
    observed_longitude: float | None,
    exif_timestamp: str | None,
    ocr_text: str | None,
    captions: list[str],
    engine: str,
    analyst_adapter: str,
    model: str | None,
    analyst_model: str | None,
    allow_local_ai: bool,
    fixture_result: dict[str, Any] | None,
    candidate_labels: list[str],
    prior_place_hypothesis: str | None,
    prior_place_confidence: float | None,
    prior_place_basis: str | None,
    prior_geolocation_hypothesis: str | None,
    prior_geolocation_confidence: float | None,
    prior_geolocation_basis: str | None,
    inherited_context: dict[str, Any] | None = None,
) -> MediaGeolocationResult:
    if fixture_result is not None:
        return _fixture_geolocation_result(fixture_result)

    resolved_engine = engine.strip().lower() or settings.source_discovery_media_geolocation_default_engine.strip().lower() or "fusion"
    if resolved_engine == "auto":
        resolved_engine = settings.source_discovery_media_geolocation_default_engine.strip().lower() or "fusion"
    if resolved_engine not in {"deterministic", "geoclip", "streetclip", "fusion"}:
        return MediaGeolocationResult(
            status="rejected",
            engine=resolved_engine,
            model_name=model,
            analyst_adapter=analyst_adapter if analyst_adapter.strip().lower() != "none" else None,
            analyst_model_name=analyst_model,
            candidate_count=0,
            top_label=None,
            top_latitude=None,
            top_longitude=None,
            top_confidence=None,
            top_basis=None,
            summary=None,
            reasoning_lines=[],
            candidates=[],
            caveats=["Unsupported media geolocation engine."],
        )

    clue_packet, deterministic_reasoning, deterministic_caveats = _extract_geolocation_clue_packet(
        settings=settings,
        observed_latitude=observed_latitude,
        observed_longitude=observed_longitude,
        exif_timestamp=exif_timestamp,
        ocr_text=ocr_text,
        captions=captions,
        artifact_metadata=artifact_metadata,
        prior_place_hypothesis=prior_place_hypothesis,
        prior_place_confidence=prior_place_confidence,
        prior_place_basis=prior_place_basis,
        prior_geolocation_hypothesis=prior_geolocation_hypothesis,
        prior_geolocation_confidence=prior_geolocation_confidence,
        prior_geolocation_basis=prior_geolocation_basis,
        inherited_context=inherited_context,
    )
    deterministic_candidates = _build_deterministic_geolocation_candidates(
        clue_packet=clue_packet,
        observed_latitude=observed_latitude,
        observed_longitude=observed_longitude,
        prior_place_hypothesis=prior_place_hypothesis,
        prior_place_confidence=prior_place_confidence,
        prior_place_basis=prior_place_basis,
        prior_geolocation_hypothesis=prior_geolocation_hypothesis,
        prior_geolocation_confidence=prior_geolocation_confidence,
        prior_geolocation_basis=prior_geolocation_basis,
    )
    all_candidates = list(deterministic_candidates)
    reasoning_lines = list(deterministic_reasoning)
    caveats = list(deterministic_caveats)
    model_name_used: str | None = None
    analyst_result: MediaGeolocationAnalystResult | None = None
    engine_attempts: list[MediaGeolocationEngineAttempt] = [
        MediaGeolocationEngineAttempt(
            engine="deterministic",
            role="core_clue_engine",
            status="completed" if deterministic_candidates else "completed",
            model_name=None,
            warm_state="stateless",
            availability_reason=None,
            produced_candidate_count=len(deterministic_candidates),
            metadata={
                "clueCounts": {
                    "coordinate": len(clue_packet.coordinate_clues),
                    "placeText": len(clue_packet.place_text_clues),
                    "scriptLanguage": len(clue_packet.script_language_clues),
                    "environment": len(clue_packet.environment_clues),
                    "time": len(clue_packet.time_clues),
                    "rejected": len(clue_packet.rejected_clues),
                }
            },
            caveats=list(deterministic_caveats),
        )
    ]
    candidate_labels_for_rerank = _build_candidate_label_bank(
        supplied_labels=candidate_labels,
        clue_packet=clue_packet,
        inherited_context=inherited_context,
    )

    if resolved_engine in {"geoclip", "fusion"}:
        geoclip_candidates, geoclip_model_name, geoclip_reasoning, geoclip_caveats, geoclip_attempt = _try_geoclip_candidates(
            settings,
            artifact_path=artifact_path,
            max_candidates=max(1, settings.source_discovery_media_geolocation_max_candidates),
        )
        engine_attempts.append(geoclip_attempt)
        if geoclip_candidates:
            all_candidates.extend(geoclip_candidates)
            reasoning_lines.extend(geoclip_reasoning)
            model_name_used = geoclip_model_name or model_name_used
        caveats.extend(geoclip_caveats)

    if resolved_engine in {"streetclip", "fusion"}:
        streetclip_candidates, streetclip_model_name, streetclip_reasoning, streetclip_caveats, streetclip_attempt = _try_streetclip_candidates(
            settings,
            artifact_path=artifact_path,
            candidate_labels=candidate_labels_for_rerank,
            max_candidates=max(1, settings.source_discovery_media_geolocation_max_candidates),
        )
        engine_attempts.append(streetclip_attempt)
        if streetclip_candidates:
            all_candidates.extend(streetclip_candidates)
            reasoning_lines.extend(streetclip_reasoning)
            if resolved_engine == "streetclip" or model_name_used is None:
                model_name_used = streetclip_model_name or model_name_used
        caveats.extend(streetclip_caveats)

    if allow_local_ai:
        analyst_result, analyst_attempt = _try_local_geolocation_analyst(
            settings,
            artifact_path=artifact_path,
            artifact_metadata=artifact_metadata,
            ocr_text=ocr_text,
            captions=captions,
            analyst_adapter=analyst_adapter,
            analyst_model=analyst_model,
            run_local=resolved_engine != "deterministic" or not all_candidates or max((candidate.confidence or 0.0) for candidate in all_candidates) < 0.75,
        )
        if analyst_attempt is not None:
            engine_attempts.append(analyst_attempt)
    if analyst_result is not None:
        all_candidates.extend(analyst_result.candidates)
        reasoning_lines.extend(analyst_result.reasoning_lines)
        caveats.extend(analyst_result.caveats)
    elif allow_local_ai and analyst_adapter.strip().lower() not in {"", "none", "deterministic", "auto"}:
        caveats.append("Requested local geolocation analyst was unavailable, so the run fell back to deterministic and specialized-engine clues only.")

    capped_candidates = _fuse_geolocation_candidates(
        all_candidates,
        clue_packet=clue_packet,
        engine_attempts=engine_attempts,
        observed_latitude=observed_latitude,
        observed_longitude=observed_longitude,
        inherited_context=inherited_context,
        analyst_result=analyst_result,
        max_candidates=max(1, settings.source_discovery_media_geolocation_max_candidates),
    )
    top_candidate = capped_candidates[0] if capped_candidates else None
    summary = _build_geolocation_summary(top_candidate, analyst_result, deterministic_reasoning)
    status = "completed" if capped_candidates or summary else "unavailable"
    metadata = {
        "requestedEngine": engine,
        "resolvedEngine": resolved_engine,
        "requestedAnalystAdapter": analyst_adapter,
        "candidateLabelsSupplied": candidate_labels[:32],
        "artifactMetadataHints": {
            "mimeType": artifact_metadata.get("mimeTypeSniffed"),
            "width": artifact_metadata.get("width"),
            "height": artifact_metadata.get("height"),
        },
        "inheritedContext": inherited_context or {},
    }
    if analyst_result is not None:
        metadata["analystMetadata"] = analyst_result.metadata
    if top_candidate is None and resolved_engine in {"geoclip", "streetclip"}:
        caveats.append("No geolocation candidates were produced by the requested specialized engine under the current local-runtime constraints.")
    engine_agreement = _summarize_engine_agreement(capped_candidates, engine_attempts)
    supporting_evidence = top_candidate.supporting_evidence if top_candidate is not None else []
    contradicting_evidence = top_candidate.contradicting_evidence if top_candidate is not None else []
    provenance_chain = top_candidate.provenance_chain if top_candidate is not None else []
    inherited_from_artifact_ids = _collect_inherited_artifact_ids(clue_packet=clue_packet, candidates=capped_candidates)
    return MediaGeolocationResult(
        status=status,
        engine=resolved_engine,
        model_name=model_name_used,
        analyst_adapter=analyst_result.adapter if analyst_result is not None else (analyst_adapter if analyst_adapter.strip().lower() != "none" else None),
        analyst_model_name=analyst_result.model_name if analyst_result is not None else analyst_model,
        candidate_count=len(capped_candidates),
        top_label=top_candidate.label if top_candidate is not None else None,
        top_latitude=top_candidate.latitude if top_candidate is not None else None,
        top_longitude=top_candidate.longitude if top_candidate is not None else None,
        top_confidence=top_candidate.confidence if top_candidate is not None else None,
        top_confidence_ceiling=top_candidate.confidence_ceiling if top_candidate is not None else None,
        top_basis="; ".join(top_candidate.basis[:3]) if top_candidate is not None and top_candidate.basis else None,
        summary=summary,
        confidence_ceiling=top_candidate.confidence_ceiling if top_candidate is not None else None,
        supporting_evidence=supporting_evidence,
        contradicting_evidence=contradicting_evidence,
        engine_agreement=engine_agreement,
        provenance_chain=provenance_chain,
        inherited_from_artifact_ids=inherited_from_artifact_ids,
        clue_packet=clue_packet,
        engine_attempts=engine_attempts,
        reasoning_lines=reasoning_lines[:16],
        candidates=capped_candidates,
        metadata=metadata,
        caveats=_dedupe_text_list(
            caveats
            + [
                "Media geolocation is a hypothesis workflow. Candidate locations require review and corroboration before they affect source truth or reputation.",
                "No people recognition, identity inference, or accusation workflow is allowed in media geolocation.",
            ]
        ),
    )


def compare_media_artifacts(
    settings: Settings,
    *,
    left_artifact_path: str | None,
    right_artifact_path: str | None,
    left_content_hash: str,
    right_content_hash: str,
    left_perceptual_hash: str | None,
    right_perceptual_hash: str | None,
    left_canonical_url: str,
    right_canonical_url: str,
    left_parent_page_url: str | None,
    right_parent_page_url: str | None,
    left_exif_timestamp: str | None,
    right_exif_timestamp: str | None,
    left_ocr_text: str | None,
    right_ocr_text: str | None,
) -> MediaComparisonResult:
    exact_hash_match = left_content_hash == right_content_hash
    perceptual_distance = _perceptual_hash_distance(left_perceptual_hash, right_perceptual_hash)
    time_delta_seconds = _time_delta_seconds(left_exif_timestamp, right_exif_timestamp)
    ocr_text_similarity = _token_similarity(left_ocr_text or "", right_ocr_text or "") if (left_ocr_text or right_ocr_text) else None
    confidence_basis: list[str] = []
    caveats: list[str] = []
    pixel_metrics = _compare_image_pixels(left_artifact_path, right_artifact_path)
    ssim_score = pixel_metrics.get("ssim_score")
    histogram_similarity = pixel_metrics.get("histogram_similarity")
    edge_similarity = pixel_metrics.get("edge_similarity")
    if pixel_metrics.get("caveat"):
        caveats.append(str(pixel_metrics["caveat"]))

    if exact_hash_match:
        confidence_basis.append("Exact content hashes match.")
    if perceptual_distance is not None:
        confidence_basis.append(f"Perceptual hash distance is {perceptual_distance}.")
    if ssim_score is not None:
        confidence_basis.append(f"Resized grayscale SSIM is {ssim_score:.4f}.")
    if histogram_similarity is not None:
        confidence_basis.append(f"Color histogram similarity is {histogram_similarity:.4f}.")
    if edge_similarity is not None:
        confidence_basis.append(f"Edge-map similarity is {edge_similarity:.4f}.")
    if ocr_text_similarity is not None:
        confidence_basis.append(f"OCR text similarity is {ocr_text_similarity:.4f}.")
    if time_delta_seconds is not None:
        confidence_basis.append(f"EXIF timestamp delta is {time_delta_seconds} seconds.")
    if canonicalize_url(left_canonical_url) == canonicalize_url(right_canonical_url):
        confidence_basis.append("Canonical media URLs match.")
    if left_parent_page_url and right_parent_page_url and canonicalize_url(left_parent_page_url) == canonicalize_url(right_parent_page_url):
        confidence_basis.append("Parent page URLs match.")

    comparison_kind = "uncertain"
    auto_signal_kind: str | None = None
    confidence_score = 0.42
    if exact_hash_match:
        comparison_kind = "exact_duplicate"
        auto_signal_kind = "duplicate_cluster_joined"
        confidence_score = 0.99
    elif (
        perceptual_distance is not None
        and perceptual_distance <= settings.source_discovery_media_phash_near_distance
        and (ssim_score is None or ssim_score >= settings.source_discovery_media_ssim_duplicate_threshold)
    ):
        comparison_kind = "near_duplicate"
        auto_signal_kind = "duplicate_cluster_joined"
        confidence_score = 0.92
    elif (
        ssim_score is not None
        and ssim_score >= settings.source_discovery_media_ssim_change_threshold
        and (edge_similarity is None or edge_similarity >= 0.62)
    ):
        comparison_kind = "same_scene_minor_change"
        auto_signal_kind = "minor_change_detected"
        confidence_score = 0.78
    elif (
        (ocr_text_similarity is not None and ocr_text_similarity >= 0.38)
        or (left_parent_page_url and right_parent_page_url and canonicalize_url(left_parent_page_url) == canonicalize_url(right_parent_page_url))
        or (time_delta_seconds is not None and time_delta_seconds <= 60 * 60 * 24 * 30)
    ):
        comparison_kind = "same_location_major_change"
        auto_signal_kind = "major_change_detected"
        confidence_score = 0.68
    elif (
        ssim_score is not None
        and ssim_score < 0.36
        and (histogram_similarity is None or histogram_similarity < 0.46)
        and (edge_similarity is None or edge_similarity < 0.42)
    ):
        comparison_kind = "different_scene"
        auto_signal_kind = "different_scene_conflict"
        confidence_score = 0.73
    return MediaComparisonResult(
        status="completed",
        comparison_kind=comparison_kind,
        algorithm_version="media-compare-v1",
        exact_hash_match=exact_hash_match,
        perceptual_hash_distance=perceptual_distance,
        ssim_score=ssim_score,
        histogram_similarity=histogram_similarity,
        edge_similarity=edge_similarity,
        ocr_text_similarity=ocr_text_similarity,
        time_delta_seconds=time_delta_seconds,
        confidence_score=round(confidence_score, 4),
        confidence_basis=confidence_basis,
        auto_signal_kind=auto_signal_kind,
        metadata=pixel_metrics,
        caveats=caveats + [
            "Deterministic media comparison may adjust review confidence but does not directly change source reputation or final truth state.",
        ],
    )


def sample_media_frames(
    settings: Settings,
    *,
    media_url: str,
    fixture_frames_base64: list[str],
    source_span_seconds: int,
    max_frames: int,
    sample_interval_seconds: int,
    request_budget: int,
) -> MediaFrameSampleResult:
    allowed_span = max(1, settings.source_discovery_media_frame_max_span_seconds)
    allowed_frames = max(1, settings.source_discovery_media_frame_max_frames)
    minimum_interval = max(1, settings.source_discovery_media_frame_min_interval_seconds)
    if source_span_seconds > allowed_span:
        return MediaFrameSampleResult(
            status="rejected",
            sampler="ffmpeg",
            frames=[],
            sample_interval_seconds=sample_interval_seconds,
            source_span_seconds=source_span_seconds,
            caveats=[f"Frame sampling span exceeds the configured cap of {allowed_span} seconds."],
        )
    if max_frames > allowed_frames:
        return MediaFrameSampleResult(
            status="rejected",
            sampler="ffmpeg",
            frames=[],
            sample_interval_seconds=sample_interval_seconds,
            source_span_seconds=source_span_seconds,
            caveats=[f"Frame sampling count exceeds the configured cap of {allowed_frames} frames."],
        )
    if sample_interval_seconds < minimum_interval:
        return MediaFrameSampleResult(
            status="rejected",
            sampler="ffmpeg",
            frames=[],
            sample_interval_seconds=sample_interval_seconds,
            source_span_seconds=source_span_seconds,
            caveats=[f"Frame sampling interval must be at least {minimum_interval} seconds."],
        )
    if fixture_frames_base64:
        frames = [base64.b64decode(item.encode("utf-8"), validate=True) for item in fixture_frames_base64[:allowed_frames]]
        return MediaFrameSampleResult(
            status="completed",
            sampler="fixture",
            frames=frames,
            sample_interval_seconds=sample_interval_seconds,
            source_span_seconds=source_span_seconds,
            metadata={"fixture": True},
            caveats=["Fixture frame sampling is deterministic test input, not a live ffmpeg extraction."],
        )
    if request_budget <= 0:
        return MediaFrameSampleResult(
            status="rejected",
            sampler="ffmpeg",
            frames=[],
            sample_interval_seconds=sample_interval_seconds,
            source_span_seconds=source_span_seconds,
            caveats=["Frame sampling requires fixture frames or a positive request budget."],
        )
    ffmpeg_binary = settings.source_discovery_media_ffmpeg_binary.strip() or "ffmpeg"
    resolved_binary = shutil.which(ffmpeg_binary) or (ffmpeg_binary if Path(ffmpeg_binary).exists() else None)
    if resolved_binary is None:
        return MediaFrameSampleResult(
            status="unavailable",
            sampler="ffmpeg",
            frames=[],
            sample_interval_seconds=sample_interval_seconds,
            source_span_seconds=source_span_seconds,
            caveats=["ffmpeg was not found on this machine. Install it or use fixture frames for tests."],
        )
    cache_dir = Path(resolve_runtime_paths(settings)["cache_dir"]) / "media-frame-samples" / hashlib.sha256(media_url.encode("utf-8")).hexdigest()[:24]
    cache_dir.mkdir(parents=True, exist_ok=True)
    pattern = cache_dir / "frame-%03d.png"
    fps = f"fps=1/{sample_interval_seconds}"
    command = [
        str(resolved_binary),
        "-y",
        "-i",
        media_url,
        "-t",
        str(source_span_seconds),
        "-vf",
        fps,
        "-frames:v",
        str(max_frames),
        str(pattern),
    ]
    result = subprocess.run(command, capture_output=True, text=True, timeout=120, check=False)
    if result.returncode != 0:
        return MediaFrameSampleResult(
            status="failed",
            sampler="ffmpeg",
            frames=[],
            sample_interval_seconds=sample_interval_seconds,
            source_span_seconds=source_span_seconds,
            caveats=[_normalize_text(result.stderr) or "ffmpeg frame extraction returned a non-zero exit code."],
        )
    frames: list[bytes] = []
    for frame_path in sorted(cache_dir.glob("frame-*.png"))[:max_frames]:
        frames.append(frame_path.read_bytes())
    return MediaFrameSampleResult(
        status="completed",
        sampler="ffmpeg",
        frames=frames,
        sample_interval_seconds=sample_interval_seconds,
        source_span_seconds=source_span_seconds,
        metadata={"frameDirectory": str(cache_dir)},
        caveats=[
            "Frame sampling is bounded and should be used only for explicit no-auth media or user-approved backend tasks.",
        ],
    )


def canonicalize_url(value: str | None, *, base_url: str | None = None) -> str | None:
    normalized = _normalize_text(value or "")
    if not normalized:
        return None
    absolute = urljoin(base_url or normalized, normalized)
    split = urlsplit(absolute)
    filtered_pairs = []
    for key, item in parse_qsl(split.query, keep_blank_values=True):
        lowered = key.casefold()
        if lowered.startswith("utm_") or lowered in {"fbclid", "gclid", "igshid", "ref", "ref_src"}:
            continue
        filtered_pairs.append((key, item))
    query = urlencode(filtered_pairs, doseq=True)
    return urlunsplit((split.scheme, split.netloc, split.path, query, ""))


def _sniff_mime_type(payload: bytes, *, content_type: str | None, url: str) -> str | None:
    header = (content_type or "").split(";", 1)[0].strip().lower()
    if header:
        return header
    if payload.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if payload.startswith(b"\xff\xd8"):
        return "image/jpeg"
    if payload.startswith((b"GIF87a", b"GIF89a")):
        return "image/gif"
    if payload.startswith(b"RIFF") and payload[8:12] == b"WEBP":
        return "image/webp"
    lowered = url.casefold()
    if lowered.endswith(".png"):
        return "image/png"
    if lowered.endswith((".jpg", ".jpeg")):
        return "image/jpeg"
    if lowered.endswith(".gif"):
        return "image/gif"
    if lowered.endswith(".webp"):
        return "image/webp"
    return None


def _parse_image_dimensions(payload: bytes) -> tuple[int | None, int | None]:
    if payload.startswith(b"\x89PNG\r\n\x1a\n") and len(payload) >= 24:
        return int.from_bytes(payload[16:20], "big"), int.from_bytes(payload[20:24], "big")
    if payload.startswith((b"GIF87a", b"GIF89a")) and len(payload) >= 10:
        return int.from_bytes(payload[6:8], "little"), int.from_bytes(payload[8:10], "little")
    if payload.startswith(b"\xff\xd8"):
        index = 2
        while index + 9 < len(payload):
            if payload[index] != 0xFF:
                index += 1
                continue
            marker = payload[index + 1]
            if marker in {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}:
                height = int.from_bytes(payload[index + 5 : index + 7], "big")
                width = int.from_bytes(payload[index + 7 : index + 9], "big")
                return width, height
            block_length = int.from_bytes(payload[index + 2 : index + 4], "big")
            if block_length <= 0:
                break
            index += block_length + 2
    if payload.startswith(b"RIFF") and payload[8:12] == b"WEBP" and len(payload) >= 30:
        if payload[12:16] == b"VP8 " and len(payload) >= 30:
            return payload[26] | (payload[27] << 8), payload[28] | (payload[29] << 8)
        if payload[12:16] == b"VP8L" and len(payload) >= 25:
            bits = int.from_bytes(payload[21:25], "little")
            return (bits & 0x3FFF) + 1, ((bits >> 14) & 0x3FFF) + 1
    return None, None


def _extension_for_mime(mime_type: str | None, url: str) -> str:
    if mime_type == "image/png":
        return ".png"
    if mime_type == "image/jpeg":
        return ".jpg"
    if mime_type == "image/gif":
        return ".gif"
    if mime_type == "image/webp":
        return ".webp"
    suffix = Path(urlsplit(url).path).suffix
    return suffix if suffix else ".bin"


def _average_hash(grayscale_image) -> str | None:
    if Image is None:
        return None
    reduced = grayscale_image.resize((8, 8))
    pixels = list(reduced.getdata())
    if not pixels:
        return None
    average = sum(int(pixel) for pixel in pixels) / len(pixels)
    bits = "".join("1" if int(pixel) >= average else "0" for pixel in pixels)
    return f"{int(bits, 2):016x}"


def _average_hash_from_pixels(width: int, height: int, pixels: list[tuple[int, int, int]]) -> str | None:
    if width <= 0 or height <= 0 or not pixels:
        return None
    reduced: list[int] = []
    for y_index in range(8):
        source_y = min(height - 1, int((y_index / 8) * height))
        for x_index in range(8):
            source_x = min(width - 1, int((x_index / 8) * width))
            red, green_channel, blue = pixels[(source_y * width) + source_x]
            reduced.append(int((red + green_channel + blue) / 3))
    average = sum(reduced) / len(reduced)
    bits = "".join("1" if value >= average else "0" for value in reduced)
    return f"{int(bits, 2):016x}"


def _seasonal_color_signals(image) -> dict[str, float]:
    pixels = list(image.getdata())
    return _seasonal_color_signals_from_pixels(pixels)


def _seasonal_color_signals_from_pixels(pixels: list[tuple[int, int, int]]) -> dict[str, float]:
    total = max(len(pixels), 1)
    green = 0
    snow = 0
    warm = 0
    water_sky = 0
    for red, green_channel, blue in pixels:
        red_f = red / 255.0
        green_f = green_channel / 255.0
        blue_f = blue / 255.0
        saturation = max(red_f, green_f, blue_f) - min(red_f, green_f, blue_f)
        if green_f > red_f * 1.08 and green_f > blue_f * 1.05 and green_f > 0.28:
            green += 1
        if red_f > 0.72 and green_f > 0.72 and blue_f > 0.72 and saturation < 0.14:
            snow += 1
        if red_f > 0.45 and green_f > 0.28 and red_f > blue_f * 1.1:
            warm += 1
        if blue_f > red_f * 1.08 and blue_f > green_f * 1.02 and blue_f > 0.3:
            water_sky += 1
    return {
        "greenRatio": round(green / total, 4),
        "snowRatio": round(snow / total, 4),
        "warmRatio": round(warm / total, 4),
        "blueRatio": round(water_sky / total, 4),
    }


def _daylight_signals(image, *, brightness: float) -> dict[str, float]:
    pixels = list(image.getdata())
    return _daylight_signals_from_pixels(pixels, brightness=brightness, width=getattr(image, "width", None))


def _daylight_signals_from_pixels(
    pixels: list[tuple[int, int, int]],
    *,
    brightness: float,
    width: int | None = None,
) -> dict[str, float]:
    total = max(len(pixels), 1)
    warm_highlights = 0
    dark_pixels = 0
    left_brightness_total = 0.0
    right_brightness_total = 0.0
    left_count = 0
    right_count = 0
    resolved_width = width if width and width > 0 else None
    for index, (red, green_channel, blue) in enumerate(pixels):
        red_f = red / 255.0
        green_f = green_channel / 255.0
        blue_f = blue / 255.0
        pixel_brightness = (red_f + green_f + blue_f) / 3.0
        if red_f > green_f and green_f > blue_f and red_f > 0.4:
            warm_highlights += 1
        if max(red_f, green_f, blue_f) < 0.18:
            dark_pixels += 1
        if resolved_width is not None:
            x_index = index % resolved_width
            if x_index < (resolved_width / 2):
                left_brightness_total += pixel_brightness
                left_count += 1
            else:
                right_brightness_total += pixel_brightness
                right_count += 1
    left_brightness = round(left_brightness_total / max(left_count, 1), 4) if resolved_width is not None else 0.0
    right_brightness = round(right_brightness_total / max(right_count, 1), 4) if resolved_width is not None else 0.0
    result = {
        "brightness": round(brightness, 4),
        "darkPixelRatio": round(dark_pixels / total, 4),
        "warmHighlightRatio": round(warm_highlights / total, 4),
    }
    if resolved_width is not None:
        result["leftBrightness"] = left_brightness
        result["rightBrightness"] = right_brightness
        if abs(left_brightness - right_brightness) >= 0.08:
            result["dominantBrightSide"] = "left" if left_brightness > right_brightness else "right"
    return result


def _fallback_image_metadata(payload: bytes, *, mime_type: str | None) -> dict[str, Any] | None:
    if mime_type == "image/png":
        return _fallback_png_metadata(payload)
    return None


def _fallback_png_metadata(payload: bytes) -> dict[str, Any] | None:
    parsed = _decode_png_rgb(payload)
    if parsed is None:
        return None
    width, height, pixels = parsed
    brightness = round(
        sum((red + green_channel + blue) / 3 for red, green_channel, blue in pixels) / (255.0 * max(len(pixels), 1)),
        4,
    )
    metadata = {
        "format": "PNG",
        "mode": "RGB",
        "channelMeans": _channel_means_from_pixels(pixels, brightness=brightness),
        "seasonalSignals": _seasonal_color_signals_from_pixels(pixels),
        "daylightSignals": _daylight_signals_from_pixels(pixels, brightness=brightness, width=width),
        "fallbackDecoder": "png-rgb-stdlib",
    }
    return {
        "width": width,
        "height": height,
        "perceptual_hash": _average_hash_from_pixels(width, height, pixels),
        "observed_latitude": None,
        "observed_longitude": None,
        "exif_timestamp": None,
        "metadata": metadata,
        "caveats": ["PNG image analysis used a stdlib fallback decoder without EXIF support."],
    }


def _channel_means_from_pixels(pixels: list[tuple[int, int, int]], *, brightness: float) -> dict[str, float]:
    total = max(len(pixels), 1)
    red = round(sum(pixel[0] for pixel in pixels) / (255.0 * total), 4)
    green = round(sum(pixel[1] for pixel in pixels) / (255.0 * total), 4)
    blue = round(sum(pixel[2] for pixel in pixels) / (255.0 * total), 4)
    return {
        "red": red,
        "green": green,
        "blue": blue,
        "brightness": round(brightness, 4),
    }


def _decode_png_rgb(payload: bytes) -> tuple[int, int, list[tuple[int, int, int]]] | None:
    if not payload.startswith(b"\x89PNG\r\n\x1a\n"):
        return None
    index = 8
    width: int | None = None
    height: int | None = None
    bit_depth: int | None = None
    color_type: int | None = None
    compressed_parts: list[bytes] = []
    while index + 8 <= len(payload):
        length = int.from_bytes(payload[index : index + 4], "big")
        chunk_type = payload[index + 4 : index + 8]
        data_start = index + 8
        data_end = data_start + length
        if data_end + 4 > len(payload):
            return None
        data = payload[data_start:data_end]
        if chunk_type == b"IHDR" and len(data) >= 13:
            width = int.from_bytes(data[0:4], "big")
            height = int.from_bytes(data[4:8], "big")
            bit_depth = data[8]
            color_type = data[9]
        elif chunk_type == b"IDAT":
            compressed_parts.append(data)
        elif chunk_type == b"IEND":
            break
        index = data_end + 4
    if width is None or height is None or bit_depth != 8 or color_type != 2:
        return None
    try:
        raw = zlib.decompress(b"".join(compressed_parts))
    except zlib.error:
        return None
    stride = width * 3
    expected = height * (stride + 1)
    if len(raw) < expected:
        return None
    rows: list[bytes] = []
    previous = bytearray(stride)
    offset = 0
    for _ in range(height):
        filter_type = raw[offset]
        row = bytearray(raw[offset + 1 : offset + 1 + stride])
        _undo_png_filter(row, previous, filter_type, bytes_per_pixel=3)
        rows.append(bytes(row))
        previous = row
        offset += stride + 1
    pixels: list[tuple[int, int, int]] = []
    for row in rows:
        for pixel_offset in range(0, len(row), 3):
            pixels.append((row[pixel_offset], row[pixel_offset + 1], row[pixel_offset + 2]))
    return width, height, pixels


def _undo_png_filter(row: bytearray, previous: bytearray, filter_type: int, *, bytes_per_pixel: int) -> None:
    if filter_type == 0:
        return
    if filter_type == 1:
        for index in range(len(row)):
            left = row[index - bytes_per_pixel] if index >= bytes_per_pixel else 0
            row[index] = (row[index] + left) & 0xFF
        return
    if filter_type == 2:
        for index in range(len(row)):
            row[index] = (row[index] + previous[index]) & 0xFF
        return
    if filter_type == 3:
        for index in range(len(row)):
            left = row[index - bytes_per_pixel] if index >= bytes_per_pixel else 0
            up = previous[index]
            row[index] = (row[index] + ((left + up) // 2)) & 0xFF
        return
    if filter_type == 4:
        for index in range(len(row)):
            left = row[index - bytes_per_pixel] if index >= bytes_per_pixel else 0
            up = previous[index]
            up_left = previous[index - bytes_per_pixel] if index >= bytes_per_pixel else 0
            row[index] = (row[index] + _paeth_predictor(left, up, up_left)) & 0xFF


def _paeth_predictor(left: int, up: int, up_left: int) -> int:
    predictor = left + up - up_left
    left_distance = abs(predictor - left)
    up_distance = abs(predictor - up)
    up_left_distance = abs(predictor - up_left)
    if left_distance <= up_distance and left_distance <= up_left_distance:
        return left
    if up_distance <= up_left_distance:
        return up
    return up_left


def _extract_exif_metadata(image) -> tuple[float | None, float | None, str | None, list[str]]:
    caveats: list[str] = []
    try:
        exif = image.getexif()
    except Exception:  # pragma: no cover - PIL backend variance
        return None, None, None, ["Image EXIF metadata could not be read."]
    if not exif:
        return None, None, None, ["Image had no usable EXIF metadata."]
    gps_info = exif.get(34853)
    exif_timestamp = exif.get(36867) or exif.get(306)
    latitude: float | None = None
    longitude: float | None = None
    if isinstance(gps_info, dict):
        latitude = _gps_dms_to_decimal(gps_info.get(2), ref=gps_info.get(1))
        longitude = _gps_dms_to_decimal(gps_info.get(4), ref=gps_info.get(3))
    return latitude, longitude, _normalize_text(str(exif_timestamp)) or None, caveats


def _gps_dms_to_decimal(value: Any, *, ref: Any) -> float | None:
    if not isinstance(value, tuple) or len(value) != 3:
        return None
    try:
        degrees = _ratio_to_float(value[0])
        minutes = _ratio_to_float(value[1])
        seconds = _ratio_to_float(value[2])
    except (TypeError, ZeroDivisionError):
        return None
    decimal = degrees + (minutes / 60.0) + (seconds / 3600.0)
    if str(ref).strip().upper() in {"S", "W"}:
        decimal *= -1
    return round(decimal, 6)


def _ratio_to_float(value: Any) -> float:
    if hasattr(value, "numerator") and hasattr(value, "denominator"):
        return float(value.numerator) / float(value.denominator)
    if isinstance(value, tuple) and len(value) == 2:
        return float(value[0]) / float(value[1])
    return float(value)


def _prepare_ocr_input(settings: Settings, artifact_path: Path, *, preprocess_mode: str) -> tuple[Path, list[str]]:
    if preprocess_mode == "none" or Image is None or ImageOps is None:
        return artifact_path, ["none"]
    cache_dir = Path(resolve_runtime_paths(settings)["cache_dir"]) / "media-ocr"
    cache_dir.mkdir(parents=True, exist_ok=True)
    with Image.open(artifact_path) as image:
        rgb = ImageOps.exif_transpose(image).convert("L")
        transforms: list[str] = ["grayscale"]
        if preprocess_mode in {"auto", "high_contrast"}:
            rgb = ImageOps.autocontrast(rgb)
            transforms.append("autocontrast")
        if preprocess_mode == "auto" and min(rgb.size) < 1000:
            rgb = rgb.resize((rgb.width * 2, rgb.height * 2))
            transforms.append("upscale2x")
        if preprocess_mode == "threshold":
            rgb = rgb.point(lambda value: 255 if value >= 160 else 0)
            transforms.append("threshold160")
        if preprocess_mode == "sharpen":
            rgb = ImageOps.autocontrast(rgb)
            if ImageFilter is not None:
                rgb = rgb.filter(ImageFilter.SHARPEN)
            transforms.append("sharpen")
        if preprocess_mode == "text_region_crop":
            crop_box = (0, int(rgb.height * 0.55), rgb.width, rgb.height)
            rgb = rgb.crop(crop_box)
            transforms.append("bottom_text_region_crop")
        prepared_path = cache_dir / f"{artifact_path.stem}.ocr.png"
        rgb.save(prepared_path, format="PNG")
        return prepared_path, transforms


def _run_tesseract_ocr(settings: Settings, artifact_path: Path, *, preprocess_mode: str) -> MediaOcrRunResult:
    binary = settings.source_discovery_media_ocr_binary.strip() or "tesseract"
    resolved_binary = shutil.which(binary) or (binary if Path(binary).exists() else None)
    if resolved_binary is None:
        return MediaOcrRunResult(
            status="unavailable",
            engine="tesseract",
            engine_version=None,
            raw_text="",
            preprocessing=[],
            mean_confidence=None,
            blocks=[],
            caveats=["Tesseract was not found on this machine. Install it or use fixture OCR for tests."],
        )
    prepared_path, preprocessing = _prepare_ocr_input(settings, artifact_path, preprocess_mode=preprocess_mode)
    try:
        version_output = subprocess.run(
            [resolved_binary, "--version"],
            capture_output=True,
            text=True,
            timeout=8,
            check=False,
        )
        engine_version = _normalize_text(version_output.stdout.splitlines()[0] if version_output.stdout else "")
        tsv_output = subprocess.run(
            [resolved_binary, str(prepared_path), "stdout", "--psm", "6", "tsv"],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        if tsv_output.returncode != 0:
            return MediaOcrRunResult(
                status="failed",
                engine="tesseract",
                engine_version=engine_version or None,
                raw_text="",
                preprocessing=preprocessing,
                mean_confidence=None,
                blocks=[],
                caveats=[_normalize_text(tsv_output.stderr) or "Tesseract OCR returned a non-zero exit code."],
            )
        blocks = _parse_tesseract_tsv(tsv_output.stdout)
        return MediaOcrRunResult(
            status="completed",
            engine="tesseract",
            engine_version=engine_version or None,
            raw_text=_normalize_text("\n".join(block.text for block in blocks)),
            preprocessing=preprocessing,
            mean_confidence=_mean_confidence(blocks),
            blocks=blocks,
            metadata={"artifactPath": str(prepared_path)},
            caveats=["OCR text is derived from pixels and must remain linked to the original artifact for review."],
        )
    finally:
        if prepared_path != artifact_path and prepared_path.exists():
            prepared_path.unlink(missing_ok=True)


def _run_rapidocr(settings: Settings, artifact_path: Path, *, preprocess_mode: str) -> MediaOcrRunResult:
    if RapidOCR is None:
        return MediaOcrRunResult(
            status="unavailable",
            engine="rapidocr_onnx",
            engine_version=None,
            raw_text="",
            preprocessing=[],
            mean_confidence=None,
            blocks=[],
            caveats=["rapidocr_onnxruntime is not installed. Add the optional media dependency or use another OCR adapter."],
        )
    prepared_path, preprocessing = _prepare_ocr_input(settings, artifact_path, preprocess_mode=preprocess_mode)
    try:
        engine = RapidOCR()
        output = engine(str(prepared_path))
    except Exception as exc:  # pragma: no cover - optional dependency runtime variance
        if prepared_path != artifact_path and prepared_path.exists():
            prepared_path.unlink(missing_ok=True)
        return MediaOcrRunResult(
            status="failed",
            engine="rapidocr_onnx",
            engine_version=None,
            raw_text="",
            preprocessing=preprocessing,
            mean_confidence=None,
            blocks=[],
            caveats=[f"RapidOCR execution failed: {_normalize_text(str(exc)) or 'unknown error'}"],
        )
    finally:
        if prepared_path != artifact_path and prepared_path.exists():
            prepared_path.unlink(missing_ok=True)
    detections = output[0] if isinstance(output, tuple) and output else output
    blocks: list[MediaOcrBlock] = []
    if isinstance(detections, list):
        for index, item in enumerate(detections):
            if not isinstance(item, (list, tuple)) or len(item) < 2:
                continue
            polygon = item[0]
            text = _normalize_text(str(item[1]))
            confidence = _coerce_float(item[2] if len(item) > 2 else None)
            left, top, width, height = _polygon_bounds(polygon)
            if text:
                blocks.append(
                    MediaOcrBlock(
                        block_index=index,
                        text=text,
                        confidence=confidence,
                        left=left,
                        top=top,
                        width=width,
                        height=height,
                    )
                )
    return MediaOcrRunResult(
        status="completed",
        engine="rapidocr_onnx",
        engine_version="rapidocr",
        raw_text=_normalize_text("\n".join(block.text for block in blocks)),
        preprocessing=preprocessing,
        mean_confidence=_mean_confidence(blocks),
        blocks=blocks,
        metadata={"artifactPath": str(artifact_path)},
        caveats=["OCR text is derived from pixels and must remain linked to the original artifact for review."],
    )


def _fixture_ocr_blocks(fixture_text: str | None, fixture_blocks: list[dict[str, Any]]) -> list[MediaOcrBlock]:
    if fixture_blocks:
        blocks: list[MediaOcrBlock] = []
        for index, item in enumerate(fixture_blocks):
            blocks.append(
                MediaOcrBlock(
                    block_index=index,
                    text=_normalize_text(str(item.get("text", ""))),
                    confidence=_coerce_float(item.get("confidence")),
                    left=_coerce_int(item.get("left")),
                    top=_coerce_int(item.get("top")),
                    width=_coerce_int(item.get("width")),
                    height=_coerce_int(item.get("height")),
                )
            )
        return [block for block in blocks if block.text]
    if not fixture_text:
        return []
    return [MediaOcrBlock(block_index=0, text=_normalize_text(fixture_text), confidence=0.99)]


def _parse_tesseract_tsv(raw_tsv: str) -> list[MediaOcrBlock]:
    lines = [line for line in raw_tsv.splitlines() if line.strip()]
    if len(lines) <= 1:
        return []
    header = lines[0].split("\t")
    indices = {name: position for position, name in enumerate(header)}
    line_groups: dict[tuple[str, str, str, str], list[dict[str, str]]] = {}
    for line in lines[1:]:
        parts = line.split("\t")
        if len(parts) != len(header):
            continue
        row = {name: parts[index] for name, index in indices.items()}
        text = _normalize_text(row.get("text", ""))
        if not text:
            continue
        key = (
            row.get("page_num", "0"),
            row.get("block_num", "0"),
            row.get("par_num", "0"),
            row.get("line_num", "0"),
        )
        line_groups.setdefault(key, []).append(row)
    blocks: list[MediaOcrBlock] = []
    for index, (_, rows) in enumerate(sorted(line_groups.items())):
        text = _normalize_text(" ".join(row.get("text", "") for row in rows))
        confidences = [float(row["conf"]) for row in rows if row.get("conf") and row["conf"] not in {"-1", ""}]
        left = min((_coerce_int(row.get("left")) or 0) for row in rows)
        top = min((_coerce_int(row.get("top")) or 0) for row in rows)
        widths = [(_coerce_int(row.get("width")) or 0) for row in rows]
        heights = [(_coerce_int(row.get("height")) or 0) for row in rows]
        blocks.append(
            MediaOcrBlock(
                block_index=index,
                text=text,
                confidence=round(sum(confidences) / len(confidences), 4) if confidences else None,
                left=left,
                top=top,
                width=max(widths) if widths else None,
                height=max(heights) if heights else None,
            )
        )
    return blocks


def _mean_confidence(blocks: list[MediaOcrBlock]) -> float | None:
    confidences = [block.confidence for block in blocks if block.confidence is not None]
    if not confidences:
        return None
    return round(sum(confidences) / len(confidences), 4)


def _fixture_interpretation(
    fixture_result: dict[str, Any],
    *,
    observed_latitude: float | None,
    observed_longitude: float | None,
) -> MediaInterpretationResult:
    return MediaInterpretationResult(
        status="completed",
        adapter="fixture",
        model_name=str(fixture_result.get("modelName") or "fixture-vision"),
        scene_labels=[str(item) for item in fixture_result.get("sceneLabels", []) if str(item).strip()],
        scene_summary=_normalize_optional(fixture_result.get("sceneSummary")),
        uncertainty_ceiling=_coerce_float(fixture_result.get("uncertaintyCeiling")) or 0.4,
        place_hypothesis=_normalize_optional(fixture_result.get("placeHypothesis")),
        place_confidence=_coerce_float(fixture_result.get("placeConfidence")),
        place_basis=_normalize_optional(fixture_result.get("placeBasis")) or "fixture_input",
        time_of_day_guess=_normalize_optional(fixture_result.get("timeOfDayGuess")),
        time_of_day_confidence=_coerce_float(fixture_result.get("timeOfDayConfidence")),
        time_of_day_basis=_normalize_optional(fixture_result.get("timeOfDayBasis")) or "fixture_input",
        season_guess=_normalize_optional(fixture_result.get("seasonGuess")),
        season_confidence=_coerce_float(fixture_result.get("seasonConfidence")),
        season_basis=_normalize_optional(fixture_result.get("seasonBasis")) or "fixture_input",
        geolocation_hypothesis=_normalize_optional(fixture_result.get("geolocationHypothesis")),
        geolocation_confidence=_coerce_float(fixture_result.get("geolocationConfidence")),
        geolocation_basis=_normalize_optional(fixture_result.get("geolocationBasis")) or "fixture_input",
        observed_latitude=observed_latitude,
        observed_longitude=observed_longitude,
        reasoning_lines=[str(item) for item in fixture_result.get("reasoningLines", []) if str(item).strip()],
        metadata={"fixture": True},
        caveats=[
            "Fixture scene interpretation is deterministic test input and not a live model judgment.",
            "No people recognition or identity analysis is performed in this workflow.",
        ],
    )


def _try_ollama_interpretation(
    settings: Settings,
    *,
    artifact_path: str | None,
    artifact_metadata: dict[str, Any],
    ocr_text: str | None,
    captions: list[str],
    model: str | None,
) -> MediaInterpretationResult | None:
    if artifact_path is None:
        return None
    resolved_model = (model or settings.source_discovery_media_ollama_model or "").strip()
    if not settings.source_discovery_media_ollama_enabled or not resolved_model:
        return None
    base_url = (settings.ollama_base_url or "").strip()
    if not re.match(r"^https?://(?:127\.0\.0\.1|localhost|\[::1\])(?::\d+)?/?$", base_url):
        return None
    try:
        encoded = base64.b64encode(Path(artifact_path).read_bytes()).decode("utf-8")
    except OSError:
        return None
    prompt = _build_ollama_prompt(artifact_metadata=artifact_metadata, ocr_text=ocr_text, captions=captions)
    request_body = json.dumps(
        {
            "model": resolved_model,
            "format": "json",
            "stream": False,
            "images": [encoded],
            "prompt": prompt,
        }
    ).encode("utf-8")
    request = Request(
        base_url.rstrip("/") + "/api/generate",
        method="POST",
        headers={"Content-Type": "application/json"},
        data=request_body,
    )
    try:
        with urlopen(request, timeout=min(45, settings.wave_llm_http_timeout_seconds)) as response:
            raw = response.read(settings.wave_llm_max_output_chars + 4096).decode("utf-8", errors="replace")
    except Exception:
        return None
    try:
        payload = json.loads(raw)
        response_text = str(payload.get("response") or "").strip()
        parsed = json.loads(response_text)
    except (json.JSONDecodeError, TypeError, ValueError):
        return None
    return MediaInterpretationResult(
        status="completed",
        adapter="ollama",
        model_name=resolved_model,
        scene_labels=[str(item) for item in parsed.get("scene_labels", []) if str(item).strip()],
        scene_summary=_normalize_optional(parsed.get("scene_summary")),
        uncertainty_ceiling=_coerce_float(parsed.get("uncertainty_ceiling")) or 0.45,
        place_hypothesis=_normalize_optional(parsed.get("place_hypothesis")),
        place_confidence=_coerce_float(parsed.get("place_confidence")),
        place_basis=_normalize_optional(parsed.get("place_basis")),
        time_of_day_guess=_normalize_optional(parsed.get("time_of_day_guess")),
        time_of_day_confidence=_coerce_float(parsed.get("time_of_day_confidence")),
        time_of_day_basis=_normalize_optional(parsed.get("time_of_day_basis")),
        season_guess=_normalize_optional(parsed.get("season_guess")),
        season_confidence=_coerce_float(parsed.get("season_confidence")),
        season_basis=_normalize_optional(parsed.get("season_basis")),
        geolocation_hypothesis=_normalize_optional(parsed.get("geolocation_hypothesis")),
        geolocation_confidence=_coerce_float(parsed.get("geolocation_confidence")),
        geolocation_basis=_normalize_optional(parsed.get("geolocation_basis")),
        observed_latitude=_coerce_float(parsed.get("observed_latitude")),
        observed_longitude=_coerce_float(parsed.get("observed_longitude")),
        reasoning_lines=[str(item) for item in parsed.get("reasoning_lines", []) if str(item).strip()],
        metadata={"provider": "ollama", "model": resolved_model},
        caveats=[
            "Ollama interpretation is a local model aid and remains review-only.",
            "No people recognition or identity analysis is allowed in this workflow.",
        ],
    )


def _try_openai_compat_local_interpretation(
    settings: Settings,
    *,
    artifact_path: str | None,
    artifact_metadata: dict[str, Any],
    ocr_text: str | None,
    captions: list[str],
    model: str | None,
) -> MediaInterpretationResult | None:
    if artifact_path is None:
        return None
    if not settings.source_discovery_media_openai_compat_enabled:
        return None
    resolved_model = (model or settings.source_discovery_media_openai_compat_model or "").strip()
    if not resolved_model:
        return None
    base_url = (settings.source_discovery_media_openai_compat_base_url or "").strip()
    if not re.match(r"^https?://(?:127\.0\.0\.1|localhost|\[::1\])(?::\d+)?(?:/.*)?$", base_url):
        return None
    try:
        encoded = base64.b64encode(Path(artifact_path).read_bytes()).decode("utf-8")
    except OSError:
        return None
    request_body = json.dumps(
        {
            "model": resolved_model,
            "response_format": {"type": "json_object"},
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": _build_ollama_prompt(artifact_metadata=artifact_metadata, ocr_text=ocr_text, captions=captions)},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{encoded}"}},
                    ],
                }
            ],
        }
    ).encode("utf-8")
    request = Request(
        base_url.rstrip("/") + "/chat/completions",
        method="POST",
        headers={"Content-Type": "application/json"},
        data=request_body,
    )
    try:
        with urlopen(request, timeout=min(45, settings.wave_llm_http_timeout_seconds)) as response:
            raw = response.read(settings.wave_llm_max_output_chars + 4096).decode("utf-8", errors="replace")
    except Exception:
        return None
    try:
        payload = json.loads(raw)
        choices = payload.get("choices") if isinstance(payload, dict) else None
        if not isinstance(choices, list) or not choices:
            return None
        message = choices[0].get("message", {})
        content = message.get("content")
        if isinstance(content, list):
            text_parts = [str(item.get("text", "")) for item in content if isinstance(item, dict)]
            response_text = _normalize_text(" ".join(text_parts))
        else:
            response_text = _normalize_text(str(content or ""))
        parsed = json.loads(response_text)
    except (json.JSONDecodeError, TypeError, ValueError, AttributeError):
        return None
    return MediaInterpretationResult(
        status="completed",
        adapter="openai_compat_local",
        model_name=resolved_model,
        scene_labels=[str(item) for item in parsed.get("scene_labels", []) if str(item).strip()],
        scene_summary=_normalize_optional(parsed.get("scene_summary")),
        uncertainty_ceiling=_coerce_float(parsed.get("uncertainty_ceiling")) or 0.45,
        place_hypothesis=_normalize_optional(parsed.get("place_hypothesis")),
        place_confidence=_coerce_float(parsed.get("place_confidence")),
        place_basis=_normalize_optional(parsed.get("place_basis")),
        time_of_day_guess=_normalize_optional(parsed.get("time_of_day_guess")),
        time_of_day_confidence=_coerce_float(parsed.get("time_of_day_confidence")),
        time_of_day_basis=_normalize_optional(parsed.get("time_of_day_basis")),
        season_guess=_normalize_optional(parsed.get("season_guess")),
        season_confidence=_coerce_float(parsed.get("season_confidence")),
        season_basis=_normalize_optional(parsed.get("season_basis")),
        geolocation_hypothesis=_normalize_optional(parsed.get("geolocation_hypothesis")),
        geolocation_confidence=_coerce_float(parsed.get("geolocation_confidence")),
        geolocation_basis=_normalize_optional(parsed.get("geolocation_basis")),
        observed_latitude=_coerce_float(parsed.get("observed_latitude")),
        observed_longitude=_coerce_float(parsed.get("observed_longitude")),
        reasoning_lines=[str(item) for item in parsed.get("reasoning_lines", []) if str(item).strip()],
        metadata={"provider": "openai_compat_local", "model": resolved_model},
        caveats=[
            "OpenAI-compatible local interpretation is a localhost model aid and remains review-only.",
            "No people recognition or identity analysis is allowed in this workflow.",
        ],
    )


def _build_ollama_prompt(
    *,
    artifact_metadata: dict[str, Any],
    ocr_text: str | None,
    captions: list[str],
) -> str:
    metadata_text = json.dumps(artifact_metadata, ensure_ascii=True)
    return (
        "You are a local-only media evidence assistant for 11Writer.\n"
        "Analyze places and scenes only. Do not identify people. Do not guess identities, guilt, or intent.\n"
        "Return strict JSON with keys: "
        "scene_labels, scene_summary, uncertainty_ceiling, place_hypothesis, place_confidence, place_basis, "
        "time_of_day_guess, time_of_day_confidence, time_of_day_basis, season_guess, season_confidence, "
        "season_basis, geolocation_hypothesis, geolocation_confidence, geolocation_basis, observed_latitude, "
        "observed_longitude, reasoning_lines.\n"
        "Keep claims narrow and uncertainty explicit.\n"
        f"Artifact metadata: {metadata_text}\n"
        f"OCR text: {_normalize_text(ocr_text or '')}\n"
        f"Captions: {_normalize_text(' '.join(captions))}"
    )


def _fixture_geolocation_result(fixture_result: dict[str, Any]) -> MediaGeolocationResult:
    candidates = [
        _coerce_geolocation_candidate(item, default_engine="fixture", rank=index + 1)
        for index, item in enumerate(fixture_result.get("candidates", []))
        if isinstance(item, dict)
    ]
    top_candidate = candidates[0] if candidates else None
    return MediaGeolocationResult(
        status=_normalize_optional(fixture_result.get("status")) or "completed",
        engine="fixture",
        model_name=_normalize_optional(fixture_result.get("modelName")),
        analyst_adapter=_normalize_optional(fixture_result.get("analystAdapter")),
        analyst_model_name=_normalize_optional(fixture_result.get("analystModelName")),
        candidate_count=len(candidates),
        top_label=top_candidate.label if top_candidate is not None else _normalize_optional(fixture_result.get("topLabel")),
        top_latitude=top_candidate.latitude if top_candidate is not None else _coerce_float(fixture_result.get("topLatitude")),
        top_longitude=top_candidate.longitude if top_candidate is not None else _coerce_float(fixture_result.get("topLongitude")),
        top_confidence=top_candidate.confidence if top_candidate is not None else _coerce_float(fixture_result.get("topConfidence")),
        top_confidence_ceiling=top_candidate.confidence_ceiling if top_candidate is not None else _coerce_float(fixture_result.get("topConfidenceCeiling")),
        top_basis="; ".join(top_candidate.basis[:3]) if top_candidate is not None and top_candidate.basis else _normalize_optional(fixture_result.get("topBasis")),
        summary=_normalize_optional(fixture_result.get("summary")),
        confidence_ceiling=top_candidate.confidence_ceiling if top_candidate is not None else _coerce_float(fixture_result.get("confidenceCeiling")),
        supporting_evidence=list(top_candidate.supporting_evidence) if top_candidate is not None else [],
        contradicting_evidence=list(top_candidate.contradicting_evidence) if top_candidate is not None else [],
        engine_agreement=top_candidate.engine_agreement if top_candidate is not None else {},
        provenance_chain=list(top_candidate.provenance_chain) if top_candidate is not None else [],
        inherited_from_artifact_ids=list(top_candidate.inherited_from_artifact_ids) if top_candidate is not None else [],
        clue_packet=MediaGeolocationCluePacket(),
        engine_attempts=[],
        reasoning_lines=[str(item) for item in fixture_result.get("reasoningLines", []) if str(item).strip()],
        candidates=candidates,
        metadata={"fixture": True},
        caveats=[
            "Fixture media geolocation is deterministic test input and not a live model judgment.",
            "No people recognition or identity analysis is performed in this workflow.",
        ],
    )


def _text_for_geolocation_clues(ocr_text: str | None, captions: list[str]) -> str:
    return _normalize_geolocation_text("\n".join([ocr_text or "", *captions]))


def _extract_geolocation_clue_packet(
    *,
    settings: Settings,
    observed_latitude: float | None,
    observed_longitude: float | None,
    exif_timestamp: str | None,
    ocr_text: str | None,
    captions: list[str],
    artifact_metadata: dict[str, Any],
    prior_place_hypothesis: str | None,
    prior_place_confidence: float | None,
    prior_place_basis: str | None,
    prior_geolocation_hypothesis: str | None,
    prior_geolocation_confidence: float | None,
    prior_geolocation_basis: str | None,
    inherited_context: dict[str, Any] | None,
) -> tuple[MediaGeolocationCluePacket, list[str], list[str]]:
    packet = MediaGeolocationCluePacket()
    reasoning = [
        "Deterministic geolocation builds structured clues from observed metadata, OCR text, captions, bounded visual heuristics, and lineage-aware inherited evidence.",
    ]
    caveats = [
        "Deterministic geolocation uses bounded metadata and clue extraction, not unrestricted world knowledge.",
    ]
    combined_text = _text_for_geolocation_clues(ocr_text, captions)

    if observed_latitude is not None and observed_longitude is not None:
        packet.coordinate_clues.append(
            MediaGeolocationClue(
                clue_type="observed_coordinates",
                text=f"{round(observed_latitude, 6)}, {round(observed_longitude, 6)}",
                confidence=0.99,
                normalized_value=f"{round(observed_latitude, 6)},{round(observed_longitude, 6)}",
                latitude=round(observed_latitude, 6),
                longitude=round(observed_longitude, 6),
                reason="Observed coordinates were embedded in media metadata or captured directly from the artifact.",
            )
        )
        reasoning.append("Observed artifact coordinates were preserved as the strongest direct location clue.")

    coordinate_clues, rejected_coordinate_clues = _extract_coordinate_clues(combined_text)
    packet.coordinate_clues.extend(coordinate_clues)
    packet.rejected_clues.extend(rejected_coordinate_clues)
    if coordinate_clues:
        reasoning.append("OCR or caption text exposed coordinate-like clues that can seed precise location hypotheses.")

    place_clues = _extract_place_text_clues(combined_text, settings=settings)
    packet.place_text_clues.extend(place_clues)
    if place_clues:
        reasoning.append("Place-text extraction found bounded location phrases, operators, or regional labels.")

    script_clues = _extract_script_language_clues(combined_text)
    packet.script_language_clues.extend(script_clues)
    if script_clues:
        reasoning.append("Visible text yielded script or language-family hints that can help regional ranking.")

    environment_clues = _extract_environment_clues(artifact_metadata)
    environment_clues.extend(_extract_text_environment_clues(combined_text))
    packet.environment_clues.extend(environment_clues)
    if environment_clues:
        reasoning.append("Bounded visual statistics contributed environment clues such as vegetation, snow, water, or urban density.")

    time_clues = _extract_time_clues(
        observed_latitude=observed_latitude,
        exif_timestamp=exif_timestamp,
        artifact_metadata=artifact_metadata,
    )
    packet.time_clues.extend(time_clues)
    if time_clues:
        reasoning.append("Timestamp and bounded brightness heuristics contributed time-of-day or season clues.")

    if prior_geolocation_hypothesis:
        packet.place_text_clues.append(
            MediaGeolocationClue(
                clue_type="prior_geolocation_hypothesis",
                text=prior_geolocation_hypothesis,
                confidence=prior_geolocation_confidence or 0.58,
                normalized_value=_normalize_text(prior_geolocation_hypothesis).casefold(),
                reason=prior_geolocation_basis or "A prior interpretation suggested a review-only geolocation hypothesis.",
            )
        )
    elif prior_place_hypothesis:
        packet.place_text_clues.append(
            MediaGeolocationClue(
                clue_type="prior_place_hypothesis",
                text=prior_place_hypothesis,
                confidence=prior_place_confidence or 0.52,
                normalized_value=_normalize_text(prior_place_hypothesis).casefold(),
                reason=prior_place_basis or "A prior interpretation suggested a review-only place hypothesis.",
            )
        )

    if inherited_context:
        inherited_packet = inherited_context.get("cluePacket") if isinstance(inherited_context.get("cluePacket"), dict) else {}
        packet.coordinate_clues.extend(_coerce_inherited_clues(inherited_packet.get("coordinateClues"), clue_type_fallback="inherited_coordinate"))
        packet.place_text_clues.extend(_coerce_inherited_clues(inherited_packet.get("placeTextClues"), clue_type_fallback="inherited_place_text"))
        packet.script_language_clues.extend(_coerce_inherited_clues(inherited_packet.get("scriptLanguageClues"), clue_type_fallback="inherited_script"))
        packet.environment_clues.extend(_coerce_inherited_clues(inherited_packet.get("environmentClues"), clue_type_fallback="inherited_environment"))
        packet.time_clues.extend(_coerce_inherited_clues(inherited_packet.get("timeClues"), clue_type_fallback="inherited_time"))
        packet.rejected_clues.extend(_coerce_inherited_clues(inherited_packet.get("rejectedClues"), clue_type_fallback="inherited_rejected"))
        if any(
            [
                inherited_packet.get("coordinateClues"),
                inherited_packet.get("placeTextClues"),
                inherited_packet.get("scriptLanguageClues"),
                inherited_packet.get("environmentClues"),
                inherited_packet.get("timeClues"),
            ]
        ):
            reasoning.append("Duplicate-cluster or sequence lineage contributed inherited clues that stay down-weighted relative to direct observations.")

    if not packet.coordinate_clues and not packet.place_text_clues and not packet.script_language_clues:
        caveats.append("No strong coordinate, place-text, or script clues were extracted from the current artifact inputs.")
    return packet, reasoning, caveats


def _build_deterministic_geolocation_candidates(
    *,
    clue_packet: MediaGeolocationCluePacket,
    observed_latitude: float | None,
    observed_longitude: float | None,
    prior_place_hypothesis: str | None,
    prior_place_confidence: float | None,
    prior_place_basis: str | None,
    prior_geolocation_hypothesis: str | None,
    prior_geolocation_confidence: float | None,
    prior_geolocation_basis: str | None,
) -> list[MediaGeolocationCandidate]:
    del prior_place_hypothesis, prior_place_confidence, prior_place_basis, prior_geolocation_hypothesis, prior_geolocation_confidence, prior_geolocation_basis
    candidates: list[MediaGeolocationCandidate] = []
    for clue in clue_packet.coordinate_clues:
        if clue.latitude is None or clue.longitude is None:
            continue
        confidence = clue.confidence or 0.82
        if clue.clue_type == "observed_coordinates":
            confidence = 0.99
        elif clue.inherited:
            confidence = max(0.35, min(confidence, 0.66))
        candidate = MediaGeolocationCandidate(
            rank=len(candidates) + 1,
            candidate_kind="gps_point",
            label=clue.normalized_value or clue.text,
            latitude=clue.latitude,
            longitude=clue.longitude,
            confidence=confidence,
            engine="deterministic",
            basis=[item for item in [clue.reason, f"Coordinate clue: {clue.text}"] if item],
            provenance_chain=["observed_metadata" if clue.clue_type == "observed_coordinates" else "ocr_or_caption_coordinate_clue"],
            inherited=clue.inherited,
            inherited_from_artifact_ids=[clue.inherited_from_artifact_id] if clue.inherited_from_artifact_id else [],
            metadata={"clueType": clue.clue_type},
        )
        candidates.append(candidate)
    for clue in clue_packet.place_text_clues[:10]:
        if not clue.text.strip():
            continue
        if clue.latitude is not None and clue.longitude is not None:
            kind = "gps_point"
        else:
            kind = "country_region" if clue.clue_type in {"country_token", "state_token", "transit_operator"} else "place_label"
        confidence = clue.confidence or 0.45
        if clue.inherited:
            confidence = max(0.25, min(confidence, 0.5))
        candidates.append(
            MediaGeolocationCandidate(
                rank=len(candidates) + 1,
                candidate_kind=kind,
                label=clue.text,
                latitude=clue.latitude,
                longitude=clue.longitude,
                confidence=confidence,
                engine="deterministic",
                basis=[item for item in [clue.reason, f"Place-text clue: {clue.text}"] if item],
                provenance_chain=["textual_place_clue"],
                inherited=clue.inherited,
                inherited_from_artifact_ids=[clue.inherited_from_artifact_id] if clue.inherited_from_artifact_id else [],
                metadata={"clueType": clue.clue_type, **clue.metadata},
            )
        )
    if observed_latitude is not None and observed_longitude is not None and not candidates:
        candidates.append(
            MediaGeolocationCandidate(
                rank=1,
                candidate_kind="gps_point",
                label="embedded_coordinates",
                latitude=round(observed_latitude, 6),
                longitude=round(observed_longitude, 6),
                confidence=0.99,
                engine="deterministic",
                basis=["Observed artifact coordinates were carried directly into geolocation fusion."],
                provenance_chain=["observed_metadata"],
            )
        )
    return candidates


def _coerce_inherited_clues(raw_items: Any, *, clue_type_fallback: str) -> list[MediaGeolocationClue]:
    clues: list[MediaGeolocationClue] = []
    if not isinstance(raw_items, list):
        return clues
    for item in raw_items:
        if not isinstance(item, dict):
            continue
        clues.append(
            MediaGeolocationClue(
                clue_type=_normalize_optional(item.get("clueType")) or clue_type_fallback,
                text=_normalize_optional(item.get("text")) or "",
                confidence=_coerce_float(item.get("confidence")),
                normalized_value=_normalize_optional(item.get("normalizedValue")),
                latitude=_coerce_float(item.get("latitude")),
                longitude=_coerce_float(item.get("longitude")),
                reason=_normalize_optional(item.get("reason")),
                inherited=True,
                inherited_from_artifact_id=_normalize_optional(item.get("inheritedFromArtifactId"))
                or _normalize_optional(item.get("artifactId")),
                inherited_from_geolocation_run_id=_normalize_optional(item.get("inheritedFromGeolocationRunId"))
                or _normalize_optional(item.get("geolocationRunId")),
                inherited_from_comparison_id=_normalize_optional(item.get("inheritedFromComparisonId"))
                or _normalize_optional(item.get("comparisonId")),
                metadata=item.get("metadata", {}) if isinstance(item.get("metadata"), dict) else {},
            )
        )
    return clues


def _extract_coordinate_clues(text: str) -> tuple[list[MediaGeolocationClue], list[MediaGeolocationClue]]:
    accepted: list[MediaGeolocationClue] = []
    rejected: list[MediaGeolocationClue] = []
    if not text:
        return accepted, rejected
    seen_values: set[str] = set()
    for match in re.finditer(r"(?P<lat>[-+]?\d{1,3}(?:\.\d+)?)[\s,;/]+(?P<lon>[-+]?\d{1,3}(?:\.\d+)?)(?!\d)", text):
        raw = f"{match.group('lat')}, {match.group('lon')}"
        latitude = _coerce_float(match.group("lat"))
        longitude = _coerce_float(match.group("lon"))
        if latitude is None or longitude is None:
            continue
        if -90.0 <= latitude <= 90.0 and -180.0 <= longitude <= 180.0:
            normalized = f"{round(latitude, 6)},{round(longitude, 6)}"
            if normalized in seen_values:
                continue
            seen_values.add(normalized)
            accepted.append(
                MediaGeolocationClue(
                    clue_type="decimal_coordinates",
                    text=raw,
                    confidence=0.89,
                    normalized_value=normalized,
                    latitude=round(latitude, 6),
                    longitude=round(longitude, 6),
                    reason="OCR or caption text contained decimal coordinates consistent with latitude and longitude bounds.",
                )
            )
        else:
            rejected.append(
                MediaGeolocationClue(
                    clue_type="rejected_decimal_coordinates",
                    text=raw,
                    confidence=0.1,
                    normalized_value=raw,
                    reason="The numeric pair resembled coordinates but fell outside valid latitude/longitude bounds.",
                )
            )
    for latitude, longitude, raw in _extract_cardinal_coordinate_pairs(text):
        normalized = f"{latitude},{longitude}"
        if normalized in seen_values:
            continue
        seen_values.add(normalized)
        accepted.append(
            MediaGeolocationClue(
                clue_type="cardinal_coordinates",
                text=raw,
                confidence=0.91,
                normalized_value=normalized,
                latitude=latitude,
                longitude=longitude,
                reason="Text contained directional latitude/longitude notation using N/S/E/W markers.",
            )
        )
    for latitude, longitude, raw in _extract_dms_coordinate_pairs(text):
        normalized = f"{latitude},{longitude}"
        if normalized in seen_values:
            continue
        seen_values.add(normalized)
        accepted.append(
            MediaGeolocationClue(
                clue_type="dms_coordinates",
                text=raw,
                confidence=0.9,
                normalized_value=normalized,
                latitude=latitude,
                longitude=longitude,
                reason="Text contained degree-minute-second coordinate notation.",
            )
        )
    for raw in _extract_utm_mgrs_like_tokens(text):
        accepted.append(
            MediaGeolocationClue(
                clue_type="utm_mgrs_like_reference",
                text=raw,
                confidence=0.54,
                normalized_value=_normalize_text(raw),
                reason="Text contained a UTM/MGRS-like reference that may help operator review even though local conversion was not attempted here.",
            )
        )
    return accepted, rejected


def _extract_place_text_clues(text: str, *, settings: Settings) -> list[MediaGeolocationClue]:
    clues: list[MediaGeolocationClue] = []
    if not text:
        return clues
    keyword_patterns = {
        "station_phrase": r"\b([A-Z][\w'&.-]+(?:\s+[A-Z][\w'&.-]+){0,4}\s+(?:Station|Terminal))\b",
        "airport_phrase": r"\b([A-Z][\w'&.-]+(?:\s+[A-Z][\w'&.-]+){0,4}\s+Airport)\b",
        "port_phrase": r"\b([A-Z][\w'&.-]+(?:\s+[A-Z][\w'&.-]+){0,4}\s+(?:Port|Harbor|Harbour))\b",
        "road_phrase": r"\b((?:Route|Road|Highway|Hwy|Interstate|I-|US-)\s*[\w-]+)\b",
        "district_phrase": r"\b([A-Z][\w'&.-]+(?:\s+[A-Z][\w'&.-]+){0,4}\s+District)\b",
        "park_phrase": r"\b([A-Z][\w'&.-]+(?:\s+[A-Z][\w'&.-]+){0,4}\s+(?:Park|Trail|Campus|Bridge|Mountain|Mount|Dam|Canyon|Crossing|Bay|Coast|Cliffs?))\b",
    }
    for clue_type, pattern in keyword_patterns.items():
        for match in re.finditer(pattern, text):
            phrase = _normalize_text(match.group(1))
            if not phrase:
                continue
            clues.append(
                MediaGeolocationClue(
                    clue_type=clue_type,
                    text=phrase,
                    confidence=0.48 if "road" in clue_type else 0.56,
                    normalized_value=phrase.casefold(),
                    reason="A place-like phrase was extracted directly from OCR or caption text.",
                )
            )
    clues.extend(_extract_route_reference_clues(text))
    clues.extend(_extract_driving_side_clues(text))
    clues.extend(_extract_gazetteer_place_text_clues(text, settings=settings))
    country_state_tokens = [
        "India",
        "Japan",
        "Norway",
        "Finland",
        "Sweden",
        "Germany",
        "France",
        "Canada",
        "United States",
        "California",
        "Texas",
        "Florida",
        "Queensland",
        "Scotland",
    ]
    for token in country_state_tokens:
        if re.search(rf"\b{re.escape(token)}\b", text, flags=re.IGNORECASE):
            clue_type = "country_token" if " " in token or token in {"India", "Japan", "Norway", "Finland", "Sweden", "Germany", "France", "Canada"} else "state_token"
            clues.append(
                MediaGeolocationClue(
                    clue_type=clue_type,
                    text=token,
                    confidence=0.42,
                    normalized_value=token.casefold(),
                    reason="OCR or caption text included a country or state token that can help regional ranking.",
                )
            )
    for operator in [
        "Amtrak",
        "BART",
        "Caltrain",
        "CTA",
        "DB",
        "JR",
        "JR East",
        "MARTA",
        "MBTA",
        "Metra",
        "Metro",
        "MTA",
        "Muni",
        "NJ Transit",
        "Renfe",
        "RER",
        "SEPTA",
        "SFMTA",
        "SNCF",
        "TfL",
        "VTA",
    ]:
        if re.search(rf"\b{re.escape(operator)}\b", text, flags=re.IGNORECASE):
            clues.append(
                MediaGeolocationClue(
                    clue_type="transit_operator",
                    text=operator,
                    confidence=0.38,
                    normalized_value=operator.casefold(),
                    reason="Text included a transit or operator token that may help later regional ranking.",
                )
            )
    return clues[:24]


def _extract_route_reference_clues(text: str) -> list[MediaGeolocationClue]:
    clues: list[MediaGeolocationClue] = []
    seen_tokens: set[str] = set()
    route_patterns = [
        ("interstate_route", re.compile(r"\b(?:Interstate|I)[-\s]?(\d{1,3}[A-Z]?)\b", re.IGNORECASE), lambda value: f"I-{value.upper()}"),
        ("us_route", re.compile(r"\bUS[-\s]?(\d{1,3}[A-Z]?)\b", re.IGNORECASE), lambda value: f"US {value.upper()}"),
        ("state_route", re.compile(r"\b(?:State Route|SR|Route|Highway|Hwy)[-\s]+(\d{1,4}[A-Z]?)\b", re.IGNORECASE), lambda value: f"Route {value.upper()}"),
    ]
    for clue_type, pattern, formatter in route_patterns:
        for match in pattern.finditer(text):
            normalized_route = formatter(match.group(1))
            route_key = f"{clue_type}:{normalized_route.casefold()}"
            if route_key in seen_tokens:
                continue
            seen_tokens.add(route_key)
            clues.append(
                MediaGeolocationClue(
                    clue_type=clue_type,
                    text=normalized_route,
                    confidence=0.44 if clue_type == "state_route" else 0.5,
                    normalized_value=normalized_route.casefold(),
                    reason="OCR or caption text exposed a route-style road reference that can assist later regional ranking.",
                )
            )
    return clues


def _extract_driving_side_clues(text: str) -> list[MediaGeolocationClue]:
    clues: list[MediaGeolocationClue] = []
    phrase_map = {
        "left_driving": [
            r"\bkeep left\b",
            r"\bleft-hand traffic\b",
            r"\bdrive on the left\b",
        ],
        "right_driving": [
            r"\bkeep right\b",
            r"\bright-hand traffic\b",
            r"\bdrive on the right\b",
        ],
    }
    for normalized_value, patterns in phrase_map.items():
        for pattern in patterns:
            if re.search(pattern, text, flags=re.IGNORECASE):
                clues.append(
                    MediaGeolocationClue(
                        clue_type="driving_side_text",
                        text=normalized_value,
                        confidence=0.53,
                        normalized_value=normalized_value,
                        reason="Visible text explicitly referenced road-side driving direction.",
                    )
                )
                break
    return clues


def _extract_gazetteer_place_text_clues(text: str, *, settings: Settings) -> list[MediaGeolocationClue]:
    clues: list[MediaGeolocationClue] = []
    seen_entries: set[str] = set()
    normalized_text = _normalize_text(text)
    if not normalized_text:
        return clues
    entries = sorted(
        _load_media_geolocation_place_gazetteer(settings),
        key=lambda item: len(str(item.get("name") or "")),
        reverse=True,
    )
    for entry in entries:
        phrases = [entry.get("name"), *(entry.get("aliases", []) if isinstance(entry.get("aliases"), list) else [])]
        for phrase in phrases:
            candidate_phrase = _normalize_text(str(phrase or ""))
            if len(candidate_phrase) < 4:
                continue
            if not re.search(rf"\b{re.escape(candidate_phrase)}\b", normalized_text, flags=re.IGNORECASE):
                continue
            entry_key = f"{entry.get('kind')}:{str(entry.get('name') or '').casefold()}"
            if entry_key in seen_entries:
                break
            seen_entries.add(entry_key)
            kind = str(entry.get("kind") or "unknown")
            confidence = 0.72 if kind == "landmark" else (0.6 if kind in {"city", "locality", "district"} else 0.52)
            clues.append(
                MediaGeolocationClue(
                    clue_type="gazetteer_landmark" if kind == "landmark" else "gazetteer_place",
                    text=str(entry.get("name") or candidate_phrase),
                    confidence=confidence,
                    normalized_value=str(entry.get("name") or candidate_phrase).casefold(),
                    latitude=_coerce_float(entry.get("latitude")),
                    longitude=_coerce_float(entry.get("longitude")),
                    reason="OCR or caption text matched a bounded offline gazetteer entry, which can seed a reviewable place hypothesis.",
                    metadata={
                        "gazetteerKind": kind,
                        "locality": entry.get("locality"),
                        "admin1": entry.get("admin1"),
                        "country": entry.get("country"),
                        "countryCode": entry.get("countryCode"),
                        "matchedPhrase": candidate_phrase,
                    },
                )
            )
            break
    return clues[:12]


def _extract_script_language_clues(text: str) -> list[MediaGeolocationClue]:
    if not text:
        return []
    script_ranges = {
        "latin": [(0x0041, 0x024F)],
        "cyrillic": [(0x0400, 0x052F)],
        "arabic": [(0x0600, 0x06FF)],
        "devanagari": [(0x0900, 0x097F)],
        "hangul": [(0xAC00, 0xD7AF)],
        "kana_han": [(0x3040, 0x30FF), (0x4E00, 0x9FFF)],
        "thai": [(0x0E00, 0x0E7F)],
    }
    counts: dict[str, int] = {}
    for char in text:
        codepoint = ord(char)
        for script, ranges in script_ranges.items():
            if any(start <= codepoint <= end for start, end in ranges):
                counts[script] = counts.get(script, 0) + 1
                break
    total = sum(counts.values())
    clues: list[MediaGeolocationClue] = []
    for script, count in sorted(counts.items(), key=lambda item: item[1], reverse=True):
        if count <= 0 or total <= 0:
            continue
        clues.append(
            MediaGeolocationClue(
                clue_type="script_family",
                text=script.replace("_", "/"),
                confidence=round(min(0.9, count / total), 4),
                normalized_value=script,
                reason="Unicode character ranges in OCR or captions suggest this script family.",
                metadata={"characterCount": count, "totalScriptCharacters": total},
            )
        )
    return clues[:4]


def _extract_environment_clues(artifact_metadata: dict[str, Any]) -> list[MediaGeolocationClue]:
    clues: list[MediaGeolocationClue] = []
    seasonal = artifact_metadata.get("seasonalSignals") if isinstance(artifact_metadata.get("seasonalSignals"), dict) else {}
    daylight = artifact_metadata.get("daylightSignals") if isinstance(artifact_metadata.get("daylightSignals"), dict) else {}
    channel_means = artifact_metadata.get("channelMeans") if isinstance(artifact_metadata.get("channelMeans"), dict) else {}
    snow_ratio = _coerce_float(seasonal.get("snowRatio")) or 0.0
    green_ratio = _coerce_float(seasonal.get("greenRatio")) or 0.0
    warm_ratio = _coerce_float(seasonal.get("warmRatio")) or 0.0
    blue_ratio = _coerce_float(seasonal.get("blueRatio")) or 0.0
    brightness = _coerce_float(daylight.get("brightness"))
    dominant_bright_side = _normalize_optional(daylight.get("dominantBrightSide"))
    if snow_ratio >= 0.14:
        clues.append(MediaGeolocationClue(clue_type="snow_or_ice", text="snow_or_ice", confidence=min(0.8, 0.45 + snow_ratio), reason="Large bright low-saturation regions suggest snow, ice, or pale terrain."))
    if green_ratio >= 0.2:
        clues.append(MediaGeolocationClue(clue_type="vegetation", text="vegetation", confidence=min(0.8, 0.35 + green_ratio), reason="Green-dominant pixels suggest vegetation or a growing-season scene."))
    if warm_ratio >= 0.24:
        clues.append(MediaGeolocationClue(clue_type="dry_or_autumn", text="dry_or_autumn", confidence=min(0.72, 0.28 + warm_ratio), reason="Warm surface colors suggest dry-season, autumn, or masonry-heavy terrain."))
    if blue_ratio >= 0.26:
        clues.append(MediaGeolocationClue(clue_type="water_or_sky", text="water_or_sky", confidence=min(0.7, 0.24 + blue_ratio), reason="Blue-dominant regions suggest sky, water, or both."))
    if brightness is not None:
        bucket = "daylight" if brightness >= 0.38 else ("twilight_or_overcast" if brightness >= 0.18 else "night")
        clues.append(MediaGeolocationClue(clue_type="brightness_bucket", text=bucket, confidence=0.5 if bucket != "daylight" else 0.62, reason="Bounded brightness statistics suggest a coarse lighting regime."))
    if dominant_bright_side:
        clues.append(
            MediaGeolocationClue(
                clue_type="light_direction_hint",
                text=dominant_bright_side,
                confidence=0.32,
                reason="Brightness imbalance across the frame suggests a bounded light-direction hint only.",
                metadata={
                    "leftBrightness": _coerce_float(daylight.get("leftBrightness")),
                    "rightBrightness": _coerce_float(daylight.get("rightBrightness")),
                },
            )
        )
    if channel_means and max((_coerce_float(channel_means.get("red")) or 0.0), (_coerce_float(channel_means.get("green")) or 0.0), (_coerce_float(channel_means.get("blue")) or 0.0)) < 0.24:
        clues.append(MediaGeolocationClue(clue_type="dark_scene", text="dark_scene", confidence=0.3, reason="Low average channel intensity suggests a dark or night scene."))
    return clues[:12]


def _extract_text_environment_clues(text: str) -> list[MediaGeolocationClue]:
    clues: list[MediaGeolocationClue] = []
    if not text:
        return clues
    keyword_sets = {
        "coastal_context": ["coast", "coastal", "harbor", "harbour", "bay", "beach", "shore"],
        "mountainous_context": ["mount", "mountain", "peak", "summit", "ridge", "alps"],
        "canyon_or_cliff_context": ["canyon", "gorge", "cliff", "cliffs"],
        "bridge_or_crossing_context": ["bridge", "crossing", "viaduct"],
        "dam_or_reservoir_context": ["dam", "reservoir"],
    }
    lowered = text.casefold()
    for clue_type, keywords in keyword_sets.items():
        matched = next((keyword for keyword in keywords if re.search(rf"\b{re.escape(keyword)}\b", lowered)), None)
        if matched is None:
            continue
        clues.append(
            MediaGeolocationClue(
                clue_type=clue_type,
                text=matched,
                confidence=0.34,
                normalized_value=matched,
                reason="OCR or caption text exposed a terrain or built-environment keyword that can help later ranking.",
            )
        )
    return clues[:8]


def _extract_time_clues(
    *,
    observed_latitude: float | None,
    exif_timestamp: str | None,
    artifact_metadata: dict[str, Any],
) -> list[MediaGeolocationClue]:
    clues: list[MediaGeolocationClue] = []
    daylight = artifact_metadata.get("daylightSignals") if isinstance(artifact_metadata.get("daylightSignals"), dict) else {}
    brightness = _coerce_float(daylight.get("brightness"))
    if brightness is not None:
        guess = "daylight" if brightness >= 0.38 else ("twilight_or_overcast" if brightness >= 0.18 else "night")
        clues.append(
            MediaGeolocationClue(
                clue_type="time_of_day_guess",
                text=guess,
                confidence=0.72 if guess == "daylight" else 0.56,
                normalized_value=guess,
                reason="Brightness-based heuristic produced a coarse time-of-day clue.",
            )
        )
    parsed_dt = _parse_datetime_like(exif_timestamp) if exif_timestamp else None
    if parsed_dt is not None:
        clues.append(
            MediaGeolocationClue(
                clue_type="exif_timestamp",
                text=parsed_dt.isoformat(),
                confidence=0.94,
                normalized_value=parsed_dt.isoformat(),
                reason="The artifact exposed an EXIF-style timestamp.",
            )
        )
        if observed_latitude is not None:
            season_guess = _season_from_month(parsed_dt.month, latitude=observed_latitude)
            clues.append(
                MediaGeolocationClue(
                    clue_type="hemisphere_aware_season",
                    text=season_guess,
                    confidence=0.86,
                    normalized_value=season_guess,
                    reason="Season inference used EXIF month plus the artifact latitude hemisphere.",
                )
            )
    return clues


def _extract_cardinal_coordinate_pairs(text: str) -> list[tuple[float, float, str]]:
    results: list[tuple[float, float, str]] = []
    patterns = [
        re.compile(r"(?P<lat>\d{1,2}(?:\.\d+)?)\s*(?P<lat_dir>[NS])[\s,;/]+(?P<lon>\d{1,3}(?:\.\d+)?)\s*(?P<lon_dir>[EW])", re.IGNORECASE),
        re.compile(r"(?P<lat_dir>[NS])\s*(?P<lat>\d{1,2}(?:\.\d+)?)[\s,;/]+(?P<lon_dir>[EW])\s*(?P<lon>\d{1,3}(?:\.\d+)?)", re.IGNORECASE),
    ]
    for pattern in patterns:
        for match in pattern.finditer(text):
            latitude = _signed_cardinal_value(match.group("lat"), match.group("lat_dir"))
            longitude = _signed_cardinal_value(match.group("lon"), match.group("lon_dir"))
            if latitude is None or longitude is None:
                continue
            if -90.0 <= latitude <= 90.0 and -180.0 <= longitude <= 180.0:
                results.append((round(latitude, 6), round(longitude, 6), _normalize_text(match.group(0))))
    return results


def _extract_dms_coordinate_pairs(text: str) -> list[tuple[float, float, str]]:
    results: list[tuple[float, float, str]] = []
    pattern = re.compile(
        r"(?P<lat_deg>\d{1,2})[°\s]+(?P<lat_min>\d{1,2})['\s]+(?P<lat_sec>\d{1,2}(?:\.\d+)?)\"?\s*(?P<lat_dir>[NS])"
        r"[\s,;/]+(?P<lon_deg>\d{1,3})[°\s]+(?P<lon_min>\d{1,2})['\s]+(?P<lon_sec>\d{1,2}(?:\.\d+)?)\"?\s*(?P<lon_dir>[EW])",
        re.IGNORECASE,
    )
    for match in pattern.finditer(text):
        latitude = _dms_to_decimal(match.group("lat_deg"), match.group("lat_min"), match.group("lat_sec"), match.group("lat_dir"))
        longitude = _dms_to_decimal(match.group("lon_deg"), match.group("lon_min"), match.group("lon_sec"), match.group("lon_dir"))
        if latitude is None or longitude is None:
            continue
        if -90.0 <= latitude <= 90.0 and -180.0 <= longitude <= 180.0:
            results.append((round(latitude, 6), round(longitude, 6), _normalize_text(match.group(0))))
    return results


def _extract_utm_mgrs_like_tokens(text: str) -> list[str]:
    tokens: list[str] = []
    patterns = [
        re.compile(r"\b\d{1,2}[C-HJ-NP-X]\s+[A-Z]{2}\s+\d{3,6}\s+\d{3,7}\b"),
        re.compile(r"\b\d{1,2}[NS]\s+\d{3,7}\s+\d{3,8}\b"),
    ]
    for pattern in patterns:
        for match in pattern.finditer(text):
            token = _normalize_text(match.group(0))
            if token and token not in tokens:
                tokens.append(token)
    return tokens[:4]


def _signed_cardinal_value(number_text: str, direction_text: str) -> float | None:
    value = _coerce_float(number_text)
    direction = _normalize_optional(direction_text)
    if value is None or not direction:
        return None
    direction = direction.upper()
    if direction in {"S", "W"}:
        value *= -1.0
    return value


def _dms_to_decimal(degrees_text: str, minutes_text: str, seconds_text: str, direction_text: str) -> float | None:
    degrees = _coerce_float(degrees_text)
    minutes = _coerce_float(minutes_text)
    seconds = _coerce_float(seconds_text)
    if degrees is None or minutes is None or seconds is None:
        return None
    decimal = abs(degrees) + (minutes / 60.0) + (seconds / 3600.0)
    direction = (_normalize_optional(direction_text) or "").upper()
    if direction in {"S", "W"}:
        decimal *= -1.0
    return decimal


def _resolve_geoclip_runtime_profile(settings: Settings) -> dict[str, Any]:
    allowed_profiles = {"full_fidelity", "balanced", "cpu_optimized"}
    profile = (_normalize_optional(settings.source_discovery_media_geoclip_runtime_profile) or "full_fidelity").casefold()
    caveats: list[str] = []
    if profile not in allowed_profiles:
        caveats.append(
            f"Unsupported GeoCLIP runtime profile `{settings.source_discovery_media_geoclip_runtime_profile}` was requested; falling back to `full_fidelity`."
        )
        profile = "full_fidelity"
    profile_default_edges: dict[str, int | None] = {
        "full_fidelity": None,
        "balanced": 1536,
        "cpu_optimized": 1024,
    }
    configured_edge = int(settings.source_discovery_media_geoclip_max_image_edge)
    if configured_edge > 0:
        max_image_edge: int | None = max(256, min(configured_edge, 4096))
    else:
        max_image_edge = profile_default_edges.get(profile)
    requested_device = (_normalize_optional(settings.source_discovery_media_geoclip_target_device) or "cpu").casefold()
    resolved_device, device_error, device_caveats = _resolve_geoclip_target_device(
        settings,
        requested_device=requested_device,
    )
    prediction_cache_entries = max(0, int(settings.source_discovery_media_geoclip_prediction_cache_entries))
    return {
        "profile": profile,
        "maxImageEdge": max_image_edge,
        "requestedDevice": requested_device,
        "resolvedDevice": resolved_device,
        "deviceError": device_error,
        "predictionCacheEntries": prediction_cache_entries,
        "experimentalAccelerationEnabled": bool(settings.source_discovery_media_geoclip_allow_experimental_acceleration),
        "caveats": _dedupe_text_list([*caveats, *device_caveats]),
    }


def _resolve_geoclip_target_device(
    settings: Settings,
    *,
    requested_device: str,
) -> tuple[str | None, str | None, list[str]]:
    normalized = requested_device.casefold().strip() if requested_device else "cpu"
    caveats: list[str] = []
    if normalized not in {"cpu", "auto", "cuda", "mps"}:
        caveats.append(f"Unsupported GeoCLIP device `{requested_device}` was requested; falling back to `cpu`.")
        normalized = "cpu"

    cuda_available = bool(
        torch is not None
        and hasattr(torch, "cuda")
        and callable(getattr(torch.cuda, "is_available", None))
        and torch.cuda.is_available()
    )
    mps_backend = getattr(getattr(torch, "backends", None), "mps", None) if torch is not None else None
    mps_available = bool(mps_backend is not None and callable(getattr(mps_backend, "is_available", None)) and mps_backend.is_available())

    if normalized == "cpu":
        return "cpu", None, caveats
    if normalized == "auto":
        if not settings.source_discovery_media_geoclip_allow_experimental_acceleration:
            return "cpu", None, caveats
        if cuda_available:
            return "cuda", None, caveats
        if mps_available:
            return "mps", None, caveats
        return "cpu", None, caveats
    if not settings.source_discovery_media_geoclip_allow_experimental_acceleration:
        reason = (
            "Non-CPU GeoCLIP execution is gated behind SOURCE_DISCOVERY_MEDIA_GEOCLIP_ALLOW_EXPERIMENTAL_ACCELERATION=true "
            "because the current repo path is validated primarily on CPU."
        )
        return None, reason, [reason]
    if normalized == "cuda":
        if not cuda_available:
            reason = "GeoCLIP requested `cuda`, but CUDA is not available in this environment."
            return None, reason, [reason]
        return "cuda", None, caveats
    if normalized == "mps":
        if not mps_available:
            reason = "GeoCLIP requested `mps`, but Apple Metal Performance Shaders are not available in this environment."
            return None, reason, [reason]
        return "mps", None, caveats
    return "cpu", None, caveats


def _prepare_geoclip_inference_artifact(
    settings: Settings,
    *,
    artifact_path: str,
    profile_config: dict[str, Any],
) -> tuple[str, dict[str, Any], list[str]]:
    metadata: dict[str, Any] = {
        "profile": profile_config.get("profile"),
        "requestedDevice": profile_config.get("requestedDevice"),
        "resolvedDevice": profile_config.get("resolvedDevice"),
        "maxImageEdge": profile_config.get("maxImageEdge"),
        "usedPreprocessedArtifact": False,
        "sourceWidth": None,
        "sourceHeight": None,
        "inferenceWidth": None,
        "inferenceHeight": None,
        "preprocessedArtifactPath": None,
    }
    caveats: list[str] = list(profile_config.get("caveats", [])) if isinstance(profile_config.get("caveats"), list) else []
    max_image_edge = profile_config.get("maxImageEdge")
    if not isinstance(max_image_edge, int) or max_image_edge <= 0:
        return artifact_path, metadata, _dedupe_text_list(caveats)
    if Image is None:
        caveats.append("GeoCLIP image resizing was skipped because Pillow is unavailable in this environment.")
        return artifact_path, metadata, _dedupe_text_list(caveats)

    source_file = Path(artifact_path)
    try:
        source_stat = source_file.stat()
    except OSError:
        caveats.append("GeoCLIP performance preprocessing could not stat the artifact path, so the original artifact was used.")
        return artifact_path, metadata, _dedupe_text_list(caveats)
    try:
        resolved_source = str(source_file.resolve())
    except OSError:
        resolved_source = str(source_file)

    try:
        with Image.open(source_file) as opened:
            oriented = ImageOps.exif_transpose(opened) if ImageOps is not None else opened.copy()
            rgb = oriented.convert("RGB")
            source_width, source_height = rgb.size
            metadata["sourceWidth"] = int(source_width)
            metadata["sourceHeight"] = int(source_height)
            longest_edge = max(source_width, source_height)
            if longest_edge <= max_image_edge:
                metadata["inferenceWidth"] = int(source_width)
                metadata["inferenceHeight"] = int(source_height)
                return artifact_path, metadata, _dedupe_text_list(caveats)
            scale = max_image_edge / float(longest_edge)
            target_width = max(1, int(round(source_width * scale)))
            target_height = max(1, int(round(source_height * scale)))
            cache_root = Path(resolve_runtime_paths(settings)["cache_dir"]) / "media-geolocation" / "geoclip-preprocessed"
            cache_root.mkdir(parents=True, exist_ok=True)
            cache_key_material = "|".join(
                [
                    resolved_source,
                    str(source_stat.st_mtime_ns),
                    str(source_stat.st_size),
                    str(profile_config.get("profile") or "full_fidelity"),
                    str(max_image_edge),
                ]
            )
            cache_key = hashlib.sha1(cache_key_material.encode("utf-8")).hexdigest()
            output_path = cache_root / f"{cache_key}.png"
            if not output_path.exists():
                lanczos = getattr(getattr(Image, "Resampling", Image), "LANCZOS", getattr(Image, "LANCZOS", 1))
                resized = rgb.resize((target_width, target_height), lanczos)
                resized.save(output_path, format="PNG")
            metadata.update(
                {
                    "usedPreprocessedArtifact": True,
                    "inferenceWidth": int(target_width),
                    "inferenceHeight": int(target_height),
                    "preprocessedArtifactPath": str(output_path),
                }
            )
            if profile_config.get("profile") != "full_fidelity":
                caveats.append(
                    f"GeoCLIP inference used the explicit `{profile_config.get('profile')}` profile with max image edge {max_image_edge}px to reduce runtime cost."
                )
            else:
                caveats.append(
                    f"GeoCLIP inference used an explicit max image edge override of {max_image_edge}px under the `full_fidelity` profile."
                )
            return str(output_path), metadata, _dedupe_text_list(caveats)
    except (OSError, UnidentifiedImageError):
        caveats.append("GeoCLIP performance preprocessing could not decode the artifact cleanly, so the original artifact was used.")
        return artifact_path, metadata, _dedupe_text_list(caveats)


def _build_geoclip_prediction_cache_key(
    runtime: dict[str, Any],
    *,
    artifact_path: str,
    max_candidates: int,
    profile_config: dict[str, Any],
) -> str:
    artifact_file = Path(artifact_path)
    try:
        artifact_stat = artifact_file.stat()
        artifact_mtime = str(artifact_stat.st_mtime_ns)
        artifact_size = str(artifact_stat.st_size)
    except OSError:
        artifact_mtime = "unknown"
        artifact_size = "unknown"
    try:
        resolved_artifact_path = str(artifact_file.resolve())
    except OSError:
        resolved_artifact_path = str(artifact_file)
    runtime_cache_key = _normalize_optional(runtime.get("cache_key")) or _normalize_optional(runtime.get("cacheKey")) or "runtime"
    return "|".join(
        [
            runtime_cache_key,
            resolved_artifact_path,
            artifact_mtime,
            artifact_size,
            str(profile_config.get("profile") or "full_fidelity"),
            str(profile_config.get("maxImageEdge")),
            str(profile_config.get("requestedDevice") or "cpu"),
            str(profile_config.get("resolvedDevice") or "cpu"),
            str(max_candidates),
        ]
    )


def _lookup_geoclip_prediction_cache(cache_key: str) -> dict[str, Any] | None:
    with _GEOCLIP_PREDICTION_CACHE_LOCK:
        cached = _GEOCLIP_PREDICTION_CACHE.get(cache_key)
        if cached is None:
            return None
        _GEOCLIP_PREDICTION_CACHE.move_to_end(cache_key)
        return dict(cached)


def _store_geoclip_prediction_cache(
    cache_key: str,
    payload: dict[str, Any],
    *,
    max_entries: int,
) -> None:
    if max_entries <= 0:
        return
    with _GEOCLIP_PREDICTION_CACHE_LOCK:
        _GEOCLIP_PREDICTION_CACHE[cache_key] = dict(payload)
        _GEOCLIP_PREDICTION_CACHE.move_to_end(cache_key)
        while len(_GEOCLIP_PREDICTION_CACHE) > max_entries:
            _GEOCLIP_PREDICTION_CACHE.popitem(last=False)


def _move_geoclip_model_to_device(model: Any, *, device: str) -> None:
    if device == "cpu":
        if hasattr(model, "to") and callable(getattr(model, "to")):
            model.to("cpu")
        if hasattr(model, "device"):
            model.device = "cpu"
        return
    if not hasattr(model, "to") or not callable(getattr(model, "to")):
        raise RuntimeError(f"GeoCLIP model does not expose `.to(...)`, so it cannot be moved to `{device}` safely.")
    model.to(device)
    if hasattr(model, "device"):
        model.device = device


def _load_geoclip_runtime(settings: Settings) -> tuple[dict[str, Any] | None, MediaGeolocationEngineAttempt]:
    attempt = MediaGeolocationEngineAttempt(
        engine="geoclip",
        role="specialized_geocoder",
        status="unavailable",
        warm_state="cold",
    )
    profile_config = _resolve_geoclip_runtime_profile(settings)
    attempt.metadata = {
        "performanceProfile": profile_config.get("profile"),
        "requestedDevice": profile_config.get("requestedDevice"),
        "resolvedDevice": profile_config.get("resolvedDevice"),
        "maxImageEdge": profile_config.get("maxImageEdge"),
        "predictionCacheEntries": profile_config.get("predictionCacheEntries"),
        "experimentalAccelerationEnabled": profile_config.get("experimentalAccelerationEnabled"),
    }
    if profile_config.get("deviceError"):
        attempt.availability_reason = str(profile_config["deviceError"])
        attempt.caveats = _dedupe_text_list(list(profile_config.get("caveats", [])) + [attempt.availability_reason])
        return None, attempt
    if GeoCLIP is None:
        attempt.availability_reason = "GeoCLIP is not installed in this environment."
        attempt.caveats = ["GeoCLIP is not installed in this environment."]
        return None, attempt
    expected_version = _normalize_optional(settings.source_discovery_media_geoclip_expected_version)
    if expected_version:
        try:
            installed_version = importlib_metadata.version("geoclip")
        except importlib_metadata.PackageNotFoundError:
            installed_version = None
        if installed_version != expected_version:
            attempt.availability_reason = f"Expected GeoCLIP version {expected_version}, found {installed_version or 'missing'}."
            attempt.caveats = [attempt.availability_reason]
            attempt.metadata = {"expectedVersion": expected_version, "installedVersion": installed_version}
            return None, attempt
        attempt.metadata["installedVersion"] = installed_version
    weights_path = _normalize_optional(settings.source_discovery_media_geoclip_weights_path)
    clip_backbone_model_id = (
        _normalize_optional(settings.source_discovery_media_geoclip_clip_backbone_model_id)
        or "openai/clip-vit-large-patch14"
    )
    cache_dir_path = _resolve_media_model_cache_dir(settings, configured=_normalize_optional(settings.source_discovery_media_geoclip_model_cache_dir))
    cache_dir = str(cache_dir_path)
    clip_backbone_dir = _resolve_media_model_dir(
        settings,
        configured=_normalize_optional(settings.source_discovery_media_geoclip_clip_backbone_dir),
        default_segments=("media-geolocation", "geoclip", "clip-backbone"),
    )
    bundled_weights_dir = _discover_geoclip_bundled_weights_dir()
    bundled_weights_available = bundled_weights_dir is not None and bundled_weights_dir.exists()
    if not settings.source_discovery_media_geoclip_allow_runtime_download and not (weights_path or bundled_weights_available):
        attempt.availability_reason = "GeoCLIP requires a prepared local weights path or cache directory when runtime downloads are disabled."
        attempt.caveats = [attempt.availability_reason]
        return None, attempt
    if weights_path and not Path(weights_path).exists():
        attempt.availability_reason = "Configured GeoCLIP weights path does not exist."
        attempt.caveats = [attempt.availability_reason]
        attempt.metadata = {"weightsPath": weights_path}
        return None, attempt
    _apply_hf_cache_environment(cache_dir=cache_dir, offline=not settings.source_discovery_media_geoclip_allow_runtime_download)
    clip_backbone_snapshot_dir, clip_backbone_error = _prepare_hf_repo_local_snapshot(
        repo_id=clip_backbone_model_id,
        cache_dir=cache_dir_path,
        local_dir=clip_backbone_dir,
        allow_download=settings.source_discovery_media_geoclip_allow_runtime_download,
        allow_patterns=[
            "*.json",
            "*.txt",
            "*.safetensors",
            "*.bin",
            "*.model",
        ],
    )
    if clip_backbone_snapshot_dir is None:
        attempt.availability_reason = clip_backbone_error or "GeoCLIP CLIP backbone is unavailable."
        attempt.caveats = [attempt.availability_reason]
        attempt.metadata = {
            "cacheDir": cache_dir,
            "clipBackboneModelId": clip_backbone_model_id,
            "clipBackboneDir": str(clip_backbone_dir),
        }
        return None, attempt
    cache_key = "|".join(
        [
            weights_path or "",
            cache_dir,
            str(clip_backbone_snapshot_dir),
            clip_backbone_model_id,
            str(bool(settings.source_discovery_media_geoclip_allow_runtime_download)),
            str(profile_config.get("resolvedDevice") or "cpu"),
        ]
    )
    with _GEOCLIP_RUNTIME_LOCK:
        existing = _GEOCLIP_RUNTIME_CACHE.get(cache_key)
        if isinstance(existing, dict) and existing.get("model") is not None:
            attempt.status = "available"
            attempt.warm_state = "warm"
            attempt.model_name = str(existing.get("model_name") or "GeoCLIP")
            attempt.metadata = {
                **attempt.metadata,
                "cacheKey": cache_key,
                "loadedAt": existing.get("loaded_at"),
                "resolvedDevice": existing.get("resolved_device") or profile_config.get("resolvedDevice"),
                "performanceProfile": existing.get("performance_profile") or profile_config.get("profile"),
            }
            attempt.caveats = _dedupe_text_list(list(profile_config.get("caveats", [])))
            return existing, attempt
        manual_weights_dir = Path(weights_path) if weights_path else bundled_weights_dir
        init_kwargs: dict[str, Any] = {}
        try:
            signature = inspect.signature(GeoCLIP)
        except (TypeError, ValueError):
            signature = None
        if signature is not None:
            parameters = signature.parameters
            if weights_path and "weights_path" in parameters:
                init_kwargs["weights_path"] = weights_path
            if cache_dir and "cache_dir" in parameters:
                init_kwargs["cache_dir"] = cache_dir
            if "download" in parameters:
                init_kwargs["download"] = bool(settings.source_discovery_media_geoclip_allow_runtime_download)
            if manual_weights_dir is not None and "from_pretrained" in parameters:
                init_kwargs["from_pretrained"] = False
        try:
            model = _instantiate_geoclip_with_local_backbone(
                clip_backbone_path=clip_backbone_snapshot_dir,
                cache_dir=cache_dir_path,
                init_kwargs=init_kwargs,
            )
            if manual_weights_dir is not None:
                _load_geoclip_weights_from_directory(model, manual_weights_dir)
            _move_geoclip_model_to_device(model, device=str(profile_config.get("resolvedDevice") or "cpu"))
            _patch_geoclip_predict_performance(model)
        except Exception as exc:  # pragma: no cover - optional dependency runtime variance
            attempt.availability_reason = f"GeoCLIP load failed: {_normalize_text(str(exc)) or 'unknown error'}"
            attempt.caveats = _dedupe_text_list(list(profile_config.get("caveats", [])) + [attempt.availability_reason])
            attempt.metadata = {
                **attempt.metadata,
                "cacheKey": cache_key,
                "weightsPath": weights_path,
                "cacheDir": cache_dir,
                "clipBackboneModelId": clip_backbone_model_id,
                "clipBackboneDir": str(clip_backbone_snapshot_dir),
            }
            return None, attempt
        runtime = {
            "model": model,
            "model_name": "GeoCLIP",
            "loaded_at": datetime.utcnow().isoformat() + "Z",
            "weights_path": weights_path,
            "cache_dir": cache_dir,
            "bundled_weights_dir": str(bundled_weights_dir) if bundled_weights_dir is not None else None,
            "clip_backbone_model_id": clip_backbone_model_id,
            "clip_backbone_dir": str(clip_backbone_snapshot_dir),
            "cache_key": cache_key,
            "requested_device": str(profile_config.get("requestedDevice") or "cpu"),
            "resolved_device": str(profile_config.get("resolvedDevice") or "cpu"),
            "performance_profile": str(profile_config.get("profile") or "full_fidelity"),
            "max_image_edge": profile_config.get("maxImageEdge"),
            "prediction_cache_entries": int(profile_config.get("predictionCacheEntries") or 0),
            "experimental_acceleration_enabled": bool(profile_config.get("experimentalAccelerationEnabled")),
        }
        _GEOCLIP_RUNTIME_CACHE[cache_key] = runtime
        attempt.status = "available"
        attempt.warm_state = "cold_loaded"
        attempt.model_name = "GeoCLIP"
        attempt.metadata = {
            **attempt.metadata,
            "cacheKey": cache_key,
            "weightsPath": weights_path,
            "cacheDir": cache_dir,
            "bundledWeightsDir": str(bundled_weights_dir) if bundled_weights_dir is not None else None,
            "clipBackboneModelId": clip_backbone_model_id,
            "clipBackboneDir": str(clip_backbone_snapshot_dir),
            "resolvedDevice": str(profile_config.get("resolvedDevice") or "cpu"),
            "performanceProfile": str(profile_config.get("profile") or "full_fidelity"),
        }
        attempt.caveats = _dedupe_text_list(list(profile_config.get("caveats", [])))
        return runtime, attempt


def _load_streetclip_runtime(settings: Settings) -> tuple[dict[str, Any] | None, MediaGeolocationEngineAttempt]:
    attempt = MediaGeolocationEngineAttempt(
        engine="streetclip",
        role="street_scene_reranker",
        status="unavailable",
        warm_state="cold",
    )
    if Image is None or torch is None or AutoModel is None or AutoProcessor is None:
        attempt.availability_reason = "StreetCLIP requires Pillow, torch, and transformers in the local environment."
        attempt.caveats = [attempt.availability_reason]
        return None, attempt
    expected_version = _normalize_optional(settings.source_discovery_media_streetclip_expected_transformers_version)
    if expected_version:
        try:
            installed_version = importlib_metadata.version("transformers")
        except importlib_metadata.PackageNotFoundError:
            installed_version = None
        if installed_version != expected_version:
            attempt.availability_reason = f"Expected transformers version {expected_version}, found {installed_version or 'missing'}."
            attempt.caveats = [attempt.availability_reason]
            attempt.metadata = {"expectedVersion": expected_version, "installedVersion": installed_version}
            return None, attempt
        attempt.metadata["installedVersion"] = installed_version
    model_id = settings.source_discovery_media_streetclip_model_id.strip() or "geolocal/StreetCLIP"
    cache_dir_path = _resolve_media_model_cache_dir(settings, configured=_normalize_optional(settings.source_discovery_media_streetclip_model_cache_dir))
    cache_dir = str(cache_dir_path)
    local_dir = _resolve_media_model_dir(
        settings,
        configured=_normalize_optional(settings.source_discovery_media_streetclip_local_dir),
        default_segments=("media-geolocation", "streetclip", _safe_id(model_id)),
    )
    local_only = not settings.source_discovery_media_streetclip_allow_runtime_download
    _apply_hf_cache_environment(cache_dir=cache_dir, offline=local_only)
    snapshot_dir, snapshot_error = _prepare_hf_repo_local_snapshot(
        repo_id=model_id,
        cache_dir=cache_dir_path,
        local_dir=local_dir,
        allow_download=not local_only,
        allow_patterns=[
            "*.json",
            "*.txt",
            "*.safetensors",
            "*.bin",
            "*.model",
        ],
    )
    if snapshot_dir is None:
        attempt.availability_reason = snapshot_error or "StreetCLIP snapshot is unavailable."
        attempt.caveats = [attempt.availability_reason]
        attempt.metadata = {"modelId": model_id, "cacheDir": cache_dir, "localDir": str(local_dir), "localOnly": local_only}
        return None, attempt
    cache_key = "|".join([model_id, cache_dir, str(snapshot_dir), str(local_only)])
    with _STREETCLIP_RUNTIME_LOCK:
        existing = _STREETCLIP_RUNTIME_CACHE.get(cache_key)
        if isinstance(existing, dict) and existing.get("model") is not None and existing.get("processor") is not None:
            attempt.status = "available"
            attempt.warm_state = "warm"
            attempt.model_name = str(existing.get("model_name") or model_id)
            attempt.metadata = {"cacheKey": cache_key, "loadedAt": existing.get("loaded_at")}
            return existing, attempt
        try:
            processor = AutoProcessor.from_pretrained(str(snapshot_dir), local_files_only=True, cache_dir=cache_dir)
            model = AutoModel.from_pretrained(str(snapshot_dir), local_files_only=True, cache_dir=cache_dir)
        except Exception as exc:  # pragma: no cover - optional dependency runtime variance
            attempt.availability_reason = f"StreetCLIP load failed: {_normalize_text(str(exc)) or 'unknown error'}"
            attempt.caveats = [attempt.availability_reason]
            attempt.metadata = {
                "modelId": model_id,
                "cacheDir": cache_dir,
                "localDir": str(snapshot_dir),
                "localOnly": local_only,
            }
            return None, attempt
        runtime = {
            "model": model,
            "processor": processor,
            "model_name": model_id,
            "loaded_at": datetime.utcnow().isoformat() + "Z",
            "local_dir": str(snapshot_dir),
        }
        _STREETCLIP_RUNTIME_CACHE[cache_key] = runtime
        attempt.status = "available"
        attempt.warm_state = "cold_loaded"
        attempt.model_name = model_id
        attempt.metadata = {
            "modelId": model_id,
            "cacheDir": cache_dir,
            "localDir": str(snapshot_dir),
            "localOnly": local_only,
        }
        return runtime, attempt


def inspect_media_geolocation_models(settings: Settings) -> list[MediaGeolocationModelHealth]:
    return [
        _inspect_geoclip_model_health(settings),
        _inspect_streetclip_model_health(settings),
    ]


def inspect_media_geolocation_model(settings: Settings, model_name: str) -> MediaGeolocationModelHealth:
    normalized = (model_name or "").strip().lower()
    if normalized == "geoclip":
        return _inspect_geoclip_model_health(settings)
    if normalized == "streetclip":
        return _inspect_streetclip_model_health(settings)
    raise ValueError(f"Unsupported media geolocation model: {model_name}")


def prewarm_media_geolocation_model(
    settings: Settings,
    model_name: str,
) -> tuple[MediaGeolocationModelHealth, MediaGeolocationEngineAttempt]:
    normalized = (model_name or "").strip().lower()
    if normalized == "geoclip":
        _, attempt = _load_geoclip_runtime(settings)
        return _inspect_geoclip_model_health(settings), attempt
    if normalized == "streetclip":
        _, attempt = _load_streetclip_runtime(settings)
        return _inspect_streetclip_model_health(settings), attempt
    raise ValueError(f"Unsupported media geolocation model: {model_name}")


def _inspect_geoclip_model_health(settings: Settings) -> MediaGeolocationModelHealth:
    enabled = settings.source_discovery_media_geoclip_enabled
    profile_config = _resolve_geoclip_runtime_profile(settings)
    expected_version = _normalize_optional(settings.source_discovery_media_geoclip_expected_version)
    installed_version = _installed_distribution_version("geoclip")
    weights_path = _normalize_optional(settings.source_discovery_media_geoclip_weights_path)
    cache_dir_path = _resolve_media_model_cache_dir(settings, configured=_normalize_optional(settings.source_discovery_media_geoclip_model_cache_dir))
    cache_dir = str(cache_dir_path)
    clip_backbone_model_id = _normalize_optional(settings.source_discovery_media_geoclip_clip_backbone_model_id) or "openai/clip-vit-large-patch14"
    clip_backbone_dir = _resolve_media_model_dir(
        settings,
        configured=_normalize_optional(settings.source_discovery_media_geoclip_clip_backbone_dir),
        default_segments=("media-geolocation", "geoclip", "clip-backbone"),
    )
    bundled_weights_dir = _discover_geoclip_bundled_weights_dir()
    manual_weights_dir = Path(weights_path) if weights_path else bundled_weights_dir
    present_components: list[str] = []
    missing_components: list[str] = []
    caveats: list[str] = []
    metadata: dict[str, Any] = {
        "clipBackboneModelId": clip_backbone_model_id,
        "bundledWeightsDir": str(bundled_weights_dir) if bundled_weights_dir is not None else None,
        "performanceProfile": profile_config.get("profile"),
        "requestedDevice": profile_config.get("requestedDevice"),
        "resolvedDevice": profile_config.get("resolvedDevice"),
        "maxImageEdge": profile_config.get("maxImageEdge"),
        "predictionCacheEntries": profile_config.get("predictionCacheEntries"),
        "experimentalAccelerationEnabled": profile_config.get("experimentalAccelerationEnabled"),
        "validatedDevices": ["cpu"],
    }
    if GeoCLIP is not None and installed_version is not None:
        present_components.append("package:geoclip")
    else:
        missing_components.append("package:geoclip")
        caveats.append("GeoCLIP is not installed in this environment.")
    if expected_version:
        metadata["expectedVersion"] = expected_version
    if installed_version:
        metadata["installedVersion"] = installed_version
    version_matches = not expected_version or installed_version == expected_version
    if expected_version and not version_matches:
        caveats.append(f"Expected GeoCLIP version {expected_version}, found {installed_version or 'missing'}.")
    if profile_config.get("deviceError"):
        caveats.append(str(profile_config["deviceError"]))
    if manual_weights_dir is not None and _geoclip_weights_dir_ready(manual_weights_dir):
        present_components.append("weights")
    else:
        missing_components.append("weights")
    if _hf_snapshot_dir_ready(clip_backbone_dir):
        present_components.append("clip_backbone_snapshot")
    else:
        missing_components.append("clip_backbone_snapshot")
    runtime_ready, warm_state, loaded_at = _geoclip_runtime_state(
        settings,
        cache_dir=cache_dir,
        weights_path=weights_path,
        clip_backbone_model_id=clip_backbone_model_id,
        clip_backbone_dir=clip_backbone_dir,
    )
    if loaded_at:
        metadata["runtimeLoadedAt"] = loaded_at
    install_ready = (
        enabled
        and "package:geoclip" in present_components
        and version_matches
        and "weights" in present_components
        and "clip_backbone_snapshot" in present_components
        and profile_config.get("resolvedDevice") is not None
    )
    if not enabled:
        status = "disabled"
        summary = "GeoCLIP is disabled by configuration."
    elif "package:geoclip" not in present_components:
        status = "missing_dependency"
        summary = "GeoCLIP package support is missing in this environment."
    elif expected_version and not version_matches:
        status = "version_mismatch"
        summary = f"GeoCLIP version mismatch: expected {expected_version}, found {installed_version or 'missing'}."
    elif profile_config.get("deviceError"):
        status = "unsupported_runtime"
        summary = str(profile_config["deviceError"])
    elif install_ready and runtime_ready:
        status = "ready"
        summary = "GeoCLIP local assets are present and the runtime is prewarmed."
    elif install_ready:
        status = "ready"
        summary = "GeoCLIP local assets are present and ready for explicit prewarm."
    elif settings.source_discovery_media_geoclip_allow_runtime_download:
        status = "degraded"
        summary = "GeoCLIP local assets are incomplete, but explicit prewarm may still recover them because runtime downloads are allowed."
    else:
        status = "missing_asset"
        summary = "GeoCLIP is enabled but one or more local assets required for no-download runtime are missing."
    return MediaGeolocationModelHealth(
        model_name="geoclip",
        role="specialized geocoder",
        enabled=enabled,
        status=status,
        install_ready=install_ready,
        runtime_ready=runtime_ready,
        warm_state=warm_state,
        summary=summary,
        installed_version=installed_version,
        expected_version=expected_version,
        model_id="GeoCLIP",
        download_allowed=bool(settings.source_discovery_media_geoclip_allow_runtime_download),
        cache_dir=cache_dir,
        local_dir=None,
        weights_path=str(manual_weights_dir) if manual_weights_dir is not None else None,
        clip_backbone_dir=str(clip_backbone_dir),
        missing_components=missing_components,
        present_components=present_components,
        metadata=metadata,
        caveats=_dedupe_text_list([*caveats, *list(profile_config.get("caveats", []))]),
    )


def _inspect_streetclip_model_health(settings: Settings) -> MediaGeolocationModelHealth:
    enabled = settings.source_discovery_media_streetclip_enabled
    expected_version = _normalize_optional(settings.source_discovery_media_streetclip_expected_transformers_version)
    installed_version = _installed_distribution_version("transformers")
    model_id = settings.source_discovery_media_streetclip_model_id.strip() or "geolocal/StreetCLIP"
    cache_dir_path = _resolve_media_model_cache_dir(settings, configured=_normalize_optional(settings.source_discovery_media_streetclip_model_cache_dir))
    cache_dir = str(cache_dir_path)
    local_dir = _resolve_media_model_dir(
        settings,
        configured=_normalize_optional(settings.source_discovery_media_streetclip_local_dir),
        default_segments=("media-geolocation", "streetclip", _safe_id(model_id)),
    )
    present_components: list[str] = []
    missing_components: list[str] = []
    caveats: list[str] = []
    metadata: dict[str, Any] = {"modelId": model_id}
    if Image is not None:
        present_components.append("dependency:pillow")
    else:
        missing_components.append("dependency:pillow")
    if torch is not None:
        present_components.append("dependency:torch")
    else:
        missing_components.append("dependency:torch")
    if AutoModel is not None and AutoProcessor is not None:
        present_components.append("dependency:transformers")
    else:
        missing_components.append("dependency:transformers")
    if installed_version:
        present_components.append("package:transformers")
        metadata["installedVersion"] = installed_version
    else:
        missing_components.append("package:transformers")
    version_matches = not expected_version or installed_version == expected_version
    if expected_version:
        metadata["expectedVersion"] = expected_version
    if expected_version and not version_matches:
        caveats.append(f"Expected transformers version {expected_version}, found {installed_version or 'missing'}.")
    if _hf_snapshot_dir_ready(local_dir):
        present_components.append("model_snapshot")
    else:
        missing_components.append("model_snapshot")
    runtime_ready, warm_state, loaded_at = _streetclip_runtime_state(
        settings,
        cache_dir=cache_dir,
        model_id=model_id,
        local_dir=local_dir,
    )
    if loaded_at:
        metadata["runtimeLoadedAt"] = loaded_at
    install_ready = (
        enabled
        and all(
            component in present_components
            for component in ["dependency:pillow", "dependency:torch", "dependency:transformers", "package:transformers", "model_snapshot"]
        )
        and version_matches
    )
    if not enabled:
        status = "disabled"
        summary = "StreetCLIP is disabled by configuration."
    elif any(component in missing_components for component in ["dependency:pillow", "dependency:torch", "dependency:transformers", "package:transformers"]):
        status = "missing_dependency"
        summary = "StreetCLIP dependencies are incomplete in this environment."
    elif expected_version and not version_matches:
        status = "version_mismatch"
        summary = f"Transformers version mismatch for StreetCLIP: expected {expected_version}, found {installed_version or 'missing'}."
    elif install_ready and runtime_ready:
        status = "ready"
        summary = "StreetCLIP local assets are present and the runtime is prewarmed."
    elif install_ready:
        status = "ready"
        summary = "StreetCLIP local assets are present and ready for explicit prewarm."
    elif settings.source_discovery_media_streetclip_allow_runtime_download:
        status = "degraded"
        summary = "StreetCLIP local assets are incomplete, but explicit prewarm may still recover them because runtime downloads are allowed."
    else:
        status = "missing_asset"
        summary = "StreetCLIP is enabled but one or more local assets required for no-download runtime are missing."
    return MediaGeolocationModelHealth(
        model_name="streetclip",
        role="street-scene reranker",
        enabled=enabled,
        status=status,
        install_ready=install_ready,
        runtime_ready=runtime_ready,
        warm_state=warm_state,
        summary=summary,
        installed_version=installed_version,
        expected_version=expected_version,
        model_id=model_id,
        download_allowed=bool(settings.source_discovery_media_streetclip_allow_runtime_download),
        cache_dir=cache_dir,
        local_dir=str(local_dir),
        weights_path=None,
        clip_backbone_dir=None,
        missing_components=missing_components,
        present_components=present_components,
        metadata=metadata,
        caveats=_dedupe_text_list(caveats),
    )


def _installed_distribution_version(distribution_name: str) -> str | None:
    try:
        return importlib_metadata.version(distribution_name)
    except importlib_metadata.PackageNotFoundError:
        return None


def _geoclip_weights_dir_ready(path: Path) -> bool:
    return path.exists() and all(
        (path / file_name).exists()
        for file_name in ["image_encoder_mlp_weights.pth", "location_encoder_weights.pth", "logit_scale_weights.pth"]
    )


def _hf_snapshot_dir_ready(path: Path) -> bool:
    if not path.exists() or not path.is_dir():
        return False
    has_config = any((path / file_name).exists() for file_name in ["config.json", "preprocessor_config.json", "tokenizer_config.json"])
    has_weights = False
    for pattern in ["*.safetensors", "*.bin", "*.model"]:
        if next(path.rglob(pattern), None) is not None:
            has_weights = True
            break
    return has_config and has_weights


def _geoclip_runtime_state(
    settings: Settings,
    *,
    cache_dir: str,
    weights_path: str | None,
    clip_backbone_model_id: str,
    clip_backbone_dir: Path,
) -> tuple[bool, str, str | None]:
    cache_key = "|".join(
        [
            weights_path or "",
            cache_dir,
            str(clip_backbone_dir),
            clip_backbone_model_id,
            str(bool(settings.source_discovery_media_geoclip_allow_runtime_download)),
        ]
    )
    with _GEOCLIP_RUNTIME_LOCK:
        runtime = _GEOCLIP_RUNTIME_CACHE.get(cache_key)
        if isinstance(runtime, dict) and runtime.get("model") is not None:
            return True, "warm", _normalize_optional(runtime.get("loaded_at"))
    return False, "cold", None


def _streetclip_runtime_state(
    settings: Settings,
    *,
    cache_dir: str,
    model_id: str,
    local_dir: Path,
) -> tuple[bool, str, str | None]:
    cache_key = "|".join(
        [
            model_id,
            cache_dir,
            str(local_dir),
            str(not settings.source_discovery_media_streetclip_allow_runtime_download),
        ]
    )
    with _STREETCLIP_RUNTIME_LOCK:
        runtime = _STREETCLIP_RUNTIME_CACHE.get(cache_key)
        if isinstance(runtime, dict) and runtime.get("model") is not None and runtime.get("processor") is not None:
            return True, "warm", _normalize_optional(runtime.get("loaded_at"))
    return False, "cold", None


def _apply_hf_cache_environment(*, cache_dir: str | None, offline: bool) -> None:
    if cache_dir:
        os.environ["HF_HOME"] = cache_dir
        os.environ["HF_HUB_CACHE"] = cache_dir
        os.environ["HUGGINGFACE_HUB_CACHE"] = cache_dir
        os.environ["TRANSFORMERS_CACHE"] = cache_dir
        os.environ["HF_ASSETS_CACHE"] = cache_dir
        os.environ["XDG_CACHE_HOME"] = str(Path(cache_dir).parent)
    if offline:
        os.environ["HF_HUB_OFFLINE"] = "1"
        os.environ["TRANSFORMERS_OFFLINE"] = "1"
    else:
        os.environ["HF_HUB_OFFLINE"] = "0"
        os.environ["TRANSFORMERS_OFFLINE"] = "0"


def _resolve_media_model_cache_dir(settings: Settings, *, configured: str | None) -> Path:
    if configured:
        candidate = Path(configured)
        if not candidate.is_absolute():
            candidate = (Path(resolve_runtime_paths(settings)["resource_dir"]) / candidate).resolve()
        return candidate
    return (Path(resolve_runtime_paths(settings)["cache_dir"]) / "huggingface").resolve()


def _resolve_media_model_dir(settings: Settings, *, configured: str | None, default_segments: tuple[str, ...]) -> Path:
    if configured:
        candidate = Path(configured)
        if not candidate.is_absolute():
            candidate = (Path(resolve_runtime_paths(settings)["resource_dir"]) / candidate).resolve()
        return candidate
    return (Path(resolve_runtime_paths(settings)["cache_dir"]) / Path(*default_segments)).resolve()


def _prepare_hf_repo_local_snapshot(
    *,
    repo_id: str,
    cache_dir: Path,
    local_dir: Path,
    allow_download: bool,
    allow_patterns: list[str] | None = None,
) -> tuple[Path | None, str | None]:
    cache_dir.mkdir(parents=True, exist_ok=True)
    local_dir.parent.mkdir(parents=True, exist_ok=True)
    if snapshot_download is None:
        if _hf_snapshot_is_usable(local_dir):
            return local_dir, None
        return None, "huggingface_hub is required to prepare the local model snapshot."
    try:
        resolved = snapshot_download(
            repo_id,
            cache_dir=str(cache_dir),
            local_dir=str(local_dir),
            local_files_only=not allow_download,
            allow_patterns=allow_patterns,
            max_workers=1,
        )
        resolved_path = Path(resolved).resolve()
        if _hf_snapshot_is_usable(resolved_path):
            return resolved_path, None
    except Exception as exc:  # pragma: no cover - optional dependency runtime variance
        if _hf_snapshot_is_usable(local_dir):
            return local_dir, None
        reason = _normalize_text(str(exc)) or "unknown error"
        if allow_download:
            return None, f"Model snapshot preparation failed for {repo_id}: {reason}"
        return None, f"Local model snapshot is missing or incomplete for {repo_id}: {reason}"
    if _hf_snapshot_is_usable(local_dir):
        return local_dir, None
    return None, f"Local model snapshot is missing required files for {repo_id}."


def _hf_snapshot_is_usable(path: Path) -> bool:
    if not path.exists() or not path.is_dir():
        return False
    has_config = (path / "config.json").exists()
    has_processor = any((path / name).exists() for name in ("preprocessor_config.json", "processor_config.json", "tokenizer_config.json"))
    has_weights = any((path / name).exists() for name in ("model.safetensors", "pytorch_model.bin", "open_clip_pytorch_model.bin"))
    return has_config and has_processor and has_weights


def _instantiate_geoclip_with_local_backbone(
    *,
    clip_backbone_path: Path,
    cache_dir: Path,
    init_kwargs: dict[str, Any],
) -> Any:
    from geoclip.model import image_encoder as geoclip_image_encoder  # type: ignore[import-not-found]

    original_clip_loader = geoclip_image_encoder.CLIPModel.from_pretrained
    original_processor_loader = geoclip_image_encoder.AutoProcessor.from_pretrained

    def _patched_clip_loader(_: str, *args: Any, **kwargs: Any) -> Any:
        kwargs["local_files_only"] = True
        kwargs["cache_dir"] = str(cache_dir)
        return original_clip_loader(str(clip_backbone_path), *args, **kwargs)

    def _patched_processor_loader(_: str, *args: Any, **kwargs: Any) -> Any:
        kwargs["local_files_only"] = True
        kwargs["cache_dir"] = str(cache_dir)
        return original_processor_loader(str(clip_backbone_path), *args, **kwargs)

    geoclip_image_encoder.CLIPModel.from_pretrained = _patched_clip_loader
    geoclip_image_encoder.AutoProcessor.from_pretrained = _patched_processor_loader
    try:
        model = GeoCLIP(**init_kwargs)
        _patch_geoclip_image_encoder_output_compat(model)
        return model
    finally:
        geoclip_image_encoder.CLIPModel.from_pretrained = original_clip_loader
        geoclip_image_encoder.AutoProcessor.from_pretrained = original_processor_loader


def _patch_geoclip_image_encoder_output_compat(model: Any) -> None:
    image_encoder = getattr(model, "image_encoder", None)
    if image_encoder is None or not hasattr(image_encoder, "CLIP") or not hasattr(image_encoder, "mlp"):
        return

    def _patched_forward(self: Any, x: Any) -> Any:
        clip_output = self.CLIP.get_image_features(pixel_values=x)
        if hasattr(clip_output, "image_embeds"):
            clip_features = clip_output.image_embeds
        elif hasattr(clip_output, "pooler_output"):
            clip_features = clip_output.pooler_output
        elif isinstance(clip_output, (list, tuple)) and clip_output:
            clip_features = clip_output[0]
        else:
            clip_features = clip_output
        return self.mlp(clip_features)

    image_encoder.forward = _patched_forward.__get__(image_encoder, image_encoder.__class__)


def _patch_geoclip_predict_performance(model: Any) -> None:
    if getattr(model, "_11writer_predict_perf_patch", False):
        return
    if Image is None or torch is None:
        return
    if not callable(getattr(model, "predict", None)):
        return
    if not callable(getattr(model, "forward", None)):
        return
    image_encoder = getattr(model, "image_encoder", None)
    if image_encoder is None or not callable(getattr(image_encoder, "preprocess_image", None)):
        return

    def _patched_predict(self: Any, image_path: str, top_k: int) -> Any:
        with Image.open(image_path) as opened:
            image = self.image_encoder.preprocess_image(opened)
        image = image.to(self.device)

        cached_gallery = getattr(self, "_11writer_cached_gps_gallery", None)
        cached_gallery_device = getattr(self, "_11writer_cached_gps_gallery_device", None)
        if cached_gallery is None or cached_gallery_device != self.device:
            cached_gallery = self.gps_gallery.to(self.device)
            self._11writer_cached_gps_gallery = cached_gallery
            self._11writer_cached_gps_gallery_device = self.device

        logits_per_image = self.forward(image, cached_gallery)
        probs_per_image = logits_per_image.softmax(dim=-1).cpu()
        top_pred = torch.topk(probs_per_image, top_k, dim=1)
        top_pred_gps = self.gps_gallery[top_pred.indices[0]]
        top_pred_prob = top_pred.values[0]
        return top_pred_gps, top_pred_prob

    model.predict = _patched_predict.__get__(model, model.__class__)
    model._11writer_predict_perf_patch = True


def _discover_geoclip_bundled_weights_dir() -> Path | None:
    try:
        class_file = Path(inspect.getfile(GeoCLIP)).resolve()
    except (TypeError, OSError):
        return None
    weights_dir = class_file.parent / "weights"
    return weights_dir if weights_dir.exists() else None


def _load_geoclip_weights_from_directory(model: Any, weights_dir: Path) -> None:
    if torch is None:
        raise RuntimeError("torch is required to load GeoCLIP weights.")
    image_weights = weights_dir / "image_encoder_mlp_weights.pth"
    location_weights = weights_dir / "location_encoder_weights.pth"
    logit_scale_weights = weights_dir / "logit_scale_weights.pth"
    if not image_weights.exists() or not location_weights.exists() or not logit_scale_weights.exists():
        raise FileNotFoundError("GeoCLIP weights directory is missing one or more required weight files.")
    model.image_encoder.mlp.load_state_dict(torch.load(image_weights, map_location="cpu"))
    model.location_encoder.load_state_dict(torch.load(location_weights, map_location="cpu"))
    model.logit_scale = torch.nn.Parameter(torch.load(logit_scale_weights, map_location="cpu"))


def _load_media_geolocation_place_gazetteer(settings: Settings) -> list[dict[str, Any]]:
    path = Path(settings.source_discovery_media_geolocation_place_gazetteer_path)
    try:
        resolved_path = path.resolve()
    except OSError:
        resolved_path = path
    if not resolved_path.exists():
        return []
    mtime_ns = resolved_path.stat().st_mtime_ns
    cache_key = str(resolved_path)
    with _PLACE_GAZETTEER_RUNTIME_LOCK:
        cached = _PLACE_GAZETTEER_RUNTIME_CACHE.get(cache_key)
        if cached and cached.get("mtimeNs") == mtime_ns:
            return list(cached.get("entries", []))
    try:
        payload = json.loads(resolved_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    raw_places = payload.get("places", []) if isinstance(payload, dict) else []
    entries: list[dict[str, Any]] = []
    for raw_entry in raw_places:
        if not isinstance(raw_entry, dict):
            continue
        name = _normalize_text(raw_entry.get("name"))
        kind = _normalize_text(raw_entry.get("kind")).casefold() or "unknown"
        latitude = _coerce_float(raw_entry.get("latitude"))
        longitude = _coerce_float(raw_entry.get("longitude"))
        if not name or latitude is None or longitude is None:
            continue
        raw_aliases = raw_entry.get("aliases", [])
        aliases = [
            alias
            for alias in (_normalize_text(item) for item in raw_aliases if isinstance(raw_aliases, list))
            if alias
        ]
        entries.append(
            {
                "name": name,
                "kind": kind,
                "latitude": round(latitude, 6),
                "longitude": round(longitude, 6),
                "locality": _normalize_text(raw_entry.get("locality")) or None,
                "admin1": _normalize_text(raw_entry.get("admin1")) or None,
                "country": _normalize_text(raw_entry.get("country")) or None,
                "countryCode": (_normalize_text(raw_entry.get("countryCode")) or None),
                "aliases": aliases[:16],
            }
        )
    with _PLACE_GAZETTEER_RUNTIME_LOCK:
        _PLACE_GAZETTEER_RUNTIME_CACHE[cache_key] = {"mtimeNs": mtime_ns, "entries": list(entries)}
    return entries


def _build_media_geolocation_place_context(
    settings: Settings,
    *,
    latitude: float,
    longitude: float,
) -> dict[str, Any] | None:
    entries = _load_media_geolocation_place_gazetteer(settings)
    if not entries:
        return None
    nearest_landmark: dict[str, Any] | None = None
    nearest_locality: dict[str, Any] | None = None
    for entry in entries:
        distance_km = _distance_km_between_points(latitude, longitude, entry.get("latitude"), entry.get("longitude"))
        if distance_km is None:
            continue
        ranked = {**entry, "distanceKm": round(distance_km, 3)}
        if entry.get("kind") == "landmark":
            if nearest_landmark is None or ranked["distanceKm"] < nearest_landmark["distanceKm"]:
                nearest_landmark = ranked
            continue
        if entry.get("kind") in {"city", "locality", "district", "region"}:
            if nearest_locality is None or ranked["distanceKm"] < nearest_locality["distanceKm"]:
                nearest_locality = ranked
    landmark_radius_km = max(0.5, float(settings.source_discovery_media_geolocation_place_landmark_radius_km))
    locality_radius_km = max(1.0, float(settings.source_discovery_media_geolocation_place_locality_radius_km))
    landmark_match = nearest_landmark if nearest_landmark and nearest_landmark["distanceKm"] <= landmark_radius_km else None
    locality_match = nearest_locality if nearest_locality and nearest_locality["distanceKm"] <= locality_radius_km else None
    if landmark_match is None and locality_match is None:
        return None
    locality_name = None
    admin1 = None
    country = None
    country_code = None
    if landmark_match is not None:
        locality_name = landmark_match.get("locality")
        admin1 = landmark_match.get("admin1")
        country = landmark_match.get("country")
        country_code = landmark_match.get("countryCode")
    if locality_match is not None:
        locality_name = locality_name or locality_match.get("name")
        admin1 = admin1 or locality_match.get("admin1")
        country = country or locality_match.get("country")
        country_code = country_code or locality_match.get("countryCode")
    label_parts: list[str] = []
    seen_parts: set[str] = set()
    for part in [
        landmark_match.get("name") if landmark_match is not None else None,
        locality_name,
        admin1,
        country,
    ]:
        normalized = _normalize_text(part)
        if not normalized:
            continue
        token = normalized.casefold()
        if token in seen_parts:
            continue
        seen_parts.add(token)
        label_parts.append(normalized)
    if not label_parts:
        return None
    agreement_labels: list[str] = []
    seen_agreement_labels: set[str] = set()
    for part in [
        landmark_match.get("name") if landmark_match is not None else None,
        locality_name,
        admin1,
        country,
        *(landmark_match.get("aliases", []) if isinstance(landmark_match, dict) else []),
        *(locality_match.get("aliases", []) if isinstance(locality_match, dict) else []),
    ]:
        normalized = _normalize_text(part)
        if not normalized:
            continue
        token = normalized.casefold()
        if token in seen_agreement_labels:
            continue
        seen_agreement_labels.add(token)
        agreement_labels.append(normalized)
    return {
        "displayLabel": ", ".join(label_parts),
        "landmark": landmark_match.get("name") if landmark_match is not None else None,
        "locality": locality_name,
        "admin1": admin1,
        "country": country,
        "countryCode": country_code,
        "nearestLandmark": landmark_match,
        "nearestLocality": locality_match,
        "agreementLabels": agreement_labels[:12],
        "distanceKm": landmark_match.get("distanceKm") if landmark_match is not None else (locality_match.get("distanceKm") if locality_match is not None else None),
        "source": "local_media_geolocation_place_gazetteer",
    }


def _distance_km_between_points(
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


def _try_geoclip_candidates(
    settings: Settings,
    *,
    artifact_path: str | None,
    max_candidates: int,
) -> tuple[list[MediaGeolocationCandidate], str | None, list[str], list[str], MediaGeolocationEngineAttempt]:
    if artifact_path is None:
        attempt = MediaGeolocationEngineAttempt(
            engine="geoclip",
            role="specialized_geocoder",
            status="rejected",
            availability_reason="GeoCLIP requires a locally stored artifact path.",
            caveats=["GeoCLIP requires a locally stored artifact path."],
        )
        return [], None, [], attempt.caveats, attempt
    if not settings.source_discovery_media_geoclip_enabled:
        attempt = MediaGeolocationEngineAttempt(
            engine="geoclip",
            role="specialized_geocoder",
            status="unavailable",
            availability_reason="GeoCLIP is disabled by configuration.",
            caveats=["GeoCLIP is disabled by configuration."],
        )
        return [], None, [], attempt.caveats, attempt
    runtime, attempt = _load_geoclip_runtime(settings)
    if runtime is None:
        return [], None, [], list(attempt.caveats), attempt
    profile_config = {
        "profile": runtime.get("performance_profile") or "full_fidelity",
        "maxImageEdge": runtime.get("max_image_edge"),
        "requestedDevice": runtime.get("requested_device") or "cpu",
        "resolvedDevice": runtime.get("resolved_device") or "cpu",
        "predictionCacheEntries": runtime.get("prediction_cache_entries") or 0,
        "experimentalAccelerationEnabled": runtime.get("experimental_acceleration_enabled") or False,
        "caveats": list(attempt.caveats),
    }
    preprocess_started = time.perf_counter()
    inference_artifact_path, preprocess_metadata, preprocess_caveats = _prepare_geoclip_inference_artifact(
        settings,
        artifact_path=artifact_path,
        profile_config=profile_config,
    )
    preprocess_ms = round((time.perf_counter() - preprocess_started) * 1000.0, 3)
    cache_key = _build_geoclip_prediction_cache_key(
        runtime,
        artifact_path=inference_artifact_path,
        max_candidates=max_candidates,
        profile_config=profile_config,
    )
    predict_ms = 0.0
    cache_hit = False
    try:
        cached_prediction = _lookup_geoclip_prediction_cache(cache_key)
        if cached_prediction is not None:
            predicted_gps = cached_prediction.get("gpsRows", [])
            predicted_probabilities = cached_prediction.get("probabilityRows", [])
            cache_hit = True
        else:
            model = runtime["model"]
            predict_started = time.perf_counter()
            predicted_gps, predicted_probabilities = model.predict(inference_artifact_path, top_k=max_candidates)
            predict_ms = round((time.perf_counter() - predict_started) * 1000.0, 3)
            gps_rows_for_cache = predicted_gps.tolist() if hasattr(predicted_gps, "tolist") else list(predicted_gps)
            probability_rows_for_cache = (
                predicted_probabilities.tolist()
                if hasattr(predicted_probabilities, "tolist")
                else list(predicted_probabilities)
            )
            _store_geoclip_prediction_cache(
                cache_key,
                {
                    "gpsRows": gps_rows_for_cache,
                    "probabilityRows": probability_rows_for_cache,
                    "createdAt": datetime.utcnow().isoformat() + "Z",
                },
                max_entries=int(profile_config.get("predictionCacheEntries") or 0),
            )
            predicted_gps = gps_rows_for_cache
            predicted_probabilities = probability_rows_for_cache
    except Exception as exc:  # pragma: no cover - optional dependency runtime variance
        message = f"GeoCLIP execution failed: {_normalize_text(str(exc)) or 'unknown error'}"
        attempt.status = "failed"
        attempt.availability_reason = message
        attempt.caveats = _dedupe_text_list([*attempt.caveats, *preprocess_caveats, message])
        attempt.metadata = {
            **attempt.metadata,
            **preprocess_metadata,
            "artifactPath": artifact_path,
            "inferenceArtifactPath": inference_artifact_path,
            "preprocessMs": preprocess_ms,
            "predictMs": predict_ms,
            "cacheHit": cache_hit,
            "performanceProfile": profile_config.get("profile"),
            "requestedDevice": profile_config.get("requestedDevice"),
            "resolvedDevice": profile_config.get("resolvedDevice"),
        }
        return [], runtime.get("model_name"), [], [message], attempt
    gps_rows = predicted_gps.tolist() if hasattr(predicted_gps, "tolist") else list(predicted_gps)
    probability_rows = predicted_probabilities.tolist() if hasattr(predicted_probabilities, "tolist") else list(predicted_probabilities)
    candidates: list[MediaGeolocationCandidate] = []
    used_place_enrichment = False
    for index, item in enumerate(gps_rows[:max_candidates]):
        if not isinstance(item, (list, tuple)) or len(item) < 2:
            continue
        latitude = _coerce_float(item[0])
        longitude = _coerce_float(item[1])
        if latitude is None or longitude is None:
            continue
        probability = probability_rows[index] if index < len(probability_rows) else None
        rounded_latitude = round(latitude, 6)
        rounded_longitude = round(longitude, 6)
        place_context = _build_media_geolocation_place_context(
            settings,
            latitude=rounded_latitude,
            longitude=rounded_longitude,
        )
        label = place_context.get("displayLabel") if isinstance(place_context, dict) else None
        if label:
            used_place_enrichment = True
        else:
            label = f"{rounded_latitude:.4f}, {rounded_longitude:.4f}"
        metadata = {"rawRetrievalScore": _coerce_float(probability)}
        basis = ["GeoCLIP image-to-GPS retrieval predicted this coordinate candidate from the image alone."]
        provenance_chain = ["geoclip_topk_retrieval"]
        candidate_caveats: list[str] = []
        if isinstance(place_context, dict):
            metadata.update(
                {
                    "placeContext": place_context,
                    "landmark": place_context.get("landmark"),
                    "locality": place_context.get("locality"),
                    "admin1": place_context.get("admin1"),
                    "country": place_context.get("country"),
                    "countryCode": place_context.get("countryCode"),
                    "agreementLabels": place_context.get("agreementLabels", []),
                }
            )
            basis.append("Human-readable place context was added from a bounded offline gazetteer around the GeoCLIP coordinate candidate.")
            provenance_chain.append("offline_place_gazetteer")
            candidate_caveats.append("The place label is an offline nearest-place enrichment around the predicted coordinates, not a direct GeoCLIP text output.")
        candidates.append(
            MediaGeolocationCandidate(
                rank=index + 1,
                candidate_kind="gps_point",
                label=label,
                latitude=rounded_latitude,
                longitude=rounded_longitude,
                confidence=_coerce_float(probability),
                engine="geoclip",
                basis=basis,
                provenance_chain=provenance_chain,
                metadata=metadata,
                caveats=candidate_caveats,
            )
        )
    reasoning = ["GeoCLIP produced image-to-GPS candidate coordinates for fusion with deterministic clues."] if candidates else []
    if used_place_enrichment:
        reasoning.append("GeoCLIP coordinate candidates were enriched with bounded offline place labels so review packets show nearby locality and landmark context.")
    if preprocess_metadata.get("usedPreprocessedArtifact"):
        reasoning.append("GeoCLIP inference reused a profile-controlled preprocessed artifact so repeated local runs can trade explicit image-size limits for lower CPU cost.")
    if cache_hit:
        reasoning.append("GeoCLIP reused a cached prediction for the exact artifact-and-profile fingerprint instead of rerunning image-to-GPS retrieval.")
    caveats = [
        "GeoCLIP output is retrieval-based and should be fused with textual, timestamp, and provenance clues before operator use."
    ] if candidates else []
    caveats = _dedupe_text_list([*caveats, *preprocess_caveats])
    attempt.status = "completed"
    attempt.produced_candidate_count = len(candidates)
    attempt.model_name = runtime.get("model_name")
    attempt.metadata = {
        **attempt.metadata,
        "artifactPath": artifact_path,
        "inferenceArtifactPath": inference_artifact_path,
        "candidateCount": len(candidates),
        "usedPlaceEnrichment": used_place_enrichment,
        "preprocessMs": preprocess_ms,
        "predictMs": predict_ms,
        "cacheHit": cache_hit,
        "performanceProfile": profile_config.get("profile"),
        "requestedDevice": profile_config.get("requestedDevice"),
        "resolvedDevice": profile_config.get("resolvedDevice"),
        **preprocess_metadata,
    }
    attempt.caveats = _dedupe_text_list(attempt.caveats + caveats)
    return candidates, runtime.get("model_name"), reasoning, caveats, attempt


def _try_streetclip_candidates(
    settings: Settings,
    *,
    artifact_path: str | None,
    candidate_labels: list[str],
    max_candidates: int,
) -> tuple[list[MediaGeolocationCandidate], str | None, list[str], list[str], MediaGeolocationEngineAttempt]:
    labels = [_normalize_text(item) for item in candidate_labels if _normalize_text(item)]
    if artifact_path is None:
        attempt = MediaGeolocationEngineAttempt(
            engine="streetclip",
            role="street_scene_reranker",
            status="rejected",
            availability_reason="StreetCLIP requires a locally stored artifact path.",
            caveats=["StreetCLIP requires a locally stored artifact path."],
        )
        return [], None, [], attempt.caveats, attempt
    if not settings.source_discovery_media_streetclip_enabled:
        attempt = MediaGeolocationEngineAttempt(
            engine="streetclip",
            role="street_scene_reranker",
            status="unavailable",
            availability_reason="StreetCLIP is disabled by configuration.",
            caveats=["StreetCLIP is disabled by configuration."],
        )
        return [], None, [], attempt.caveats, attempt
    if not labels:
        attempt = MediaGeolocationEngineAttempt(
            engine="streetclip",
            role="street_scene_reranker",
            status="unavailable",
            availability_reason="StreetCLIP needs candidate labels to rank.",
            caveats=["StreetCLIP needs candidate labels to rank."],
        )
        return [], settings.source_discovery_media_streetclip_model_id, [], attempt.caveats, attempt
    runtime, attempt = _load_streetclip_runtime(settings)
    if runtime is None:
        return [], settings.source_discovery_media_streetclip_model_id, [], list(attempt.caveats), attempt
    try:
        processor = runtime["processor"]
        model = runtime["model"]
        with Image.open(artifact_path) as image:
            rgb = ImageOps.exif_transpose(image).convert("RGB") if ImageOps is not None else image.convert("RGB")
            inputs = processor(text=labels, images=rgb, return_tensors="pt", padding=True)
        with torch.no_grad():
            outputs = model(**inputs)
        logits = getattr(outputs, "logits_per_image", None)
        if logits is None:
            message = "StreetCLIP did not return image/text similarity logits in the expected format."
            attempt.status = "failed"
            attempt.availability_reason = message
            attempt.caveats = _dedupe_text_list(attempt.caveats + [message])
            return [], runtime.get("model_name"), [], [message], attempt
        probabilities = logits.softmax(dim=1).tolist()[0]
    except Exception as exc:  # pragma: no cover - optional dependency runtime variance
        message = f"StreetCLIP execution failed: {_normalize_text(str(exc)) or 'unknown error'}"
        attempt.status = "failed"
        attempt.availability_reason = message
        attempt.caveats = _dedupe_text_list(attempt.caveats + [message])
        return [], runtime.get("model_name"), [], [message], attempt
    ranked = sorted(zip(labels, probabilities), key=lambda item: item[1], reverse=True)[:max_candidates]
    candidates = [
        MediaGeolocationCandidate(
            rank=index + 1,
            candidate_kind="country_region",
            label=label,
            latitude=None,
            longitude=None,
            confidence=round(float(probability), 6),
            engine="streetclip",
            basis=["StreetCLIP ranked this supplied place label from street-level visual similarity."],
            provenance_chain=["streetclip_label_rerank"],
            metadata={"rawRetrievalScore": round(float(probability), 6)},
        )
        for index, (label, probability) in enumerate(ranked)
    ]
    reasoning = ["StreetCLIP ranked supplied candidate labels using street-scene visual similarity."] if candidates else []
    caveats = [
        "StreetCLIP is most reliable on road, urban, and rural street-level imagery and should not be treated as a general exact geocoder.",
        "StreetCLIP coverage and licensing caveats should stay attached to every run.",
    ] if candidates else []
    attempt.status = "completed"
    attempt.produced_candidate_count = len(candidates)
    attempt.model_name = runtime.get("model_name")
    attempt.metadata = {
        **attempt.metadata,
        "candidateLabelCount": len(labels),
    }
    attempt.caveats = _dedupe_text_list(attempt.caveats + caveats)
    return candidates, runtime.get("model_name"), reasoning, caveats, attempt


def _try_local_geolocation_analyst(
    settings: Settings,
    *,
    artifact_path: str | None,
    artifact_metadata: dict[str, Any],
    ocr_text: str | None,
    captions: list[str],
    analyst_adapter: str,
    analyst_model: str | None,
    run_local: bool,
) -> tuple[MediaGeolocationAnalystResult | None, MediaGeolocationEngineAttempt | None]:
    if not run_local or artifact_path is None:
        return None, None
    resolved = analyst_adapter.strip().lower() or "auto"
    if resolved in {"none", "deterministic"}:
        return None, None
    if resolved == "auto":
        if settings.source_discovery_media_openai_compat_enabled and (
            settings.source_discovery_media_qwen_vl_local_model
            or settings.source_discovery_media_internvl_local_model
            or settings.source_discovery_media_llava_local_model
            or settings.source_discovery_media_openai_compat_model
        ):
            resolved = "qwen_vl_local" if settings.source_discovery_media_qwen_vl_local_model else "openai_compat_local"
        elif settings.source_discovery_media_ollama_enabled and settings.source_discovery_media_ollama_model:
            resolved = "ollama"
        else:
            attempt = MediaGeolocationEngineAttempt(
                engine="local_vlm_auto",
                role="clue_analyst",
                status="unavailable",
                availability_reason="No local analyst adapter was configured.",
                caveats=["No local analyst adapter was configured."],
            )
            return None, attempt
    if resolved == "ollama":
        result = _try_ollama_geolocation_analyst(
            settings,
            artifact_path=artifact_path,
            artifact_metadata=artifact_metadata,
            ocr_text=ocr_text,
            captions=captions,
            model=analyst_model,
        )
        attempt = MediaGeolocationEngineAttempt(
            engine=resolved,
            role="clue_analyst",
            status="completed" if result is not None else "unavailable",
            model_name=result.model_name if result is not None else (analyst_model or settings.source_discovery_media_ollama_model),
            warm_state="request_scoped",
            availability_reason=None if result is not None else "Ollama local analyst was unavailable under current localhost-only constraints.",
            produced_candidate_count=len(result.candidates) if result is not None else 0,
            metadata=result.metadata if result is not None else {},
            caveats=list(result.caveats) if result is not None else ["Ollama local analyst was unavailable under current localhost-only constraints."],
        )
        return result, attempt
    if resolved in {"openai_compat_local", "qwen_vl_local", "internvl_local", "llava_local"}:
        result = _try_openai_compat_local_geolocation_analyst(
            settings,
            artifact_path=artifact_path,
            artifact_metadata=artifact_metadata,
            ocr_text=ocr_text,
            captions=captions,
            adapter=resolved,
            model=analyst_model,
        )
        resolved_model = _resolve_openai_compat_local_geolocation_model(settings, adapter=resolved, override=analyst_model)
        attempt = MediaGeolocationEngineAttempt(
            engine=resolved,
            role="clue_analyst",
            status="completed" if result is not None else "unavailable",
            model_name=result.model_name if result is not None else resolved_model,
            warm_state="request_scoped",
            availability_reason=None if result is not None else "Local OpenAI-compatible analyst was unavailable under current localhost-only constraints.",
            produced_candidate_count=len(result.candidates) if result is not None else 0,
            metadata=result.metadata if result is not None else {"requestedModel": resolved_model},
            caveats=list(result.caveats) if result is not None else ["Local OpenAI-compatible analyst was unavailable under current localhost-only constraints."],
        )
        return result, attempt
    attempt = MediaGeolocationEngineAttempt(
        engine=resolved,
        role="clue_analyst",
        status="rejected",
        availability_reason="Unsupported local analyst adapter.",
        caveats=["Unsupported local geolocation analyst adapter."],
    )
    return None, attempt


def _try_ollama_geolocation_analyst(
    settings: Settings,
    *,
    artifact_path: str,
    artifact_metadata: dict[str, Any],
    ocr_text: str | None,
    captions: list[str],
    model: str | None,
) -> MediaGeolocationAnalystResult | None:
    resolved_model = (model or settings.source_discovery_media_ollama_model or "").strip()
    if not settings.source_discovery_media_ollama_enabled or not resolved_model:
        return None
    base_url = (settings.ollama_base_url or "").strip()
    if not re.match(r"^https?://(?:127\.0\.0\.1|localhost|\[::1\])(?::\d+)?/?$", base_url):
        return None
    try:
        encoded = base64.b64encode(Path(artifact_path).read_bytes()).decode("utf-8")
    except OSError:
        return None
    request_body = json.dumps(
        {
            "model": resolved_model,
            "format": "json",
            "stream": False,
            "images": [encoded],
            "prompt": _build_geolocation_prompt(artifact_metadata=artifact_metadata, ocr_text=ocr_text, captions=captions),
        }
    ).encode("utf-8")
    request = Request(
        base_url.rstrip("/") + "/api/generate",
        method="POST",
        headers={"Content-Type": "application/json"},
        data=request_body,
    )
    try:
        with urlopen(request, timeout=min(45, settings.wave_llm_http_timeout_seconds)) as response:
            raw = response.read(settings.wave_llm_max_output_chars + 4096).decode("utf-8", errors="replace")
        payload = json.loads(raw)
        response_text = str(payload.get("response") or "").strip()
        parsed = json.loads(response_text)
    except Exception:
        return None
    return _parse_geolocation_analyst_payload(
        parsed,
        adapter="ollama",
        model_name=resolved_model,
        provider_metadata={"provider": "ollama", "model": resolved_model},
        extra_caveats=["Ollama geolocation clue analysis is a local model aid and remains review-only."],
    )


def _try_openai_compat_local_geolocation_analyst(
    settings: Settings,
    *,
    artifact_path: str,
    artifact_metadata: dict[str, Any],
    ocr_text: str | None,
    captions: list[str],
    adapter: str,
    model: str | None,
) -> MediaGeolocationAnalystResult | None:
    if not settings.source_discovery_media_openai_compat_enabled:
        return None
    resolved_model = _resolve_openai_compat_local_geolocation_model(settings, adapter=adapter, override=model)
    if not resolved_model:
        return None
    base_url = (settings.source_discovery_media_openai_compat_base_url or "").strip()
    if not re.match(r"^https?://(?:127\.0\.0\.1|localhost|\[::1\])(?::\d+)?(?:/.*)?$", base_url):
        return None
    try:
        encoded = base64.b64encode(Path(artifact_path).read_bytes()).decode("utf-8")
    except OSError:
        return None
    request_body = json.dumps(
        {
            "model": resolved_model,
            "response_format": {"type": "json_object"},
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": _build_geolocation_prompt(artifact_metadata=artifact_metadata, ocr_text=ocr_text, captions=captions)},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{encoded}"}},
                    ],
                }
            ],
        }
    ).encode("utf-8")
    request = Request(
        base_url.rstrip("/") + "/chat/completions",
        method="POST",
        headers={"Content-Type": "application/json"},
        data=request_body,
    )
    try:
        with urlopen(request, timeout=min(45, settings.wave_llm_http_timeout_seconds)) as response:
            raw = response.read(settings.wave_llm_max_output_chars + 4096).decode("utf-8", errors="replace")
        payload = json.loads(raw)
        choices = payload.get("choices") if isinstance(payload, dict) else None
        if not isinstance(choices, list) or not choices:
            return None
        message = choices[0].get("message", {})
        content = message.get("content")
        if isinstance(content, list):
            response_text = _normalize_text(" ".join(str(item.get("text", "")) for item in content if isinstance(item, dict)))
        else:
            response_text = _normalize_text(str(content or ""))
        parsed = json.loads(response_text)
    except Exception:
        return None
    return _parse_geolocation_analyst_payload(
        parsed,
        adapter=adapter,
        model_name=resolved_model,
        provider_metadata={"provider": "openai_compat_local", "model": resolved_model},
        extra_caveats=["OpenAI-compatible local geolocation clue analysis remains review-only and localhost-only."],
    )


def _parse_geolocation_analyst_payload(
    payload: dict[str, Any],
    *,
    adapter: str,
    model_name: str | None,
    provider_metadata: dict[str, Any],
    extra_caveats: list[str],
) -> MediaGeolocationAnalystResult:
    candidate_items = payload.get("candidate_locations", [])
    candidates = [
        _coerce_geolocation_candidate(item, default_engine=adapter, rank=index + 1)
        for index, item in enumerate(candidate_items)
        if isinstance(item, dict)
    ]
    return MediaGeolocationAnalystResult(
        adapter=adapter,
        model_name=model_name,
        summary=_normalize_optional(payload.get("summary")) or _normalize_optional(payload.get("place_hypothesis")),
        reasoning_lines=[str(item) for item in payload.get("reasoning_lines", []) if str(item).strip()],
        candidates=candidates,
        negative_evidence=[str(item) for item in payload.get("negative_evidence", []) if str(item).strip()],
        metadata={
            **provider_metadata,
            "placeBasis": _normalize_optional(payload.get("place_basis")),
            "geolocationBasis": _normalize_optional(payload.get("geolocation_basis")),
            "timeOfDayBasis": _normalize_optional(payload.get("time_of_day_basis")),
            "seasonBasis": _normalize_optional(payload.get("season_basis")),
            "uncertaintyCeiling": _coerce_float(payload.get("uncertainty_ceiling")),
        },
        caveats=extra_caveats + [
            "Local VLM geolocation clues can help ranking and explanation, but they do not become final location truth without review.",
            "No people recognition or identity analysis is allowed in this workflow.",
        ],
    )


def _resolve_openai_compat_local_geolocation_model(settings: Settings, *, adapter: str, override: str | None) -> str | None:
    if override and override.strip():
        return override.strip()
    if adapter == "qwen_vl_local":
        return _normalize_optional(settings.source_discovery_media_qwen_vl_local_model) or _normalize_optional(settings.source_discovery_media_openai_compat_model)
    if adapter == "internvl_local":
        return _normalize_optional(settings.source_discovery_media_internvl_local_model) or _normalize_optional(settings.source_discovery_media_openai_compat_model)
    if adapter == "llava_local":
        return _normalize_optional(settings.source_discovery_media_llava_local_model) or _normalize_optional(settings.source_discovery_media_openai_compat_model)
    return _normalize_optional(settings.source_discovery_media_openai_compat_model)


def _build_geolocation_prompt(
    *,
    artifact_metadata: dict[str, Any],
    ocr_text: str | None,
    captions: list[str],
) -> str:
    metadata_text = json.dumps(artifact_metadata, ensure_ascii=True)
    return (
        "You are a local-only media geolocation clue analyst for 11Writer.\n"
        "Analyze places, landscape, architecture, visible text, road clues, climate clues, and terrain clues only.\n"
        "Do not identify people. Do not guess identities, guilt, or intent.\n"
        "Return strict JSON with keys: summary, candidate_locations, place_basis, geolocation_basis, time_of_day_basis, "
        "season_basis, uncertainty_ceiling, negative_evidence, reasoning_lines.\n"
        "candidate_locations must be a list of objects with keys: label, latitude, longitude, confidence, basis, candidate_kind.\n"
        "negative_evidence must be a short list of reasons the scene may not fit certain regions or labels.\n"
        "Use null for unknown latitude/longitude. Keep uncertainty explicit and conservative.\n"
        f"Artifact metadata: {metadata_text}\n"
        f"OCR text: {_normalize_text(ocr_text or '')}\n"
        f"Captions: {_normalize_text(' '.join(captions))}"
    )


def _coerce_geolocation_candidate(item: dict[str, Any], *, default_engine: str, rank: int) -> MediaGeolocationCandidate:
    candidate_kind = _normalize_optional(item.get("candidate_kind")) or "model_hypothesis"
    return MediaGeolocationCandidate(
        rank=rank,
        candidate_kind=candidate_kind,
        label=_normalize_optional(item.get("label")),
        latitude=_coerce_float(item.get("latitude")),
        longitude=_coerce_float(item.get("longitude")),
        confidence=_coerce_float(item.get("confidence")),
        confidence_score=_coerce_float(item.get("confidence_score")) or _coerce_float(item.get("confidence")),
        confidence_ceiling=_coerce_float(item.get("confidence_ceiling")),
        engine=_normalize_optional(item.get("engine")) or default_engine,
        basis=[str(entry) for entry in item.get("basis", []) if str(entry).strip()] if isinstance(item.get("basis"), list) else [],
        supporting_evidence=[str(entry) for entry in item.get("supporting_evidence", []) if str(entry).strip()] if isinstance(item.get("supporting_evidence"), list) else [],
        contradicting_evidence=[str(entry) for entry in item.get("contradicting_evidence", []) if str(entry).strip()] if isinstance(item.get("contradicting_evidence"), list) else [],
        engine_agreement=item.get("engine_agreement", {}) if isinstance(item.get("engine_agreement"), dict) else {},
        provenance_chain=[str(entry) for entry in item.get("provenance_chain", []) if str(entry).strip()] if isinstance(item.get("provenance_chain"), list) else [],
        inherited=bool(item.get("inherited", False)),
        inherited_from_artifact_ids=[
            str(entry) for entry in item.get("inherited_from_artifact_ids", []) if str(entry).strip()
        ] if isinstance(item.get("inherited_from_artifact_ids"), list) else [],
        metadata=item.get("metadata", {}) if isinstance(item.get("metadata"), dict) else {},
        caveats=[str(entry) for entry in item.get("caveats", []) if str(entry).strip()] if isinstance(item.get("caveats"), list) else [],
    )


def _build_candidate_label_bank(
    *,
    supplied_labels: list[str],
    clue_packet: MediaGeolocationCluePacket,
    inherited_context: dict[str, Any] | None,
) -> list[str]:
    labels: list[str] = []
    for item in supplied_labels:
        normalized = _normalize_text(item)
        if normalized and normalized not in labels:
            labels.append(normalized)
    for clue in clue_packet.place_text_clues:
        label = _normalize_text(clue.text)
        if label and label not in labels:
            labels.append(label)
    if inherited_context and isinstance(inherited_context.get("candidateLabels"), list):
        for item in inherited_context.get("candidateLabels", []):
            label = _normalize_text(str(item))
            if label and label not in labels:
                labels.append(label)
    return labels[:24]


def _fuse_geolocation_candidates(
    candidates: list[MediaGeolocationCandidate],
    *,
    clue_packet: MediaGeolocationCluePacket,
    engine_attempts: list[MediaGeolocationEngineAttempt],
    observed_latitude: float | None,
    observed_longitude: float | None,
    inherited_context: dict[str, Any] | None,
    analyst_result: MediaGeolocationAnalystResult | None,
    max_candidates: int,
) -> list[MediaGeolocationCandidate]:
    deduped: dict[str, MediaGeolocationCandidate] = {}
    for item in candidates:
        key = _geolocation_candidate_key(item)
        existing = deduped.get(key)
        if existing is None or (item.confidence or 0.0) > (existing.confidence or 0.0):
            deduped[key] = item
            continue
        existing.basis = _dedupe_text_list(existing.basis + item.basis)
        existing.caveats = _dedupe_text_list(existing.caveats + item.caveats)
        existing.supporting_evidence = _dedupe_text_list(existing.supporting_evidence + item.supporting_evidence)
        existing.contradicting_evidence = _dedupe_text_list(existing.contradicting_evidence + item.contradicting_evidence)
        existing.provenance_chain = _dedupe_text_list(existing.provenance_chain + item.provenance_chain)
        existing.inherited = existing.inherited or item.inherited
        existing.inherited_from_artifact_ids = sorted(set(existing.inherited_from_artifact_ids + item.inherited_from_artifact_ids))
    ranked_items = list(deduped.values())
    for item in ranked_items:
        _score_geolocation_candidate(
            item,
            clue_packet=clue_packet,
            all_candidates=ranked_items,
            engine_attempts=engine_attempts,
            observed_latitude=observed_latitude,
            observed_longitude=observed_longitude,
            analyst_result=analyst_result,
            inherited_context=inherited_context,
        )
    ranked = sorted(
        ranked_items,
        key=lambda candidate: (
            _geolocation_candidate_sort_priority(candidate),
            -_effective_geolocation_ranking_score(candidate),
            candidate.label or "",
        ),
    )[:max_candidates]
    for index, item in enumerate(ranked):
        item.rank = index + 1
    return ranked


def _score_geolocation_candidate(
    candidate: MediaGeolocationCandidate,
    *,
    clue_packet: MediaGeolocationCluePacket,
    all_candidates: list[MediaGeolocationCandidate],
    engine_attempts: list[MediaGeolocationEngineAttempt],
    observed_latitude: float | None,
    observed_longitude: float | None,
    analyst_result: MediaGeolocationAnalystResult | None,
    inherited_context: dict[str, Any] | None,
) -> None:
    base = candidate.confidence if candidate.confidence is not None else 0.35
    supporting = list(candidate.basis)
    contradicting: list[str] = []
    provenance = list(candidate.provenance_chain)
    evidence_families: list[str] = []
    direct_coordinate_support = False
    if candidate.engine == "deterministic":
        evidence_families.append("deterministic")
        base += 0.08
    if candidate.engine == "geoclip":
        evidence_families.append("geoclip")
        base = max(base + 0.05, 0.72 if candidate.latitude is not None and candidate.longitude is not None else 0.48)
        supporting.append("GeoCLIP contributed direct coordinate retrieval, which outranks coarse place-label similarity in fusion.")
    if candidate.engine == "streetclip":
        evidence_families.append("streetclip")
        base += 0.02
        if candidate.latitude is None or candidate.longitude is None:
            base = min(base, 0.54)
            supporting.append("StreetCLIP contributed coarse place-label ranking rather than direct coordinates.")
    if candidate.engine in {"ollama", "openai_compat_local", "qwen_vl_local", "internvl_local", "llava_local"}:
        evidence_families.append("local_vlm")
    if candidate.latitude is not None and candidate.longitude is not None:
        evidence_families.append("gps_point")
    else:
        evidence_families.append("coarse_label")
    if observed_latitude is not None and observed_longitude is not None and candidate.latitude is not None and candidate.longitude is not None:
        if abs(candidate.latitude - observed_latitude) < 0.001 and abs(candidate.longitude - observed_longitude) < 0.001:
            base = max(base, 0.99)
            direct_coordinate_support = True
            supporting.append("Observed media coordinates matched this candidate directly.")
            provenance.append("observed_metadata")
    for clue in clue_packet.coordinate_clues:
        if candidate.latitude is not None and candidate.longitude is not None and clue.latitude is not None and clue.longitude is not None:
            if abs(candidate.latitude - clue.latitude) < 0.02 and abs(candidate.longitude - clue.longitude) < 0.02:
                supporting.append(f"Coordinate clue supported this candidate: {clue.text}.")
                if clue.clue_type == "observed_coordinates":
                    base = max(base, 0.99)
                    direct_coordinate_support = True
                elif clue.inherited:
                    base = max(base, 0.52)
                else:
                    base = max(base, 0.84)
        elif candidate.label and clue.normalized_value and clue.normalized_value in candidate.label.casefold():
            supporting.append(f"Textual coordinate clue was attached to label context: {clue.text}.")
    for clue in clue_packet.place_text_clues:
        if candidate.label and clue.text and clue.text.casefold() in candidate.label.casefold():
            supporting.append(f"Place-text clue matched this candidate: {clue.text}.")
            base += 0.04 if not clue.inherited else 0.01
    if analyst_result is not None:
        for negative in analyst_result.negative_evidence:
            if candidate.label and candidate.label.casefold() in negative.casefold():
                contradicting.append(negative)
                base -= 0.06
    other_supporting_engines = {
        other.engine
        for other in all_candidates
        if other is not candidate and _geolocation_candidates_agree(candidate, other)
    }
    conflicting_engines = {
        other.engine
        for other in all_candidates
        if other is not candidate and _geolocation_candidates_conflict(candidate, other)
    }
    if other_supporting_engines:
        supporting.append(f"Other engines agreed with this hypothesis: {', '.join(sorted(other_supporting_engines))}.")
        base += min(0.08, 0.02 * len(other_supporting_engines))
    if conflicting_engines:
        contradicting.append(f"Conflicting candidates were also produced by: {', '.join(sorted(conflicting_engines))}.")
        base -= min(0.12, 0.03 * len(conflicting_engines))
    ceiling = 0.88
    if candidate.engine == "geoclip":
        ceiling = 0.82
    if candidate.engine == "streetclip":
        ceiling = 0.62
    if candidate.engine in {"ollama", "openai_compat_local", "qwen_vl_local", "internvl_local", "llava_local"}:
        ceiling = 0.58
    if direct_coordinate_support:
        ceiling = max(ceiling, 0.99)
    if candidate.inherited:
        ceiling = min(ceiling, 0.68)
        base -= 0.06
        supporting.append("Some support for this candidate came from duplicate-cluster or sequence lineage rather than direct observation.")
    if conflicting_engines:
        ceiling -= 0.08
    if inherited_context and inherited_context.get("relationshipKinds"):
        provenance.extend(str(item) for item in inherited_context.get("relationshipKinds", []) if str(item).strip())
    candidate.confidence_score = round(max(0.0, min(0.99, min(base, ceiling))), 4)
    candidate.confidence_ceiling = round(max(0.0, min(0.99, ceiling)), 4)
    candidate.confidence = candidate.confidence_score
    candidate.supporting_evidence = _dedupe_text_list(supporting)
    candidate.contradicting_evidence = _dedupe_text_list(contradicting)
    candidate.provenance_chain = _dedupe_text_list(provenance + evidence_families)
    candidate.engine_agreement = {
        "supportingEngines": sorted(other_supporting_engines),
        "conflictingEngines": sorted(conflicting_engines),
        "attemptedEngines": sorted({attempt.engine for attempt in engine_attempts}),
    }


def _geolocation_candidate_sort_priority(candidate: MediaGeolocationCandidate) -> int:
    if candidate.latitude is not None and candidate.longitude is not None:
        if candidate.engine == "deterministic":
            return 0
        if candidate.engine == "geoclip":
            return 1
        return 2
    if candidate.engine == "streetclip":
        return 4
    if candidate.engine in {"ollama", "openai_compat_local", "qwen_vl_local", "internvl_local", "llava_local"}:
        return 5
    return 3


def _effective_geolocation_ranking_score(candidate: MediaGeolocationCandidate) -> float:
    raw_score = candidate.confidence_score if candidate.confidence_score is not None else candidate.confidence or 0.0
    if candidate.confidence_ceiling is None:
        return raw_score
    return min(raw_score, candidate.confidence_ceiling)


def _candidate_geolocation_agreement_terms(candidate: MediaGeolocationCandidate) -> set[str]:
    terms: set[str] = set()
    if candidate.label:
        normalized_label = _normalize_text(candidate.label)
        if normalized_label:
            terms.add(normalized_label.casefold())
            for part in normalized_label.split(","):
                normalized_part = _normalize_text(part)
                if normalized_part:
                    terms.add(normalized_part.casefold())
    metadata = candidate.metadata if isinstance(candidate.metadata, dict) else {}
    for key in ("landmark", "locality", "admin1", "country"):
        normalized = _normalize_text(metadata.get(key))
        if normalized:
            terms.add(normalized.casefold())
    agreement_labels = metadata.get("agreementLabels")
    if isinstance(agreement_labels, list):
        for item in agreement_labels:
            normalized = _normalize_text(item)
            if normalized:
                terms.add(normalized.casefold())
    return terms


def _geolocation_candidates_agree(left: MediaGeolocationCandidate, right: MediaGeolocationCandidate) -> bool:
    if left.latitude is not None and left.longitude is not None and right.latitude is not None and right.longitude is not None:
        return abs(left.latitude - right.latitude) < 1.0 and abs(left.longitude - right.longitude) < 1.0
    left_terms = _candidate_geolocation_agreement_terms(left)
    right_terms = _candidate_geolocation_agreement_terms(right)
    if left_terms and right_terms and left_terms.intersection(right_terms):
        return True
    return False


def _geolocation_candidates_conflict(left: MediaGeolocationCandidate, right: MediaGeolocationCandidate) -> bool:
    if left.latitude is not None and left.longitude is not None and right.latitude is not None and right.longitude is not None:
        return abs(left.latitude - right.latitude) > 5.0 or abs(left.longitude - right.longitude) > 5.0
    left_terms = _candidate_geolocation_agreement_terms(left)
    right_terms = _candidate_geolocation_agreement_terms(right)
    if left_terms and right_terms and left_terms.intersection(right_terms):
        return False
    if left.label and right.label:
        return left.label.casefold() != right.label.casefold()
    return False


def _summarize_engine_agreement(
    candidates: list[MediaGeolocationCandidate],
    engine_attempts: list[MediaGeolocationEngineAttempt],
) -> dict[str, Any]:
    return {
        "attemptedEngines": sorted({attempt.engine for attempt in engine_attempts}),
        "completedEngines": sorted({attempt.engine for attempt in engine_attempts if attempt.status == "completed"}),
        "availableEngines": sorted({attempt.engine for attempt in engine_attempts if attempt.status in {"available", "completed"}}),
        "candidateEngines": sorted({candidate.engine for candidate in candidates}),
        "hasConflict": any(candidate.contradicting_evidence for candidate in candidates),
    }


def _collect_inherited_artifact_ids(
    *,
    clue_packet: MediaGeolocationCluePacket,
    candidates: list[MediaGeolocationCandidate],
) -> list[str]:
    artifact_ids = {
        clue.inherited_from_artifact_id
        for clue in (
            clue_packet.coordinate_clues
            + clue_packet.place_text_clues
            + clue_packet.script_language_clues
            + clue_packet.environment_clues
            + clue_packet.time_clues
        )
        if clue.inherited_from_artifact_id
    }
    for candidate in candidates:
        artifact_ids.update(candidate.inherited_from_artifact_ids)
    return sorted(artifact_ids)


def _geolocation_candidate_key(candidate: MediaGeolocationCandidate) -> str:
    if candidate.latitude is not None and candidate.longitude is not None:
        return f"gps:{round(candidate.latitude, 3)}:{round(candidate.longitude, 3)}:{candidate.candidate_kind}"
    return f"label:{(candidate.label or '').casefold()}:{candidate.candidate_kind}"


def _build_geolocation_summary(
    top_candidate: MediaGeolocationCandidate | None,
    analyst_result: MediaGeolocationAnalystResult | None,
    deterministic_reasoning: list[str],
) -> str | None:
    if top_candidate is not None:
        top_confidence = top_candidate.confidence_score if top_candidate.confidence_score is not None else (top_candidate.confidence or 0.0)
        if top_candidate.latitude is not None and top_candidate.longitude is not None and top_candidate.label:
            return (
                f"Top media geolocation candidate is '{top_candidate.label}'"
                f" at {top_candidate.latitude:.4f}, {top_candidate.longitude:.4f}"
                f" via {top_candidate.engine} with confidence {top_confidence:.2f}."
            )
        if top_candidate.latitude is not None and top_candidate.longitude is not None:
            return (
                f"Top media geolocation candidate is {top_candidate.latitude:.4f}, {top_candidate.longitude:.4f}"
                f" via {top_candidate.engine} with confidence {top_confidence:.2f}."
            )
        if top_candidate.label:
            return (
                f"Top media geolocation candidate is '{top_candidate.label}'"
                f" via {top_candidate.engine} with confidence {top_confidence:.2f}."
            )
    if analyst_result is not None and analyst_result.summary:
        return analyst_result.summary
    if deterministic_reasoning:
        return deterministic_reasoning[0]
    return None


def _extract_coordinate_pairs(text: str) -> list[tuple[float, float]]:
    pairs: list[tuple[float, float]] = []
    if not text:
        return pairs
    for match in re.finditer(r"(-?\d{1,2}\.\d{2,8})\s*[,/ ]\s*(-?\d{1,3}\.\d{2,8})", text):
        latitude = _coerce_float(match.group(1))
        longitude = _coerce_float(match.group(2))
        if latitude is None or longitude is None:
            continue
        if -90.0 <= latitude <= 90.0 and -180.0 <= longitude <= 180.0:
            pair = (round(latitude, 6), round(longitude, 6))
            if pair not in pairs:
                pairs.append(pair)
    return pairs


def _deterministic_interpretation(
    *,
    artifact_metadata: dict[str, Any],
    observed_latitude: float | None,
    observed_longitude: float | None,
    exif_timestamp: str | None,
    ocr_text: str | None,
    captions: list[str],
) -> MediaInterpretationResult:
    labels: list[str] = []
    reasoning: list[str] = []
    caveats: list[str] = [
        "Deterministic scene interpretation uses bounded metadata and heuristics, not a full visual foundation model.",
        "No people recognition or identity analysis is performed in this workflow.",
    ]
    place_basis: str | None = None
    time_of_day_basis: str | None = None
    season_basis: str | None = None
    geolocation_basis: str | None = None
    seasonal = artifact_metadata.get("seasonalSignals") if isinstance(artifact_metadata.get("seasonalSignals"), dict) else {}
    daylight = artifact_metadata.get("daylightSignals") if isinstance(artifact_metadata.get("daylightSignals"), dict) else {}
    channel_means = artifact_metadata.get("channelMeans") if isinstance(artifact_metadata.get("channelMeans"), dict) else {}
    brightness = _coerce_float(daylight.get("brightness"))
    snow_ratio = _coerce_float(seasonal.get("snowRatio")) or 0.0
    green_ratio = _coerce_float(seasonal.get("greenRatio")) or 0.0
    warm_ratio = _coerce_float(seasonal.get("warmRatio")) or 0.0
    blue_ratio = _coerce_float(seasonal.get("blueRatio")) or 0.0
    time_of_day_guess: str | None = None
    time_of_day_confidence: float | None = None
    if brightness is not None:
        if brightness < 0.18:
            time_of_day_guess = "night"
            time_of_day_confidence = 0.78
            reasoning.append("Low measured brightness suggests a night or very dark scene.")
            labels.append("low-light")
        elif brightness < 0.38:
            time_of_day_guess = "twilight_or_overcast"
            time_of_day_confidence = 0.56
            reasoning.append("Moderate brightness suggests twilight, heavy shade, or overcast conditions.")
        else:
            time_of_day_guess = "daylight"
            time_of_day_confidence = 0.72
            reasoning.append("Higher measured brightness suggests daylight conditions.")
        time_of_day_basis = "bounded_visual_brightness"
        if warm_ratio > 0.22 and brightness < 0.65:
            reasoning.append("Warm highlight balance may indicate golden-hour light, but that is not conclusive.")
    season_guess: str | None = None
    season_confidence: float | None = None
    if observed_latitude is not None and exif_timestamp:
        parsed_month = _month_from_timestamp(exif_timestamp)
        if parsed_month is not None:
            season_guess = _season_from_month(parsed_month, latitude=observed_latitude)
            season_confidence = 0.86
            reasoning.append("Season guess used EXIF timestamp plus hemisphere-aware latitude.")
            season_basis = "exif_timestamp_plus_latitude"
    if season_guess is None:
        if snow_ratio >= 0.16:
            season_guess = "winter_like"
            season_confidence = 0.58
            labels.append("snow_or_ice")
            reasoning.append("Large bright low-saturation pixel areas suggest snow, ice, or pale concrete.")
            season_basis = "bounded_pixel_heuristics"
        elif green_ratio >= 0.24:
            season_guess = "growing_season_like"
            season_confidence = 0.46
            labels.append("vegetated")
            reasoning.append("Green-dominant pixels suggest vegetation or a growing-season scene.")
            season_basis = "bounded_pixel_heuristics"
        elif warm_ratio >= 0.26:
            season_guess = "autumn_or_dry_season_like"
            season_confidence = 0.38
            reasoning.append("Warm foliage or dry-surface colors suggest autumn-like or dry-season-like conditions.")
            season_basis = "bounded_pixel_heuristics"
    if blue_ratio >= 0.28:
        labels.append("water_or_sky_dominant")
        reasoning.append("Blue-dominant image regions suggest sky, water, or both.")
    width = _coerce_int(artifact_metadata.get("width"))
    height = _coerce_int(artifact_metadata.get("height"))
    if width and height:
        labels.append("landscape_frame" if width >= height else "portrait_frame")
    text_for_clues = _normalize_text(" ".join(part for part in [ocr_text or "", " ".join(captions)] if part))
    place_hypothesis, place_confidence, extra_labels, extra_reasoning = _keyword_place_clues(text_for_clues)
    labels.extend(extra_labels)
    reasoning.extend(extra_reasoning)
    if place_hypothesis:
        place_basis = "ocr_or_caption_keyword_clues"
    geolocation_hypothesis: str | None = None
    geolocation_confidence: float | None = None
    coordinate_pair = _extract_coordinate_pair(text_for_clues)
    if observed_latitude is not None and observed_longitude is not None:
        geolocation_hypothesis = f"Embedded coordinates {observed_latitude}, {observed_longitude} were found in media metadata."
        geolocation_confidence = 0.98
        reasoning.append("Geolocation hypothesis is based on embedded media metadata, not scene-only inference.")
        geolocation_basis = "embedded_media_metadata"
    elif coordinate_pair is not None:
        geolocation_hypothesis = f"Visible text referenced coordinates near {coordinate_pair[0]}, {coordinate_pair[1]}."
        geolocation_confidence = 0.82
        reasoning.append("Geolocation hypothesis used explicit coordinate text found via OCR or captions.")
        geolocation_basis = "ocr_or_caption_coordinates"
    elif place_hypothesis:
        geolocation_hypothesis = place_hypothesis
        geolocation_confidence = min(0.55, place_confidence or 0.35)
        reasoning.append("Geolocation hypothesis is text-clue-based and should be corroborated.")
        geolocation_basis = "textual_place_clues"
    if not reasoning:
        reasoning.append("Only limited deterministic media signals were available; stronger local model interpretation was not used.")
    uncertainty_ceiling = 0.72
    if geolocation_confidence and geolocation_confidence >= 0.9:
        uncertainty_ceiling = 0.22
    elif time_of_day_confidence and season_confidence and place_confidence:
        uncertainty_ceiling = 0.4
    return MediaInterpretationResult(
        status="completed",
        adapter="deterministic",
        model_name=None,
        scene_labels=sorted({label for label in labels if label}),
        scene_summary=_build_scene_summary(labels=labels, time_of_day_guess=time_of_day_guess, season_guess=season_guess),
        uncertainty_ceiling=uncertainty_ceiling,
        place_hypothesis=place_hypothesis,
        place_confidence=place_confidence,
        place_basis=place_basis,
        time_of_day_guess=time_of_day_guess,
        time_of_day_confidence=time_of_day_confidence,
        time_of_day_basis=time_of_day_basis,
        season_guess=season_guess,
        season_confidence=season_confidence,
        season_basis=season_basis,
        geolocation_hypothesis=geolocation_hypothesis,
        geolocation_confidence=geolocation_confidence,
        geolocation_basis=geolocation_basis,
        observed_latitude=observed_latitude,
        observed_longitude=observed_longitude,
        reasoning_lines=reasoning,
        metadata={
            "channelMeans": channel_means,
            "seasonalSignals": seasonal,
            "daylightSignals": daylight,
        },
        caveats=caveats,
    )


def _keyword_place_clues(text: str) -> tuple[str | None, float | None, list[str], list[str]]:
    lowered = text.casefold()
    labels: list[str] = []
    reasoning: list[str] = []
    if not lowered:
        return None, None, labels, reasoning
    keywords = {
        "airport": ("airport_or_airfield", 0.62),
        "station": ("station_or_transit_stop", 0.56),
        "harbor": ("harbor_or_port", 0.6),
        "port": ("harbor_or_port", 0.52),
        "bridge": ("bridge_or_river_crossing", 0.5),
        "castle": ("castle_or_historic_site", 0.58),
        "beach": ("coast_or_beach", 0.54),
        "trail": ("park_or_trail", 0.44),
        "park": ("park_or_public_space", 0.42),
        "terminal": ("terminal_or_station", 0.52),
    }
    best_label: str | None = None
    best_confidence: float | None = None
    for keyword, (label, confidence) in keywords.items():
        if keyword in lowered:
            labels.append(label)
            reasoning.append(f"Visible text includes '{keyword}', which suggests {label.replace('_', ' ')}.")
            if best_label is None or confidence > (best_confidence or 0.0):
                best_label = label
                best_confidence = confidence
    if best_label is None:
        return None, None, labels, reasoning
    return best_label.replace("_", " "), best_confidence, labels, reasoning


def _extract_coordinate_pair(text: str) -> tuple[float, float] | None:
    match = re.search(r"([-+]?\d{1,2}\.\d+)\s*,\s*([-+]?\d{1,3}\.\d+)", text)
    if not match:
        return None
    latitude = float(match.group(1))
    longitude = float(match.group(2))
    if not (-90.0 <= latitude <= 90.0 and -180.0 <= longitude <= 180.0):
        return None
    return round(latitude, 6), round(longitude, 6)


def _deterministic_result_needs_local_assist(result: MediaInterpretationResult) -> bool:
    if result.uncertainty_ceiling is not None and result.uncertainty_ceiling >= 0.5:
        return True
    if not result.place_hypothesis and not result.geolocation_hypothesis:
        return True
    return len(result.scene_labels) <= 1


def _merge_local_interpretation_with_deterministic(
    local_result: MediaInterpretationResult,
    deterministic_result: MediaInterpretationResult,
) -> MediaInterpretationResult:
    if not local_result.scene_labels:
        local_result.scene_labels = deterministic_result.scene_labels
    else:
        local_result.scene_labels = sorted(set(local_result.scene_labels + deterministic_result.scene_labels))
    if not local_result.scene_summary:
        local_result.scene_summary = deterministic_result.scene_summary
    if local_result.place_hypothesis is None:
        local_result.place_hypothesis = deterministic_result.place_hypothesis
        local_result.place_confidence = deterministic_result.place_confidence
        local_result.place_basis = deterministic_result.place_basis
    if local_result.time_of_day_guess is None:
        local_result.time_of_day_guess = deterministic_result.time_of_day_guess
        local_result.time_of_day_confidence = deterministic_result.time_of_day_confidence
        local_result.time_of_day_basis = deterministic_result.time_of_day_basis
    if local_result.season_guess is None:
        local_result.season_guess = deterministic_result.season_guess
        local_result.season_confidence = deterministic_result.season_confidence
        local_result.season_basis = deterministic_result.season_basis
    if local_result.geolocation_hypothesis is None:
        local_result.geolocation_hypothesis = deterministic_result.geolocation_hypothesis
        local_result.geolocation_confidence = deterministic_result.geolocation_confidence
        local_result.geolocation_basis = deterministic_result.geolocation_basis
    if local_result.observed_latitude is None:
        local_result.observed_latitude = deterministic_result.observed_latitude
    if local_result.observed_longitude is None:
        local_result.observed_longitude = deterministic_result.observed_longitude
    local_result.reasoning_lines = deterministic_result.reasoning_lines + local_result.reasoning_lines
    local_result.caveats = deterministic_result.caveats + local_result.caveats
    if local_result.uncertainty_ceiling is None:
        local_result.uncertainty_ceiling = deterministic_result.uncertainty_ceiling
    elif deterministic_result.uncertainty_ceiling is not None:
        local_result.uncertainty_ceiling = min(local_result.uncertainty_ceiling, deterministic_result.uncertainty_ceiling)
    return local_result


def _perceptual_hash_distance(left_hash: str | None, right_hash: str | None) -> int | None:
    if not left_hash or not right_hash:
        return None
    try:
        xor = int(left_hash, 16) ^ int(right_hash, 16)
    except ValueError:
        return None
    return bin(xor).count("1")


def _time_delta_seconds(left_value: str | None, right_value: str | None) -> int | None:
    if not left_value or not right_value:
        return None
    left = _parse_datetime_like(left_value)
    right = _parse_datetime_like(right_value)
    if left is None or right is None:
        return None
    return int(abs((left - right).total_seconds()))


def _parse_datetime_like(value: str) -> datetime | None:
    normalized = value.strip()
    if not normalized:
        return None
    for candidate in (normalized.replace("Z", "+00:00"), normalized.replace(":", "-", 2)):
        try:
            return datetime.fromisoformat(candidate)
        except ValueError:
            continue
    return None


def _compare_image_pixels(left_artifact_path: str | None, right_artifact_path: str | None) -> dict[str, Any]:
    left = _load_image_rgb_pixels(left_artifact_path)
    right = _load_image_rgb_pixels(right_artifact_path)
    if left is None or right is None:
        return {"caveat": "Image pixel comparison was limited because one or both artifacts could not be decoded."}
    left_width, left_height, left_pixels = left
    right_width, right_height, right_pixels = right
    left_gray = _resize_grayscale_pixels(left_width, left_height, left_pixels, 64, 64)
    right_gray = _resize_grayscale_pixels(right_width, right_height, right_pixels, 64, 64)
    left_color = _resize_rgb_pixels(left_width, left_height, left_pixels, 32, 32)
    right_color = _resize_rgb_pixels(right_width, right_height, right_pixels, 32, 32)
    return {
        "ssim_score": _ssim_score(left_gray, right_gray),
        "histogram_similarity": _histogram_similarity(left_color, right_color),
        "edge_similarity": _edge_similarity(left_gray, right_gray),
        "leftSize": {"width": left_width, "height": left_height},
        "rightSize": {"width": right_width, "height": right_height},
    }


def _load_image_rgb_pixels(artifact_path: str | None) -> tuple[int, int, list[tuple[int, int, int]]] | None:
    if not artifact_path:
        return None
    path = Path(artifact_path)
    if not path.exists():
        return None
    payload = path.read_bytes()
    if Image is not None:
        try:
            with Image.open(BytesIO(payload)) as image:
                rgb = ImageOps.exif_transpose(image).convert("RGB") if ImageOps is not None else image.convert("RGB")
                return rgb.width, rgb.height, list(rgb.getdata())
        except (UnidentifiedImageError, OSError):
            pass
    if payload.startswith(b"\x89PNG\r\n\x1a\n"):
        return _decode_png_rgb(payload)
    return None


def _resize_grayscale_pixels(
    width: int,
    height: int,
    pixels: list[tuple[int, int, int]],
    target_width: int,
    target_height: int,
) -> list[float]:
    resized: list[float] = []
    for y_index in range(target_height):
        source_y = min(height - 1, int((y_index / max(target_height, 1)) * height))
        for x_index in range(target_width):
            source_x = min(width - 1, int((x_index / max(target_width, 1)) * width))
            red, green_channel, blue = pixels[(source_y * width) + source_x]
            resized.append(round((red + green_channel + blue) / (3 * 255.0), 6))
    return resized


def _resize_rgb_pixels(
    width: int,
    height: int,
    pixels: list[tuple[int, int, int]],
    target_width: int,
    target_height: int,
) -> list[tuple[float, float, float]]:
    resized: list[tuple[float, float, float]] = []
    for y_index in range(target_height):
        source_y = min(height - 1, int((y_index / max(target_height, 1)) * height))
        for x_index in range(target_width):
            source_x = min(width - 1, int((x_index / max(target_width, 1)) * width))
            red, green_channel, blue = pixels[(source_y * width) + source_x]
            resized.append((red / 255.0, green_channel / 255.0, blue / 255.0))
    return resized


def _ssim_score(left: list[float], right: list[float]) -> float | None:
    if not left or not right or len(left) != len(right):
        return None
    left_mean = sum(left) / len(left)
    right_mean = sum(right) / len(right)
    left_variance = sum((value - left_mean) ** 2 for value in left) / len(left)
    right_variance = sum((value - right_mean) ** 2 for value in right) / len(right)
    covariance = sum((left[index] - left_mean) * (right[index] - right_mean) for index in range(len(left))) / len(left)
    c1 = 0.01 ** 2
    c2 = 0.03 ** 2
    denominator = (left_mean ** 2 + right_mean ** 2 + c1) * (left_variance + right_variance + c2)
    if denominator == 0:
        return None
    numerator = (2 * left_mean * right_mean + c1) * (2 * covariance + c2)
    return round(max(-1.0, min(1.0, numerator / denominator)), 4)


def _histogram_similarity(left: list[tuple[float, float, float]], right: list[tuple[float, float, float]]) -> float | None:
    if not left or not right:
        return None
    bins = 16
    left_hist = [0] * (bins * 3)
    right_hist = [0] * (bins * 3)
    for red, green_channel, blue in left:
        left_hist[min(bins - 1, int(red * bins))] += 1
        left_hist[bins + min(bins - 1, int(green_channel * bins))] += 1
        left_hist[(2 * bins) + min(bins - 1, int(blue * bins))] += 1
    for red, green_channel, blue in right:
        right_hist[min(bins - 1, int(red * bins))] += 1
        right_hist[bins + min(bins - 1, int(green_channel * bins))] += 1
        right_hist[(2 * bins) + min(bins - 1, int(blue * bins))] += 1
    distance = sum(abs(left_hist[index] - right_hist[index]) for index in range(len(left_hist)))
    total = max(1, sum(left_hist) + sum(right_hist))
    return round(max(0.0, 1.0 - (distance / total)), 4)


def _edge_similarity(left: list[float], right: list[float]) -> float | None:
    if not left or not right or len(left) != len(right):
        return None
    side = int(len(left) ** 0.5)
    if side * side != len(left):
        return None
    left_edges = _edge_map(left, side)
    right_edges = _edge_map(right, side)
    if not left_edges or not right_edges:
        return None
    difference = sum(abs(left_edges[index] - right_edges[index]) for index in range(len(left_edges)))
    total = max(1.0, sum(left_edges) + sum(right_edges))
    return round(max(0.0, 1.0 - (difference / total)), 4)


def _edge_map(values: list[float], side: int) -> list[float]:
    edges: list[float] = []
    for y_index in range(side):
        for x_index in range(side):
            index = (y_index * side) + x_index
            current = values[index]
            right = values[index + 1] if x_index + 1 < side else current
            down = values[index + side] if y_index + 1 < side else current
            edges.append(abs(current - right) + abs(current - down))
    return edges


def _token_similarity(left: str, right: str) -> float:
    left_tokens = _normalized_token_set(left)
    right_tokens = _normalized_token_set(right)
    if not left_tokens or not right_tokens:
        return 0.0
    return round(len(left_tokens & right_tokens) / len(left_tokens | right_tokens), 4)


def _normalized_token_set(text: str) -> set[str]:
    return {token for token in re.findall(r"[a-z0-9]{3,}", (text or "").casefold())}


def _polygon_bounds(polygon: Any) -> tuple[int | None, int | None, int | None, int | None]:
    if not isinstance(polygon, (list, tuple)) or not polygon:
        return None, None, None, None
    points = [point for point in polygon if isinstance(point, (list, tuple)) and len(point) >= 2]
    if not points:
        return None, None, None, None
    xs = [int(float(point[0])) for point in points]
    ys = [int(float(point[1])) for point in points]
    left = min(xs)
    top = min(ys)
    return left, top, max(xs) - left, max(ys) - top


def _build_scene_summary(*, labels: list[str], time_of_day_guess: str | None, season_guess: str | None) -> str | None:
    parts: list[str] = []
    if labels:
        parts.append("Scene labels: " + ", ".join(sorted({label.replace("_", " ") for label in labels})))
    if time_of_day_guess:
        parts.append(f"Time-of-day guess: {time_of_day_guess.replace('_', ' ')}")
    if season_guess:
        parts.append(f"Season guess: {season_guess.replace('_', ' ')}")
    if not parts:
        return None
    return "; ".join(parts)


def _month_from_timestamp(value: str) -> int | None:
    match = re.search(r"-(\d{2})-", value)
    if not match:
        return None
    month = int(match.group(1))
    return month if 1 <= month <= 12 else None


def _season_from_month(month: int, *, latitude: float) -> str:
    northern = latitude >= 0
    if month in {12, 1, 2}:
        return "winter" if northern else "summer"
    if month in {3, 4, 5}:
        return "spring" if northern else "autumn"
    if month in {6, 7, 8}:
        return "summer" if northern else "winter"
    return "autumn" if northern else "spring"


def _dedupe_text_list(values: list[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for item in values:
        normalized = _normalize_text(item)
        if not normalized:
            continue
        lowered = normalized.casefold()
        if lowered in seen:
            continue
        seen.add(lowered)
        deduped.append(normalized)
    return deduped


def _coerce_int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _coerce_float(value: Any) -> float | None:
    try:
        if value is None or value == "":
            return None
        return round(float(value), 4)
    except (TypeError, ValueError):
        return None


def _normalize_optional(value: Any) -> str | None:
    if value is None:
        return None
    normalized = _normalize_text(str(value))
    return normalized or None


def _normalize_geolocation_text(value: str) -> str:
    normalized = value or ""
    replacements = {
        "\u00a0": " ",
        "Â°": "°",
        "º": "°",
        "–": "-",
        "—": "-",
        "−": "-",
        "“": '"',
        "”": '"',
        "‟": '"',
        "’": "'",
        "‘": "'",
        "′": "'",
        "″": '"',
    }
    for old, new in replacements.items():
        normalized = normalized.replace(old, new)
    normalized = re.sub(r"\b([Il|])\s*-\s*(\d{1,3}[A-Z]?)\b", lambda match: f"I-{match.group(2).upper()}", normalized)
    normalized = re.sub(r"\b([Il|])\s+(\d{1,3}[A-Z]?)\b", lambda match: f"I-{match.group(2).upper()}", normalized)
    normalized = re.sub(r"\bU[S5]\s*-\s*(\d{1,3}[A-Z]?)\b", lambda match: f"US {match.group(1).upper()}", normalized, flags=re.IGNORECASE)
    normalized = re.sub(r"\bU[S5]\s+(\d{1,3}[A-Z]?)\b", lambda match: f"US {match.group(1).upper()}", normalized, flags=re.IGNORECASE)
    return _normalize_text(normalized)


def _normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def _safe_id(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9]+", "-", value).strip("-").lower() or "unknown"
