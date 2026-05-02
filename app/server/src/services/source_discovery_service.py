from __future__ import annotations

import asyncio
import hashlib
import json
import re
from datetime import datetime, timedelta, timezone
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qsl, urlencode, urljoin, urlparse, urlunparse
from urllib.request import Request, urlopen

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.config.settings import Settings
from src.services.content_extraction import extract_article_snapshot_from_html, extract_social_metadata_from_html
from src.services.data_ai_multi_feed_service import DataAiMultiFeedQuery, DataAiMultiFeedService
from src.services.rss_feed_service import parse_feed_document
from src.services.wave_llm_service import WaveLlmService
from src.source_discovery.db import session_scope
from src.source_discovery.models import (
    SourceClaimOutcomeORM,
    SourceContentSnapshotORM,
    RuntimeSchedulerRunORM,
    RuntimeSchedulerWorkerORM,
    SourceReviewClaimApplicationORM,
    SourceDiscoveryJobORM,
    SourceHealthCheckORM,
    SourceMemoryORM,
    SourceReputationEventORM,
    SourceReviewActionORM,
    SourceSchedulerTickORM,
    SourceWaveFitORM,
)
from src.types.source_discovery import (
    SourceDiscoveryCandidateSeed,
    SourceDiscoveryCatalogScanRequest,
    SourceDiscoveryCatalogScanResponse,
    SourceDiscoveryClaimOutcomeRequest,
    SourceDiscoveryClaimOutcomeSummary,
    SourceDiscoveryClaimOutcomeResponse,
    SourceDiscoveryArticleFetchRequest,
    SourceDiscoveryArticleFetchResponse,
    SourceDiscoveryContentSnapshotRequest,
    SourceDiscoveryContentSnapshotResponse,
    SourceDiscoveryContentSnapshotSummary,
    SourceDiscoveryFeedLinkScanRequest,
    SourceDiscoveryFeedLinkScanResponse,
    SourceDiscoveryExpansionJobRequest,
    SourceDiscoveryExpansionJobResponse,
    SourceDiscoveryHealthCheckRequest,
    SourceDiscoveryHealthCheckResponse,
    SourceDiscoveryHealthCheckSummary,
    SourceDiscoveryJobSummary,
    SourceDiscoveryMemory,
    SourceDiscoveryMemoryDetailResponse,
    SourceDiscoveryMemoryExportPacket,
    SourceDiscoveryMemoryExportResponse,
    SourceDiscoveryMemoryListResponse,
    SourceDiscoveryMemoryOverviewResponse,
    SourceDiscoveryRecordSourceExtractRequest,
    SourceDiscoveryRecordSourceExtractResponse,
    SourceDiscoveryReputationEventSummary,
    SourceDiscoveryReputationReversalRequest,
    SourceDiscoveryReputationReversalResponse,
    SourceDiscoveryReviewActionRequest,
    SourceDiscoveryReviewActionResponse,
    SourceDiscoveryReviewActionSummary,
    SourceDiscoveryReviewClaimApplicationRequest,
    SourceDiscoveryReviewClaimApplicationResponse,
    SourceDiscoveryReviewClaimApplicationSummary,
    SourceDiscoveryReviewQueueItem,
    SourceDiscoveryReviewQueueResponse,
    SourceDiscoverySocialMetadataJobRequest,
    SourceDiscoverySocialMetadataJobResponse,
    SourceDiscoverySocialMetadataSummary,
    SourceDiscoverySchedulerTickRequest,
    SourceDiscoverySchedulerTickResponse,
    SourceDiscoverySeedUrlJobRequest,
    SourceDiscoverySeedUrlJobResponse,
    SourceDiscoveryWaveFit,
)
from src.types.wave_monitor import WaveLlmExecutionSummary, WaveLlmInterpretationTaskRequest, WaveLlmTaskExecuteRequest
from src.wave_monitor.db import session_scope as wave_session_scope
from src.wave_monitor.models import WaveLlmReviewORM, WaveLlmTaskORM, WaveMonitorORM, WaveRecordORM


SOURCE_DISCOVERY_CAVEATS = [
    "Source reputation is learned from evidence over time; it is not proof that every future item is correct.",
    "Wave fit is separate from correctness: a source can be accurate but irrelevant to a specific wave.",
    "Discovered sources are not implemented or scheduled automatically.",
]

HTTP_USER_AGENT = "11Writer/SourceDiscovery (+https://local.11writer.invalid; public-no-auth-source-checks)"
MAX_FETCH_BYTES = 512_000
LIVE_NETWORK_LLM_PROVIDERS = {"openai", "openrouter", "anthropic", "xai", "google", "openclaw", "ollama"}

OUTCOME_SCORE_DELTAS = {
    "confirmed": 0.06,
    "contradicted": -0.10,
    "corrected": -0.03,
    "outdated": -0.02,
    "unresolved": 0.0,
    "not_applicable": 0.0,
}


class SourceDiscoveryService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def overview(self, *, limit: int = 100) -> SourceDiscoveryMemoryOverviewResponse:
        with session_scope(self._settings.source_discovery_database_url) as session:
            memories = list(
                session.scalars(
                    select(SourceMemoryORM)
                    .order_by(SourceMemoryORM.global_reputation_score.desc(), SourceMemoryORM.source_id)
                    .limit(limit)
                )
            )
            fits = list(
                session.scalars(
                    select(SourceWaveFitORM)
                    .order_by(SourceWaveFitORM.wave_id, SourceWaveFitORM.fit_score.desc())
                    .limit(limit * 3)
                )
            )
            jobs = list(
                session.scalars(
                    select(SourceDiscoveryJobORM)
                    .order_by(SourceDiscoveryJobORM.started_at.desc())
                    .limit(20)
                )
            )
            events = list(
                session.scalars(
                    select(SourceReputationEventORM)
                    .order_by(SourceReputationEventORM.created_at.desc())
                    .limit(20)
                )
            )
            return SourceDiscoveryMemoryOverviewResponse(
                metadata={
                    "source": "source-discovery-memory",
                    "storageMode": "persistent-sqlite",
                    "reputationMode": "claim-outcome-v1",
                    "count": len(memories),
                },
                memories=[_serialize_memory(memory) for memory in memories],
                wave_fits=[_serialize_wave_fit(fit) for fit in fits],
                recent_jobs=[_serialize_job(job) for job in jobs],
                recent_reputation_events=[_serialize_reputation_event(event) for event in events],
                caveats=SOURCE_DISCOVERY_CAVEATS,
            )

    def list_memories(
        self,
        *,
        limit: int = 100,
        owner_lane: str | None = None,
        source_class: str | None = None,
        lifecycle_state: str | None = None,
    ) -> SourceDiscoveryMemoryListResponse:
        with session_scope(self._settings.source_discovery_database_url) as session:
            stmt = select(SourceMemoryORM).order_by(SourceMemoryORM.last_seen_at.desc(), SourceMemoryORM.source_id)
            if owner_lane:
                stmt = stmt.where(SourceMemoryORM.owner_lane == owner_lane)
            if source_class:
                stmt = stmt.where(SourceMemoryORM.source_class == source_class)
            if lifecycle_state:
                stmt = stmt.where(SourceMemoryORM.lifecycle_state == lifecycle_state)
            memories = list(session.scalars(stmt.limit(max(0, limit))))
            return SourceDiscoveryMemoryListResponse(
                metadata={
                    "source": "source-discovery-memory-list",
                    "count": len(memories),
                    "ownerLane": owner_lane,
                    "sourceClass": source_class,
                    "lifecycleState": lifecycle_state,
                },
                memories=[_serialize_memory(memory) for memory in memories],
                caveats=SOURCE_DISCOVERY_CAVEATS,
            )

    def memory_detail(self, source_id: str, *, limit: int = 25) -> SourceDiscoveryMemoryDetailResponse:
        with session_scope(self._settings.source_discovery_database_url) as session:
            memory = session.get(SourceMemoryORM, source_id)
            if memory is None:
                raise ValueError(f"Unknown source_id: {source_id}")
            return _build_memory_detail_response(session, memory, limit=limit)

    def export_memory_packet(self, source_id: str, *, limit: int = 25) -> SourceDiscoveryMemoryExportResponse:
        with session_scope(self._settings.source_discovery_database_url) as session:
            memory = session.get(SourceMemoryORM, source_id)
            if memory is None:
                raise ValueError(f"Unknown source_id: {source_id}")
            detail = _build_memory_detail_response(session, memory, limit=limit)
            return SourceDiscoveryMemoryExportResponse(
                packet=SourceDiscoveryMemoryExportPacket(
                    export_type="source_packet_v1",
                    generated_at=_utc_now(),
                    memory=detail.memory,
                    wave_fits=detail.wave_fits,
                    snapshots=detail.snapshots,
                    health_checks=detail.health_checks,
                    review_actions=detail.review_actions,
                    reputation_events=detail.reputation_events,
                    claim_outcomes=detail.claim_outcomes,
                    caveats=detail.caveats + [
                        "Export packet is a source-review handoff artifact, not proof that the source is true or production-ready.",
                    ],
                ),
                caveats=SOURCE_DISCOVERY_CAVEATS,
            )

    def upsert_candidate(self, seed: SourceDiscoveryCandidateSeed) -> SourceDiscoveryMemory:
        with session_scope(self._settings.source_discovery_database_url) as session:
            memory = _upsert_candidate_row(session, seed, now=_utc_now())
            session.flush()
            return _serialize_memory(memory)

    def upsert_candidates(self, seeds: list[SourceDiscoveryCandidateSeed]) -> list[SourceDiscoveryMemory]:
        with session_scope(self._settings.source_discovery_database_url) as session:
            now = _utc_now()
            memories = [_upsert_candidate_row(session, seed, now=now) for seed in seeds]
            session.flush()
            return [_serialize_memory(memory) for memory in memories]

    def record_claim_outcome(
        self,
        request: SourceDiscoveryClaimOutcomeRequest,
    ) -> SourceDiscoveryClaimOutcomeResponse:
        with session_scope(self._settings.source_discovery_database_url) as session:
            now = _utc_now()
            memory = session.get(SourceMemoryORM, request.source_id)
            if memory is None:
                memory = _upsert_candidate_row(
                    session,
                    SourceDiscoveryCandidateSeed(
                        source_id=request.source_id,
                        title=request.source_id,
                        url="unknown",
                        parent_domain="unknown",
                        source_type="unknown",
                        source_class="unknown",
                        wave_id=request.wave_id,
                        lifecycle_state="discovered",
                        caveats=["Memory was created from a claim outcome before candidate metadata existed."],
                    ),
                    now=now,
                )

            observed_at = request.observed_at or now
            session.add(
                SourceClaimOutcomeORM(
                    source_id=request.source_id,
                    wave_id=request.wave_id,
                    claim_text=request.claim_text,
                    claim_type=request.claim_type,
                    outcome=request.outcome,
                    evidence_basis=request.evidence_basis,
                    observed_at=observed_at,
                    assessed_at=now,
                    corroborating_source_ids_json=json.dumps(request.corroborating_source_ids),
                    contradiction_source_ids_json=json.dumps(request.contradiction_source_ids),
                    caveats_json=json.dumps(request.caveats),
                )
            )
            _apply_claim_outcome(session, memory, request, now)
            fits = _fits_for_source(session, request.source_id)
            session.flush()
            return SourceDiscoveryClaimOutcomeResponse(
                memory=_serialize_memory(memory),
                wave_fits=[_serialize_wave_fit(fit) for fit in fits],
                caveats=SOURCE_DISCOVERY_CAVEATS,
            )

    def run_seed_url_job(self, request: SourceDiscoverySeedUrlJobRequest) -> SourceDiscoverySeedUrlJobResponse:
        now = _utc_now()
        parsed = urlparse(request.seed_url)
        job_id = f"source-discovery-job:{_safe_id(request.seed_url)}:{_compact_timestamp(now)}"
        caveats = list(request.caveats)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            job = SourceDiscoveryJobORM(
                job_id=job_id,
                job_type="seed_url",
                status="rejected",
                seed_url=request.seed_url,
                wave_id=request.wave_id,
                wave_title=request.wave_title,
                discovered_source_ids_json=json.dumps([]),
                rejected_reason="Seed URL must be an absolute http(s) URL.",
                request_budget=request.request_budget,
                used_requests=0,
                started_at=now,
                finished_at=now,
                caveats_json=json.dumps(["Rejected before network access or candidate creation."]),
            )
            with session_scope(self._settings.source_discovery_database_url) as session:
                session.add(job)
                session.flush()
                return SourceDiscoverySeedUrlJobResponse(
                    job=_serialize_job(job),
                    memory=None,
                    wave_fits=[],
                    caveats=SOURCE_DISCOVERY_CAVEATS,
                )

        classification = _classify_seed_url(request.seed_url)
        source_id = request.source_id or f"source:{_safe_id(parsed.netloc + parsed.path)[:120]}"
        title = request.title or parsed.netloc
        seed = SourceDiscoveryCandidateSeed(
            source_id=source_id,
            title=title,
            url=request.seed_url,
            parent_domain=parsed.netloc,
            source_type=classification["source_type"],
            source_class=classification["source_class"],  # type: ignore[arg-type]
            wave_id=request.wave_id,
            wave_title=request.wave_title,
            lifecycle_state="candidate",
            source_health="unknown",
            policy_state=classification["policy_state"],
            access_result=classification["access_result"],
            machine_readable_result=classification["machine_readable_result"],
            wave_fit_score=0.55 if request.wave_id else 0.5,
            relevance_basis=[
                request.discovery_reason,
                "Seed URL job created a candidate only; no automatic polling was enabled.",
            ],
            caveats=caveats + classification["caveats"],
        )
        with session_scope(self._settings.source_discovery_database_url) as session:
            memory = _upsert_candidate_row(session, seed, now=now)
            job = SourceDiscoveryJobORM(
                job_id=job_id,
                job_type="seed_url",
                status="completed",
                seed_url=request.seed_url,
                wave_id=request.wave_id,
                wave_title=request.wave_title,
                discovered_source_ids_json=json.dumps([memory.source_id]),
                rejected_reason=None,
                request_budget=max(0, request.request_budget),
                used_requests=0,
                started_at=now,
                finished_at=now,
                caveats_json=json.dumps([
                    "Seed URL job is classification-only in this slice; no deep crawl or polling was run.",
                    "Candidate reputation remains thin until claim outcomes and source health accumulate.",
                ]),
            )
            session.add(job)
            session.flush()
            fits = _fits_for_source(session, memory.source_id)
            return SourceDiscoverySeedUrlJobResponse(
                job=_serialize_job(job),
                memory=_serialize_memory(memory),
                wave_fits=[_serialize_wave_fit(fit) for fit in fits],
                caveats=SOURCE_DISCOVERY_CAVEATS,
            )

    def check_source_health(self, request: SourceDiscoveryHealthCheckRequest) -> SourceDiscoveryHealthCheckResponse:
        now = _utc_now()
        check_id = f"source-health:{_safe_id(request.source_id)}:{_compact_timestamp(now)}"
        with session_scope(self._settings.source_discovery_database_url) as session:
            memory = session.get(SourceMemoryORM, request.source_id)
            if memory is None:
                raise ValueError(f"Unknown source_id: {request.source_id}")

            used_requests = 0
            http_status: int | None = None
            content_type: str | None = None
            error_summary: str | None = None
            caveats = list(request.caveats)
            status = "metadata_only"
            access_result = memory.access_result
            machine_readable_result = memory.machine_readable_result
            source_health = memory.source_health
            source_health_score = memory.source_health_score
            health_check_fail_count = memory.health_check_fail_count

            parsed = urlparse(memory.url)
            if parsed.scheme not in {"http", "https"} or not parsed.netloc:
                status = "rejected"
                access_result = "blocked"
                source_health = "blocked"
                source_health_score = 0.0
                health_check_fail_count += 1
                error_summary = "Health checks require an absolute http(s) URL."
                caveats.append("Rejected before network access because source URL is not http(s).")
            elif request.request_budget <= 0:
                caveats.append("Health check ran in metadata-only scheduler mode; no network request was used.")
            else:
                used_requests = 1
                try:
                    fetched = _fetch_url(memory.url, method="GET", max_bytes=4096)
                    http_status = fetched["status"]
                    content_type = fetched["content_type"]
                    status = "completed"
                    access_result = "reachable" if 200 <= (http_status or 0) < 400 else "degraded"
                    machine_readable_result = _machine_readable_from_content_type(content_type, memory.url)
                    source_health = "healthy" if access_result == "reachable" else "degraded"
                    source_health_score = _health_score_for_result(memory.source_class, source_health)
                    health_check_fail_count = 0
                except HTTPError as exc:
                    http_status = exc.code
                    status = "failed"
                    source_health = "rate_limited" if exc.code == 429 else "degraded"
                    access_result = "rate_limited" if exc.code == 429 else "http_error"
                    source_health_score = _health_score_for_result(memory.source_class, source_health)
                    health_check_fail_count += 1
                    error_summary = f"HTTP {exc.code}"
                except (URLError, TimeoutError, OSError) as exc:
                    status = "failed"
                    source_health = "unreachable"
                    access_result = "network_error"
                    source_health_score = _health_score_for_result(memory.source_class, source_health)
                    health_check_fail_count += 1
                    error_summary = str(exc)[:300]

            next_check_after = request.next_check_after or _next_health_check_after(
                source_class=memory.source_class,
                status=status,
                source_health=source_health,
                now=now,
                fail_count=health_check_fail_count,
            )
            memory.source_health = source_health
            memory.source_health_score = source_health_score
            memory.access_result = access_result
            memory.machine_readable_result = machine_readable_result
            memory.last_seen_at = now
            memory.next_check_at = next_check_after
            memory.health_check_fail_count = health_check_fail_count
            memory.timeliness_score = _timeliness_after_health_check(
                source_class=memory.source_class,
                current_score=memory.timeliness_score,
                source_health=source_health,
                status=status,
            )
            memory.caveats_json = json.dumps(sorted(set(_loads_list(memory.caveats_json) + caveats)))
            health_check = SourceHealthCheckORM(
                check_id=check_id,
                source_id=memory.source_id,
                url=memory.url,
                status=status,
                http_status=http_status,
                content_type=content_type,
                access_result=access_result,
                machine_readable_result=machine_readable_result,
                source_health=source_health,
                source_health_score=source_health_score,
                request_budget=max(0, request.request_budget),
                used_requests=used_requests,
                checked_at=now,
                next_check_after=next_check_after,
                error_summary=error_summary,
                caveats_json=json.dumps(caveats),
            )
            session.add(health_check)
            session.flush()
            return SourceDiscoveryHealthCheckResponse(
                health_check=_serialize_health_check(health_check),
                memory=_serialize_memory(memory),
                caveats=SOURCE_DISCOVERY_CAVEATS,
            )

    def run_expansion_job(self, request: SourceDiscoveryExpansionJobRequest) -> SourceDiscoveryExpansionJobResponse:
        now = _utc_now()
        parsed = urlparse(request.seed_url)
        job_id = f"source-expansion:{_safe_id(request.seed_url)}:{_compact_timestamp(now)}"
        caveats = list(request.caveats)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            job = SourceDiscoveryJobORM(
                job_id=job_id,
                job_type="bounded_expansion",
                status="rejected",
                seed_url=request.seed_url,
                wave_id=request.wave_id,
                wave_title=request.wave_title,
                discovered_source_ids_json=json.dumps([]),
                rejected_reason="Seed URL must be an absolute http(s) URL.",
                request_budget=request.request_budget,
                used_requests=0,
                started_at=now,
                finished_at=now,
                caveats_json=json.dumps(["Rejected before network access or candidate creation."]),
            )
            with session_scope(self._settings.source_discovery_database_url) as session:
                session.add(job)
                session.flush()
                return SourceDiscoveryExpansionJobResponse(
                    job=_serialize_job(job),
                    memories=[],
                    caveats=SOURCE_DISCOVERY_CAVEATS,
                )

        used_requests = 0
        raw_text = request.fixture_text or ""
        if not raw_text and request.request_budget > 0:
            try:
                fetched = _fetch_url(request.seed_url, method="GET", max_bytes=MAX_FETCH_BYTES)
                raw_text = fetched["body"]
                used_requests = 1
            except (HTTPError, URLError, TimeoutError, OSError) as exc:
                caveats.append(f"Expansion fetch failed; only supplied candidate URLs were used: {str(exc)[:180]}")

        discovered_urls = _bounded_candidate_urls(
            request.seed_url,
            request.candidate_urls + _extract_candidate_links(request.seed_url, raw_text),
            max_discovered=max(0, request.max_discovered),
        )
        seeds: list[SourceDiscoveryCandidateSeed] = []
        for discovered_url in discovered_urls:
            child = urlparse(discovered_url)
            classification = _classify_seed_url(discovered_url)
            seeds.append(
                SourceDiscoveryCandidateSeed(
                    source_id=f"source:{_safe_id(child.netloc + child.path)[:120]}",
                    title=child.netloc,
                    url=discovered_url,
                    parent_domain=child.netloc,
                    source_type=classification["source_type"],
                    source_class=classification["source_class"],  # type: ignore[arg-type]
                    wave_id=request.wave_id,
                    wave_title=request.wave_title,
                    lifecycle_state="candidate",
                    source_health="unknown",
                    policy_state="manual_review",
                    access_result="unknown",
                    machine_readable_result=classification["machine_readable_result"],
                    wave_fit_score=0.52 if request.wave_id else 0.5,
                    relevance_basis=[
                        request.discovery_reason,
                        "Bounded expansion discovered this URL but did not poll or trust it.",
                    ],
                    caveats=caveats + classification["caveats"] + [
                        "Expansion jobs create review candidates only; child sources require health checks before scheduling.",
                    ],
                )
            )

        with session_scope(self._settings.source_discovery_database_url) as session:
            memories = [_upsert_candidate_row(session, seed, now=now) for seed in seeds]
            job = SourceDiscoveryJobORM(
                job_id=job_id,
                job_type="bounded_expansion",
                status="completed",
                seed_url=request.seed_url,
                wave_id=request.wave_id,
                wave_title=request.wave_title,
                discovered_source_ids_json=json.dumps([memory.source_id for memory in memories]),
                rejected_reason=None,
                request_budget=max(0, request.request_budget),
                used_requests=used_requests,
                started_at=now,
                finished_at=now,
                caveats_json=json.dumps(caveats + [
                    "Bounded expansion is not broad crawling; discovered URLs were not fetched as child sources.",
                ]),
            )
            session.add(job)
            session.flush()
            return SourceDiscoveryExpansionJobResponse(
                job=_serialize_job(job),
                memories=[_serialize_memory(memory) for memory in memories],
                caveats=SOURCE_DISCOVERY_CAVEATS,
            )

    def run_feed_link_scan_job(
        self,
        request: SourceDiscoveryFeedLinkScanRequest,
    ) -> SourceDiscoveryFeedLinkScanResponse:
        now = _utc_now()
        parsed = urlparse(request.feed_url)
        job_id = f"source-feed-scan:{_safe_id(request.feed_url)}:{_compact_timestamp(now)}"
        caveats = list(request.caveats)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            job = SourceDiscoveryJobORM(
                job_id=job_id,
                job_type="feed_link_scan",
                status="rejected",
                seed_url=request.feed_url,
                wave_id=request.wave_id,
                wave_title=request.wave_title,
                discovered_source_ids_json=json.dumps([]),
                rejected_reason="Feed URL must be an absolute http(s) URL.",
                request_budget=request.request_budget,
                used_requests=0,
                started_at=now,
                finished_at=now,
                caveats_json=json.dumps(["Rejected before feed parsing or candidate creation."]),
            )
            with session_scope(self._settings.source_discovery_database_url) as session:
                session.add(job)
                session.flush()
                return SourceDiscoveryFeedLinkScanResponse(
                    job=_serialize_job(job),
                    memories=[],
                    snapshots=[],
                    feed_type="unknown",
                    feed_title=None,
                    scanned_item_count=0,
                    extracted_url_count=0,
                    caveats=SOURCE_DISCOVERY_CAVEATS,
                )

        used_requests = 0
        try:
            if request.fixture_text is not None:
                document = request.fixture_text
                source_mode = "fixture"
            elif request.request_budget > 0:
                fetched = _fetch_url(request.feed_url, method="GET", max_bytes=MAX_FETCH_BYTES)
                document = fetched["body"]
                source_mode = "live"
                used_requests = 1
            else:
                raise ValueError("Feed link scan requires fixture_text or request_budget > 0.")
            parsed_feed = parse_feed_document(document, source_mode=source_mode, feed_url=request.feed_url)
        except Exception as exc:  # noqa: BLE001
            job = SourceDiscoveryJobORM(
                job_id=job_id,
                job_type="feed_link_scan",
                status="failed",
                seed_url=request.feed_url,
                wave_id=request.wave_id,
                wave_title=request.wave_title,
                discovered_source_ids_json=json.dumps([]),
                rejected_reason=str(exc)[:300],
                request_budget=request.request_budget,
                used_requests=used_requests,
                started_at=now,
                finished_at=now,
                caveats_json=json.dumps(caveats + [
                    "Feed parsing failed; no candidates or snapshots were created.",
                ]),
            )
            with session_scope(self._settings.source_discovery_database_url) as session:
                session.add(job)
                session.flush()
                return SourceDiscoveryFeedLinkScanResponse(
                    job=_serialize_job(job),
                    memories=[],
                    snapshots=[],
                    feed_type="unknown",
                    feed_title=None,
                    scanned_item_count=0,
                    extracted_url_count=0,
                    caveats=SOURCE_DISCOVERY_CAVEATS,
                )

        records = parsed_feed.items[: max(0, request.max_items)]
        seeds: list[SourceDiscoveryCandidateSeed] = []
        summary_candidates: list[tuple[str, object]] = []
        extracted_urls: set[str] = set()
        for record in records:
            if not record.link:
                continue
            canonical_url = _canonical_source_url(record.link)
            if canonical_url in extracted_urls or len(extracted_urls) >= max(0, request.max_discovered):
                continue
            extracted_urls.add(canonical_url)
            seed = _candidate_seed_from_extracted_url(
                url=record.link,
                source_id=f"source:{_safe_id(urlparse(canonical_url).netloc + urlparse(canonical_url).path)[:120]}",
                title=record.title or parsed_feed.feed_title or parsed.netloc,
                wave_id=request.wave_id,
                wave_title=request.wave_title,
                discovery_reason=request.discovery_reason,
                caveats=[
                    "Feed link scan is bounded to known public feed items and creates review candidates only.",
                    "Feed item text remains source-reported context and does not prove event truth or attribution.",
                ] + caveats,
            )
            if seed is None:
                continue
            seeds.append(seed)
            if request.capture_item_summaries:
                summary_candidates.append((canonical_url, record))

        with session_scope(self._settings.source_discovery_database_url) as session:
            memories = [_upsert_candidate_row(session, seed, now=now) for seed in seeds]
            session.flush()
            snapshots: list[SourceContentSnapshotORM] = []
            if request.capture_item_summaries:
                for canonical_url, record in summary_candidates:
                    memory = session.scalar(select(SourceMemoryORM).where(SourceMemoryORM.canonical_url == canonical_url))
                    if memory is None:
                        continue
                    snapshot = _build_feed_item_snapshot(
                        source_id=memory.source_id,
                        url=memory.url,
                        title=record.title,
                        summary=record.summary,
                        published_at=record.updated_at or record.published_at,
                        fetched_at=now,
                    )
                    if snapshot is None:
                        continue
                    session.merge(snapshot)
                    snapshots.append(snapshot)
            job = SourceDiscoveryJobORM(
                job_id=job_id,
                job_type="feed_link_scan",
                status="completed",
                seed_url=request.feed_url,
                wave_id=request.wave_id,
                wave_title=request.wave_title,
                discovered_source_ids_json=json.dumps([memory.source_id for memory in memories]),
                rejected_reason=None,
                request_budget=max(0, request.request_budget),
                used_requests=used_requests,
                started_at=now,
                finished_at=now,
                caveats_json=json.dumps(caveats + [
                    "Feed link scan is bounded to feed items and does not auto-activate or poll discovered links.",
                ]),
            )
            session.add(job)
            session.flush()
            return SourceDiscoveryFeedLinkScanResponse(
                job=_serialize_job(job),
                memories=[_serialize_memory(memory) for memory in memories],
                snapshots=[_serialize_snapshot(snapshot) for snapshot in snapshots],
                feed_type=parsed_feed.feed_type,
                feed_title=parsed_feed.feed_title,
                scanned_item_count=len(records),
                extracted_url_count=len(extracted_urls),
                caveats=SOURCE_DISCOVERY_CAVEATS,
            )

    def run_catalog_scan_job(
        self,
        request: SourceDiscoveryCatalogScanRequest,
    ) -> SourceDiscoveryCatalogScanResponse:
        now = _utc_now()
        parsed = urlparse(request.catalog_url)
        job_id = f"source-catalog-scan:{_safe_id(request.catalog_url)}:{_compact_timestamp(now)}"
        caveats = list(request.caveats)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            job = SourceDiscoveryJobORM(
                job_id=job_id,
                job_type="catalog_scan",
                status="rejected",
                seed_url=request.catalog_url,
                wave_id=request.wave_id,
                wave_title=request.wave_title,
                discovered_source_ids_json=json.dumps([]),
                rejected_reason="Catalog URL must be an absolute http(s) URL.",
                request_budget=request.request_budget,
                used_requests=0,
                started_at=now,
                finished_at=now,
                caveats_json=json.dumps(["Rejected before catalog parsing or candidate creation."]),
            )
            with session_scope(self._settings.source_discovery_database_url) as session:
                session.add(job)
                session.flush()
                return SourceDiscoveryCatalogScanResponse(
                    job=_serialize_job(job),
                    memories=[],
                    catalog_type="unknown",
                    extracted_url_count=0,
                    caveats=SOURCE_DISCOVERY_CAVEATS,
                )

        used_requests = 0
        try:
            if request.fixture_text is not None:
                document = request.fixture_text
            elif request.request_budget > 0:
                fetched = _fetch_url(request.catalog_url, method="GET", max_bytes=MAX_FETCH_BYTES)
                document = fetched["body"]
                used_requests = 1
            else:
                raise ValueError("Catalog scan requires fixture_text or request_budget > 0.")
            catalog_urls, catalog_type = _extract_catalog_candidate_urls(
                request.catalog_url,
                document,
                max_discovered=max(0, request.max_discovered),
            )
        except Exception as exc:  # noqa: BLE001
            job = SourceDiscoveryJobORM(
                job_id=job_id,
                job_type="catalog_scan",
                status="failed",
                seed_url=request.catalog_url,
                wave_id=request.wave_id,
                wave_title=request.wave_title,
                discovered_source_ids_json=json.dumps([]),
                rejected_reason=str(exc)[:300],
                request_budget=request.request_budget,
                used_requests=used_requests,
                started_at=now,
                finished_at=now,
                caveats_json=json.dumps(caveats + [
                    "Catalog parsing failed; no candidates were created.",
                ]),
            )
            with session_scope(self._settings.source_discovery_database_url) as session:
                session.add(job)
                session.flush()
                return SourceDiscoveryCatalogScanResponse(
                    job=_serialize_job(job),
                    memories=[],
                    catalog_type="unknown",
                    extracted_url_count=0,
                    caveats=SOURCE_DISCOVERY_CAVEATS,
                )

        seeds: list[SourceDiscoveryCandidateSeed] = []
        for url in catalog_urls:
            canonical_url = _canonical_source_url(url)
            seed = _candidate_seed_from_extracted_url(
                url=canonical_url,
                source_id=f"source:{_safe_id(urlparse(canonical_url).netloc + urlparse(canonical_url).path)[:120]}",
                title=parsed.netloc,
                wave_id=request.wave_id,
                wave_title=request.wave_title,
                discovery_reason=request.discovery_reason,
                caveats=[
                    "Catalog scan is bounded to one allowed public page or API response and creates candidates only.",
                    "Catalog links are not recursively crawled or automatically scheduled.",
                ] + caveats,
            )
            if seed is not None:
                seeds.append(seed)

        with session_scope(self._settings.source_discovery_database_url) as session:
            memories = [_upsert_candidate_row(session, seed, now=now) for seed in seeds]
            job = SourceDiscoveryJobORM(
                job_id=job_id,
                job_type="catalog_scan",
                status="completed",
                seed_url=request.catalog_url,
                wave_id=request.wave_id,
                wave_title=request.wave_title,
                discovered_source_ids_json=json.dumps([memory.source_id for memory in memories]),
                rejected_reason=None,
                request_budget=max(0, request.request_budget),
                used_requests=used_requests,
                started_at=now,
                finished_at=now,
                caveats_json=json.dumps(caveats + [
                    "Catalog scan is bounded and candidate-only; it does not fetch or activate child sources.",
                ]),
            )
            session.add(job)
            session.flush()
            return SourceDiscoveryCatalogScanResponse(
                job=_serialize_job(job),
                memories=[_serialize_memory(memory) for memory in memories],
                catalog_type=catalog_type,
                extracted_url_count=len(catalog_urls),
                caveats=SOURCE_DISCOVERY_CAVEATS,
            )

    def run_record_source_extract_job(
        self,
        request: SourceDiscoveryRecordSourceExtractRequest,
    ) -> SourceDiscoveryRecordSourceExtractResponse:
        now = _utc_now()
        job_id = f"source-record-extract:{_compact_timestamp(now)}"
        caveats = list(request.caveats)
        used_requests = 0
        scanned_record_count = 0
        seeds: list[SourceDiscoveryCandidateSeed] = []
        extracted_urls: set[str] = set()

        with wave_session_scope(self._settings.wave_monitor_database_url) as session:
            stmt = select(WaveRecordORM).order_by(WaveRecordORM.collected_at.desc())
            if request.wave_monitor_monitor_id:
                stmt = stmt.where(WaveRecordORM.monitor_id == request.wave_monitor_monitor_id)
            wave_records = list(session.scalars(stmt.limit(max(0, request.wave_monitor_limit))))
            monitor_titles = {
                monitor.monitor_id: monitor.title
                for monitor in session.scalars(select(WaveMonitorORM).order_by(WaveMonitorORM.monitor_id))
            }
            scanned_record_count += len(wave_records)
            for record in wave_records:
                for url in _extract_urls_from_wave_record(record):
                    canonical_url = _canonical_source_url(url)
                    if canonical_url in extracted_urls:
                        continue
                    extracted_urls.add(canonical_url)
                    seed = _candidate_seed_from_extracted_url(
                        url=url,
                        source_id=f"source:{_safe_id(urlparse(canonical_url).netloc + urlparse(canonical_url).path)[:120]}",
                        title=record.source_name or record.title,
                        wave_id=record.monitor_id,
                        wave_title=monitor_titles.get(record.monitor_id),
                        discovery_reason="Record source extracted from existing Wave Monitor record.",
                        caveats=[
                            "Record-source extraction creates review candidates only and does not activate or poll the source.",
                            "Wave Monitor record text remains source-scoped context, not truth proof.",
                        ],
                    )
                    if seed is not None:
                        seeds.append(seed)

        if request.data_ai_limit > 0:
            mode = self._settings.data_ai_multi_feed_source_mode.strip().lower()
            if mode != "fixture" and request.request_budget <= 0:
                caveats.append(
                    "Data AI record-source extraction was skipped because live multi-feed loading requires explicit request budget in this slice."
                )
            else:
                query = DataAiMultiFeedQuery(
                    limit=max(0, request.data_ai_limit),
                    dedupe=True,
                    source_ids=request.data_ai_source_ids or None,
                )
                response = asyncio.run(DataAiMultiFeedService(self._settings).list_recent(query))
                scanned_record_count += len(response.items)
                if mode == "live":
                    selected_source_ids = request.data_ai_source_ids or response.metadata.selected_source_ids
                    used_requests += len(selected_source_ids)
                    caveats.append(
                        "Data AI live record-source extraction estimates request usage per selected source feed."
                    )
                for item in response.items[: max(0, request.data_ai_limit)]:
                    for url in _extract_urls_from_data_ai_item(item):
                        canonical_url = _canonical_source_url(url)
                        if canonical_url in extracted_urls:
                            continue
                        extracted_urls.add(canonical_url)
                        seed = _candidate_seed_from_extracted_url(
                            url=url,
                            source_id=f"source:{_safe_id(urlparse(canonical_url).netloc + urlparse(canonical_url).path)[:120]}",
                            title=item.title or item.source_name,
                            wave_id=None,
                            wave_title=None,
                            discovery_reason="Record source extracted from Data AI feed item.",
                            caveats=[
                                "Data AI feed item text remains inert data and does not prove event truth, attribution, or impact.",
                                f"Extracted from Data AI source {item.source_id}.",
                            ],
                        )
                        if seed is not None:
                            seeds.append(seed)

        with session_scope(self._settings.source_discovery_database_url) as session:
            memories = [_upsert_candidate_row(session, seed, now=now) for seed in seeds]
            job = SourceDiscoveryJobORM(
                job_id=job_id,
                job_type="record_source_extract",
                status="completed",
                seed_url=None,
                wave_id=request.wave_monitor_monitor_id,
                wave_title=None,
                discovered_source_ids_json=json.dumps([memory.source_id for memory in memories]),
                rejected_reason=None,
                request_budget=max(0, request.request_budget),
                used_requests=used_requests,
                started_at=now,
                finished_at=now,
                caveats_json=json.dumps(caveats + [
                    "Record-source extraction is bounded to existing records/items and creates candidates only.",
                ]),
            )
            session.add(job)
            session.flush()
            return SourceDiscoveryRecordSourceExtractResponse(
                job=_serialize_job(job),
                memories=[_serialize_memory(memory) for memory in memories],
                scanned_record_count=scanned_record_count,
                extracted_url_count=len(extracted_urls),
                caveats=SOURCE_DISCOVERY_CAVEATS,
            )

    def store_content_snapshot(
        self,
        request: SourceDiscoveryContentSnapshotRequest,
    ) -> SourceDiscoveryContentSnapshotResponse:
        now = _utc_now()
        with session_scope(self._settings.source_discovery_database_url) as session:
            memory = session.get(SourceMemoryORM, request.source_id)
            if memory is None:
                raise ValueError(f"Unknown source_id: {request.source_id}")

            url = request.url or memory.url
            used_requests = 0
            content_type = request.content_type
            extraction_method = "raw_text"
            caveats = list(request.caveats)
            title = request.title
            author = request.author
            published_at = request.published_at
            if request.raw_text is not None:
                full_text = request.raw_text
            elif request.html_text is not None:
                article_snapshot = extract_article_snapshot_from_html(request.html_text, base_url=url)
                full_text = article_snapshot.text
                extraction_method = article_snapshot.method
                content_type = content_type or "text/html"
                url = article_snapshot.canonical_url or url
                title = title or article_snapshot.title
                author = author or article_snapshot.author
                published_at = published_at or article_snapshot.published_at
            elif request.request_budget > 0:
                fetched = _fetch_url(url, method="GET", max_bytes=MAX_FETCH_BYTES)
                used_requests = 1
                content_type = fetched["content_type"]
                if "html" in (content_type or "").lower():
                    article_snapshot = extract_article_snapshot_from_html(str(fetched["body"]), base_url=url)
                    full_text = article_snapshot.text
                    extraction_method = f"live_fetch_{article_snapshot.method}"
                    url = article_snapshot.canonical_url or url
                    title = title or article_snapshot.title
                    author = author or article_snapshot.author
                    published_at = published_at or article_snapshot.published_at
                else:
                    full_text = str(fetched["body"])
                    extraction_method = "live_fetch"
            else:
                full_text = ""
                extraction_method = "metadata_only"
                caveats.append("No raw/html text supplied and request budget was zero.")

            normalized_text = _normalize_text(full_text)
            text_hash = hashlib.sha256(normalized_text.encode("utf-8")).hexdigest()
            snapshot = SourceContentSnapshotORM(
                snapshot_id=f"source-snapshot:{_safe_id(request.source_id)}:{text_hash[:16]}",
                source_id=request.source_id,
                url=url,
                title=title or memory.title,
                content_type=content_type,
                extraction_method=extraction_method,
                text_hash=text_hash,
                text_length=len(normalized_text),
                full_text=normalized_text,
                author=author,
                published_at=published_at,
                fetched_at=now,
                request_budget=max(0, request.request_budget),
                used_requests=used_requests,
                extraction_confidence=_extraction_confidence(normalized_text, extraction_method),
                caveats_json=json.dumps(caveats + [
                    "Full text is stored as source evidence input; it does not prove claims without assessment.",
                ]),
            )
            memory.last_seen_at = now
            memory.caveats_json = json.dumps(sorted(set(_loads_list(memory.caveats_json) + caveats)))
            session.merge(snapshot)
            session.flush()
            return SourceDiscoveryContentSnapshotResponse(
                snapshot=_serialize_snapshot(snapshot),
                memory=_serialize_memory(memory),
                caveats=SOURCE_DISCOVERY_CAVEATS,
            )

    def run_article_fetch_job(
        self,
        request: SourceDiscoveryArticleFetchRequest,
    ) -> SourceDiscoveryArticleFetchResponse:
        now = _utc_now()
        job_id = f"source-article-fetch:{_safe_id(request.source_id)}:{_compact_timestamp(now)}"
        caveats = list(request.caveats)
        with session_scope(self._settings.source_discovery_database_url) as session:
            memory = session.get(SourceMemoryORM, request.source_id)
            if memory is None:
                raise ValueError(f"Unknown source_id: {request.source_id}")
            if memory.source_class not in {"article", "community", "official"}:
                job = SourceDiscoveryJobORM(
                    job_id=job_id,
                    job_type="article_fetch",
                    status="rejected",
                    seed_url=memory.url,
                    wave_id=None,
                    wave_title=None,
                    discovered_source_ids_json=json.dumps([memory.source_id]),
                    rejected_reason="Article fetch is only allowed for article/community/official source classes.",
                    request_budget=max(0, request.request_budget),
                    used_requests=0,
                    started_at=now,
                    finished_at=now,
                    caveats_json=json.dumps(caveats),
                )
                session.add(job)
                session.flush()
                return SourceDiscoveryArticleFetchResponse(
                    job=_serialize_job(job),
                    snapshot=None,
                    memory=_serialize_memory(memory),
                    caveats=SOURCE_DISCOVERY_CAVEATS,
                )
            if memory.lifecycle_state not in {"approved-unvalidated", "sandboxed", "validated"} or memory.policy_state == "blocked":
                job = SourceDiscoveryJobORM(
                    job_id=job_id,
                    job_type="article_fetch",
                    status="rejected",
                    seed_url=memory.url,
                    wave_id=None,
                    wave_title=None,
                    discovered_source_ids_json=json.dumps([memory.source_id]),
                    rejected_reason="Article fetch requires approved, sandboxed, or validated source state and non-blocked policy.",
                    request_budget=max(0, request.request_budget),
                    used_requests=0,
                    started_at=now,
                    finished_at=now,
                    caveats_json=json.dumps(caveats),
                )
                session.add(job)
                session.flush()
                return SourceDiscoveryArticleFetchResponse(
                    job=_serialize_job(job),
                    snapshot=None,
                    memory=_serialize_memory(memory),
                    caveats=SOURCE_DISCOVERY_CAVEATS,
                )

        snapshot_response = self.store_content_snapshot(
            SourceDiscoveryContentSnapshotRequest(
                source_id=request.source_id,
                raw_text=request.fixture_text,
                html_text=request.fixture_html,
                request_budget=request.request_budget if request.fixture_text is None and request.fixture_html is None else 0,
                caveats=caveats + [
                    "Article fetch is bounded to one approved or sandboxed source and stores evidence text only.",
                ],
            )
        )
        used_requests = snapshot_response.snapshot.used_requests
        with session_scope(self._settings.source_discovery_database_url) as session:
            job = SourceDiscoveryJobORM(
                job_id=job_id,
                job_type="article_fetch",
                status="completed",
                seed_url=snapshot_response.snapshot.url,
                wave_id=None,
                wave_title=None,
                discovered_source_ids_json=json.dumps([request.source_id]),
                rejected_reason=None,
                request_budget=max(0, request.request_budget),
                used_requests=used_requests,
                started_at=now,
                finished_at=_utc_now(),
                caveats_json=json.dumps(caveats + [
                    "Article fetch does not fetch children or promote claims automatically.",
                ]),
            )
            session.add(job)
            session.flush()
            return SourceDiscoveryArticleFetchResponse(
                job=_serialize_job(job),
                snapshot=snapshot_response.snapshot,
                memory=snapshot_response.memory,
                caveats=SOURCE_DISCOVERY_CAVEATS,
            )

    def run_social_metadata_job(
        self,
        request: SourceDiscoverySocialMetadataJobRequest,
    ) -> SourceDiscoverySocialMetadataJobResponse:
        now = _utc_now()
        job_id = f"source-social-metadata:{_safe_id(request.url)}:{_compact_timestamp(now)}"
        caveats = list(request.caveats)
        parsed = urlparse(request.url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            job = SourceDiscoveryJobORM(
                job_id=job_id,
                job_type="social_metadata",
                status="rejected",
                seed_url=request.url,
                wave_id=request.wave_id,
                wave_title=request.wave_title,
                discovered_source_ids_json=json.dumps([]),
                rejected_reason="Social/image metadata job requires an absolute http(s) URL.",
                request_budget=max(0, request.request_budget),
                used_requests=0,
                started_at=now,
                finished_at=now,
                caveats_json=json.dumps(caveats),
            )
            with session_scope(self._settings.source_discovery_database_url) as session:
                session.add(job)
                session.flush()
                return SourceDiscoverySocialMetadataJobResponse(
                    job=_serialize_job(job),
                    memory=None,
                    snapshot=None,
                    metadata=SourceDiscoverySocialMetadataSummary(),
                    caveats=SOURCE_DISCOVERY_CAVEATS,
                )

        seed = _candidate_seed_from_extracted_url(
            url=request.url,
            source_id=request.source_id or f"source:{_safe_id(parsed.netloc + parsed.path)[:120]}",
            title=request.title or parsed.netloc,
            wave_id=request.wave_id,
            wave_title=request.wave_title,
            discovery_reason="public social/image metadata scan",
            caveats=caveats + [
                "Public social/image evidence is contextual and remains bounded to public page text, captions, and media references.",
                "No login-only, hidden, OCR-heavy, or media-blob routes are allowed.",
            ],
        )
        if seed is None:
            raise ValueError(f"Could not derive candidate seed from URL: {request.url}")
        seed.source_class = "social_image"
        seed.source_type = "social"
        seed.machine_readable_result = "partial"

        with session_scope(self._settings.source_discovery_database_url) as session:
            memory = _upsert_candidate_row(session, seed, now=now)
            session.flush()
            serialized_memory = _serialize_memory(memory)

        used_requests = 0
        if request.fixture_html is not None:
            body = request.fixture_html
        elif request.fixture_text is not None:
            body = request.fixture_text
        elif request.request_budget > 0:
            fetched = _fetch_url(request.url, method="GET", max_bytes=MAX_FETCH_BYTES)
            body = fetched["body"]
            used_requests = 1
        else:
            body = ""

        extraction = extract_social_metadata_from_html(body, url=request.url)
        metadata = extraction.metadata
        metadata_text = _build_social_metadata_text(metadata)
        snapshot_response: SourceDiscoveryContentSnapshotResponse | None = None
        if metadata_text:
            snapshot_response = self.store_content_snapshot(
                SourceDiscoveryContentSnapshotRequest(
                    source_id=serialized_memory.source_id,
                    raw_text=metadata_text,
                    url=metadata.canonical_url or request.url,
                    title=metadata.display_title,
                    author=metadata.author,
                    published_at=metadata.published_at,
                    content_type="text/html" if request.fixture_html or used_requests > 0 else "text/plain",
                    request_budget=0,
                    caveats=caveats + [
                        "Stored text is bounded public page evidence and may omit private, dynamic, or media-embedded details.",
                    ],
                )
            )

        with session_scope(self._settings.source_discovery_database_url) as session:
            job = SourceDiscoveryJobORM(
                job_id=job_id,
                job_type="social_metadata",
                status="completed",
                seed_url=request.url,
                wave_id=request.wave_id,
                wave_title=request.wave_title,
                discovered_source_ids_json=json.dumps([serialized_memory.source_id]),
                rejected_reason=None,
                request_budget=max(0, request.request_budget),
                used_requests=used_requests,
                started_at=now,
                finished_at=_utc_now(),
                caveats_json=json.dumps(caveats + [
                    "Social/image job captures public page evidence only and does not fetch media blobs or private endpoints.",
                ]),
            )
            session.add(job)
            session.flush()
            return SourceDiscoverySocialMetadataJobResponse(
                job=_serialize_job(job),
                memory=snapshot_response.memory if snapshot_response else serialized_memory,
                snapshot=snapshot_response.snapshot if snapshot_response else None,
                metadata=metadata,
                caveats=SOURCE_DISCOVERY_CAVEATS,
            )

    def review_queue(self, *, limit: int = 100, owner_lane: str | None = None) -> SourceDiscoveryReviewQueueResponse:
        with session_scope(self._settings.source_discovery_database_url) as session:
            memories = list(
                session.scalars(
                    select(SourceMemoryORM)
                    .where(SourceMemoryORM.lifecycle_state.not_in(["rejected", "archived"]))
                    .order_by(SourceMemoryORM.last_seen_at.desc())
                    .limit(max(0, limit) * 4)
                )
            )
            items: list[tuple[int, SourceDiscoveryReviewQueueItem]] = []
            for memory in memories:
                if owner_lane and memory.owner_lane != owner_lane:
                    continue
                fits = _fits_for_source(session, memory.source_id)
                best_fit = _best_wave_fit(fits)
                has_snapshot = session.scalar(
                    select(SourceContentSnapshotORM.snapshot_id)
                    .where(SourceContentSnapshotORM.source_id == memory.source_id)
                    .limit(1)
                ) is not None
                reasons = _review_reasons(memory, best_fit=best_fit, has_snapshot=has_snapshot)
                if not reasons:
                    continue
                priority_score, priority = _review_priority(memory, best_fit=best_fit, has_snapshot=has_snapshot)
                items.append(
                    (
                        priority_score,
                        SourceDiscoveryReviewQueueItem(
                            source_id=memory.source_id,
                            title=memory.title,
                            url=memory.url,
                            source_class=memory.source_class,  # type: ignore[arg-type]
                            lifecycle_state=memory.lifecycle_state,
                            policy_state=memory.policy_state,
                            source_health=memory.source_health,
                            owner_lane=memory.owner_lane,
                            priority=priority,
                            review_reasons=reasons,
                            recommended_actions=_recommended_review_actions(memory, owner_lane=memory.owner_lane),
                            global_reputation_score=memory.global_reputation_score,
                            domain_reputation_score=memory.domain_reputation_score,
                            source_health_score=memory.source_health_score,
                            timeliness_score=memory.timeliness_score,
                            confidence_level=memory.confidence_level,
                            best_wave_id=best_fit.wave_id if best_fit else None,
                            best_wave_title=best_fit.wave_title if best_fit else None,
                            best_wave_fit_score=best_fit.fit_score if best_fit else None,
                            next_check_at=memory.next_check_at,
                        ),
                    )
                )
            sorted_items = [
                item
                for _, item in sorted(
                    items,
                    key=lambda pair: (
                        -pair[0],
                        -(pair[1].best_wave_fit_score or 0.0),
                        pair[1].title.casefold(),
                    ),
                )[: max(0, limit)]
            ]
            return SourceDiscoveryReviewQueueResponse(
                metadata={
                    "source": "source-discovery-review-queue",
                    "count": len(sorted_items),
                    "ownerLane": owner_lane,
                },
                items=sorted_items,
                caveats=SOURCE_DISCOVERY_CAVEATS + [
                    "Review queue items are prioritization aids only and do not approve, reject, or validate a source by themselves.",
                ],
            )

    def apply_review_action(
        self,
        request: SourceDiscoveryReviewActionRequest,
    ) -> SourceDiscoveryReviewActionResponse:
        now = _utc_now()
        with session_scope(self._settings.source_discovery_database_url) as session:
            memory = session.get(SourceMemoryORM, request.source_id)
            if memory is None:
                raise ValueError(f"Unknown source_id: {request.source_id}")
            previous_lifecycle_state = memory.lifecycle_state
            previous_policy_state = memory.policy_state
            owner_lane = memory.owner_lane

            if request.action == "mark_reviewed":
                memory.policy_state = "reviewed"
            elif request.action == "approve_candidate":
                memory.lifecycle_state = "approved-unvalidated"
                memory.policy_state = "reviewed"
            elif request.action == "sandbox_check":
                memory.lifecycle_state = "sandboxed"
                memory.policy_state = "reviewed"
            elif request.action == "reject":
                memory.lifecycle_state = "rejected"
                memory.policy_state = "blocked"
            elif request.action == "archive":
                memory.lifecycle_state = "archived"
                memory.policy_state = "reviewed"
            elif request.action == "assign_owner":
                if not request.owner_lane or not request.owner_lane.strip():
                    raise ValueError("assign_owner requires owner_lane.")
                owner_lane = request.owner_lane.strip()
                memory.owner_lane = owner_lane
            else:
                raise ValueError(f"Unsupported review action: {request.action}")

            if request.owner_lane and request.action != "assign_owner":
                owner_lane = request.owner_lane.strip()
                memory.owner_lane = owner_lane

            memory.last_seen_at = now
            basis = _loads_list(memory.reputation_basis_json)
            basis.append(f"review_action:{request.action}:{request.reason[:120]}")
            memory.reputation_basis_json = json.dumps(basis[-20:])
            action = SourceReviewActionORM(
                source_id=memory.source_id,
                action=request.action,
                reviewed_by=request.reviewed_by,
                reason=request.reason[:600],
                owner_lane=owner_lane,
                previous_lifecycle_state=previous_lifecycle_state,
                new_lifecycle_state=memory.lifecycle_state,
                previous_policy_state=previous_policy_state,
                new_policy_state=memory.policy_state,
                created_at=now,
            )
            session.add(action)
            session.flush()
            return SourceDiscoveryReviewActionResponse(
                action=_serialize_review_action(action),
                memory=_serialize_memory(memory),
                caveats=SOURCE_DISCOVERY_CAVEATS,
            )

    def apply_review_claims(
        self,
        request: SourceDiscoveryReviewClaimApplicationRequest,
    ) -> SourceDiscoveryReviewClaimApplicationResponse:
        if not request.applications:
            raise ValueError("At least one claim application is required.")
        with wave_session_scope(self._settings.wave_monitor_database_url) as wave_session:
            review = wave_session.get(WaveLlmReviewORM, request.review_id)
            if review is None:
                raise ValueError(f"Unknown review_id: {request.review_id}")
            task = wave_session.get(WaveLlmTaskORM, review.task_id)
            if task is None:
                raise ValueError(f"Unknown task_id for review: {review.task_id}")
            task_id = task.task_id
            task_monitor_id = task.monitor_id
            parsed_claims = _load_wave_review_claims(review.parsed_claims_json)
            accepted_claims = {
                index: claim
                for index, claim in enumerate(parsed_claims)
                if str(claim.get("status", "")) == "accepted_for_review"
            }
            source_ids = _loads_list(task.source_ids_json)
            if request.source_id:
                source_id = request.source_id
            elif len(source_ids) == 1:
                source_id = source_ids[0]
            else:
                raise ValueError("Review claim application requires source_id when the task references zero or multiple sources.")

        now = _utc_now()
        with session_scope(self._settings.source_discovery_database_url) as session:
            memory = session.get(SourceMemoryORM, source_id)
            if memory is None:
                raise ValueError(f"Unknown source_id: {source_id}")
            if memory.policy_state == "blocked" or memory.lifecycle_state in {"rejected", "archived"}:
                raise ValueError("Review claims cannot be applied to blocked, rejected, or archived sources.")
            if memory.policy_state != "reviewed":
                raise ValueError("Review claims require the source to be explicitly reviewed first.")

            created_rows: list[SourceReviewClaimApplicationORM] = []
            for application in request.applications:
                if application.claim_index not in accepted_claims:
                    raise ValueError(f"claim_index {application.claim_index} is not an accepted review claim.")
                existing = session.scalar(
                    select(SourceReviewClaimApplicationORM).where(
                        SourceReviewClaimApplicationORM.review_id == request.review_id,
                        SourceReviewClaimApplicationORM.source_id == source_id,
                        SourceReviewClaimApplicationORM.claim_index == application.claim_index,
                    )
                )
                if existing is not None:
                    raise ValueError(f"claim_index {application.claim_index} for this review and source has already been applied.")

                claim = accepted_claims[application.claim_index]
                claim_request = SourceDiscoveryClaimOutcomeRequest(
                    source_id=source_id,
                    wave_id=task_monitor_id,
                    claim_text=str(claim.get("claim_text", "")),
                    claim_type=str(claim.get("claim_type", "state")),
                    outcome=application.outcome,
                    evidence_basis=str(claim.get("evidence_basis", "contextual")),
                    observed_at=now,
                    caveats=application.caveats + [
                        f"Applied from Wave LLM review {request.review_id} by {request.approved_by}.",
                    ],
                )
                session.add(
                    SourceClaimOutcomeORM(
                        source_id=claim_request.source_id,
                        wave_id=claim_request.wave_id,
                        claim_text=claim_request.claim_text,
                        claim_type=claim_request.claim_type,
                        outcome=claim_request.outcome,
                        evidence_basis=claim_request.evidence_basis,
                        observed_at=claim_request.observed_at or now,
                        assessed_at=now,
                        corroborating_source_ids_json=json.dumps([]),
                        contradiction_source_ids_json=json.dumps([]),
                        caveats_json=json.dumps(claim_request.caveats),
                    )
                )
                _apply_claim_outcome(session, memory, claim_request, now)
                row = SourceReviewClaimApplicationORM(
                    review_id=request.review_id,
                    task_id=task_id,
                    source_id=source_id,
                    wave_id=task_monitor_id,
                    claim_index=application.claim_index,
                    claim_text=claim_request.claim_text[:1000],
                    outcome=application.outcome,
                    applied_by=request.approved_by,
                    approval_reason=request.approval_reason[:600],
                    created_at=now,
                    caveats_json=json.dumps(application.caveats + [
                        "LLM review claim application is deterministic and audit-logged; it is not automatic model promotion.",
                    ]),
                )
                session.add(row)
                created_rows.append(row)

            memory.policy_state = "reviewed"
            memory.last_seen_at = now
            session.flush()
            fits = _fits_for_source(session, source_id)
            return SourceDiscoveryReviewClaimApplicationResponse(
                memory=_serialize_memory(memory),
                applications=[_serialize_review_claim_application(row) for row in created_rows],
                wave_fits=[_serialize_wave_fit(fit) for fit in fits],
                caveats=SOURCE_DISCOVERY_CAVEATS + [
                    "Applied review claims affect reputation only through explicit approved outcomes, not directly from model output.",
                ],
            )

    def reverse_reputation_event(
        self,
        request: SourceDiscoveryReputationReversalRequest,
    ) -> SourceDiscoveryReputationReversalResponse:
        now = _utc_now()
        with session_scope(self._settings.source_discovery_database_url) as session:
            event = session.get(SourceReputationEventORM, request.event_id)
            if event is None:
                raise ValueError(f"Unknown event_id: {request.event_id}")
            memory = session.get(SourceMemoryORM, event.source_id)
            if memory is None:
                raise ValueError(f"Unknown source_id on event: {event.source_id}")

            reversal_event: SourceReputationEventORM | None = None
            if event.reversed_at is None:
                before = memory.global_reputation_score
                delta = event.score_before - event.score_after
                memory.global_reputation_score = _clamp(memory.global_reputation_score + delta)
                memory.domain_reputation_score = _clamp(memory.domain_reputation_score + delta)
                memory.last_reputation_event_at = now
                event.reversed_at = now
                event.reversal_reason = request.reason
                reversal_event = SourceReputationEventORM(
                    source_id=event.source_id,
                    wave_id=event.wave_id,
                    event_type="reversal",
                    outcome=event.outcome,
                    score_before=before,
                    score_after=memory.global_reputation_score,
                    reason=f"Reversed event {event.event_id}: {request.reason[:400]}",
                    created_at=now,
                )
                session.add(reversal_event)
            session.flush()
            return SourceDiscoveryReputationReversalResponse(
                reversed_event=_serialize_reputation_event(event),
                reversal_event=_serialize_reputation_event(reversal_event) if reversal_event else None,
                memory=_serialize_memory(memory),
                caveats=SOURCE_DISCOVERY_CAVEATS,
            )

    def run_scheduler_tick(self, request: SourceDiscoverySchedulerTickRequest) -> SourceDiscoverySchedulerTickResponse:
        now = _utc_now()
        tick_id = f"source-scheduler:{_compact_timestamp(now)}"
        remaining_budget = max(0, request.request_budget)
        checks: list[SourceDiscoveryHealthCheckSummary] = []
        jobs: list[SourceDiscoveryJobSummary] = []
        llm_executions: list[WaveLlmExecutionSummary] = []
        caveats = list(request.caveats) + [
            "Scheduler tick is bounded; it does not auto-approve discovered or checked sources.",
        ]

        with session_scope(self._settings.source_discovery_database_url) as session:
            memories = list(
                session.scalars(
                    select(SourceMemoryORM)
                    .where(SourceMemoryORM.lifecycle_state != "rejected")
                    .order_by(SourceMemoryORM.next_check_at, SourceMemoryORM.last_seen_at)
                )
            )
            source_ids = [
                memory.source_id
                for memory in memories
                if _is_due_for_health_check(memory.next_check_at, now)
            ][: max(0, request.health_check_limit)]

        for source_id in source_ids:
            per_check_budget = 1 if remaining_budget > 0 else 0
            remaining_budget -= per_check_budget
            response = self.check_source_health(
                SourceDiscoveryHealthCheckRequest(
                    source_id=source_id,
                    request_budget=per_check_budget,
                    caveats=["Scheduler-triggered health check."],
                )
            )
            checks.append(response.health_check)

        record_extract_jobs_completed = 0
        if request.record_source_extract_limit > 0:
            record_extract = self.run_record_source_extract_job(
                SourceDiscoveryRecordSourceExtractRequest(
                    wave_monitor_limit=max(0, request.record_source_extract_limit),
                    request_budget=0,
                    caveats=["Scheduler-triggered record-source extraction."],
                )
            )
            jobs.append(record_extract.job)
            record_extract_jobs_completed = 1

        llm_executions = self._run_scheduler_llm_tasks(
            tick_id=tick_id,
            limit=max(0, request.llm_task_limit),
            provider=request.llm_provider or self._settings.wave_llm_default_provider,
            allow_network=request.llm_allow_network,
            remaining_budget=remaining_budget,
        )

        finished_at = _utc_now()
        used_requests = (
            sum(check.used_requests for check in checks)
            + sum(job.used_requests for job in jobs)
            + sum(execution.used_requests for execution in llm_executions)
        )
        with session_scope(self._settings.source_discovery_database_url) as session:
            tick = SourceSchedulerTickORM(
                tick_id=tick_id,
                status="completed",
                requested_at=now,
                finished_at=finished_at,
                health_checks_requested=max(0, request.health_check_limit),
                health_checks_completed=len(checks),
                expansion_jobs_requested=max(0, request.expansion_job_limit),
                expansion_jobs_completed=len(jobs),
                record_extract_jobs_requested=max(0, request.record_source_extract_limit),
                record_extract_jobs_completed=record_extract_jobs_completed,
                llm_tasks_requested=max(0, request.llm_task_limit),
                llm_tasks_completed=len(llm_executions),
                request_budget=max(0, request.request_budget),
                used_requests=used_requests,
                caveats_json=json.dumps(caveats),
            )
            session.add(tick)
            session.flush()
        return SourceDiscoverySchedulerTickResponse(
            tick_id=tick_id,
            status="completed",
            requested_at=now,
            finished_at=finished_at,
            health_checks_completed=len(checks),
            expansion_jobs_completed=len(jobs),
            record_extract_jobs_completed=record_extract_jobs_completed,
            llm_tasks_completed=len(llm_executions),
            request_budget=max(0, request.request_budget),
            used_requests=used_requests,
            health_checks=checks,
            jobs=jobs,
            llm_executions=llm_executions,
            caveats=SOURCE_DISCOVERY_CAVEATS + caveats,
        )

    def _run_scheduler_llm_tasks(
        self,
        *,
        tick_id: str,
        limit: int,
        provider: str,
        allow_network: bool,
        remaining_budget: int,
    ) -> list[WaveLlmExecutionSummary]:
        if limit <= 0:
            return []

        candidates: list[dict[str, object]] = []
        with session_scope(self._settings.source_discovery_database_url) as session:
            snapshots = list(
                session.scalars(
                    select(SourceContentSnapshotORM)
                    .order_by(SourceContentSnapshotORM.fetched_at.desc(), SourceContentSnapshotORM.text_length.desc())
                    .limit(max(0, limit) * 8)
                )
            )
            for snapshot in snapshots:
                memory = session.get(SourceMemoryORM, snapshot.source_id)
                if memory is None or memory.lifecycle_state in {"rejected", "archived"}:
                    continue
                if memory.policy_state == "blocked" or snapshot.text_length < 250:
                    continue
                if memory.source_class not in {"article", "community", "official", "live"}:
                    continue
                best_fit = _best_wave_fit(_fits_for_source(session, memory.source_id))
                if best_fit is None or best_fit.fit_score < 0.45:
                    continue
                candidates.append(
                    {
                        "source_id": memory.source_id,
                        "memory_title": memory.title,
                        "source_class": memory.source_class,
                        "snapshot_id": snapshot.snapshot_id,
                        "snapshot_title": snapshot.title,
                        "snapshot_url": snapshot.url,
                        "snapshot_published_at": snapshot.published_at,
                        "snapshot_full_text": snapshot.full_text,
                        "wave_id": best_fit.wave_id,
                    }
                )
                if len(candidates) >= limit:
                    break

        if not candidates:
            return []

        executions: list[WaveLlmExecutionSummary] = []
        llm_service = WaveLlmService(self._settings)
        with wave_session_scope(self._settings.wave_monitor_database_url) as session:
            for candidate in candidates:
                wave_id = str(candidate["wave_id"])
                if session.get(WaveMonitorORM, wave_id) is None:
                    continue
                marker = f"source-snapshot:{candidate['snapshot_id']}"
                recent_tasks = list(
                    session.scalars(
                        select(WaveLlmTaskORM)
                        .where(WaveLlmTaskORM.monitor_id == wave_id)
                        .order_by(WaveLlmTaskORM.created_at.desc())
                        .limit(50)
                    )
                )
                if any(task.provider == provider and marker in _loads_list(task.caveats_json) for task in recent_tasks):
                    continue

                model = self._settings.wave_llm_default_model
                full_text = str(candidate["snapshot_full_text"])
                task_type = (
                    "article_claim_extraction"
                    if str(candidate["source_class"]) in {"article", "community", "official"} and len(full_text) >= 600
                    else "source_summary"
                )
                prefix = (
                    f"Source title: {candidate['snapshot_title'] or candidate['memory_title']}\n"
                    f"Source URL: {candidate['snapshot_url']}\n"
                    f"Source id: {candidate['source_id']}\n"
                    f"Source class: {candidate['source_class']}\n"
                    f"Published at: {candidate['snapshot_published_at'] or 'unknown'}\n\n"
                    "Analyze this source text conservatively and emit JSON only.\n\n"
                )
                input_budget = max(0, self._settings.wave_llm_max_input_chars - len(prefix))
                task_response = llm_service.create_interpretation_task(
                    WaveLlmInterpretationTaskRequest(
                        monitor_id=wave_id,
                        task_type=task_type,  # type: ignore[arg-type]
                        provider=provider,  # type: ignore[arg-type]
                        model=model,
                        input_text=prefix + full_text[:input_budget],
                        source_ids=[str(candidate["source_id"])],
                        record_ids=[],
                        caveats=[
                            marker,
                            f"source-discovery-scheduler:{tick_id}",
                            "Scheduler-created Wave LLM task remains review-only and must not promote sources or claims directly.",
                        ],
                    )
                )
                execution_budget = 0
                if provider in LIVE_NETWORK_LLM_PROVIDERS and ((provider == "ollama" and remaining_budget > 0) or (provider != "ollama" and allow_network and remaining_budget > 0)):
                    execution_budget = 1
                execution_response = llm_service.execute_task(
                    WaveLlmTaskExecuteRequest(
                        task_id=task_response.task.task_id,
                        allow_network=allow_network,
                        request_budget=execution_budget,
                        max_retries=0,
                        caveats=["Scheduler-triggered Wave LLM execution remains bounded and review-only."],
                    )
                )
                remaining_budget = max(0, remaining_budget - execution_response.execution.used_requests)
                executions.append(execution_response.execution)
        return executions


def _upsert_candidate_row(
    session: Session,
    seed: SourceDiscoveryCandidateSeed,
    *,
    now: str,
) -> SourceMemoryORM:
    canonical_url = _canonical_source_url(seed.url)
    parent_domain = seed.parent_domain or _domain_from_url(seed.url)
    domain_scope = _domain_scope(parent_domain)
    memory = _find_existing_memory(session, source_id=seed.source_id, canonical_url=canonical_url)
    if memory is None:
        memory = SourceMemoryORM(
            source_id=seed.source_id,
            title=seed.title,
            url=seed.url,
            canonical_url=canonical_url,
            parent_domain=parent_domain,
            domain_scope=domain_scope,
            owner_lane=None,
            source_type=seed.source_type,
            source_class=seed.source_class,
            lifecycle_state=seed.lifecycle_state,
            source_health=seed.source_health,
            policy_state=seed.policy_state,
            access_result=seed.access_result,
            machine_readable_result=seed.machine_readable_result,
            source_health_score=_initial_source_health_score(seed.source_class),
            timeliness_score=_initial_timeliness_score(seed.source_class),
            first_seen_at=now,
            last_seen_at=now,
            next_check_at=now,
            health_check_fail_count=0,
            caveats_json=json.dumps(seed.caveats),
            reputation_basis_json=json.dumps([
                "Initial reputation is thin until claim outcomes accumulate.",
            ]),
            known_aliases_json=json.dumps([]),
        )
        session.add(memory)
    else:
        aliases = _loads_list(memory.known_aliases_json)
        if seed.source_id != memory.source_id:
            aliases.append(f"source-id:{seed.source_id}")
        if seed.url and seed.url != memory.url:
            aliases.append(seed.url)
        memory.title = seed.title or memory.title
        memory.url = seed.url or memory.url
        memory.canonical_url = canonical_url or memory.canonical_url
        memory.parent_domain = parent_domain or memory.parent_domain
        memory.domain_scope = domain_scope or memory.domain_scope
        memory.source_type = seed.source_type or memory.source_type
        memory.source_class = seed.source_class if seed.source_class != "unknown" else memory.source_class
        memory.lifecycle_state = seed.lifecycle_state or memory.lifecycle_state
        memory.source_health = seed.source_health or memory.source_health
        memory.policy_state = seed.policy_state or memory.policy_state
        memory.access_result = seed.access_result or memory.access_result
        memory.machine_readable_result = seed.machine_readable_result or memory.machine_readable_result
        memory.last_seen_at = now
        memory.known_aliases_json = json.dumps(sorted(set(aliases)))
        memory.caveats_json = json.dumps(sorted(set(_loads_list(memory.caveats_json) + seed.caveats)))

    if seed.wave_id:
        canonical_seed = seed.model_copy(update={"source_id": memory.source_id})
        _upsert_wave_fit(session, canonical_seed, now=now)
    return memory


def _upsert_wave_fit(session: Session, seed: SourceDiscoveryCandidateSeed, *, now: str) -> None:
    fit = session.scalar(
        select(SourceWaveFitORM).where(
            SourceWaveFitORM.source_id == seed.source_id,
            SourceWaveFitORM.wave_id == seed.wave_id,
        )
    )
    if fit is None:
        fit = SourceWaveFitORM(
            source_id=seed.source_id,
            wave_id=seed.wave_id or "",
            wave_title=seed.wave_title or "",
            fit_score=seed.wave_fit_score,
            fit_state="candidate",
            relevance_basis_json=json.dumps(seed.relevance_basis),
            last_seen_at=now,
        )
        session.add(fit)
    else:
        fit.wave_title = seed.wave_title or fit.wave_title
        fit.fit_score = seed.wave_fit_score
        fit.relevance_basis_json = json.dumps(
            sorted(set(_loads_list(fit.relevance_basis_json) + seed.relevance_basis))
        )
        fit.last_seen_at = now


def _apply_claim_outcome(
    session: Session,
    memory: SourceMemoryORM,
    request: SourceDiscoveryClaimOutcomeRequest,
    now: str,
) -> None:
    before = memory.global_reputation_score
    delta = _outcome_delta(memory.source_class, request.outcome)
    if request.outcome == "confirmed":
        memory.confirmed_claim_count += 1
    elif request.outcome == "contradicted":
        memory.contradicted_claim_count += 1
    elif request.outcome == "corrected":
        memory.corrected_claim_count += 1
        memory.correction_score = _clamp(memory.correction_score + 0.04)
    elif request.outcome == "outdated":
        memory.outdated_claim_count += 1
        if memory.source_class != "static":
            memory.timeliness_score = _clamp(memory.timeliness_score - 0.03)
    elif request.outcome == "unresolved":
        memory.unresolved_claim_count += 1
    elif request.outcome == "not_applicable":
        memory.not_applicable_claim_count += 1
        if request.wave_id:
            _lower_wave_fit_for_not_applicable(session, request.source_id, request.wave_id, now)

    memory.global_reputation_score = _clamp(memory.global_reputation_score + delta)
    memory.domain_reputation_score = _clamp(memory.domain_reputation_score + delta)
    memory.confidence_level = _confidence_level(memory)
    memory.last_reputation_event_at = now
    basis = _loads_list(memory.reputation_basis_json)
    basis.append(f"{request.outcome}: {request.claim_text[:140]}")
    memory.reputation_basis_json = json.dumps(basis[-20:])
    session.add(
        SourceReputationEventORM(
            source_id=request.source_id,
            wave_id=request.wave_id,
            event_type="claim_outcome",
            outcome=request.outcome,
            score_before=before,
            score_after=memory.global_reputation_score,
            reason=request.claim_text[:500],
            created_at=now,
        )
    )


def _lower_wave_fit_for_not_applicable(session: Session, source_id: str, wave_id: str, now: str) -> None:
    fit = session.scalar(
        select(SourceWaveFitORM).where(
            SourceWaveFitORM.source_id == source_id,
            SourceWaveFitORM.wave_id == wave_id,
        )
    )
    if fit is None:
        return
    fit.fit_score = _clamp(fit.fit_score - 0.08)
    fit.fit_state = "low_fit" if fit.fit_score < 0.35 else fit.fit_state
    fit.last_seen_at = now


def _fits_for_source(session: Session, source_id: str) -> list[SourceWaveFitORM]:
    return list(
        session.scalars(
            select(SourceWaveFitORM)
            .where(SourceWaveFitORM.source_id == source_id)
            .order_by(SourceWaveFitORM.wave_id)
        )
    )


def _build_memory_detail_response(
    session: Session,
    memory: SourceMemoryORM,
    *,
    limit: int,
) -> SourceDiscoveryMemoryDetailResponse:
    return SourceDiscoveryMemoryDetailResponse(
        memory=_serialize_memory(memory),
        wave_fits=[_serialize_wave_fit(fit) for fit in _fits_for_source(session, memory.source_id)],
        snapshots=[
            _serialize_snapshot(snapshot)
            for snapshot in session.scalars(
                select(SourceContentSnapshotORM)
                .where(SourceContentSnapshotORM.source_id == memory.source_id)
                .order_by(SourceContentSnapshotORM.fetched_at.desc())
                .limit(max(0, limit))
            )
        ],
        health_checks=[
            _serialize_health_check(check)
            for check in session.scalars(
                select(SourceHealthCheckORM)
                .where(SourceHealthCheckORM.source_id == memory.source_id)
                .order_by(SourceHealthCheckORM.checked_at.desc())
                .limit(max(0, limit))
            )
        ],
        review_actions=[
            _serialize_review_action(action)
            for action in session.scalars(
                select(SourceReviewActionORM)
                .where(SourceReviewActionORM.source_id == memory.source_id)
                .order_by(SourceReviewActionORM.created_at.desc())
                .limit(max(0, limit))
            )
        ],
        reputation_events=[
            _serialize_reputation_event(event)
            for event in session.scalars(
                select(SourceReputationEventORM)
                .where(SourceReputationEventORM.source_id == memory.source_id)
                .order_by(SourceReputationEventORM.created_at.desc())
                .limit(max(0, limit))
            )
        ],
        claim_outcomes=[
            _serialize_claim_outcome(outcome)
            for outcome in session.scalars(
                select(SourceClaimOutcomeORM)
                .where(SourceClaimOutcomeORM.source_id == memory.source_id)
                .order_by(SourceClaimOutcomeORM.assessed_at.desc())
                .limit(max(0, limit))
            )
        ],
        caveats=SOURCE_DISCOVERY_CAVEATS,
    )


def _serialize_memory(memory: SourceMemoryORM) -> SourceDiscoveryMemory:
    return SourceDiscoveryMemory(
        source_id=memory.source_id,
        title=memory.title,
        url=memory.url,
        canonical_url=memory.canonical_url or _canonical_source_url(memory.url),
        parent_domain=memory.parent_domain,
        domain_scope=memory.domain_scope or _domain_scope(memory.parent_domain),
        owner_lane=memory.owner_lane,
        source_type=memory.source_type,
        source_class=memory.source_class,  # type: ignore[arg-type]
        lifecycle_state=memory.lifecycle_state,
        source_health=memory.source_health,
        policy_state=memory.policy_state,
        access_result=memory.access_result,
        machine_readable_result=memory.machine_readable_result,
        global_reputation_score=memory.global_reputation_score,
        domain_reputation_score=memory.domain_reputation_score,
        source_health_score=memory.source_health_score,
        timeliness_score=memory.timeliness_score,
        correction_score=memory.correction_score,
        confidence_level=memory.confidence_level,
        claim_outcomes={
            "confirmed": memory.confirmed_claim_count,
            "contradicted": memory.contradicted_claim_count,
            "corrected": memory.corrected_claim_count,
            "outdated": memory.outdated_claim_count,
            "unresolved": memory.unresolved_claim_count,
            "notApplicable": memory.not_applicable_claim_count,
        },
        caveats=_loads_list(memory.caveats_json),
        reputation_basis=_loads_list(memory.reputation_basis_json),
        known_aliases=_loads_list(memory.known_aliases_json),
        first_seen_at=memory.first_seen_at,
        last_seen_at=memory.last_seen_at,
        last_reputation_event_at=memory.last_reputation_event_at,
        next_check_at=memory.next_check_at,
        health_check_fail_count=memory.health_check_fail_count,
    )


def _serialize_wave_fit(fit: SourceWaveFitORM) -> SourceDiscoveryWaveFit:
    return SourceDiscoveryWaveFit(
        source_id=fit.source_id,
        wave_id=fit.wave_id,
        wave_title=fit.wave_title,
        fit_score=fit.fit_score,
        fit_state=fit.fit_state,
        relevance_basis=_loads_list(fit.relevance_basis_json),
        last_seen_at=fit.last_seen_at,
    )


def _serialize_job(job: SourceDiscoveryJobORM) -> SourceDiscoveryJobSummary:
    return SourceDiscoveryJobSummary(
        job_id=job.job_id,
        job_type=job.job_type,
        status=job.status,
        seed_url=job.seed_url,
        wave_id=job.wave_id,
        wave_title=job.wave_title,
        discovered_source_ids=_loads_list(job.discovered_source_ids_json),
        rejected_reason=job.rejected_reason,
        request_budget=job.request_budget,
        used_requests=job.used_requests,
        started_at=job.started_at,
        finished_at=job.finished_at,
        caveats=_loads_list(job.caveats_json),
    )


def _serialize_health_check(check: SourceHealthCheckORM) -> SourceDiscoveryHealthCheckSummary:
    return SourceDiscoveryHealthCheckSummary(
        check_id=check.check_id,
        source_id=check.source_id,
        url=check.url,
        status=check.status,
        http_status=check.http_status,
        content_type=check.content_type,
        access_result=check.access_result,
        machine_readable_result=check.machine_readable_result,
        source_health=check.source_health,
        source_health_score=check.source_health_score,
        request_budget=check.request_budget,
        used_requests=check.used_requests,
        checked_at=check.checked_at,
        next_check_after=check.next_check_after,
        error_summary=check.error_summary,
        caveats=_loads_list(check.caveats_json),
    )


def _serialize_snapshot(snapshot: SourceContentSnapshotORM) -> SourceDiscoveryContentSnapshotSummary:
    return SourceDiscoveryContentSnapshotSummary(
        snapshot_id=snapshot.snapshot_id,
        source_id=snapshot.source_id,
        url=snapshot.url,
        title=snapshot.title,
        content_type=snapshot.content_type,
        extraction_method=snapshot.extraction_method,
        text_hash=snapshot.text_hash,
        text_length=snapshot.text_length,
        author=snapshot.author,
        published_at=snapshot.published_at,
        fetched_at=snapshot.fetched_at,
        request_budget=snapshot.request_budget,
        used_requests=snapshot.used_requests,
        extraction_confidence=snapshot.extraction_confidence,
        caveats=_loads_list(snapshot.caveats_json),
    )


def _serialize_reputation_event(event: SourceReputationEventORM) -> SourceDiscoveryReputationEventSummary:
    return SourceDiscoveryReputationEventSummary(
        event_id=event.event_id,
        source_id=event.source_id,
        wave_id=event.wave_id,
        event_type=event.event_type,
        outcome=event.outcome,
        score_before=event.score_before,
        score_after=event.score_after,
        reason=event.reason,
        created_at=event.created_at,
        reversed_at=event.reversed_at,
        reversal_reason=event.reversal_reason,
    )


def _serialize_claim_outcome(outcome: SourceClaimOutcomeORM) -> SourceDiscoveryClaimOutcomeSummary:
    return SourceDiscoveryClaimOutcomeSummary(
        outcome_id=outcome.outcome_id,
        source_id=outcome.source_id,
        wave_id=outcome.wave_id,
        claim_text=outcome.claim_text,
        claim_type=outcome.claim_type,
        outcome=outcome.outcome,  # type: ignore[arg-type]
        evidence_basis=outcome.evidence_basis,
        observed_at=outcome.observed_at,
        assessed_at=outcome.assessed_at,
        corroborating_source_ids=_loads_list(outcome.corroborating_source_ids_json),
        contradiction_source_ids=_loads_list(outcome.contradiction_source_ids_json),
        caveats=_loads_list(outcome.caveats_json),
    )


def _serialize_review_action(action: SourceReviewActionORM) -> SourceDiscoveryReviewActionSummary:
    return SourceDiscoveryReviewActionSummary(
        review_action_id=action.review_action_id,
        source_id=action.source_id,
        action=action.action,  # type: ignore[arg-type]
        reviewed_by=action.reviewed_by,
        reason=action.reason,
        owner_lane=action.owner_lane,
        previous_lifecycle_state=action.previous_lifecycle_state,
        new_lifecycle_state=action.new_lifecycle_state,
        previous_policy_state=action.previous_policy_state,
        new_policy_state=action.new_policy_state,
        created_at=action.created_at,
    )


def _serialize_review_claim_application(
    row: SourceReviewClaimApplicationORM,
) -> SourceDiscoveryReviewClaimApplicationSummary:
    return SourceDiscoveryReviewClaimApplicationSummary(
        application_id=row.application_id,
        review_id=row.review_id,
        task_id=row.task_id,
        source_id=row.source_id,
        wave_id=row.wave_id,
        claim_index=row.claim_index,
        claim_text=row.claim_text,
        outcome=row.outcome,  # type: ignore[arg-type]
        applied_by=row.applied_by,
        approval_reason=row.approval_reason,
        created_at=row.created_at,
    )


def _find_existing_memory(session: Session, *, source_id: str, canonical_url: str) -> SourceMemoryORM | None:
    memory = session.get(SourceMemoryORM, source_id)
    if memory is not None:
        return memory
    return session.scalar(select(SourceMemoryORM).where(SourceMemoryORM.canonical_url == canonical_url))


def _canonical_source_url(url: str) -> str:
    parsed = urlparse(url.strip())
    scheme = (parsed.scheme or "https").lower()
    netloc = parsed.netloc.lower()
    if netloc.endswith(":80") and scheme == "http":
        netloc = netloc[:-3]
    if netloc.endswith(":443") and scheme == "https":
        netloc = netloc[:-4]
    path = parsed.path or "/"
    if path != "/":
        path = path.rstrip("/") or "/"
    query_pairs = [
        (key, value)
        for key, value in parse_qsl(parsed.query, keep_blank_values=True)
        if key.casefold() not in {"utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content", "fbclid", "gclid"}
    ]
    query = urlencode(sorted(query_pairs))
    return urlunparse((scheme, netloc, path, "", query, ""))


def _domain_scope(domain: str) -> str:
    normalized = domain.casefold().strip(".")
    parts = [part for part in normalized.split(".") if part]
    if len(parts) <= 2:
        return normalized or "unknown"
    if len(parts[-1]) == 2 and parts[-2] in {"ac", "co", "com", "edu", "gov", "net", "org"}:
        return ".".join(parts[-3:])
    return ".".join(parts[-2:])


def _initial_source_health_score(source_class: str) -> float:
    return {
        "static": 0.66,
        "dataset": 0.6,
        "official": 0.58,
        "live": 0.52,
        "article": 0.5,
        "community": 0.46,
        "social_image": 0.42,
    }.get(source_class, 0.5)


def _initial_timeliness_score(source_class: str) -> float:
    return {
        "static": 0.84,
        "dataset": 0.58,
        "official": 0.56,
        "live": 0.55,
        "article": 0.52,
        "community": 0.5,
        "social_image": 0.48,
    }.get(source_class, 0.5)


def _health_score_for_result(source_class: str, source_health: str) -> float:
    if source_health == "healthy":
        return {
            "live": 0.82,
            "article": 0.72,
            "community": 0.66,
            "social_image": 0.62,
            "dataset": 0.7,
            "static": 0.78,
        }.get(source_class, 0.74)
    if source_health == "degraded":
        return 0.38
    if source_health == "rate_limited":
        return 0.25
    if source_health in {"unreachable", "blocked"}:
        return 0.1
    return 0.3


def _next_health_check_after(
    *,
    source_class: str,
    status: str,
    source_health: str,
    now: str,
    fail_count: int,
) -> str:
    current = _parse_utc_like(now) or datetime.now(tz=timezone.utc)
    healthy_hours = {
        "live": 6,
        "article": 24,
        "community": 24,
        "social_image": 12,
        "dataset": 24,
        "static": 24 * 7,
        "official": 12,
    }.get(source_class, 24)
    if status == "metadata_only":
        hours = max(1, healthy_hours // 2)
    elif status == "completed" and source_health == "healthy":
        hours = healthy_hours
    elif source_health == "rate_limited":
        hours = min(24 * 7, max(6, healthy_hours) * (2 ** max(0, fail_count - 1)))
    else:
        hours = min(24 * 7, max(2, healthy_hours // 2) * (2 ** max(0, fail_count - 1)))
    return (current + timedelta(hours=hours)).isoformat().replace("+00:00", "Z")


def _timeliness_after_health_check(
    *,
    source_class: str,
    current_score: float,
    source_health: str,
    status: str,
) -> float:
    if source_class == "static":
        return max(current_score, 0.82)
    if status == "completed" and source_health == "healthy":
        return max(current_score, 0.68 if source_class == "live" else 0.62)
    if status in {"failed", "rejected"} or source_health in {"degraded", "rate_limited", "unreachable"}:
        penalty = 0.06 if source_class in {"live", "article", "community", "social_image"} else 0.03
        return _clamp(current_score - penalty)
    return current_score


def _is_due_for_health_check(next_check_at: str | None, now: str) -> bool:
    if not next_check_at:
        return True
    due_at = _parse_utc_like(next_check_at)
    current = _parse_utc_like(now)
    if due_at is None or current is None:
        return True
    return due_at <= current


def _extract_urls_from_wave_record(record: WaveRecordORM) -> list[str]:
    urls: list[str] = []
    if record.source_url:
        urls.append(record.source_url)
    urls.extend(_collect_urls_from_text(record.content))
    try:
        payload = json.loads(record.raw_payload_json or "{}")
    except json.JSONDecodeError:
        payload = {}
    urls.extend(_collect_urls_from_object(payload))
    return _dedupe_urls(urls)


def _extract_urls_from_data_ai_item(item) -> list[str]:
    return _dedupe_urls([
        str(value)
        for value in [getattr(item, "link", None), getattr(item, "feed_url", None), getattr(item, "final_url", None)]
        if isinstance(value, str) and value.strip()
    ])


def _collect_urls_from_object(value: object) -> list[str]:
    if isinstance(value, str):
        return _collect_urls_from_text(value)
    if isinstance(value, dict):
        urls: list[str] = []
        for nested in value.values():
            urls.extend(_collect_urls_from_object(nested))
        return urls
    if isinstance(value, list):
        urls: list[str] = []
        for nested in value:
            urls.extend(_collect_urls_from_object(nested))
        return urls
    return []


def _collect_urls_from_text(value: str) -> list[str]:
    return re.findall(r"https?://[^\s<>'\"]+", value)


def _dedupe_urls(urls: list[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for url in urls:
        parsed = urlparse(url.strip())
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            continue
        canonical = _canonical_source_url(url)
        if canonical in seen:
            continue
        seen.add(canonical)
        deduped.append(canonical)
    return deduped


def _candidate_seed_from_extracted_url(
    *,
    url: str,
    source_id: str,
    title: str,
    wave_id: str | None,
    wave_title: str | None,
    discovery_reason: str,
    caveats: list[str],
) -> SourceDiscoveryCandidateSeed | None:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return None
    classification = _classify_seed_url(url)
    return SourceDiscoveryCandidateSeed(
        source_id=source_id,
        title=title or parsed.netloc,
        url=url,
        parent_domain=parsed.netloc,
        source_type=classification["source_type"],
        source_class=classification["source_class"],  # type: ignore[arg-type]
        wave_id=wave_id,
        wave_title=wave_title,
        lifecycle_state="candidate",
        source_health="unknown",
        policy_state=classification["policy_state"],
        access_result=classification["access_result"],
        machine_readable_result=classification["machine_readable_result"],
        wave_fit_score=0.56 if wave_id else 0.5,
        relevance_basis=[
            discovery_reason,
            "Extracted source remains candidate-only until health, policy, and evidence review run.",
        ],
        caveats=caveats + classification["caveats"],
    )


def _build_feed_item_snapshot(
    *,
    source_id: str,
    url: str,
    title: str | None,
    summary: str | None,
    published_at: str | None,
    fetched_at: str,
) -> SourceContentSnapshotORM | None:
    text = _normalize_text(" ".join(part for part in [title or "", summary or ""] if part))
    if not text:
        return None
    text_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return SourceContentSnapshotORM(
        snapshot_id=f"source-snapshot:{_safe_id(source_id)}:{text_hash[:16]}",
        source_id=source_id,
        url=url,
        title=title,
        content_type="application/rss+xml",
        extraction_method="feed_item_summary",
        text_hash=text_hash,
        text_length=len(text),
        full_text=text,
        author=None,
        published_at=published_at,
        fetched_at=fetched_at,
        request_budget=0,
        used_requests=0,
        extraction_confidence=_extraction_confidence(text, "feed_item_summary"),
        caveats_json=json.dumps([
            "Feed item summary snapshot is bounded source text and may omit article-body detail.",
            "Feed item summary does not replace later full-text article extraction when available.",
        ]),
    )


def _best_wave_fit(fits: list[SourceWaveFitORM]) -> SourceWaveFitORM | None:
    if not fits:
        return None
    return max(fits, key=lambda fit: fit.fit_score)


def _review_reasons(
    memory: SourceMemoryORM,
    *,
    best_fit: SourceWaveFitORM | None,
    has_snapshot: bool,
) -> list[str]:
    reasons: list[str] = []
    if memory.policy_state == "manual_review":
        reasons.append("manual review pending")
    if memory.lifecycle_state in {"discovered", "candidate", "sandboxed"}:
        reasons.append(f"lifecycle state is {memory.lifecycle_state}")
    if memory.source_health in {"degraded", "rate_limited", "unreachable", "blocked"}:
        reasons.append(f"source health is {memory.source_health}")
    if not memory.owner_lane:
        reasons.append("owner lane is not assigned")
    if memory.confidence_level == "thin":
        reasons.append("reputation confidence is still thin")
    if memory.source_class in {"article", "community", "official"} and not has_snapshot:
        reasons.append("no content snapshot is stored yet")
    if best_fit is not None and best_fit.fit_score >= 0.75:
        reasons.append("high-fit source for an active wave")
    return reasons


def _review_priority(
    memory: SourceMemoryORM,
    *,
    best_fit: SourceWaveFitORM | None,
    has_snapshot: bool,
) -> tuple[int, str]:
    score = 0
    if memory.policy_state == "manual_review":
        score += 3
    if memory.source_health in {"degraded", "rate_limited", "unreachable", "blocked"}:
        score += 3
    if memory.lifecycle_state in {"discovered", "candidate", "sandboxed"}:
        score += 2
    if not memory.owner_lane:
        score += 1
    if memory.confidence_level == "thin":
        score += 1
    if memory.source_class in {"article", "community", "official"} and not has_snapshot:
        score += 1
    if best_fit is not None and best_fit.fit_score >= 0.75:
        score += 2
    if score >= 7:
        return score, "high"
    if score >= 3:
        return score, "medium"
    return score, "low"


def _recommended_review_actions(memory: SourceMemoryORM, *, owner_lane: str | None) -> list[str]:
    actions: list[str] = []
    if memory.policy_state == "manual_review":
        actions.append("mark_reviewed")
    if memory.lifecycle_state in {"discovered", "candidate"}:
        actions.extend(["approve_candidate", "sandbox_check"])
    if not owner_lane:
        actions.append("assign_owner")
    if memory.source_health in {"degraded", "rate_limited", "unreachable", "blocked"}:
        actions.append("sandbox_check")
    actions.extend(["reject", "archive"])
    seen: set[str] = set()
    ordered: list[str] = []
    for action in actions:
        if action in seen:
            continue
        seen.add(action)
        ordered.append(action)
    return ordered


def _classify_seed_url(url: str) -> dict[str, object]:
    lowered = url.lower()
    caveats = [
        "Classification is URL-shape based in this first slice; later jobs should fetch metadata within budget.",
    ]
    if any(token in lowered for token in ("/rss", "feed", ".xml", ".atom")):
        return {
            "source_type": "rss",
            "source_class": "live",
            "access_result": "unknown",
            "machine_readable_result": "partial",
            "policy_state": "manual_review",
            "caveats": caveats + ["Possible feed candidate; parser validation still required."],
        }
    if any(token in lowered for token in (".json", ".geojson", ".csv", ".kml", ".netcdf", ".nc")):
        return {
            "source_type": "dataset",
            "source_class": "dataset",
            "access_result": "unknown",
            "machine_readable_result": "partial",
            "policy_state": "manual_review",
            "caveats": caveats + ["Possible machine-readable dataset candidate; schema validation still required."],
        }
    if any(token in lowered for token in ("twitter.com", "x.com", "instagram.com", "facebook.com", "tiktok.com")):
        return {
            "source_type": "social",
            "source_class": "social_image",
            "access_result": "unknown",
            "machine_readable_result": "unknown",
            "policy_state": "manual_review",
            "caveats": caveats + [
                "Public social source must not be accessed through login-only, app-only, CAPTCHA, or ToS-hostile routes.",
                "Social/image evidence remains candidate evidence until corroborated.",
            ],
        }
    return {
        "source_type": "web",
        "source_class": "article",
        "access_result": "unknown",
        "machine_readable_result": "unknown",
        "policy_state": "manual_review",
        "caveats": caveats + ["Article/web candidate requires allowed full-text fetch before claim assessment."],
    }


def _fetch_url(url: str, *, method: str, max_bytes: int) -> dict[str, object]:
    request = Request(url, method=method, headers={"User-Agent": HTTP_USER_AGENT})
    with urlopen(request, timeout=8) as response:
        body = response.read(max_bytes + 1)
        if len(body) > max_bytes:
            body = body[:max_bytes]
        content_type = response.headers.get("content-type")
        charset = response.headers.get_content_charset() or "utf-8"
        return {
            "status": int(response.status),
            "content_type": content_type,
            "body": body.decode(charset, errors="replace"),
        }


def _machine_readable_from_content_type(content_type: str | None, url: str) -> str:
    value = f"{content_type or ''} {url}".lower()
    if any(token in value for token in ("json", "xml", "atom", "rss", "csv", "geojson", "netcdf")):
        return "confirmed"
    if any(token in value for token in ("html", "text/plain")):
        return "partial"
    return "unknown"


def _extract_candidate_links(base_url: str, text: str) -> list[str]:
    if not text:
        return []
    links = re.findall(r"""(?:href|src)=["']([^"']+)["']""", text, flags=re.IGNORECASE)
    links.extend(re.findall(r"<link[^>]*>(https?://[^<\s]+)</link>", text, flags=re.IGNORECASE))
    links.extend(re.findall(r"https?://[^\s<>'\"]+", text))
    return [urljoin(base_url, link.strip()) for link in links]


def _extract_catalog_candidate_urls(base_url: str, text: str, *, max_discovered: int) -> tuple[list[str], str]:
    if not text.strip():
        return [], "empty"
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        payload = None
    if payload is not None:
        urls = _collect_urls_from_object(payload)
        return _bounded_candidate_urls(base_url, urls, max_discovered=max_discovered), "json"
    urls = _extract_candidate_links(base_url, text)
    looks_like_xml = bool(re.search(r"<(?:rss|feed|urlset|sitemapindex)\b", text, flags=re.IGNORECASE))
    return _bounded_candidate_urls(base_url, urls, max_discovered=max_discovered), "xml" if looks_like_xml else "html"


def _bounded_candidate_urls(base_url: str, urls: list[str], *, max_discovered: int) -> list[str]:
    discovered: list[str] = []
    base_domain = urlparse(base_url).netloc.lower()
    for url in urls:
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            continue
        normalized = url.split("#", 1)[0]
        lowered = normalized.lower()
        if normalized in discovered:
            continue
        if len(discovered) >= max_discovered:
            break
        if parsed.netloc.lower() != base_domain and not _looks_like_feed_or_data(lowered):
            continue
        discovered.append(normalized)
    return discovered


def _looks_like_feed_or_data(url: str) -> bool:
    return any(token in url for token in ("/rss", "feed", ".xml", ".atom", ".json", ".geojson", ".csv"))


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _extraction_confidence(text: str, method: str) -> float:
    if not text:
        return 0.0
    if method == "metadata_only":
        return 0.1
    if method == "social_metadata":
        return 0.34 if len(text) >= 40 else 0.18
    if method == "social_page_evidence":
        return 0.56 if len(text) >= 140 else 0.38
    if method == "feed_item_summary":
        return 0.44 if len(text) >= 120 else 0.28
    if method in {"html_article_json_ld", "live_fetch_html_article_json_ld"} and len(text) >= 400:
        return 0.92
    if method in {"html_article_readability", "live_fetch_html_article_readability"} and len(text) >= 400:
        return 0.88
    if method in {"html_article_fallback", "live_fetch_html_article_fallback"} and len(text) >= 600:
        return 0.74
    if len(text) >= 1200:
        return 0.82
    if len(text) >= 250:
        return 0.62
    return 0.35


def _extract_social_metadata(text: str, url: str) -> SourceDiscoverySocialMetadataSummary:
    display_title = (
        _extract_meta_content(text, "property", "og:title")
        or _extract_meta_content(text, "name", "twitter:title")
        or _extract_tag_text(text, "title")
    )
    description = (
        _extract_meta_content(text, "property", "og:description")
        or _extract_meta_content(text, "name", "description")
        or _extract_meta_content(text, "name", "twitter:description")
    )
    author = (
        _extract_meta_content(text, "name", "author")
        or _extract_meta_content(text, "property", "article:author")
        or _extract_meta_content(text, "name", "twitter:creator")
    )
    published_at = (
        _extract_meta_content(text, "property", "article:published_time")
        or _extract_meta_content(text, "name", "article:published_time")
        or _extract_meta_content(text, "itemprop", "datePublished")
    )
    image_url = (
        _extract_meta_content(text, "property", "og:image")
        or _extract_meta_content(text, "name", "twitter:image")
    )
    media_hints: list[str] = []
    lowered_url = url.casefold()
    if image_url or any(lowered_url.endswith(ext) for ext in (".jpg", ".jpeg", ".png", ".gif", ".webp")):
        media_hints.append("image")
    if any(token in lowered_url for token in ("video", "youtube", "vimeo", "tiktok")):
        media_hints.append("video")
    if "instagram.com" in lowered_url:
        media_hints.append("social-post")
    if "x.com" in lowered_url or "twitter.com" in lowered_url:
        media_hints.append("social-post")
    return SourceDiscoverySocialMetadataSummary(
        display_title=display_title,
        description=description,
        author=author,
        published_at=published_at,
        image_url=image_url,
        media_hints=media_hints,
    )


def _build_social_metadata_text(metadata: SourceDiscoverySocialMetadataSummary) -> str:
    parts = [
        metadata.display_title or "",
        metadata.description or "",
        metadata.author or "",
        metadata.published_at or "",
        metadata.evidence_text or "",
        " ".join(metadata.captions),
        " ".join(metadata.alt_texts),
        " ".join(metadata.media_hints),
        metadata.image_url or "",
        " ".join(metadata.media_urls),
    ]
    return _normalize_text(" ".join(part for part in parts if part))


def _load_wave_review_claims(raw: str | None) -> list[dict[str, object]]:
    if not raw:
        return []
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return []
    if not isinstance(parsed, list):
        return []
    return [item for item in parsed if isinstance(item, dict)]


def _confidence_level(memory: SourceMemoryORM) -> str:
    total = (
        memory.confirmed_claim_count
        + memory.contradicted_claim_count
        + memory.corrected_claim_count
        + memory.outdated_claim_count
        + memory.unresolved_claim_count
    )
    if total >= 25:
        return "mature"
    if total >= 8:
        return "developing"
    return "thin"


def _outcome_delta(source_class: str, outcome: str) -> float:
    if outcome == "outdated" and source_class == "static":
        return 0.0
    return OUTCOME_SCORE_DELTAS[outcome]


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, round(value, 4)))


def _domain_from_url(url: str) -> str:
    parsed = urlparse(url)
    return parsed.netloc or "unknown"


def _loads_list(raw: str | None) -> list[str]:
    if not raw:
        return []
    try:
        value = json.loads(raw)
    except json.JSONDecodeError:
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    return []


def _parse_utc_like(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
    except ValueError:
        return None


def _utc_now() -> str:
    return datetime.now(tz=timezone.utc).isoformat().replace("+00:00", "Z")


def _compact_timestamp(value: str) -> str:
    return re.sub(r"[^0-9]", "", value)[:20]


def _safe_id(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9]+", "-", value).strip("-").lower() or "unknown"
