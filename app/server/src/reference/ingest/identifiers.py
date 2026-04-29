from __future__ import annotations

from src.reference.repository import normalize_alias


def build_ref_id(object_type: str, dataset_name: str, source_key: str) -> str:
    canonical_key = normalize_alias(source_key) or "unknown"
    return f"ref:{object_type}:{dataset_name}:{canonical_key}"
