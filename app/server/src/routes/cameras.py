from fastapi import APIRouter, Depends, HTTPException, Query

from src.config.settings import Settings, get_settings
from src.services.camera_source_ops_detail import build_camera_source_ops_detail
from src.services.camera_source_ops_evidence_packets import (
    build_camera_source_ops_evidence_packet_export_bundle,
    build_camera_source_ops_evidence_packet_handoff_export_bundle,
    build_camera_source_ops_evidence_packet_handoff_summary,
    build_camera_source_ops_evidence_packets,
)
from src.services.camera_source_ops_export_summary import build_camera_source_ops_export_summary
from src.services.camera_source_ops_export_readiness import build_camera_source_ops_export_readiness
from src.services.camera_source_ops_report_index import build_camera_source_ops_report_index
from src.services.camera_source_ops_review_queue import build_filtered_camera_source_ops_review_queue
from src.services.camera_source_ops_review_queue import build_camera_source_ops_review_queue_export_bundle
from src.services.camera_source_ops_unified_export_surface import build_camera_source_ops_unified_export_surface
from src.services.camera_service import CameraService
from src.types.api import (
    CameraQuery,
    CameraResponse,
    CameraSourceInventoryResponse,
    CameraSourceOpsDetailResponse,
    CameraSourceOpsEvidencePacketExportBundleResponse,
    CameraSourceOpsEvidencePacketHandoffExportBundleResponse,
    CameraSourceOpsEvidencePacketHandoffSummaryResponse,
    CameraSourceOpsEvidencePacketResponse,
    CameraSourceOpsExportSummaryResponse,
    CameraSourceOpsExportReadinessResponse,
    CameraSourceOpsIndexResponse,
    CameraSourceOpsReviewQueueExportBundleResponse,
    CameraSourceOpsReviewQueueResponse,
    CameraSourceOpsUnifiedExportSurfaceResponse,
    CameraSourceRegistryResponse,
    ReviewQueueResponse,
)

router = APIRouter(prefix="/api/cameras", tags=["cameras"])


@router.get("", response_model=CameraResponse)
async def list_cameras(
    lamin: float | None = Query(default=None, ge=-90.0, le=90.0),
    lamax: float | None = Query(default=None, ge=-90.0, le=90.0),
    lomin: float | None = Query(default=None, ge=-180.0, le=180.0),
    lomax: float | None = Query(default=None, ge=-180.0, le=180.0),
    limit: int = Query(default=500, ge=1, le=5000),
    q: str | None = Query(default=None),
    source: str | None = Query(default=None),
    state: str | None = Query(default=None, min_length=2, max_length=2),
    review_status: str | None = Query(default=None),
    coordinate_kind: str | None = Query(default=None),
    orientation_kind: str | None = Query(default=None),
    active_only: bool = Query(default=True),
    settings: Settings = Depends(get_settings),
) -> CameraResponse:
    query = CameraQuery(
        lamin=lamin,
        lamax=lamax,
        lomin=lomin,
        lomax=lomax,
        limit=limit,
        q=q,
        source=source,
        state=state.upper() if state else None,
        review_status=review_status,
        coordinate_kind=coordinate_kind,
        orientation_kind=orientation_kind,
        active_only=active_only,
    )
    return await CameraService(settings).list_cameras(query)


@router.get("/sources", response_model=CameraSourceRegistryResponse)
async def list_camera_sources(settings: Settings = Depends(get_settings)) -> CameraSourceRegistryResponse:
    return await CameraService(settings).list_sources()


@router.get("/source-inventory", response_model=CameraSourceInventoryResponse)
async def list_camera_source_inventory(settings: Settings = Depends(get_settings)) -> CameraSourceInventoryResponse:
    return await CameraService(settings).list_source_inventory()


@router.get("/source-ops-index", response_model=CameraSourceOpsIndexResponse)
async def list_camera_source_ops_index(
    settings: Settings = Depends(get_settings),
) -> CameraSourceOpsIndexResponse:
    return build_camera_source_ops_report_index(settings)


@router.get("/source-ops-index/{source_id}", response_model=CameraSourceOpsDetailResponse)
async def get_camera_source_ops_detail(
    source_id: str,
    settings: Settings = Depends(get_settings),
) -> CameraSourceOpsDetailResponse:
    detail = build_camera_source_ops_detail(settings, source_id)
    if detail is None:
        raise HTTPException(status_code=404, detail=f"Camera source '{source_id}' was not found")
    return detail


@router.get("/source-ops-export-summary", response_model=CameraSourceOpsExportSummaryResponse)
async def get_camera_source_ops_export_summary(
    source_ids: str | None = Query(default=None, description="Comma-separated source ids for detail export lines"),
    include_review_queue_aggregate_lines: bool = Query(default=False),
    review_queue_priority_band: str | None = Query(default=None),
    review_queue_reason_category: str | None = Query(default=None),
    review_queue_lifecycle_state: str | None = Query(default=None),
    review_queue_source_ids: str | None = Query(default=None, description="Comma-separated source ids for filtered review queue aggregate lines"),
    review_queue_limit: int = Query(default=50, ge=1, le=200),
    settings: Settings = Depends(get_settings),
) -> CameraSourceOpsExportSummaryResponse:
    requested_ids = [item.strip() for item in (source_ids or "").split(",") if item.strip()]
    review_queue_requested_ids = [item.strip() for item in (review_queue_source_ids or "").split(",") if item.strip()]
    return build_camera_source_ops_export_summary(
        settings,
        requested_ids or None,
        include_review_queue_aggregate_lines=include_review_queue_aggregate_lines,
        review_queue_priority_band=review_queue_priority_band,
        review_queue_reason_category=review_queue_reason_category,
        review_queue_lifecycle_state=review_queue_lifecycle_state,
        review_queue_source_ids=review_queue_requested_ids or None,
        review_queue_limit=review_queue_limit,
    )


@router.get("/source-ops-review-queue", response_model=CameraSourceOpsReviewQueueResponse)
async def get_camera_source_ops_review_queue(
    priority_band: str | None = Query(default=None),
    reason_category: str | None = Query(default=None),
    lifecycle_state: str | None = Query(default=None),
    source_ids: str | None = Query(default=None, description="Comma-separated source ids to constrain review items"),
    limit: int = Query(default=50, ge=1, le=200),
    aggregate_only: bool = Query(default=False),
    settings: Settings = Depends(get_settings),
) -> CameraSourceOpsReviewQueueResponse:
    requested_ids = [item.strip() for item in (source_ids or "").split(",") if item.strip()]
    return build_filtered_camera_source_ops_review_queue(
        settings,
        priority_band=priority_band,
        reason_category=reason_category,
        lifecycle_state=lifecycle_state,
        source_ids=requested_ids or None,
        limit=limit,
        aggregate_only=aggregate_only,
    )


@router.get("/source-ops-review-queue-export-bundle", response_model=CameraSourceOpsReviewQueueExportBundleResponse)
async def get_camera_source_ops_review_queue_export_bundle(
    priority_band: str | None = Query(default=None),
    reason_category: str | None = Query(default=None),
    lifecycle_state: str | None = Query(default=None),
    source_ids: str | None = Query(default=None, description="Comma-separated source ids to constrain review aggregate lines"),
    limit: int = Query(default=50, ge=1, le=200),
    settings: Settings = Depends(get_settings),
) -> CameraSourceOpsReviewQueueExportBundleResponse:
    requested_ids = [item.strip() for item in (source_ids or "").split(",") if item.strip()]
    return build_camera_source_ops_review_queue_export_bundle(
        settings,
        priority_band=priority_band,
        reason_category=reason_category,
        lifecycle_state=lifecycle_state,
        source_ids=requested_ids or None,
        limit=limit,
    )


@router.get("/source-ops-export-readiness", response_model=CameraSourceOpsExportReadinessResponse)
async def get_camera_source_ops_export_readiness(
    source_ids: str | None = Query(default=None, description="Comma-separated source ids to constrain export-readiness output"),
    lifecycle_state: str | None = Query(default=None),
    missing_evidence_category: str | None = Query(default=None),
    settings: Settings = Depends(get_settings),
) -> CameraSourceOpsExportReadinessResponse:
    requested_ids = [item.strip() for item in (source_ids or "").split(",") if item.strip()]
    return build_camera_source_ops_export_readiness(
        settings,
        source_ids=requested_ids or None,
        lifecycle_state=lifecycle_state,
        missing_evidence_category=missing_evidence_category,
    )


@router.get("/source-ops-evidence-packets", response_model=CameraSourceOpsEvidencePacketResponse)
async def get_camera_source_ops_evidence_packets(
    source_ids: str | None = Query(default=None, description="Comma-separated source ids to constrain evidence packets"),
    lifecycle_state: str | None = Query(default=None),
    blocked_reason_posture: str | None = Query(default=None),
    evidence_gap_family: str | None = Query(default=None),
    settings: Settings = Depends(get_settings),
) -> CameraSourceOpsEvidencePacketResponse:
    requested_ids = [item.strip() for item in (source_ids or "").split(",") if item.strip()]
    return build_camera_source_ops_evidence_packets(
        settings,
        source_ids=requested_ids or None,
        lifecycle_state=lifecycle_state,
        blocked_reason_posture=blocked_reason_posture,
        evidence_gap_family=evidence_gap_family,
    )


@router.get(
    "/source-ops-evidence-packets-export-bundle",
    response_model=CameraSourceOpsEvidencePacketExportBundleResponse,
)
async def get_camera_source_ops_evidence_packet_export_bundle(
    source_ids: str | None = Query(default=None, description="Comma-separated source ids to constrain evidence-packet export bundle"),
    lifecycle_state: str | None = Query(default=None),
    blocked_reason_posture: str | None = Query(default=None),
    evidence_gap_family: str | None = Query(default=None),
    settings: Settings = Depends(get_settings),
) -> CameraSourceOpsEvidencePacketExportBundleResponse:
    requested_ids = [item.strip() for item in (source_ids or "").split(",") if item.strip()]
    return build_camera_source_ops_evidence_packet_export_bundle(
        settings,
        source_ids=requested_ids or None,
        lifecycle_state=lifecycle_state,
        blocked_reason_posture=blocked_reason_posture,
        evidence_gap_family=evidence_gap_family,
    )


@router.get(
    "/source-ops-evidence-packets-handoff-summary",
    response_model=CameraSourceOpsEvidencePacketHandoffSummaryResponse,
)
async def get_camera_source_ops_evidence_packet_handoff_summary(
    source_ids: str | None = Query(default=None, description="Comma-separated source ids to constrain evidence-packet handoff summary"),
    lifecycle_state: str | None = Query(default=None),
    blocked_reason_posture: str | None = Query(default=None),
    evidence_gap_family: str | None = Query(default=None),
    settings: Settings = Depends(get_settings),
) -> CameraSourceOpsEvidencePacketHandoffSummaryResponse:
    requested_ids = [item.strip() for item in (source_ids or "").split(",") if item.strip()]
    return build_camera_source_ops_evidence_packet_handoff_summary(
        settings,
        source_ids=requested_ids or None,
        lifecycle_state=lifecycle_state,
        blocked_reason_posture=blocked_reason_posture,
        evidence_gap_family=evidence_gap_family,
    )


@router.get(
    "/source-ops-evidence-packets-handoff-export-bundle",
    response_model=CameraSourceOpsEvidencePacketHandoffExportBundleResponse,
)
async def get_camera_source_ops_evidence_packet_handoff_export_bundle(
    source_ids: str | None = Query(default=None, description="Comma-separated source ids to constrain handoff export bundle"),
    lifecycle_state: str | None = Query(default=None),
    blocked_reason_posture: str | None = Query(default=None),
    evidence_gap_family: str | None = Query(default=None),
    settings: Settings = Depends(get_settings),
) -> CameraSourceOpsEvidencePacketHandoffExportBundleResponse:
    requested_ids = [item.strip() for item in (source_ids or "").split(",") if item.strip()]
    return build_camera_source_ops_evidence_packet_handoff_export_bundle(
        settings,
        source_ids=requested_ids or None,
        lifecycle_state=lifecycle_state,
        blocked_reason_posture=blocked_reason_posture,
        evidence_gap_family=evidence_gap_family,
    )


@router.get(
    "/source-ops-export-surface",
    response_model=CameraSourceOpsUnifiedExportSurfaceResponse,
)
async def get_camera_source_ops_unified_export_surface(
    source_ids: str | None = Query(default=None, description="Comma-separated source ids to constrain the unified source-ops export surface"),
    lifecycle_state: str | None = Query(default=None),
    blocked_reason_posture: str | None = Query(default=None),
    evidence_gap_family: str | None = Query(default=None),
    review_queue_priority_band: str | None = Query(default=None),
    review_queue_reason_category: str | None = Query(default=None),
    settings: Settings = Depends(get_settings),
) -> CameraSourceOpsUnifiedExportSurfaceResponse:
    requested_ids = [item.strip() for item in (source_ids or "").split(",") if item.strip()]
    return build_camera_source_ops_unified_export_surface(
        settings,
        source_ids=requested_ids or None,
        lifecycle_state=lifecycle_state,
        blocked_reason_posture=blocked_reason_posture,
        evidence_gap_family=evidence_gap_family,
        review_queue_priority_band=review_queue_priority_band,
        review_queue_reason_category=review_queue_reason_category,
    )


@router.get("/review-queue", response_model=ReviewQueueResponse)
async def list_camera_review_queue(
    limit: int = Query(default=200, ge=1, le=2000),
    settings: Settings = Depends(get_settings),
) -> ReviewQueueResponse:
    return await CameraService(settings).build_review_queue(limit=limit)
