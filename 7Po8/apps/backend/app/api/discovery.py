from datetime import datetime
from typing import Literal

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from sqlmodel import Session

from app.api.deps import get_session
from app.models.common import SourceCheckStatus, SourceLifecycleState
from app.schemas.discovered_source import (
    ApproveSourceResponse,
    BatchSourceCheckResponse,
    DiscoveredSourceRead,
    DiscoveredSourceUpdate,
    DiscoverSourcesRequest,
    DiscoverSourcesResponse,
    SourceCheckRead,
)
from app.services.discovery_service import (
    approve_discovered_source,
    get_discovered_source_or_none,
    list_discovered_sources_for_wave,
    run_discovery_for_wave,
    update_discovered_source,
)
from app.services.source_check_service import (
    check_discovered_source,
    check_sources_for_wave,
    list_checks_for_source,
)
from app.services.source_policy_service import (
    reevaluate_discovered_source,
    reevaluate_discovered_sources_for_wave,
    serialize_discovered_source,
)
from app.services.wave_service import get_wave_or_none

wave_router = APIRouter(prefix="/waves/{wave_id}", tags=["discovery"])
root_router = APIRouter(prefix="/discovered-sources", tags=["discovery"])


@wave_router.post(
    "/discover-sources",
    response_model=DiscoverSourcesResponse,
    status_code=status.HTTP_200_OK,
)
def post_discover_sources(
    wave_id: int,
    payload: DiscoverSourcesRequest | None = Body(default=None),
    session: Session = Depends(get_session),
) -> DiscoverSourcesResponse:
    wave = get_wave_or_none(session, wave_id)
    if wave is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wave not found")

    discovered_count, deduped_count = run_discovery_for_wave(
        session,
        wave,
        seed_urls=[str(url) for url in (payload.seed_urls if payload else [])],
    )
    return DiscoverSourcesResponse(
        wave_id=wave_id,
        discovered_count=discovered_count,
        deduped_count=deduped_count,
    )


@wave_router.get(
    "/discovered-sources",
    response_model=list[DiscoveredSourceRead],
    status_code=status.HTTP_200_OK,
)
def get_discovered_sources(
    wave_id: int,
    limit: int = Query(default=200, ge=1, le=300),
    status: SourceLifecycleState | None = None,
    source_type: str | None = None,
    min_relevance_score: float | None = Query(default=None, ge=0.0, le=1.0),
    min_stability_score: float | None = Query(default=None, ge=0.0, le=1.0),
    parent_domain: str | None = None,
    approved_only: bool = False,
    new_only: bool = False,
    sort: Literal[
        "newest",
        "oldest",
        "relevance_desc",
        "relevance_asc",
        "stability_desc",
        "stability_asc",
    ] = "relevance_desc",
    session: Session = Depends(get_session),
) -> list[DiscoveredSourceRead]:
    wave = get_wave_or_none(session, wave_id)
    if wave is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wave not found")
    sources = list_discovered_sources_for_wave(
        session,
        wave_id,
        limit=limit,
        status=status,
        source_type=source_type,
        min_relevance_score=min_relevance_score,
        min_stability_score=min_stability_score,
        parent_domain=parent_domain,
        approved_only=approved_only,
        new_only=new_only,
        sort=sort,
    )
    return [serialize_discovered_source(session, source) for source in sources]


@root_router.patch(
    "/{source_id}",
    response_model=DiscoveredSourceRead,
    status_code=status.HTTP_200_OK,
)
def patch_discovered_source(
    source_id: int,
    payload: DiscoveredSourceUpdate,
    session: Session = Depends(get_session),
) -> DiscoveredSourceRead:
    source = get_discovered_source_or_none(session, source_id)
    if source is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Discovered source not found",
        )
    updated = update_discovered_source(session, source, **payload.model_dump(exclude_unset=True))
    return serialize_discovered_source(session, updated)


@root_router.post(
    "/{source_id}/approve",
    response_model=ApproveSourceResponse,
    status_code=status.HTTP_200_OK,
)
def post_approve_discovered_source(
    source_id: int,
    session: Session = Depends(get_session),
) -> ApproveSourceResponse:
    source = get_discovered_source_or_none(session, source_id)
    if source is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Discovered source not found",
        )
    try:
        connector_id = approve_discovered_source(session, source)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return ApproveSourceResponse(
        source_id=source.id,
        status=source.status,
        connector_id=connector_id,
    )


@root_router.post(
    "/{source_id}/check",
    response_model=SourceCheckRead,
    status_code=status.HTTP_200_OK,
)
def post_source_check(
    source_id: int,
    session: Session = Depends(get_session),
) -> SourceCheckRead:
    source = get_discovered_source_or_none(session, source_id)
    if source is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Discovered source not found",
        )
    return check_discovered_source(session, source)


@root_router.post(
    "/{source_id}/reevaluate-lifecycle",
    response_model=DiscoveredSourceRead,
    status_code=status.HTTP_200_OK,
)
def post_reevaluate_discovered_source_lifecycle(
    source_id: int,
    session: Session = Depends(get_session),
) -> DiscoveredSourceRead:
    source = get_discovered_source_or_none(session, source_id)
    if source is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Discovered source not found",
        )
    reevaluate_discovered_source(session, source, trigger="manual_review")
    return serialize_discovered_source(session, source)


@root_router.get(
    "/{source_id}/checks",
    response_model=list[SourceCheckRead],
    status_code=status.HTTP_200_OK,
)
def get_source_checks(
    source_id: int,
    limit: int = Query(default=20, ge=1, le=200),
    status: SourceCheckStatus | None = None,
    reachable: bool | None = None,
    parseable: bool | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    content_type: str | None = None,
    sort: Literal["newest", "oldest"] = "newest",
    session: Session = Depends(get_session),
) -> list[SourceCheckRead]:
    source = get_discovered_source_or_none(session, source_id)
    if source is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Discovered source not found",
        )
    return list_checks_for_source(
        session,
        source_id,
        limit=limit,
        status=status,
        reachable=reachable,
        parseable=parseable,
        start_date=start_date,
        end_date=end_date,
        content_type=content_type,
        sort=sort,
    )


@wave_router.post(
    "/check-discovered-sources",
    response_model=BatchSourceCheckResponse,
    status_code=status.HTTP_200_OK,
)
def post_batch_source_checks(
    wave_id: int,
    limit: int = Query(default=100, ge=1, le=300),
    session: Session = Depends(get_session),
) -> BatchSourceCheckResponse:
    wave = get_wave_or_none(session, wave_id)
    if wave is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wave not found")

    checks = check_sources_for_wave(session, wave_id, limit=limit)
    success_count = sum(1 for row in checks if row.status == SourceCheckStatus.SUCCESS)
    failed_count = sum(1 for row in checks if row.status == SourceCheckStatus.FAILED)
    skipped_count = sum(1 for row in checks if row.status == SourceCheckStatus.SKIPPED)
    return BatchSourceCheckResponse(
        wave_id=wave_id,
        checked_count=len(checks),
        success_count=success_count,
        failed_count=failed_count,
        skipped_count=skipped_count,
    )


@wave_router.post(
    "/reevaluate-sources",
    status_code=status.HTTP_200_OK,
)
def post_reevaluate_wave_sources(
    wave_id: int,
    session: Session = Depends(get_session),
) -> dict[str, int | str]:
    wave = get_wave_or_none(session, wave_id)
    if wave is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wave not found")
    result = reevaluate_discovered_sources_for_wave(session, wave_id)
    return {
        "domain": result.domain,
        "evaluated_count": result.evaluated_count,
        "changed_count": result.changed_count,
        "auto_approved_count": result.auto_approved_count,
        "blocked_count": result.blocked_count,
        "reviewable_count": result.reviewable_count,
        "preserved_count": result.preserved_count,
    }
