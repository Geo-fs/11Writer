from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ReferenceRecord:
    ref_id: str
    object_type: str
    canonical_name: str
    primary_code: str | None
    source_dataset: str
    source_key: str
    status: str
    country_code: str | None
    admin1_code: str | None
    centroid_lat: float | None
    centroid_lon: float | None
    bbox_min_lat: float | None
    bbox_min_lon: float | None
    bbox_max_lat: float | None
    bbox_max_lon: float | None
    geometry_json: str | None
    coverage_tier: str
    search_text: str | None = None
    source_version: str | None = None
    last_ingested_at: str | None = None
    aliases: list[tuple[str, str]] = field(default_factory=list)
    detail: dict[str, Any] = field(default_factory=dict)


@dataclass
class SearchCandidate:
    record: ReferenceRecord
    rank_reason: str
    score: float
    matched_field: str | None = None
    matched_value: str | None = None


@dataclass
class ReviewedLinkRecord:
    link_id: int
    external_system: str
    external_object_type: str
    external_object_id: str
    ref_id: str
    link_kind: str
    confidence: float
    method: str
    notes: str | None
    review_status: str
    reviewed_by: str | None
    reviewed_at: str | None
    review_source: str | None
    candidate_method: str | None = None
    candidate_score: float | None = None
    created_at: str | None = None
    updated_at: str | None = None
