from __future__ import annotations

import asyncio
import base64
import hashlib
import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any
from xml.etree import ElementTree
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qsl, urlencode, urljoin, urlparse, urlunparse
from urllib.request import Request, urlopen

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from src.config.settings import Settings
from src.services.content_extraction import extract_article_snapshot_from_html, extract_social_metadata_from_html
from src.services.data_ai_multi_feed_service import DataAiMultiFeedQuery, DataAiMultiFeedService
from src.services.media_evidence_service import (
    canonicalize_url as canonicalize_media_url,
    compare_media_artifacts,
    fetch_media_artifact,
    geolocate_media_artifact,
    interpret_media_artifact,
    run_media_ocr,
    sample_media_frames,
)
from src.services.rss_feed_service import parse_feed_document
from src.services.wave_llm_provider_config_service import WaveLlmProviderConfigService
from src.services.wave_llm_service import WaveLlmService
from src.source_discovery.db import session_scope
from src.source_discovery.models import (
    SourceClaimOutcomeORM,
    SourceContentSnapshotORM,
    SourceKnowledgeNodeORM,
    RuntimeSchedulerRunORM,
    RuntimeSchedulerWorkerORM,
    SourceReviewClaimApplicationORM,
    SourceReviewClaimCandidateORM,
    SourceDiscoveryJobORM,
    SourceHealthCheckORM,
    SourceMemoryORM,
    SourceMediaArtifactORM,
    SourceMediaComparisonORM,
    SourceMediaDuplicateClusterORM,
    SourceMediaGeolocationRunORM,
    SourceMediaInterpretationORM,
    SourceMediaOcrRunORM,
    SourceMediaSequenceORM,
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
    SourceDiscoveryDiscoveryOverviewResponse,
    SourceDiscoveryDiscoveryQueueItem,
    SourceDiscoveryDiscoveryQueueResponse,
    SourceDiscoveryDiscoveryRunSummary,
    SourceDiscoveryDiscoveryRunsResponse,
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
    SourceDiscoveryKnowledgeNodeDetailResponse,
    SourceDiscoveryKnowledgeBackfillRequest,
    SourceDiscoveryKnowledgeBackfillResponse,
    SourceDiscoveryMediaArtifactDetailResponse,
    SourceDiscoveryMediaArtifactFetchRequest,
    SourceDiscoveryMediaArtifactFetchResponse,
    SourceDiscoveryMediaArtifactListResponse,
    SourceDiscoveryMediaArtifactSummary,
    SourceDiscoveryMediaCompareJobRequest,
    SourceDiscoveryMediaCompareJobResponse,
    SourceDiscoveryMediaComparisonDetailResponse,
    SourceDiscoveryMediaComparisonSummary,
    SourceDiscoveryMediaDuplicateClusterSummary,
    SourceDiscoveryMediaFrameSampleJobRequest,
    SourceDiscoveryMediaFrameSampleJobResponse,
    SourceDiscoveryMediaGeolocateJobRequest,
    SourceDiscoveryMediaGeolocateJobResponse,
    SourceDiscoveryMediaGeolocationDetailResponse,
    SourceDiscoveryMediaGeolocationRunSummary,
    SourceDiscoveryMediaInterpretationJobRequest,
    SourceDiscoveryMediaInterpretationJobResponse,
    SourceDiscoveryMediaInterpretationSummary,
    SourceDiscoveryMediaOcrBlock,
    SourceDiscoveryMediaOcrJobRequest,
    SourceDiscoveryMediaOcrJobResponse,
    SourceDiscoveryMediaOcrRunSummary,
    SourceDiscoveryMediaSequenceDetailResponse,
    SourceDiscoveryMediaSequenceSummary,
    SourceDiscoveryAutoMediaSignalSummary,
    SourceDiscoveryKnowledgeNodeListResponse,
    SourceDiscoveryKnowledgeNodeMember,
    SourceDiscoveryKnowledgeNodeSummary,
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
    SourceDiscoveryReviewClaimCandidateSummary,
    SourceDiscoveryReviewClaimImportRequest,
    SourceDiscoveryReviewClaimImportResponse,
    SourceDiscoveryReviewQueueItem,
    SourceDiscoveryReviewQueueResponse,
    SourceDiscoverySocialMetadataJobRequest,
    SourceDiscoverySocialMetadataJobResponse,
    SourceDiscoverySocialMetadataSummary,
    SourceDiscoverySchedulerTickRequest,
    SourceDiscoverySchedulerTickResponse,
    SourceDiscoveryScopeHints,
    SourceDiscoverySeedBatchRequest,
    SourceDiscoverySeedBatchResponse,
    SourceDiscoverySeedUrlJobRequest,
    SourceDiscoverySeedUrlJobResponse,
    SourceDiscoverySitemapScanRequest,
    SourceDiscoverySitemapScanResponse,
    SourceDiscoveryNextAction,
    SourceDiscoveryPriority,
    SourceDiscoveryStructureScanRequest,
    SourceDiscoveryStructureScanResponse,
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
PUBLIC_DISCOVERY_CADENCE_HOURS = {
    "feed_link_scan": 6,
    "sitemap_scan": 12,
    "catalog_scan": 24,
}

OUTCOME_SCORE_DELTAS = {
    "confirmed": 0.06,
    "contradicted": -0.10,
    "corrected": -0.03,
    "outdated": -0.02,
    "unresolved": 0.0,
    "not_applicable": 0.0,
}


@dataclass
class _DiscoveryPriorityContext:
    best_fit_by_source_id: dict[str, SourceWaveFitORM | None] = field(default_factory=dict)
    root_domain_counts: dict[str, int] = field(default_factory=dict)
    root_tag_counts: dict[str, int] = field(default_factory=dict)


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
            context = _build_discovery_priority_context(session)
            return SourceDiscoveryMemoryOverviewResponse(
                metadata={
                    "source": "source-discovery-memory",
                    "storageMode": "persistent-sqlite",
                    "reputationMode": "claim-outcome-v1",
                    "count": len(memories),
                },
                memories=[_serialize_memory(session, memory, context=context) for memory in memories],
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
            context = _build_discovery_priority_context(session)
            return SourceDiscoveryMemoryListResponse(
                metadata={
                    "source": "source-discovery-memory-list",
                    "count": len(memories),
                    "ownerLane": owner_lane,
                    "sourceClass": source_class,
                    "lifecycleState": lifecycle_state,
                },
                memories=[_serialize_memory(session, memory, context=context) for memory in memories],
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
                    knowledge_nodes=detail.knowledge_nodes,
                    media_artifacts=detail.media_artifacts,
                    media_clusters=detail.media_clusters,
                    media_comparisons=detail.media_comparisons,
                    auto_media_signals=detail.auto_media_signals,
                    media_sequences=detail.media_sequences,
                    media_ocr_runs=detail.media_ocr_runs,
                    media_interpretations=detail.media_interpretations,
                    media_geolocations=detail.media_geolocations,
                    health_checks=detail.health_checks,
                    review_actions=detail.review_actions,
                    reputation_events=detail.reputation_events,
                    claim_outcomes=detail.claim_outcomes,
                    pending_review_claims=detail.pending_review_claims,
                    pending_claim_count=detail.pending_claim_count,
                    latest_review_claim_at=detail.latest_review_claim_at,
                    caveats=detail.caveats + [
                        "Export packet is a source-review handoff artifact, not proof that the source is true or production-ready.",
                    ],
                ),
                caveats=SOURCE_DISCOVERY_CAVEATS,
            )

    def knowledge_overview(
        self,
        *,
        limit: int = 100,
        source_id: str | None = None,
    ) -> SourceDiscoveryKnowledgeNodeListResponse:
        with session_scope(self._settings.source_discovery_database_url) as session:
            stmt = select(SourceKnowledgeNodeORM).order_by(SourceKnowledgeNodeORM.last_seen_at.desc(), SourceKnowledgeNodeORM.node_id)
            if source_id:
                _ensure_knowledge_nodes_for_source(session, source_id)
                stmt = stmt.where(
                    SourceKnowledgeNodeORM.node_id.in_(
                        select(SourceContentSnapshotORM.knowledge_node_id).where(
                            SourceContentSnapshotORM.source_id == source_id,
                            SourceContentSnapshotORM.knowledge_node_id.is_not(None),
                        )
                    )
                )
            nodes = list(session.scalars(stmt.limit(max(0, limit))))
            return SourceDiscoveryKnowledgeNodeListResponse(
                metadata={
                    "source": "source-discovery-knowledge-overview",
                    "count": len(nodes),
                    "sourceId": source_id,
                },
                nodes=[_serialize_knowledge_node(session, node) for node in nodes],
                caveats=SOURCE_DISCOVERY_CAVEATS + [
                    "Knowledge nodes are duplicate-aware content clusters; they preserve corroboration lineage but do not prove event truth.",
                ],
            )

    def knowledge_detail(self, node_id: str) -> SourceDiscoveryKnowledgeNodeDetailResponse:
        with session_scope(self._settings.source_discovery_database_url) as session:
            node = session.get(SourceKnowledgeNodeORM, node_id)
            if node is None:
                raise ValueError(f"Unknown node_id: {node_id}")
            pending_claims = _pending_review_claim_candidates_for_node(session, node.node_id)
            return SourceDiscoveryKnowledgeNodeDetailResponse(
                node=_serialize_knowledge_node(session, node),
                members=_knowledge_node_members(session, node.node_id),
                pending_claim_count=len(pending_claims),
                latest_review_claim_at=pending_claims[0].created_at if pending_claims else None,
                caveats=SOURCE_DISCOVERY_CAVEATS + [
                    "Duplicate classes are heuristic workflow aids and should be reviewed before they affect downstream interpretation.",
                ],
            )

    def upsert_candidate(self, seed: SourceDiscoveryCandidateSeed) -> SourceDiscoveryMemory:
        with session_scope(self._settings.source_discovery_database_url) as session:
            memory = _upsert_candidate_row(session, seed, now=_utc_now())
            session.flush()
            return _serialize_memory(session, memory)

    def upsert_candidates(self, seeds: list[SourceDiscoveryCandidateSeed]) -> list[SourceDiscoveryMemory]:
        with session_scope(self._settings.source_discovery_database_url) as session:
            now = _utc_now()
            memories = [_upsert_candidate_row(session, seed, now=now) for seed in seeds]
            session.flush()
            context = _build_discovery_priority_context(session)
            return [_serialize_memory(session, memory, context=context) for memory in memories]

    def bulk_seed_candidates(
        self,
        request: SourceDiscoverySeedBatchRequest,
    ) -> SourceDiscoverySeedBatchResponse:
        with session_scope(self._settings.source_discovery_database_url) as session:
            now = _utc_now()
            created_count = 0
            updated_count = 0
            memories: list[SourceMemoryORM] = []
            packet_caveats = list(request.packet_caveats)
            if request.packet_provenance:
                packet_caveats.append(f"Seed packet provenance: {request.packet_provenance}")
            if request.imported_by:
                packet_caveats.append(f"Seed packet imported by: {request.imported_by}")
            for raw_seed in request.seeds:
                existing = _find_existing_memory(
                    session,
                    source_id=raw_seed.source_id,
                    canonical_url=_canonical_source_url(raw_seed.url),
                )
                if existing is None:
                    created_count += 1
                else:
                    updated_count += 1
                seed = raw_seed.model_copy(
                    update={
                        "caveats": sorted(set(raw_seed.caveats + list(request.caveats) + packet_caveats)),
                        "seed_packet_id": raw_seed.seed_packet_id or request.packet_id,
                        "seed_packet_title": raw_seed.seed_packet_title or request.packet_title,
                    }
                )
                memories.append(_upsert_candidate_row(session, seed, now=now))
                session.flush()
            session.flush()
            context = _build_discovery_priority_context(session)
            return SourceDiscoverySeedBatchResponse(
                memories=[_serialize_memory(session, memory, context=context) for memory in memories],
                created_count=created_count,
                updated_count=updated_count,
                caveats=SOURCE_DISCOVERY_CAVEATS + [
                    "Bulk seed ingestion is registry-only and does not auto-run discovery jobs or approve sources.",
                ],
            )

    def discovery_overview(self, *, limit: int = 100) -> SourceDiscoveryDiscoveryOverviewResponse:
        with session_scope(self._settings.source_discovery_database_url) as session:
            context = _build_discovery_priority_context(session)
            memories = list(
                session.scalars(
                    select(SourceMemoryORM)
                    .where(SourceMemoryORM.discovery_role == "root")
                    .order_by(SourceMemoryORM.last_seen_at.desc(), SourceMemoryORM.source_id)
                )
            )
            jobs = list(
                session.scalars(
                    select(SourceDiscoveryJobORM)
                    .where(SourceDiscoveryJobORM.job_type.in_(["structure_scan", "feed_link_scan", "sitemap_scan", "catalog_scan"]))
                    .order_by(SourceDiscoveryJobORM.started_at.desc())
                    .limit(20)
                )
            )
            now = _utc_now()
            counts_by_seed_family: dict[str, int] = {}
            counts_by_platform_family: dict[str, int] = {}
            counts_by_next_action: dict[str, int] = {}
            counts_by_intake_disposition: dict[str, int] = {}
            counts_by_owner_lane: dict[str, int] = {}
            total_root_count = 0
            due_root_count = 0
            pending_structure_scan_count = 0
            eligible_public_followup_count = 0
            blocked_root_count = 0
            hold_review_root_count = 0

            for memory in memories:
                total_root_count += 1
                action = _suggest_discovery_action(memory)
                counts_by_seed_family[memory.seed_family or "other"] = counts_by_seed_family.get(memory.seed_family or "other", 0) + 1
                counts_by_platform_family[memory.platform_family or "unknown"] = counts_by_platform_family.get(memory.platform_family or "unknown", 0) + 1
                counts_by_next_action[action] = counts_by_next_action.get(action, 0) + 1
                counts_by_intake_disposition[memory.intake_disposition] = counts_by_intake_disposition.get(memory.intake_disposition, 0) + 1
                owner_key = memory.owner_lane or "unassigned"
                counts_by_owner_lane[owner_key] = counts_by_owner_lane.get(owner_key, 0) + 1
                if memory.intake_disposition == "blocked":
                    blocked_root_count += 1
                if memory.intake_disposition == "hold_review":
                    hold_review_root_count += 1
                if _is_scheduler_structure_scan_candidate(memory):
                    pending_structure_scan_count += 1
                    due_root_count += 1
                elif _is_scheduler_public_discovery_candidate(memory, now):
                    eligible_public_followup_count += 1
                    due_root_count += 1

            return SourceDiscoveryDiscoveryOverviewResponse(
                metadata={
                    "source": "source-discovery-discovery-overview",
                    "count": total_root_count,
                },
                total_root_count=total_root_count,
                due_root_count=due_root_count,
                pending_structure_scan_count=pending_structure_scan_count,
                eligible_public_followup_count=eligible_public_followup_count,
                blocked_root_count=blocked_root_count,
                hold_review_root_count=hold_review_root_count,
                counts_by_seed_family=counts_by_seed_family,
                counts_by_platform_family=counts_by_platform_family,
                counts_by_next_action=counts_by_next_action,
                counts_by_intake_disposition=counts_by_intake_disposition,
                counts_by_owner_lane=counts_by_owner_lane,
                recent_runs=[_serialize_discovery_run(session, job) for job in jobs],
                caveats=SOURCE_DISCOVERY_CAVEATS + [
                    "Discovery overview counts bounded public-web roots only; it is not a crawler status board.",
                ],
            )

    def discovery_queue(
        self,
        *,
        limit: int = 100,
        eligible_only: bool = False,
        seed_family: str | None = None,
        platform_family: str | None = None,
        next_action: str | None = None,
        owner_lane: str | None = None,
        priority: str | None = None,
        policy_state: str | None = None,
        lifecycle_state: str | None = None,
    ) -> SourceDiscoveryDiscoveryQueueResponse:
        with session_scope(self._settings.source_discovery_database_url) as session:
            context = _build_discovery_priority_context(session)
            now = _utc_now()
            stmt = (
                select(SourceMemoryORM)
                .where(SourceMemoryORM.discovery_role == "root")
                .order_by(SourceMemoryORM.last_seen_at.desc(), SourceMemoryORM.source_id)
            )
            if owner_lane:
                stmt = stmt.where(SourceMemoryORM.owner_lane == owner_lane)
            if seed_family:
                stmt = stmt.where(SourceMemoryORM.seed_family == seed_family)
            if platform_family:
                stmt = stmt.where(SourceMemoryORM.platform_family == platform_family)
            if policy_state:
                stmt = stmt.where(SourceMemoryORM.policy_state == policy_state)
            if lifecycle_state:
                stmt = stmt.where(SourceMemoryORM.lifecycle_state == lifecycle_state)
            memories = list(session.scalars(stmt.limit(max(0, limit) * 8)))
            items: list[SourceDiscoveryDiscoveryQueueItem] = []
            for memory in memories:
                suggested_action = _suggest_discovery_action(memory)
                blocked_reasons = _discovery_blocked_reasons(memory, now)
                is_eligible = _is_scheduler_structure_scan_candidate(memory) or _is_scheduler_public_discovery_candidate(memory, now)
                if eligible_only and not is_eligible:
                    continue
                score, priority_label, basis = _compute_discovery_priority(session, memory, now=now, context=context)
                if next_action and suggested_action != next_action:
                    continue
                if priority and priority_label != priority:
                    continue
                best_fit = context.best_fit_by_source_id.get(memory.source_id)
                why_eligible = _discovery_eligibility_reasons(memory, now)
                item = SourceDiscoveryDiscoveryQueueItem(
                    source_id=memory.source_id,
                    title=memory.title,
                    url=memory.url,
                    owner_lane=memory.owner_lane,
                    source_type=memory.source_type,
                    source_class=memory.source_class,  # type: ignore[arg-type]
                    lifecycle_state=memory.lifecycle_state,
                    policy_state=memory.policy_state,
                    intake_disposition=memory.intake_disposition,  # type: ignore[arg-type]
                    auth_requirement=memory.auth_requirement,  # type: ignore[arg-type]
                    captcha_requirement=memory.captcha_requirement,  # type: ignore[arg-type]
                    discovery_role=memory.discovery_role,  # type: ignore[arg-type]
                    seed_family=memory.seed_family,  # type: ignore[arg-type]
                    seed_packet_id=memory.seed_packet_id,
                    seed_packet_title=memory.seed_packet_title,
                    platform_family=memory.platform_family,  # type: ignore[arg-type]
                    source_family_tags=_loads_list(memory.source_family_tags_json),
                    scope_hints=_loads_scope_hints(memory.scope_hints_json),
                    structure_hints=_loads_list(memory.structure_hints_json),
                    source_health=memory.source_health,
                    source_health_score=memory.source_health_score,
                    global_reputation_score=memory.global_reputation_score,
                    domain_reputation_score=memory.domain_reputation_score,
                    best_wave_id=best_fit.wave_id if best_fit else None,
                    best_wave_title=best_fit.wave_title if best_fit else None,
                    best_wave_fit_score=best_fit.fit_score if best_fit else None,
                    next_discovery_action=suggested_action,  # type: ignore[arg-type]
                    discovery_priority_score=score,
                    discovery_priority=priority_label,  # type: ignore[arg-type]
                    discovery_priority_basis=basis,
                    why_eligible=why_eligible,
                    why_prioritized=basis,
                    blocked_reasons=blocked_reasons,
                    last_discovery_outcome=memory.last_discovery_outcome,
                    last_discovery_scan_at=memory.last_discovery_scan_at,
                    next_discovery_scan_at=memory.next_discovery_scan_at,
                    discovery_scan_fail_count=memory.discovery_scan_fail_count,
                )
                items.append(item)
            items = sorted(
                items,
                key=lambda item: (-item.discovery_priority_score, -(item.best_wave_fit_score or 0.0), item.title.casefold()),
            )[: max(0, limit)]
            return SourceDiscoveryDiscoveryQueueResponse(
                metadata={
                    "source": "source-discovery-discovery-queue",
                    "count": len(items),
                    "eligibleOnly": eligible_only,
                    "seedFamily": seed_family,
                    "platformFamily": platform_family,
                    "nextAction": next_action,
                    "ownerLane": owner_lane,
                    "priority": priority,
                    "policyState": policy_state,
                    "lifecycleState": lifecycle_state,
                },
                items=items,
                caveats=SOURCE_DISCOVERY_CAVEATS + [
                    "Discovery queue items explain bounded scheduling choices; they do not approve or trust a source by themselves.",
                ],
            )

    def discovery_runs(self, *, limit: int = 50) -> SourceDiscoveryDiscoveryRunsResponse:
        with session_scope(self._settings.source_discovery_database_url) as session:
            jobs = list(
                session.scalars(
                    select(SourceDiscoveryJobORM)
                    .where(SourceDiscoveryJobORM.job_type.in_(["structure_scan", "feed_link_scan", "sitemap_scan", "catalog_scan"]))
                    .order_by(SourceDiscoveryJobORM.started_at.desc())
                    .limit(max(0, limit))
                )
            )
            return SourceDiscoveryDiscoveryRunsResponse(
                metadata={
                    "source": "source-discovery-discovery-runs",
                    "count": len(jobs),
                },
                runs=[_serialize_discovery_run(session, job) for job in jobs],
                caveats=SOURCE_DISCOVERY_CAVEATS + [
                    "Discovery run history is operator-facing review metadata and does not certify source truth.",
                ],
            )

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
        source_id = request.source_id or _generated_source_id_for_url(request.seed_url)
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
            auth_requirement=classification["auth_requirement"],  # type: ignore[arg-type]
            captcha_requirement=classification["captcha_requirement"],  # type: ignore[arg-type]
            intake_disposition=classification["intake_disposition"],  # type: ignore[arg-type]
            wave_fit_score=0.55 if request.wave_id else 0.5,
            relevance_basis=[
                request.discovery_reason,
                "Seed URL job created a candidate only; no automatic polling was enabled.",
            ],
            caveats=caveats + classification["caveats"],
            discovery_methods=["seed_url"],
            discovery_role=request.discovery_role,
            seed_family=request.seed_family,
            platform_family=request.platform_family,
            source_family_tags=request.source_family_tags,
            scope_hints=request.scope_hints,
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
                outcome_summary=f"Registered {memory.discovery_role} candidate from explicit seed URL.",
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
                memory=_serialize_memory(session, memory),
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
            if memory.intake_disposition == "blocked" or memory.auth_requirement == "login_required":
                status = "rejected"
                access_result = "blocked"
                source_health = "blocked"
                source_health_score = 0.0
                health_check_fail_count += 1
                error_summary = "Health checks skip login-required or blocked-intake sources."
                caveats.append("Skipped before network access because the source is outside the public no-auth intake policy.")
            elif memory.captcha_requirement == "captcha_required":
                status = "rejected"
                access_result = "blocked"
                source_health = "blocked"
                source_health_score = 0.0
                health_check_fail_count += 1
                error_summary = "Health checks skip CAPTCHA-gated sources."
                caveats.append("Skipped before network access because the source appears to require CAPTCHA interaction.")
            elif parsed.scheme not in {"http", "https"} or not parsed.netloc:
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
                    auth_requirement=classification["auth_requirement"],  # type: ignore[arg-type]
                    captcha_requirement=classification["captcha_requirement"],  # type: ignore[arg-type]
                    intake_disposition=classification["intake_disposition"],  # type: ignore[arg-type]
                    wave_fit_score=0.52 if request.wave_id else 0.5,
                    relevance_basis=[
                        request.discovery_reason,
                        "Bounded expansion discovered this URL but did not poll or trust it.",
                    ],
                    caveats=caveats + classification["caveats"] + [
                        "Expansion jobs create review candidates only; child sources require health checks before scheduling.",
                    ],
                    discovery_methods=["bounded_expansion"],
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
                outcome_summary="Rejected invalid feed URL before any discovery work ran.",
                caveats_json=json.dumps(["Rejected before feed parsing or candidate creation."]),
            )
            with session_scope(self._settings.source_discovery_database_url) as session:
                _apply_public_discovery_scan_failure_for_url(
                    session,
                    request.feed_url,
                    now=now,
                    scan_kind="feed_link_scan",
                    outcome_summary="Rejected invalid feed URL before any discovery work ran.",
                )
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
                outcome_summary=f"Feed parsing failed: {str(exc)[:160]}",
                caveats_json=json.dumps(caveats + [
                    "Feed parsing failed; no candidates or snapshots were created.",
                ]),
            )
            with session_scope(self._settings.source_discovery_database_url) as session:
                _apply_public_discovery_scan_failure_for_url(
                    session,
                    request.feed_url,
                    now=now,
                    scan_kind="feed_link_scan",
                    outcome_summary=f"Feed parsing failed: {str(exc)[:160]}",
                )
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
                source_id=_generated_source_id_for_url(canonical_url),
                title=record.title or parsed_feed.feed_title or parsed.netloc,
                wave_id=request.wave_id,
                wave_title=request.wave_title,
                discovery_reason=request.discovery_reason,
                caveats=[
                    "Feed link scan is bounded to known public feed items and creates review candidates only.",
                    "Feed item text remains source-reported context and does not prove event truth or attribution.",
                ] + caveats,
                discovery_methods=["feed_link_scan"],
                structure_hints=["feed_item_link"],
            )
            if seed is None:
                continue
            seeds.append(seed)
            if request.capture_item_summaries:
                summary_candidates.append((canonical_url, record))

        with session_scope(self._settings.source_discovery_database_url) as session:
            novel_candidate_count = _count_novel_candidate_seeds(session, seeds)
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
                    _assign_snapshot_to_knowledge_node(
                        session,
                        snapshot,
                        memory=memory,
                        normalized_text=snapshot.full_text,
                        now=now,
                    )
                    session.merge(snapshot)
                    snapshots.append(snapshot)
            outcome_summary = (
                f"Feed follow-up scanned {len(records)} items and produced {novel_candidate_count} novel candidates."
            )
            _apply_public_discovery_scan_success_for_url(
                session,
                request.feed_url,
                now=now,
                scan_kind="feed_link_scan",
                outcome_summary=outcome_summary,
                novel_candidate_count=novel_candidate_count,
            )
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
                outcome_summary=outcome_summary,
                caveats_json=json.dumps(caveats + [
                    "Feed link scan is bounded to feed items and does not auto-activate or poll discovered links.",
                ]),
            )
            session.add(job)
            session.flush()
            return SourceDiscoveryFeedLinkScanResponse(
                job=_serialize_job(job),
                memories=[_serialize_memory(session, memory) for memory in memories],
                snapshots=[_serialize_snapshot(session, snapshot) for snapshot in snapshots],
                feed_type=parsed_feed.feed_type,
                feed_title=parsed_feed.feed_title,
                scanned_item_count=len(records),
                extracted_url_count=len(extracted_urls),
                caveats=SOURCE_DISCOVERY_CAVEATS,
            )

    def run_sitemap_scan_job(
        self,
        request: SourceDiscoverySitemapScanRequest,
    ) -> SourceDiscoverySitemapScanResponse:
        now = _utc_now()
        parsed = urlparse(request.sitemap_url)
        job_id = f"source-sitemap-scan:{_safe_id(request.sitemap_url)}:{_compact_timestamp(now)}"
        caveats = list(request.caveats)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            job = SourceDiscoveryJobORM(
                job_id=job_id,
                job_type="sitemap_scan",
                status="rejected",
                seed_url=request.sitemap_url,
                wave_id=request.wave_id,
                wave_title=request.wave_title,
                discovered_source_ids_json=json.dumps([]),
                rejected_reason="Sitemap URL must be an absolute http(s) URL.",
                request_budget=request.request_budget,
                used_requests=0,
                started_at=now,
                finished_at=now,
                outcome_summary="Rejected invalid sitemap URL before any discovery work ran.",
                caveats_json=json.dumps(["Rejected before sitemap parsing or candidate creation."]),
            )
            with session_scope(self._settings.source_discovery_database_url) as session:
                _apply_public_discovery_scan_failure_for_url(
                    session,
                    request.sitemap_url,
                    now=now,
                    scan_kind="sitemap_scan",
                    outcome_summary="Rejected invalid sitemap URL before any discovery work ran.",
                )
                session.add(job)
                session.flush()
                return SourceDiscoverySitemapScanResponse(
                    job=_serialize_job(job),
                    memories=[],
                    sitemap_type="unknown",
                    scanned_url_count=0,
                    extracted_url_count=0,
                    discovered_sitemap_urls=[],
                    caveats=SOURCE_DISCOVERY_CAVEATS,
                )

        used_requests = 0
        try:
            if request.fixture_text is not None:
                document = request.fixture_text
            elif request.request_budget > 0:
                fetched = _fetch_url(request.sitemap_url, method="GET", max_bytes=MAX_FETCH_BYTES)
                document = fetched["body"]
                used_requests = 1
            else:
                raise ValueError("Sitemap scan requires fixture_text or request_budget > 0.")
            sitemap_urls, sitemap_type, scanned_url_count = _extract_sitemap_candidate_urls(
                request.sitemap_url,
                document,
                max_discovered=max(0, request.max_discovered),
            )
        except Exception as exc:  # noqa: BLE001
            job = SourceDiscoveryJobORM(
                job_id=job_id,
                job_type="sitemap_scan",
                status="failed",
                seed_url=request.sitemap_url,
                wave_id=request.wave_id,
                wave_title=request.wave_title,
                discovered_source_ids_json=json.dumps([]),
                rejected_reason=str(exc)[:300],
                request_budget=request.request_budget,
                used_requests=used_requests,
                started_at=now,
                finished_at=now,
                outcome_summary=f"Sitemap parsing failed: {str(exc)[:160]}",
                caveats_json=json.dumps(caveats + [
                    "Sitemap parsing failed; no candidates were created.",
                ]),
            )
            with session_scope(self._settings.source_discovery_database_url) as session:
                _apply_public_discovery_scan_failure_for_url(
                    session,
                    request.sitemap_url,
                    now=now,
                    scan_kind="sitemap_scan",
                    outcome_summary=f"Sitemap parsing failed: {str(exc)[:160]}",
                )
                session.add(job)
                session.flush()
                return SourceDiscoverySitemapScanResponse(
                    job=_serialize_job(job),
                    memories=[],
                    sitemap_type="unknown",
                    scanned_url_count=0,
                    extracted_url_count=0,
                    discovered_sitemap_urls=[],
                    caveats=SOURCE_DISCOVERY_CAVEATS,
                )

        seeds: list[SourceDiscoveryCandidateSeed] = []
        discovered_sitemap_urls: list[str] = []
        for url in sitemap_urls:
            canonical_url = _canonical_source_url(url)
            structure_hints = ["sitemap_child"] if "sitemap" in canonical_url.casefold() else ["sitemap_entry_link"]
            seed = _candidate_seed_from_extracted_url(
                url=canonical_url,
                source_id=_generated_source_id_for_url(canonical_url),
                title=parsed.netloc,
                wave_id=request.wave_id,
                wave_title=request.wave_title,
                discovery_reason=request.discovery_reason,
                caveats=[
                    "Sitemap scan is bounded to one allowed public sitemap or sitemap index and creates candidates only.",
                    "Sitemap links are discovery surfaces, not proof that linked sources are trustworthy or maintained.",
                ] + caveats,
                discovery_methods=["sitemap_scan"],
                structure_hints=structure_hints,
            )
            if seed is None:
                continue
            if seed.source_type == "sitemap":
                discovered_sitemap_urls.append(canonical_url)
            seeds.append(seed)

        with session_scope(self._settings.source_discovery_database_url) as session:
            novel_candidate_count = _count_novel_candidate_seeds(session, seeds)
            memories = [_upsert_candidate_row(session, seed, now=now) for seed in seeds]
            outcome_summary = (
                f"Sitemap follow-up scanned {scanned_url_count} URLs and produced {novel_candidate_count} novel candidates."
            )
            _apply_public_discovery_scan_success_for_url(
                session,
                request.sitemap_url,
                now=now,
                scan_kind="sitemap_scan",
                outcome_summary=outcome_summary,
                novel_candidate_count=novel_candidate_count,
            )
            job = SourceDiscoveryJobORM(
                job_id=job_id,
                job_type="sitemap_scan",
                status="completed",
                seed_url=request.sitemap_url,
                wave_id=request.wave_id,
                wave_title=request.wave_title,
                discovered_source_ids_json=json.dumps([memory.source_id for memory in memories]),
                rejected_reason=None,
                request_budget=max(0, request.request_budget),
                used_requests=used_requests,
                started_at=now,
                finished_at=now,
                outcome_summary=outcome_summary,
                caveats_json=json.dumps(caveats + [
                    "Sitemap scan is bounded and candidate-only; it does not fetch or activate child links.",
                ]),
            )
            session.add(job)
            session.flush()
            return SourceDiscoverySitemapScanResponse(
                job=_serialize_job(job),
                memories=[_serialize_memory(session, memory) for memory in memories],
                sitemap_type=sitemap_type,
                scanned_url_count=scanned_url_count,
                extracted_url_count=len(sitemap_urls),
                discovered_sitemap_urls=_dedupe_urls(discovered_sitemap_urls),
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
        root_platform_family = "unknown"
        with session_scope(self._settings.source_discovery_database_url) as session:
            root_memory = _find_memory_by_canonical_url(session, request.catalog_url)
            if root_memory is not None and root_memory.platform_family:
                root_platform_family = root_memory.platform_family
            else:
                root_platform_family = _detect_platform_family_from_url(request.catalog_url)
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
                outcome_summary="Rejected invalid catalog URL before any discovery work ran.",
                caveats_json=json.dumps(["Rejected before catalog parsing or candidate creation."]),
            )
            with session_scope(self._settings.source_discovery_database_url) as session:
                _apply_public_discovery_scan_failure_for_url(
                    session,
                    request.catalog_url,
                    now=now,
                    scan_kind="catalog_scan",
                    outcome_summary="Rejected invalid catalog URL before any discovery work ran.",
                )
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
                platform_family=root_platform_family,
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
                outcome_summary=f"Catalog parsing failed: {str(exc)[:160]}",
                caveats_json=json.dumps(caveats + [
                    "Catalog parsing failed; no candidates were created.",
                ]),
            )
            with session_scope(self._settings.source_discovery_database_url) as session:
                _apply_public_discovery_scan_failure_for_url(
                    session,
                    request.catalog_url,
                    now=now,
                    scan_kind="catalog_scan",
                    outcome_summary=f"Catalog parsing failed: {str(exc)[:160]}",
                )
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
                source_id=_generated_source_id_for_url(canonical_url),
                title=parsed.netloc,
                wave_id=request.wave_id,
                wave_title=request.wave_title,
                discovery_reason=request.discovery_reason,
                caveats=[
                    "Catalog scan is bounded to one allowed public page or API response and creates candidates only.",
                    "Catalog links are not recursively crawled or automatically scheduled.",
                ] + caveats,
                discovery_methods=["catalog_scan"],
                structure_hints=["catalog_link"],
                platform_family=root_platform_family,
            )
            if seed is not None:
                seeds.append(
                    _apply_platform_seed_overrides(
                        seed,
                        url=canonical_url,
                        platform_family=root_platform_family,
                        discovery_method="catalog_scan",
                    )
                )

        with session_scope(self._settings.source_discovery_database_url) as session:
            novel_candidate_count = _count_novel_candidate_seeds(session, seeds)
            memories = [_upsert_candidate_row(session, seed, now=now) for seed in seeds]
            outcome_summary = (
                f"Catalog follow-up extracted {len(catalog_urls)} URLs and produced {novel_candidate_count} novel candidates."
            )
            _apply_public_discovery_scan_success_for_url(
                session,
                request.catalog_url,
                now=now,
                scan_kind="catalog_scan",
                outcome_summary=outcome_summary,
                novel_candidate_count=novel_candidate_count,
            )
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
                outcome_summary=outcome_summary,
                caveats_json=json.dumps(caveats + [
                    "Catalog scan is bounded and candidate-only; it does not fetch or activate child sources.",
                ]),
            )
            session.add(job)
            session.flush()
            return SourceDiscoveryCatalogScanResponse(
                job=_serialize_job(job),
                memories=[_serialize_memory(session, memory) for memory in memories],
                catalog_type=catalog_type,
                extracted_url_count=len(catalog_urls),
                caveats=SOURCE_DISCOVERY_CAVEATS,
            )

    def run_structure_scan_job(
        self,
        request: SourceDiscoveryStructureScanRequest,
    ) -> SourceDiscoveryStructureScanResponse:
        now = _utc_now()
        parsed = urlparse(request.target_url)
        job_id = f"source-structure-scan:{_safe_id(request.target_url)}:{_compact_timestamp(now)}"
        caveats = list(request.caveats)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            job = SourceDiscoveryJobORM(
                job_id=job_id,
                job_type="structure_scan",
                status="rejected",
                seed_url=request.target_url,
                wave_id=request.wave_id,
                wave_title=request.wave_title,
                discovered_source_ids_json=json.dumps([]),
                rejected_reason="Target URL must be an absolute http(s) URL.",
                request_budget=request.request_budget,
                used_requests=0,
                started_at=now,
                finished_at=now,
                caveats_json=json.dumps(["Rejected before structure discovery or candidate creation."]),
            )
            with session_scope(self._settings.source_discovery_database_url) as session:
                session.add(job)
                session.flush()
                return SourceDiscoveryStructureScanResponse(
                    job=_serialize_job(job),
                    memory=None,
                    memories=[],
                    discovered_feed_urls=[],
                    discovered_sitemap_urls=[],
                    discovered_navigation_urls=[],
                    auth_signals=[],
                    captcha_signals=[],
                    intake_disposition="blocked",
                    structure_hints=[],
                    caveats=SOURCE_DISCOVERY_CAVEATS,
                )

        used_requests = 0
        html_text = request.fixture_html
        robots_text = request.fixture_robots_txt
        if html_text is None and request.request_budget > 0:
            fetched = _fetch_url(request.target_url, method="GET", max_bytes=MAX_FETCH_BYTES)
            html_text = str(fetched["body"])
            used_requests += 1
        if robots_text is None and request.request_budget > used_requests:
            robots_url = _robots_url_for_target(request.target_url)
            try:
                fetched = _fetch_url(robots_url, method="GET", max_bytes=64_000)
                robots_text = str(fetched["body"])
                used_requests += 1
            except Exception:  # noqa: BLE001
                robots_text = ""

        analysis = _analyze_structure_scan(
            target_url=request.target_url,
            html_text=html_text or "",
            robots_text=robots_text or "",
            max_discovered=max(0, request.max_discovered),
        )

        root_seed = SourceDiscoveryCandidateSeed(
            source_id=_generated_source_id_for_url(request.target_url),
            title=parsed.netloc,
            url=request.target_url,
            parent_domain=parsed.netloc,
            source_type="web",
            source_class=_structure_scan_root_source_class(str(analysis["platform_family"])),
            wave_id=request.wave_id,
            wave_title=request.wave_title,
            lifecycle_state="candidate",
            source_health="unknown",
            policy_state="manual_review",
            access_result="reachable" if html_text else "unknown",
            machine_readable_result="partial" if analysis["discovered_feed_urls"] or analysis["discovered_sitemap_urls"] else "unknown",
            auth_requirement=analysis["auth_requirement"],
            captcha_requirement=analysis["captcha_requirement"],
            intake_disposition=analysis["intake_disposition"],
            wave_fit_score=0.54 if request.wave_id else 0.5,
            relevance_basis=[
                request.discovery_reason,
                "Structure scan inspected public discovery surfaces before any deeper candidate handling.",
            ],
            caveats=caveats + [
                "Structure scan is bounded to one public page plus optional robots.txt fetch.",
                "Discovered links remain candidates only and are not auto-approved or scheduled.",
            ],
            discovery_methods=["structure_scan"],
            structure_hints=analysis["structure_hints"],
            platform_family=str(analysis["platform_family"]),
        )

        child_seeds = _structure_candidate_seeds(
            request,
            analysis=analysis,
            caveats=caveats,
        )
        with session_scope(self._settings.source_discovery_database_url) as session:
            novel_candidate_count = _count_novel_candidate_seeds(session, child_seeds)
            root_memory = _upsert_candidate_row(session, root_seed, now=now)
            child_memories = [_upsert_candidate_row(session, seed, now=now) for seed in child_seeds]
            outcome_summary = (
                f"Structure scan found {len(child_memories)} candidate surfaces and {novel_candidate_count} novel root or child candidates."
            )
            _apply_structure_scan_outcome(
                root_memory,
                now=now,
                outcome_summary=outcome_summary,
                discovered_candidate_count=novel_candidate_count,
            )
            discovered_ids = [root_memory.source_id] + [memory.source_id for memory in child_memories]
            job = SourceDiscoveryJobORM(
                job_id=job_id,
                job_type="structure_scan",
                status="completed",
                seed_url=request.target_url,
                wave_id=request.wave_id,
                wave_title=request.wave_title,
                discovered_source_ids_json=json.dumps(discovered_ids),
                rejected_reason=None,
                request_budget=max(0, request.request_budget),
                used_requests=used_requests,
                started_at=now,
                finished_at=now,
                outcome_summary=outcome_summary,
                caveats_json=json.dumps(caveats + [
                    "Structure scan fingerprints public discovery surfaces and intake restrictions before deeper retrieval.",
                ]),
            )
            session.add(job)
            session.flush()
            return SourceDiscoveryStructureScanResponse(
                job=_serialize_job(job),
                memory=_serialize_memory(session, root_memory),
                memories=[_serialize_memory(session, memory) for memory in child_memories],
                discovered_feed_urls=analysis["discovered_feed_urls"],
                discovered_sitemap_urls=analysis["discovered_sitemap_urls"],
                discovered_navigation_urls=analysis["discovered_navigation_urls"],
                platform_family=analysis["platform_family"],
                auth_signals=analysis["auth_signals"],
                captcha_signals=analysis["captcha_signals"],
                intake_disposition=analysis["intake_disposition"],
                structure_hints=analysis["structure_hints"],
                caveats=SOURCE_DISCOVERY_CAVEATS,
            )

    def run_knowledge_backfill_job(
        self,
        request: SourceDiscoveryKnowledgeBackfillRequest,
    ) -> SourceDiscoveryKnowledgeBackfillResponse:
        now = _utc_now()
        job_id = f"source-knowledge-backfill:{_compact_timestamp(now)}"
        caveats = list(request.caveats)
        with session_scope(self._settings.source_discovery_database_url) as session:
            snapshots = _select_knowledge_backfill_snapshots(session, request)
            preexisting_node_ids = {
                node_id
                for node_id in session.scalars(select(SourceKnowledgeNodeORM.node_id))
            }
            touched_node_ids: set[str] = set()
            compacted_snapshot_count = 0
            affected_source_ids = sorted({snapshot.source_id for snapshot in snapshots})
            detached_node_ids: set[str] = set()

            if request.mode == "recompute_selected":
                for snapshot in snapshots:
                    if snapshot.knowledge_node_id:
                        detached_node_ids.add(snapshot.knowledge_node_id)
                    snapshot.knowledge_node_id = None
                    snapshot.canonical_snapshot_id = None
                    snapshot.duplicate_class = None
                    snapshot.body_storage_mode = "metadata_only" if snapshot.extraction_method == "metadata_only" else "full_text"
                for node_id in detached_node_ids:
                    _refresh_or_delete_knowledge_node(session, node_id)

            for snapshot in snapshots:
                memory = session.get(SourceMemoryORM, snapshot.source_id)
                if memory is None:
                    continue
                if request.mode == "missing_only" and snapshot.knowledge_node_id and session.get(SourceKnowledgeNodeORM, snapshot.knowledge_node_id) is not None:
                    touched_node_ids.add(snapshot.knowledge_node_id)
                    _refresh_knowledge_node_aggregates(session, snapshot.knowledge_node_id)
                    continue
                before_mode = snapshot.body_storage_mode
                _assign_snapshot_to_knowledge_node(
                    session,
                    snapshot,
                    memory=memory,
                    normalized_text=snapshot.full_text,
                    now=snapshot.fetched_at or now,
                )
                if snapshot.knowledge_node_id:
                    touched_node_ids.add(snapshot.knowledge_node_id)
                if before_mode != "compacted_duplicate" and snapshot.body_storage_mode == "compacted_duplicate":
                    compacted_snapshot_count += 1

            created_node_count = len(touched_node_ids - preexisting_node_ids)
            updated_node_count = len(touched_node_ids & preexisting_node_ids)
            job = SourceDiscoveryJobORM(
                job_id=job_id,
                job_type="knowledge_backfill",
                status="completed",
                seed_url=None,
                wave_id=None,
                wave_title=None,
                discovered_source_ids_json=json.dumps(affected_source_ids),
                rejected_reason=None,
                request_budget=0,
                used_requests=0,
                started_at=now,
                finished_at=_utc_now(),
                caveats_json=json.dumps(caveats + [
                    "Knowledge backfill is non-network and recomputes duplicate-aware node linkage only for the selected snapshots.",
                ]),
            )
            session.add(job)
            session.flush()
            return SourceDiscoveryKnowledgeBackfillResponse(
                job=_serialize_job(job),
                processed_snapshot_count=len(snapshots),
                created_node_count=created_node_count,
                updated_node_count=updated_node_count,
                compacted_snapshot_count=compacted_snapshot_count,
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
                        source_id=_generated_source_id_for_url(canonical_url),
                        title=record.source_name or record.title,
                        wave_id=record.monitor_id,
                        wave_title=monitor_titles.get(record.monitor_id),
                        discovery_reason="Record source extracted from existing Wave Monitor record.",
                        caveats=[
                            "Record-source extraction creates review candidates only and does not activate or poll the source.",
                            "Wave Monitor record text remains source-scoped context, not truth proof.",
                        ],
                        discovery_methods=["record_source_extract", "wave_monitor_record"],
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
                            source_id=_generated_source_id_for_url(canonical_url),
                            title=item.title or item.source_name,
                            wave_id=None,
                            wave_title=None,
                            discovery_reason="Record source extracted from Data AI feed item.",
                            caveats=[
                                "Data AI feed item text remains inert data and does not prove event truth, attribution, or impact.",
                                f"Extracted from Data AI source {item.source_id}.",
                            ],
                            discovery_methods=["record_source_extract", "data_ai_record"],
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
            _assign_snapshot_to_knowledge_node(
                session,
                snapshot,
                memory=memory,
                normalized_text=normalized_text,
                now=now,
            )
            memory.last_seen_at = now
            memory.caveats_json = json.dumps(sorted(set(_loads_list(memory.caveats_json) + caveats)))
            session.merge(snapshot)
            session.flush()
            return SourceDiscoveryContentSnapshotResponse(
                snapshot=_serialize_snapshot(session, snapshot),
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
            source_id=request.source_id or _generated_source_id_for_url(request.url),
            title=request.title or parsed.netloc,
            wave_id=request.wave_id,
            wave_title=request.wave_title,
            discovery_reason="public social/image metadata scan",
            caveats=caveats + [
                "Public social/image evidence is contextual and remains bounded to public page text, captions, and media references.",
                "No login-only, hidden, OCR-heavy, or media-blob routes are allowed.",
            ],
            discovery_methods=["social_metadata_scan"],
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

    def list_media_artifacts(
        self,
        source_id: str,
        *,
        limit: int = 25,
    ) -> SourceDiscoveryMediaArtifactListResponse:
        with session_scope(self._settings.source_discovery_database_url) as session:
            memory = session.get(SourceMemoryORM, source_id)
            if memory is None:
                raise ValueError(f"Unknown source_id: {source_id}")
            artifacts = list(
                session.scalars(
                    select(SourceMediaArtifactORM)
                    .where(SourceMediaArtifactORM.source_id == source_id)
                    .order_by(SourceMediaArtifactORM.captured_at.desc(), SourceMediaArtifactORM.artifact_id.desc())
                    .limit(max(0, limit))
                )
            )
            return SourceDiscoveryMediaArtifactListResponse(
                metadata={
                    "source": "source-discovery-media-artifacts",
                    "sourceId": source_id,
                    "count": len(artifacts),
                },
                artifacts=[_serialize_media_artifact(artifact) for artifact in artifacts],
                caveats=SOURCE_DISCOVERY_CAVEATS + [
                    "Media artifacts are evidence objects with their own provenance and caveats; they do not automatically validate the parent source.",
                ],
            )

    def media_artifact_detail(self, artifact_id: str, *, limit: int = 10) -> SourceDiscoveryMediaArtifactDetailResponse:
        with session_scope(self._settings.source_discovery_database_url) as session:
            artifact = session.get(SourceMediaArtifactORM, artifact_id)
            if artifact is None:
                raise ValueError(f"Unknown artifact_id: {artifact_id}")
            return SourceDiscoveryMediaArtifactDetailResponse(
                artifact=_serialize_media_artifact(artifact),
                ocr_runs=[
                    _serialize_media_ocr_run(row)
                    for row in session.scalars(
                        select(SourceMediaOcrRunORM)
                        .where(SourceMediaOcrRunORM.artifact_id == artifact_id)
                        .order_by(SourceMediaOcrRunORM.created_at.desc(), SourceMediaOcrRunORM.ocr_run_id.desc())
                        .limit(max(0, limit))
                    )
                ],
                interpretations=[
                    _serialize_media_interpretation(row)
                    for row in session.scalars(
                        select(SourceMediaInterpretationORM)
                        .where(SourceMediaInterpretationORM.artifact_id == artifact_id)
                        .order_by(SourceMediaInterpretationORM.created_at.desc(), SourceMediaInterpretationORM.interpretation_id.desc())
                        .limit(max(0, limit))
                    )
                ],
                geolocation_runs=[
                    _serialize_media_geolocation_run(row)
                    for row in session.scalars(
                        select(SourceMediaGeolocationRunORM)
                        .where(SourceMediaGeolocationRunORM.artifact_id == artifact_id)
                        .order_by(SourceMediaGeolocationRunORM.created_at.desc(), SourceMediaGeolocationRunORM.geolocation_run_id.desc())
                        .limit(max(0, limit))
                    )
                ],
                caveats=SOURCE_DISCOVERY_CAVEATS + [
                    "Place/time/season interpretations are review-oriented hypotheses, not silent truth promotion.",
                ],
            )

    def media_geolocation_detail(self, geolocation_run_id: str) -> SourceDiscoveryMediaGeolocationDetailResponse:
        with session_scope(self._settings.source_discovery_database_url) as session:
            geolocation_run = session.get(SourceMediaGeolocationRunORM, geolocation_run_id)
            if geolocation_run is None:
                raise ValueError(f"Unknown geolocation_run_id: {geolocation_run_id}")
            artifact = session.get(SourceMediaArtifactORM, geolocation_run.artifact_id)
            ocr_run = session.get(SourceMediaOcrRunORM, geolocation_run.ocr_run_id) if geolocation_run.ocr_run_id else None
            interpretation = (
                session.get(SourceMediaInterpretationORM, geolocation_run.interpretation_id)
                if geolocation_run.interpretation_id
                else None
            )
            return SourceDiscoveryMediaGeolocationDetailResponse(
                geolocation_run=_serialize_media_geolocation_run(geolocation_run),
                artifact=_serialize_media_artifact(artifact) if artifact is not None else None,
                ocr_run=_serialize_media_ocr_run(ocr_run) if ocr_run is not None else None,
                interpretation=_serialize_media_interpretation(interpretation) if interpretation is not None else None,
                caveats=SOURCE_DISCOVERY_CAVEATS + [
                    "Media geolocation runs are candidate-location packets for review and corroboration, not final truth state.",
                ],
            )

    def media_comparison_detail(self, comparison_id: str) -> SourceDiscoveryMediaComparisonDetailResponse:
        with session_scope(self._settings.source_discovery_database_url) as session:
            comparison = session.get(SourceMediaComparisonORM, comparison_id)
            if comparison is None:
                raise ValueError(f"Unknown comparison_id: {comparison_id}")
            left_artifact = session.get(SourceMediaArtifactORM, comparison.left_artifact_id)
            right_artifact = session.get(SourceMediaArtifactORM, comparison.right_artifact_id)
            cluster = _cluster_for_comparison(session, comparison)
            return SourceDiscoveryMediaComparisonDetailResponse(
                comparison=_serialize_media_comparison(comparison),
                left_artifact=_serialize_media_artifact(left_artifact) if left_artifact is not None else None,
                right_artifact=_serialize_media_artifact(right_artifact) if right_artifact is not None else None,
                cluster=_serialize_media_cluster(cluster) if cluster is not None else None,
                caveats=SOURCE_DISCOVERY_CAVEATS + [
                    "Media comparisons are deterministic evidence aids and may adjust review confidence without changing source reputation directly.",
                ],
            )

    def media_sequence_detail(self, sequence_id: str, *, limit: int = 24) -> SourceDiscoveryMediaSequenceDetailResponse:
        with session_scope(self._settings.source_discovery_database_url) as session:
            sequence = session.get(SourceMediaSequenceORM, sequence_id)
            if sequence is None:
                raise ValueError(f"Unknown sequence_id: {sequence_id}")
            artifacts = list(
                session.scalars(
                    select(SourceMediaArtifactORM)
                    .where(SourceMediaArtifactORM.sequence_id == sequence_id)
                    .order_by(SourceMediaArtifactORM.frame_index.asc(), SourceMediaArtifactORM.captured_at.asc())
                    .limit(max(0, limit))
                )
            )
            artifact_ids = [artifact.artifact_id for artifact in artifacts]
            comparisons = list(
                session.scalars(
                    select(SourceMediaComparisonORM)
                    .where(
                        SourceMediaComparisonORM.left_artifact_id.in_(artifact_ids) | SourceMediaComparisonORM.right_artifact_id.in_(artifact_ids)
                    )
                    .order_by(SourceMediaComparisonORM.created_at.desc(), SourceMediaComparisonORM.comparison_id.desc())
                    .limit(max(0, limit * 2))
                )
            ) if artifact_ids else []
            return SourceDiscoveryMediaSequenceDetailResponse(
                sequence=_serialize_media_sequence(sequence),
                artifacts=[_serialize_media_artifact(artifact) for artifact in artifacts],
                comparisons=[_serialize_media_comparison(row) for row in comparisons],
                caveats=SOURCE_DISCOVERY_CAVEATS + [
                    "Frame-sequence evidence is bounded and should not be treated as live continuous surveillance.",
                ],
            )

    def run_media_artifact_fetch_job(
        self,
        request: SourceDiscoveryMediaArtifactFetchRequest,
    ) -> SourceDiscoveryMediaArtifactFetchResponse:
        now = _utc_now()
        job_id = f"source-media-fetch:{_safe_id(request.source_id)}:{_compact_timestamp(now)}"
        media_url = canonicalize_media_url(request.media_url, base_url=request.parent_page_url or request.origin_url)
        if not media_url:
            raise ValueError("Media artifact fetch requires a non-empty media_url.")
        parsed = urlparse(media_url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("Media artifact fetch requires an absolute http(s) media URL.")
        with session_scope(self._settings.source_discovery_database_url) as session:
            memory = session.get(SourceMemoryORM, request.source_id)
            if memory is None:
                raise ValueError(f"Unknown source_id: {request.source_id}")
            if memory.policy_state == "blocked" or memory.intake_disposition == "blocked":
                job = SourceDiscoveryJobORM(
                    job_id=job_id,
                    job_type="media_artifact_fetch",
                    status="rejected",
                    seed_url=media_url,
                    wave_id=None,
                    wave_title=None,
                    discovered_source_ids_json=json.dumps([request.source_id]),
                    rejected_reason="Media artifact fetch is blocked for sources in blocked policy or intake state.",
                    request_budget=max(0, request.request_budget),
                    used_requests=0,
                    started_at=now,
                    finished_at=now,
                    caveats_json=json.dumps(request.caveats),
                )
                session.add(job)
                session.flush()
                return SourceDiscoveryMediaArtifactFetchResponse(
                    job=_serialize_job(job),
                    memory=_serialize_memory(memory),
                    artifact=None,
                    caveats=SOURCE_DISCOVERY_CAVEATS,
                )

        inspection, used_requests = fetch_media_artifact(
            self._settings,
            source_id=request.source_id,
            media_url=media_url,
            parent_page_url=request.parent_page_url or request.origin_url,
            fixture_bytes_base64=request.fixture_bytes_base64,
            fixture_content_type=request.fixture_content_type,
            request_budget=request.request_budget,
            max_bytes=max(1, self._settings.source_discovery_media_max_bytes),
        )
        artifact_caveats = list(request.caveats) + inspection.caveats + [
            "Media artifact fetch is bounded to a single public media URL and preserves local provenance.",
        ]
        with session_scope(self._settings.source_discovery_database_url) as session:
            memory = session.get(SourceMemoryORM, request.source_id)
            if memory is None:
                raise ValueError(f"Unknown source_id: {request.source_id}")
            artifact = _upsert_media_artifact_row(
                session,
                source_id=request.source_id,
                origin_url=request.origin_url or request.parent_page_url or media_url,
                published_at=request.published_at,
                inspection=inspection,
                now=now,
                caveats=artifact_caveats,
            )
            _auto_compare_media_artifact(session, self._settings, artifact, now=now)
            memory.last_seen_at = now
            memory.caveats_json = json.dumps(sorted(set(_loads_list(memory.caveats_json) + artifact_caveats)))
            job = SourceDiscoveryJobORM(
                job_id=job_id,
                job_type="media_artifact_fetch",
                status="completed",
                seed_url=media_url,
                wave_id=None,
                wave_title=None,
                discovered_source_ids_json=json.dumps([request.source_id]),
                rejected_reason=None,
                request_budget=max(0, request.request_budget),
                used_requests=used_requests,
                started_at=now,
                finished_at=_utc_now(),
                caveats_json=json.dumps(artifact_caveats),
            )
            session.add(job)
            session.flush()
            return SourceDiscoveryMediaArtifactFetchResponse(
                job=_serialize_job(job),
                memory=_serialize_memory(memory),
                artifact=_serialize_media_artifact(artifact),
                caveats=SOURCE_DISCOVERY_CAVEATS,
            )

    def run_media_ocr_job(
        self,
        request: SourceDiscoveryMediaOcrJobRequest,
    ) -> SourceDiscoveryMediaOcrJobResponse:
        now = _utc_now()
        job_id = f"source-media-ocr:{_safe_id(request.artifact_id)}:{_compact_timestamp(now)}"
        with session_scope(self._settings.source_discovery_database_url) as session:
            artifact = session.get(SourceMediaArtifactORM, request.artifact_id)
            if artifact is None:
                raise ValueError(f"Unknown artifact_id: {request.artifact_id}")
            artifact_source_id = artifact.source_id
            artifact_origin_url = artifact.origin_url
            engines = _ocr_engine_sequence(self._settings, request.engine)
            attempt_rows: list[SourceMediaOcrRunORM] = []
            attempt_results: list[tuple[SourceMediaOcrRunORM, Any]] = []
            fixture_blocks = [block.model_dump(by_alias=False) for block in request.fixture_blocks]
            for attempt_index, engine_name in enumerate(engines):
                result = run_media_ocr(
                    self._settings,
                    artifact_path=artifact.artifact_path,
                    engine=engine_name,
                    preprocess_mode=request.preprocess_mode,
                    fixture_text=request.fixture_text if engine_name == "fixture" else request.fixture_text,
                    fixture_blocks=fixture_blocks,
                )
                ocr_caveats = list(request.caveats) + result.caveats
                row = SourceMediaOcrRunORM(
                    ocr_run_id=f"source-media-ocr-run:{_safe_id(request.artifact_id)}:{attempt_index}:{_compact_timestamp(now)}",
                    artifact_id=artifact.artifact_id,
                    source_id=artifact.source_id,
                    engine=result.engine,
                    engine_version=result.engine_version,
                    status=result.status,
                    attempt_index=attempt_index,
                    selected_result=False,
                    preprocessing_json=json.dumps(result.preprocessing),
                    raw_text=result.raw_text,
                    text_length=len(result.raw_text),
                    mean_confidence=result.mean_confidence,
                    line_count=len(result.blocks),
                    metadata_json=json.dumps(
                        {
                            **result.metadata,
                            "blocks": [
                                {
                                    "block_index": block.block_index,
                                    "text": block.text,
                                    "confidence": block.confidence,
                                    "left": block.left,
                                    "top": block.top,
                                    "width": block.width,
                                    "height": block.height,
                                }
                                for block in result.blocks
                            ],
                        }
                    ),
                    created_at=now,
                    caveats_json=json.dumps(ocr_caveats),
                )
                session.add(row)
                session.flush()
                attempt_rows.append(row)
                attempt_results.append((row, result))
                if not _should_run_ocr_fallback(self._settings, artifact, request.engine, result):
                    break
            selected_row, selected_result = _select_final_ocr_attempt(attempt_results)
            selected_row.selected_result = True
            selected_ocr_run_id = selected_row.ocr_run_id
            if len(attempt_results) > 1:
                disagreement_caveat = _ocr_disagreement_caveat([result for _, result in attempt_results])
                if disagreement_caveat:
                    for row, _ in attempt_results:
                        row.caveats_json = json.dumps(sorted(set(_loads_list(row.caveats_json) + [disagreement_caveat])))
            if selected_result.raw_text:
                artifact.review_state = "ocr_review_pending"
            session.flush()
            snapshot_response: SourceDiscoveryContentSnapshotResponse | None = None
        if selected_result.raw_text:
            snapshot_response = self.store_content_snapshot(
                SourceDiscoveryContentSnapshotRequest(
                    source_id=artifact_source_id,
                    url=artifact_origin_url,
                    title=f"OCR extract for {artifact_origin_url}",
                    raw_text=selected_result.raw_text,
                    content_type="text/plain",
                    request_budget=0,
                    caveats=list(request.caveats) + [
                        "This snapshot is OCR-derived text from a media artifact and must remain linked to the original pixels.",
                    ],
                )
            )
        with session_scope(self._settings.source_discovery_database_url) as session:
            artifact = session.get(SourceMediaArtifactORM, request.artifact_id)
            if artifact is None:
                raise ValueError(f"Unknown artifact_id: {request.artifact_id}")
            _auto_compare_media_artifact(session, self._settings, artifact, now=_utc_now())
            ocr_row = session.get(SourceMediaOcrRunORM, selected_ocr_run_id)
            if ocr_row is None:
                raise ValueError("OCR run was not persisted.")
            final_caveats = _loads_list(ocr_row.caveats_json) + [
                "OCR is derived evidence and must not overwrite or silently replace source-reported text.",
            ]
            job = SourceDiscoveryJobORM(
                job_id=job_id,
                job_type="media_ocr",
                status=selected_result.status,
                seed_url=artifact.media_url,
                wave_id=None,
                wave_title=None,
                discovered_source_ids_json=json.dumps([artifact.source_id]),
                rejected_reason=None if selected_result.status == "completed" else "; ".join(selected_result.caveats) or None,
                request_budget=max(0, request.request_budget),
                used_requests=0,
                started_at=now,
                finished_at=_utc_now(),
                caveats_json=json.dumps(final_caveats),
            )
            session.add(job)
            session.flush()
            return SourceDiscoveryMediaOcrJobResponse(
                job=_serialize_job(job),
                artifact=_serialize_media_artifact(artifact),
                ocr_run=_serialize_media_ocr_run(ocr_row),
                snapshot=snapshot_response.snapshot if snapshot_response else None,
                caveats=SOURCE_DISCOVERY_CAVEATS,
            )

    def run_media_interpretation_job(
        self,
        request: SourceDiscoveryMediaInterpretationJobRequest,
    ) -> SourceDiscoveryMediaInterpretationJobResponse:
        now = _utc_now()
        job_id = f"source-media-interpret:{_safe_id(request.artifact_id)}:{_compact_timestamp(now)}"
        with session_scope(self._settings.source_discovery_database_url) as session:
            artifact = session.get(SourceMediaArtifactORM, request.artifact_id)
            if artifact is None:
                raise ValueError(f"Unknown artifact_id: {request.artifact_id}")
            latest_ocr = session.scalar(
                select(SourceMediaOcrRunORM)
                .where(SourceMediaOcrRunORM.artifact_id == artifact.artifact_id)
                .order_by(SourceMediaOcrRunORM.created_at.desc(), SourceMediaOcrRunORM.ocr_run_id.desc())
                .limit(1)
            )
            metadata = _loads_dict(artifact.metadata_json)
            captions = [str(item) for item in metadata.get("captions", [])] if isinstance(metadata.get("captions"), list) else []
            result = interpret_media_artifact(
                self._settings,
                artifact_path=artifact.artifact_path,
                artifact_metadata={
                    **metadata,
                    "width": artifact.width,
                    "height": artifact.height,
                },
                observed_latitude=artifact.observed_latitude,
                observed_longitude=artifact.observed_longitude,
                exif_timestamp=artifact.exif_timestamp,
                ocr_text=latest_ocr.raw_text if latest_ocr is not None else None,
                captions=captions,
                adapter=request.adapter,
                model=request.model,
                allow_local_ai=request.allow_local_ai,
                fixture_result=request.fixture_result,
            )
            interpretation_caveats = list(request.caveats) + result.caveats
            interpretation_row = SourceMediaInterpretationORM(
                interpretation_id=f"source-media-interpretation:{_safe_id(request.artifact_id)}:{_compact_timestamp(now)}",
                artifact_id=artifact.artifact_id,
                source_id=artifact.source_id,
                ocr_run_id=latest_ocr.ocr_run_id if latest_ocr is not None else None,
                adapter=result.adapter,
                model_name=result.model_name,
                status=result.status,
                review_state="interpret_review_pending",
                people_analysis_performed=False,
                uncertainty_ceiling=result.uncertainty_ceiling,
                scene_labels_json=json.dumps(result.scene_labels),
                scene_summary=result.scene_summary,
                place_hypothesis=result.place_hypothesis,
                place_confidence=result.place_confidence,
                place_basis=result.place_basis,
                time_of_day_guess=result.time_of_day_guess,
                time_of_day_confidence=result.time_of_day_confidence,
                time_of_day_basis=result.time_of_day_basis,
                season_guess=result.season_guess,
                season_confidence=result.season_confidence,
                season_basis=result.season_basis,
                geolocation_hypothesis=result.geolocation_hypothesis,
                geolocation_confidence=result.geolocation_confidence,
                geolocation_basis=result.geolocation_basis,
                observed_latitude=result.observed_latitude,
                observed_longitude=result.observed_longitude,
                reasoning_lines_json=json.dumps(result.reasoning_lines),
                metadata_json=json.dumps(result.metadata),
                created_at=now,
                caveats_json=json.dumps(interpretation_caveats),
            )
            session.add(interpretation_row)
            artifact.review_state = "interpret_review_pending"
            job = SourceDiscoveryJobORM(
                job_id=job_id,
                job_type="media_interpret",
                status=result.status,
                seed_url=artifact.media_url,
                wave_id=None,
                wave_title=None,
                discovered_source_ids_json=json.dumps([artifact.source_id]),
                rejected_reason=None if result.status == "completed" else "; ".join(result.caveats) or None,
                request_budget=max(0, request.request_budget),
                used_requests=0,
                started_at=now,
                finished_at=_utc_now(),
                caveats_json=json.dumps(interpretation_caveats + [
                    "Image interpretation remains review-only and must not promote identity, guilt, or unsupported location claims.",
                ]),
            )
            session.add(job)
            session.flush()
            return SourceDiscoveryMediaInterpretationJobResponse(
                job=_serialize_job(job),
                artifact=_serialize_media_artifact(artifact),
                interpretation=_serialize_media_interpretation(interpretation_row),
                caveats=SOURCE_DISCOVERY_CAVEATS,
            )

    def run_media_geolocation_job(
        self,
        request: SourceDiscoveryMediaGeolocateJobRequest,
    ) -> SourceDiscoveryMediaGeolocateJobResponse:
        now = _utc_now()
        job_id = f"source-media-geolocate:{_safe_id(request.artifact_id)}:{_compact_timestamp(now)}"
        with session_scope(self._settings.source_discovery_database_url) as session:
            artifact = session.get(SourceMediaArtifactORM, request.artifact_id)
            if artifact is None:
                raise ValueError(f"Unknown artifact_id: {request.artifact_id}")
            latest_ocr = session.scalar(
                select(SourceMediaOcrRunORM)
                .where(SourceMediaOcrRunORM.artifact_id == artifact.artifact_id)
                .order_by(SourceMediaOcrRunORM.created_at.desc(), SourceMediaOcrRunORM.ocr_run_id.desc())
                .limit(1)
            )
            latest_interpretation = session.scalar(
                select(SourceMediaInterpretationORM)
                .where(SourceMediaInterpretationORM.artifact_id == artifact.artifact_id)
                .order_by(SourceMediaInterpretationORM.created_at.desc(), SourceMediaInterpretationORM.interpretation_id.desc())
                .limit(1)
            )
            metadata = _loads_dict(artifact.metadata_json)
            captions = [str(item) for item in metadata.get("captions", [])] if isinstance(metadata.get("captions"), list) else []
            inherited_context = _build_media_geolocation_inherited_context(session, artifact)
            result = geolocate_media_artifact(
                self._settings,
                artifact_path=artifact.artifact_path,
                artifact_metadata={
                    **metadata,
                    "width": artifact.width,
                    "height": artifact.height,
                },
                observed_latitude=artifact.observed_latitude,
                observed_longitude=artifact.observed_longitude,
                exif_timestamp=artifact.exif_timestamp,
                ocr_text=latest_ocr.raw_text if latest_ocr is not None else None,
                captions=captions,
                engine=request.engine,
                analyst_adapter=request.analyst_adapter,
                model=request.model,
                analyst_model=request.analyst_model,
                allow_local_ai=request.allow_local_ai,
                fixture_result=request.fixture_result,
                candidate_labels=request.candidate_labels,
                prior_place_hypothesis=latest_interpretation.place_hypothesis if latest_interpretation is not None else None,
                prior_place_confidence=latest_interpretation.place_confidence if latest_interpretation is not None else None,
                prior_place_basis=latest_interpretation.place_basis if latest_interpretation is not None else None,
                prior_geolocation_hypothesis=latest_interpretation.geolocation_hypothesis if latest_interpretation is not None else None,
                prior_geolocation_confidence=latest_interpretation.geolocation_confidence if latest_interpretation is not None else None,
                prior_geolocation_basis=latest_interpretation.geolocation_basis if latest_interpretation is not None else None,
                inherited_context=inherited_context,
            )
            run_caveats = list(request.caveats) + result.caveats
            run_metadata = {
                **result.metadata,
                "confidenceCeiling": result.confidence_ceiling,
                "supportingEvidence": result.supporting_evidence,
                "contradictingEvidence": result.contradicting_evidence,
                "engineAgreement": result.engine_agreement,
                "provenanceChain": result.provenance_chain,
                "inheritedFromArtifactIds": result.inherited_from_artifact_ids,
                "cluePacket": _serialize_geolocation_clue_packet(result.clue_packet),
                "engineAttempts": [_serialize_geolocation_engine_attempt(item) for item in result.engine_attempts],
            }
            geolocation_row = SourceMediaGeolocationRunORM(
                geolocation_run_id=f"source-media-geolocation:{_safe_id(request.artifact_id)}:{_compact_timestamp(now)}",
                artifact_id=artifact.artifact_id,
                source_id=artifact.source_id,
                ocr_run_id=latest_ocr.ocr_run_id if latest_ocr is not None else None,
                interpretation_id=latest_interpretation.interpretation_id if latest_interpretation is not None else None,
                engine=result.engine,
                model_name=result.model_name,
                analyst_adapter=result.analyst_adapter,
                analyst_model_name=result.analyst_model_name,
                status=result.status,
                review_state="interpret_review_pending",
                candidate_count=result.candidate_count,
                top_label=result.top_label,
                top_latitude=result.top_latitude,
                top_longitude=result.top_longitude,
                top_confidence=result.top_confidence,
                top_basis=result.top_basis,
                summary=result.summary,
                reasoning_lines_json=json.dumps(result.reasoning_lines),
                metadata_json=json.dumps(run_metadata),
                candidates_json=json.dumps([
                    {
                        "rank": candidate.rank,
                        "candidate_kind": candidate.candidate_kind,
                        "label": candidate.label,
                        "latitude": candidate.latitude,
                        "longitude": candidate.longitude,
                        "confidence": candidate.confidence,
                        "confidence_score": candidate.confidence_score,
                        "confidence_ceiling": candidate.confidence_ceiling,
                        "engine": candidate.engine,
                        "basis": candidate.basis,
                        "supporting_evidence": candidate.supporting_evidence,
                        "contradicting_evidence": candidate.contradicting_evidence,
                        "engine_agreement": candidate.engine_agreement,
                        "provenance_chain": candidate.provenance_chain,
                        "inherited": candidate.inherited,
                        "inherited_from_artifact_ids": candidate.inherited_from_artifact_ids,
                        "metadata": candidate.metadata,
                        "caveats": candidate.caveats,
                    }
                    for candidate in result.candidates
                ]),
                created_at=now,
                caveats_json=json.dumps(run_caveats),
            )
            session.add(geolocation_row)
            artifact.review_state = "interpret_review_pending"
            job = SourceDiscoveryJobORM(
                job_id=job_id,
                job_type="media_geolocate",
                status=result.status,
                seed_url=artifact.media_url,
                wave_id=None,
                wave_title=None,
                discovered_source_ids_json=json.dumps([artifact.source_id]),
                rejected_reason=None if result.status == "completed" else "; ".join(result.caveats) or None,
                request_budget=max(0, request.request_budget),
                used_requests=0,
                started_at=now,
                finished_at=_utc_now(),
                caveats_json=json.dumps(run_caveats + [
                    "Media geolocation remains candidate-location infrastructure and must not silently promote truth, blame, or source reputation changes.",
                ]),
            )
            session.add(job)
            session.flush()
            return SourceDiscoveryMediaGeolocateJobResponse(
                job=_serialize_job(job),
                artifact=_serialize_media_artifact(artifact),
                geolocation_run=_serialize_media_geolocation_run(geolocation_row),
                caveats=SOURCE_DISCOVERY_CAVEATS,
            )

    def run_media_compare_job(
        self,
        request: SourceDiscoveryMediaCompareJobRequest,
    ) -> SourceDiscoveryMediaCompareJobResponse:
        now = _utc_now()
        job_id = f"source-media-compare:{_safe_id(request.left_artifact_id)}:{_safe_id(request.right_artifact_id)}:{_compact_timestamp(now)}"
        with session_scope(self._settings.source_discovery_database_url) as session:
            left_artifact = session.get(SourceMediaArtifactORM, request.left_artifact_id)
            right_artifact = session.get(SourceMediaArtifactORM, request.right_artifact_id)
            if left_artifact is None or right_artifact is None:
                raise ValueError("Media comparison requires two known artifact_ids.")
            comparison = _create_or_refresh_media_comparison(
                session,
                self._settings,
                left_artifact,
                right_artifact,
                now=now,
                manual_caveats=list(request.caveats),
            )
            cluster = _cluster_for_comparison(session, comparison)
            job = SourceDiscoveryJobORM(
                job_id=job_id,
                job_type="media_compare",
                status=comparison.status,
                seed_url=left_artifact.media_url,
                wave_id=None,
                wave_title=None,
                discovered_source_ids_json=json.dumps(sorted({left_artifact.source_id, right_artifact.source_id})),
                rejected_reason=None if comparison.status == "completed" else "; ".join(_loads_list(comparison.caveats_json)) or None,
                request_budget=max(0, request.request_budget),
                used_requests=0,
                started_at=now,
                finished_at=_utc_now(),
                caveats_json=json.dumps(_loads_list(comparison.caveats_json)),
            )
            session.add(job)
            session.flush()
            return SourceDiscoveryMediaCompareJobResponse(
                job=_serialize_job(job),
                comparison=_serialize_media_comparison(comparison),
                left_artifact=_serialize_media_artifact(left_artifact),
                right_artifact=_serialize_media_artifact(right_artifact),
                cluster=_serialize_media_cluster(cluster) if cluster is not None else None,
                caveats=SOURCE_DISCOVERY_CAVEATS,
            )

    def run_media_frame_sample_job(
        self,
        request: SourceDiscoveryMediaFrameSampleJobRequest,
    ) -> SourceDiscoveryMediaFrameSampleJobResponse:
        now = _utc_now()
        job_id = f"source-media-frame-sample:{_safe_id(request.source_id)}:{_compact_timestamp(now)}"
        media_url = canonicalize_media_url(request.media_url, base_url=request.parent_page_url or request.origin_url)
        if not media_url:
            raise ValueError("Frame sampling requires a non-empty media_url.")
        with session_scope(self._settings.source_discovery_database_url) as session:
            memory = session.get(SourceMemoryORM, request.source_id)
            if memory is None:
                raise ValueError(f"Unknown source_id: {request.source_id}")
            if memory.policy_state == "blocked" or memory.intake_disposition == "blocked":
                raise ValueError("Frame sampling is blocked for sources in blocked policy or intake state.")
        sample_result = sample_media_frames(
            self._settings,
            media_url=media_url,
            fixture_frames_base64=request.fixture_frames_base64,
            source_span_seconds=request.source_span_seconds,
            max_frames=request.max_frames,
            sample_interval_seconds=request.sample_interval_seconds,
            request_budget=request.request_budget,
        )
        with session_scope(self._settings.source_discovery_database_url) as session:
            memory = session.get(SourceMemoryORM, request.source_id)
            if memory is None:
                raise ValueError(f"Unknown source_id: {request.source_id}")
            sequence = SourceMediaSequenceORM(
                sequence_id=f"source-media-sequence:{_safe_id(request.source_id)}:{_compact_timestamp(now)}",
                source_id=request.source_id,
                origin_url=request.origin_url or request.parent_page_url or media_url,
                canonical_url=media_url,
                parent_page_url=request.parent_page_url or request.origin_url,
                media_kind="video_frame",
                sampler=sample_result.sampler,
                status=sample_result.status,
                source_span_seconds=min(request.source_span_seconds, self._settings.source_discovery_media_frame_max_span_seconds),
                frame_count=len(sample_result.frames),
                sample_interval_seconds=max(request.sample_interval_seconds, self._settings.source_discovery_media_frame_min_interval_seconds),
                request_budget=max(0, request.request_budget),
                used_requests=0 if sample_result.sampler == "fixture" else max(0, min(1, request.request_budget)),
                created_at=now,
                metadata_json=json.dumps(sample_result.metadata),
                caveats_json=json.dumps(list(request.caveats) + sample_result.caveats),
            )
            session.add(sequence)
            session.flush()
            artifacts: list[SourceMediaArtifactORM] = []
            comparisons: list[SourceMediaComparisonORM] = []
            for frame_index, frame_bytes in enumerate(sample_result.frames[: self._settings.source_discovery_media_frame_max_frames]):
                inspection = fetch_media_artifact(
                    self._settings,
                    source_id=request.source_id,
                    media_url=media_url,
                    parent_page_url=request.parent_page_url or request.origin_url,
                    fixture_bytes_base64=base64.b64encode(frame_bytes).decode("utf-8"),
                    fixture_content_type=request.fixture_content_type or "image/png",
                    request_budget=0,
                    max_bytes=max(1, self._settings.source_discovery_media_max_bytes),
                )[0]
                artifact = _upsert_media_artifact_row(
                    session,
                    source_id=request.source_id,
                    origin_url=request.origin_url or request.parent_page_url or media_url,
                    published_at=None,
                    inspection=inspection,
                    now=now,
                    caveats=list(request.caveats) + sample_result.caveats,
                    dedupe_by_hash=False,
                    artifact_id_suffix=f"frame-{frame_index}",
                )
                artifact.media_kind = "video_frame"
                artifact.sequence_id = sequence.sequence_id
                artifact.frame_index = frame_index
                artifact.sampled_at_ms = frame_index * sequence.sample_interval_seconds * 1000
                artifacts.append(artifact)
                _auto_compare_media_artifact(session, self._settings, artifact, now=now)
            for index in range(len(artifacts) - 1):
                comparisons.append(
                    _create_or_refresh_media_comparison(
                        session,
                        self._settings,
                        artifacts[index],
                        artifacts[index + 1],
                        now=now,
                        manual_caveats=["Adjacent frame comparison within a bounded sequence."],
                    )
                )
            if len(artifacts) >= 2:
                comparisons.append(
                    _create_or_refresh_media_comparison(
                        session,
                        self._settings,
                        artifacts[0],
                        artifacts[-1],
                        now=now,
                        manual_caveats=["First-versus-last frame comparison within a bounded sequence."],
                    )
                )
            sequence.frame_count = len(artifacts)
            memory.last_seen_at = now
            job = SourceDiscoveryJobORM(
                job_id=job_id,
                job_type="media_frame_sample",
                status=sample_result.status,
                seed_url=media_url,
                wave_id=None,
                wave_title=None,
                discovered_source_ids_json=json.dumps([request.source_id]),
                rejected_reason=None if sample_result.status == "completed" else "; ".join(sample_result.caveats) or None,
                request_budget=max(0, request.request_budget),
                used_requests=sequence.used_requests,
                started_at=now,
                finished_at=_utc_now(),
                caveats_json=json.dumps(list(request.caveats) + sample_result.caveats),
            )
            session.add(job)
            session.flush()
            return SourceDiscoveryMediaFrameSampleJobResponse(
                job=_serialize_job(job),
                sequence=_serialize_media_sequence(sequence),
                artifacts=[_serialize_media_artifact(artifact) for artifact in artifacts],
                comparisons=[_serialize_media_comparison(row) for row in comparisons],
                caveats=SOURCE_DISCOVERY_CAVEATS,
            )

    def review_queue(self, *, limit: int = 100, owner_lane: str | None = None) -> SourceDiscoveryReviewQueueResponse:
        with session_scope(self._settings.source_discovery_database_url) as session:
            context = _build_discovery_priority_context(session)
            now = _utc_now()
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
                pending_claims = _pending_review_claim_candidates_for_source(session, memory.source_id)
                corrective_cluster = _source_has_corrective_cluster(session, memory.source_id)
                unscanned_public_root = _is_unscanned_public_candidate_root(memory)
                reasons = _review_reasons(
                    memory,
                    best_fit=best_fit,
                    has_snapshot=has_snapshot,
                    pending_claim_count=len(pending_claims),
                    corrective_cluster=corrective_cluster,
                    unscanned_public_root=unscanned_public_root,
                )
                if not reasons:
                    continue
                priority_score, priority = _review_priority(
                    memory,
                    best_fit=best_fit,
                    has_snapshot=has_snapshot,
                    pending_claim_count=len(pending_claims),
                    corrective_cluster=corrective_cluster,
                    unscanned_public_root=unscanned_public_root,
                )
                discovery_priority_score, discovery_priority, discovery_priority_basis = _compute_discovery_priority(
                    session,
                    memory,
                    now=now,
                    context=context,
                )
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
                            auth_requirement=memory.auth_requirement,  # type: ignore[arg-type]
                            captcha_requirement=memory.captcha_requirement,  # type: ignore[arg-type]
                            intake_disposition=memory.intake_disposition,  # type: ignore[arg-type]
                            priority=priority,
                            review_reasons=reasons,
                            recommended_actions=_recommended_review_actions(memory, owner_lane=memory.owner_lane),
                            structure_hints=_loads_list(memory.structure_hints_json),
                            discovery_role=memory.discovery_role,  # type: ignore[arg-type]
                            seed_family=memory.seed_family,  # type: ignore[arg-type]
                            seed_packet_id=memory.seed_packet_id,
                            seed_packet_title=memory.seed_packet_title,
                            platform_family=memory.platform_family,  # type: ignore[arg-type]
                            source_family_tags=_loads_list(memory.source_family_tags_json),
                            scope_hints=_loads_scope_hints(memory.scope_hints_json),
                            global_reputation_score=memory.global_reputation_score,
                            domain_reputation_score=memory.domain_reputation_score,
                            source_health_score=memory.source_health_score,
                            timeliness_score=memory.timeliness_score,
                            confidence_level=memory.confidence_level,
                            best_wave_id=best_fit.wave_id if best_fit else None,
                            best_wave_title=best_fit.wave_title if best_fit else None,
                            best_wave_fit_score=best_fit.fit_score if best_fit else None,
                            next_check_at=memory.next_check_at,
                            pending_claim_count=len(pending_claims),
                            next_discovery_action=_suggest_discovery_action(memory),  # type: ignore[arg-type]
                            discovery_priority_score=discovery_priority_score,
                            discovery_priority=discovery_priority,  # type: ignore[arg-type]
                            discovery_priority_basis=discovery_priority_basis,
                            last_discovery_outcome=memory.last_discovery_outcome,
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

    def import_review_claims(
        self,
        request: SourceDiscoveryReviewClaimImportRequest,
    ) -> SourceDiscoveryReviewClaimImportResponse:
        context = _load_review_claim_import_context(
            self._settings,
            review_id=request.review_id,
            requested_source_id=request.source_id,
        )
        now = _utc_now()
        with session_scope(self._settings.source_discovery_database_url) as session:
            memory = session.get(SourceMemoryORM, str(context["source_id"]))
            if memory is None:
                raise ValueError(f"Unknown source_id: {context['source_id']}")
            candidates = _upsert_review_claim_candidates(
                session,
                context=context,
                now=now,
                imported_by=request.imported_by,
                caveats=request.caveats,
            )
            session.flush()
            return SourceDiscoveryReviewClaimImportResponse(
                memory=_serialize_memory(memory),
                claims=[_serialize_review_claim_candidate(row) for row in candidates],
                wave_fits=[_serialize_wave_fit(fit) for fit in _fits_for_source(session, memory.source_id)],
                caveats=SOURCE_DISCOVERY_CAVEATS + [
                    "Imported review claims remain pending until an explicit reviewed application updates source memory.",
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
                if memory.intake_disposition == "blocked" or memory.auth_requirement == "login_required":
                    raise ValueError("approve_candidate is not allowed for login-required or blocked-intake sources.")
                if memory.captcha_requirement == "captcha_required":
                    raise ValueError("approve_candidate is not allowed for CAPTCHA-gated sources.")
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
        context = _load_review_claim_import_context(
            self._settings,
            review_id=request.review_id,
            requested_source_id=request.source_id,
        )
        source_id = str(context["source_id"])

        now = _utc_now()
        with session_scope(self._settings.source_discovery_database_url) as session:
            memory = session.get(SourceMemoryORM, source_id)
            if memory is None:
                raise ValueError(f"Unknown source_id: {source_id}")
            if memory.policy_state == "blocked" or memory.lifecycle_state in {"rejected", "archived"}:
                raise ValueError("Review claims cannot be applied to blocked, rejected, or archived sources.")
            if memory.policy_state != "reviewed":
                raise ValueError("Review claims require the source to be explicitly reviewed first.")

            candidates = _upsert_review_claim_candidates(
                session,
                context=context,
                now=now,
                imported_by=request.approved_by,
                caveats=["Auto-imported during apply-claims."],
            )
            candidates_by_index = {candidate.claim_index: candidate for candidate in candidates}
            created_rows: list[SourceReviewClaimApplicationORM] = []
            for application in request.applications:
                candidate = candidates_by_index.get(application.claim_index)
                if candidate is None:
                    raise ValueError(f"claim_index {application.claim_index} is not an accepted review claim.")
                if candidate.status == "applied":
                    raise ValueError(f"claim_index {application.claim_index} for this review and source has already been applied.")
                existing = session.scalar(
                    select(SourceReviewClaimApplicationORM).where(
                        SourceReviewClaimApplicationORM.review_id == request.review_id,
                        SourceReviewClaimApplicationORM.source_id == source_id,
                        SourceReviewClaimApplicationORM.claim_index == application.claim_index,
                    )
                )
                if existing is not None:
                    raise ValueError(f"claim_index {application.claim_index} for this review and source has already been applied.")
                corroborating_source_ids, contradiction_source_ids = _claim_candidate_supporting_sources(
                    session,
                    candidate,
                    source_id=source_id,
                )
                claim_request = SourceDiscoveryClaimOutcomeRequest(
                    source_id=source_id,
                    wave_id=candidate.wave_id,
                    claim_text=candidate.claim_text,
                    claim_type=candidate.claim_type,
                    outcome=application.outcome,
                    evidence_basis=candidate.evidence_basis,
                    observed_at=now,
                    corroborating_source_ids=corroborating_source_ids,
                    contradiction_source_ids=contradiction_source_ids,
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
                        corroborating_source_ids_json=json.dumps(claim_request.corroborating_source_ids),
                        contradiction_source_ids_json=json.dumps(claim_request.contradiction_source_ids),
                        caveats_json=json.dumps(claim_request.caveats),
                    )
                )
                _apply_claim_outcome(session, memory, claim_request, now)
                candidate.status = "applied"
                candidate.applied_at = now
                row = SourceReviewClaimApplicationORM(
                    review_id=request.review_id,
                    task_id=candidate.task_id,
                    source_id=source_id,
                    wave_id=candidate.wave_id,
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
        structure_scans_completed = 0
        public_discovery_jobs_completed = 0
        expansion_jobs_completed = 0
        knowledge_backfill_jobs_completed = 0
        duplicate_snapshots_skipped = 0
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
            best_fit_by_source_id = {}
            for memory in memories:
                best_fit = _best_wave_fit(_fits_for_source(session, memory.source_id))
                best_fit_by_source_id[memory.source_id] = (
                    best_fit.wave_id if best_fit else None,
                    best_fit.wave_title if best_fit else None,
                )
            discovery_context = _build_discovery_priority_context(session)
            source_ids = [
                memory.source_id
                for memory in memories
                if _is_due_for_health_check(memory.next_check_at, now)
            ][: max(0, request.health_check_limit)]
            eligible_structure_memories = [memory for memory in memories if _is_scheduler_structure_scan_candidate(memory)]
            structure_scan_memories = [
                {
                    "url": memory.url,
                    "wave_id": best_fit_by_source_id[memory.source_id][0],
                    "wave_title": best_fit_by_source_id[memory.source_id][1],
                }
                for memory in sorted(
                    eligible_structure_memories,
                    key=lambda item: (
                        -_compute_discovery_priority(session, item, now=now, context=discovery_context)[0],
                        -((discovery_context.best_fit_by_source_id.get(item.source_id).fit_score) if discovery_context.best_fit_by_source_id.get(item.source_id) else 0.0),
                        item.title.casefold(),
                    ),
                )
            ][: max(0, request.structure_scan_limit)]
            expansion_memories = [
                {
                    "url": memory.url,
                    "wave_id": best_fit_by_source_id[memory.source_id][0],
                    "wave_title": best_fit_by_source_id[memory.source_id][1],
                }
                for memory in memories
                if _is_scheduler_expansion_candidate(memory)
            ][: max(0, request.expansion_job_limit)]
            eligible_public_discovery_memories = [memory for memory in memories if _is_scheduler_public_discovery_candidate(memory, now)]
            public_discovery_memories = [
                {
                    "url": memory.url,
                    "wave_id": best_fit_by_source_id[memory.source_id][0],
                    "wave_title": best_fit_by_source_id[memory.source_id][1],
                    "job_type": _public_discovery_followup_kind(memory),
                }
                for memory in sorted(
                    eligible_public_discovery_memories,
                    key=lambda item: (
                        -_compute_discovery_priority(session, item, now=now, context=discovery_context)[0],
                        (_parse_utc_like(item.next_discovery_scan_at) or datetime.min.replace(tzinfo=timezone.utc)),
                        _parse_utc_like(item.last_discovery_scan_at) or datetime.min.replace(tzinfo=timezone.utc),
                        _parse_utc_like(item.last_seen_at) or datetime.min.replace(tzinfo=timezone.utc),
                    ),
                )
            ][: max(0, request.public_discovery_job_limit)]

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

        for memory in structure_scan_memories:
            per_job_budget = 1 if remaining_budget > 0 else 0
            remaining_budget = max(0, remaining_budget - per_job_budget)
            response = self.run_structure_scan_job(
                SourceDiscoveryStructureScanRequest(
                    target_url=str(memory["url"]),
                    wave_id=memory["wave_id"],  # type: ignore[index]
                    wave_title=memory["wave_title"],  # type: ignore[index]
                    request_budget=per_job_budget,
                    caveats=["Scheduler-triggered structure scan."],
                )
            )
            jobs.append(response.job)
            structure_scans_completed += 1

        for memory in public_discovery_memories:
            per_job_budget = 1 if remaining_budget > 0 else 0
            if per_job_budget <= 0:
                break
            remaining_budget = max(0, remaining_budget - per_job_budget)
            job_type = str(memory["job_type"])
            if job_type == "feed_link_scan":
                response = self.run_feed_link_scan_job(
                    SourceDiscoveryFeedLinkScanRequest(
                        feed_url=str(memory["url"]),
                        wave_id=memory["wave_id"],  # type: ignore[index]
                        wave_title=memory["wave_title"],  # type: ignore[index]
                        request_budget=per_job_budget,
                        caveats=["Scheduler-triggered public feed discovery follow-up."],
                    )
                )
                jobs.append(response.job)
                public_discovery_jobs_completed += 1
            elif job_type == "sitemap_scan":
                response = self.run_sitemap_scan_job(
                    SourceDiscoverySitemapScanRequest(
                        sitemap_url=str(memory["url"]),
                        wave_id=memory["wave_id"],  # type: ignore[index]
                        wave_title=memory["wave_title"],  # type: ignore[index]
                        request_budget=per_job_budget,
                        caveats=["Scheduler-triggered public sitemap discovery follow-up."],
                    )
                )
                jobs.append(response.job)
                public_discovery_jobs_completed += 1
            elif job_type == "catalog_scan":
                response = self.run_catalog_scan_job(
                    SourceDiscoveryCatalogScanRequest(
                        catalog_url=str(memory["url"]),
                        wave_id=memory["wave_id"],  # type: ignore[index]
                        wave_title=memory["wave_title"],  # type: ignore[index]
                        request_budget=per_job_budget,
                        caveats=["Scheduler-triggered public catalog discovery follow-up."],
                    )
                )
                jobs.append(response.job)
                public_discovery_jobs_completed += 1

        for memory in expansion_memories:
            per_job_budget = 1 if remaining_budget > 0 else 0
            remaining_budget = max(0, remaining_budget - per_job_budget)
            response = self.run_expansion_job(
                SourceDiscoveryExpansionJobRequest(
                    seed_url=str(memory["url"]),
                    wave_id=memory["wave_id"],  # type: ignore[index]
                    wave_title=memory["wave_title"],  # type: ignore[index]
                    request_budget=per_job_budget,
                    caveats=["Scheduler-triggered bounded expansion."],
                )
            )
            jobs.append(response.job)
            expansion_jobs_completed += 1

        if request.knowledge_backfill_limit > 0:
            backfill = self.run_knowledge_backfill_job(
                SourceDiscoveryKnowledgeBackfillRequest(
                    max_snapshots=max(0, request.knowledge_backfill_limit),
                    mode="missing_only",
                    caveats=["Scheduler-triggered knowledge-node backfill."],
                )
            )
            jobs.append(backfill.job)
            knowledge_backfill_jobs_completed = 1

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

        llm_executions, duplicate_snapshots_skipped = self._run_scheduler_llm_tasks(
            tick_id=tick_id,
            limit=max(0, request.llm_task_limit),
            provider_override=request.llm_provider,
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
                structure_scans_requested=max(0, request.structure_scan_limit),
                structure_scans_completed=structure_scans_completed,
                public_discovery_jobs_requested=max(0, request.public_discovery_job_limit),
                public_discovery_jobs_completed=public_discovery_jobs_completed,
                expansion_jobs_requested=max(0, request.expansion_job_limit),
                expansion_jobs_completed=expansion_jobs_completed,
                knowledge_backfill_jobs_requested=max(0, request.knowledge_backfill_limit),
                knowledge_backfill_jobs_completed=knowledge_backfill_jobs_completed,
                record_extract_jobs_requested=max(0, request.record_source_extract_limit),
                record_extract_jobs_completed=record_extract_jobs_completed,
                llm_tasks_requested=max(0, request.llm_task_limit),
                llm_tasks_completed=len(llm_executions),
                duplicate_snapshots_skipped=duplicate_snapshots_skipped,
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
            structure_scans_completed=structure_scans_completed,
            public_discovery_jobs_completed=public_discovery_jobs_completed,
            expansion_jobs_completed=expansion_jobs_completed,
            knowledge_backfill_jobs_completed=knowledge_backfill_jobs_completed,
            record_extract_jobs_completed=record_extract_jobs_completed,
            llm_tasks_completed=len(llm_executions),
            duplicate_snapshots_skipped=duplicate_snapshots_skipped,
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
        provider_override: str | None,
        allow_network: bool,
        remaining_budget: int,
    ) -> tuple[list[WaveLlmExecutionSummary], int]:
        if limit <= 0:
            return [], 0

        candidates: list[dict[str, object]] = []
        duplicate_snapshots_skipped = 0
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
                if snapshot.knowledge_node_id and not _is_scheduler_llm_snapshot_eligible(session, snapshot):
                    duplicate_snapshots_skipped += 1
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
            return [], duplicate_snapshots_skipped

        executions: list[WaveLlmExecutionSummary] = []
        llm_service = WaveLlmService(self._settings)
        provider_config = WaveLlmProviderConfigService(self._settings)
        with wave_session_scope(self._settings.wave_monitor_database_url) as session:
            for candidate in candidates:
                wave_id = str(candidate["wave_id"])
                if session.get(WaveMonitorORM, wave_id) is None:
                    continue
                task_profile = provider_config.resolve_task_profile(
                    monitor_id=wave_id,
                    requested_provider=provider_override,  # type: ignore[arg-type]
                    requested_model=None,
                )
                provider = task_profile.provider
                marker = str(candidate["snapshot_id"])
                legacy_marker = f"source-snapshot:{marker}"
                recent_tasks = list(
                    session.scalars(
                        select(WaveLlmTaskORM)
                        .where(WaveLlmTaskORM.monitor_id == wave_id)
                        .order_by(WaveLlmTaskORM.created_at.desc())
                        .limit(50)
                    )
                )
                if any(
                    task.provider == provider
                    and ({marker, legacy_marker} & set(_loads_list(task.caveats_json)))
                    for task in recent_tasks
                ):
                    continue

                model = task_profile.model
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
        return executions, duplicate_snapshots_skipped


def _upsert_candidate_row(
    session: Session,
    seed: SourceDiscoveryCandidateSeed,
    *,
    now: str,
) -> SourceMemoryORM:
    seed = _normalize_candidate_seed(seed)
    canonical_url = _canonical_source_url(seed.url)
    parent_domain = seed.parent_domain or _domain_from_url(seed.url)
    domain_scope = _domain_scope(parent_domain)
    memory = _find_existing_memory(session, source_id=seed.source_id, canonical_url=canonical_url)
    scope_hints = _normalize_scope_hints(seed.scope_hints)
    scope_hints_json = json.dumps(scope_hints.model_dump())
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
            auth_requirement=seed.auth_requirement,
            captcha_requirement=seed.captcha_requirement,
            intake_disposition=_merge_intake_disposition(
                "hold_review",
                seed.intake_disposition,
                auth_requirement=seed.auth_requirement,
                captcha_requirement=seed.captcha_requirement,
            ),
            source_health_score=_initial_source_health_score(seed.source_class),
            timeliness_score=_initial_timeliness_score(seed.source_class),
            first_seen_at=now,
            last_seen_at=now,
            next_check_at=now,
            last_discovery_scan_at=None,
            next_discovery_scan_at=_initial_next_discovery_scan_at(seed.source_type, seed.structure_hints, now),
            discovery_scan_fail_count=0,
            health_check_fail_count=0,
            caveats_json=json.dumps(seed.caveats),
            reputation_basis_json=json.dumps([
                "Initial reputation is thin until claim outcomes accumulate.",
            ]),
            known_aliases_json=json.dumps([]),
            discovery_methods_json=json.dumps(sorted(set(seed.discovery_methods))),
            structure_hints_json=json.dumps(sorted(set(seed.structure_hints))),
            discovery_role=str(seed.discovery_role or "candidate"),
            seed_family=str(seed.seed_family or "other"),
            seed_packet_id=seed.seed_packet_id,
            seed_packet_title=seed.seed_packet_title,
            platform_family=str(seed.platform_family or "unknown"),
            source_family_tags_json=json.dumps(sorted(set(seed.source_family_tags))),
            scope_hints_json=scope_hints_json,
            last_discovery_outcome=None,
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
        memory.auth_requirement = _merge_auth_requirement(memory.auth_requirement, seed.auth_requirement)
        memory.captcha_requirement = _merge_captcha_requirement(memory.captcha_requirement, seed.captcha_requirement)
        memory.intake_disposition = _merge_intake_disposition(
            memory.intake_disposition,
            seed.intake_disposition,
            auth_requirement=memory.auth_requirement,
            captcha_requirement=memory.captcha_requirement,
        )
        memory.last_seen_at = now
        memory.known_aliases_json = json.dumps(sorted(set(aliases)))
        memory.caveats_json = json.dumps(sorted(set(_loads_list(memory.caveats_json) + seed.caveats)))
        memory.discovery_methods_json = json.dumps(
            sorted(set(_loads_list(memory.discovery_methods_json) + seed.discovery_methods))
        )
        memory.structure_hints_json = json.dumps(
            sorted(set(_loads_list(memory.structure_hints_json) + seed.structure_hints))
        )
        memory.discovery_role = _merge_discovery_role(memory.discovery_role, str(seed.discovery_role or "candidate"))
        memory.seed_family = _merge_seed_family(memory.seed_family, str(seed.seed_family or "other"))
        memory.seed_packet_id = _merge_optional_text(memory.seed_packet_id, seed.seed_packet_id)
        memory.seed_packet_title = _merge_optional_text(memory.seed_packet_title, seed.seed_packet_title)
        memory.platform_family = _merge_platform_family(memory.platform_family, str(seed.platform_family or "unknown"))
        memory.source_family_tags_json = json.dumps(
            sorted(set(_loads_list(memory.source_family_tags_json) + seed.source_family_tags))
        )
        memory.scope_hints_json = json.dumps(
            _merge_scope_hints(_loads_scope_hints(memory.scope_hints_json), scope_hints).model_dump()
        )
        if memory.next_discovery_scan_at is None:
            memory.next_discovery_scan_at = _initial_next_discovery_scan_at(
                memory.source_type or seed.source_type,
                sorted(set(_loads_list(memory.structure_hints_json) + seed.structure_hints)),
                now,
            )

    if seed.wave_id:
        canonical_seed = seed.model_copy(update={"source_id": memory.source_id})
        _upsert_wave_fit(session, canonical_seed, now=now)
    return memory


def _upsert_media_artifact_row(
    session: Session,
    *,
    source_id: str,
    origin_url: str,
    published_at: str | None,
    inspection,
    now: str,
    caveats: list[str],
    dedupe_by_hash: bool = True,
    artifact_id_suffix: str | None = None,
) -> SourceMediaArtifactORM:
    existing = None
    if dedupe_by_hash:
        existing = session.scalar(
            select(SourceMediaArtifactORM)
            .where(
                SourceMediaArtifactORM.source_id == source_id,
                SourceMediaArtifactORM.content_hash == inspection.content_hash,
                SourceMediaArtifactORM.canonical_url == inspection.canonical_url,
                SourceMediaArtifactORM.origin_url == origin_url,
                SourceMediaArtifactORM.parent_page_url == inspection.parent_page_url,
            )
            .limit(1)
        )
    artifact_identity_seed = artifact_id_suffix or inspection.canonical_url or origin_url or now
    artifact_identity_hash = hashlib.sha1(artifact_identity_seed.encode("utf-8")).hexdigest()[:8]
    artifact = existing or SourceMediaArtifactORM(
        artifact_id=f"source-media:{_safe_id(source_id)}:{inspection.content_hash[:20]}:{artifact_identity_hash}",
        source_id=source_id,
        origin_url=origin_url,
        canonical_url=inspection.canonical_url,
        media_url=inspection.media_url,
        parent_page_url=inspection.parent_page_url,
        published_at=published_at,
        discovered_at=now,
        captured_at=now,
        content_hash=inspection.content_hash,
        perceptual_hash=inspection.perceptual_hash,
        mime_type=inspection.mime_type,
        media_kind=inspection.media_kind,
        width=inspection.width,
        height=inspection.height,
        byte_length=inspection.byte_length,
        artifact_path=inspection.artifact_path,
        duplicate_cluster_id=None,
        sequence_id=None,
        frame_index=None,
        sampled_at_ms=None,
        acquisition_method=inspection.acquisition_method,
        evidence_basis=inspection.evidence_basis,
        review_state="captured",
        observed_latitude=inspection.observed_latitude,
        observed_longitude=inspection.observed_longitude,
        exif_timestamp=inspection.exif_timestamp,
        metadata_json=json.dumps(inspection.metadata),
        caveats_json=json.dumps(caveats),
    )
    artifact.origin_url = origin_url
    artifact.canonical_url = inspection.canonical_url
    artifact.media_url = inspection.media_url
    artifact.parent_page_url = inspection.parent_page_url
    artifact.published_at = published_at or artifact.published_at
    artifact.captured_at = now
    artifact.perceptual_hash = inspection.perceptual_hash or artifact.perceptual_hash
    artifact.mime_type = inspection.mime_type or artifact.mime_type
    artifact.media_kind = inspection.media_kind or artifact.media_kind
    artifact.width = inspection.width or artifact.width
    artifact.height = inspection.height or artifact.height
    artifact.byte_length = inspection.byte_length or artifact.byte_length
    artifact.artifact_path = inspection.artifact_path or artifact.artifact_path
    artifact.acquisition_method = inspection.acquisition_method or artifact.acquisition_method
    artifact.evidence_basis = inspection.evidence_basis or artifact.evidence_basis
    artifact.observed_latitude = (
        inspection.observed_latitude if inspection.observed_latitude is not None else artifact.observed_latitude
    )
    artifact.observed_longitude = (
        inspection.observed_longitude if inspection.observed_longitude is not None else artifact.observed_longitude
    )
    artifact.exif_timestamp = inspection.exif_timestamp or artifact.exif_timestamp
    artifact.metadata_json = json.dumps({**_loads_dict(artifact.metadata_json), **inspection.metadata})
    artifact.caveats_json = json.dumps(sorted(set(_loads_list(artifact.caveats_json) + caveats)))
    session.add(artifact)
    return artifact


def _ocr_engine_sequence(settings: Settings, requested_engine: str) -> list[str]:
    base_engine = (settings.source_discovery_media_ocr_default_engine if requested_engine == "auto" else requested_engine).strip().lower()
    if base_engine == "fixture":
        return ["fixture"]
    if base_engine == "rapidocr_onnx":
        return ["rapidocr_onnx"]
    engines = ["tesseract" if base_engine in {"auto", "tesseract", ""} else base_engine]
    if engines[0] == "tesseract" and settings.source_discovery_media_ocr_fallback_enabled:
        engines.append("rapidocr_onnx")
    return engines


def _should_run_ocr_fallback(
    settings: Settings,
    artifact: SourceMediaArtifactORM,
    requested_engine: str,
    result: Any,
) -> bool:
    if requested_engine not in {"auto", "tesseract"}:
        return False
    if not settings.source_discovery_media_ocr_fallback_enabled:
        return False
    if result.engine != "tesseract":
        return False
    if result.status != "completed":
        return True
    metadata = _loads_dict(artifact.metadata_json)
    captions = metadata.get("captions") if isinstance(metadata.get("captions"), list) else []
    likely_text_heavy = bool(captions) or artifact.width is not None and artifact.height is not None and artifact.width > artifact.height
    low_confidence = result.mean_confidence is None or result.mean_confidence < settings.source_discovery_media_ocr_confidence_threshold
    short_text = len(result.raw_text) < settings.source_discovery_media_ocr_min_text_length
    return low_confidence or (likely_text_heavy and short_text)


def _select_final_ocr_attempt(attempts: list[tuple[SourceMediaOcrRunORM, Any]]) -> tuple[SourceMediaOcrRunORM, Any]:
    def _score(item: tuple[SourceMediaOcrRunORM, Any]) -> float:
        row, result = item
        completed_bonus = 0.5 if result.status == "completed" else 0.0
        confidence = (result.mean_confidence or 0.0) * 0.35
        text_weight = min(0.15, len(result.raw_text) / 400.0)
        block_weight = min(0.1, len(result.blocks) / 20.0)
        selected_bonus = 0.02 if row.engine == "rapidocr_onnx" and len(result.raw_text) > len(attempts[0][1].raw_text) else 0.0
        return completed_bonus + confidence + text_weight + block_weight + selected_bonus

    return max(attempts, key=_score)


def _ocr_disagreement_caveat(results: list[Any]) -> str | None:
    texts = [_normalize_text(result.raw_text) for result in results if _normalize_text(result.raw_text)]
    if len(texts) < 2:
        return None
    if max(_token_similarity(left, right) for left in texts for right in texts if left != right) >= 0.82:
        return None
    return "Multiple OCR engines disagreed materially; review the original artifact and OCR blocks before trusting extracted text."


def _create_or_refresh_media_comparison(
    session: Session,
    settings: Settings,
    left_artifact: SourceMediaArtifactORM,
    right_artifact: SourceMediaArtifactORM,
    *,
    now: str,
    manual_caveats: list[str],
) -> SourceMediaComparisonORM:
    ordered_left, ordered_right = (left_artifact, right_artifact) if left_artifact.artifact_id <= right_artifact.artifact_id else (right_artifact, left_artifact)
    existing = session.scalar(
        select(SourceMediaComparisonORM).where(
            SourceMediaComparisonORM.left_artifact_id == ordered_left.artifact_id,
            SourceMediaComparisonORM.right_artifact_id == ordered_right.artifact_id,
        )
    )
    left_ocr = _selected_ocr_run_for_artifact(session, ordered_left.artifact_id)
    right_ocr = _selected_ocr_run_for_artifact(session, ordered_right.artifact_id)
    result = compare_media_artifacts(
        settings,
        left_artifact_path=ordered_left.artifact_path,
        right_artifact_path=ordered_right.artifact_path,
        left_content_hash=ordered_left.content_hash,
        right_content_hash=ordered_right.content_hash,
        left_perceptual_hash=ordered_left.perceptual_hash,
        right_perceptual_hash=ordered_right.perceptual_hash,
        left_canonical_url=ordered_left.canonical_url,
        right_canonical_url=ordered_right.canonical_url,
        left_parent_page_url=ordered_left.parent_page_url,
        right_parent_page_url=ordered_right.parent_page_url,
        left_exif_timestamp=ordered_left.exif_timestamp,
        right_exif_timestamp=ordered_right.exif_timestamp,
        left_ocr_text=left_ocr.raw_text if left_ocr is not None else None,
        right_ocr_text=right_ocr.raw_text if right_ocr is not None else None,
    )
    row = existing or SourceMediaComparisonORM(
        comparison_id=f"source-media-comparison:{_safe_id(ordered_left.artifact_id)}:{_safe_id(ordered_right.artifact_id)}",
        left_artifact_id=ordered_left.artifact_id,
        right_artifact_id=ordered_right.artifact_id,
        left_source_id=ordered_left.source_id,
        right_source_id=ordered_right.source_id,
        comparison_kind=result.comparison_kind,
        status=result.status,
        algorithm_version=result.algorithm_version,
        exact_hash_match=result.exact_hash_match,
        perceptual_hash_distance=result.perceptual_hash_distance,
        ssim_score=result.ssim_score,
        histogram_similarity=result.histogram_similarity,
        edge_similarity=result.edge_similarity,
        ocr_text_similarity=result.ocr_text_similarity,
        time_delta_seconds=result.time_delta_seconds,
        confidence_score=result.confidence_score,
        auto_signal_kind=result.auto_signal_kind,
        created_at=now,
        confidence_basis_json=json.dumps(result.confidence_basis),
        metadata_json=json.dumps(result.metadata),
        caveats_json=json.dumps(sorted(set(result.caveats + manual_caveats))),
    )
    row.comparison_kind = result.comparison_kind
    row.status = result.status
    row.algorithm_version = result.algorithm_version
    row.exact_hash_match = result.exact_hash_match
    row.perceptual_hash_distance = result.perceptual_hash_distance
    row.ssim_score = result.ssim_score
    row.histogram_similarity = result.histogram_similarity
    row.edge_similarity = result.edge_similarity
    row.ocr_text_similarity = result.ocr_text_similarity
    row.time_delta_seconds = result.time_delta_seconds
    row.confidence_score = result.confidence_score
    row.auto_signal_kind = result.auto_signal_kind
    row.created_at = now
    row.confidence_basis_json = json.dumps(result.confidence_basis)
    row.metadata_json = json.dumps(result.metadata)
    row.caveats_json = json.dumps(sorted(set(result.caveats + manual_caveats)))
    session.add(row)
    cluster = _upsert_media_cluster_from_comparison(session, row, ordered_left, ordered_right, now=now)
    if cluster is not None:
        ordered_left.duplicate_cluster_id = cluster.cluster_id
        ordered_right.duplicate_cluster_id = cluster.cluster_id
        session.add(ordered_left)
        session.add(ordered_right)
    _apply_media_comparison_confidence_to_pending_claims(session, row)
    session.flush()
    return row


def _selected_ocr_run_for_artifact(session: Session, artifact_id: str) -> SourceMediaOcrRunORM | None:
    selected = session.scalar(
        select(SourceMediaOcrRunORM)
        .where(SourceMediaOcrRunORM.artifact_id == artifact_id, SourceMediaOcrRunORM.selected_result.is_(True))
        .order_by(SourceMediaOcrRunORM.created_at.desc(), SourceMediaOcrRunORM.ocr_run_id.desc())
        .limit(1)
    )
    if selected is not None:
        return selected
    return session.scalar(
        select(SourceMediaOcrRunORM)
        .where(SourceMediaOcrRunORM.artifact_id == artifact_id)
        .order_by(SourceMediaOcrRunORM.created_at.desc(), SourceMediaOcrRunORM.ocr_run_id.desc())
        .limit(1)
    )


def _upsert_media_cluster_from_comparison(
    session: Session,
    comparison: SourceMediaComparisonORM,
    left_artifact: SourceMediaArtifactORM,
    right_artifact: SourceMediaArtifactORM,
    *,
    now: str,
) -> SourceMediaDuplicateClusterORM | None:
    if comparison.comparison_kind not in {"exact_duplicate", "near_duplicate"}:
        return None
    left_cluster = session.get(SourceMediaDuplicateClusterORM, left_artifact.duplicate_cluster_id) if left_artifact.duplicate_cluster_id else None
    right_cluster = session.get(SourceMediaDuplicateClusterORM, right_artifact.duplicate_cluster_id) if right_artifact.duplicate_cluster_id else None
    cluster = left_cluster or right_cluster
    if cluster is None:
        cluster = SourceMediaDuplicateClusterORM(
            cluster_id=f"source-media-cluster:{comparison.comparison_id}",
            canonical_artifact_id=left_artifact.artifact_id,
            canonical_source_id=left_artifact.source_id,
            cluster_kind="duplicate_cluster",
            status="active",
            member_count=0,
            confidence_score=comparison.confidence_score,
            first_seen_at=now,
            last_seen_at=now,
            confidence_basis_json=json.dumps(_loads_list(comparison.confidence_basis_json)),
            member_source_ids_json=json.dumps(sorted({left_artifact.source_id, right_artifact.source_id})),
            caveats_json=json.dumps(["Duplicate cluster groups artifacts that look like the same underlying visual evidence."]),
        )
        session.add(cluster)
    if left_cluster is not None and right_cluster is not None and left_cluster.cluster_id != right_cluster.cluster_id:
        for artifact in session.scalars(select(SourceMediaArtifactORM).where(SourceMediaArtifactORM.duplicate_cluster_id == right_cluster.cluster_id)):
            artifact.duplicate_cluster_id = left_cluster.cluster_id
            session.add(artifact)
        session.delete(right_cluster)
        cluster = left_cluster
    left_artifact.duplicate_cluster_id = cluster.cluster_id
    right_artifact.duplicate_cluster_id = cluster.cluster_id
    session.add(left_artifact)
    session.add(right_artifact)
    session.flush()
    _refresh_media_cluster(session, cluster, comparison=comparison, now=now)
    return cluster


def _refresh_media_cluster(
    session: Session,
    cluster: SourceMediaDuplicateClusterORM,
    *,
    comparison: SourceMediaComparisonORM,
    now: str,
) -> None:
    artifacts = list(
        session.scalars(
            select(SourceMediaArtifactORM)
            .where(SourceMediaArtifactORM.duplicate_cluster_id == cluster.cluster_id)
            .order_by(SourceMediaArtifactORM.captured_at.asc(), SourceMediaArtifactORM.artifact_id.asc())
        )
    )
    if not artifacts:
        return
    cluster.canonical_artifact_id = artifacts[0].artifact_id
    cluster.canonical_source_id = artifacts[0].source_id
    cluster.member_count = len(artifacts)
    cluster.first_seen_at = artifacts[0].captured_at
    cluster.last_seen_at = artifacts[-1].captured_at
    cluster.confidence_score = max(cluster.confidence_score, comparison.confidence_score)
    cluster.confidence_basis_json = json.dumps(sorted(set(_loads_list(cluster.confidence_basis_json) + _loads_list(comparison.confidence_basis_json))))
    cluster.member_source_ids_json = json.dumps(sorted({artifact.source_id for artifact in artifacts}))
    cluster.status = "active"
    cluster.caveats_json = json.dumps(sorted(set(_loads_list(cluster.caveats_json) + [
        "Cluster membership is deterministic duplicate grouping, not truth adjudication.",
    ])))
    session.add(cluster)


def _cluster_for_comparison(session: Session, comparison: SourceMediaComparisonORM) -> SourceMediaDuplicateClusterORM | None:
    left_artifact = session.get(SourceMediaArtifactORM, comparison.left_artifact_id)
    right_artifact = session.get(SourceMediaArtifactORM, comparison.right_artifact_id)
    cluster_id = left_artifact.duplicate_cluster_id if left_artifact is not None else None
    if cluster_id and right_artifact is not None and right_artifact.duplicate_cluster_id == cluster_id:
        return session.get(SourceMediaDuplicateClusterORM, cluster_id)
    return None


def _auto_compare_media_artifact(session: Session, settings: Settings, artifact: SourceMediaArtifactORM, *, now: str) -> list[SourceMediaComparisonORM]:
    comparisons: list[SourceMediaComparisonORM] = []
    for candidate in _comparison_candidate_artifacts(session, artifact, cap=max(1, settings.source_discovery_media_comparison_candidate_cap)):
        comparisons.append(
            _create_or_refresh_media_comparison(
                session,
                settings,
                artifact,
                candidate,
                now=now,
                manual_caveats=["Auto comparison ran as part of bounded media artifact ingestion."],
            )
        )
    return comparisons


def _comparison_candidate_artifacts(session: Session, artifact: SourceMediaArtifactORM, *, cap: int) -> list[SourceMediaArtifactORM]:
    current_wave_ids = set(
        session.scalars(select(SourceWaveFitORM.wave_id).where(SourceWaveFitORM.source_id == artifact.source_id))
    )
    recent = list(
        session.scalars(
            select(SourceMediaArtifactORM)
            .where(SourceMediaArtifactORM.artifact_id != artifact.artifact_id)
            .order_by(SourceMediaArtifactORM.captured_at.desc(), SourceMediaArtifactORM.artifact_id.desc())
            .limit(max(cap * 12, 40))
        )
    )
    scored: list[tuple[int, SourceMediaArtifactORM]] = []
    for candidate in recent:
        score = 0
        if candidate.source_id == artifact.source_id:
            score += 4
        if candidate.canonical_url == artifact.canonical_url:
            score += 3
        if artifact.parent_page_url and candidate.parent_page_url and artifact.parent_page_url == candidate.parent_page_url:
            score += 2
        if current_wave_ids:
            other_wave_ids = set(
                session.scalars(select(SourceWaveFitORM.wave_id).where(SourceWaveFitORM.source_id == candidate.source_id))
            )
            if current_wave_ids.intersection(other_wave_ids):
                score += 1
        if score > 0:
            scored.append((score, candidate))
    scored.sort(key=lambda item: (item[0], item[1].captured_at, item[1].artifact_id), reverse=True)
    selected: list[SourceMediaArtifactORM] = []
    seen: set[str] = set()
    for _, candidate in scored:
        if candidate.artifact_id in seen:
            continue
        seen.add(candidate.artifact_id)
        selected.append(candidate)
        if len(selected) >= cap:
            break
    return selected


def _apply_media_comparison_confidence_to_pending_claims(session: Session, comparison: SourceMediaComparisonORM) -> None:
    if comparison.auto_signal_kind is None:
        return
    basis_line = f"Deterministic media comparison {comparison.auto_signal_kind} from {comparison.comparison_id} adjusted pending-claim confidence."
    for source_id in {comparison.left_source_id, comparison.right_source_id}:
        for candidate in _pending_review_claim_candidates_for_source(session, source_id):
            delta = 0.0
            if comparison.auto_signal_kind == "duplicate_cluster_joined":
                delta = 0.03
            elif comparison.auto_signal_kind == "minor_change_detected":
                delta = 0.08 if candidate.claim_type == "change" else 0.03
            elif comparison.auto_signal_kind == "major_change_detected":
                delta = 0.14 if candidate.claim_type == "change" else 0.06
            elif comparison.auto_signal_kind == "different_scene_conflict":
                delta = -0.08 if candidate.claim_type in {"change", "location", "state"} else -0.04
            candidate.confidence_score = _clamp(candidate.confidence_score + delta)
            candidate.confidence_basis_json = json.dumps(
                sorted(set(_loads_list(candidate.confidence_basis_json) + [basis_line]))
            )
            session.add(candidate)


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
    context = _build_discovery_priority_context(session)
    _ensure_knowledge_nodes_for_source(session, memory.source_id)
    snapshots = list(
        session.scalars(
            select(SourceContentSnapshotORM)
            .where(SourceContentSnapshotORM.source_id == memory.source_id)
            .order_by(SourceContentSnapshotORM.fetched_at.desc())
            .limit(max(0, limit))
        )
    )
    node_ids = sorted({snapshot.knowledge_node_id for snapshot in snapshots if snapshot.knowledge_node_id})
    nodes = [
        node
        for node in (session.get(SourceKnowledgeNodeORM, node_id) for node_id in node_ids)
        if node is not None
    ]
    media_artifacts = list(
        session.scalars(
            select(SourceMediaArtifactORM)
            .where(SourceMediaArtifactORM.source_id == memory.source_id)
            .order_by(SourceMediaArtifactORM.captured_at.desc(), SourceMediaArtifactORM.artifact_id.desc())
            .limit(max(0, limit))
        )
    )
    cluster_ids = sorted({artifact.duplicate_cluster_id for artifact in media_artifacts if artifact.duplicate_cluster_id})
    sequence_ids = sorted({artifact.sequence_id for artifact in media_artifacts if artifact.sequence_id})
    artifact_ids = [artifact.artifact_id for artifact in media_artifacts]
    media_clusters = [
        cluster
        for cluster in (session.get(SourceMediaDuplicateClusterORM, cluster_id) for cluster_id in cluster_ids)
        if cluster is not None
    ]
    media_sequences = [
        sequence
        for sequence in (session.get(SourceMediaSequenceORM, sequence_id) for sequence_id in sequence_ids)
        if sequence is not None
    ]
    media_comparisons = list(
        session.scalars(
            select(SourceMediaComparisonORM)
            .where(
                SourceMediaComparisonORM.left_source_id == memory.source_id,
            )
            .order_by(SourceMediaComparisonORM.created_at.desc(), SourceMediaComparisonORM.comparison_id.desc())
            .limit(max(0, limit * 2))
        )
    )
    seen_comparison_ids = {row.comparison_id for row in media_comparisons}
    if artifact_ids:
        extra_comparisons = list(
            session.scalars(
                select(SourceMediaComparisonORM)
                .where(SourceMediaComparisonORM.right_source_id == memory.source_id)
                .order_by(SourceMediaComparisonORM.created_at.desc(), SourceMediaComparisonORM.comparison_id.desc())
                .limit(max(0, limit * 2))
            )
        )
        for row in extra_comparisons:
            if row.comparison_id not in seen_comparison_ids:
                media_comparisons.append(row)
                seen_comparison_ids.add(row.comparison_id)
    auto_media_signals = [
        _serialize_auto_media_signal(row)
        for row in media_comparisons
        if row.auto_signal_kind is not None
    ]
    media_ocr_runs = list(
        session.scalars(
            select(SourceMediaOcrRunORM)
            .where(SourceMediaOcrRunORM.source_id == memory.source_id)
            .order_by(SourceMediaOcrRunORM.created_at.desc(), SourceMediaOcrRunORM.ocr_run_id.desc())
            .limit(max(0, limit))
        )
    )
    media_interpretations = list(
        session.scalars(
            select(SourceMediaInterpretationORM)
            .where(SourceMediaInterpretationORM.source_id == memory.source_id)
            .order_by(SourceMediaInterpretationORM.created_at.desc(), SourceMediaInterpretationORM.interpretation_id.desc())
            .limit(max(0, limit))
        )
    )
    media_geolocations = list(
        session.scalars(
            select(SourceMediaGeolocationRunORM)
            .where(SourceMediaGeolocationRunORM.source_id == memory.source_id)
            .order_by(SourceMediaGeolocationRunORM.created_at.desc(), SourceMediaGeolocationRunORM.geolocation_run_id.desc())
            .limit(max(0, limit))
        )
    )
    pending_review_claims = _pending_review_claim_candidates_for_source(session, memory.source_id, limit=max(0, limit))
    return SourceDiscoveryMemoryDetailResponse(
        memory=_serialize_memory(session, memory, context=context),
        wave_fits=[_serialize_wave_fit(fit) for fit in _fits_for_source(session, memory.source_id)],
        snapshots=[_serialize_snapshot(session, snapshot) for snapshot in snapshots],
        knowledge_nodes=[_serialize_knowledge_node(session, node) for node in nodes],
        media_artifacts=[_serialize_media_artifact(artifact) for artifact in media_artifacts],
        media_clusters=[_serialize_media_cluster(cluster) for cluster in media_clusters],
        media_comparisons=[_serialize_media_comparison(row) for row in media_comparisons[: max(0, limit * 2)]],
        auto_media_signals=auto_media_signals[: max(0, limit * 2)],
        media_sequences=[_serialize_media_sequence(row) for row in media_sequences],
        media_ocr_runs=[_serialize_media_ocr_run(row) for row in media_ocr_runs],
        media_interpretations=[_serialize_media_interpretation(row) for row in media_interpretations],
        media_geolocations=[_serialize_media_geolocation_run(row) for row in media_geolocations],
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
        pending_review_claims=[_serialize_review_claim_candidate(row) for row in pending_review_claims],
        pending_claim_count=len(_pending_review_claim_candidates_for_source(session, memory.source_id)),
        latest_review_claim_at=pending_review_claims[0].created_at if pending_review_claims else None,
        caveats=SOURCE_DISCOVERY_CAVEATS,
    )


def _serialize_memory(
    session_or_memory: Session | SourceMemoryORM,
    memory: SourceMemoryORM | None = None,
    *,
    context: _DiscoveryPriorityContext | None = None,
) -> SourceDiscoveryMemory:
    if memory is None:
        session = None
        memory = session_or_memory  # type: ignore[assignment]
    else:
        session = session_or_memory  # type: ignore[assignment]
    now = _utc_now()
    active_context = context
    if session is not None and active_context is None:
        active_context = _build_discovery_priority_context(session)
    if session is not None and active_context is not None:
        priority_score, priority, priority_basis = _compute_discovery_priority(
            session,
            memory,
            now=now,
            context=active_context,
        )
    else:
        priority_score, priority, priority_basis = (0, "low", [])
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
        auth_requirement=memory.auth_requirement,  # type: ignore[arg-type]
        captcha_requirement=memory.captcha_requirement,  # type: ignore[arg-type]
        intake_disposition=memory.intake_disposition,  # type: ignore[arg-type]
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
        discovery_methods=_loads_list(memory.discovery_methods_json),
        structure_hints=_loads_list(memory.structure_hints_json),
        discovery_role=memory.discovery_role,  # type: ignore[arg-type]
        seed_family=memory.seed_family,  # type: ignore[arg-type]
        seed_packet_id=memory.seed_packet_id,
        seed_packet_title=memory.seed_packet_title,
        platform_family=memory.platform_family,  # type: ignore[arg-type]
        source_family_tags=_loads_list(memory.source_family_tags_json),
        scope_hints=_loads_scope_hints(memory.scope_hints_json),
        first_seen_at=memory.first_seen_at,
        last_seen_at=memory.last_seen_at,
        last_reputation_event_at=memory.last_reputation_event_at,
        next_check_at=memory.next_check_at,
        last_discovery_scan_at=memory.last_discovery_scan_at,
        next_discovery_scan_at=memory.next_discovery_scan_at,
        discovery_scan_fail_count=memory.discovery_scan_fail_count,
        health_check_fail_count=memory.health_check_fail_count,
        next_discovery_action=_suggest_discovery_action(memory),  # type: ignore[arg-type]
        discovery_priority_score=priority_score,
        discovery_priority=priority,  # type: ignore[arg-type]
        discovery_priority_basis=priority_basis,
        last_discovery_outcome=memory.last_discovery_outcome,
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


def _serialize_discovery_run(session: Session, job: SourceDiscoveryJobORM) -> SourceDiscoveryDiscoveryRunSummary:
    root_memory = _find_memory_by_canonical_url(session, job.seed_url) if job.seed_url else None
    outcome_summary = job.outcome_summary
    if not outcome_summary:
        if job.status == "completed":
            outcome_summary = f"{job.job_type} completed with {len(_loads_list(job.discovered_source_ids_json))} discovered source ids."
        elif job.rejected_reason:
            outcome_summary = job.rejected_reason
    return SourceDiscoveryDiscoveryRunSummary(
        job_id=job.job_id,
        job_type=job.job_type,
        root_source_id=root_memory.source_id if root_memory is not None else None,
        root_url=job.seed_url,
        status=job.status,
        discovered_candidate_count=len(_loads_list(job.discovered_source_ids_json)),
        used_requests=job.used_requests,
        rejected_reason=job.rejected_reason,
        outcome_summary=outcome_summary,
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


def _serialize_snapshot(session: Session, snapshot: SourceContentSnapshotORM) -> SourceDiscoveryContentSnapshotSummary:
    node = session.get(SourceKnowledgeNodeORM, snapshot.knowledge_node_id) if snapshot.knowledge_node_id else None
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
        knowledge_node_id=snapshot.knowledge_node_id,
        canonical_snapshot_id=snapshot.canonical_snapshot_id,
        duplicate_class=snapshot.duplicate_class,  # type: ignore[arg-type]
        body_storage_mode=snapshot.body_storage_mode,  # type: ignore[arg-type]
        supporting_source_count=node.supporting_source_count if node is not None else 1,
        independent_source_count=node.independent_source_count if node is not None else 1,
        as_detailed_in_addition_to=_loads_list(node.as_detailed_in_addition_to_json) if node is not None else [],
        caveats=_loads_list(snapshot.caveats_json),
    )


def _serialize_media_artifact(artifact: SourceMediaArtifactORM) -> SourceDiscoveryMediaArtifactSummary:
    return SourceDiscoveryMediaArtifactSummary(
        artifact_id=artifact.artifact_id,
        source_id=artifact.source_id,
        origin_url=artifact.origin_url,
        canonical_url=artifact.canonical_url,
        media_url=artifact.media_url,
        parent_page_url=artifact.parent_page_url,
        published_at=artifact.published_at,
        discovered_at=artifact.discovered_at,
        captured_at=artifact.captured_at,
        content_hash=artifact.content_hash,
        perceptual_hash=artifact.perceptual_hash,
        mime_type=artifact.mime_type,
        media_kind=artifact.media_kind,  # type: ignore[arg-type]
        width=artifact.width,
        height=artifact.height,
        byte_length=artifact.byte_length,
        artifact_path=artifact.artifact_path,
        duplicate_cluster_id=artifact.duplicate_cluster_id,
        sequence_id=artifact.sequence_id,
        frame_index=artifact.frame_index,
        sampled_at_ms=artifact.sampled_at_ms,
        acquisition_method=artifact.acquisition_method,
        evidence_basis=artifact.evidence_basis,  # type: ignore[arg-type]
        review_state=artifact.review_state,  # type: ignore[arg-type]
        observed_latitude=artifact.observed_latitude,
        observed_longitude=artifact.observed_longitude,
        exif_timestamp=artifact.exif_timestamp,
        metadata=_loads_dict(artifact.metadata_json),
        caveats=_loads_list(artifact.caveats_json),
    )


def _serialize_media_ocr_run(row: SourceMediaOcrRunORM) -> SourceDiscoveryMediaOcrRunSummary:
    block_rows = _loads_list_of_dicts(_loads_dict(row.metadata_json).get("blocks"))
    blocks = [
        SourceDiscoveryMediaOcrBlock(
            block_index=int(item.get("block_index", index)),
            text=str(item.get("text", "")),
            confidence=_coerce_optional_float(item.get("confidence")),
            left=_coerce_optional_int(item.get("left")),
            top=_coerce_optional_int(item.get("top")),
            width=_coerce_optional_int(item.get("width")),
            height=_coerce_optional_int(item.get("height")),
        )
        for index, item in enumerate(block_rows)
        if str(item.get("text", "")).strip()
    ]
    return SourceDiscoveryMediaOcrRunSummary(
        ocr_run_id=row.ocr_run_id,
        artifact_id=row.artifact_id,
        source_id=row.source_id,
        engine=row.engine,
        engine_version=row.engine_version,
        status=row.status,
        attempt_index=row.attempt_index,
        selected_result=row.selected_result,
        preprocessing=_loads_list(row.preprocessing_json),
        raw_text=row.raw_text,
        text_length=row.text_length,
        mean_confidence=row.mean_confidence,
        line_count=row.line_count,
        metadata=_loads_dict(row.metadata_json),
        created_at=row.created_at,
        caveats=_loads_list(row.caveats_json),
        blocks=blocks,
    )


def _serialize_media_interpretation(row: SourceMediaInterpretationORM) -> SourceDiscoveryMediaInterpretationSummary:
    return SourceDiscoveryMediaInterpretationSummary(
        interpretation_id=row.interpretation_id,
        artifact_id=row.artifact_id,
        source_id=row.source_id,
        ocr_run_id=row.ocr_run_id,
        adapter=row.adapter,
        model_name=row.model_name,
        status=row.status,
        review_state=row.review_state,  # type: ignore[arg-type]
        people_analysis_performed=row.people_analysis_performed,
        uncertainty_ceiling=row.uncertainty_ceiling,
        scene_labels=_loads_list(row.scene_labels_json),
        scene_summary=row.scene_summary,
        place_hypothesis=row.place_hypothesis,
        place_confidence=row.place_confidence,
        place_basis=row.place_basis,
        time_of_day_guess=row.time_of_day_guess,
        time_of_day_confidence=row.time_of_day_confidence,
        time_of_day_basis=row.time_of_day_basis,
        season_guess=row.season_guess,
        season_confidence=row.season_confidence,
        season_basis=row.season_basis,
        geolocation_hypothesis=row.geolocation_hypothesis,
        geolocation_confidence=row.geolocation_confidence,
        geolocation_basis=row.geolocation_basis,
        observed_latitude=row.observed_latitude,
        observed_longitude=row.observed_longitude,
        reasoning_lines=_loads_list(row.reasoning_lines_json),
        metadata=_loads_dict(row.metadata_json),
        created_at=row.created_at,
        caveats=_loads_list(row.caveats_json),
    )


def _build_media_geolocation_inherited_context(
    session: Session,
    artifact: SourceMediaArtifactORM,
) -> dict[str, Any]:
    related_artifact_ids: list[str] = []
    relationship_by_artifact_id: dict[str, set[str]] = {}
    comparison_by_artifact_id: dict[str, str] = {}
    if artifact.duplicate_cluster_id:
        cluster_artifacts = list(
            session.scalars(
                select(SourceMediaArtifactORM)
                .where(SourceMediaArtifactORM.duplicate_cluster_id == artifact.duplicate_cluster_id)
                .order_by(SourceMediaArtifactORM.frame_index.asc().nulls_last(), SourceMediaArtifactORM.artifact_id.asc())
                .limit(8)
            )
        )
        for row in cluster_artifacts:
            if row.artifact_id == artifact.artifact_id:
                continue
            if row.artifact_id not in related_artifact_ids:
                related_artifact_ids.append(row.artifact_id)
            relationship_by_artifact_id.setdefault(row.artifact_id, set()).add("duplicate_cluster")
    if artifact.sequence_id:
        sequence_artifacts = list(
            session.scalars(
                select(SourceMediaArtifactORM)
                .where(SourceMediaArtifactORM.sequence_id == artifact.sequence_id)
                .order_by(SourceMediaArtifactORM.frame_index.asc().nulls_last(), SourceMediaArtifactORM.artifact_id.asc())
                .limit(12)
            )
        )
        for row in sequence_artifacts:
            if row.artifact_id == artifact.artifact_id:
                continue
            if artifact.frame_index is not None and row.frame_index is not None and abs(row.frame_index - artifact.frame_index) > 2:
                continue
            if row.artifact_id not in related_artifact_ids:
                related_artifact_ids.append(row.artifact_id)
            relationship_by_artifact_id.setdefault(row.artifact_id, set()).add("adjacent_sequence_frame")
    comparisons = list(
        session.scalars(
            select(SourceMediaComparisonORM)
            .where(
                or_(
                    SourceMediaComparisonORM.left_artifact_id == artifact.artifact_id,
                    SourceMediaComparisonORM.right_artifact_id == artifact.artifact_id,
                )
            )
            .order_by(SourceMediaComparisonORM.created_at.desc(), SourceMediaComparisonORM.comparison_id.desc())
            .limit(16)
        )
    )
    for comparison in comparisons:
        if comparison.comparison_kind not in {"exact_duplicate", "near_duplicate", "same_scene_minor_change", "same_location_major_change"}:
            continue
        other_artifact_id = comparison.right_artifact_id if comparison.left_artifact_id == artifact.artifact_id else comparison.left_artifact_id
        if other_artifact_id == artifact.artifact_id:
            continue
        if other_artifact_id not in related_artifact_ids:
            related_artifact_ids.append(other_artifact_id)
        relationship_by_artifact_id.setdefault(other_artifact_id, set()).add(comparison.comparison_kind)
        comparison_by_artifact_id.setdefault(other_artifact_id, comparison.comparison_id)
    merged_clues = {
        "coordinateClues": [],
        "placeTextClues": [],
        "scriptLanguageClues": [],
        "environmentClues": [],
        "timeClues": [],
        "rejectedClues": [],
    }
    candidate_labels: list[str] = []
    lineage: list[dict[str, Any]] = []
    for related_artifact_id in related_artifact_ids[:8]:
        related_artifact = session.get(SourceMediaArtifactORM, related_artifact_id)
        if related_artifact is None:
            continue
        latest_geolocation = session.scalar(
            select(SourceMediaGeolocationRunORM)
            .where(SourceMediaGeolocationRunORM.artifact_id == related_artifact_id)
            .order_by(SourceMediaGeolocationRunORM.created_at.desc(), SourceMediaGeolocationRunORM.geolocation_run_id.desc())
            .limit(1)
        )
        latest_interpretation = session.scalar(
            select(SourceMediaInterpretationORM)
            .where(SourceMediaInterpretationORM.artifact_id == related_artifact_id)
            .order_by(SourceMediaInterpretationORM.created_at.desc(), SourceMediaInterpretationORM.interpretation_id.desc())
            .limit(1)
        )
        if latest_geolocation is not None:
            geolocation_metadata = _loads_dict(latest_geolocation.metadata_json)
            clue_packet = geolocation_metadata.get("cluePacket", {}) if isinstance(geolocation_metadata.get("cluePacket"), dict) else {}
            for source_key, target_key in [
                ("coordinateClues", "coordinateClues"),
                ("placeTextClues", "placeTextClues"),
                ("scriptLanguageClues", "scriptLanguageClues"),
                ("environmentClues", "environmentClues"),
                ("timeClues", "timeClues"),
                ("rejectedClues", "rejectedClues"),
            ]:
                raw_items = clue_packet.get(source_key)
                if not isinstance(raw_items, list):
                    continue
                for raw in raw_items[:12]:
                    if not isinstance(raw, dict):
                        continue
                    merged_clues[target_key].append(
                        {
                            **raw,
                            "inheritedFromArtifactId": raw.get("inheritedFromArtifactId") or related_artifact_id,
                            "inheritedFromGeolocationRunId": raw.get("inheritedFromGeolocationRunId") or latest_geolocation.geolocation_run_id,
                            "inheritedFromComparisonId": raw.get("inheritedFromComparisonId") or comparison_by_artifact_id.get(related_artifact_id),
                        }
                    )
            if latest_geolocation.top_label and latest_geolocation.top_label not in candidate_labels:
                candidate_labels.append(latest_geolocation.top_label)
        if latest_interpretation is not None:
            for label in [latest_interpretation.place_hypothesis, latest_interpretation.geolocation_hypothesis]:
                if label and label not in candidate_labels:
                    candidate_labels.append(label)
        lineage.append(
            {
                "artifactId": related_artifact_id,
                "geolocationRunId": latest_geolocation.geolocation_run_id if latest_geolocation is not None else None,
                "comparisonId": comparison_by_artifact_id.get(related_artifact_id),
                "relationshipKinds": sorted(relationship_by_artifact_id.get(related_artifact_id, set())),
            }
        )
    return {
        "relatedArtifactIds": related_artifact_ids[:8],
        "relationshipKinds": sorted({kind for values in relationship_by_artifact_id.values() for kind in values}),
        "candidateLabels": candidate_labels[:24],
        "cluePacket": merged_clues,
        "lineage": lineage,
    }


def _serialize_geolocation_clue_packet(packet: Any) -> dict[str, Any]:
    return {
        "coordinateClues": [_serialize_geolocation_clue(item) for item in getattr(packet, "coordinate_clues", [])],
        "placeTextClues": [_serialize_geolocation_clue(item) for item in getattr(packet, "place_text_clues", [])],
        "scriptLanguageClues": [_serialize_geolocation_clue(item) for item in getattr(packet, "script_language_clues", [])],
        "environmentClues": [_serialize_geolocation_clue(item) for item in getattr(packet, "environment_clues", [])],
        "timeClues": [_serialize_geolocation_clue(item) for item in getattr(packet, "time_clues", [])],
        "rejectedClues": [_serialize_geolocation_clue(item) for item in getattr(packet, "rejected_clues", [])],
    }


def _serialize_geolocation_clue(item: Any) -> dict[str, Any]:
    return {
        "clueType": getattr(item, "clue_type", None),
        "text": getattr(item, "text", None),
        "confidence": getattr(item, "confidence", None),
        "normalizedValue": getattr(item, "normalized_value", None),
        "latitude": getattr(item, "latitude", None),
        "longitude": getattr(item, "longitude", None),
        "reason": getattr(item, "reason", None),
        "inherited": bool(getattr(item, "inherited", False)),
        "inheritedFromArtifactId": getattr(item, "inherited_from_artifact_id", None),
        "inheritedFromGeolocationRunId": getattr(item, "inherited_from_geolocation_run_id", None),
        "inheritedFromComparisonId": getattr(item, "inherited_from_comparison_id", None),
        "metadata": getattr(item, "metadata", {}) or {},
    }


def _serialize_geolocation_engine_attempt(item: Any) -> dict[str, Any]:
    return {
        "engine": getattr(item, "engine", None),
        "role": getattr(item, "role", None),
        "status": getattr(item, "status", None),
        "modelName": getattr(item, "model_name", None),
        "warmState": getattr(item, "warm_state", None),
        "availabilityReason": getattr(item, "availability_reason", None),
        "producedCandidateCount": getattr(item, "produced_candidate_count", 0),
        "metadata": getattr(item, "metadata", {}) or {},
        "caveats": list(getattr(item, "caveats", []) or []),
    }


def _serialize_media_geolocation_run(row: SourceMediaGeolocationRunORM) -> SourceDiscoveryMediaGeolocationRunSummary:
    metadata = _loads_dict(row.metadata_json)
    candidates = []
    for item in _loads_list(row.candidates_json):
        if not isinstance(item, dict):
            continue
        candidates.append(
            {
                "rank": item.get("rank"),
                "candidate_kind": item.get("candidate_kind"),
                "label": item.get("label"),
                "latitude": item.get("latitude"),
                "longitude": item.get("longitude"),
                "confidence": item.get("confidence"),
                "confidence_score": item.get("confidence_score"),
                "confidence_ceiling": item.get("confidence_ceiling"),
                "engine": item.get("engine"),
                "basis": item.get("basis"),
                "supporting_evidence": item.get("supporting_evidence"),
                "contradicting_evidence": item.get("contradicting_evidence"),
                "engine_agreement": item.get("engine_agreement"),
                "provenance_chain": item.get("provenance_chain"),
                "inherited": item.get("inherited"),
                "inherited_from_artifact_ids": item.get("inherited_from_artifact_ids"),
                "metadata": item.get("metadata"),
                "caveats": item.get("caveats"),
            }
        )
    return SourceDiscoveryMediaGeolocationRunSummary(
        geolocation_run_id=row.geolocation_run_id,
        artifact_id=row.artifact_id,
        source_id=row.source_id,
        ocr_run_id=row.ocr_run_id,
        interpretation_id=row.interpretation_id,
        engine=row.engine,  # type: ignore[arg-type]
        model_name=row.model_name,
        analyst_adapter=row.analyst_adapter,  # type: ignore[arg-type]
        analyst_model_name=row.analyst_model_name,
        status=row.status,  # type: ignore[arg-type]
        review_state=row.review_state,  # type: ignore[arg-type]
        candidate_count=row.candidate_count,
        top_label=row.top_label,
        top_latitude=row.top_latitude,
        top_longitude=row.top_longitude,
        top_confidence=row.top_confidence,
        top_confidence_ceiling=_coerce_float(metadata.get("confidenceCeiling")),
        top_basis=row.top_basis,
        summary=row.summary,
        confidence_ceiling=_coerce_float(metadata.get("confidenceCeiling")),
        supporting_evidence=[str(item) for item in metadata.get("supportingEvidence", []) if str(item).strip()] if isinstance(metadata.get("supportingEvidence"), list) else [],
        contradicting_evidence=[str(item) for item in metadata.get("contradictingEvidence", []) if str(item).strip()] if isinstance(metadata.get("contradictingEvidence"), list) else [],
        engine_agreement=metadata.get("engineAgreement", {}) if isinstance(metadata.get("engineAgreement"), dict) else {},
        provenance_chain=[str(item) for item in metadata.get("provenanceChain", []) if str(item).strip()] if isinstance(metadata.get("provenanceChain"), list) else [],
        inherited_from_artifact_ids=[str(item) for item in metadata.get("inheritedFromArtifactIds", []) if str(item).strip()] if isinstance(metadata.get("inheritedFromArtifactIds"), list) else [],
        clue_packet=metadata.get("cluePacket", {}) if isinstance(metadata.get("cluePacket"), dict) else {},
        engine_attempts=metadata.get("engineAttempts", []) if isinstance(metadata.get("engineAttempts"), list) else [],
        reasoning_lines=_loads_list(row.reasoning_lines_json),
        metadata=metadata,
        candidates=candidates,  # type: ignore[arg-type]
        created_at=row.created_at,
        caveats=_loads_list(row.caveats_json),
    )


def _serialize_media_cluster(row: SourceMediaDuplicateClusterORM) -> SourceDiscoveryMediaDuplicateClusterSummary:
    return SourceDiscoveryMediaDuplicateClusterSummary(
        cluster_id=row.cluster_id,
        canonical_artifact_id=row.canonical_artifact_id,
        canonical_source_id=row.canonical_source_id,
        cluster_kind=row.cluster_kind,
        status=row.status,
        member_count=row.member_count,
        confidence_score=row.confidence_score,
        first_seen_at=row.first_seen_at,
        last_seen_at=row.last_seen_at,
        confidence_basis=_loads_list(row.confidence_basis_json),
        member_source_ids=_loads_list(row.member_source_ids_json),
        caveats=_loads_list(row.caveats_json),
    )


def _serialize_media_comparison(row: SourceMediaComparisonORM) -> SourceDiscoveryMediaComparisonSummary:
    return SourceDiscoveryMediaComparisonSummary(
        comparison_id=row.comparison_id,
        left_artifact_id=row.left_artifact_id,
        right_artifact_id=row.right_artifact_id,
        left_source_id=row.left_source_id,
        right_source_id=row.right_source_id,
        comparison_kind=row.comparison_kind,  # type: ignore[arg-type]
        status=row.status,  # type: ignore[arg-type]
        algorithm_version=row.algorithm_version,
        exact_hash_match=row.exact_hash_match,
        perceptual_hash_distance=row.perceptual_hash_distance,
        ssim_score=row.ssim_score,
        histogram_similarity=row.histogram_similarity,
        edge_similarity=row.edge_similarity,
        ocr_text_similarity=row.ocr_text_similarity,
        time_delta_seconds=row.time_delta_seconds,
        confidence_score=row.confidence_score,
        confidence_basis=_loads_list(row.confidence_basis_json),
        auto_signal_kind=row.auto_signal_kind,  # type: ignore[arg-type]
        metadata=_loads_dict(row.metadata_json),
        created_at=row.created_at,
        caveats=_loads_list(row.caveats_json),
    )


def _serialize_auto_media_signal(row: SourceMediaComparisonORM) -> SourceDiscoveryAutoMediaSignalSummary:
    return SourceDiscoveryAutoMediaSignalSummary(
        comparison_id=row.comparison_id,
        signal_kind=row.auto_signal_kind,  # type: ignore[arg-type]
        artifact_ids=[row.left_artifact_id, row.right_artifact_id],
        confidence_score=row.confidence_score,
        confidence_basis=_loads_list(row.confidence_basis_json),
        created_at=row.created_at,
        caveats=_loads_list(row.caveats_json),
    )


def _serialize_media_sequence(row: SourceMediaSequenceORM) -> SourceDiscoveryMediaSequenceSummary:
    return SourceDiscoveryMediaSequenceSummary(
        sequence_id=row.sequence_id,
        source_id=row.source_id,
        origin_url=row.origin_url,
        canonical_url=row.canonical_url,
        parent_page_url=row.parent_page_url,
        media_kind=row.media_kind,  # type: ignore[arg-type]
        sampler=row.sampler,
        status=row.status,
        source_span_seconds=row.source_span_seconds,
        frame_count=row.frame_count,
        sample_interval_seconds=row.sample_interval_seconds,
        request_budget=row.request_budget,
        used_requests=row.used_requests,
        created_at=row.created_at,
        metadata=_loads_dict(row.metadata_json),
        caveats=_loads_list(row.caveats_json),
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


def _serialize_review_claim_candidate(
    row: SourceReviewClaimCandidateORM,
) -> SourceDiscoveryReviewClaimCandidateSummary:
    return SourceDiscoveryReviewClaimCandidateSummary(
        claim_candidate_id=row.claim_candidate_id,
        review_id=row.review_id,
        task_id=row.task_id,
        source_id=row.source_id,
        wave_id=row.wave_id,
        snapshot_id=row.snapshot_id,
        knowledge_node_id=row.knowledge_node_id,
        claim_index=row.claim_index,
        claim_text=row.claim_text,
        claim_type=row.claim_type,
        evidence_basis=row.evidence_basis,
        status=row.status,  # type: ignore[arg-type]
        confidence_score=row.confidence_score,
        confidence_basis=_loads_list(row.confidence_basis_json),
        created_at=row.created_at,
        applied_at=row.applied_at,
        caveats=_loads_list(row.caveats_json),
    )


def _serialize_knowledge_node(session: Session, node: SourceKnowledgeNodeORM) -> SourceDiscoveryKnowledgeNodeSummary:
    return SourceDiscoveryKnowledgeNodeSummary(
        node_id=node.node_id,
        canonical_snapshot_id=node.canonical_snapshot_id,
        canonical_source_id=node.canonical_source_id,
        canonical_url=node.canonical_url,
        canonical_title=node.canonical_title,
        cluster_kind=node.cluster_kind,
        duplicate_posture=node.duplicate_posture,
        supporting_record_count=node.supporting_record_count,
        supporting_source_count=node.supporting_source_count,
        independent_source_count=node.independent_source_count,
        first_seen_at=node.first_seen_at,
        last_seen_at=node.last_seen_at,
        member_source_ids=_loads_list(node.member_source_ids_json),
        as_detailed_in_addition_to=_loads_list(node.as_detailed_in_addition_to_json),
        caveats=_loads_list(node.caveats_json),
    )


def _knowledge_node_members(session: Session, node_id: str) -> list[SourceDiscoveryKnowledgeNodeMember]:
    node = session.get(SourceKnowledgeNodeORM, node_id)
    if node is None:
        return []
    snapshots = list(
        session.scalars(
            select(SourceContentSnapshotORM)
            .where(SourceContentSnapshotORM.knowledge_node_id == node_id)
            .order_by(SourceContentSnapshotORM.fetched_at.desc(), SourceContentSnapshotORM.snapshot_id)
        )
    )
    members: list[SourceDiscoveryKnowledgeNodeMember] = []
    for snapshot in snapshots:
        memory = session.get(SourceMemoryORM, snapshot.source_id)
        members.append(
            SourceDiscoveryKnowledgeNodeMember(
                snapshot_id=snapshot.snapshot_id,
                source_id=snapshot.source_id,
                url=snapshot.url,
                title=snapshot.title,
                source_domain=(memory.domain_scope if memory is not None else _domain_from_url(snapshot.url)),
                duplicate_class=(snapshot.duplicate_class or "canonical"),  # type: ignore[arg-type]
                body_storage_mode=snapshot.body_storage_mode,  # type: ignore[arg-type]
                is_canonical=snapshot.snapshot_id == node.canonical_snapshot_id,
                published_at=snapshot.published_at,
                fetched_at=snapshot.fetched_at,
            )
        )
    return members


def _ensure_knowledge_nodes_for_source(session: Session, source_id: str) -> None:
    memory = session.get(SourceMemoryORM, source_id)
    if memory is None:
        return
    snapshots = list(
        session.scalars(
            select(SourceContentSnapshotORM)
            .where(SourceContentSnapshotORM.source_id == source_id)
            .order_by(SourceContentSnapshotORM.fetched_at.asc(), SourceContentSnapshotORM.snapshot_id.asc())
        )
    )
    for snapshot in snapshots:
        if snapshot.knowledge_node_id and session.get(SourceKnowledgeNodeORM, snapshot.knowledge_node_id) is not None:
            _refresh_knowledge_node_aggregates(session, snapshot.knowledge_node_id)
            continue
        _assign_snapshot_to_knowledge_node(
            session,
            snapshot,
            memory=memory,
            normalized_text=snapshot.full_text,
            now=snapshot.fetched_at or _utc_now(),
        )
    session.flush()


def _assign_snapshot_to_knowledge_node(
    session: Session,
    snapshot: SourceContentSnapshotORM,
    *,
    memory: SourceMemoryORM,
    normalized_text: str,
    now: str,
) -> None:
    text = _normalize_text(normalized_text)
    matched = _match_existing_knowledge_node(session, snapshot, memory=memory, normalized_text=text)
    if matched is None:
        node_id = f"knowledge-node:{_safe_id(snapshot.source_id)}:{snapshot.text_hash[:16]}"
        snapshot.knowledge_node_id = node_id
        snapshot.canonical_snapshot_id = snapshot.snapshot_id
        snapshot.duplicate_class = "canonical"
        snapshot.body_storage_mode = "metadata_only" if snapshot.extraction_method == "metadata_only" else "full_text"
        session.add(snapshot)
        node = session.get(SourceKnowledgeNodeORM, node_id)
        if node is None:
            node = SourceKnowledgeNodeORM(
                node_id=node_id,
                canonical_snapshot_id=snapshot.snapshot_id,
                canonical_source_id=snapshot.source_id,
                canonical_text_hash=snapshot.text_hash,
                canonical_url=snapshot.url,
                canonical_title=snapshot.title,
                cluster_kind="content_cluster",
                duplicate_posture="canonical_only",
                supporting_record_count=1,
                supporting_source_count=1,
                independent_source_count=1,
                first_seen_at=now,
                last_seen_at=now,
                member_source_ids_json=json.dumps([snapshot.source_id]),
                as_detailed_in_addition_to_json=json.dumps([]),
                caveats_json=json.dumps([
                    "Knowledge node grouping is heuristic and review-oriented; it is not event-truth adjudication.",
                ]),
            )
            session.add(node)
        session.flush()
        _refresh_knowledge_node_aggregates(session, node_id)
        return

    node, duplicate_class = matched
    snapshot.knowledge_node_id = node.node_id
    snapshot.canonical_snapshot_id = node.canonical_snapshot_id
    snapshot.duplicate_class = duplicate_class
    if duplicate_class in {"exact_duplicate", "wire_syndication", "near_duplicate"} and snapshot.snapshot_id != node.canonical_snapshot_id:
        snapshot.body_storage_mode = "compacted_duplicate"
        snapshot.full_text = _compact_duplicate_text(text)
        snapshot.text_length = len(snapshot.full_text)
        snapshot.caveats_json = json.dumps(
            sorted(
                set(_loads_list(snapshot.caveats_json) + [
                    "Duplicate body was compacted to preserve lineage while reducing repeated storage.",
                ])
            )
        )
    else:
        snapshot.body_storage_mode = "metadata_only" if snapshot.extraction_method == "metadata_only" else "full_text"
    session.add(snapshot)
    session.flush()
    _refresh_knowledge_node_aggregates(session, node.node_id)


def _match_existing_knowledge_node(
    session: Session,
    snapshot: SourceContentSnapshotORM,
    *,
    memory: SourceMemoryORM,
    normalized_text: str,
) -> tuple[SourceKnowledgeNodeORM, str] | None:
    exact = session.scalar(
        select(SourceKnowledgeNodeORM).where(SourceKnowledgeNodeORM.canonical_text_hash == snapshot.text_hash).limit(1)
    )
    if exact is not None:
        exact_class = "exact_duplicate" if exact.canonical_source_id != snapshot.source_id else "canonical"
        return exact, exact_class

    nodes = list(
        session.scalars(
            select(SourceKnowledgeNodeORM)
            .order_by(SourceKnowledgeNodeORM.last_seen_at.desc())
            .limit(80)
        )
    )
    best_match: tuple[SourceKnowledgeNodeORM, str, float] | None = None
    new_title = snapshot.title or memory.title
    new_domain = memory.domain_scope
    for node in nodes:
        canonical_snapshot = session.get(SourceContentSnapshotORM, node.canonical_snapshot_id)
        if canonical_snapshot is None:
            continue
        canonical_memory = session.get(SourceMemoryORM, canonical_snapshot.source_id)
        duplicate_class, score = _classify_duplicate_relationship(
            new_text=normalized_text,
            new_title=new_title,
            new_domain=new_domain,
            canonical_text=canonical_snapshot.full_text,
            canonical_title=canonical_snapshot.title or canonical_memory.title if canonical_memory is not None else canonical_snapshot.title,
            canonical_domain=(canonical_memory.domain_scope if canonical_memory is not None else _domain_from_url(canonical_snapshot.url)),
        )
        if duplicate_class is None:
            continue
        if best_match is None or score > best_match[2]:
            best_match = (node, duplicate_class, score)
    if best_match is None:
        return None
    return best_match[0], best_match[1]


def _classify_duplicate_relationship(
    *,
    new_text: str,
    new_title: str | None,
    new_domain: str,
    canonical_text: str,
    canonical_title: str | None,
    canonical_domain: str,
) -> tuple[str | None, float]:
    title_similarity = _title_similarity(new_title or "", canonical_title or "")
    text_similarity = _token_similarity(new_text, canonical_text)
    token_overlap = len(_normalized_token_set(new_text) & _normalized_token_set(canonical_text))
    if title_similarity >= 0.6 and _looks_like_correction_or_contradiction(new_title or "", new_text):
        return "correction_or_contradiction", max(title_similarity, text_similarity)
    if text_similarity >= 0.94:
        return ("wire_syndication" if new_domain != canonical_domain else "near_duplicate"), text_similarity
    if text_similarity >= 0.82 and title_similarity >= 0.55:
        return "near_duplicate", (text_similarity + title_similarity) / 2
    if title_similarity >= 0.84 and (text_similarity >= 0.45 or (text_similarity >= 0.24 and token_overlap >= 6)):
        return "independent_corroboration", (text_similarity + title_similarity) / 2
    if title_similarity >= 0.62 and _looks_like_follow_up(new_title or "", canonical_title or ""):
        return "follow_up", max(title_similarity, text_similarity)
    return None, 0.0


def _refresh_knowledge_node_aggregates(session: Session, node_id: str) -> None:
    node = session.get(SourceKnowledgeNodeORM, node_id)
    if node is None:
        return
    snapshots = list(
        session.scalars(
            select(SourceContentSnapshotORM)
            .where(SourceContentSnapshotORM.knowledge_node_id == node_id)
            .order_by(SourceContentSnapshotORM.fetched_at.asc(), SourceContentSnapshotORM.snapshot_id.asc())
        )
    )
    if not snapshots:
        return
    canonical_snapshot = session.get(SourceContentSnapshotORM, node.canonical_snapshot_id) or snapshots[0]
    node.canonical_snapshot_id = canonical_snapshot.snapshot_id
    node.canonical_source_id = canonical_snapshot.source_id
    node.canonical_text_hash = canonical_snapshot.text_hash
    node.canonical_url = canonical_snapshot.url
    node.canonical_title = canonical_snapshot.title
    for snapshot in snapshots:
        snapshot.canonical_snapshot_id = canonical_snapshot.snapshot_id
        if snapshot.snapshot_id == canonical_snapshot.snapshot_id:
            snapshot.duplicate_class = "canonical"
    node.first_seen_at = snapshots[0].fetched_at
    node.last_seen_at = snapshots[-1].fetched_at
    node.supporting_record_count = len(snapshots)

    source_ids: set[str] = set()
    domains: set[str] = set()
    additions: list[str] = []
    duplicate_classes: set[str] = set()
    for snapshot in snapshots:
        memory = session.get(SourceMemoryORM, snapshot.source_id)
        source_ids.add(snapshot.source_id)
        domains.add(memory.domain_scope if memory is not None else _domain_from_url(snapshot.url))
        duplicate_classes.add(snapshot.duplicate_class or "canonical")
        if snapshot.snapshot_id != canonical_snapshot.snapshot_id:
            label = f"{snapshot.title or snapshot.source_id} ({memory.domain_scope if memory is not None else _domain_from_url(snapshot.url)})"
            if label not in additions:
                additions.append(label)

    if len(snapshots) == 1:
        duplicate_posture = "canonical_only"
    elif duplicate_classes.issubset({"canonical", "exact_duplicate", "wire_syndication", "near_duplicate"}):
        duplicate_posture = "duplicate_heavy"
    elif "correction_or_contradiction" in duplicate_classes:
        duplicate_posture = "corrective_cluster"
    elif duplicate_classes.intersection({"follow_up", "independent_corroboration"}):
        duplicate_posture = "corroborated_cluster"
    else:
        duplicate_posture = "mixed"

    node.duplicate_posture = duplicate_posture
    node.supporting_source_count = len(source_ids)
    node.independent_source_count = len(domains)
    node.member_source_ids_json = json.dumps(sorted(source_ids))
    node.as_detailed_in_addition_to_json = json.dumps(additions[:12])
    node.caveats_json = json.dumps([
        "Knowledge node grouping is heuristic and intended to preserve provenance while reducing duplicate storage.",
    ])


def _compact_duplicate_text(text: str) -> str:
    normalized = _normalize_text(text)
    return normalized[:600]


def _token_similarity(left: str, right: str) -> float:
    left_tokens = _normalized_token_set(left)
    right_tokens = _normalized_token_set(right)
    if not left_tokens or not right_tokens:
        return 0.0
    intersection = len(left_tokens & right_tokens)
    union = len(left_tokens | right_tokens)
    return round(intersection / union, 4) if union else 0.0


def _title_similarity(left: str, right: str) -> float:
    return _token_similarity(left, right)


def _normalized_token_set(text: str) -> set[str]:
    stopwords = {
        "the", "and", "for", "with", "that", "this", "from", "into", "their", "have", "has",
        "been", "will", "were", "over", "after", "before", "about", "into", "while", "would",
        "could", "should", "said", "says", "also", "than", "then", "when", "where", "what",
        "news", "report", "reports", "article", "update", "public",
    }
    return {
        token
        for token in re.findall(r"[a-z0-9]{3,}", (text or "").casefold())
        if token not in stopwords
    }


def _looks_like_correction_or_contradiction(title: str, text: str) -> bool:
    lowered = f"{title} {text}".casefold()
    return any(token in lowered for token in ("correction", "corrected", "contradicted", "wrong", "update:", "clarification"))


def _looks_like_follow_up(title: str, canonical_title: str) -> bool:
    lowered = f"{title} {canonical_title}".casefold()
    return any(token in lowered for token in ("update", "follow-up", "follow up", "latest", "new details", "more details"))


def _merge_auth_requirement(existing: str, incoming: str) -> str:
    if "login_required" in {existing, incoming}:
        return "login_required"
    if "no_auth" in {existing, incoming}:
        return "no_auth"
    return "unknown"


def _merge_captcha_requirement(existing: str, incoming: str) -> str:
    if "captcha_required" in {existing, incoming}:
        return "captcha_required"
    if "no_captcha" in {existing, incoming}:
        return "no_captcha"
    return "unknown"


def _merge_intake_disposition(
    existing: str,
    incoming: str,
    *,
    auth_requirement: str,
    captcha_requirement: str,
) -> str:
    if auth_requirement == "login_required" or captcha_requirement == "captcha_required":
        return "blocked"
    if "blocked" in {existing, incoming}:
        return "blocked"
    if "public_no_auth" in {existing, incoming} and auth_requirement != "login_required" and captcha_requirement != "captcha_required":
        return "public_no_auth"
    return "hold_review"


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


def _generated_source_id_for_url(url: str) -> str:
    parsed = urlparse(url)
    identity = parsed.netloc + parsed.path
    if parsed.query:
        identity = f"{identity}?{parsed.query}"
    return f"source:{_safe_id(identity)[:120]}"


def _candidate_seed_from_extracted_url(
    *,
    url: str,
    source_id: str,
    title: str,
    wave_id: str | None,
    wave_title: str | None,
    discovery_reason: str,
    caveats: list[str],
    discovery_methods: list[str] | None = None,
    structure_hints: list[str] | None = None,
    platform_family: str | None = None,
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
        auth_requirement=classification["auth_requirement"],  # type: ignore[arg-type]
        captcha_requirement=classification["captcha_requirement"],  # type: ignore[arg-type]
        intake_disposition=classification["intake_disposition"],  # type: ignore[arg-type]
        wave_fit_score=0.56 if wave_id else 0.5,
        relevance_basis=[
            discovery_reason,
            "Extracted source remains candidate-only until health, policy, and evidence review run.",
        ],
        caveats=caveats + classification["caveats"],
        discovery_methods=list(discovery_methods or []),
        structure_hints=list(structure_hints or []),
        platform_family=platform_family,
    )


def _count_novel_candidate_seeds(session: Session, seeds: list[SourceDiscoveryCandidateSeed]) -> int:
    canonical_urls = {_canonical_source_url(seed.url) for seed in seeds if seed.url}
    if not canonical_urls:
        return 0
    existing_urls = {
        row[0]
        for row in session.execute(
            select(SourceMemoryORM.canonical_url).where(SourceMemoryORM.canonical_url.in_(canonical_urls))
        ).all()
        if row[0]
    }
    return sum(1 for canonical_url in canonical_urls if canonical_url not in existing_urls)


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


def _default_scope_hints_dict() -> dict[str, list[str]]:
    return {"spatial": [], "language": [], "topic": []}


def _loads_scope_hints(raw: str | None) -> SourceDiscoveryScopeHints:
    payload = _default_scope_hints_dict()
    value = _loads_dict(raw)
    if isinstance(value.get("spatial"), list):
        payload["spatial"] = [str(item) for item in value.get("spatial", []) if str(item).strip()]
    if isinstance(value.get("language"), list):
        payload["language"] = [str(item) for item in value.get("language", []) if str(item).strip()]
    if isinstance(value.get("topic"), list):
        payload["topic"] = [str(item) for item in value.get("topic", []) if str(item).strip()]
    return SourceDiscoveryScopeHints(**payload)


def _normalize_scope_hints(scope_hints: SourceDiscoveryScopeHints | dict[str, Any] | None) -> SourceDiscoveryScopeHints:
    if isinstance(scope_hints, SourceDiscoveryScopeHints):
        return SourceDiscoveryScopeHints(
            spatial=sorted(set(scope_hints.spatial)),
            language=sorted(set(scope_hints.language)),
            topic=sorted(set(scope_hints.topic)),
        )
    payload = _default_scope_hints_dict()
    if isinstance(scope_hints, dict):
        for key in ("spatial", "language", "topic"):
            value = scope_hints.get(key, [])
            if isinstance(value, list):
                payload[key] = sorted({str(item).strip() for item in value if str(item).strip()})
    return SourceDiscoveryScopeHints(**payload)


def _normalize_platform_family(
    platform_family: str | None,
    url: str,
    structure_hints: list[str] | None = None,
) -> str:
    if platform_family and platform_family != "unknown":
        return platform_family
    for hint in structure_hints or []:
        if hint.startswith("platform_"):
            return hint.removeprefix("platform_")
    return _detect_platform_family_from_url(url)


def _merge_scope_hints(
    existing: SourceDiscoveryScopeHints | None,
    incoming: SourceDiscoveryScopeHints | None,
) -> SourceDiscoveryScopeHints:
    left = existing or SourceDiscoveryScopeHints()
    right = incoming or SourceDiscoveryScopeHints()
    return SourceDiscoveryScopeHints(
        spatial=sorted(set(left.spatial + right.spatial)),
        language=sorted(set(left.language + right.language)),
        topic=sorted(set(left.topic + right.topic)),
    )


def _merge_discovery_role(current: str, incoming: str) -> str:
    if current == "root" or incoming == "root":
        return "root"
    if current == "candidate" or incoming == "candidate":
        return "candidate"
    return incoming or current or "candidate"


def _merge_seed_family(current: str, incoming: str) -> str:
    if current and current != "other":
        return current
    return incoming or current or "other"


def _merge_platform_family(current: str, incoming: str) -> str:
    if current and current != "unknown":
        return current
    return incoming or current or "unknown"


def _merge_optional_text(current: str | None, incoming: str | None) -> str | None:
    if current and current.strip():
        return current
    if incoming and incoming.strip():
        return incoming
    return current or incoming


def _normalized_source_family_tags(seed: SourceDiscoveryCandidateSeed) -> list[str]:
    tags = {tag.strip() for tag in seed.source_family_tags if tag.strip()}
    if seed.seed_family == "regional_outlet":
        tags.update({"regional", "local_news"})
    if seed.seed_family == "official_bulletin":
        tags.add("official")
    if seed.seed_family == "forum_root":
        tags.add("forum")
    if seed.seed_family == "wiki_root":
        tags.add("wiki")
    if seed.seed_family == "status_root":
        tags.add("status_page")
    if seed.seed_family in {"archive_root", "archive_index"}:
        tags.add("archive")
    if seed.platform_family in {"discourse", "stack_exchange"}:
        tags.add("forum")
    if seed.platform_family == "mediawiki":
        tags.add("wiki")
    if seed.platform_family == "mastodon":
        tags.update({"federated", "social_public"})
    if seed.platform_family == "statuspage":
        tags.update({"official", "status_page"})
    domain = (seed.parent_domain or _domain_from_url(seed.url)).casefold()
    if domain.endswith(".gov") or ".gov." in domain or domain.endswith(".mil") or domain.endswith(".edu"):
        tags.add("official")
    if "forum" in domain or "discourse" in domain:
        tags.add("forum")
    if "wiki" in domain:
        tags.add("wiki")
    if "status" in domain:
        tags.add("status_page")
    return sorted(tags)


def _derived_seed_family(seed: SourceDiscoveryCandidateSeed) -> str:
    if seed.seed_family:
        return seed.seed_family
    discovery_methods = set(seed.discovery_methods)
    structure_hints = set(seed.structure_hints)
    domain = (seed.parent_domain or _domain_from_url(seed.url)).casefold()
    if seed.platform_family in {"discourse", "stack_exchange"}:
        return "forum_root"
    if seed.platform_family == "mediawiki":
        return "wiki_root"
    if seed.platform_family == "statuspage":
        return "status_root"
    if "seed_url" in discovery_methods:
        return "wave_seed" if seed.wave_id else "user_seed"
    if seed.source_type == "rss":
        return "feed_root"
    if seed.source_type == "sitemap":
        return "sitemap_root"
    if seed.source_type == "dataset":
        return "catalog_root"
    if not discovery_methods:
        return "wave_seed" if seed.wave_id else "user_seed"
    if "record_source_extract" in discovery_methods:
        return "record_extract"
    if structure_hints.intersection({"archive_or_latest_navigation", "category_navigation", "tag_navigation"}):
        return "archive_root"
    if domain.endswith(".gov") or ".gov." in domain or domain.endswith(".mil"):
        return "official_bulletin"
    if "forum" in domain or "discourse" in domain:
        return "forum_root"
    if "wiki" in domain:
        return "wiki_root"
    if "status" in domain:
        return "status_root"
    return "other"


def _derived_discovery_role(seed: SourceDiscoveryCandidateSeed) -> str:
    if seed.discovery_role:
        return seed.discovery_role
    discovery_methods = set(seed.discovery_methods)
    structure_hints = set(seed.structure_hints)
    if not discovery_methods and seed.source_type in {"web", "unknown", "rss", "sitemap", "dataset"}:
        return "root"
    if seed.seed_family in {
        "user_seed",
        "wave_seed",
        "feed_root",
        "sitemap_root",
        "catalog_root",
        "archive_root",
        "regional_outlet",
        "official_bulletin",
        "forum_root",
        "wiki_root",
        "status_root",
        "archive_index",
    }:
        return "root"
    if seed.source_type in {"rss", "sitemap", "dataset"}:
        return "root"
    if discovery_methods.intersection({"seed_url", "structure_scan"}) and seed.source_type in {"web", "unknown"}:
        return "root"
    if structure_hints.intersection({"feed_autodiscovery", "robots_sitemap", "archive_or_latest_navigation", "category_navigation", "tag_navigation"}):
        return "root"
    if "record_source_extract" in discovery_methods:
        return "derived"
    if discovery_methods.intersection({"feed_link_scan", "sitemap_scan", "catalog_scan", "bounded_expansion", "record_source_extract"}):
        return "candidate"
    return "candidate"


def _normalize_candidate_seed(seed: SourceDiscoveryCandidateSeed) -> SourceDiscoveryCandidateSeed:
    normalized_scope_hints = _normalize_scope_hints(seed.scope_hints)
    provisional_seed = seed.model_copy(
        update={
            "scope_hints": normalized_scope_hints,
            "platform_family": _normalize_platform_family(seed.platform_family, seed.url, seed.structure_hints),
        }
    )
    seed_family = _derived_seed_family(provisional_seed)
    normalized_seed = provisional_seed.model_copy(
        update={
            "seed_family": seed_family,
            "source_family_tags": _normalized_source_family_tags(provisional_seed.model_copy(update={"seed_family": seed_family})),
        }
    )
    discovery_role = _derived_discovery_role(normalized_seed)
    return normalized_seed.model_copy(update={"discovery_role": discovery_role})


def _suggest_discovery_action(memory: SourceMemoryORM) -> SourceDiscoveryNextAction:
    if memory.discovery_role != "root":
        return "none"
    if memory.lifecycle_state in {"rejected", "archived"}:
        return "none"
    discovery_methods = set(_loads_list(memory.discovery_methods_json))
    if memory.source_type in {"web", "unknown"} and "structure_scan" not in discovery_methods:
        return "structure_scan"
    followup = _public_discovery_followup_kind(memory)
    if followup is not None:
        return followup  # type: ignore[return-value]
    return "none"


def _build_discovery_priority_context(session: Session) -> _DiscoveryPriorityContext:
    context = _DiscoveryPriorityContext()
    roots = list(
        session.scalars(
            select(SourceMemoryORM)
            .where(SourceMemoryORM.discovery_role == "root")
            .where(SourceMemoryORM.lifecycle_state.not_in(["rejected", "archived"]))
        )
    )
    for memory in roots:
        domain_key = memory.domain_scope or "unknown"
        context.root_domain_counts[domain_key] = context.root_domain_counts.get(domain_key, 0) + 1
        for tag in _loads_list(memory.source_family_tags_json):
            context.root_tag_counts[tag] = context.root_tag_counts.get(tag, 0) + 1
    fit_rows = list(session.scalars(select(SourceWaveFitORM)))
    grouped: dict[str, list[SourceWaveFitORM]] = {}
    for row in fit_rows:
        grouped.setdefault(row.source_id, []).append(row)
    context.best_fit_by_source_id = {
        source_id: _best_wave_fit(rows)
        for source_id, rows in grouped.items()
    }
    return context


def _compute_discovery_priority(
    session: Session,
    memory: SourceMemoryORM,
    *,
    now: str,
    context: _DiscoveryPriorityContext | None = None,
) -> tuple[int, SourceDiscoveryPriority, list[str]]:
    active_context = context or _build_discovery_priority_context(session)
    basis: list[str] = []
    score = 0
    if memory.discovery_role != "root":
        return 0, "low", ["memory is not a discovery root"]
    if memory.intake_disposition == "public_no_auth" and memory.captcha_requirement == "no_captcha":
        score += 3
        basis.append("public no-auth root")
    if _is_scheduler_structure_scan_candidate(memory):
        score += 4
        basis.append("public candidate root has not been structure-scanned yet")
    elif _is_scheduler_public_discovery_candidate(memory, now):
        score += 3
        basis.append(f"due for public {_suggest_discovery_action(memory).replace('_', ' ')} follow-up")
    if memory.source_type in {"rss", "sitemap", "dataset"}:
        score += 2
        basis.append("machine-readable discovery surface")
    structure_hints = set(_loads_list(memory.structure_hints_json))
    if structure_hints.intersection({"archive_or_latest_navigation", "category_navigation", "tag_navigation", "catalog_link"}):
        score += 2
        basis.append("structured archive or catalog navigation")
    scope_hints = _loads_scope_hints(memory.scope_hints_json)
    if scope_hints.spatial:
        score += 1
        basis.append("explicit spatial scope hints are present")
    if scope_hints.topic:
        score += 1
        basis.append("explicit topic scope hints are present")
    tags = set(_loads_list(memory.source_family_tags_json))
    if tags.intersection({"local_news", "regional", "official"}):
        score += 2
        basis.append("regional or primary-source long-tail root")
    if memory.platform_family == "statuspage":
        score += 1
        basis.append("official status or maintenance root")
    elif memory.platform_family == "mastodon":
        score += 1
        basis.append("federated/public-social discovery root")
    elif memory.platform_family == "stack_exchange":
        score += 1
        basis.append("technical Q&A long-tail root")
    elif tags.intersection({"forum", "wiki", "status_page", "federated"}):
        score += 1
        basis.append("platform-specific long-tail root")
    if memory.seed_packet_id and tags.intersection({"regional", "local_news"}):
        basis.append("curated regional/local packet root")
    domain_count = active_context.root_domain_counts.get(memory.domain_scope or "unknown", 0)
    if domain_count <= 1:
        score += 1
        basis.append("adds domain diversity across discovery roots")
    rare_tags = [tag for tag in tags if active_context.root_tag_counts.get(tag, 0) <= 1]
    if rare_tags:
        score += 1
        basis.append("adds source-family diversity")
    best_fit = active_context.best_fit_by_source_id.get(memory.source_id)
    if best_fit is not None and best_fit.fit_score >= 0.75:
        score += 2
        basis.append("high-fit root for an active wave")
    if memory.intake_disposition == "blocked":
        score -= 5
        basis.append("root is blocked by intake policy")
    elif memory.intake_disposition == "hold_review":
        score -= 1
        basis.append("root remains hold-review until clearer public intake evidence exists")
    if memory.auth_requirement == "login_required":
        score -= 4
        basis.append("root is blocked by auth requirement")
    if memory.captcha_requirement == "captcha_required":
        score -= 4
        basis.append("root is blocked by CAPTCHA requirement")
    if memory.discovery_scan_fail_count > 0:
        score -= min(3, memory.discovery_scan_fail_count)
        basis.append("recent discovery failures triggered backoff")
    if memory.discovery_low_yield_count > 0:
        score -= min(3, memory.discovery_low_yield_count)
        basis.append("root has repeated low-yield discovery outcomes")
    if score >= 7:
        return score, "high", basis
    if score >= 3:
        return score, "medium", basis
    return score, "low", basis or ["bounded review-only discovery root"]


def _discovery_eligibility_reasons(memory: SourceMemoryORM, now: str) -> list[str]:
    action = _suggest_discovery_action(memory)
    reasons: list[str] = []
    if action == "structure_scan" and _is_scheduler_structure_scan_candidate(memory):
        reasons.append("eligible for bounded structure scan")
    elif action != "none" and _is_scheduler_public_discovery_candidate(memory, now):
        reasons.append(f"eligible for due public {action.replace('_', ' ')} follow-up")
    return reasons


def _discovery_blocked_reasons(memory: SourceMemoryORM, now: str) -> list[str]:
    action = _suggest_discovery_action(memory)
    reasons: list[str] = []
    if memory.discovery_role != "root":
        reasons.append("memory is not a discovery root")
        return reasons
    if memory.lifecycle_state in {"rejected", "archived"}:
        reasons.append(f"lifecycle state is {memory.lifecycle_state}")
    if memory.intake_disposition == "blocked":
        reasons.append("root is blocked by intake disposition")
    elif memory.intake_disposition == "hold_review":
        reasons.append("root remains hold-review")
    if memory.auth_requirement == "login_required":
        reasons.append("root is blocked by auth requirement")
    if memory.captcha_requirement == "captcha_required":
        reasons.append("root is blocked by CAPTCHA requirement")
    if action == "structure_scan" and "structure_scan" in _loads_list(memory.discovery_methods_json):
        reasons.append("structure scan already ran on this root")
    if action != "none" and action != "structure_scan" and not _is_due_for_public_discovery(memory.next_discovery_scan_at, now):
        reasons.append("public follow-up is not due yet")
    if action == "none" and not reasons:
        reasons.append("no supported public discovery action is currently available")
    return reasons


def _review_reasons(
    memory: SourceMemoryORM,
    *,
    best_fit: SourceWaveFitORM | None,
    has_snapshot: bool,
    pending_claim_count: int,
    corrective_cluster: bool,
    unscanned_public_root: bool,
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
    if memory.intake_disposition != "public_no_auth":
        reasons.append(f"intake disposition is {memory.intake_disposition}")
    if memory.auth_requirement != "no_auth":
        reasons.append(f"auth requirement is {memory.auth_requirement}")
    if memory.captcha_requirement == "captcha_required":
        reasons.append("captcha requirement is captcha_required")
    if best_fit is not None and best_fit.fit_score >= 0.75:
        reasons.append("high-fit source for an active wave")
    if unscanned_public_root:
        reasons.append("public candidate root has not been structure-scanned yet")
    if corrective_cluster:
        reasons.append("corrective knowledge-node cluster is present")
    if pending_claim_count > 0 and memory.policy_state == "reviewed":
        reasons.append("reviewed source has pending review claims")
    if memory.discovery_role == "root":
        tags = set(_loads_list(memory.source_family_tags_json))
        if tags.intersection({"regional", "local_news"}):
            reasons.append("regional or local long-tail root")
        if memory.platform_family == "statuspage":
            reasons.append("official status or outage context root")
        elif memory.platform_family == "mastodon":
            reasons.append("federated/public-social discovery root")
        elif memory.platform_family == "stack_exchange":
            reasons.append("technical Q&A long-tail root")
        elif tags.intersection({"forum", "wiki", "status_page", "federated"}):
            reasons.append("platform-specific long-tail root")
        if memory.seed_packet_id and tags.intersection({"regional", "local_news"}):
            reasons.append("curated regional/local packet root")
        if _is_scheduler_public_discovery_candidate(memory, _utc_now()):
            reasons.append(f"due for public {_suggest_discovery_action(memory).replace('_', '/')} follow-up")
        if memory.auth_requirement == "login_required" or memory.captcha_requirement == "captcha_required":
            reasons.append("root is blocked by auth or CAPTCHA")
        if memory.discovery_low_yield_count > 0:
            reasons.append("root has repeated low-yield discovery outcomes")
        if best_fit is not None and best_fit.fit_score >= 0.75 and memory.discovery_role == "root":
            reasons.append("root contributes domain or locality diversity for an active wave")
    return reasons


def _review_priority(
    memory: SourceMemoryORM,
    *,
    best_fit: SourceWaveFitORM | None,
    has_snapshot: bool,
    pending_claim_count: int,
    corrective_cluster: bool,
    unscanned_public_root: bool,
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
    if memory.intake_disposition == "blocked":
        score += 4
    elif memory.intake_disposition != "public_no_auth":
        score += 2
    if memory.auth_requirement == "login_required":
        score += 3
    elif memory.auth_requirement == "unknown":
        score += 1
    if memory.captcha_requirement == "captcha_required":
        score += 3
    if best_fit is not None and best_fit.fit_score >= 0.75:
        score += 2
    if unscanned_public_root:
        score += 2
    if corrective_cluster:
        score += 2
    if pending_claim_count > 0 and memory.policy_state == "reviewed":
        score += 3
    if memory.discovery_role == "root":
        tags = set(_loads_list(memory.source_family_tags_json))
        if tags.intersection({"regional", "local_news"}):
            score += 1
        if tags.intersection({"forum", "wiki", "status_page", "federated"}):
            score += 1
        if _is_scheduler_public_discovery_candidate(memory, _utc_now()):
            score += 1
        if memory.auth_requirement == "login_required" or memory.captcha_requirement == "captcha_required":
            score += 2
        if memory.discovery_low_yield_count > 0:
            score += 1
    if score >= 7:
        return score, "high"
    if score >= 3:
        return score, "medium"
    return score, "low"


def _recommended_review_actions(memory: SourceMemoryORM, *, owner_lane: str | None) -> list[str]:
    actions: list[str] = []
    if memory.policy_state == "manual_review":
        actions.append("mark_reviewed")
    if memory.lifecycle_state in {"discovered", "candidate"} and memory.intake_disposition != "blocked":
        actions.extend(["approve_candidate", "sandbox_check"])
    if not owner_lane:
        actions.append("assign_owner")
    if memory.source_health in {"degraded", "rate_limited", "unreachable", "blocked"}:
        actions.append("sandbox_check")
    if memory.intake_disposition == "blocked":
        actions.append("reject")
    actions.extend(["reject", "archive"])
    seen: set[str] = set()
    ordered: list[str] = []
    for action in actions:
        if action in seen:
            continue
        seen.add(action)
        ordered.append(action)
    return ordered


def _is_unscanned_public_candidate_root(memory: SourceMemoryORM) -> bool:
    discovery_methods = set(_loads_list(memory.discovery_methods_json))
    return (
        memory.discovery_role == "root"
        and
        memory.lifecycle_state in {"discovered", "candidate"}
        and memory.source_type in {"web", "unknown"}
        and memory.intake_disposition == "public_no_auth"
        and "structure_scan" not in discovery_methods
    )


def _is_scheduler_structure_scan_candidate(memory: SourceMemoryORM) -> bool:
    discovery_methods = set(_loads_list(memory.discovery_methods_json))
    return (
        memory.discovery_role == "root"
        and
        memory.lifecycle_state in {"discovered", "candidate"}
        and memory.source_type in {"web", "unknown"}
        and memory.intake_disposition != "blocked"
        and memory.auth_requirement != "login_required"
        and memory.captcha_requirement != "captcha_required"
        and "structure_scan" not in discovery_methods
    )


def _is_scheduler_expansion_candidate(memory: SourceMemoryORM) -> bool:
    structure_hints = set(_loads_list(memory.structure_hints_json))
    return (
        memory.discovery_role == "root"
        and
        (memory.policy_state == "reviewed" or memory.lifecycle_state == "sandboxed")
        and memory.lifecycle_state not in {"rejected", "archived"}
        and memory.intake_disposition == "public_no_auth"
        and bool(structure_hints.intersection({"archive_or_latest_navigation", "catalog_link", "category_navigation", "tag_navigation"}))
    )


def _public_discovery_followup_kind(memory: SourceMemoryORM) -> str | None:
    if memory.discovery_role != "root":
        return None
    if memory.lifecycle_state in {"rejected", "archived"}:
        return None
    if memory.intake_disposition != "public_no_auth":
        return None
    if memory.auth_requirement != "no_auth" or memory.captcha_requirement != "no_captcha":
        return None
    if memory.source_type == "rss":
        return "feed_link_scan"
    if memory.source_type == "sitemap":
        return "sitemap_scan"
    structure_hints = set(_loads_list(memory.structure_hints_json))
    catalog_like_hints = {
        "catalog_link",
        "feed_autodiscovery",
        "robots_sitemap",
        "status_history_navigation",
        "mastodon_instance_api",
        "mastodon_tag_navigation",
        "mastodon_account_navigation",
    }
    if memory.source_type == "dataset" and (
        memory.machine_readable_result in {"yes", "partial"}
        or bool(structure_hints.intersection(catalog_like_hints))
    ):
        return "catalog_scan"
    if memory.source_type in {"web", "unknown"} and bool(
        structure_hints.intersection({"catalog_link", "status_history_navigation", "mastodon_instance_api", "mastodon_tag_navigation", "mastodon_account_navigation"})
    ):
        return "catalog_scan"
    return None


def _is_due_for_public_discovery(next_discovery_scan_at: str | None, now: str) -> bool:
    if not next_discovery_scan_at:
        return True
    due_at = _parse_utc_like(next_discovery_scan_at)
    now_dt = _parse_utc_like(now)
    if due_at is None or now_dt is None:
        return True
    return due_at <= now_dt


def _is_scheduler_public_discovery_candidate(memory: SourceMemoryORM, now: str) -> bool:
    return _public_discovery_followup_kind(memory) is not None and _is_due_for_public_discovery(
        memory.next_discovery_scan_at,
        now,
    )


def _initial_next_discovery_scan_at(source_type: str, structure_hints: list[str], now: str) -> str | None:
    if source_type in {"rss", "sitemap", "dataset"}:
        return now
    if set(structure_hints).intersection(
        {
            "feed_autodiscovery",
            "robots_sitemap",
            "catalog_link",
            "status_history_navigation",
            "mastodon_instance_api",
            "mastodon_tag_navigation",
            "mastodon_account_navigation",
        }
    ):
        return now
    return None


def _next_public_discovery_scan_at(scan_kind: str, now: str) -> str:
    now_dt = _parse_utc_like(now) or datetime.now(tz=timezone.utc)
    hours = PUBLIC_DISCOVERY_CADENCE_HOURS.get(scan_kind, 24)
    return (now_dt + timedelta(hours=hours)).isoformat().replace("+00:00", "Z")


def _public_discovery_backoff_at(fail_count: int, now: str) -> str:
    now_dt = _parse_utc_like(now) or datetime.now(tz=timezone.utc)
    hours = min(24, 2 ** max(0, min(fail_count, 4)))
    return (now_dt + timedelta(hours=hours)).isoformat().replace("+00:00", "Z")


def _find_memory_by_canonical_url(session: Session, url: str) -> SourceMemoryORM | None:
    canonical_url = _canonical_source_url(url)
    return session.scalar(select(SourceMemoryORM).where(SourceMemoryORM.canonical_url == canonical_url).limit(1))


def _apply_public_discovery_scan_success_for_url(
    session: Session,
    url: str,
    *,
    now: str,
    scan_kind: str,
    outcome_summary: str | None = None,
    novel_candidate_count: int | None = None,
) -> None:
    memory = _find_memory_by_canonical_url(session, url)
    if memory is None:
        return
    existing_methods = set(_loads_list(memory.discovery_methods_json))
    existing_methods.add(scan_kind)
    memory.discovery_methods_json = json.dumps(sorted(existing_methods))
    memory.last_discovery_scan_at = now
    memory.next_discovery_scan_at = _next_public_discovery_scan_at(scan_kind, now)
    memory.discovery_scan_fail_count = 0
    if novel_candidate_count is not None:
        memory.discovery_low_yield_count = 0 if novel_candidate_count > 0 else max(0, memory.discovery_low_yield_count) + 1
    if outcome_summary:
        memory.last_discovery_outcome = outcome_summary


def _apply_public_discovery_scan_failure_for_url(
    session: Session,
    url: str,
    *,
    now: str,
    scan_kind: str,
    outcome_summary: str | None = None,
) -> None:
    memory = _find_memory_by_canonical_url(session, url)
    if memory is None:
        return
    existing_methods = set(_loads_list(memory.discovery_methods_json))
    existing_methods.add(scan_kind)
    memory.discovery_methods_json = json.dumps(sorted(existing_methods))
    memory.last_discovery_scan_at = now
    memory.discovery_scan_fail_count = max(0, memory.discovery_scan_fail_count) + 1
    memory.next_discovery_scan_at = _public_discovery_backoff_at(memory.discovery_scan_fail_count, now)
    if outcome_summary:
        memory.last_discovery_outcome = outcome_summary


def _apply_structure_scan_outcome(
    memory: SourceMemoryORM,
    *,
    now: str,
    outcome_summary: str,
    discovered_candidate_count: int,
) -> None:
    existing_methods = set(_loads_list(memory.discovery_methods_json))
    existing_methods.add("structure_scan")
    memory.discovery_methods_json = json.dumps(sorted(existing_methods))
    memory.last_discovery_scan_at = now
    memory.discovery_scan_fail_count = 0
    memory.discovery_low_yield_count = 0 if discovered_candidate_count > 0 else max(0, memory.discovery_low_yield_count) + 1
    memory.last_discovery_outcome = outcome_summary


def _pending_review_claim_candidates_for_source(
    session: Session,
    source_id: str,
    *,
    limit: int | None = None,
) -> list[SourceReviewClaimCandidateORM]:
    stmt = (
        select(SourceReviewClaimCandidateORM)
        .where(
            SourceReviewClaimCandidateORM.source_id == source_id,
            SourceReviewClaimCandidateORM.status == "pending",
        )
        .order_by(SourceReviewClaimCandidateORM.created_at.desc(), SourceReviewClaimCandidateORM.claim_candidate_id.desc())
    )
    if limit is not None:
        stmt = stmt.limit(max(0, limit))
    return list(session.scalars(stmt))


def _pending_review_claim_candidates_for_node(
    session: Session,
    node_id: str,
    *,
    limit: int | None = None,
) -> list[SourceReviewClaimCandidateORM]:
    stmt = (
        select(SourceReviewClaimCandidateORM)
        .where(
            SourceReviewClaimCandidateORM.knowledge_node_id == node_id,
            SourceReviewClaimCandidateORM.status == "pending",
        )
        .order_by(SourceReviewClaimCandidateORM.created_at.desc(), SourceReviewClaimCandidateORM.claim_candidate_id.desc())
    )
    if limit is not None:
        stmt = stmt.limit(max(0, limit))
    return list(session.scalars(stmt))


def _source_has_corrective_cluster(session: Session, source_id: str) -> bool:
    _ensure_knowledge_nodes_for_source(session, source_id)
    return session.scalar(
        select(SourceKnowledgeNodeORM.node_id)
        .where(
            SourceKnowledgeNodeORM.duplicate_posture == "corrective_cluster",
            SourceKnowledgeNodeORM.node_id.in_(
                select(SourceContentSnapshotORM.knowledge_node_id).where(
                    SourceContentSnapshotORM.source_id == source_id,
                    SourceContentSnapshotORM.knowledge_node_id.is_not(None),
                )
            ),
        )
        .limit(1)
    ) is not None


def _select_knowledge_backfill_snapshots(
    session: Session,
    request: SourceDiscoveryKnowledgeBackfillRequest,
) -> list[SourceContentSnapshotORM]:
    stmt = select(SourceContentSnapshotORM)
    if request.snapshot_ids:
        stmt = stmt.where(SourceContentSnapshotORM.snapshot_id.in_(request.snapshot_ids))
    elif request.source_ids:
        stmt = stmt.where(SourceContentSnapshotORM.source_id.in_(request.source_ids))
    else:
        stmt = stmt.where(SourceContentSnapshotORM.knowledge_node_id.is_(None))
    if request.mode == "missing_only" and not request.snapshot_ids:
        stmt = stmt.where(SourceContentSnapshotORM.knowledge_node_id.is_(None))
    stmt = stmt.order_by(SourceContentSnapshotORM.fetched_at.desc(), SourceContentSnapshotORM.snapshot_id.desc())
    return list(session.scalars(stmt.limit(max(0, request.max_snapshots))))


def _refresh_or_delete_knowledge_node(session: Session, node_id: str) -> None:
    node = session.get(SourceKnowledgeNodeORM, node_id)
    if node is None:
        return
    has_members = session.scalar(
        select(SourceContentSnapshotORM.snapshot_id)
        .where(SourceContentSnapshotORM.knowledge_node_id == node_id)
        .limit(1)
    )
    if has_members is None:
        session.delete(node)
        return
    _refresh_knowledge_node_aggregates(session, node_id)


def _is_scheduler_llm_snapshot_eligible(session: Session, snapshot: SourceContentSnapshotORM) -> bool:
    if not snapshot.knowledge_node_id:
        return True
    if snapshot.snapshot_id == snapshot.canonical_snapshot_id:
        return True
    return snapshot.duplicate_class in {"independent_corroboration", "correction_or_contradiction", "follow_up"}


def _load_review_claim_import_context(
    settings: Settings,
    *,
    review_id: str,
    requested_source_id: str | None,
) -> dict[str, object]:
    with wave_session_scope(settings.wave_monitor_database_url) as wave_session:
        review = wave_session.get(WaveLlmReviewORM, review_id)
        if review is None:
            raise ValueError(f"Unknown review_id: {review_id}")
        task = wave_session.get(WaveLlmTaskORM, review.task_id)
        if task is None:
            raise ValueError(f"Unknown task_id for review: {review.task_id}")
        parsed_claims = _load_wave_review_claims(review.parsed_claims_json)
        accepted_claims = [
            (index, claim)
            for index, claim in enumerate(parsed_claims)
            if str(claim.get("status", "")) == "accepted_for_review"
        ]
        source_ids = _loads_list(task.source_ids_json)
        if requested_source_id:
            if source_ids and requested_source_id not in source_ids:
                raise ValueError("Requested source_id is not attached to the referenced review task.")
            source_id = requested_source_id
        elif len(source_ids) == 1:
            source_id = source_ids[0]
        else:
            raise ValueError("Review claim import requires source_id when the task references zero or multiple sources.")
        return {
            "review_id": review_id,
            "task_id": task.task_id,
            "wave_id": task.monitor_id,
            "source_id": source_id,
            "accepted_claims": accepted_claims,
            "snapshot_id": _snapshot_id_from_task(task),
        }


def _snapshot_id_from_task(task: WaveLlmTaskORM) -> str | None:
    for caveat in _loads_list(task.caveats_json):
        if caveat.startswith("source-snapshot:source-snapshot:"):
            return caveat[len("source-snapshot:"):]
        if caveat.startswith("source-snapshot:"):
            return caveat
    return None


def _upsert_review_claim_candidates(
    session: Session,
    *,
    context: dict[str, object],
    now: str,
    imported_by: str,
    caveats: list[str],
) -> list[SourceReviewClaimCandidateORM]:
    source_id = str(context["source_id"])
    snapshot_id = str(context["snapshot_id"]) if context.get("snapshot_id") else None
    snapshot = session.get(SourceContentSnapshotORM, snapshot_id) if snapshot_id else None
    knowledge_node_id = snapshot.knowledge_node_id if snapshot is not None else None
    rows: list[SourceReviewClaimCandidateORM] = []
    for claim_index, claim in context["accepted_claims"]:  # type: ignore[index]
        existing = session.scalar(
            select(SourceReviewClaimCandidateORM).where(
                SourceReviewClaimCandidateORM.review_id == str(context["review_id"]),
                SourceReviewClaimCandidateORM.source_id == source_id,
                SourceReviewClaimCandidateORM.claim_index == int(claim_index),
            )
        )
        if existing is None:
            existing = SourceReviewClaimCandidateORM(
                review_id=str(context["review_id"]),
                task_id=str(context["task_id"]),
                source_id=source_id,
                wave_id=str(context["wave_id"]) if context.get("wave_id") else None,
                snapshot_id=snapshot_id,
                knowledge_node_id=knowledge_node_id,
                claim_index=int(claim_index),
                claim_text=str(claim.get("claim_text", ""))[:2000],
                claim_type=str(claim.get("claim_type", "state"))[:64],
                evidence_basis=str(claim.get("evidence_basis", "contextual"))[:64],
                status="pending",
                confidence_score=0.5,
                created_at=now,
                applied_at=None,
                confidence_basis_json=json.dumps([
                    "Imported review claim starts at neutral confidence until corroborating text, media, or operator review adds more evidence.",
                ]),
                caveats_json=json.dumps(caveats + [
                    f"Imported from Wave LLM review by {imported_by}.",
                ]),
            )
            session.add(existing)
        else:
            existing.task_id = str(context["task_id"])
            existing.wave_id = str(context["wave_id"]) if context.get("wave_id") else existing.wave_id
            existing.snapshot_id = snapshot_id or existing.snapshot_id
            existing.knowledge_node_id = knowledge_node_id or existing.knowledge_node_id
            existing.claim_text = str(claim.get("claim_text", existing.claim_text))[:2000]
            existing.claim_type = str(claim.get("claim_type", existing.claim_type))[:64]
            existing.evidence_basis = str(claim.get("evidence_basis", existing.evidence_basis))[:64]
            if existing.confidence_score is None:
                existing.confidence_score = 0.5
            existing.caveats_json = json.dumps(
                sorted(set(_loads_list(existing.caveats_json) + caveats + [
                    f"Imported from Wave LLM review by {imported_by}.",
                ]))
            )
        rows.append(existing)
    session.flush()
    return sorted(rows, key=lambda row: row.claim_index)


def _claim_candidate_supporting_sources(
    session: Session,
    candidate: SourceReviewClaimCandidateORM,
    *,
    source_id: str,
) -> tuple[list[str], list[str]]:
    corroborating: set[str] = set()
    contradictions: set[str] = set()
    if candidate.knowledge_node_id:
        snapshots = list(
            session.scalars(
                select(SourceContentSnapshotORM)
                .where(SourceContentSnapshotORM.knowledge_node_id == candidate.knowledge_node_id)
            )
        )
        corroborating.update(
            snapshot.source_id
            for snapshot in snapshots
            if snapshot.source_id != source_id
            and snapshot.duplicate_class in {
                "canonical",
                "exact_duplicate",
                "wire_syndication",
                "near_duplicate",
                "follow_up",
                "independent_corroboration",
            }
        )
        contradictions.update(
            snapshot.source_id
            for snapshot in snapshots
            if snapshot.source_id != source_id and snapshot.duplicate_class == "correction_or_contradiction"
        )

    primary_snapshot = session.get(SourceContentSnapshotORM, candidate.snapshot_id) if candidate.snapshot_id else None
    primary_memory = session.get(SourceMemoryORM, source_id)
    if primary_snapshot is None or primary_memory is None:
        return sorted(corroborating), sorted(contradictions)

    comparison_snapshots = list(
        session.scalars(
            select(SourceContentSnapshotORM)
            .where(SourceContentSnapshotORM.source_id != source_id)
            .order_by(SourceContentSnapshotORM.fetched_at.desc(), SourceContentSnapshotORM.snapshot_id.desc())
            .limit(120)
        )
    )
    for snapshot in comparison_snapshots:
        other_memory = session.get(SourceMemoryORM, snapshot.source_id)
        if other_memory is None:
            continue
        duplicate_class, score = _classify_duplicate_relationship(
            new_text=snapshot.full_text,
            new_title=snapshot.title or other_memory.title,
            new_domain=other_memory.domain_scope,
            canonical_text=primary_snapshot.full_text,
            canonical_title=primary_snapshot.title or primary_memory.title,
            canonical_domain=primary_memory.domain_scope,
        )
        if duplicate_class in {
            "canonical",
            "exact_duplicate",
            "wire_syndication",
            "near_duplicate",
            "follow_up",
            "independent_corroboration",
        } and score >= 0.45:
            corroborating.add(snapshot.source_id)
        elif duplicate_class == "correction_or_contradiction":
            contradictions.add(snapshot.source_id)
    return sorted(corroborating), sorted(contradictions)


def _classify_seed_url(url: str) -> dict[str, object]:
    lowered = url.lower()
    parsed_url = urlparse(url)
    host = parsed_url.netloc.casefold()
    path = urlparse(url).path.casefold()
    caveats = [
        "Classification is URL-shape based in this first slice; later jobs should fetch metadata within budget.",
    ]
    login_markers = ("login", "signin", "sign-in", "account", "auth", "oauth", "session")
    captcha_markers = ("captcha", "recaptcha", "hcaptcha", "cf-chl")
    if any(token in lowered for token in login_markers):
        return {
            "source_type": "web",
            "source_class": "article",
            "access_result": "blocked",
            "machine_readable_result": "unknown",
            "auth_requirement": "login_required",
            "captcha_requirement": "unknown",
            "intake_disposition": "blocked",
            "policy_state": "manual_review",
            "caveats": caveats + ["URL shape suggests login-gated access; keep outside default public no-auth intake."],
        }
    if any(token in lowered for token in captcha_markers):
        return {
            "source_type": "web",
            "source_class": "article",
            "access_result": "blocked",
            "machine_readable_result": "unknown",
            "auth_requirement": "unknown",
            "captcha_requirement": "captcha_required",
            "intake_disposition": "blocked",
            "policy_state": "manual_review",
            "caveats": caveats + ["URL shape suggests CAPTCHA or anti-bot gating; keep outside default public no-auth intake."],
        }
    if "sitemap" in lowered:
        return {
            "source_type": "sitemap",
            "source_class": "static",
            "access_result": "unknown",
            "machine_readable_result": "partial",
            "auth_requirement": "no_auth",
            "captcha_requirement": "no_captcha",
            "intake_disposition": "public_no_auth",
            "policy_state": "manual_review",
            "caveats": caveats + ["Possible sitemap or index candidate; treat as structure-discovery surface, not a truth source."],
        }
    if any(token in lowered for token in ("/rss", ".rss", "feed", ".xml", ".atom")):
        return {
            "source_type": "rss",
            "source_class": "live",
            "access_result": "unknown",
            "machine_readable_result": "partial",
            "auth_requirement": "no_auth",
            "captcha_requirement": "no_captcha",
            "intake_disposition": "public_no_auth",
            "policy_state": "manual_review",
            "caveats": caveats + ["Possible feed candidate; parser validation still required."],
        }
    if path == "/api/v2/instance" or path.startswith("/api/v1/tags/"):
        return {
            "source_type": "dataset",
            "source_class": "dataset",
            "access_result": "unknown",
            "machine_readable_result": "partial",
            "auth_requirement": "no_auth",
            "captcha_requirement": "no_captcha",
            "intake_disposition": "public_no_auth",
            "policy_state": "manual_review",
            "caveats": caveats + [
                "Possible bounded public platform API root; treat as machine-readable discovery surface, not source truth.",
            ],
        }
    if _is_stack_exchange_api_url(url):
        return {
            "source_type": "dataset",
            "source_class": "dataset",
            "access_result": "unknown",
            "machine_readable_result": "partial",
            "auth_requirement": "no_auth",
            "captcha_requirement": "no_captcha",
            "intake_disposition": "public_no_auth",
            "policy_state": "manual_review",
            "caveats": caveats + [
                "Possible bounded Stack Exchange API root; treat as machine-readable discovery surface, not source truth.",
            ],
        }
    if any(token in lowered for token in (".json", ".geojson", ".csv", ".kml", ".netcdf", ".nc")):
        return {
            "source_type": "dataset",
            "source_class": "dataset",
            "access_result": "unknown",
            "machine_readable_result": "partial",
            "auth_requirement": "no_auth",
            "captcha_requirement": "no_captcha",
            "intake_disposition": "public_no_auth",
            "policy_state": "manual_review",
            "caveats": caveats + ["Possible machine-readable dataset candidate; schema validation still required."],
        }
    if any(token in lowered for token in ("twitter.com", "x.com", "instagram.com", "facebook.com", "tiktok.com")):
        return {
            "source_type": "social",
            "source_class": "social_image",
            "access_result": "unknown",
            "machine_readable_result": "unknown",
            "auth_requirement": "unknown",
            "captcha_requirement": "unknown",
            "intake_disposition": "hold_review",
            "policy_state": "manual_review",
            "caveats": caveats + [
                "Public social source must not be accessed through login-only, app-only, CAPTCHA, or ToS-hostile routes.",
                "Social/image evidence remains candidate evidence until corroborated.",
            ],
        }
    if host.endswith(".stackexchange.com") or host in {
        "stackoverflow.com",
        "serverfault.com",
        "superuser.com",
        "askubuntu.com",
        "mathoverflow.net",
    }:
        return {
            "source_type": "web",
            "source_class": "community",
            "access_result": "unknown",
            "machine_readable_result": "unknown",
            "auth_requirement": "unknown",
            "captcha_requirement": "unknown",
            "intake_disposition": "hold_review",
            "policy_state": "manual_review",
            "caveats": caveats + [
                "Technical Q&A platform root remains candidate-only until structure scan confirms bounded public discovery surfaces.",
            ],
        }
    return {
        "source_type": "web",
        "source_class": "article",
        "access_result": "unknown",
        "machine_readable_result": "unknown",
        "auth_requirement": "unknown",
        "captcha_requirement": "unknown",
        "intake_disposition": "hold_review",
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


def _robots_url_for_target(target_url: str) -> str:
    parsed = urlparse(target_url)
    return urlunparse((parsed.scheme, parsed.netloc, "/robots.txt", "", "", ""))


def _detect_platform_family_from_url(url: str) -> str:
    parsed = urlparse(url or "")
    lowered = (url or "").casefold()
    host = parsed.netloc.casefold()
    path = parsed.path.casefold()
    if _is_stack_exchange_api_url(url) or host.endswith(".stackexchange.com") or host in {
        "stackoverflow.com",
        "serverfault.com",
        "superuser.com",
        "askubuntu.com",
        "mathoverflow.net",
    }:
        return "stack_exchange"
    if "statuspage.io" in lowered:
        return "statuspage"
    if path == "/api/v2/instance" or path.startswith("/api/v1/tags/"):
        return "mastodon"
    if "/@" in lowered or "/web/@" in lowered or "mastodon" in lowered:
        return "mastodon"
    return "unknown"


def _detect_platform_family(target_url: str, html_text: str) -> str:
    lowered_url = (target_url or "").casefold()
    lowered_html = (html_text or "").casefold()
    if (
        "content=\"discourse" in lowered_html
        or "content='discourse" in lowered_html
        or "data-discourse" in lowered_html
        or "discourse_theme_id" in lowered_html
    ):
        return "discourse"
    if (
        "content=\"mediawiki" in lowered_html
        or "content='mediawiki" in lowered_html
        or "/w/load.php" in lowered_html
        or "mw-page-" in lowered_html
    ):
        return "mediawiki"
    if (
        "stack exchange network" in lowered_html
        or "stackexchange" in lowered_html and ("/questions/tagged/" in lowered_html or "/tags/" in lowered_html)
        or "stackoverflow" in lowered_url
        or "serverfault" in lowered_url
        or "superuser" in lowered_url
        or "askubuntu" in lowered_url
        or "mathoverflow" in lowered_url
    ):
        return "stack_exchange"
    if (
        "content=\"mastodon" in lowered_html
        or "content='mastodon" in lowered_html
        or "mastodon" in lowered_html and "/@" in lowered_html
        or "application/activity+json" in lowered_html and ("/@" in lowered_html or "/users/" in lowered_html)
    ):
        return "mastodon"
    detected_from_url = _detect_platform_family_from_url(lowered_url)
    if detected_from_url != "unknown":
        return detected_from_url
    if (
        "statuspage" in lowered_html
        or "status embed" in lowered_html
        or "component-container" in lowered_html
        or "incident-history" in lowered_html
    ):
        return "statuspage"
    return "unknown"


def _structure_scan_root_source_class(platform_family: str) -> str:
    if platform_family in {"discourse", "mediawiki", "mastodon", "stack_exchange"}:
        return "community"
    if platform_family == "statuspage":
        return "official"
    return "article"


def _extract_discourse_feed_urls(base_url: str, html_text: str) -> list[str]:
    parsed = urlparse(base_url)
    origin = f"{parsed.scheme}://{parsed.netloc}"
    urls = [urljoin(origin, "/latest.rss"), urljoin(origin, "/top.rss")]
    link_targets = re.findall(r"""href=["']([^"']+)["']""", html_text or "", flags=re.IGNORECASE)
    for target in link_targets:
        absolute = urljoin(origin, target.strip())
        absolute = absolute.split("#", 1)[0]
        target_path = urlparse(absolute).path
        if re.search(r"^/(?:c|tag)/", target_path):
            urls.append(urljoin(origin, target_path.rstrip("/") + ".rss"))
    return _dedupe_urls(urls)


def _extract_mediawiki_feed_urls(base_url: str, html_text: str) -> list[str]:
    urls: list[str] = []
    candidates = re.findall(
        r"""href=["']([^"']*Special:(?:RecentChanges|NewPages)[^"']*)["']""",
        html_text or "",
        flags=re.IGNORECASE,
    )
    candidates.extend(["/wiki/Special:RecentChanges", "/wiki/Special:NewPages"])
    for candidate in candidates:
        absolute = urljoin(base_url, candidate.strip())
        parsed = urlparse(absolute)
        query = dict(parse_qsl(parsed.query, keep_blank_values=True))
        query["feed"] = "rss"
        urls.append(
            urlunparse(
                (
                    parsed.scheme,
                    parsed.netloc,
                    parsed.path,
                    parsed.params,
                    urlencode(sorted(query.items())),
                    "",
                )
            )
        )
    return _dedupe_urls(urls)


def _same_origin_links(base_url: str, text: str) -> list[str]:
    parsed = urlparse(base_url)
    urls: list[str] = []
    for target in re.findall(r"""href=["']([^"']+)["']""", text or "", flags=re.IGNORECASE):
        absolute = urljoin(base_url, target.strip()).split("#", 1)[0]
        candidate = urlparse(absolute)
        if candidate.scheme not in {"http", "https"} or candidate.netloc != parsed.netloc:
            continue
        urls.append(absolute)
    return _dedupe_urls(urls)


def _statuspage_excluded_url(url: str) -> bool:
    lowered = f"{urlparse(url).path}?{urlparse(url).query}".casefold()
    return any(
        token in lowered
        for token in ("subscribe", "subscriber", "login", "auth", "manage", "admin", "support", "webhook", "api", "private")
    )


def _is_statuspage_history_path(path: str) -> bool:
    return path == "/history" or path.startswith("/history/") or re.search(r"/incidents/?$", path) is not None


def _is_statuspage_incident_path(path: str) -> bool:
    return "/incidents/" in path


def _is_statuspage_component_or_status_path(path: str) -> bool:
    return re.search(r"^/(?:components|status)(?:/|$)", path) is not None


def _extract_statuspage_root_urls(base_url: str, html_text: str) -> list[str]:
    urls: list[str] = []
    for absolute in _same_origin_links(base_url, html_text):
        if _statuspage_excluded_url(absolute):
            continue
        path = urlparse(absolute).path.casefold()
        if _is_statuspage_history_path(path) or _is_statuspage_incident_path(path) or _is_statuspage_component_or_status_path(path):
            urls.append(absolute)
    return _dedupe_urls(urls)


def _mastodon_excluded_url(url: str) -> bool:
    lowered = f"{urlparse(url).path}?{urlparse(url).query}".casefold()
    return any(
        token in lowered
        for token in ("auth", "oauth", "login", "register", "remote_interaction", "share", "media", "files")
    )


def _is_mastodon_account_path(path: str) -> bool:
    return re.search(r"^/(?:web/)?@[^/?#]+/?$", path, flags=re.IGNORECASE) is not None or re.search(
        r"^/users/[^/?#]+/?$",
        path,
        flags=re.IGNORECASE,
    ) is not None


def _is_mastodon_tag_path(path: str) -> bool:
    return re.search(r"^/(?:web/)?tags/[^/?#]+/?$", path, flags=re.IGNORECASE) is not None


def _is_mastodon_status_path(path: str) -> bool:
    return re.search(r"^/@[^/?#]+/\d+(?:/)?$", path, flags=re.IGNORECASE) is not None or re.search(
        r"^/users/[^/?#]+/statuses/\d+(?:/)?$",
        path,
        flags=re.IGNORECASE,
    ) is not None


def _is_mastodon_instance_api_path(path: str) -> bool:
    return path == "/api/v2/instance"


def _is_mastodon_tag_api_path(path: str) -> bool:
    return path.startswith("/api/v1/tags/")


def _extract_mastodon_root_urls(base_url: str, html_text: str) -> list[str]:
    parsed = urlparse(base_url)
    origin = f"{parsed.scheme}://{parsed.netloc}"
    urls = [urljoin(origin, "/api/v2/instance")]
    for absolute in _same_origin_links(base_url, html_text):
        if _mastodon_excluded_url(absolute):
            continue
        path = urlparse(absolute).path
        if _is_mastodon_account_path(path):
            urls.append(absolute)
        elif _is_mastodon_tag_path(path):
            normalized = absolute.rstrip("/")
            urls.append(normalized)
            segments = [segment for segment in urlparse(normalized).path.split("/") if segment]
            tag_name = segments[-1] if segments else ""
            if tag_name:
                urls.append(urljoin(origin, f"/api/v1/tags/{tag_name}"))
    return _dedupe_urls(urls)


STACK_EXCHANGE_SITE_HOSTS = {
    "stackoverflow.com": "stackoverflow",
    "serverfault.com": "serverfault",
    "superuser.com": "superuser",
    "askubuntu.com": "askubuntu",
    "mathoverflow.net": "mathoverflow",
}

STACK_EXCHANGE_SITE_DOMAINS = {
    "stackoverflow": "stackoverflow.com",
    "serverfault": "serverfault.com",
    "superuser": "superuser.com",
    "askubuntu": "askubuntu.com",
    "mathoverflow": "mathoverflow.net",
}


def _stack_exchange_site_for_url(url: str) -> str | None:
    host = urlparse(url).netloc.casefold()
    if host.startswith("www."):
        host = host[4:]
    if host == "api.stackexchange.com":
        return None
    if host in STACK_EXCHANGE_SITE_HOSTS:
        return STACK_EXCHANGE_SITE_HOSTS[host]
    if host.endswith(".stackexchange.com"):
        return host.removesuffix(".stackexchange.com").split(".", 1)[0] or None
    return None


def _stack_exchange_site_from_api_url(url: str) -> str | None:
    parsed = urlparse(url)
    if parsed.netloc.casefold() != "api.stackexchange.com":
        return None
    query = dict(parse_qsl(parsed.query, keep_blank_values=True))
    site = (query.get("site") or "").strip().casefold()
    return site or None


def _stack_exchange_domain_for_site(site: str | None) -> str | None:
    if not site:
        return None
    return STACK_EXCHANGE_SITE_DOMAINS.get(site) or f"{site}.stackexchange.com"


def _stack_exchange_query_site_matches(url: str, expected_site: str | None) -> bool:
    if not expected_site:
        return False
    return _stack_exchange_site_from_api_url(url) == expected_site


def _is_stack_exchange_info_api_path(path: str) -> bool:
    return path == "/2.3/info"


def _is_stack_exchange_tags_index_api_path(path: str) -> bool:
    return path == "/2.3/tags"


def _is_stack_exchange_tag_info_api_path(path: str) -> bool:
    return re.search(r"^/2\.3/tags/[^/?#]+/info/?$", path, flags=re.IGNORECASE) is not None


def _is_stack_exchange_tag_related_api_path(path: str) -> bool:
    return re.search(r"^/2\.3/tags/[^/?#]+/related/?$", path, flags=re.IGNORECASE) is not None


def _is_stack_exchange_api_url(url: str) -> bool:
    parsed = urlparse(url)
    if parsed.netloc.casefold() != "api.stackexchange.com":
        return False
    path = parsed.path.casefold()
    return (
        _is_stack_exchange_info_api_path(path)
        or _is_stack_exchange_tags_index_api_path(path)
        or _is_stack_exchange_tag_info_api_path(path)
        or _is_stack_exchange_tag_related_api_path(path)
    )


def _is_stack_exchange_tag_path(path: str) -> bool:
    return re.search(r"^/(?:questions/tagged|tags)/[^/?#]+(?:/info)?/?$", path, flags=re.IGNORECASE) is not None


def _is_stack_exchange_question_path(path: str) -> bool:
    return re.search(r"^/questions/\d+(?:/|$)", path, flags=re.IGNORECASE) is not None


def _stack_exchange_tag_slug_from_url(url: str) -> str | None:
    segments = [segment for segment in urlparse(url).path.split("/") if segment]
    if len(segments) >= 3 and segments[0] == "questions" and segments[1] == "tagged":
        return segments[2]
    if len(segments) >= 2 and segments[0] == "tags":
        return segments[1]
    return None


def _stack_exchange_excluded_url(url: str) -> bool:
    lowered = f"{urlparse(url).path}?{urlparse(url).query}".casefold()
    return any(
        token in lowered
        for token in (
            "/search",
            "search/advanced",
            "/similar",
            "auth",
            "oauth",
            "login",
            "signup",
            "/questions/ask",
            "/users/login",
            "/users/signup",
            "/review",
            "/posts/",
        )
    )


def _extract_stack_exchange_root_urls(base_url: str, html_text: str) -> list[str]:
    site = _stack_exchange_site_for_url(base_url)
    if not site:
        return []
    urls = [
        f"https://api.stackexchange.com/2.3/info?site={site}",
        f"https://api.stackexchange.com/2.3/tags?site={site}&sort=popular",
    ]
    for absolute in _same_origin_links(base_url, html_text):
        if _stack_exchange_excluded_url(absolute):
            continue
        path = urlparse(absolute).path
        if not _is_stack_exchange_tag_path(path):
            continue
        normalized = _canonical_source_url(absolute)
        urls.append(normalized)
        tag_slug = _stack_exchange_tag_slug_from_url(normalized)
        if tag_slug:
            urls.append(f"https://api.stackexchange.com/2.3/tags/{tag_slug}/info?site={site}")
            urls.append(f"https://api.stackexchange.com/2.3/tags/{tag_slug}/related?site={site}")
    return _dedupe_urls(urls)


def _structure_seed_hints_for_url(url: str, analysis: dict[str, object]) -> list[str]:
    path = urlparse(url).path.casefold()
    hints = {
        hint
        for hint in list(analysis["structure_hints"])
        if hint.startswith("platform_") or hint.endswith("_platform")
    }
    if url in list(analysis["discovered_feed_urls"]):
        hints.add("feed_autodiscovery")
    if url in list(analysis["discovered_sitemap_urls"]):
        hints.add("robots_sitemap")
    if url in list(analysis["discovered_navigation_urls"]):
        if any(token in path for token in ("/archive", "/latest")):
            hints.add("archive_or_latest_navigation")
        if any(token in path for token in ("/category", "/categories", "/c/")):
            hints.add("category_navigation")
        if any(token in path for token in ("/tag", "/tags")):
            hints.add("tag_navigation")
        if "special:recentchanges" in path or "special:newpages" in path:
            hints.add("recent_changes_navigation")
        if _is_statuspage_history_path(path):
            hints.add("status_history_navigation")
        if _is_statuspage_incident_path(path):
            hints.add("status_incident_link")
        if _is_mastodon_instance_api_path(path):
            hints.add("mastodon_instance_api")
        if _is_mastodon_tag_api_path(path) or _is_mastodon_tag_path(path):
            hints.add("mastodon_tag_navigation")
            hints.add("catalog_link")
        if _is_mastodon_account_path(path):
            hints.add("mastodon_account_navigation")
            hints.add("catalog_link")
        if _is_stack_exchange_api_url(url):
            hints.add("catalog_link")
            if _is_stack_exchange_info_api_path(path):
                hints.add("stack_exchange_info_api")
            elif _is_stack_exchange_tags_index_api_path(path):
                hints.add("stack_exchange_tag_index")
            elif _is_stack_exchange_tag_info_api_path(path):
                hints.add("stack_exchange_tag_info")
            elif _is_stack_exchange_tag_related_api_path(path):
                hints.add("stack_exchange_tag_related")
        if _is_stack_exchange_tag_path(path):
            hints.update({"catalog_link", "tag_navigation", "stack_exchange_tag_index"})
        if _is_stack_exchange_question_path(path):
            hints.add("stack_exchange_question_navigation")
    return sorted(hints)


def _apply_platform_seed_overrides(
    seed: SourceDiscoveryCandidateSeed,
    *,
    url: str,
    platform_family: str,
    discovery_method: str,
) -> SourceDiscoveryCandidateSeed:
    if platform_family not in {"mastodon", "statuspage", "stack_exchange"}:
        return seed
    path = urlparse(url).path.casefold()
    hints = set(seed.structure_hints)
    tags = set(seed.source_family_tags)
    updates: dict[str, object] = {
        "platform_family": platform_family,
        "auth_requirement": "no_auth",
        "captcha_requirement": "no_captcha",
        "intake_disposition": "public_no_auth",
        "policy_state": "manual_review",
        "access_result": seed.access_result,
        "machine_readable_result": seed.machine_readable_result,
    }
    if platform_family == "statuspage":
        tags.update({"official", "status_page"})
        hints.update({"platform_statuspage", "status_platform"})
        updates["source_class"] = "official"
        if _is_statuspage_history_path(path):
            hints.update({"catalog_link", "status_history_navigation"})
            updates["discovery_role"] = "root" if discovery_method == "structure_scan" else "candidate"
        elif _is_statuspage_incident_path(path):
            hints.add("status_incident_link")
            updates["discovery_role"] = "candidate"
        elif _is_statuspage_component_or_status_path(path):
            updates["discovery_role"] = "candidate"
    elif platform_family == "mastodon":
        tags.update({"federated", "social_public"})
        hints.update({"platform_mastodon", "federated_platform"})
        if _is_mastodon_instance_api_path(path):
            hints.update({"catalog_link", "mastodon_instance_api"})
            updates.update(
                {
                    "source_type": "dataset",
                    "source_class": "dataset",
                    "machine_readable_result": "partial",
                    "discovery_role": "root" if discovery_method == "structure_scan" else "candidate",
                }
            )
        elif _is_mastodon_tag_api_path(path):
            hints.update({"catalog_link", "mastodon_tag_navigation"})
            updates.update(
                {
                    "source_type": "dataset",
                    "source_class": "dataset",
                    "machine_readable_result": "partial",
                    "discovery_role": "root" if discovery_method == "structure_scan" else "candidate",
                }
            )
        elif _is_mastodon_tag_path(path):
            hints.update({"catalog_link", "mastodon_tag_navigation"})
            updates.update(
                {
                    "source_class": "community",
                    "discovery_role": "root" if discovery_method == "structure_scan" else "candidate",
                }
            )
        elif _is_mastodon_account_path(path):
            hints.update({"catalog_link", "mastodon_account_navigation"})
            updates.update(
                {
                    "source_class": "community",
                    "discovery_role": "root" if discovery_method == "structure_scan" else "candidate",
                }
            )
        elif _is_mastodon_status_path(path):
            updates.update({"source_class": "community", "discovery_role": "candidate"})
    elif platform_family == "stack_exchange":
        tags.add("forum")
        hints.update({"platform_stack_exchange", "forum_platform"})
        if _is_stack_exchange_api_url(url):
            hints.add("catalog_link")
            updates.update(
                {
                    "source_type": "dataset",
                    "source_class": "dataset",
                    "machine_readable_result": "partial",
                    "discovery_role": "root" if discovery_method == "structure_scan" else "candidate",
                }
            )
            if _is_stack_exchange_info_api_path(path):
                hints.add("stack_exchange_info_api")
            elif _is_stack_exchange_tags_index_api_path(path):
                hints.add("stack_exchange_tag_index")
            elif _is_stack_exchange_tag_info_api_path(path):
                hints.add("stack_exchange_tag_info")
            elif _is_stack_exchange_tag_related_api_path(path):
                hints.add("stack_exchange_tag_related")
        elif _is_stack_exchange_tag_path(path):
            hints.update({"catalog_link", "tag_navigation", "stack_exchange_tag_index"})
            updates.update(
                {
                    "source_class": "community",
                    "discovery_role": "root" if discovery_method == "structure_scan" else "candidate",
                }
            )
        elif _is_stack_exchange_question_path(path):
            hints.add("stack_exchange_question_navigation")
            updates.update({"source_class": "community", "discovery_role": "candidate"})
    updates["structure_hints"] = sorted(hints)
    updates["source_family_tags"] = sorted(tags)
    return seed.model_copy(update=updates)


def _platform_discovery_surfaces(target_url: str, html_text: str, platform_family: str) -> tuple[list[str], list[str], list[str]]:
    if platform_family == "discourse":
        return _extract_discourse_feed_urls(target_url, html_text), [], ["forum_platform", "platform_discourse"]
    if platform_family == "mediawiki":
        navigation_urls = _dedupe_urls(
            [
                urljoin(target_url, "/wiki/Special:RecentChanges"),
                urljoin(target_url, "/wiki/Special:NewPages"),
            ]
        )
        return _extract_mediawiki_feed_urls(target_url, html_text), navigation_urls, ["wiki_platform", "platform_mediawiki"]
    if platform_family == "mastodon":
        return [], _extract_mastodon_root_urls(target_url, html_text), ["federated_platform", "platform_mastodon"]
    if platform_family == "stack_exchange":
        return [], _extract_stack_exchange_root_urls(target_url, html_text), ["forum_platform", "platform_stack_exchange"]
    if platform_family == "statuspage":
        return [], _extract_statuspage_root_urls(target_url, html_text), ["status_platform", "platform_statuspage"]
    return [], [], []


def _analyze_structure_scan(
    *,
    target_url: str,
    html_text: str,
    robots_text: str,
    max_discovered: int,
) -> dict[str, object]:
    platform_family = _detect_platform_family(target_url, html_text)
    feed_urls = _extract_feed_urls_from_html(target_url, html_text)
    sitemap_urls = _extract_sitemap_urls_from_robots(target_url, robots_text)[:max_discovered]
    navigation_urls = _extract_navigation_urls(target_url, html_text)
    platform_feed_urls, platform_navigation_urls, platform_hints = _platform_discovery_surfaces(
        target_url,
        html_text,
        platform_family,
    )
    feed_urls = _dedupe_urls(feed_urls + platform_feed_urls)[:max_discovered]
    navigation_urls = _dedupe_urls(navigation_urls + platform_navigation_urls)[:max_discovered]
    auth_signals = _detect_auth_signals(html_text)
    captcha_signals = _detect_captcha_signals(html_text)
    structure_hints = sorted(
        set(
            _structure_hints_from_scan(
                feed_urls=feed_urls,
                sitemap_urls=sitemap_urls,
                navigation_urls=navigation_urls,
                auth_signals=auth_signals,
                captcha_signals=captcha_signals,
                platform_hints=platform_hints,
            )
        )
    )
    if not (html_text or robots_text):
        auth_requirement = "unknown"
        captcha_requirement = "unknown"
    else:
        auth_requirement = "login_required" if auth_signals else "no_auth"
        captcha_requirement = "captcha_required" if captcha_signals else "no_captcha"
    intake_disposition = _merge_intake_disposition(
        "hold_review",
        "public_no_auth" if auth_requirement == "no_auth" and captcha_requirement == "no_captcha" else "hold_review",
        auth_requirement=auth_requirement,
        captcha_requirement=captcha_requirement,
    )
    return {
        "discovered_feed_urls": feed_urls,
        "discovered_sitemap_urls": sitemap_urls,
        "discovered_navigation_urls": navigation_urls,
        "platform_family": platform_family,
        "auth_signals": auth_signals,
        "captcha_signals": captcha_signals,
        "structure_hints": structure_hints,
        "auth_requirement": auth_requirement,
        "captcha_requirement": captcha_requirement,
        "intake_disposition": intake_disposition,
    }


def _structure_candidate_seeds(
    request: SourceDiscoveryStructureScanRequest,
    *,
    analysis: dict[str, object],
    caveats: list[str],
) -> list[SourceDiscoveryCandidateSeed]:
    seeds: list[SourceDiscoveryCandidateSeed] = []
    for url in list(analysis["discovered_feed_urls"]) + list(analysis["discovered_sitemap_urls"]) + list(analysis["discovered_navigation_urls"]):
        canonical_url = _canonical_source_url(str(url))
        seed = _candidate_seed_from_extracted_url(
            url=canonical_url,
            source_id=_generated_source_id_for_url(canonical_url),
            title=urlparse(canonical_url).netloc,
            wave_id=request.wave_id,
            wave_title=request.wave_title,
            discovery_reason=request.discovery_reason,
            caveats=caveats + [
                "Structure scan candidate came from site-native discovery surfaces and remains candidate-only.",
            ],
            discovery_methods=["structure_scan"],
            structure_hints=_structure_seed_hints_for_url(canonical_url, analysis),
            platform_family=str(analysis["platform_family"]),
        )
        if seed is None:
            continue
        seeds.append(
            _apply_platform_seed_overrides(
                seed,
                url=canonical_url,
                platform_family=str(analysis["platform_family"]),
                discovery_method="structure_scan",
            )
        )
    deduped: list[SourceDiscoveryCandidateSeed] = []
    seen: set[str] = set()
    for seed in seeds:
        if seed.url in seen:
            continue
        seen.add(seed.url)
        deduped.append(seed)
    return deduped


def _extract_feed_urls_from_html(base_url: str, html_text: str) -> list[str]:
    urls = re.findall(
        r"""<link[^>]+rel=["'][^"']*alternate[^"']*["'][^>]+type=["'][^"']*(?:rss|atom)[^"']*["'][^>]+href=["']([^"']+)["']""",
        html_text or "",
        flags=re.IGNORECASE,
    )
    urls.extend(
        re.findall(
            r"""href=["']([^"']*(?:/feed|/rss|\.xml|\.atom)[^"']*)["']""",
            html_text or "",
            flags=re.IGNORECASE,
        )
    )
    return _dedupe_urls([urljoin(base_url, value.strip()) for value in urls])


def _extract_sitemap_urls_from_robots(base_url: str, robots_text: str) -> list[str]:
    urls = [
        value.strip()
        for value in re.findall(r"(?im)^\s*Sitemap:\s*(\S+)\s*$", robots_text or "")
    ]
    if not urls and robots_text:
        urls.extend(re.findall(r"https?://[^\s]+sitemap[^\s]*", robots_text, flags=re.IGNORECASE))
    if not urls:
        parsed = urlparse(base_url)
        urls.append(urlunparse((parsed.scheme, parsed.netloc, "/sitemap.xml", "", "", "")))
    return _dedupe_urls(urls)


def _extract_navigation_urls(base_url: str, html_text: str) -> list[str]:
    urls = re.findall(
        r"""href=["']([^"']*(?:latest|archive|archives|category|categories|tag|tags|status|incidents?)[^"']*)["']""",
        html_text or "",
        flags=re.IGNORECASE,
    )
    return _dedupe_urls([urljoin(base_url, value.strip()) for value in urls])


def _extract_sitemap_candidate_urls(base_url: str, text: str, *, max_discovered: int) -> tuple[list[str], str, int]:
    if not text.strip():
        return [], "empty", 0
    extracted: list[str] = []
    sitemap_type = "unknown"
    scanned_url_count = 0
    try:
        root = ElementTree.fromstring(text)
        root_name = _xml_local_name(root.tag)
        if root_name == "sitemapindex":
            sitemap_type = "sitemap_index"
            extracted = [
                _normalize_text(element.text or "")
                for element in root.iter()
                if _xml_local_name(element.tag) == "loc" and _normalize_text(element.text or "")
            ]
        elif root_name == "urlset":
            sitemap_type = "urlset"
            extracted = [
                _normalize_text(element.text or "")
                for element in root.iter()
                if _xml_local_name(element.tag) == "loc" and _normalize_text(element.text or "")
            ]
        else:
            fallback = [
                _normalize_text(element.text or "")
                for element in root.iter()
                if _xml_local_name(element.tag) == "loc" and _normalize_text(element.text or "")
            ]
            if fallback:
                sitemap_type = "xml_loc_set"
                extracted = fallback
    except ElementTree.ParseError:
        extracted = []
    if not extracted:
        sitemap_type = "html_fallback"
        extracted = _extract_candidate_links(base_url, text)
    scanned_url_count = len(extracted)
    canonical_urls = _dedupe_urls([urljoin(base_url, value) for value in extracted])[:max_discovered]
    return canonical_urls, sitemap_type, scanned_url_count


def _xml_local_name(tag: str) -> str:
    if "}" in tag:
        return tag.rsplit("}", 1)[-1]
    return tag


def _detect_auth_signals(html_text: str) -> list[str]:
    lowered = (html_text or "").casefold()
    signals: list[str] = []
    if any(token in lowered for token in ("type=\"password\"", "name=\"password\"", "sign in", "log in", "login", "oauth", "subscribe to continue")):
        signals.append("login_prompt_detected")
    if any(token in lowered for token in ("account required", "members only", "subscriber only")):
        signals.append("restricted_content_marker")
    return signals


def _detect_captcha_signals(html_text: str) -> list[str]:
    lowered = (html_text or "").casefold()
    signals: list[str] = []
    if any(token in lowered for token in ("recaptcha", "hcaptcha", "g-recaptcha", "cf-challenge", "captcha")):
        signals.append("captcha_marker_detected")
    return signals


def _structure_hints_from_scan(
    *,
    feed_urls: list[str],
    sitemap_urls: list[str],
    navigation_urls: list[str],
    auth_signals: list[str],
    captcha_signals: list[str],
    platform_hints: list[str] | None = None,
) -> list[str]:
    hints: list[str] = []
    if feed_urls:
        hints.append("feed_autodiscovery")
    if sitemap_urls:
        hints.append("robots_sitemap")
    if navigation_urls:
        hints.append("archive_or_latest_navigation")
    lowered_navigation = [url.casefold() for url in navigation_urls]
    if any(token in url for url in lowered_navigation for token in ("/category", "/categories", "/c/")):
        hints.append("category_navigation")
    if any(token in url for url in lowered_navigation for token in ("/tag", "/tags")):
        hints.append("tag_navigation")
    if any("special:recentchanges" in url or "special:newpages" in url for url in lowered_navigation):
        hints.append("recent_changes_navigation")
    if any(_is_statuspage_history_path(urlparse(url).path.casefold()) for url in navigation_urls):
        hints.append("status_history_navigation")
    if any(_is_statuspage_incident_path(urlparse(url).path.casefold()) for url in navigation_urls):
        hints.append("status_incident_link")
    if any(_is_mastodon_instance_api_path(urlparse(url).path.casefold()) for url in navigation_urls):
        hints.append("mastodon_instance_api")
    if any(
        _is_mastodon_tag_api_path(urlparse(url).path.casefold()) or _is_mastodon_tag_path(urlparse(url).path)
        for url in navigation_urls
    ):
        hints.append("mastodon_tag_navigation")
    if any(_is_mastodon_account_path(urlparse(url).path) for url in navigation_urls):
        hints.append("mastodon_account_navigation")
    if auth_signals:
        hints.append("login_markers_detected")
    if captcha_signals:
        hints.append("captcha_markers_detected")
    hints.extend(platform_hints or [])
    return hints


def _extract_candidate_links(base_url: str, text: str) -> list[str]:
    if not text:
        return []
    links = re.findall(r"""(?:href|src)=["']([^"']+)["']""", text, flags=re.IGNORECASE)
    links.extend(re.findall(r"<link[^>]*>(https?://[^<\s]+)</link>", text, flags=re.IGNORECASE))
    links.extend(re.findall(r"https?://[^\s<>'\"]+", text))
    return [urljoin(base_url, link.strip()) for link in links]


def _extract_catalog_candidate_urls(
    base_url: str,
    text: str,
    *,
    max_discovered: int,
    platform_family: str | None = None,
) -> tuple[list[str], str]:
    if not text.strip():
        return [], "empty"
    active_platform_family = platform_family or _detect_platform_family_from_url(base_url)
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        payload = None
    if active_platform_family == "unknown" and payload is None:
        active_platform_family = _detect_platform_family(base_url, text)
    if active_platform_family == "statuspage":
        urls = _collect_urls_from_object(payload) if payload is not None else _extract_candidate_links(base_url, text)
        return _bounded_statuspage_candidate_urls(base_url, urls, max_discovered=max_discovered), "json" if payload is not None else "html"
    if active_platform_family == "mastodon":
        urls = _collect_urls_from_object(payload) if payload is not None else _extract_candidate_links(base_url, text)
        return _bounded_mastodon_candidate_urls(base_url, urls, max_discovered=max_discovered), "json" if payload is not None else "html"
    if active_platform_family == "stack_exchange":
        urls = _collect_urls_from_object(payload) if payload is not None else _extract_candidate_links(base_url, text)
        return _bounded_stack_exchange_candidate_urls(base_url, urls, max_discovered=max_discovered), "json" if payload is not None else "html"
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


def _bounded_statuspage_candidate_urls(base_url: str, urls: list[str], *, max_discovered: int) -> list[str]:
    discovered: list[str] = []
    base_domain = urlparse(base_url).netloc.lower()
    for url in urls:
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"} or parsed.netloc.lower() != base_domain:
            continue
        normalized = _canonical_source_url(url)
        path = parsed.path.casefold()
        if normalized in discovered or _statuspage_excluded_url(normalized):
            continue
        if not (
            _is_statuspage_history_path(path)
            or _is_statuspage_incident_path(path)
            or _is_statuspage_component_or_status_path(path)
        ):
            continue
        discovered.append(normalized)
        if len(discovered) >= max_discovered:
            break
    return discovered


def _bounded_mastodon_candidate_urls(base_url: str, urls: list[str], *, max_discovered: int) -> list[str]:
    discovered: list[str] = []
    base_domain = urlparse(base_url).netloc.lower()
    for url in urls:
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"} or parsed.netloc.lower() != base_domain:
            continue
        normalized = _canonical_source_url(url)
        path = parsed.path.casefold()
        if normalized in discovered or _mastodon_excluded_url(normalized):
            continue
        if not (
            _is_mastodon_account_path(path)
            or _is_mastodon_tag_path(path)
            or _is_mastodon_status_path(path)
            or _is_mastodon_instance_api_path(path)
            or _is_mastodon_tag_api_path(path)
        ):
            continue
        discovered.append(normalized)
        if len(discovered) >= max_discovered:
            break
    return discovered


def _bounded_stack_exchange_candidate_urls(base_url: str, urls: list[str], *, max_discovered: int) -> list[str]:
    discovered: list[str] = []
    expected_site = _stack_exchange_site_for_url(base_url) or _stack_exchange_site_from_api_url(base_url)
    allowed_html_host = (_stack_exchange_domain_for_site(expected_site) or urlparse(base_url).netloc).casefold()
    for url in urls:
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"}:
            continue
        normalized = _canonical_source_url(url)
        if normalized in discovered or _stack_exchange_excluded_url(normalized):
            continue
        host = parsed.netloc.casefold()
        path = parsed.path.casefold()
        if host == allowed_html_host:
            if not (_is_stack_exchange_tag_path(path) or _is_stack_exchange_question_path(path)):
                continue
        elif host == "api.stackexchange.com":
            if not _stack_exchange_query_site_matches(normalized, expected_site):
                continue
            if not (_is_stack_exchange_tag_info_api_path(path) or _is_stack_exchange_tag_related_api_path(path)):
                continue
        else:
            continue
        discovered.append(normalized)
        if len(discovered) >= max_discovered:
            break
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


def _loads_dict(raw: str | None) -> dict[str, Any]:
    if not raw:
        return {}
    try:
        value = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    return value if isinstance(value, dict) else {}


def _coerce_float(value: object) -> float | None:
    try:
        if value is None or value == "":
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _loads_list_of_dicts(value: object) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def _coerce_optional_int(value: object) -> int | None:
    try:
        if value is None or value == "":
            return None
        return int(value)
    except (TypeError, ValueError):
        return None


def _coerce_optional_float(value: object) -> float | None:
    try:
        if value is None or value == "":
            return None
        return round(float(value), 4)
    except (TypeError, ValueError):
        return None


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
