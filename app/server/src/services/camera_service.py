from __future__ import annotations

from datetime import datetime, timezone

from src.config.settings import Settings
from src.services.camera_registry import is_camera_source_sandbox_importable
from src.types.api import (
    CameraQuery,
    CameraResponse,
    CameraSourceInventoryEntry,
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
            persisted_source_rows = repository.list_sources()
            source_map = {source.key: source for source in persisted_source_rows}
            persisted_sources = _merge_inventory(
                persisted_source_rows,
                [
                    _with_sandbox_metadata(self._settings, item, source_map.get(item.key))
                    for item in repository.list_source_inventory()
                ],
                self._settings,
            )
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
            persisted_source_rows = repository.list_sources()
            source_map = {source.key: source for source in persisted_source_rows}
            sources = _merge_inventory(
                persisted_source_rows,
                [
                    _with_sandbox_metadata(self._settings, item, source_map.get(item.key))
                    for item in repository.list_source_inventory()
                ],
                self._settings,
            )
        return CameraSourceRegistryResponse(sources=sources)

    async def list_source_inventory(self) -> CameraSourceInventoryResponse:
        await self._refresh_service.bootstrap_inventory()
        with session_scope(self._database_url) as session:
            repository = WebcamRepository(session)
            source_map = {source.key: source for source in repository.list_sources()}
            sources = [
                _with_sandbox_metadata(self._settings, item, source_map.get(item.key))
                for item in repository.list_source_inventory()
            ]
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
    settings: Settings,
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
                    "endpoint_verification_status": item.endpoint_verification_status,
                    "candidate_endpoint_url": item.candidate_endpoint_url,
                    "machine_readable_endpoint_url": item.machine_readable_endpoint_url,
                    "last_endpoint_check_at": item.last_endpoint_check_at,
                    "last_endpoint_http_status": item.last_endpoint_http_status,
                    "last_endpoint_content_type": item.last_endpoint_content_type,
                    "last_endpoint_result": item.last_endpoint_result,
                    "last_endpoint_notes": item.last_endpoint_notes,
                    "verification_caveat": item.verification_caveat,
                    "sandbox_import_available": item.sandbox_import_available,
                    "sandbox_import_mode": item.sandbox_import_mode,
                    "sandbox_connector_id": item.sandbox_connector_id,
                    "last_sandbox_import_at": item.last_sandbox_import_at,
                    "last_sandbox_import_outcome": item.last_sandbox_import_outcome,
                    "sandbox_discovered_count": item.sandbox_discovered_count,
                    "sandbox_usable_count": item.sandbox_usable_count,
                    "sandbox_review_queue_count": item.sandbox_review_queue_count,
                    "sandbox_validation_caveat": item.sandbox_validation_caveat,
                }
            )
        )
    return merged


def _with_sandbox_metadata(
    settings: Settings,
    item: CameraSourceInventoryEntry,
    source: CameraSourceRegistryEntry | None = None,
) -> CameraSourceInventoryEntry:
    sandbox_available = is_camera_source_sandbox_importable(item.key, settings)
    if not sandbox_available:
        return item
    mode = settings.finland_digitraffic_weathercam_mode.lower()
    return item.model_copy(
        update={
            "sandbox_import_available": True,
            "sandbox_import_mode": mode if mode in {"fixture", "live"} else None,
            "sandbox_connector_id": "FinlandDigitrafficWeatherCamConnector",
            "last_sandbox_import_at": (
                source.last_validation_at
                or source.last_completed_at
                or item.last_catalog_import_at
            ) if source is not None else item.last_catalog_import_at,
            "last_sandbox_import_outcome": (
                item.last_import_outcome
                or item.last_catalog_import_status
                or source.status
            ) if source is not None else (item.last_import_outcome or item.last_catalog_import_status),
            "sandbox_discovered_count": item.discovered_camera_count,
            "sandbox_usable_count": item.usable_camera_count,
            "sandbox_review_queue_count": item.review_queue_count,
            "sandbox_validation_caveat": (
                "Sandbox fixture import proves mapping only. It does not mark the source validated or enable scheduled ingestion."
            ),
        }
    )


def _now_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat()
