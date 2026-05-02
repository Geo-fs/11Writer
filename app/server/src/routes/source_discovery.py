from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from src.config.settings import Settings, get_settings
from src.services.source_discovery_service import SourceDiscoveryService
from src.services.runtime_scheduler_service import (
    build_runtime_service_bundle,
    build_runtime_status,
    control_runtime_worker,
)
from src.types.source_discovery import (
    SourceDiscoveryArticleFetchRequest,
    SourceDiscoveryArticleFetchResponse,
    SourceDiscoveryCatalogScanRequest,
    SourceDiscoveryCatalogScanResponse,
    SourceDiscoveryCandidateSeed,
    SourceDiscoveryClaimOutcomeRequest,
    SourceDiscoveryClaimOutcomeResponse,
    SourceDiscoveryContentSnapshotRequest,
    SourceDiscoveryContentSnapshotResponse,
    SourceDiscoveryFeedLinkScanRequest,
    SourceDiscoveryFeedLinkScanResponse,
    SourceDiscoveryExpansionJobRequest,
    SourceDiscoveryExpansionJobResponse,
    SourceDiscoveryHealthCheckRequest,
    SourceDiscoveryHealthCheckResponse,
    SourceDiscoveryMemory,
    SourceDiscoveryMemoryDetailResponse,
    SourceDiscoveryMemoryExportResponse,
    SourceDiscoveryMemoryListResponse,
    SourceDiscoveryMemoryOverviewResponse,
    SourceDiscoveryRecordSourceExtractRequest,
    SourceDiscoveryRecordSourceExtractResponse,
    SourceDiscoveryReputationReversalRequest,
    SourceDiscoveryReputationReversalResponse,
    SourceDiscoveryReviewActionRequest,
    SourceDiscoveryReviewActionResponse,
    SourceDiscoveryReviewClaimApplicationRequest,
    SourceDiscoveryReviewClaimApplicationResponse,
    SourceDiscoveryReviewQueueResponse,
    SourceDiscoveryRuntimeControlRequest,
    SourceDiscoveryRuntimeControlResponse,
    SourceDiscoveryRuntimeServiceBundleResponse,
    SourceDiscoveryRuntimeStatusResponse,
    SourceDiscoverySchedulerTickRequest,
    SourceDiscoverySchedulerTickResponse,
    SourceDiscoverySeedUrlJobRequest,
    SourceDiscoverySeedUrlJobResponse,
    SourceDiscoverySocialMetadataJobRequest,
    SourceDiscoverySocialMetadataJobResponse,
)

router = APIRouter(prefix="/api/source-discovery", tags=["source-discovery"])


@router.get("/memory/overview", response_model=SourceDiscoveryMemoryOverviewResponse)
def source_discovery_memory_overview(
    limit: int = 100,
    settings: Settings = Depends(get_settings),
) -> SourceDiscoveryMemoryOverviewResponse:
    service = SourceDiscoveryService(settings)
    return service.overview(limit=limit)


@router.get("/memory/list", response_model=SourceDiscoveryMemoryListResponse)
def source_discovery_memory_list(
    limit: int = 100,
    owner_lane: str | None = None,
    source_class: str | None = None,
    lifecycle_state: str | None = None,
    settings: Settings = Depends(get_settings),
) -> SourceDiscoveryMemoryListResponse:
    service = SourceDiscoveryService(settings)
    return service.list_memories(
        limit=limit,
        owner_lane=owner_lane,
        source_class=source_class,
        lifecycle_state=lifecycle_state,
    )


@router.get("/memory/{source_id}", response_model=SourceDiscoveryMemoryDetailResponse)
def source_discovery_memory_detail(
    source_id: str,
    limit: int = 25,
    settings: Settings = Depends(get_settings),
) -> SourceDiscoveryMemoryDetailResponse:
    service = SourceDiscoveryService(settings)
    try:
        return service.memory_detail(source_id, limit=limit)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/memory/{source_id}/export", response_model=SourceDiscoveryMemoryExportResponse)
def source_discovery_memory_export(
    source_id: str,
    limit: int = 25,
    settings: Settings = Depends(get_settings),
) -> SourceDiscoveryMemoryExportResponse:
    service = SourceDiscoveryService(settings)
    try:
        return service.export_memory_packet(source_id, limit=limit)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/memory/candidates", response_model=SourceDiscoveryMemory)
def source_discovery_upsert_candidate(
    seed: SourceDiscoveryCandidateSeed,
    settings: Settings = Depends(get_settings),
) -> SourceDiscoveryMemory:
    service = SourceDiscoveryService(settings)
    return service.upsert_candidate(seed)


@router.post("/memory/claim-outcomes", response_model=SourceDiscoveryClaimOutcomeResponse)
def source_discovery_record_claim_outcome(
    request: SourceDiscoveryClaimOutcomeRequest,
    settings: Settings = Depends(get_settings),
) -> SourceDiscoveryClaimOutcomeResponse:
    service = SourceDiscoveryService(settings)
    return service.record_claim_outcome(request)


@router.post("/jobs/seed-url", response_model=SourceDiscoverySeedUrlJobResponse)
def source_discovery_run_seed_url_job(
    request: SourceDiscoverySeedUrlJobRequest,
    settings: Settings = Depends(get_settings),
) -> SourceDiscoverySeedUrlJobResponse:
    service = SourceDiscoveryService(settings)
    return service.run_seed_url_job(request)


@router.post("/health/check", response_model=SourceDiscoveryHealthCheckResponse)
def source_discovery_check_health(
    request: SourceDiscoveryHealthCheckRequest,
    settings: Settings = Depends(get_settings),
) -> SourceDiscoveryHealthCheckResponse:
    service = SourceDiscoveryService(settings)
    try:
        return service.check_source_health(request)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/jobs/expand", response_model=SourceDiscoveryExpansionJobResponse)
def source_discovery_run_expansion_job(
    request: SourceDiscoveryExpansionJobRequest,
    settings: Settings = Depends(get_settings),
) -> SourceDiscoveryExpansionJobResponse:
    service = SourceDiscoveryService(settings)
    return service.run_expansion_job(request)


@router.post("/jobs/catalog-scan", response_model=SourceDiscoveryCatalogScanResponse)
def source_discovery_run_catalog_scan_job(
    request: SourceDiscoveryCatalogScanRequest,
    settings: Settings = Depends(get_settings),
) -> SourceDiscoveryCatalogScanResponse:
    service = SourceDiscoveryService(settings)
    return service.run_catalog_scan_job(request)


@router.post("/jobs/feed-link-scan", response_model=SourceDiscoveryFeedLinkScanResponse)
def source_discovery_run_feed_link_scan_job(
    request: SourceDiscoveryFeedLinkScanRequest,
    settings: Settings = Depends(get_settings),
) -> SourceDiscoveryFeedLinkScanResponse:
    service = SourceDiscoveryService(settings)
    return service.run_feed_link_scan_job(request)


@router.post("/jobs/record-source-extract", response_model=SourceDiscoveryRecordSourceExtractResponse)
def source_discovery_run_record_source_extract_job(
    request: SourceDiscoveryRecordSourceExtractRequest,
    settings: Settings = Depends(get_settings),
) -> SourceDiscoveryRecordSourceExtractResponse:
    service = SourceDiscoveryService(settings)
    return service.run_record_source_extract_job(request)


@router.post("/content/snapshots", response_model=SourceDiscoveryContentSnapshotResponse)
def source_discovery_store_content_snapshot(
    request: SourceDiscoveryContentSnapshotRequest,
    settings: Settings = Depends(get_settings),
) -> SourceDiscoveryContentSnapshotResponse:
    service = SourceDiscoveryService(settings)
    try:
        return service.store_content_snapshot(request)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/jobs/article-fetch", response_model=SourceDiscoveryArticleFetchResponse)
def source_discovery_run_article_fetch_job(
    request: SourceDiscoveryArticleFetchRequest,
    settings: Settings = Depends(get_settings),
) -> SourceDiscoveryArticleFetchResponse:
    service = SourceDiscoveryService(settings)
    try:
        return service.run_article_fetch_job(request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/jobs/social-metadata", response_model=SourceDiscoverySocialMetadataJobResponse)
def source_discovery_run_social_metadata_job(
    request: SourceDiscoverySocialMetadataJobRequest,
    settings: Settings = Depends(get_settings),
) -> SourceDiscoverySocialMetadataJobResponse:
    service = SourceDiscoveryService(settings)
    try:
        return service.run_social_metadata_job(request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/reputation/reverse-event", response_model=SourceDiscoveryReputationReversalResponse)
def source_discovery_reverse_reputation_event(
    request: SourceDiscoveryReputationReversalRequest,
    settings: Settings = Depends(get_settings),
) -> SourceDiscoveryReputationReversalResponse:
    service = SourceDiscoveryService(settings)
    try:
        return service.reverse_reputation_event(request)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/scheduler/tick", response_model=SourceDiscoverySchedulerTickResponse)
def source_discovery_scheduler_tick(
    request: SourceDiscoverySchedulerTickRequest,
    settings: Settings = Depends(get_settings),
) -> SourceDiscoverySchedulerTickResponse:
    service = SourceDiscoveryService(settings)
    return service.run_scheduler_tick(request)


@router.get("/review/queue", response_model=SourceDiscoveryReviewQueueResponse)
def source_discovery_review_queue(
    limit: int = 100,
    owner_lane: str | None = None,
    settings: Settings = Depends(get_settings),
) -> SourceDiscoveryReviewQueueResponse:
    service = SourceDiscoveryService(settings)
    return service.review_queue(limit=limit, owner_lane=owner_lane)


@router.post("/review/actions", response_model=SourceDiscoveryReviewActionResponse)
def source_discovery_apply_review_action(
    request: SourceDiscoveryReviewActionRequest,
    settings: Settings = Depends(get_settings),
) -> SourceDiscoveryReviewActionResponse:
    service = SourceDiscoveryService(settings)
    try:
        return service.apply_review_action(request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/reviews/apply-claims", response_model=SourceDiscoveryReviewClaimApplicationResponse)
def source_discovery_apply_review_claims(
    request: SourceDiscoveryReviewClaimApplicationRequest,
    settings: Settings = Depends(get_settings),
) -> SourceDiscoveryReviewClaimApplicationResponse:
    service = SourceDiscoveryService(settings)
    try:
        return service.apply_review_claims(request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/runtime/status", response_model=SourceDiscoveryRuntimeStatusResponse)
def source_discovery_runtime_status(
    settings: Settings = Depends(get_settings),
) -> SourceDiscoveryRuntimeStatusResponse:
    return build_runtime_status(settings)


@router.get("/runtime/services", response_model=SourceDiscoveryRuntimeServiceBundleResponse)
def source_discovery_runtime_services(
    platform_name: str | None = None,
    settings: Settings = Depends(get_settings),
) -> SourceDiscoveryRuntimeServiceBundleResponse:
    try:
        return build_runtime_service_bundle(settings, platform_name=platform_name)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/runtime/workers/{worker_name}/control", response_model=SourceDiscoveryRuntimeControlResponse)
def source_discovery_runtime_control(
    worker_name: str,
    request: SourceDiscoveryRuntimeControlRequest,
    settings: Settings = Depends(get_settings),
) -> SourceDiscoveryRuntimeControlResponse:
    try:
        return control_runtime_worker(settings, worker_name, request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
