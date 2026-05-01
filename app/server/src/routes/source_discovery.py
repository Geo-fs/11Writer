from __future__ import annotations

from fastapi import APIRouter, Depends

from src.config.settings import Settings, get_settings
from src.services.source_discovery_service import SourceDiscoveryService
from src.types.source_discovery import (
    SourceDiscoveryCandidateSeed,
    SourceDiscoveryClaimOutcomeRequest,
    SourceDiscoveryClaimOutcomeResponse,
    SourceDiscoveryMemory,
    SourceDiscoveryMemoryOverviewResponse,
    SourceDiscoverySeedUrlJobRequest,
    SourceDiscoverySeedUrlJobResponse,
)

router = APIRouter(prefix="/api/source-discovery", tags=["source-discovery"])


@router.get("/memory/overview", response_model=SourceDiscoveryMemoryOverviewResponse)
def source_discovery_memory_overview(
    limit: int = 100,
    settings: Settings = Depends(get_settings),
) -> SourceDiscoveryMemoryOverviewResponse:
    service = SourceDiscoveryService(settings)
    return service.overview(limit=limit)


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
