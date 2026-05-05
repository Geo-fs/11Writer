from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from src.config.settings import Settings, get_settings
from src.services.source_discovery_service import SourceDiscoveryService
from src.services.runtime_scheduler_service import (
    build_runtime_service_bundle,
    build_runtime_status,
    control_runtime_worker,
    manage_runtime_service,
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
    SourceDiscoveryDiscoveryOverviewResponse,
    SourceDiscoveryDiscoveryQueueResponse,
    SourceDiscoveryDiscoveryRunsResponse,
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
    SourceDiscoveryKnowledgeNodeDetailResponse,
    SourceDiscoveryKnowledgeNodeListResponse,
    SourceDiscoveryKnowledgeBackfillRequest,
    SourceDiscoveryKnowledgeBackfillResponse,
    SourceDiscoveryMediaArtifactDetailResponse,
    SourceDiscoveryMediaArtifactFetchRequest,
    SourceDiscoveryMediaArtifactFetchResponse,
    SourceDiscoveryMediaArtifactListResponse,
    SourceDiscoveryMediaCompareJobRequest,
    SourceDiscoveryMediaCompareJobResponse,
    SourceDiscoveryMediaComparisonDetailResponse,
    SourceDiscoveryMediaFrameSampleJobRequest,
    SourceDiscoveryMediaFrameSampleJobResponse,
    SourceDiscoveryMediaGeolocateJobRequest,
    SourceDiscoveryMediaGeolocateJobResponse,
    SourceDiscoveryMediaGeolocationDetailResponse,
    SourceDiscoveryMediaInterpretationJobRequest,
    SourceDiscoveryMediaInterpretationJobResponse,
    SourceDiscoveryMediaOcrJobRequest,
    SourceDiscoveryMediaOcrJobResponse,
    SourceDiscoveryMediaSequenceDetailResponse,
    SourceDiscoveryRecordSourceExtractRequest,
    SourceDiscoveryRecordSourceExtractResponse,
    SourceDiscoveryReputationReversalRequest,
    SourceDiscoveryReputationReversalResponse,
    SourceDiscoverySitemapScanRequest,
    SourceDiscoverySitemapScanResponse,
    SourceDiscoveryReviewActionRequest,
    SourceDiscoveryReviewActionResponse,
    SourceDiscoveryReviewClaimApplicationRequest,
    SourceDiscoveryReviewClaimApplicationResponse,
    SourceDiscoveryReviewClaimImportRequest,
    SourceDiscoveryReviewClaimImportResponse,
    SourceDiscoveryReviewQueueResponse,
    SourceDiscoveryRuntimeControlRequest,
    SourceDiscoveryRuntimeControlResponse,
    SourceDiscoveryRuntimeServiceActionRequest,
    SourceDiscoveryRuntimeServiceActionResponse,
    SourceDiscoveryRuntimeServiceBundleResponse,
    SourceDiscoveryRuntimeStatusResponse,
    SourceDiscoverySchedulerTickRequest,
    SourceDiscoverySchedulerTickResponse,
    SourceDiscoverySeedBatchRequest,
    SourceDiscoverySeedBatchResponse,
    SourceDiscoverySeedUrlJobRequest,
    SourceDiscoverySeedUrlJobResponse,
    SourceDiscoveryStructureScanRequest,
    SourceDiscoveryStructureScanResponse,
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


@router.get("/knowledge/overview", response_model=SourceDiscoveryKnowledgeNodeListResponse)
def source_discovery_knowledge_overview(
    limit: int = 100,
    source_id: str | None = None,
    settings: Settings = Depends(get_settings),
) -> SourceDiscoveryKnowledgeNodeListResponse:
    service = SourceDiscoveryService(settings)
    return service.knowledge_overview(limit=limit, source_id=source_id)


@router.get("/knowledge/{node_id}", response_model=SourceDiscoveryKnowledgeNodeDetailResponse)
def source_discovery_knowledge_detail(
    node_id: str,
    settings: Settings = Depends(get_settings),
) -> SourceDiscoveryKnowledgeNodeDetailResponse:
    service = SourceDiscoveryService(settings)
    try:
        return service.knowledge_detail(node_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/memory/candidates", response_model=SourceDiscoveryMemory)
def source_discovery_upsert_candidate(
    seed: SourceDiscoveryCandidateSeed,
    settings: Settings = Depends(get_settings),
) -> SourceDiscoveryMemory:
    service = SourceDiscoveryService(settings)
    return service.upsert_candidate(seed)


@router.post("/seeds/bulk", response_model=SourceDiscoverySeedBatchResponse)
def source_discovery_bulk_seed_candidates(
    request: SourceDiscoverySeedBatchRequest,
    settings: Settings = Depends(get_settings),
) -> SourceDiscoverySeedBatchResponse:
    service = SourceDiscoveryService(settings)
    return service.bulk_seed_candidates(request)


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


@router.post("/jobs/structure-scan", response_model=SourceDiscoveryStructureScanResponse)
def source_discovery_run_structure_scan_job(
    request: SourceDiscoveryStructureScanRequest,
    settings: Settings = Depends(get_settings),
) -> SourceDiscoveryStructureScanResponse:
    service = SourceDiscoveryService(settings)
    return service.run_structure_scan_job(request)


@router.post("/jobs/knowledge-backfill", response_model=SourceDiscoveryKnowledgeBackfillResponse)
def source_discovery_run_knowledge_backfill_job(
    request: SourceDiscoveryKnowledgeBackfillRequest,
    settings: Settings = Depends(get_settings),
) -> SourceDiscoveryKnowledgeBackfillResponse:
    service = SourceDiscoveryService(settings)
    return service.run_knowledge_backfill_job(request)


@router.post("/jobs/feed-link-scan", response_model=SourceDiscoveryFeedLinkScanResponse)
def source_discovery_run_feed_link_scan_job(
    request: SourceDiscoveryFeedLinkScanRequest,
    settings: Settings = Depends(get_settings),
) -> SourceDiscoveryFeedLinkScanResponse:
    service = SourceDiscoveryService(settings)
    return service.run_feed_link_scan_job(request)


@router.post("/jobs/sitemap-scan", response_model=SourceDiscoverySitemapScanResponse)
def source_discovery_run_sitemap_scan_job(
    request: SourceDiscoverySitemapScanRequest,
    settings: Settings = Depends(get_settings),
) -> SourceDiscoverySitemapScanResponse:
    service = SourceDiscoveryService(settings)
    return service.run_sitemap_scan_job(request)


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


@router.get("/media/by-source/{source_id}", response_model=SourceDiscoveryMediaArtifactListResponse)
def source_discovery_media_artifacts_for_source(
    source_id: str,
    limit: int = 25,
    settings: Settings = Depends(get_settings),
) -> SourceDiscoveryMediaArtifactListResponse:
    service = SourceDiscoveryService(settings)
    try:
        return service.list_media_artifacts(source_id, limit=limit)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/media/artifacts/{artifact_id}", response_model=SourceDiscoveryMediaArtifactDetailResponse)
def source_discovery_media_artifact_detail(
    artifact_id: str,
    limit: int = 10,
    settings: Settings = Depends(get_settings),
) -> SourceDiscoveryMediaArtifactDetailResponse:
    service = SourceDiscoveryService(settings)
    try:
        return service.media_artifact_detail(artifact_id, limit=limit)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/media/comparisons/{comparison_id}", response_model=SourceDiscoveryMediaComparisonDetailResponse)
def source_discovery_media_comparison_detail(
    comparison_id: str,
    settings: Settings = Depends(get_settings),
) -> SourceDiscoveryMediaComparisonDetailResponse:
    service = SourceDiscoveryService(settings)
    try:
        return service.media_comparison_detail(comparison_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/media/geolocations/{geolocation_run_id}", response_model=SourceDiscoveryMediaGeolocationDetailResponse)
def source_discovery_media_geolocation_detail(
    geolocation_run_id: str,
    settings: Settings = Depends(get_settings),
) -> SourceDiscoveryMediaGeolocationDetailResponse:
    service = SourceDiscoveryService(settings)
    try:
        return service.media_geolocation_detail(geolocation_run_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/media/sequences/{sequence_id}", response_model=SourceDiscoveryMediaSequenceDetailResponse)
def source_discovery_media_sequence_detail(
    sequence_id: str,
    limit: int = 24,
    settings: Settings = Depends(get_settings),
) -> SourceDiscoveryMediaSequenceDetailResponse:
    service = SourceDiscoveryService(settings)
    try:
        return service.media_sequence_detail(sequence_id, limit=limit)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/jobs/media-artifact-fetch", response_model=SourceDiscoveryMediaArtifactFetchResponse)
def source_discovery_run_media_artifact_fetch_job(
    request: SourceDiscoveryMediaArtifactFetchRequest,
    settings: Settings = Depends(get_settings),
) -> SourceDiscoveryMediaArtifactFetchResponse:
    service = SourceDiscoveryService(settings)
    try:
        return service.run_media_artifact_fetch_job(request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/jobs/media-compare", response_model=SourceDiscoveryMediaCompareJobResponse)
def source_discovery_run_media_compare_job(
    request: SourceDiscoveryMediaCompareJobRequest,
    settings: Settings = Depends(get_settings),
) -> SourceDiscoveryMediaCompareJobResponse:
    service = SourceDiscoveryService(settings)
    try:
        return service.run_media_compare_job(request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/jobs/media-ocr", response_model=SourceDiscoveryMediaOcrJobResponse)
def source_discovery_run_media_ocr_job(
    request: SourceDiscoveryMediaOcrJobRequest,
    settings: Settings = Depends(get_settings),
) -> SourceDiscoveryMediaOcrJobResponse:
    service = SourceDiscoveryService(settings)
    try:
        return service.run_media_ocr_job(request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/jobs/media-interpret", response_model=SourceDiscoveryMediaInterpretationJobResponse)
def source_discovery_run_media_interpretation_job(
    request: SourceDiscoveryMediaInterpretationJobRequest,
    settings: Settings = Depends(get_settings),
) -> SourceDiscoveryMediaInterpretationJobResponse:
    service = SourceDiscoveryService(settings)
    try:
        return service.run_media_interpretation_job(request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/jobs/media-geolocate", response_model=SourceDiscoveryMediaGeolocateJobResponse)
def source_discovery_run_media_geolocation_job(
    request: SourceDiscoveryMediaGeolocateJobRequest,
    settings: Settings = Depends(get_settings),
) -> SourceDiscoveryMediaGeolocateJobResponse:
    service = SourceDiscoveryService(settings)
    try:
        return service.run_media_geolocation_job(request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/jobs/media-frame-sample", response_model=SourceDiscoveryMediaFrameSampleJobResponse)
def source_discovery_run_media_frame_sample_job(
    request: SourceDiscoveryMediaFrameSampleJobRequest,
    settings: Settings = Depends(get_settings),
) -> SourceDiscoveryMediaFrameSampleJobResponse:
    service = SourceDiscoveryService(settings)
    try:
        return service.run_media_frame_sample_job(request)
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


@router.get("/discovery/overview", response_model=SourceDiscoveryDiscoveryOverviewResponse)
def source_discovery_discovery_overview(
    limit: int = 100,
    settings: Settings = Depends(get_settings),
) -> SourceDiscoveryDiscoveryOverviewResponse:
    service = SourceDiscoveryService(settings)
    return service.discovery_overview(limit=limit)


@router.get("/discovery/queue", response_model=SourceDiscoveryDiscoveryQueueResponse)
def source_discovery_discovery_queue(
    limit: int = 100,
    eligible_only: bool = False,
    seed_family: str | None = None,
    platform_family: str | None = None,
    next_action: str | None = None,
    owner_lane: str | None = None,
    priority: str | None = None,
    policy_state: str | None = None,
    lifecycle_state: str | None = None,
    settings: Settings = Depends(get_settings),
) -> SourceDiscoveryDiscoveryQueueResponse:
    service = SourceDiscoveryService(settings)
    return service.discovery_queue(
        limit=limit,
        eligible_only=eligible_only,
        seed_family=seed_family,
        platform_family=platform_family,
        next_action=next_action,
        owner_lane=owner_lane,
        priority=priority,
        policy_state=policy_state,
        lifecycle_state=lifecycle_state,
    )


@router.get("/discovery/runs", response_model=SourceDiscoveryDiscoveryRunsResponse)
def source_discovery_discovery_runs(
    limit: int = 50,
    settings: Settings = Depends(get_settings),
) -> SourceDiscoveryDiscoveryRunsResponse:
    service = SourceDiscoveryService(settings)
    return service.discovery_runs(limit=limit)


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


@router.post("/reviews/import-claims", response_model=SourceDiscoveryReviewClaimImportResponse)
def source_discovery_import_review_claims(
    request: SourceDiscoveryReviewClaimImportRequest,
    settings: Settings = Depends(get_settings),
) -> SourceDiscoveryReviewClaimImportResponse:
    service = SourceDiscoveryService(settings)
    try:
        return service.import_review_claims(request)
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


@router.post("/runtime/services/{worker_name}/actions", response_model=SourceDiscoveryRuntimeServiceActionResponse)
def source_discovery_runtime_service_action(
    worker_name: str,
    request: SourceDiscoveryRuntimeServiceActionRequest,
    settings: Settings = Depends(get_settings),
) -> SourceDiscoveryRuntimeServiceActionResponse:
    try:
        return manage_runtime_service(settings, worker_name, request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
