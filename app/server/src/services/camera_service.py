from __future__ import annotations

from datetime import datetime, timezone

from src.config.settings import Settings
from src.types.api import (
    CameraQuery,
    CameraResponse,
    CameraSourceInventoryResponse,
    CameraSourceInventorySummary,
    CameraSourceRegistryEntry,
    CameraSourceRegistryResponse,
    FilterSummary,
    ReviewQueueResponse,
)
from src.types.entities import CameraEntity
from src.webcam.db import session_scope
from src.webcam.refresh import WebcamRefreshService, build_review_items
from src.webcam.repository import WebcamRepository


class CameraService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._database_url = settings.camera_database_url
        self._refresh_service = WebcamRefreshService(settings)

    async def list_cameras(self, query: CameraQuery) -> CameraResponse:
        await self._refresh_service.run_due_work()
        with session_scope(self._database_url) as session:
            repository = WebcamRepository(session)
            all_cameras = repository.list_cameras()
            persisted_sources = _merge_inventory(repository.list_sources(), repository.list_source_inventory())
        filtered = self._apply_query(all_cameras, query)[: query.limit]
        return CameraResponse(
            fetched_at=_now_iso(),
            source="camera-registry",
            count=len(filtered),
            summary=FilterSummary(
                active_filters=_build_filter_summary(query),
                total_candidates=len(all_cameras),
                filtered_count=len(filtered),
                staleness_warning=_camera_staleness_warning(persisted_sources),
            ),
            cameras=filtered,
            sources=persisted_sources,
        )

    async def list_sources(self) -> CameraSourceRegistryResponse:
        await self._refresh_service.run_due_work()
        with session_scope(self._database_url) as session:
            repository = WebcamRepository(session)
            sources = _merge_inventory(repository.list_sources(), repository.list_source_inventory())
        return CameraSourceRegistryResponse(sources=sources)

    async def list_source_inventory(self) -> CameraSourceInventoryResponse:
        await self._refresh_service.bootstrap_inventory()
        with session_scope(self._database_url) as session:
            sources = WebcamRepository(session).list_source_inventory()
        sources_by_type: dict[str, int] = {}
        for source in sources:
            sources_by_type[source.source_type] = sources_by_type.get(source.source_type, 0) + 1
        return CameraSourceInventoryResponse(
            fetched_at=_now_iso(),
            count=len(sources),
            summary=CameraSourceInventorySummary(
                total_sources=len(sources),
                active_sources=sum(1 for source in sources if source.onboarding_state == "active"),
                credentialed_sources=sum(1 for source in sources if source.authentication != "none"),
                credentialless_sources=sum(1 for source in sources if source.authentication == "none"),
                direct_image_sources=sum(1 for source in sources if source.provides_direct_image),
                viewer_only_sources=sum(1 for source in sources if source.provides_viewer_only and not source.provides_direct_image),
                validated_sources=sum(1 for source in sources if source.import_readiness == "validated"),
                low_yield_sources=sum(1 for source in sources if source.import_readiness == "low-yield"),
                poor_quality_sources=sum(1 for source in sources if source.import_readiness == "poor-quality"),
                sources_by_type=sources_by_type,
            ),
            sources=sources,
        )

    async def build_review_queue(self, *, limit: int = 200) -> ReviewQueueResponse:
        await self._refresh_service.run_due_work()
        with session_scope(self._database_url) as session:
            repository = WebcamRepository(session)
            persisted = repository.list_review_queue(limit=limit)
            if persisted:
                items = persisted
            else:
                items = build_review_items(repository.list_cameras())
                repository.replace_review_queue(items)
        return ReviewQueueResponse(
            fetched_at=_now_iso(),
            count=min(len(items), limit),
            items=items[:limit],
        )

    @staticmethod
    def _apply_query(cameras: list[CameraEntity], query: CameraQuery) -> list[CameraEntity]:
        results: list[CameraEntity] = []
        for camera in cameras:
            if query.active_only and camera.status != "active":
                continue
            if query.source and camera.source != query.source:
                continue
            if query.state and (camera.state or "").lower() != query.state.lower():
                continue
            if query.review_status and camera.review.status != query.review_status:
                continue
            if query.coordinate_kind and camera.position.kind != query.coordinate_kind:
                continue
            if query.orientation_kind and camera.orientation.kind != query.orientation_kind:
                continue
            if query.q:
                needle = query.q.strip().lower()
                haystacks = [
                    camera.label.lower(),
                    (camera.roadway or "").lower(),
                    (camera.location_description or "").lower(),
                    (camera.state or "").lower(),
                    (camera.region or "").lower(),
                    (camera.camera_id or "").lower(),
                ]
                if not any(needle in haystack for haystack in haystacks):
                    continue
            if query.lamin is not None and camera.latitude < min(query.lamin, query.lamax or query.lamin):
                continue
            if query.lamax is not None and camera.latitude > max(query.lamax, query.lamin or query.lamax):
                continue
            if query.lomin is not None and camera.longitude < min(query.lomin, query.lomax or query.lomin):
                continue
            if query.lomax is not None and camera.longitude > max(query.lomax, query.lomin or query.lomax):
                continue
            results.append(camera)
        return results


def _build_filter_summary(query: CameraQuery) -> dict[str, str]:
    filters: dict[str, str] = {"limit": str(query.limit)}
    for key in (
        "q",
        "source",
        "state",
        "review_status",
        "coordinate_kind",
        "orientation_kind",
        "active_only",
    ):
        value = getattr(query, key)
        if value is not None:
            filters[key] = str(value)
    if None not in (query.lamin, query.lamax, query.lomin, query.lomax):
        filters["viewport"] = (
            f"{query.lamin:.4f},{query.lamax:.4f},{query.lomin:.4f},{query.lomax:.4f}"
        )
    return filters


def _camera_staleness_warning(sources: list[CameraSourceRegistryEntry]) -> str | None:
    stale = [source.display_name for source in sources if source.status == "stale"]
    if not stale:
        return None
    return f"Some camera sources are stale: {', '.join(stale[:3])}"


def _merge_inventory(
    sources: list[CameraSourceRegistryEntry],
    inventory: list,
) -> list[CameraSourceRegistryEntry]:
    inventory_map = {item.key: item for item in inventory}
    merged: list[CameraSourceRegistryEntry] = []
    for source in sources:
        item = inventory_map.get(source.key)
        if item is None:
            merged.append(source)
            continue
        merged.append(
            source.model_copy(
                update={
                    "inventory_source_type": item.source_type,
                    "access_method": item.access_method,
                    "onboarding_state": item.onboarding_state,
                    "coverage_states": item.coverage_states,
                    "coverage_regions": item.coverage_regions,
                    "provides_exact_coordinates": item.provides_exact_coordinates,
                    "provides_direction_text": item.provides_direction_text,
                    "provides_numeric_heading": item.provides_numeric_heading,
                    "provides_direct_image": item.provides_direct_image,
                    "provides_viewer_only": item.provides_viewer_only,
                    "supports_embed": item.supports_embed,
                    "supports_storage": item.supports_storage,
                    "approximate_camera_count": item.approximate_camera_count or source.last_camera_count,
                    "import_readiness": item.import_readiness,
                    "discovered_camera_count": item.discovered_camera_count,
                    "usable_camera_count": item.usable_camera_count,
                    "direct_image_camera_count": item.direct_image_camera_count,
                    "viewer_only_camera_count": item.viewer_only_camera_count,
                    "missing_coordinate_camera_count": item.missing_coordinate_camera_count,
                    "uncertain_orientation_camera_count": item.uncertain_orientation_camera_count,
                    "review_queue_count": item.review_queue_count,
                    "last_import_outcome": item.last_import_outcome,
                    "source_quality_notes": item.source_quality_notes,
                    "source_stability_notes": item.source_stability_notes,
                    "page_structure": item.page_structure,
                    "likely_camera_count": item.likely_camera_count,
                    "compliance_risk": item.compliance_risk,
                    "extraction_feasibility": item.extraction_feasibility,
                }
            )
        )
    return merged


def _now_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat()
