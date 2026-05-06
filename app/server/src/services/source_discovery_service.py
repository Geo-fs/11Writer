from __future__ import annotations

import asyncio
import base64
import hashlib
import json
import re
import unicodedata
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
    SourceAdversarialFindingORM,
    SourceClaimOutcomeORM,
    SourceContentSnapshotORM,
    SourceKnowledgeNodeORM,
    RuntimeSchedulerRunORM,
    RuntimeSchedulerWorkerORM,
    SourceArchiveHitORM,
    SourceEventClusterORM,
    SourceEventMemberORM,
    SourceEventOpenQuestionORM,
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
    SourceRuntimeBudgetWindowORM,
    SourceRuntimeWorkAttemptORM,
    SourceRuntimeWorkItemORM,
    SourceWaveFitORM,
)
from src.types.source_discovery import (
    SourceDiscoveryAdversarialFindingSummary,
    SourceDiscoveryAdversarialFindingsResponse,
    SourceDiscoveryAdversarialOverviewResponse,
    SourceDiscoveryAdversarialRiskLevel,
    SourceDiscoveryArchiveIndexScanRequest,
    SourceDiscoveryArchiveIndexScanResponse,
    SourceDiscoveryArchiveHitSummary,
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
    SourceDiscoveryDirectoryScanRequest,
    SourceDiscoveryDirectoryScanResponse,
    SourceDiscoveryEventClusterDetailResponse,
    SourceDiscoveryEventClusterSummary,
    SourceDiscoveryEventGraphRefreshRequest,
    SourceDiscoveryEventGraphRefreshResponse,
    SourceDiscoveryEventMemberSummary,
    SourceDiscoveryEventOpenQuestionSummary,
    SourceDiscoveryEventOverviewResponse,
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
    SourceDiscoveryLinkGraphScanRequest,
    SourceDiscoveryLinkGraphScanResponse,
    SourceDiscoveryLocaleExpansionProviderRunSummary,
    SourceDiscoveryLocaleSeedExpandRequest,
    SourceDiscoveryLocaleSeedExpandResponse,
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
    SourceDiscoveryReputationProfileSummary,
    SourceDiscoveryReputationProfilesResponse,
    SourceDiscoveryReputationRecomputeRequest,
    SourceDiscoveryReputationRecomputeResponse,
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
    SourceDiscoveryRuntimeFailureSummary,
    SourceDiscoveryRuntimeFailuresResponse,
    SourceDiscoveryRuntimeRunDetailResponse,
    SourceDiscoveryRuntimeRunSummary,
    SourceDiscoveryRuntimeWorkItemSummary,
    SourceDiscoveryRuntimeWorkQueueResponse,
    SourceDiscoveryRuntimeRunsResponse,
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
    "link_graph_scan": 24,
}

ALLOWED_ARCHIVE_FETCH_HOSTS = {
    "webcache.archive-it.org",
    "wayback.archive-it.org",
    "web.archive.org",
}

OUTCOME_SCORE_DELTAS = {
    "confirmed": 0.06,
    "contradicted": -0.10,
    "corrected": -0.03,
    "outdated": -0.02,
    "unresolved": 0.0,
    "not_applicable": 0.0,
}

DEFAULT_REPUTATION_PROFILE = "baseline_v2"
REPUTATION_PROFILES: dict[str, dict[str, object]] = {
    "baseline_v2": {
        "outcome_deltas": dict(OUTCOME_SCORE_DELTAS),
        "source_class_bias": {
            "official": 0.0,
            "records": 0.0,
            "news": 0.0,
            "community": 0.0,
            "social": 0.0,
            "unknown": 0.0,
        },
        "evidence_basis_bias": {
            "primary": 0.0,
            "observed": 0.0,
            "documented": 0.0,
            "contextual": 0.0,
            "reported": 0.0,
        },
        "corroboration_bonus": 0.0,
        "contradiction_penalty": 0.0,
        "correction_penalty": 0.0,
        "health_penalty": {
            "degraded": 0.0,
            "offline": 0.0,
            "blocked": 0.0,
        },
        "timeliness_penalty": 0.0,
    },
    "calibrated_v1": {
        "outcome_deltas": dict(OUTCOME_SCORE_DELTAS),
        "source_class_bias": {
            "official": 0.01,
            "records": 0.01,
            "news": 0.0,
            "community": 0.0,
            "social": -0.005,
            "unknown": 0.0,
        },
        "evidence_basis_bias": {
            "primary": 0.015,
            "observed": 0.01,
            "documented": 0.005,
            "contextual": 0.0,
            "reported": 0.0,
        },
        "corroboration_bonus": 0.01,
        "contradiction_penalty": -0.012,
        "correction_penalty": -0.008,
        "health_penalty": {
            "degraded": -0.01,
            "offline": -0.015,
            "blocked": -0.02,
        },
        "timeliness_penalty": -0.01,
    },
}
ADVERSARIAL_RISK_ORDER = {"none": 0, "low": 1, "medium": 2, "high": 3}
ADVERSARIAL_FINDING_RULES: list[dict[str, object]] = [
    {
        "signal_type": "instruction_override",
        "risk_level": "medium",
        "summary": "Page text attempts to override or ignore agent instructions.",
        "patterns": [
            r"ignore (?:all )?(?:previous|prior) instructions",
            r"disregard .*instructions",
            r"override (?:your|system) instructions",
            r"forget (?:the )?(?:rules|policy|previous instructions)",
        ],
    },
    {
        "signal_type": "secret_request",
        "risk_level": "high",
        "summary": "Page text asks for secrets, system prompts, tokens, or credentials.",
        "patterns": [
            r"reveal (?:your )?(?:system prompt|hidden prompt|api key|token|credentials|password)",
            r"show (?:your )?(?:system prompt|api key|token|credentials|password)",
            r"print (?:your )?(?:system prompt|api key|token|credentials|password)",
            r"paste (?:your )?(?:token|api key|password|credentials)",
        ],
    },
    {
        "signal_type": "download_or_execute_request",
        "risk_level": "high",
        "summary": "Page text asks the agent or user to download, run, or execute code.",
        "patterns": [
            r"download .* and run",
            r"run (?:this|the following) (?:script|command|code)",
            r"execute (?:this|the following) (?:script|command|code)",
            r"(?:powershell|bash|cmd|curl|wget)\b.{0,80}",
        ],
    },
    {
        "signal_type": "developer_tools_request",
        "risk_level": "high",
        "summary": "Page text asks the agent or user to use DevTools, console commands, or local shell steps.",
        "patterns": [
            r"open devtools",
            r"open the console",
            r"paste .* into (?:devtools|the console)",
            r"run this in (?:your )?(?:terminal|shell|powershell)",
        ],
    },
    {
        "signal_type": "credential_or_login_request",
        "risk_level": "high",
        "summary": "Page text asks for login, credentials, or file/clipboard access outside approved workflow.",
        "patterns": [
            r"enter (?:your )?(?:login|credentials|password)",
            r"sign in to continue",
            r"upload (?:a|your) file",
            r"paste from (?:the )?clipboard",
            r"share (?:your )?(?:history|local files|browser history)",
        ],
    },
    {
        "signal_type": "validation_bypass_request",
        "risk_level": "medium",
        "summary": "Page text attempts to bypass review or promote trust or validation directly.",
        "patterns": [
            r"mark (?:this|the source) as (?:validated|trusted|approved)",
            r"bypass (?:review|validation|safety)",
            r"skip (?:review|validation|approval)",
            r"approve this source immediately",
        ],
    },
]
RUNTIME_BUDGET_WINDOW_MINUTES = 60
RETRYABLE_FAILURE_KINDS = {"rate_limited", "timeout", "dns_error", "tls_error", "unexpected_status", "parse_error", "unsupported_shape"}
BLOCKING_FAILURE_KINDS = {"blocked_auth", "blocked_captcha", "operator_hold"}


@dataclass
class _DiscoveryPriorityContext:
    best_fit_by_source_id: dict[str, SourceWaveFitORM | None] = field(default_factory=dict)
    root_domain_counts: dict[str, int] = field(default_factory=dict)
    root_tag_counts: dict[str, int] = field(default_factory=dict)


@dataclass
class _ArchiveDiscoveryRecord:
    provider: str
    original_url: str | None
    archive_url: str | None
    timestamp: str | None = None


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
                    archive_hits=detail.archive_hits,
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
                    adversarial_findings=detail.adversarial_findings,
                    pending_claim_count=detail.pending_claim_count,
                    latest_review_claim_at=detail.latest_review_claim_at,
                    event_clusters=detail.event_clusters,
                    contested_event_count=detail.contested_event_count,
                    open_question_count=detail.open_question_count,
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
                linked_events=_event_clusters_for_knowledge_node(session, node.node_id, limit=25),
                caveats=SOURCE_DISCOVERY_CAVEATS + [
                    "Duplicate classes are heuristic workflow aids and should be reviewed before they affect downstream interpretation.",
                ],
            )

    def event_overview(
        self,
        *,
        limit: int = 100,
        source_id: str | None = None,
        wave_id: str | None = None,
        knowledge_node_id: str | None = None,
    ) -> SourceDiscoveryEventOverviewResponse:
        with session_scope(self._settings.source_discovery_database_url) as session:
            stmt = select(SourceEventClusterORM).order_by(SourceEventClusterORM.last_seen_at.desc(), SourceEventClusterORM.event_id)
            if wave_id:
                stmt = stmt.where(SourceEventClusterORM.wave_id == wave_id)
            events = list(session.scalars(stmt))
            if source_id:
                source_event_ids = {
                    row.event_id
                    for row in session.scalars(
                        select(SourceEventMemberORM).where(SourceEventMemberORM.source_id == source_id)
                    )
                }
                events = [event for event in events if event.event_id in source_event_ids]
            if knowledge_node_id:
                events = [event for event in events if knowledge_node_id in _loads_list(event.knowledge_node_ids_json)]
            counts_by_status: dict[str, int] = {}
            contested_count = 0
            open_question_count = 0
            for event in events:
                counts_by_status[event.status] = counts_by_status.get(event.status, 0) + 1
                if event.status in {"contested", "corrected"}:
                    contested_count += 1
                if event.status == "open_question":
                    open_question_count += 1
            return SourceDiscoveryEventOverviewResponse(
                metadata={
                    "source": "source-discovery-event-overview",
                    "count": len(events[: max(0, limit)]),
                    "sourceId": source_id,
                    "waveId": wave_id,
                    "knowledgeNodeId": knowledge_node_id,
                },
                total_event_count=len(events),
                contested_event_count=contested_count,
                open_question_count=open_question_count,
                counts_by_status=counts_by_status,
                events=[_serialize_event_cluster(event) for event in events[: max(0, limit)]],
                caveats=SOURCE_DISCOVERY_CAVEATS + [
                    "Event clusters are deterministic review artifacts and do not adjudicate event truth.",
                ],
            )

    def event_detail(self, event_id: str) -> SourceDiscoveryEventClusterDetailResponse:
        with session_scope(self._settings.source_discovery_database_url) as session:
            event = session.get(SourceEventClusterORM, event_id)
            if event is None:
                raise ValueError(f"Unknown event_id: {event_id}")
            members = list(
                session.scalars(
                    select(SourceEventMemberORM)
                    .where(SourceEventMemberORM.event_id == event_id)
                    .order_by(SourceEventMemberORM.created_at.asc(), SourceEventMemberORM.member_id.asc())
                )
            )
            open_questions = list(
                session.scalars(
                    select(SourceEventOpenQuestionORM)
                    .where(SourceEventOpenQuestionORM.event_id == event_id)
                    .order_by(SourceEventOpenQuestionORM.created_at.asc(), SourceEventOpenQuestionORM.question_id.asc())
                )
            )
            return SourceDiscoveryEventClusterDetailResponse(
                event=_serialize_event_cluster(event),
                members=[_serialize_event_member(row) for row in members],
                open_questions=[_serialize_event_open_question(row) for row in open_questions],
                caveats=SOURCE_DISCOVERY_CAVEATS + [
                    "Contradiction and correction posture are evidence-graph states, not automated truth resolution.",
                ],
            )

    def run_event_graph_refresh_job(
        self,
        request: SourceDiscoveryEventGraphRefreshRequest,
    ) -> SourceDiscoveryEventGraphRefreshResponse:
        now = _utc_now()
        job_id = f"source-discovery-job:event-graph-refresh:{_compact_timestamp(now)}"
        with session_scope(self._settings.source_discovery_database_url) as session:
            summary = _refresh_event_graph(
                session,
                source_ids=request.source_ids,
                wave_ids=request.wave_ids,
                knowledge_node_ids=request.knowledge_node_ids,
                include_pending_claims=request.include_pending_claims,
                mode=request.mode,
                max_events=max(0, request.max_events),
                now=now,
            )
            job = SourceDiscoveryJobORM(
                job_id=job_id,
                job_type="event_graph_refresh",
                status="completed",
                seed_url=None,
                wave_id=request.wave_ids[0] if request.wave_ids else None,
                wave_title=None,
                discovered_source_ids_json=json.dumps(sorted(summary["source_ids"])),
                rejected_reason=None,
                request_budget=0,
                used_requests=0,
                started_at=now,
                finished_at=now,
                outcome_summary=f"Refreshed {summary['created_event_count'] + summary['updated_event_count']} event clusters from {summary['processed_claim_count']} reviewable claims.",
                caveats_json=json.dumps(list(request.caveats) + [
                    "Event graph refresh is deterministic and local-only; no network access was performed.",
                ]),
            )
            session.add(job)
            session.flush()
            events = [
                event
                for event in (
                    session.get(SourceEventClusterORM, event_id)
                    for event_id in summary["event_ids"][: max(0, request.max_events)]
                )
                if event is not None
            ]
            return SourceDiscoveryEventGraphRefreshResponse(
                job=_serialize_job(job),
                processed_claim_count=summary["processed_claim_count"],
                created_event_count=summary["created_event_count"],
                updated_event_count=summary["updated_event_count"],
                contested_event_count=summary["contested_event_count"],
                open_question_count=summary["open_question_count"],
                events=[_serialize_event_cluster(event) for event in events],
                caveats=SOURCE_DISCOVERY_CAVEATS + [
                    "Event clusters remain review-oriented even when multiple supporting sources converge.",
                ],
            )

    def list_reputation_profiles(self) -> SourceDiscoveryReputationProfilesResponse:
        profiles: list[SourceDiscoveryReputationProfileSummary] = []
        for name, profile in REPUTATION_PROFILES.items():
            outcome_deltas = profile.get("outcome_deltas", {})
            profiles.append(
                SourceDiscoveryReputationProfileSummary(
                    profile_name=name,
                    version=name,
                    description="Deterministic claim-outcome calibration profile for research-grade source evaluation.",
                    claim_outcome_deltas={str(key): float(value) for key, value in dict(outcome_deltas).items()},
                    source_class_modifiers={str(key): float(value) for key, value in dict(profile.get("source_class_bias", {})).items()},
                    corroboration_bonus=float(profile.get("corroboration_bonus", 0.0)),
                    contradiction_penalty=float(profile.get("contradiction_penalty", 0.0)),
                    correction_penalty=float(profile.get("correction_penalty", 0.0)),
                    timeliness_penalty=float(profile.get("timeliness_penalty", 0.0)),
                    caveats=[
                        "Default profile." if name == DEFAULT_REPUTATION_PROFILE else "Alternate profile.",
                        "Profiles are deterministic calibration presets and do not auto-switch source reputation policy.",
                    ],
                )
            )
        return SourceDiscoveryReputationProfilesResponse(
            metadata={"source": "source-discovery-reputation-profiles", "count": len(profiles)},
            profiles=profiles,
            caveats=SOURCE_DISCOVERY_CAVEATS + [
                "Profile inspection is advisory; active scoring stays fixed until an explicit recompute apply run.",
            ],
        )

    def recompute_reputation(
        self,
        request: SourceDiscoveryReputationRecomputeRequest,
    ) -> SourceDiscoveryReputationRecomputeResponse:
        now = _utc_now()
        profile_name = request.profile_name if request.profile_name in REPUTATION_PROFILES else DEFAULT_REPUTATION_PROFILE
        job_id = f"source-discovery-job:reputation-recompute:{_compact_timestamp(now)}"
        with session_scope(self._settings.source_discovery_database_url) as session:
            target_memories = _select_reputation_recompute_targets(
                session,
                source_ids=request.source_ids,
                wave_ids=request.wave_ids,
                max_sources=max(0, request.max_sources),
            )
            changed_count = 0
            score_delta_summary = {"increased": 0, "decreased": 0, "unchanged": 0}
            serialized_memories: list[SourceDiscoveryMemory] = []
            for memory in target_memories:
                baseline = _recompute_memory_reputation(session, memory, profile_name=profile_name, apply=request.mode == "apply", now=now)
                if baseline["changed"]:
                    changed_count += 1
                score_delta_summary[baseline["direction"]] = score_delta_summary.get(baseline["direction"], 0) + 1
                serialized_memories.append(_serialize_memory(session, memory))
            job = SourceDiscoveryJobORM(
                job_id=job_id,
                job_type="reputation_recompute",
                status="completed",
                seed_url=None,
                wave_id=request.wave_ids[0] if request.wave_ids else None,
                wave_title=None,
                discovered_source_ids_json=json.dumps([memory.source_id for memory in target_memories]),
                rejected_reason=None,
                request_budget=0,
                used_requests=0,
                started_at=now,
                finished_at=now,
                outcome_summary=f"Recomputed {len(target_memories)} source reputations under {profile_name} ({request.mode}).",
                caveats_json=json.dumps(list(request.caveats) + [
                    "Reputation recompute replays audited outcomes deterministically; it does not infer new claim truth.",
                ]),
            )
            session.add(job)
            session.flush()
            return SourceDiscoveryReputationRecomputeResponse(
                job=_serialize_job(job),
                profile_name=profile_name,
                affected_source_count=len(target_memories),
                changed_source_count=changed_count,
                score_delta_summary=score_delta_summary,
                memories=serialized_memories,
                caveats=SOURCE_DISCOVERY_CAVEATS + [
                    "Dry-run recompute reports projected drift only; apply mode persists the selected policy version.",
                ],
            )

    def runtime_work_queue(self, *, limit: int = 100, status: str | None = None) -> SourceDiscoveryRuntimeWorkQueueResponse:
        with session_scope(self._settings.source_discovery_database_url) as session:
            stmt = select(SourceRuntimeWorkItemORM).order_by(SourceRuntimeWorkItemORM.next_run_at.asc(), SourceRuntimeWorkItemORM.priority_score.desc())
            if status:
                stmt = stmt.where(SourceRuntimeWorkItemORM.status == status)
            items = list(session.scalars(stmt.limit(max(0, limit))))
            return SourceDiscoveryRuntimeWorkQueueResponse(
                metadata={
                    "source": "source-discovery-runtime-work-queue",
                    "count": len(items),
                    "status": status,
                },
                items=[_serialize_runtime_work_item(row) for row in items],
                caveats=SOURCE_DISCOVERY_CAVEATS + [
                    "Runtime work queue is operational state only; queued work does not approve any source.",
                ],
            )

    def runtime_failures(self, *, limit: int = 100, failure_kind: str | None = None) -> SourceDiscoveryRuntimeFailuresResponse:
        with session_scope(self._settings.source_discovery_database_url) as session:
            stmt = (
                select(SourceRuntimeWorkAttemptORM)
                .where(SourceRuntimeWorkAttemptORM.failure_kind.is_not(None))
                .order_by(SourceRuntimeWorkAttemptORM.started_at.desc(), SourceRuntimeWorkAttemptORM.attempt_id.desc())
            )
            if failure_kind:
                stmt = stmt.where(SourceRuntimeWorkAttemptORM.failure_kind == failure_kind)
            failures = list(session.scalars(stmt.limit(max(0, limit))))
            return SourceDiscoveryRuntimeFailuresResponse(
                metadata={
                    "source": "source-discovery-runtime-failures",
                    "count": len(failures),
                    "failureKind": failure_kind,
                },
                failures=[_serialize_runtime_failure(row) for row in failures],
                caveats=SOURCE_DISCOVERY_CAVEATS + [
                    "Failure history is runtime diagnostics only and should not be interpreted as source falsity.",
                ],
            )

    def runtime_runs(self, *, limit: int = 50) -> SourceDiscoveryRuntimeRunsResponse:
        with session_scope(self._settings.source_discovery_database_url) as session:
            runs = list(
                session.scalars(
                    select(RuntimeSchedulerRunORM)
                    .where(RuntimeSchedulerRunORM.worker_name == "source_discovery")
                    .order_by(RuntimeSchedulerRunORM.started_at.desc())
                    .limit(max(0, limit))
                )
            )
            return SourceDiscoveryRuntimeRunsResponse(
                metadata={"source": "source-discovery-runtime-runs", "count": len(runs)},
                runs=[_serialize_runtime_run(row) for row in runs],
                caveats=SOURCE_DISCOVERY_CAVEATS + [
                    "Runtime run summaries describe queue execution decisions; they do not re-execute work.",
                ],
            )

    def runtime_run_detail(self, run_id: str) -> SourceDiscoveryRuntimeRunDetailResponse:
        with session_scope(self._settings.source_discovery_database_url) as session:
            run = session.get(RuntimeSchedulerRunORM, run_id)
            if run is None:
                raise ValueError(f"Unknown run_id: {run_id}")
            attempts = list(
                session.scalars(
                    select(SourceRuntimeWorkAttemptORM)
                    .where(SourceRuntimeWorkAttemptORM.run_id == run_id)
                    .order_by(SourceRuntimeWorkAttemptORM.started_at.asc(), SourceRuntimeWorkAttemptORM.attempt_id.asc())
                )
            )
            work_item_ids = [row.work_item_id for row in attempts]
            work_items = [
                item
                for item in (session.get(SourceRuntimeWorkItemORM, work_item_id) for work_item_id in work_item_ids)
                if item is not None
            ]
            return SourceDiscoveryRuntimeRunDetailResponse(
                run=_serialize_runtime_run(run),
                work_items=[_serialize_runtime_work_item(row) for row in work_items],
                failures=[_serialize_runtime_failure(row) for row in attempts if row.failure_kind],
                caveats=SOURCE_DISCOVERY_CAVEATS + [
                    "Run detail is replay-safe metadata only; it does not retry or re-fetch network resources.",
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
                        "seed_family": raw_seed.seed_family or request.default_seed_family,
                        "source_family_tags": sorted(set(raw_seed.source_family_tags + list(request.default_source_family_tags))),
                        "scope_hints": _merge_scope_hints(raw_seed.scope_hints, request.default_scope_hints),
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
                    .where(SourceDiscoveryJobORM.job_type.in_(["structure_scan", "feed_link_scan", "sitemap_scan", "catalog_scan", "archive_index_scan", "directory_scan", "locale_seed_expand", "link_graph_scan"]))
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
                elif _is_scheduler_link_graph_candidate(memory, now):
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

    def adversarial_overview(self, *, limit: int = 100) -> SourceDiscoveryAdversarialOverviewResponse:
        with session_scope(self._settings.source_discovery_database_url) as session:
            all_findings = list(
                session.scalars(
                    select(SourceAdversarialFindingORM)
                    .order_by(SourceAdversarialFindingORM.detected_at.desc(), SourceAdversarialFindingORM.finding_id.desc())
                )
            )
            open_findings = [row for row in all_findings if row.status == "open"]
            counts_by_risk_level: dict[str, int] = {}
            counts_by_signal_type: dict[str, int] = {}
            for row in open_findings:
                counts_by_risk_level[row.risk_level] = counts_by_risk_level.get(row.risk_level, 0) + 1
                counts_by_signal_type[row.signal_type] = counts_by_signal_type.get(row.signal_type, 0) + 1
            flagged_source_count = sum(
                1
                for _ in session.scalars(
                    select(SourceMemoryORM.source_id).where(SourceMemoryORM.adversarial_signal_count > 0)
                )
            )
            high_risk_source_count = sum(
                1
                for _ in session.scalars(
                    select(SourceMemoryORM.source_id).where(SourceMemoryORM.adversarial_risk_level == "high")
                )
            )
            recent_findings = all_findings[: max(0, limit)]
            return SourceDiscoveryAdversarialOverviewResponse(
                metadata={"source": "source-discovery-adversarial-overview", "count": len(recent_findings)},
                total_finding_count=len(all_findings),
                open_finding_count=len(open_findings),
                flagged_source_count=flagged_source_count,
                high_risk_source_count=high_risk_source_count,
                counts_by_risk_level=counts_by_risk_level,
                counts_by_signal_type=counts_by_signal_type,
                recent_findings=[_serialize_adversarial_finding(row) for row in recent_findings],
                caveats=SOURCE_DISCOVERY_CAVEATS + [
                    "Adversarial findings are untrusted-content safety metadata only; they do not prove malicious ownership or claim falsity.",
                ],
            )

    def adversarial_findings(
        self,
        *,
        limit: int = 100,
        source_id: str | None = None,
        risk_level: str | None = None,
        status: str | None = "open",
    ) -> SourceDiscoveryAdversarialFindingsResponse:
        with session_scope(self._settings.source_discovery_database_url) as session:
            stmt = select(SourceAdversarialFindingORM).order_by(
                SourceAdversarialFindingORM.detected_at.desc(),
                SourceAdversarialFindingORM.finding_id.desc(),
            )
            if source_id:
                stmt = stmt.where(SourceAdversarialFindingORM.source_id == source_id)
            if risk_level:
                stmt = stmt.where(SourceAdversarialFindingORM.risk_level == risk_level)
            if status:
                stmt = stmt.where(SourceAdversarialFindingORM.status == status)
            findings = list(session.scalars(stmt.limit(max(0, limit))))
            return SourceDiscoveryAdversarialFindingsResponse(
                metadata={
                    "source": "source-discovery-adversarial-findings",
                    "count": len(findings),
                    "sourceId": source_id,
                    "riskLevel": risk_level,
                    "status": status,
                },
                findings=[_serialize_adversarial_finding(row) for row in findings],
                caveats=SOURCE_DISCOVERY_CAVEATS + [
                    "Adversarial finding feeds are review surfaces, not source-validation proof.",
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
                is_eligible = (
                    _is_scheduler_structure_scan_candidate(memory)
                    or _is_scheduler_public_discovery_candidate(memory, now)
                    or _is_scheduler_link_graph_candidate(memory, now)
                )
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
                    locale_expansion_basis=_loads_list(memory.locale_expansion_basis_json),
                    discovered_from_provider=memory.discovered_from_provider,
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
                    adversarial_risk_level=memory.adversarial_risk_level,  # type: ignore[arg-type]
                    adversarial_signal_count=int(memory.adversarial_signal_count or 0),
                    adversarial_signals=_loads_list(memory.adversarial_signals_json),
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
                    .where(SourceDiscoveryJobORM.job_type.in_(["structure_scan", "feed_link_scan", "sitemap_scan", "catalog_scan", "archive_index_scan", "directory_scan", "locale_seed_expand", "link_graph_scan"]))
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
            session.flush()
            _refresh_event_graph(
                session,
                source_ids=[request.source_id],
                wave_ids=[request.wave_id] if request.wave_id else [],
                knowledge_node_ids=[],
                include_pending_claims=False,
                mode="recompute_selected",
                max_events=50,
                now=now,
            )
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

    def run_archive_index_scan_job(
        self,
        request: SourceDiscoveryArchiveIndexScanRequest,
    ) -> SourceDiscoveryArchiveIndexScanResponse:
        now = _utc_now()
        normalized_host = _normalize_archive_target_host(request.target_host)
        seed_url = _archive_seed_url(normalized_host, request.url_prefix)
        job_id = f"source-archive-index-scan:{request.provider}:{_safe_id(seed_url or request.target_host)}:{_compact_timestamp(now)}"
        caveats = list(request.caveats)
        if normalized_host is None:
            job = SourceDiscoveryJobORM(
                job_id=job_id,
                job_type="archive_index_scan",
                status="rejected",
                seed_url=seed_url or request.target_host,
                wave_id=request.wave_id,
                wave_title=request.wave_title,
                discovered_source_ids_json=json.dumps([]),
                rejected_reason="Archive index targetHost must resolve to a public host name.",
                request_budget=max(0, request.request_budget),
                used_requests=0,
                started_at=now,
                finished_at=now,
                outcome_summary="Rejected archive-index scan before any provider lookup ran.",
                caveats_json=json.dumps(["Rejected before archive provider parsing or candidate creation."]),
            )
            with session_scope(self._settings.source_discovery_database_url) as session:
                session.add(job)
                session.flush()
                return SourceDiscoveryArchiveIndexScanResponse(
                    job=_serialize_job(job),
                    provider=request.provider,
                    discovered_capture_count=0,
                    discovered_candidate_count=0,
                    memories=[],
                    caveats=SOURCE_DISCOVERY_CAVEATS,
                )

        used_requests = 0
        try:
            if request.fixture_text is not None:
                document = request.fixture_text
            elif request.request_budget > 0:
                document, used_requests = _fetch_archive_index_document(request, normalized_host)
            else:
                raise ValueError("Archive index scan requires fixture_text or request_budget > 0.")
            records = _parse_archive_index_records(
                provider=request.provider,
                text=document,
                target_host=normalized_host,
                url_prefix=request.url_prefix,
                max_results=max(0, request.max_results),
            )
        except Exception as exc:  # noqa: BLE001
            job = SourceDiscoveryJobORM(
                job_id=job_id,
                job_type="archive_index_scan",
                status="failed",
                seed_url=seed_url or request.target_host,
                wave_id=request.wave_id,
                wave_title=request.wave_title,
                discovered_source_ids_json=json.dumps([]),
                rejected_reason=str(exc)[:300],
                request_budget=max(0, request.request_budget),
                used_requests=used_requests,
                started_at=now,
                finished_at=now,
                outcome_summary=f"Archive index parsing failed: {str(exc)[:160]}",
                caveats_json=json.dumps(caveats + [
                    "Archive index parsing failed; no candidates were created.",
                ]),
            )
            with session_scope(self._settings.source_discovery_database_url) as session:
                session.add(job)
                session.flush()
                return SourceDiscoveryArchiveIndexScanResponse(
                    job=_serialize_job(job),
                    provider=request.provider,
                    discovered_capture_count=0,
                    discovered_candidate_count=0,
                    memories=[],
                    caveats=SOURCE_DISCOVERY_CAVEATS,
                )

        seed_records: list[tuple[SourceDiscoveryCandidateSeed, _ArchiveDiscoveryRecord]] = []
        for record in records:
            target_url = record.original_url or record.archive_url
            if not target_url or _discovery_target_requires_auth_or_captcha(target_url):
                continue
            canonical_url = _canonical_source_url(target_url)
            seed = _candidate_seed_from_extracted_url(
                url=canonical_url,
                source_id=_generated_source_id_for_url(canonical_url),
                title=urlparse(canonical_url).netloc or normalized_host,
                wave_id=request.wave_id,
                wave_title=request.wave_title,
                discovery_reason=f"archive index scan via {request.provider}",
                caveats=[
                    "Archive index discovery is candidate/review infrastructure only and does not fetch archived page bodies in this slice.",
                    "Archive captures are provenance signals, not trust or validation proof.",
                    _archive_record_caveat(record),
                ] + caveats,
                discovery_methods=["archive_index_scan"],
                structure_hints=["archive_index_result"],
            )
            if seed is not None:
                seed_records.append((seed, record))

        with session_scope(self._settings.source_discovery_database_url) as session:
            novel_candidate_count = _count_novel_candidate_seeds(session, [seed for seed, _ in seed_records])
            memories: list[SourceMemoryORM] = []
            for seed, record in seed_records:
                memory = _upsert_candidate_row(session, seed, now=now)
                _upsert_archive_hit_row(
                    session,
                    source_id=memory.source_id,
                    record=record,
                    now=now,
                    caveats=[
                        "Archive hit provenance is source-discovery context only and does not validate article truth.",
                    ] + caveats,
                )
                memories.append(memory)
            outcome_summary = (
                f"Archive index scan parsed {len(records)} captures and produced {novel_candidate_count} novel candidates."
            )
            job = SourceDiscoveryJobORM(
                job_id=job_id,
                job_type="archive_index_scan",
                status="completed",
                seed_url=seed_url or request.target_host,
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
                    "Archive index scan is bounded and candidate-only; it records archive provenance without fetching archived page bodies.",
                ]),
            )
            session.add(job)
            session.flush()
            context = _build_discovery_priority_context(session)
            return SourceDiscoveryArchiveIndexScanResponse(
                job=_serialize_job(job),
                provider=request.provider,
                discovered_capture_count=len(records),
                discovered_candidate_count=len(memories),
                memories=[_serialize_memory(session, memory, context=context) for memory in memories],
                caveats=SOURCE_DISCOVERY_CAVEATS,
            )

    def run_directory_scan_job(
        self,
        request: SourceDiscoveryDirectoryScanRequest,
    ) -> SourceDiscoveryDirectoryScanResponse:
        now = _utc_now()
        parsed = urlparse(request.directory_url)
        job_id = f"source-directory-scan:{_safe_id(request.directory_url)}:{_compact_timestamp(now)}"
        caveats = list(request.caveats)
        packet_caveats = list(request.packet_caveats)
        if request.packet_provenance:
            packet_caveats.append(f"Seed packet provenance: {request.packet_provenance}")
        if request.imported_by:
            packet_caveats.append(f"Seed packet imported by: {request.imported_by}")
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            job = SourceDiscoveryJobORM(
                job_id=job_id,
                job_type="directory_scan",
                status="rejected",
                seed_url=request.directory_url,
                wave_id=request.wave_id,
                wave_title=request.wave_title,
                discovered_source_ids_json=json.dumps([]),
                rejected_reason="Directory URL must be an absolute http(s) URL.",
                request_budget=max(0, request.request_budget),
                used_requests=0,
                started_at=now,
                finished_at=now,
                outcome_summary="Rejected invalid directory URL before any discovery work ran.",
                caveats_json=json.dumps(["Rejected before directory parsing or candidate creation."]),
            )
            with session_scope(self._settings.source_discovery_database_url) as session:
                session.add(job)
                session.flush()
                return SourceDiscoveryDirectoryScanResponse(
                    job=_serialize_job(job),
                    directory_type=request.directory_type,
                    extracted_url_count=0,
                    discovered_domain_count=0,
                    memories=[],
                    caveats=SOURCE_DISCOVERY_CAVEATS,
                )

        used_requests = 0
        try:
            if request.fixture_text is not None:
                document = request.fixture_text
            elif request.request_budget > 0:
                fetched = _fetch_url(request.directory_url, method="GET", max_bytes=MAX_FETCH_BYTES)
                document = str(fetched["body"])
                used_requests = 1
            else:
                raise ValueError("Directory scan requires fixture_text or request_budget > 0.")
            directory_urls, resolved_directory_type, discovered_domain_count = _extract_directory_candidate_urls(
                request.directory_url,
                document,
                directory_type=request.directory_type,
                max_external_domains=max(0, request.max_external_domains),
                max_discovered=max(0, request.max_discovered),
            )
        except Exception as exc:  # noqa: BLE001
            job = SourceDiscoveryJobORM(
                job_id=job_id,
                job_type="directory_scan",
                status="failed",
                seed_url=request.directory_url,
                wave_id=request.wave_id,
                wave_title=request.wave_title,
                discovered_source_ids_json=json.dumps([]),
                rejected_reason=str(exc)[:300],
                request_budget=max(0, request.request_budget),
                used_requests=used_requests,
                started_at=now,
                finished_at=now,
                outcome_summary=f"Directory parsing failed: {str(exc)[:160]}",
                caveats_json=json.dumps(caveats + [
                    "Directory parsing failed; no candidates were created.",
                ]),
            )
            with session_scope(self._settings.source_discovery_database_url) as session:
                session.add(job)
                session.flush()
                return SourceDiscoveryDirectoryScanResponse(
                    job=_serialize_job(job),
                    directory_type=request.directory_type,
                    extracted_url_count=0,
                    discovered_domain_count=0,
                    memories=[],
                    caveats=SOURCE_DISCOVERY_CAVEATS,
                )

        seeds: list[SourceDiscoveryCandidateSeed] = []
        for url in directory_urls:
            normalized_url = _normalize_directory_seed_target(url)
            seed = _candidate_seed_from_extracted_url(
                url=normalized_url,
                source_id=_generated_source_id_for_url(normalized_url),
                title=urlparse(normalized_url).netloc or parsed.netloc,
                wave_id=request.wave_id,
                wave_title=request.wave_title,
                discovery_reason=request.discovery_reason,
                caveats=[
                    "Directory scan is bounded to one visible public directory page and creates review-only roots or candidates.",
                    "Curated directory membership is explainability metadata only and does not validate a source.",
                ] + caveats + packet_caveats,
                discovery_methods=["directory_scan"],
                structure_hints=["directory_link"],
            )
            if seed is None:
                continue
            merged_tags = sorted(set(seed.source_family_tags + list(request.source_family_tags)))
            merged_scope_hints = _merge_scope_hints(seed.scope_hints, request.scope_hints)
            derived_seed_family = request.seed_family
            if derived_seed_family is None and set(merged_tags).intersection({"regional", "local_news"}):
                derived_seed_family = "regional_outlet"
            elif derived_seed_family is None and "official" in merged_tags:
                derived_seed_family = "official_bulletin"
            seeds.append(
                seed.model_copy(
                    update={
                        "seed_family": derived_seed_family,
                        "source_family_tags": merged_tags,
                        "scope_hints": merged_scope_hints,
                        "seed_packet_id": request.packet_id,
                        "seed_packet_title": request.packet_title,
                        "discovery_role": "root",
                    }
                )
            )

        with session_scope(self._settings.source_discovery_database_url) as session:
            novel_candidate_count = _count_novel_candidate_seeds(session, seeds)
            memories = [_upsert_candidate_row(session, seed, now=now) for seed in seeds]
            outcome_summary = (
                f"Directory scan extracted {len(directory_urls)} public links across {discovered_domain_count} domains and produced {novel_candidate_count} novel candidates."
            )
            job = SourceDiscoveryJobORM(
                job_id=job_id,
                job_type="directory_scan",
                status="completed",
                seed_url=request.directory_url,
                wave_id=request.wave_id,
                wave_title=request.wave_title,
                discovered_source_ids_json=json.dumps([memory.source_id for memory in memories]),
                rejected_reason=None,
                request_budget=max(0, request.request_budget),
                used_requests=used_requests,
                started_at=now,
                finished_at=now,
                outcome_summary=outcome_summary,
                caveats_json=json.dumps(caveats + packet_caveats + [
                    "Directory scan is bounded to visible outbound public links and does not crawl discovered domains.",
                ]),
            )
            session.add(job)
            session.flush()
            context = _build_discovery_priority_context(session)
            return SourceDiscoveryDirectoryScanResponse(
                job=_serialize_job(job),
                directory_type=resolved_directory_type,  # type: ignore[arg-type]
                extracted_url_count=len(directory_urls),
                discovered_domain_count=discovered_domain_count,
                memories=[_serialize_memory(session, memory, context=context) for memory in memories],
                caveats=SOURCE_DISCOVERY_CAVEATS,
            )

    def run_locale_seed_expand_job(
        self,
        request: SourceDiscoveryLocaleSeedExpandRequest,
    ) -> SourceDiscoveryLocaleSeedExpandResponse:
        now = _utc_now()
        job_id = f"source-locale-seed-expand:{_compact_timestamp(now)}"
        caveats = list(request.caveats)
        packet_caveats = list(caveats)
        if request.packet_provenance:
            packet_caveats.append(f"Seed packet provenance: {request.packet_provenance}")
        if request.imported_by:
            packet_caveats.append(f"Seed packet imported by: {request.imported_by}")
        raw_terms = [term for term in [*request.seed_terms, *request.aliases] if str(term).strip()]
        if not raw_terms:
            job = SourceDiscoveryJobORM(
                job_id=job_id,
                job_type="locale_seed_expand",
                status="rejected",
                seed_url=None,
                wave_id=request.wave_id,
                wave_title=request.wave_title,
                discovered_source_ids_json=json.dumps([]),
                rejected_reason="Locale seed expansion requires at least one seed term or alias.",
                request_budget=max(0, request.request_budget),
                used_requests=0,
                started_at=now,
                finished_at=now,
                outcome_summary="Rejected locale seed expansion before any provider lookup ran.",
                caveats_json=json.dumps(caveats),
            )
            with session_scope(self._settings.source_discovery_database_url) as session:
                session.add(job)
                session.flush()
                return SourceDiscoveryLocaleSeedExpandResponse(
                    job=_serialize_job(job),
                    caveats=SOURCE_DISCOVERY_CAVEATS,
                )

        scope_hints = _merge_scope_hints(
            request.scope_hints,
            SourceDiscoveryScopeHints(
                spatial=sorted({label.strip() for label in request.place_labels if label.strip()}),
                language=sorted({code.strip().casefold() for code in request.language_codes if code.strip()}),
            ),
        )
        generated_aliases = _generate_locale_aliases(raw_terms)
        generated_queries = _build_locale_queries(
            generated_aliases,
            country_codes=request.country_codes,
            language_codes=request.language_codes,
            max_queries=max(0, request.max_queries),
        )
        provider_runs: list[SourceDiscoveryLocaleExpansionProviderRunSummary] = []
        seed_records: list[SourceDiscoveryCandidateSeed] = []
        used_requests = 0
        locale_basis = _locale_basis_lines(
            generated_aliases=generated_aliases,
            country_codes=request.country_codes,
            language_codes=request.language_codes,
            place_labels=request.place_labels,
        )

        if "deterministic" in request.providers:
            provider_runs.append(
                SourceDiscoveryLocaleExpansionProviderRunSummary(
                    provider="deterministic",
                    query_count=len(generated_queries),
                    raw_result_count=0,
                    discovered_count=0,
                    status="completed",
                    caveats=["Deterministic locale expansion generated bounded aliases and queries only."],
                )
            )

        if "gdelt_doc" in request.providers:
            gdelt_queries = generated_queries[: max(0, request.max_queries)]
            gdelt_candidates: list[dict[str, str]] = []
            provider_caveats: list[str] = []
            attempted_queries = 0
            fixture_payload = request.fixture_provider_payloads.get("gdelt_doc")
            if fixture_payload is not None:
                attempted_queries = 1 if gdelt_queries else 0
                gdelt_candidates = _parse_gdelt_doc_candidates(fixture_payload, max_hits=max(0, request.max_provider_hits))
            elif request.request_budget > 0 and gdelt_queries:
                for query in gdelt_queries:
                    if len(gdelt_candidates) >= max(0, request.max_provider_hits):
                        break
                    if used_requests >= max(0, request.request_budget):
                        provider_caveats.append("GDELT DOC query budget was exhausted before all locale queries ran.")
                        break
                    attempted_queries += 1
                    payload = _fetch_gdelt_doc_payload(query, max_records=max(1, min(request.max_provider_hits, 50)))
                    used_requests += 1
                    gdelt_candidates.extend(
                        _parse_gdelt_doc_candidates(
                            payload,
                            max_hits=max(0, request.max_provider_hits),
                        )
                    )
            else:
                provider_caveats.append("GDELT DOC provider was skipped because no fixture payload or live request budget was provided.")

            seed_records = _locale_candidate_seeds_from_provider_results(
                gdelt_candidates,
                wave_id=request.wave_id,
                wave_title=request.wave_title,
                packet_id=request.packet_id,
                packet_title=request.packet_title,
                source_family_tags=request.source_family_tags,
                scope_hints=scope_hints,
                locale_basis=locale_basis,
                max_domains=max(0, request.max_domains),
                max_discovered=max(0, request.max_discovered),
                base_caveats=packet_caveats + [
                    "Locale/provider expansion is bounded discovery only and does not validate matched articles or outlets.",
                ],
            )
            provider_runs.append(
                SourceDiscoveryLocaleExpansionProviderRunSummary(
                    provider="gdelt_doc",
                    query_count=attempted_queries,
                    raw_result_count=len(gdelt_candidates),
                    discovered_count=len(seed_records),
                    status="completed" if fixture_payload is not None or attempted_queries > 0 else "skipped",
                    caveats=provider_caveats,
                )
            )

        with session_scope(self._settings.source_discovery_database_url) as session:
            memories = [_upsert_candidate_row(session, seed, now=now) for seed in seed_records]
            discovered_domain_count = len({memory.parent_domain for memory in memories if memory.parent_domain})
            outcome_summary = (
                f"Locale seed expansion generated {len(generated_aliases)} aliases, ran {sum(run.query_count for run in provider_runs)} queries, and created {len(memories)} discovery roots."
            )
            job = SourceDiscoveryJobORM(
                job_id=job_id,
                job_type="locale_seed_expand",
                status="completed",
                seed_url=None,
                wave_id=request.wave_id,
                wave_title=request.wave_title,
                discovered_source_ids_json=json.dumps([memory.source_id for memory in memories]),
                rejected_reason=None,
                request_budget=max(0, request.request_budget),
                used_requests=used_requests,
                started_at=now,
                finished_at=now,
                outcome_summary=outcome_summary,
                caveats_json=json.dumps(packet_caveats + [
                    "Locale expansion stays bounded to explicit user-provided terms, locales, and public provider results.",
                    "No open-ended machine translation or generic search scraping is used in this slice.",
                ]),
            )
            session.add(job)
            session.flush()
            context = _build_discovery_priority_context(session)
            return SourceDiscoveryLocaleSeedExpandResponse(
                job=_serialize_job(job),
                generated_aliases=generated_aliases,
                generated_queries=generated_queries,
                provider_runs=provider_runs,
                discovered_domain_count=discovered_domain_count,
                memories=[_serialize_memory(session, memory, context=context) for memory in memories],
                caveats=SOURCE_DISCOVERY_CAVEATS,
            )

    def run_link_graph_scan_job(
        self,
        request: SourceDiscoveryLinkGraphScanRequest,
    ) -> SourceDiscoveryLinkGraphScanResponse:
        now = _utc_now()
        job_id = f"source-link-graph-scan:{_safe_id(request.source_id)}:{_compact_timestamp(now)}"
        caveats = list(request.caveats)
        with session_scope(self._settings.source_discovery_database_url) as session:
            memory = session.get(SourceMemoryORM, request.source_id)
            if memory is None:
                raise ValueError(f"Unknown source_id: {request.source_id}")
            if not _is_link_graph_scan_allowed(memory):
                job = SourceDiscoveryJobORM(
                    job_id=job_id,
                    job_type="link_graph_scan",
                    status="rejected",
                    seed_url=memory.url,
                    wave_id=None,
                    wave_title=None,
                    discovered_source_ids_json=json.dumps([memory.source_id]),
                    rejected_reason="Link-graph scan requires a reviewed or approved public no-auth root.",
                    request_budget=max(0, request.request_budget),
                    used_requests=0,
                    started_at=now,
                    finished_at=now,
                    outcome_summary="Rejected link-graph scan before any fetch or extraction ran.",
                    caveats_json=json.dumps(caveats),
                )
                session.add(job)
                session.flush()
                return SourceDiscoveryLinkGraphScanResponse(
                    job=_serialize_job(job),
                    caveats=SOURCE_DISCOVERY_CAVEATS,
                )
            best_fit = _best_wave_fit(_fits_for_source(session, memory.source_id))
            seed_url = memory.url
            source_scope_hints = _loads_scope_hints(memory.scope_hints_json)

        used_requests = 0
        if request.fixture_text is not None:
            document = request.fixture_text
        elif request.request_budget > 0:
            fetched = _fetch_url(seed_url, method="GET", max_bytes=MAX_FETCH_BYTES)
            document = str(fetched["body"])
            used_requests = 1
        else:
            raise ValueError("Link-graph scan requires fixture_text or request_budget > 0.")

        candidate_urls, extracted_url_count, discovered_domain_count, page_hints = _extract_link_graph_candidate_urls(
            seed_url,
            document,
            max_same_domain=max(0, request.max_same_domain),
            max_external_domains=max(0, request.max_external_domains),
            max_discovered=max(0, request.max_discovered),
        )

        seeds: list[SourceDiscoveryCandidateSeed] = []
        for target_url in candidate_urls:
            seed = _candidate_seed_from_extracted_url(
                url=target_url,
                source_id=_generated_source_id_for_url(target_url),
                title=urlparse(target_url).netloc or target_url,
                wave_id=best_fit.wave_id if best_fit else None,
                wave_title=best_fit.wave_title if best_fit else None,
                discovery_reason="trusted public root link-graph expansion",
                caveats=caveats + [
                    "Link-graph expansion is bounded to one reviewed public root page and root-like outbound links only.",
                    f"Discovered via trusted root {seed_url}.",
                ],
                discovery_methods=["link_graph_scan"],
                structure_hints=sorted(set(["linked_root_candidate", "trusted_root_link_graph", *page_hints])),
            )
            if seed is None:
                continue
            seeds.append(
                seed.model_copy(
                    update={
                        "discovery_role": "root",
                        "scope_hints": source_scope_hints,
                    }
                )
            )

        with session_scope(self._settings.source_discovery_database_url) as session:
            root_memory = session.get(SourceMemoryORM, request.source_id)
            if root_memory is None:
                raise ValueError(f"Unknown source_id: {request.source_id}")
            novel_candidate_count = _count_novel_candidate_seeds(session, seeds)
            memories = [_upsert_candidate_row(session, seed, now=now) for seed in seeds]
            outcome_summary = (
                f"Link-graph scan extracted {extracted_url_count} outbound links and produced {novel_candidate_count} novel root candidates."
            )
            _apply_public_discovery_scan_success_for_url(
                session,
                root_memory.url,
                now=now,
                scan_kind="link_graph_scan",
                outcome_summary=outcome_summary,
                novel_candidate_count=novel_candidate_count,
            )
            job = SourceDiscoveryJobORM(
                job_id=job_id,
                job_type="link_graph_scan",
                status="completed",
                seed_url=root_memory.url,
                wave_id=best_fit.wave_id if best_fit else None,
                wave_title=best_fit.wave_title if best_fit else None,
                discovered_source_ids_json=json.dumps([memory.source_id for memory in memories]),
                rejected_reason=None,
                request_budget=max(0, request.request_budget),
                used_requests=used_requests,
                started_at=now,
                finished_at=now,
                outcome_summary=outcome_summary,
                caveats_json=json.dumps(caveats + [
                    "Link-graph scan does not recurse and does not fetch discovered children in this slice.",
                ]),
            )
            session.add(job)
            session.flush()
            context = _build_discovery_priority_context(session)
            return SourceDiscoveryLinkGraphScanResponse(
                job=_serialize_job(job),
                discovered_domain_count=discovered_domain_count,
                extracted_url_count=extracted_url_count,
                memories=[_serialize_memory(session, memory, context=context) for memory in memories],
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
        adversarial_findings = _detect_adversarial_findings(html_text or "", url=request.target_url)

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
            if adversarial_findings:
                _record_adversarial_findings(
                    session,
                    source_id=root_memory.source_id,
                    snapshot_id=None,
                    job_id=job_id,
                    surface_type="structure_scan",
                    findings=adversarial_findings,
                    now=now,
                )
                _apply_adversarial_hold_review(root_memory, adversarial_findings)
            else:
                _refresh_adversarial_posture(session, source_id=root_memory.source_id, snapshot_id=None, now=now)
            child_memories = [_upsert_candidate_row(session, seed, now=now) for seed in child_seeds]
            outcome_summary = (
                f"Structure scan found {len(child_memories)} candidate surfaces and {novel_candidate_count} novel root or child candidates."
            )
            if adversarial_findings:
                outcome_summary += f" Flagged {len(adversarial_findings)} adversarial or prompt-injection signals for review."
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
            retrieval_origin = request.retrieval_origin
            retrieved_from_url = request.retrieved_from_url
            resolved_original_url = request.resolved_original_url
            detected_language = request.detected_language
            normalization_notes = list(request.normalization_notes)
            detection_document = request.raw_text or request.html_text or ""
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
                resolved_original_url = resolved_original_url or article_snapshot.canonical_url or url
                detected_language = detected_language or _detect_language_hint(
                    request.html_text,
                    candidate_url=resolved_original_url or url,
                )
            elif request.request_budget > 0:
                fetched = _fetch_url(url, method="GET", max_bytes=MAX_FETCH_BYTES)
                used_requests = 1
                content_type = fetched["content_type"]
                retrieved_from_url = retrieved_from_url or url
                detection_document = str(fetched["body"])
                if "html" in (content_type or "").lower():
                    article_snapshot = extract_article_snapshot_from_html(str(fetched["body"]), base_url=url)
                    full_text = article_snapshot.text
                    extraction_method = f"live_fetch_{article_snapshot.method}"
                    url = article_snapshot.canonical_url or url
                    title = title or article_snapshot.title
                    author = author or article_snapshot.author
                    published_at = published_at or article_snapshot.published_at
                    resolved_original_url = resolved_original_url or article_snapshot.canonical_url or url
                    detected_language = detected_language or _detect_language_hint(
                        str(fetched["body"]),
                        candidate_url=resolved_original_url or url,
                    )
                else:
                    full_text = str(fetched["body"])
                    extraction_method = "live_fetch"
                    detected_language = detected_language or _language_hint_from_url(url)
            else:
                full_text = ""
                extraction_method = "metadata_only"
                caveats.append("No raw/html text supplied and request budget was zero.")

            normalized_text = _normalize_text(full_text)
            adversarial_findings = _detect_adversarial_findings(
                detection_document or normalized_text,
                url=resolved_original_url or url,
            )
            if adversarial_findings:
                caveats.append("Captured content contains adversarial or prompt-injection signals and requires review-only handling.")
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
                retrieval_origin=retrieval_origin,
                retrieved_from_url=retrieved_from_url,
                resolved_original_url=resolved_original_url or url,
                detected_language=detected_language,
                adversarial_risk_level=_highest_adversarial_risk([finding["risk_level"] for finding in adversarial_findings]),
                adversarial_signal_count=len(adversarial_findings),
                adversarial_signals_json=json.dumps(sorted({finding["signal_type"] for finding in adversarial_findings})),
                caveats_json=json.dumps(caveats + [
                    "Full text is stored as source evidence input; it does not prove claims without assessment.",
                ]),
                normalization_notes_json=json.dumps(normalization_notes),
            )
            _assign_snapshot_to_knowledge_node(
                session,
                snapshot,
                memory=memory,
                normalized_text=normalized_text,
                now=now,
            )
            memory.last_seen_at = now
            if detected_language:
                memory.scope_hints_json = json.dumps(
                    _merge_scope_hints(
                        _loads_scope_hints(memory.scope_hints_json),
                        SourceDiscoveryScopeHints(language=[detected_language]),
                    ).model_dump()
                )
            memory.caveats_json = json.dumps(sorted(set(_loads_list(memory.caveats_json) + caveats)))
            session.merge(snapshot)
            session.flush()
            if adversarial_findings:
                _record_adversarial_findings(
                    session,
                    source_id=request.source_id,
                    snapshot_id=snapshot.snapshot_id,
                    job_id=None,
                    surface_type="content_snapshot",
                    findings=adversarial_findings,
                    now=now,
                )
            else:
                _refresh_adversarial_posture(session, source_id=request.source_id, snapshot_id=snapshot.snapshot_id, now=now)
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
        fetch_mode = request.fetch_mode
        if fetch_mode == "auto":
            if request.archive_hit_id or request.archive_url or request.fixture_archive_html is not None:
                fetch_mode = "archive"
            else:
                fetch_mode = "live"
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
            if (
                memory.policy_state == "blocked"
                or memory.lifecycle_state in {"rejected", "archived"}
                or (
                    memory.policy_state != "reviewed"
                    and memory.lifecycle_state not in {"approved-unvalidated", "sandboxed", "validated"}
                )
            ):
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
            archive_hit = session.get(SourceArchiveHitORM, request.archive_hit_id) if request.archive_hit_id else None
            if request.archive_hit_id and archive_hit is None:
                raise ValueError(f"Unknown archive_hit_id: {request.archive_hit_id}")
            source_url = memory.url
            archive_url = request.archive_url or (archive_hit.archive_url if archive_hit is not None else None)
            archive_original_url = archive_hit.original_url if archive_hit is not None else None

        snapshot_request: SourceDiscoveryContentSnapshotRequest
        prefetch_used_requests = 0
        if fetch_mode == "archive":
            if not request.fixture_archive_html and not archive_url:
                with session_scope(self._settings.source_discovery_database_url) as session:
                    memory = session.get(SourceMemoryORM, request.source_id)
                    if memory is None:
                        raise ValueError(f"Unknown source_id: {request.source_id}")
                    job = SourceDiscoveryJobORM(
                        job_id=job_id,
                        job_type="article_fetch",
                        status="rejected",
                        seed_url=memory.url,
                        wave_id=None,
                        wave_title=None,
                        discovered_source_ids_json=json.dumps([memory.source_id]),
                        rejected_reason="Archive fetch requires an explicit archiveHitId, archiveUrl, or fixtureArchiveHtml.",
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
            if archive_url and not _is_allowed_archive_fetch_url(archive_url):
                with session_scope(self._settings.source_discovery_database_url) as session:
                    memory = session.get(SourceMemoryORM, request.source_id)
                    if memory is None:
                        raise ValueError(f"Unknown source_id: {request.source_id}")
                    job = SourceDiscoveryJobORM(
                        job_id=job_id,
                        job_type="article_fetch",
                        status="rejected",
                        seed_url=archive_url,
                        wave_id=None,
                        wave_title=None,
                        discovered_source_ids_json=json.dumps([memory.source_id]),
                        rejected_reason="Archive fetch requires an explicit public capture URL from an allowed archive host.",
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
            if request.fixture_archive_html is not None:
                archive_html = request.fixture_archive_html
            elif request.request_budget > 0 and archive_url:
                fetched = _fetch_url(archive_url, method="GET", max_bytes=MAX_FETCH_BYTES)
                archive_html = str(fetched["body"])
                prefetch_used_requests = 1
            else:
                raise ValueError("Archive fetch requires fixtureArchiveHtml or request_budget > 0 with an explicit archive URL.")
            normalized_html, inferred_original_url, normalization_notes = _normalize_archive_capture_html(
                archive_html,
                archive_url or source_url,
            )
            resolved_original_url = archive_original_url or inferred_original_url or source_url
            snapshot_request = SourceDiscoveryContentSnapshotRequest(
                source_id=request.source_id,
                url=resolved_original_url,
                html_text=normalized_html,
                retrieval_origin="archive",
                retrieved_from_url=archive_url or source_url,
                resolved_original_url=resolved_original_url,
                detected_language=_detect_language_hint(normalized_html, candidate_url=resolved_original_url),
                normalization_notes=normalization_notes,
                request_budget=0,
                caveats=caveats + [
                    "Archive fetch is bounded to one explicit public capture and does not browse or follow archived links.",
                ],
            )
        else:
            snapshot_request = SourceDiscoveryContentSnapshotRequest(
                source_id=request.source_id,
                raw_text=request.fixture_text,
                html_text=request.fixture_html,
                retrieval_origin="live",
                retrieved_from_url=source_url,
                resolved_original_url=source_url,
                request_budget=request.request_budget if request.fixture_text is None and request.fixture_html is None else 0,
                caveats=caveats + [
                    "Article fetch is bounded to one approved or sandboxed source and stores evidence text only.",
                ],
            )

        snapshot_response = self.store_content_snapshot(
            snapshot_request
        )
        used_requests = prefetch_used_requests + snapshot_response.snapshot.used_requests
        with session_scope(self._settings.source_discovery_database_url) as session:
            job = SourceDiscoveryJobORM(
                job_id=job_id,
                job_type="article_fetch",
                status="completed",
                seed_url=snapshot_response.snapshot.retrieved_from_url or snapshot_response.snapshot.url,
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
                contested_event_count = _count_events_for_source_by_status(session, memory.source_id, {"contested", "corrected"})
                open_question_count = _count_events_for_source_by_status(session, memory.source_id, {"open_question"})
                reasons = _review_reasons(
                    memory,
                    best_fit=best_fit,
                    has_snapshot=has_snapshot,
                    pending_claim_count=len(pending_claims),
                    corrective_cluster=corrective_cluster,
                    unscanned_public_root=unscanned_public_root,
                    contested_event_count=contested_event_count,
                    open_question_count=open_question_count,
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
                    contested_event_count=contested_event_count,
                    open_question_count=open_question_count,
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
                            locale_expansion_basis=_loads_list(memory.locale_expansion_basis_json),
                            discovered_from_provider=memory.discovered_from_provider,
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
                            contested_event_count=contested_event_count,
                            open_question_count=open_question_count,
                            adversarial_risk_level=memory.adversarial_risk_level,  # type: ignore[arg-type]
                            adversarial_signal_count=int(memory.adversarial_signal_count or 0),
                            adversarial_signals=_loads_list(memory.adversarial_signals_json),
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
            _refresh_event_graph(
                session,
                source_ids=[source_id],
                wave_ids=[wave_id for wave_id in {candidate.wave_id for candidate in candidates if candidate.wave_id}],
                knowledge_node_ids=[candidate.knowledge_node_id for candidate in candidates if candidate.knowledge_node_id],
                include_pending_claims=False,
                mode="recompute_selected",
                max_events=100,
                now=now,
            )
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
        if self._settings.source_discovery_queue_enabled:
            return _run_scheduler_tick_queue(self, request)
        now = _utc_now()
        tick_id = f"source-scheduler:{_compact_timestamp(now)}"
        remaining_budget = max(0, request.request_budget)
        checks: list[SourceDiscoveryHealthCheckSummary] = []
        jobs: list[SourceDiscoveryJobSummary] = []
        llm_executions: list[WaveLlmExecutionSummary] = []
        structure_scans_completed = 0
        public_discovery_jobs_completed = 0
        link_graph_jobs_completed = 0
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
            eligible_link_graph_memories = [memory for memory in memories if _is_scheduler_link_graph_candidate(memory, now)]
            link_graph_memories = [
                {
                    "source_id": memory.source_id,
                }
                for memory in sorted(
                    eligible_link_graph_memories,
                    key=lambda item: (
                        -_compute_discovery_priority(session, item, now=now, context=discovery_context)[0],
                        -((discovery_context.best_fit_by_source_id.get(item.source_id).fit_score) if discovery_context.best_fit_by_source_id.get(item.source_id) else 0.0),
                        item.title.casefold(),
                    ),
                )
            ][: max(0, request.link_graph_job_limit)]

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

        for memory in link_graph_memories:
            per_job_budget = 1 if remaining_budget > 0 else 0
            if per_job_budget <= 0 and request.request_budget > 0:
                break
            remaining_budget = max(0, remaining_budget - per_job_budget)
            response = self.run_link_graph_scan_job(
                SourceDiscoveryLinkGraphScanRequest(
                    source_id=str(memory["source_id"]),
                    request_budget=per_job_budget,
                    caveats=["Scheduler-triggered bounded trusted-root link-graph expansion."],
                )
            )
            jobs.append(response.job)
            link_graph_jobs_completed += 1

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
                link_graph_jobs_requested=max(0, request.link_graph_job_limit),
                link_graph_jobs_completed=link_graph_jobs_completed,
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
            link_graph_jobs_completed=link_graph_jobs_completed,
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


def _run_scheduler_tick_queue(
    service: SourceDiscoveryService,
    request: SourceDiscoverySchedulerTickRequest,
) -> SourceDiscoverySchedulerTickResponse:
    now = _utc_now()
    tick_id = f"source-scheduler-queue:{_compact_timestamp(now)}"
    active_shard_id = f"{service._settings.source_discovery_shard_index}/{max(1, service._settings.source_discovery_shard_count)}"
    caveats = list(request.caveats) + [
        "Queue-backed scheduler tick is bounded and review-only.",
        "Queue replay surfaces expose recorded decisions only; they do not re-execute network work.",
    ]
    queued_work_items = 0
    executed_work_items = 0
    retry_scheduled_items = 0
    budget_blocked_items = 0
    dead_lettered_items = 0
    checks: list[SourceDiscoveryHealthCheckSummary] = []
    jobs: list[SourceDiscoveryJobSummary] = []
    llm_executions: list[WaveLlmExecutionSummary] = []
    structure_scans_completed = 0
    public_discovery_jobs_completed = 0
    link_graph_jobs_completed = 0
    expansion_jobs_completed = 0
    knowledge_backfill_jobs_completed = 0
    record_extract_jobs_completed = 0
    duplicate_snapshots_skipped = 0

    with session_scope(service._settings.source_discovery_database_url) as session:
        run = RuntimeSchedulerRunORM(
            run_id=tick_id,
            worker_name="source_discovery",
            trigger_kind="api_tick",
            status="running",
            requested_by="scheduler/tick",
            lease_owner=tick_id,
            started_at=now,
            finished_at=None,
            summary=None,
            error_summary=None,
        )
        session.add(run)
        queue_specs = _build_queue_specs(session, request, now=now)
        for spec in queue_specs:
            item, created = _queue_runtime_work_item(session, service._settings, spec=spec, now=now)
            if created:
                queued_work_items += 1
        session.flush()

    remaining_budget = max(0, request.request_budget)
    execute_limit = min(
        max(0, service._settings.source_discovery_per_tick_execute_limit),
        max(0, request.health_check_limit + request.structure_scan_limit + request.public_discovery_job_limit + request.link_graph_job_limit + request.expansion_job_limit + request.knowledge_backfill_limit + request.record_source_extract_limit),
    )
    if execute_limit <= 0:
        execute_limit = max(0, service._settings.source_discovery_per_tick_execute_limit)
    work_items_to_run: list[str] = []
    with session_scope(service._settings.source_discovery_database_url) as session:
        items = list(
            session.scalars(
                select(SourceRuntimeWorkItemORM)
                .where(
                    SourceRuntimeWorkItemORM.worker_name == "source_discovery",
                    SourceRuntimeWorkItemORM.status.in_(["queued", "retry_scheduled", "skipped_budget"]),
                )
                .order_by(SourceRuntimeWorkItemORM.priority_score.desc(), SourceRuntimeWorkItemORM.next_run_at.asc(), SourceRuntimeWorkItemORM.created_at.asc())
                .limit(max(0, execute_limit or service._settings.source_discovery_per_tick_execute_limit or 50) * 4)
            )
        )
        for item in items:
            if _parse_utc_like(item.next_run_at) and _parse_utc_like(item.next_run_at) > _parse_utc_like(now):
                continue
            if item.shard_index != service._settings.source_discovery_shard_index:
                continue
            work_items_to_run.append(item.work_item_id)
            if len(work_items_to_run) >= max(0, execute_limit or service._settings.source_discovery_per_tick_execute_limit or 50):
                break

    for work_item_id in work_items_to_run:
        with session_scope(service._settings.source_discovery_database_url) as session:
            item = session.get(SourceRuntimeWorkItemORM, work_item_id)
            if item is None:
                continue
            if item.status not in {"queued", "retry_scheduled", "skipped_budget"}:
                continue
            domain_limit = service._settings.source_discovery_per_domain_request_budget
            provider_limit = service._settings.source_discovery_per_provider_request_budget
            if remaining_budget <= 0 and request.request_budget > 0:
                item.status = "skipped_budget"
                item.next_run_at = _isoformat_utc(_parse_utc_like(now) + timedelta(minutes=15))
                item.updated_at = now
                budget_blocked_items += 1
                continue
            if item.domain_key and not _runtime_budget_has_capacity(session, scope="domain", key=item.domain_key, request_limit=domain_limit, needed=max(1, item.request_budget), now=now):
                item.status = "skipped_budget"
                item.last_failure_kind = "budget_exhausted"
                item.next_run_at = _isoformat_utc(_parse_utc_like(now) + timedelta(minutes=15))
                item.updated_at = now
                budget_blocked_items += 1
                continue
            if item.provider_key and not _runtime_budget_has_capacity(session, scope="provider", key=item.provider_key, request_limit=provider_limit, needed=max(1, item.request_budget), now=now):
                item.status = "skipped_budget"
                item.last_failure_kind = "budget_exhausted"
                item.next_run_at = _isoformat_utc(_parse_utc_like(now) + timedelta(minutes=15))
                item.updated_at = now
                budget_blocked_items += 1
                continue
            attempt = SourceRuntimeWorkAttemptORM(
                work_item_id=item.work_item_id,
                run_id=tick_id,
                job_type=item.job_type,
                status="running",
                failure_kind=None,
                source_id=item.source_id,
                domain_key=item.domain_key,
                provider_key=item.provider_key,
                attempt_index=item.attempt_count + 1,
                started_at=now,
                finished_at=None,
                used_requests=0,
                summary=None,
                error_summary=None,
                caveats_json=item.caveats_json,
            )
            session.add(attempt)
            item.status = "running"
            item.lease_owner = tick_id
            item.lease_expires_at = _isoformat_utc(_parse_utc_like(now) + timedelta(seconds=max(30, service._settings.source_discovery_work_item_lease_seconds)))
            item.updated_at = now
            item.attempt_count += 1
            session.flush()

        try:
            result = _execute_runtime_work_item(service, work_item_id, tick_id=tick_id)
            executed_work_items += 1
            remaining_budget = max(0, remaining_budget - result["used_requests"])
            if result["health_check"] is not None:
                checks.append(result["health_check"])  # type: ignore[arg-type]
            if result["job"] is not None:
                jobs.append(result["job"])  # type: ignore[arg-type]
                if result["job_type"] == "structure_scan":
                    structure_scans_completed += 1
                elif result["job_type"] in {"feed_link_scan", "sitemap_scan", "catalog_scan"}:
                    public_discovery_jobs_completed += 1
                elif result["job_type"] == "link_graph_scan":
                    link_graph_jobs_completed += 1
                elif result["job_type"] == "expand":
                    expansion_jobs_completed += 1
                elif result["job_type"] == "knowledge_backfill":
                    knowledge_backfill_jobs_completed += 1
                elif result["job_type"] == "record_source_extract":
                    record_extract_jobs_completed += 1
        except Exception as exc:  # noqa: BLE001
            failure_kind = _classify_runtime_failure(exc)
            with session_scope(service._settings.source_discovery_database_url) as session:
                item = session.get(SourceRuntimeWorkItemORM, work_item_id)
                attempt = session.scalar(
                    select(SourceRuntimeWorkAttemptORM)
                    .where(
                        SourceRuntimeWorkAttemptORM.work_item_id == work_item_id,
                        SourceRuntimeWorkAttemptORM.run_id == tick_id,
                    )
                    .order_by(SourceRuntimeWorkAttemptORM.attempt_id.desc())
                    .limit(1)
                )
                if item is None or attempt is None:
                    continue
                attempt.failure_kind = failure_kind
                attempt.status = "blocked" if failure_kind in BLOCKING_FAILURE_KINDS else "retry_scheduled"
                attempt.finished_at = _utc_now()
                attempt.summary = f"{item.job_type} failed"
                attempt.error_summary = str(exc)[:800]
                item.last_failure_kind = failure_kind
                item.last_error = str(exc)[:800]
                item.lease_owner = None
                item.lease_expires_at = None
                item.updated_at = _utc_now()
                if failure_kind in BLOCKING_FAILURE_KINDS:
                    item.status = "blocked"
                elif item.attempt_count >= max(1, item.max_attempts):
                    item.status = "dead_lettered"
                    dead_lettered_items += 1
                else:
                    item.status = "retry_scheduled"
                    retry_scheduled_items += 1
                    item.next_run_at = _isoformat_utc(
                        _parse_utc_like(now)
                        + timedelta(seconds=_retry_backoff_seconds(service._settings, item.attempt_count))
                    )
                session.flush()

        with session_scope(service._settings.source_discovery_database_url) as session:
            item = session.get(SourceRuntimeWorkItemORM, work_item_id)
            attempt = session.scalar(
                select(SourceRuntimeWorkAttemptORM)
                .where(
                    SourceRuntimeWorkAttemptORM.work_item_id == work_item_id,
                    SourceRuntimeWorkAttemptORM.run_id == tick_id,
                )
                .order_by(SourceRuntimeWorkAttemptORM.attempt_id.desc())
                .limit(1)
            )
            if item is None or attempt is None:
                continue
            if item.status == "running":
                if item.domain_key:
                    _consume_runtime_budget(session, scope="domain", key=item.domain_key, request_limit=service._settings.source_discovery_per_domain_request_budget, used=max(1, item.request_budget), now=_utc_now())
                if item.provider_key:
                    _consume_runtime_budget(session, scope="provider", key=item.provider_key, request_limit=service._settings.source_discovery_per_provider_request_budget, used=max(1, item.request_budget), now=_utc_now())
                attempt.status = "completed"
                attempt.finished_at = _utc_now()
                attempt.summary = f"{item.job_type} completed"
                attempt.used_requests = max(0, item.request_budget)
                item.status = "completed"
                item.lease_owner = None
                item.lease_expires_at = None
                item.updated_at = _utc_now()
                item.next_run_at = _isoformat_utc(_parse_utc_like(now) + timedelta(hours=1))
                session.flush()

    finished_at = _utc_now()
    used_requests = (
        sum(check.used_requests for check in checks)
        + sum(job.used_requests for job in jobs)
        + sum(execution.used_requests for execution in llm_executions)
    )
    with session_scope(service._settings.source_discovery_database_url) as session:
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
            link_graph_jobs_requested=max(0, request.link_graph_job_limit),
            link_graph_jobs_completed=link_graph_jobs_completed,
            expansion_jobs_requested=max(0, request.expansion_job_limit),
            expansion_jobs_completed=expansion_jobs_completed,
            knowledge_backfill_jobs_requested=max(0, request.knowledge_backfill_limit),
            knowledge_backfill_jobs_completed=knowledge_backfill_jobs_completed,
            record_extract_jobs_requested=max(0, request.record_source_extract_limit),
            record_extract_jobs_completed=record_extract_jobs_completed,
            llm_tasks_requested=0,
            llm_tasks_completed=0,
            duplicate_snapshots_skipped=duplicate_snapshots_skipped,
            request_budget=max(0, request.request_budget),
            used_requests=used_requests,
            caveats_json=json.dumps(caveats),
        )
        session.add(tick)
        run = session.get(RuntimeSchedulerRunORM, tick_id)
        if run is not None:
            run.status = "completed"
            run.finished_at = finished_at
            run.summary = (
                f"queued={queued_work_items} executed={executed_work_items} "
                f"retry={retry_scheduled_items} budget_blocked={budget_blocked_items} dead_lettered={dead_lettered_items}"
            )
        queue_job = SourceDiscoveryJobORM(
            job_id=f"source-discovery-job:scheduler-queue-run:{_compact_timestamp(now)}",
            job_type="scheduler_queue_run",
            status="completed",
            seed_url=None,
            wave_id=None,
            wave_title=None,
            discovered_source_ids_json=json.dumps([]),
            rejected_reason=None,
            request_budget=max(0, request.request_budget),
            used_requests=used_requests,
            started_at=now,
            finished_at=finished_at,
            outcome_summary=run.summary if run is not None else None,
            caveats_json=json.dumps(caveats),
        )
        session.add(queue_job)
        session.flush()

    return SourceDiscoverySchedulerTickResponse(
        tick_id=tick_id,
        status="completed",
        requested_at=now,
        finished_at=finished_at,
        health_checks_completed=len(checks),
        structure_scans_completed=structure_scans_completed,
        public_discovery_jobs_completed=public_discovery_jobs_completed,
        link_graph_jobs_completed=link_graph_jobs_completed,
        expansion_jobs_completed=expansion_jobs_completed,
        knowledge_backfill_jobs_completed=knowledge_backfill_jobs_completed,
        record_extract_jobs_completed=record_extract_jobs_completed,
        llm_tasks_completed=0,
        duplicate_snapshots_skipped=duplicate_snapshots_skipped,
        request_budget=max(0, request.request_budget),
        used_requests=used_requests,
        queued_work_items=queued_work_items,
        executed_work_items=executed_work_items,
        retry_scheduled_items=retry_scheduled_items,
        budget_blocked_items=budget_blocked_items,
        dead_lettered_items=dead_lettered_items,
        active_shard_id=active_shard_id,
        health_checks=checks,
        jobs=jobs,
        llm_executions=llm_executions,
        caveats=SOURCE_DISCOVERY_CAVEATS + caveats,
    )


def _build_queue_specs(
    session: Session,
    request: SourceDiscoverySchedulerTickRequest,
    *,
    now: str,
) -> list[dict[str, object]]:
    memories = list(
        session.scalars(
            select(SourceMemoryORM)
            .where(SourceMemoryORM.lifecycle_state != "rejected")
            .order_by(SourceMemoryORM.next_check_at, SourceMemoryORM.last_seen_at)
        )
    )
    best_fit_by_source_id: dict[str, tuple[str | None, str | None]] = {}
    for memory in memories:
        best_fit = _best_wave_fit(_fits_for_source(session, memory.source_id))
        best_fit_by_source_id[memory.source_id] = (
            best_fit.wave_id if best_fit else None,
            best_fit.wave_title if best_fit else None,
        )
    discovery_context = _build_discovery_priority_context(session)
    specs: list[dict[str, object]] = []
    for memory in memories:
        wave_id, wave_title = best_fit_by_source_id[memory.source_id]
        if _is_due_for_health_check(memory.next_check_at, now) and len([spec for spec in specs if spec["job_type"] == "health_check"]) < max(0, request.health_check_limit):
            specs.append(_work_spec_for_memory("health_check", memory, wave_id=wave_id, wave_title=wave_title, priority_score=70))
        if _is_scheduler_structure_scan_candidate(memory) and len([spec for spec in specs if spec["job_type"] == "structure_scan"]) < max(0, request.structure_scan_limit):
            score = _compute_discovery_priority(session, memory, now=now, context=discovery_context)[0]
            specs.append(_work_spec_for_memory("structure_scan", memory, wave_id=wave_id, wave_title=wave_title, priority_score=score))
        if _is_scheduler_public_discovery_candidate(memory, now) and len([spec for spec in specs if spec["job_type"] in {"feed_link_scan", "sitemap_scan", "catalog_scan"}]) < max(0, request.public_discovery_job_limit):
            job_type = _public_discovery_followup_kind(memory)
            score = _compute_discovery_priority(session, memory, now=now, context=discovery_context)[0]
            specs.append(_work_spec_for_memory(job_type, memory, wave_id=wave_id, wave_title=wave_title, priority_score=score))
        if _is_scheduler_link_graph_candidate(memory, now) and len([spec for spec in specs if spec["job_type"] == "link_graph_scan"]) < max(0, request.link_graph_job_limit):
            score = _compute_discovery_priority(session, memory, now=now, context=discovery_context)[0]
            specs.append(_work_spec_for_memory("link_graph_scan", memory, wave_id=wave_id, wave_title=wave_title, priority_score=score))
        if _is_scheduler_expansion_candidate(memory) and len([spec for spec in specs if spec["job_type"] == "expand"]) < max(0, request.expansion_job_limit):
            specs.append(_work_spec_for_memory("expand", memory, wave_id=wave_id, wave_title=wave_title, priority_score=50))
    if request.knowledge_backfill_limit > 0:
        specs.append(
            {
                "job_type": "knowledge_backfill",
                "source_id": None,
                "seed_url": None,
                "domain_key": "internal",
                "provider_key": "knowledge_backfill",
                "wave_id": None,
                "wave_title": None,
                "payload": {"max_snapshots": max(0, request.knowledge_backfill_limit)},
                "priority_score": 40,
                "request_budget": 0,
                "caveats": ["Queue-triggered knowledge-node backfill."],
            }
        )
    if request.record_source_extract_limit > 0:
        specs.append(
            {
                "job_type": "record_source_extract",
                "source_id": None,
                "seed_url": None,
                "domain_key": "internal",
                "provider_key": "record_extract",
                "wave_id": None,
                "wave_title": None,
                "payload": {"wave_monitor_limit": max(0, request.record_source_extract_limit)},
                "priority_score": 35,
                "request_budget": 0,
                "caveats": ["Queue-triggered record-source extraction."],
            }
        )
    return specs


def _work_spec_for_memory(
    job_type: str,
    memory: SourceMemoryORM,
    *,
    wave_id: str | None,
    wave_title: str | None,
    priority_score: int,
) -> dict[str, object]:
    return {
        "job_type": job_type,
        "source_id": memory.source_id,
        "seed_url": memory.url,
        "domain_key": memory.parent_domain or _domain_from_url(memory.url),
        "provider_key": job_type,
        "wave_id": wave_id,
        "wave_title": wave_title,
        "payload": {},
        "priority_score": int(priority_score),
        "request_budget": 1 if job_type != "knowledge_backfill" else 0,
        "caveats": [f"Queue-triggered {job_type.replace('_', ' ')}."],
    }


def _queue_runtime_work_item(
    session: Session,
    settings: Settings,
    *,
    spec: dict[str, object],
    now: str,
) -> tuple[SourceRuntimeWorkItemORM, bool]:
    domain_key = str(spec.get("domain_key") or "")
    source_id = str(spec.get("source_id")) if spec.get("source_id") else None
    seed_url = str(spec.get("seed_url")) if spec.get("seed_url") else None
    dedupe_key = "|".join([
        str(spec["job_type"]),
        source_id or "-",
        seed_url or "-",
        domain_key or "-",
    ])
    existing = session.scalar(
        select(SourceRuntimeWorkItemORM)
        .where(
            SourceRuntimeWorkItemORM.worker_name == "source_discovery",
            SourceRuntimeWorkItemORM.dedupe_key == dedupe_key,
        )
        .order_by(SourceRuntimeWorkItemORM.updated_at.desc())
        .limit(1)
    )
    shard_count = max(1, settings.source_discovery_shard_count)
    shard_index = _stable_shard_index(domain_key or source_id or dedupe_key, shard_count)
    if existing is not None:
        existing.next_run_at = min(existing.next_run_at, now) if existing.next_run_at else now
        existing.priority_score = max(existing.priority_score, int(spec.get("priority_score", 0)))
        existing.request_budget = max(existing.request_budget, int(spec.get("request_budget", 0)))
        existing.payload_json = json.dumps(spec.get("payload", {}))
        existing.caveats_json = json.dumps(list(spec.get("caveats") or []))
        existing.domain_key = domain_key or existing.domain_key
        existing.provider_key = str(spec.get("provider_key") or existing.provider_key or "")
        existing.shard_index = shard_index
        existing.shard_count = shard_count
        existing.updated_at = now
        if existing.status in {"completed", "dead_lettered", "blocked"}:
            existing.status = "queued"
            existing.next_run_at = now
        return existing, False
    item = SourceRuntimeWorkItemORM(
        work_item_id=f"source-runtime-work:{_safe_id(dedupe_key)}:{_compact_timestamp(now)}",
        worker_name="source_discovery",
        job_type=str(spec["job_type"]),
        status="queued",
        source_id=source_id,
        seed_url=seed_url,
        domain_key=domain_key or None,
        provider_key=str(spec.get("provider_key") or spec["job_type"]),
        shard_index=shard_index,
        shard_count=shard_count,
        dedupe_key=dedupe_key,
        priority_score=int(spec.get("priority_score", 0)),
        next_run_at=now,
        lease_owner=None,
        lease_expires_at=None,
        attempt_count=0,
        max_attempts=max(1, settings.source_discovery_work_item_max_attempts),
        request_budget=int(spec.get("request_budget", 0)),
        last_failure_kind=None,
        last_error=None,
        payload_json=json.dumps(spec.get("payload", {})),
        caveats_json=json.dumps(list(spec.get("caveats") or [])),
        created_at=now,
        updated_at=now,
    )
    session.add(item)
    session.flush()
    return item, True


def _stable_shard_index(key: str, shard_count: int) -> int:
    if shard_count <= 1:
        return 0
    digest = hashlib.sha256(key.encode("utf-8")).hexdigest()
    return int(digest[:8], 16) % shard_count


def _runtime_budget_window_bounds(now: str) -> tuple[str, str]:
    dt = _parse_utc_like(now)
    start = dt.replace(minute=0, second=0, microsecond=0)
    end = start + timedelta(minutes=RUNTIME_BUDGET_WINDOW_MINUTES)
    return _isoformat_utc(start), _isoformat_utc(end)


def _runtime_budget_has_capacity(session: Session, *, scope: str, key: str, request_limit: int, needed: int, now: str) -> bool:
    if request_limit <= 0:
        return True
    window = _get_or_create_runtime_budget_window(session, scope=scope, key=key, request_limit=request_limit, now=now)
    return window.used_requests + needed <= request_limit


def _consume_runtime_budget(session: Session, *, scope: str, key: str, request_limit: int, used: int, now: str) -> None:
    if request_limit <= 0:
        return
    window = _get_or_create_runtime_budget_window(session, scope=scope, key=key, request_limit=request_limit, now=now)
    window.used_requests += used
    window.updated_at = now


def _get_or_create_runtime_budget_window(session: Session, *, scope: str, key: str, request_limit: int, now: str) -> SourceRuntimeBudgetWindowORM:
    window_start, window_end = _runtime_budget_window_bounds(now)
    row = session.scalar(
        select(SourceRuntimeBudgetWindowORM).where(
            SourceRuntimeBudgetWindowORM.budget_scope == scope,
            SourceRuntimeBudgetWindowORM.budget_key == key,
            SourceRuntimeBudgetWindowORM.window_start == window_start,
        ).limit(1)
    )
    if row is not None:
        return row
    row = SourceRuntimeBudgetWindowORM(
        budget_scope=scope,
        budget_key=key,
        window_start=window_start,
        window_end=window_end,
        request_limit=request_limit,
        used_requests=0,
        created_at=now,
        updated_at=now,
    )
    session.add(row)
    session.flush()
    return row


def _retry_backoff_seconds(settings: Settings, attempt_count: int) -> int:
    exponent = max(0, attempt_count - 1)
    value = settings.source_discovery_retry_backoff_base_seconds * (2 ** exponent)
    return min(settings.source_discovery_retry_backoff_max_seconds, value)


def _classify_runtime_failure(exc: Exception) -> str:
    text = str(exc).casefold()
    if "captcha" in text:
        return "blocked_captcha"
    if "login" in text or "auth" in text:
        return "blocked_auth"
    if "rate limit" in text or "429" in text:
        return "rate_limited"
    if "timeout" in text:
        return "timeout"
    if "dns" in text or "name resolution" in text:
        return "dns_error"
    if "tls" in text or "ssl" in text:
        return "tls_error"
    if "parse" in text:
        return "parse_error"
    if "unsupported" in text:
        return "unsupported_shape"
    if "budget" in text:
        return "budget_exhausted"
    return "unexpected_status"


def _execute_runtime_work_item(
    service: SourceDiscoveryService,
    work_item_id: str,
    *,
    tick_id: str,
) -> dict[str, object]:
    with session_scope(service._settings.source_discovery_database_url) as session:
        item = session.get(SourceRuntimeWorkItemORM, work_item_id)
        if item is None:
            raise ValueError(f"Unknown work_item_id: {work_item_id}")
        payload = _loads_dict(item.payload_json)
        wave_id = payload.get("wave_id")
        wave_title = payload.get("wave_title")
        job_type = item.job_type
        if job_type == "health_check":
            response = service.check_source_health(
                SourceDiscoveryHealthCheckRequest(
                    source_id=item.source_id or "",
                    request_budget=item.request_budget,
                    caveats=_loads_list(item.caveats_json),
                )
            )
            return {"job_type": job_type, "health_check": response.health_check, "job": None, "used_requests": response.health_check.used_requests}
        if job_type == "structure_scan":
            response = service.run_structure_scan_job(
                SourceDiscoveryStructureScanRequest(
                    target_url=item.seed_url or "",
                    wave_id=wave_id if isinstance(wave_id, str) else None,
                    wave_title=wave_title if isinstance(wave_title, str) else None,
                    request_budget=item.request_budget,
                    caveats=_loads_list(item.caveats_json),
                )
            )
            job = _coerce_job_summary(response.job)
            return {"job_type": job_type, "health_check": None, "job": job, "used_requests": job.used_requests}
        if job_type == "feed_link_scan":
            response = service.run_feed_link_scan_job(
                SourceDiscoveryFeedLinkScanRequest(
                    feed_url=item.seed_url or "",
                    wave_id=wave_id if isinstance(wave_id, str) else None,
                    wave_title=wave_title if isinstance(wave_title, str) else None,
                    request_budget=item.request_budget,
                    caveats=_loads_list(item.caveats_json),
                )
            )
            job = _coerce_job_summary(response.job)
            return {"job_type": job_type, "health_check": None, "job": job, "used_requests": job.used_requests}
        if job_type == "sitemap_scan":
            response = service.run_sitemap_scan_job(
                SourceDiscoverySitemapScanRequest(
                    sitemap_url=item.seed_url or "",
                    wave_id=wave_id if isinstance(wave_id, str) else None,
                    wave_title=wave_title if isinstance(wave_title, str) else None,
                    request_budget=item.request_budget,
                    caveats=_loads_list(item.caveats_json),
                )
            )
            job = _coerce_job_summary(response.job)
            return {"job_type": job_type, "health_check": None, "job": job, "used_requests": job.used_requests}
        if job_type == "catalog_scan":
            response = service.run_catalog_scan_job(
                SourceDiscoveryCatalogScanRequest(
                    catalog_url=item.seed_url or "",
                    wave_id=wave_id if isinstance(wave_id, str) else None,
                    wave_title=wave_title if isinstance(wave_title, str) else None,
                    request_budget=item.request_budget,
                    caveats=_loads_list(item.caveats_json),
                )
            )
            job = _coerce_job_summary(response.job)
            return {"job_type": job_type, "health_check": None, "job": job, "used_requests": job.used_requests}
        if job_type == "link_graph_scan":
            response = service.run_link_graph_scan_job(
                SourceDiscoveryLinkGraphScanRequest(
                    source_id=item.source_id or "",
                    request_budget=item.request_budget,
                    caveats=_loads_list(item.caveats_json),
                )
            )
            job = _coerce_job_summary(response.job)
            return {"job_type": job_type, "health_check": None, "job": job, "used_requests": job.used_requests}
        if job_type == "expand":
            response = service.run_expansion_job(
                SourceDiscoveryExpansionJobRequest(
                    seed_url=item.seed_url or "",
                    wave_id=wave_id if isinstance(wave_id, str) else None,
                    wave_title=wave_title if isinstance(wave_title, str) else None,
                    request_budget=item.request_budget,
                    caveats=_loads_list(item.caveats_json),
                )
            )
            job = _coerce_job_summary(response.job)
            return {"job_type": job_type, "health_check": None, "job": job, "used_requests": job.used_requests}
        if job_type == "knowledge_backfill":
            response = service.run_knowledge_backfill_job(
                SourceDiscoveryKnowledgeBackfillRequest(
                    max_snapshots=int(payload.get("max_snapshots", 0)),
                    mode="missing_only",
                    caveats=_loads_list(item.caveats_json),
                )
            )
            job = _coerce_job_summary(response.job)
            return {"job_type": job_type, "health_check": None, "job": job, "used_requests": job.used_requests}
        if job_type == "record_source_extract":
            response = service.run_record_source_extract_job(
                SourceDiscoveryRecordSourceExtractRequest(
                    wave_monitor_limit=int(payload.get("wave_monitor_limit", 0)),
                    request_budget=item.request_budget,
                    caveats=_loads_list(item.caveats_json),
                )
            )
            job = _coerce_job_summary(response.job)
            return {"job_type": job_type, "health_check": None, "job": job, "used_requests": job.used_requests}
        raise ValueError(f"Unsupported runtime work item job_type: {job_type}")
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
            locale_expansion_basis_json=json.dumps(sorted(set(seed.locale_expansion_basis))),
            discovered_from_provider=seed.discovered_from_provider,
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
        memory.locale_expansion_basis_json = json.dumps(
            sorted(set(_loads_list(memory.locale_expansion_basis_json) + seed.locale_expansion_basis))
        )
        if seed.discovered_from_provider:
            memory.discovered_from_provider = _merge_optional_text(memory.discovered_from_provider, seed.discovered_from_provider)
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
    memory.confirmed_claim_count = int(memory.confirmed_claim_count or 0)
    memory.contradicted_claim_count = int(memory.contradicted_claim_count or 0)
    memory.corrected_claim_count = int(memory.corrected_claim_count or 0)
    memory.outdated_claim_count = int(memory.outdated_claim_count or 0)
    memory.unresolved_claim_count = int(memory.unresolved_claim_count or 0)
    memory.not_applicable_claim_count = int(memory.not_applicable_claim_count or 0)
    memory.global_reputation_score = float(memory.global_reputation_score if memory.global_reputation_score is not None else 0.5)
    memory.domain_reputation_score = float(memory.domain_reputation_score if memory.domain_reputation_score is not None else memory.global_reputation_score)
    memory.correction_score = float(memory.correction_score if memory.correction_score is not None else 0.5)
    memory.timeliness_score = float(memory.timeliness_score if memory.timeliness_score is not None else 0.5)
    before = memory.global_reputation_score
    profile_name = memory.reputation_policy_version or DEFAULT_REPUTATION_PROFILE
    delta = _profile_outcome_delta(
        memory,
        request,
        profile_name=profile_name,
    )
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
    memory.last_calibrated_at = now
    memory.reputation_policy_version = profile_name
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
            policy_version=profile_name,
        )
    )


def _reputation_profile(name: str | None) -> dict[str, object]:
    if name and name in REPUTATION_PROFILES:
        return REPUTATION_PROFILES[name]
    return REPUTATION_PROFILES[DEFAULT_REPUTATION_PROFILE]


def _profile_outcome_delta(
    memory: SourceMemoryORM,
    request: SourceDiscoveryClaimOutcomeRequest,
    *,
    profile_name: str | None,
) -> float:
    profile = _reputation_profile(profile_name)
    outcome_deltas = dict(profile.get("outcome_deltas", {}))
    base_delta = _outcome_delta(memory.source_class, request.outcome)
    delta = float(outcome_deltas.get(request.outcome, base_delta))
    if request.outcome == "outdated" and memory.source_class == "static":
        delta = 0.0
    source_bias = dict(profile.get("source_class_bias", {}))
    evidence_bias = dict(profile.get("evidence_basis_bias", {}))
    delta += float(source_bias.get(memory.source_class, 0.0))
    delta += float(evidence_bias.get(request.evidence_basis, 0.0))
    if request.corroborating_source_ids:
        delta += min(len(request.corroborating_source_ids), 3) * float(profile.get("corroboration_bonus", 0.0))
    if request.contradiction_source_ids:
        delta += min(len(request.contradiction_source_ids), 3) * float(profile.get("contradiction_penalty", 0.0))
    if request.outcome == "corrected":
        delta += float(profile.get("correction_penalty", 0.0))
    health_penalty = dict(profile.get("health_penalty", {}))
    delta += float(health_penalty.get(memory.source_health, 0.0))
    if request.outcome == "outdated" and memory.source_class != "static":
        delta += float(profile.get("timeliness_penalty", 0.0))
    return delta


def _event_role_for_outcome(outcome: str | None) -> str:
    if outcome == "contradicted":
        return "contradicting"
    if outcome == "corrected":
        return "corrective"
    if outcome == "unresolved":
        return "open_question"
    return "supporting"


def _event_day(value: str | None) -> str | None:
    if not value:
        return None
    return value[:10]


def _event_scope_for_source(session: Session, source_id: str) -> SourceDiscoveryScopeHints:
    memory = session.get(SourceMemoryORM, source_id)
    if memory is None:
        return SourceDiscoveryScopeHints()
    return _loads_scope_hints(memory.scope_hints_json)


def _event_media_cluster_ids_for_source(session: Session, source_id: str) -> list[str]:
    return sorted({
        cluster_id
        for cluster_id in session.scalars(
            select(SourceMediaArtifactORM.duplicate_cluster_id).where(
                SourceMediaArtifactORM.source_id == source_id,
                SourceMediaArtifactORM.duplicate_cluster_id.is_not(None),
            )
        )
        if cluster_id
    })


def _event_signature(
    *,
    claim_text: str,
    claim_type: str,
    observed_at: str | None,
    knowledge_node_id: str | None,
    scope_hints: SourceDiscoveryScopeHints,
) -> tuple[str, str]:
    normalized_claim = _normalize_text(claim_text)
    canonical_parts = [
        claim_type.strip().casefold(),
        normalized_claim,
        (knowledge_node_id or "").strip().casefold(),
        (_event_day(observed_at) or "").strip().casefold(),
        "|".join(sorted(item.casefold() for item in scope_hints.spatial[:3])),
        "|".join(sorted(item.casefold() for item in scope_hints.topic[:3])),
    ]
    signature = hashlib.sha256("||".join(canonical_parts).encode("utf-8")).hexdigest()
    return signature, normalized_claim


def _claim_candidate_observed_at(session: Session, candidate: SourceReviewClaimCandidateORM) -> str | None:
    if candidate.snapshot_id:
        snapshot = session.get(SourceContentSnapshotORM, candidate.snapshot_id)
        if snapshot is not None:
            return snapshot.published_at or snapshot.fetched_at
    return candidate.created_at


def _refresh_event_graph(
    session: Session,
    *,
    source_ids: list[str],
    wave_ids: list[str],
    knowledge_node_ids: list[str],
    include_pending_claims: bool,
    mode: str,
    max_events: int,
    now: str,
) -> dict[str, object]:
    source_ids = [value for value in source_ids if value]
    wave_ids = [value for value in wave_ids if value]
    knowledge_node_ids = [value for value in knowledge_node_ids if value]
    allowed_snapshots = {
        snapshot.snapshot_id
        for snapshot in session.scalars(
            select(SourceContentSnapshotORM).where(SourceContentSnapshotORM.knowledge_node_id.in_(knowledge_node_ids))
        )
    } if knowledge_node_ids else set()
    all_claim_rows = list(session.scalars(select(SourceClaimOutcomeORM).order_by(SourceClaimOutcomeORM.assessed_at.desc(), SourceClaimOutcomeORM.outcome_id.desc())))
    all_candidate_rows = list(
        session.scalars(
            select(SourceReviewClaimCandidateORM)
            .where(SourceReviewClaimCandidateORM.status == "pending")
            .order_by(SourceReviewClaimCandidateORM.created_at.desc(), SourceReviewClaimCandidateORM.claim_candidate_id.desc())
        )
    ) if include_pending_claims else []

    def _claim_targeted(row: SourceClaimOutcomeORM) -> bool:
        if source_ids and row.source_id in source_ids:
            return True
        if wave_ids and row.wave_id in wave_ids:
            return True
        if knowledge_node_ids:
            linked = session.scalar(
                select(SourceContentSnapshotORM.snapshot_id)
                .where(
                    SourceContentSnapshotORM.source_id == row.source_id,
                    SourceContentSnapshotORM.knowledge_node_id.in_(knowledge_node_ids),
                )
                .limit(1)
            )
            if linked is not None:
                return True
        return not source_ids and not wave_ids and not knowledge_node_ids

    def _candidate_targeted(row: SourceReviewClaimCandidateORM) -> bool:
        if source_ids and row.source_id in source_ids:
            return True
        if wave_ids and row.wave_id in wave_ids:
            return True
        if knowledge_node_ids and row.knowledge_node_id in knowledge_node_ids:
            return True
        return not source_ids and not wave_ids and not knowledge_node_ids

    def _claim_payload(row: SourceClaimOutcomeORM) -> dict[str, object]:
        if knowledge_node_ids and allowed_snapshots:
            linked_snapshot = session.scalar(
                select(SourceContentSnapshotORM)
                .where(
                    SourceContentSnapshotORM.source_id == row.source_id,
                    SourceContentSnapshotORM.knowledge_node_id.in_(knowledge_node_ids),
                )
                .order_by(SourceContentSnapshotORM.fetched_at.desc(), SourceContentSnapshotORM.snapshot_id.desc())
                .limit(1)
            )
        else:
            linked_snapshot = session.scalar(
                select(SourceContentSnapshotORM)
                .where(SourceContentSnapshotORM.source_id == row.source_id)
                .order_by(SourceContentSnapshotORM.fetched_at.desc(), SourceContentSnapshotORM.snapshot_id.desc())
                .limit(1)
            )
        knowledge_node_id = linked_snapshot.knowledge_node_id if linked_snapshot is not None else None
        snapshot_id = linked_snapshot.snapshot_id if linked_snapshot is not None else None
        scope_hints = _event_scope_for_source(session, row.source_id)
        signature, normalized_claim = _event_signature(
            claim_text=row.claim_text,
            claim_type=row.claim_type,
            observed_at=row.observed_at,
            knowledge_node_id=knowledge_node_id,
            scope_hints=scope_hints,
        )
        memory = session.get(SourceMemoryORM, row.source_id)
        return {
            "kind": "outcome",
            "signature": signature,
            "normalized_claim": normalized_claim,
            "source_id": row.source_id,
            "wave_id": row.wave_id,
            "role": _event_role_for_outcome(row.outcome),
            "claim_text": row.claim_text,
            "claim_type": row.claim_type,
            "evidence_basis": row.evidence_basis,
            "outcome": row.outcome,
            "observed_at": row.observed_at,
            "snapshot_id": snapshot_id,
            "knowledge_node_id": knowledge_node_id,
            "media_cluster_ids": _event_media_cluster_ids_for_source(session, row.source_id),
            "claim_outcome_id": row.outcome_id,
            "claim_candidate_id": None,
            "source_class": memory.source_class if memory is not None else "unknown",
            "scope_hints": scope_hints,
            "created_at": row.assessed_at,
            "caveats": _loads_list(row.caveats_json),
        }

    def _candidate_payload(row: SourceReviewClaimCandidateORM) -> dict[str, object]:
        observed_at = _claim_candidate_observed_at(session, row)
        scope_hints = _event_scope_for_source(session, row.source_id)
        signature, normalized_claim = _event_signature(
            claim_text=row.claim_text,
            claim_type=row.claim_type,
            observed_at=observed_at,
            knowledge_node_id=row.knowledge_node_id,
            scope_hints=scope_hints,
        )
        memory = session.get(SourceMemoryORM, row.source_id)
        return {
            "kind": "candidate",
            "signature": signature,
            "normalized_claim": normalized_claim,
            "source_id": row.source_id,
            "wave_id": row.wave_id,
            "role": "provisional",
            "claim_text": row.claim_text,
            "claim_type": row.claim_type,
            "evidence_basis": row.evidence_basis,
            "outcome": None,
            "observed_at": observed_at,
            "snapshot_id": row.snapshot_id,
            "knowledge_node_id": row.knowledge_node_id,
            "media_cluster_ids": _event_media_cluster_ids_for_source(session, row.source_id),
            "claim_outcome_id": None,
            "claim_candidate_id": row.claim_candidate_id,
            "source_class": memory.source_class if memory is not None else "unknown",
            "scope_hints": scope_hints,
            "created_at": row.created_at,
            "caveats": _loads_list(row.caveats_json),
        }

    targeted_payloads = [_claim_payload(row) for row in all_claim_rows if _claim_targeted(row)]
    if include_pending_claims:
        targeted_payloads.extend(_candidate_payload(row) for row in all_candidate_rows if _candidate_targeted(row))
    target_signatures = {str(payload["signature"]) for payload in targeted_payloads}
    payloads: list[dict[str, object]] = []
    if not target_signatures and not source_ids and not wave_ids and not knowledge_node_ids:
        target_signatures = {str(_claim_payload(row)["signature"]) for row in all_claim_rows}
        if include_pending_claims:
            target_signatures.update(str(_candidate_payload(row)["signature"]) for row in all_candidate_rows)
    if target_signatures:
        for row in all_claim_rows:
            payload = _claim_payload(row)
            if str(payload["signature"]) in target_signatures:
                payloads.append(payload)
        for row in all_candidate_rows:
            payload = _candidate_payload(row)
            if str(payload["signature"]) in target_signatures:
                payloads.append(payload)

    grouped: dict[str, list[dict[str, object]]] = {}
    for payload in payloads:
        grouped.setdefault(str(payload["signature"]), []).append(payload)
    signatures = list(grouped.keys())
    if mode == "missing_only":
        existing_signatures = {
            signature
            for signature in session.scalars(
                select(SourceEventClusterORM.signature).where(SourceEventClusterORM.signature.in_(signatures))
            )
        }
        signatures = [signature for signature in signatures if signature not in existing_signatures]
    signatures = signatures[: max(0, max_events)]

    created_event_count = 0
    updated_event_count = 0
    contested_event_count = 0
    open_question_count = 0
    affected_event_ids: list[str] = []
    affected_source_ids: set[str] = set()
    for signature in signatures:
        rows = grouped[signature]
        existing = session.scalar(select(SourceEventClusterORM).where(SourceEventClusterORM.signature == signature).limit(1))
        if existing is not None and mode == "recompute_selected":
            session.query(SourceEventMemberORM).where(SourceEventMemberORM.event_id == existing.event_id).delete()
            session.query(SourceEventOpenQuestionORM).where(SourceEventOpenQuestionORM.event_id == existing.event_id).delete()
            event = existing
            updated_event_count += 1
        elif existing is None:
            event = SourceEventClusterORM(
                event_id=f"source-event:{signature[:20]}",
                signature=signature,
                first_seen_at=now,
                last_seen_at=now,
                last_graph_refresh_at=now,
            )
            session.add(event)
            created_event_count += 1
        else:
            event = existing
            updated_event_count += 1
            session.query(SourceEventMemberORM).where(SourceEventMemberORM.event_id == existing.event_id).delete()
            session.query(SourceEventOpenQuestionORM).where(SourceEventOpenQuestionORM.event_id == existing.event_id).delete()

        source_ids_in_event = sorted({str(row["source_id"]) for row in rows})
        knowledge_ids = sorted({str(row["knowledge_node_id"]) for row in rows if row.get("knowledge_node_id")})
        media_cluster_ids = sorted({cluster_id for row in rows for cluster_id in list(row.get("media_cluster_ids") or []) if cluster_id})
        supporting_sources = {str(row["source_id"]) for row in rows if row["role"] in {"supporting", "provisional"}}
        contradiction_sources = {str(row["source_id"]) for row in rows if row["role"] == "contradicting"}
        corrective_sources = {str(row["source_id"]) for row in rows if row["role"] == "corrective"}
        open_question_sources = {str(row["source_id"]) for row in rows if row["role"] == "open_question"}
        if corrective_sources:
            status = "corrected"
        elif contradiction_sources:
            status = "contested"
        elif open_question_sources and not supporting_sources:
            status = "open_question"
        elif len(supporting_sources) > 1:
            status = "corroborated"
        else:
            status = "single_source"
        if status in {"contested", "corrected"}:
            contested_event_count += 1
        if status == "open_question":
            open_question_count += 1
        first_payload = rows[0]
        merged_scope = SourceDiscoveryScopeHints()
        for row in rows:
            merged_scope = _merge_scope_hints(merged_scope, row["scope_hints"])  # type: ignore[arg-type]
        event.status = status
        event.claim_type = str(first_payload["claim_type"])
        event.canonical_claim_text = str(first_payload["claim_text"])[:1000]
        event.normalized_claim_text = str(first_payload["normalized_claim"])
        event.observed_day = _event_day(first_payload.get("observed_at"))  # type: ignore[arg-type]
        event.wave_id = str(first_payload["wave_id"]) if first_payload.get("wave_id") else None
        event.supporting_source_count = len(supporting_sources)
        event.contradiction_source_count = len(contradiction_sources)
        event.corrective_source_count = len(corrective_sources)
        event.open_question_count = len(open_question_sources)
        event.last_seen_at = max(str(row["created_at"]) for row in rows)
        event.last_graph_refresh_at = now
        event.member_source_ids_json = json.dumps(source_ids_in_event)
        event.knowledge_node_ids_json = json.dumps(knowledge_ids)
        event.media_cluster_ids_json = json.dumps(media_cluster_ids)
        event.scope_hints_json = _dumps_scope_hints(merged_scope)
        event.caveats_json = json.dumps([
            "Event clusters are deterministic evidence groupings and do not adjudicate truth on their own.",
        ])
        session.flush()
        affected_event_ids.append(event.event_id)
        affected_source_ids.update(source_ids_in_event)
        for row in rows:
            session.add(
                SourceEventMemberORM(
                    event_id=event.event_id,
                    source_id=str(row["source_id"]),
                    wave_id=str(row["wave_id"]) if row.get("wave_id") else None,
                    role=str(row["role"]),
                    claim_text=str(row["claim_text"])[:1000],
                    claim_type=str(row["claim_type"]),
                    evidence_basis=str(row["evidence_basis"]),
                    outcome=str(row["outcome"]) if row.get("outcome") else None,
                    observed_at=str(row["observed_at"]) if row.get("observed_at") else None,
                    snapshot_id=str(row["snapshot_id"]) if row.get("snapshot_id") else None,
                    knowledge_node_id=str(row["knowledge_node_id"]) if row.get("knowledge_node_id") else None,
                    media_cluster_id=(list(row.get("media_cluster_ids") or [None])[0] if list(row.get("media_cluster_ids") or []) else None),
                    claim_outcome_id=row.get("claim_outcome_id"),  # type: ignore[arg-type]
                    claim_candidate_id=row.get("claim_candidate_id"),  # type: ignore[arg-type]
                    source_class=str(row["source_class"]),
                    created_at=str(row["created_at"]),
                    caveats_json=json.dumps(list(row.get("caveats") or [])),
                )
            )
            if str(row["role"]) == "open_question":
                session.add(
                    SourceEventOpenQuestionORM(
                        event_id=event.event_id,
                        source_id=str(row["source_id"]),
                        question_text=str(row["claim_text"])[:1000],
                        created_at=str(row["created_at"]),
                        status="open",
                        caveats_json=json.dumps([
                            "Open question was derived from an unresolved claim outcome.",
                        ]),
                    )
                )
        for source_id in source_ids_in_event:
            memory = session.get(SourceMemoryORM, source_id)
            if memory is not None:
                memory.latest_event_graph_at = now

    session.flush()
    return {
        "processed_claim_count": len(payloads),
        "created_event_count": created_event_count,
        "updated_event_count": updated_event_count,
        "contested_event_count": contested_event_count,
        "open_question_count": open_question_count,
        "event_ids": affected_event_ids,
        "source_ids": sorted(affected_source_ids),
    }


def _select_reputation_recompute_targets(
    session: Session,
    *,
    source_ids: list[str],
    wave_ids: list[str],
    max_sources: int,
) -> list[SourceMemoryORM]:
    if source_ids:
        return [
            memory
            for memory in (session.get(SourceMemoryORM, source_id) for source_id in source_ids[: max(0, max_sources)])
            if memory is not None
        ]
    if wave_ids:
        candidate_source_ids = sorted({
            fit.source_id
            for fit in session.scalars(select(SourceWaveFitORM).where(SourceWaveFitORM.wave_id.in_(wave_ids)))
        })
        return [
            memory
            for memory in (session.get(SourceMemoryORM, source_id) for source_id in candidate_source_ids[: max(0, max_sources)])
            if memory is not None
        ]
    return list(
        session.scalars(
            select(SourceMemoryORM)
            .order_by(SourceMemoryORM.last_reputation_event_at.desc(), SourceMemoryORM.source_id.asc())
            .limit(max(0, max_sources))
        )
    )


def _recompute_memory_reputation(
    session: Session,
    memory: SourceMemoryORM,
    *,
    profile_name: str,
    apply: bool,
    now: str,
) -> dict[str, object]:
    outcomes = list(
        session.scalars(
            select(SourceClaimOutcomeORM)
            .where(SourceClaimOutcomeORM.source_id == memory.source_id)
            .order_by(SourceClaimOutcomeORM.assessed_at.asc(), SourceClaimOutcomeORM.outcome_id.asc())
        )
    )
    projected_score = 0.5
    projected_domain_score = 0.5
    counts = {
        "confirmed": 0,
        "contradicted": 0,
        "corrected": 0,
        "outdated": 0,
        "unresolved": 0,
        "not_applicable": 0,
    }
    correction_score = 0.5
    timeliness_score = 0.5
    for outcome in outcomes:
        request = SourceDiscoveryClaimOutcomeRequest(
            source_id=memory.source_id,
            wave_id=outcome.wave_id,
            claim_text=outcome.claim_text,
            claim_type=outcome.claim_type,
            outcome=outcome.outcome,  # type: ignore[arg-type]
            evidence_basis=outcome.evidence_basis,
            observed_at=outcome.observed_at,
            corroborating_source_ids=_loads_list(outcome.corroborating_source_ids_json),
            contradiction_source_ids=_loads_list(outcome.contradiction_source_ids_json),
            caveats=_loads_list(outcome.caveats_json),
        )
        delta = _profile_outcome_delta(memory, request, profile_name=profile_name)
        projected_score = _clamp(projected_score + delta)
        projected_domain_score = _clamp(projected_domain_score + delta)
        counts[outcome.outcome] = counts.get(outcome.outcome, 0) + 1
        if outcome.outcome == "corrected":
            correction_score = _clamp(correction_score + 0.04)
        elif outcome.outcome == "outdated" and memory.source_class != "static":
            timeliness_score = _clamp(timeliness_score - 0.03)
    changed = abs(projected_score - memory.global_reputation_score) > 1e-9 or profile_name != (memory.reputation_policy_version or DEFAULT_REPUTATION_PROFILE)
    direction = "unchanged"
    if projected_score > memory.global_reputation_score + 1e-9:
        direction = "increased"
    elif projected_score < memory.global_reputation_score - 1e-9:
        direction = "decreased"
    if apply:
        memory.global_reputation_score = projected_score
        memory.domain_reputation_score = projected_domain_score
        memory.confirmed_claim_count = counts["confirmed"]
        memory.contradicted_claim_count = counts["contradicted"]
        memory.corrected_claim_count = counts["corrected"]
        memory.outdated_claim_count = counts["outdated"]
        memory.unresolved_claim_count = counts["unresolved"]
        memory.not_applicable_claim_count = counts["not_applicable"]
        memory.correction_score = correction_score
        memory.timeliness_score = timeliness_score
        memory.confidence_level = _confidence_level(memory)
        memory.reputation_policy_version = profile_name
        memory.last_calibrated_at = now
    return {"changed": changed, "direction": direction}


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
    archive_hits = list(
        session.scalars(
            select(SourceArchiveHitORM)
            .where(SourceArchiveHitORM.source_id == memory.source_id)
            .order_by(SourceArchiveHitORM.discovered_at.desc(), SourceArchiveHitORM.archive_hit_id.desc())
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
    adversarial_findings = _adversarial_findings_for_source(session, memory.source_id, limit=max(0, limit))
    event_clusters = _event_clusters_for_source(session, memory.source_id, limit=max(0, limit))
    contested_event_count = _count_events_for_source_by_status(session, memory.source_id, {"contested", "corrected"})
    open_question_count = _count_events_for_source_by_status(session, memory.source_id, {"open_question"})
    return SourceDiscoveryMemoryDetailResponse(
        memory=_serialize_memory(session, memory, context=context),
        wave_fits=[_serialize_wave_fit(fit) for fit in _fits_for_source(session, memory.source_id)],
        snapshots=[_serialize_snapshot(session, snapshot) for snapshot in snapshots],
        archive_hits=[_serialize_archive_hit(row) for row in archive_hits],
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
        adversarial_findings=[_serialize_adversarial_finding(row) for row in adversarial_findings],
        pending_claim_count=len(_pending_review_claim_candidates_for_source(session, memory.source_id)),
        latest_review_claim_at=pending_review_claims[0].created_at if pending_review_claims else None,
        event_clusters=event_clusters,
        contested_event_count=contested_event_count,
        open_question_count=open_question_count,
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
        reputation_policy_version=memory.reputation_policy_version,
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
        locale_expansion_basis=_loads_list(memory.locale_expansion_basis_json),
        discovered_from_provider=memory.discovered_from_provider,
        first_seen_at=memory.first_seen_at,
        last_seen_at=memory.last_seen_at,
        last_reputation_event_at=memory.last_reputation_event_at,
        last_calibrated_at=memory.last_calibrated_at,
        latest_event_graph_at=memory.latest_event_graph_at,
        adversarial_risk_level=memory.adversarial_risk_level,  # type: ignore[arg-type]
        adversarial_signal_count=int(memory.adversarial_signal_count or 0),
        adversarial_signals=_loads_list(memory.adversarial_signals_json),
        latest_adversarial_scan_at=memory.latest_adversarial_scan_at,
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


def _serialize_runtime_run(row: RuntimeSchedulerRunORM) -> SourceDiscoveryRuntimeRunSummary:
    return SourceDiscoveryRuntimeRunSummary(
        run_id=row.run_id,
        worker_name=row.worker_name,  # type: ignore[arg-type]
        trigger_kind=row.trigger_kind,
        status=row.status,
        requested_by=row.requested_by,
        lease_owner=row.lease_owner,
        started_at=row.started_at,
        finished_at=row.finished_at,
        summary=row.summary,
        error_summary=row.error_summary,
    )


def _serialize_runtime_work_item(row: SourceRuntimeWorkItemORM) -> SourceDiscoveryRuntimeWorkItemSummary:
    return SourceDiscoveryRuntimeWorkItemSummary(
        work_item_id=row.work_item_id,
        worker_name=row.worker_name,  # type: ignore[arg-type]
        job_type=row.job_type,
        status=row.status,  # type: ignore[arg-type]
        source_id=row.source_id,
        seed_url=row.seed_url,
        domain_key=row.domain_key,
        provider_key=row.provider_key,
        shard_index=row.shard_index,
        shard_count=row.shard_count,
        dedupe_key=row.dedupe_key,
        priority_score=row.priority_score,
        next_run_at=row.next_run_at,
        lease_owner=row.lease_owner,
        lease_expires_at=row.lease_expires_at,
        attempt_count=row.attempt_count,
        max_attempts=row.max_attempts,
        request_budget=row.request_budget,
        last_failure_kind=row.last_failure_kind,  # type: ignore[arg-type]
        last_error=row.last_error,
        created_at=row.created_at,
        updated_at=row.updated_at,
        caveats=_loads_list(row.caveats_json),
    )


def _serialize_runtime_failure(row: SourceRuntimeWorkAttemptORM) -> SourceDiscoveryRuntimeFailureSummary:
    return SourceDiscoveryRuntimeFailureSummary(
        attempt_id=row.attempt_id,
        work_item_id=row.work_item_id,
        run_id=row.run_id,
        job_type=row.job_type,
        status=row.status,  # type: ignore[arg-type]
        failure_kind=row.failure_kind,  # type: ignore[arg-type]
        source_id=row.source_id,
        domain_key=row.domain_key,
        provider_key=row.provider_key,
        attempt_index=row.attempt_index,
        started_at=row.started_at,
        finished_at=row.finished_at,
        used_requests=row.used_requests,
        summary=row.summary,
        error_summary=row.error_summary,
    )


def _coerce_job_summary(value: object) -> SourceDiscoveryJobSummary:
    if isinstance(value, SourceDiscoveryJobSummary):
        return value
    if isinstance(value, dict):
        return SourceDiscoveryJobSummary.model_validate(value)
    data = {
        "job_id": getattr(value, "job_id"),
        "job_type": getattr(value, "job_type"),
        "status": getattr(value, "status"),
        "seed_url": getattr(value, "seed_url", None),
        "wave_id": getattr(value, "wave_id", None),
        "wave_title": getattr(value, "wave_title", None),
        "discovered_source_ids": list(getattr(value, "discovered_source_ids", []) or []),
        "rejected_reason": getattr(value, "rejected_reason", None),
        "request_budget": int(getattr(value, "request_budget", 0) or 0),
        "used_requests": int(getattr(value, "used_requests", 0) or 0),
        "started_at": getattr(value, "started_at"),
        "finished_at": getattr(value, "finished_at", None),
        "caveats": list(getattr(value, "caveats", []) or []),
    }
    return SourceDiscoveryJobSummary.model_validate(data)


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


def _serialize_adversarial_finding(row: SourceAdversarialFindingORM) -> SourceDiscoveryAdversarialFindingSummary:
    return SourceDiscoveryAdversarialFindingSummary(
        finding_id=row.finding_id,
        source_id=row.source_id,
        snapshot_id=row.snapshot_id,
        job_id=row.job_id,
        surface_type=row.surface_type,
        signal_type=row.signal_type,
        risk_level=row.risk_level,  # type: ignore[arg-type]
        summary=row.summary,
        matched_text=row.matched_text,
        detected_at=row.detected_at,
        status=row.status,  # type: ignore[arg-type]
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
        retrieval_origin=snapshot.retrieval_origin,  # type: ignore[arg-type]
        retrieved_from_url=snapshot.retrieved_from_url,
        resolved_original_url=snapshot.resolved_original_url,
        detected_language=snapshot.detected_language,
        normalization_notes=_loads_list(snapshot.normalization_notes_json),
        knowledge_node_id=snapshot.knowledge_node_id,
        canonical_snapshot_id=snapshot.canonical_snapshot_id,
        duplicate_class=snapshot.duplicate_class,  # type: ignore[arg-type]
        body_storage_mode=snapshot.body_storage_mode,  # type: ignore[arg-type]
        supporting_source_count=node.supporting_source_count if node is not None else 1,
        independent_source_count=node.independent_source_count if node is not None else 1,
        as_detailed_in_addition_to=_loads_list(node.as_detailed_in_addition_to_json) if node is not None else [],
        adversarial_risk_level=snapshot.adversarial_risk_level,  # type: ignore[arg-type]
        adversarial_signal_count=int(snapshot.adversarial_signal_count or 0),
        adversarial_signals=_loads_list(snapshot.adversarial_signals_json),
        caveats=_loads_list(snapshot.caveats_json),
    )


def _serialize_archive_hit(row: SourceArchiveHitORM) -> SourceDiscoveryArchiveHitSummary:
    return SourceDiscoveryArchiveHitSummary(
        archive_hit_id=row.archive_hit_id,
        source_id=row.source_id,
        provider=row.provider,
        original_url=row.original_url,
        archive_url=row.archive_url,
        captured_at=row.captured_at,
        discovered_at=row.discovered_at,
        caveats=_loads_list(row.caveats_json),
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


def _adversarial_findings_for_source(session: Session, source_id: str, *, limit: int) -> list[SourceAdversarialFindingORM]:
    return list(
        session.scalars(
            select(SourceAdversarialFindingORM)
            .where(SourceAdversarialFindingORM.source_id == source_id)
            .order_by(SourceAdversarialFindingORM.detected_at.desc(), SourceAdversarialFindingORM.finding_id.desc())
            .limit(max(0, limit))
        )
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
        policy_version=event.policy_version,
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


def _serialize_event_cluster(row: SourceEventClusterORM) -> SourceDiscoveryEventClusterSummary:
    return SourceDiscoveryEventClusterSummary(
        event_id=row.event_id,
        signature=row.signature,
        status=row.status,  # type: ignore[arg-type]
        claim_type=row.claim_type,
        canonical_claim_text=row.canonical_claim_text,
        observed_day=row.observed_day,
        wave_id=row.wave_id,
        knowledge_node_ids=_loads_list(row.knowledge_node_ids_json),
        media_cluster_ids=_loads_list(row.media_cluster_ids_json),
        member_source_ids=_loads_list(row.member_source_ids_json),
        supporting_source_count=row.supporting_source_count,
        contradiction_source_count=row.contradiction_source_count,
        corrective_source_count=row.corrective_source_count,
        open_question_count=row.open_question_count,
        first_seen_at=row.first_seen_at,
        last_seen_at=row.last_seen_at,
        caveats=_loads_list(row.caveats_json),
    )


def _serialize_event_member(row: SourceEventMemberORM) -> SourceDiscoveryEventMemberSummary:
    return SourceDiscoveryEventMemberSummary(
        member_id=row.member_id,
        event_id=row.event_id,
        source_id=row.source_id,
        wave_id=row.wave_id,
        role=row.role,  # type: ignore[arg-type]
        claim_text=row.claim_text,
        claim_type=row.claim_type,
        evidence_basis=row.evidence_basis,
        outcome=row.outcome,  # type: ignore[arg-type]
        observed_at=row.observed_at,
        snapshot_id=row.snapshot_id,
        knowledge_node_id=row.knowledge_node_id,
        media_cluster_id=row.media_cluster_id,
        claim_outcome_id=row.claim_outcome_id,
        claim_candidate_id=row.claim_candidate_id,
        source_class=row.source_class,  # type: ignore[arg-type]
        created_at=row.created_at,
        caveats=_loads_list(row.caveats_json),
    )


def _serialize_event_open_question(row: SourceEventOpenQuestionORM) -> SourceDiscoveryEventOpenQuestionSummary:
    return SourceDiscoveryEventOpenQuestionSummary(
        question_id=row.question_id,
        event_id=row.event_id,
        source_id=row.source_id,
        question_text=row.question_text,
        created_at=row.created_at,
        status=row.status,
        caveats=_loads_list(row.caveats_json),
    )


def _event_clusters_for_source(session: Session, source_id: str, *, limit: int | None = None) -> list[SourceDiscoveryEventClusterSummary]:
    event_ids = [
        row.event_id
        for row in session.scalars(
            select(SourceEventMemberORM)
            .where(SourceEventMemberORM.source_id == source_id)
            .order_by(SourceEventMemberORM.created_at.desc(), SourceEventMemberORM.member_id.desc())
        )
    ]
    unique_event_ids: list[str] = []
    seen: set[str] = set()
    for event_id in event_ids:
        if event_id not in seen:
            unique_event_ids.append(event_id)
            seen.add(event_id)
    if limit is not None:
        unique_event_ids = unique_event_ids[: max(0, limit)]
    events = [
        event
        for event in (session.get(SourceEventClusterORM, event_id) for event_id in unique_event_ids)
        if event is not None
    ]
    return [_serialize_event_cluster(event) for event in events]


def _event_clusters_for_knowledge_node(session: Session, node_id: str, *, limit: int | None = None) -> list[SourceDiscoveryEventClusterSummary]:
    events = list(
        session.scalars(
            select(SourceEventClusterORM)
            .order_by(SourceEventClusterORM.last_seen_at.desc(), SourceEventClusterORM.event_id.asc())
        )
    )
    filtered = [event for event in events if node_id in _loads_list(event.knowledge_node_ids_json)]
    if limit is not None:
        filtered = filtered[: max(0, limit)]
    return [_serialize_event_cluster(event) for event in filtered]


def _count_events_for_source_by_status(session: Session, source_id: str, statuses: set[str]) -> int:
    if not statuses:
        return 0
    event_ids = {
        row.event_id
        for row in session.scalars(
            select(SourceEventMemberORM).where(SourceEventMemberORM.source_id == source_id)
        )
    }
    if not event_ids:
        return 0
    return len(
        list(
            session.scalars(
                select(SourceEventClusterORM.event_id).where(
                    SourceEventClusterORM.event_id.in_(event_ids),
                    SourceEventClusterORM.status.in_(sorted(statuses)),
                )
            )
        )
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


def _dumps_scope_hints(scope_hints: SourceDiscoveryScopeHints | dict[str, Any] | None) -> str:
    return json.dumps(_normalize_scope_hints(scope_hints).model_dump())


def _adversarial_risk_value(level: str | None) -> int:
    return ADVERSARIAL_RISK_ORDER.get((level or "none").casefold(), 0)


def _highest_adversarial_risk(levels: list[str]) -> str:
    if not levels:
        return "none"
    return max(levels, key=_adversarial_risk_value)


def _truncate_match_excerpt(text: str | None, *, max_length: int = 220) -> str | None:
    if not text:
        return None
    compact = re.sub(r"\s+", " ", text).strip()
    if len(compact) <= max_length:
        return compact
    return compact[: max_length - 3].rstrip() + "..."


def _detect_adversarial_findings(
    text: str | None,
    *,
    url: str,
) -> list[dict[str, str]]:
    document = text or ""
    if not document.strip():
        return []
    findings: list[dict[str, str]] = []
    seen_signals: set[str] = set()
    for rule in ADVERSARIAL_FINDING_RULES:
        signal_type = str(rule["signal_type"])
        for pattern in list(rule["patterns"]):
            match = re.search(str(pattern), document, flags=re.IGNORECASE)
            if match is None:
                continue
            if signal_type in seen_signals:
                break
            seen_signals.add(signal_type)
            findings.append(
                {
                    "signal_type": signal_type,
                    "risk_level": str(rule["risk_level"]),
                    "summary": str(rule["summary"]),
                    "matched_text": _truncate_match_excerpt(document[max(0, match.start() - 60): min(len(document), match.end() + 120)]),
                }
            )
            break
    lowered = document.casefold()
    if (
        any(marker in lowered for marker in ("display:none", "display: none", "opacity:0", "font-size:0", "aria-hidden"))
        and any(finding["signal_type"] in {"instruction_override", "secret_request", "validation_bypass_request"} for finding in findings)
        and "hidden_instruction_text" not in seen_signals
    ):
        findings.append(
            {
                "signal_type": "hidden_instruction_text",
                "risk_level": "high",
                "summary": "Page appears to hide instruction-like text in markup or styling.",
                "matched_text": _truncate_match_excerpt(url),
            }
        )
    return findings


def _source_adversarial_review_reasons(memory: SourceMemoryORM) -> list[str]:
    signals = _loads_list(memory.adversarial_signals_json)
    if not signals:
        return []
    reasons = ["Prompt-injection or adversarial page behavior detected during source discovery or content capture."]
    if "secret_request" in signals:
        reasons.append("Suspicious text requested secrets, credentials, or hidden prompt material.")
    if "download_or_execute_request" in signals or "developer_tools_request" in signals:
        reasons.append("Suspicious text requested code execution, DevTools interaction, or shell steps.")
    if "validation_bypass_request" in signals:
        reasons.append("Suspicious text attempted to bypass review or promote trust directly.")
    return reasons


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


def _refresh_adversarial_posture(session: Session, *, source_id: str, snapshot_id: str | None, now: str) -> None:
    memory = session.get(SourceMemoryORM, source_id)
    source_rows = list(
        session.scalars(
            select(SourceAdversarialFindingORM)
            .where(
                SourceAdversarialFindingORM.source_id == source_id,
                SourceAdversarialFindingORM.status == "open",
            )
            .order_by(SourceAdversarialFindingORM.detected_at.desc(), SourceAdversarialFindingORM.finding_id.desc())
        )
    )
    if memory is not None:
        memory.latest_adversarial_scan_at = now
        memory.adversarial_signal_count = len(source_rows)
        memory.adversarial_signals_json = json.dumps(sorted({row.signal_type for row in source_rows}))
        memory.adversarial_risk_level = _highest_adversarial_risk([row.risk_level for row in source_rows])
    if snapshot_id:
        snapshot = session.get(SourceContentSnapshotORM, snapshot_id)
        if snapshot is not None:
            snapshot_rows = [row for row in source_rows if row.snapshot_id == snapshot_id]
            snapshot.adversarial_signal_count = len(snapshot_rows)
            snapshot.adversarial_signals_json = json.dumps(sorted({row.signal_type for row in snapshot_rows}))
            snapshot.adversarial_risk_level = _highest_adversarial_risk([row.risk_level for row in snapshot_rows])


def _record_adversarial_findings(
    session: Session,
    *,
    source_id: str,
    snapshot_id: str | None,
    job_id: str | None,
    surface_type: str,
    findings: list[dict[str, str]],
    now: str,
) -> list[SourceAdversarialFindingORM]:
    rows: list[SourceAdversarialFindingORM] = []
    for finding in findings:
        row = SourceAdversarialFindingORM(
            source_id=source_id,
            snapshot_id=snapshot_id,
            job_id=job_id,
            surface_type=surface_type,
            signal_type=finding["signal_type"],
            risk_level=finding["risk_level"],
            summary=finding["summary"],
            matched_text=finding.get("matched_text"),
            detected_at=now,
            status="open",
        )
        session.add(row)
        rows.append(row)
    session.flush()
    _refresh_adversarial_posture(session, source_id=source_id, snapshot_id=snapshot_id, now=now)
    memory = session.get(SourceMemoryORM, source_id)
    if memory is not None and findings:
        caveats = _loads_list(memory.caveats_json)
        caveats.append(f"Adversarial or prompt-injection signals detected during {surface_type}.")
        memory.caveats_json = json.dumps(sorted(set(caveats)))
    return rows


def _apply_adversarial_hold_review(memory: SourceMemoryORM, findings: list[dict[str, str]]) -> None:
    if not findings:
        return
    risk = _highest_adversarial_risk([finding["risk_level"] for finding in findings])
    if _adversarial_risk_value(risk) >= _adversarial_risk_value("medium") and memory.intake_disposition != "blocked":
        memory.intake_disposition = "hold_review"


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
    if seed.seed_family == "mailing_list_root":
        tags.update({"forum", "archive"})
    if seed.seed_family in {"archive_root", "archive_index"}:
        tags.add("archive")
    if seed.platform_family in {"discourse", "stack_exchange", "mailing_list"}:
        tags.add("forum")
    if seed.platform_family == "mailing_list":
        tags.add("archive")
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
    if seed.platform_family == "mailing_list":
        return "mailing_list_root"
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
        "mailing_list_root",
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
    if _is_scheduler_link_graph_candidate(memory, _utc_now()):
        return "link_graph_scan"
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
    elif _is_scheduler_link_graph_candidate(memory, now):
        score += 2
        basis.append("reviewed public root eligible for bounded link-graph expansion")
    if memory.source_type in {"rss", "sitemap", "dataset"}:
        score += 2
        basis.append("machine-readable discovery surface")
    structure_hints = set(_loads_list(memory.structure_hints_json))
    if structure_hints.intersection({"archive_or_latest_navigation", "category_navigation", "tag_navigation", "catalog_link"}):
        score += 2
        basis.append("structured archive or catalog navigation")
    if structure_hints.intersection({"association_link_page", "blogroll_navigation", "partner_links_navigation"}):
        score += 1
        basis.append("association or blogroll style root")
    scope_hints = _loads_scope_hints(memory.scope_hints_json)
    if scope_hints.spatial:
        score += 1
        basis.append("matches requested locality")
    if scope_hints.language:
        score += 1
        basis.append("matches requested source language")
    if scope_hints.topic:
        score += 1
        basis.append("explicit topic scope hints are present")
    locale_basis = _loads_list(memory.locale_expansion_basis_json)
    if locale_basis:
        score += 1
        basis.append("locale-expanded root")
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
    elif memory.platform_family == "mailing_list":
        score += 1
        basis.append("public mailing-list archive root")
    elif tags.intersection({"forum", "wiki", "status_page", "federated"}):
        score += 1
        basis.append("platform-specific long-tail root")
    if memory.seed_packet_id and tags.intersection({"regional", "local_news"}):
        basis.append("curated regional/local packet root")
    if "directory_scan" in _loads_list(memory.discovery_methods_json):
        score += 1
        basis.append("curated directory or regional portal root")
    if "link_graph_scan" in _loads_list(memory.discovery_methods_json):
        score += 1
        basis.append("trusted-root link-graph derived root")
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
    if int(memory.adversarial_signal_count or 0) > 0:
        score -= 3 if _adversarial_risk_value(memory.adversarial_risk_level) >= _adversarial_risk_value("high") else 2
        basis.append("root has adversarial or prompt-injection findings")
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
    elif action == "link_graph_scan" and _is_scheduler_link_graph_candidate(memory, now):
        reasons.append("eligible for bounded trusted-root link-graph expansion")
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
    if int(memory.adversarial_signal_count or 0) > 0:
        reasons.append("root has adversarial or prompt-injection findings")
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
    contested_event_count: int,
    open_question_count: int,
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
    if contested_event_count > 0:
        reasons.append("source participates in contested or corrected event clusters")
    if open_question_count > 0:
        reasons.append("source participates in open-question event clusters")
    reasons.extend(_source_adversarial_review_reasons(memory))
    if memory.discovery_role == "root":
        tags = set(_loads_list(memory.source_family_tags_json))
        if _loads_list(memory.locale_expansion_basis_json):
            reasons.append("locale-expanded root")
        if _loads_scope_hints(memory.scope_hints_json).language:
            reasons.append("matches requested source language")
        if _loads_scope_hints(memory.scope_hints_json).spatial:
            reasons.append("matches requested locality")
        if tags.intersection({"regional", "local_news"}):
            reasons.append("regional or local long-tail root")
        if memory.platform_family == "statuspage":
            reasons.append("official status or outage context root")
        elif memory.platform_family == "mastodon":
            reasons.append("federated/public-social discovery root")
        elif memory.platform_family == "stack_exchange":
            reasons.append("technical Q&A long-tail root")
        elif memory.platform_family == "mailing_list":
            reasons.append("public mailing-list archive root")
        elif tags.intersection({"forum", "wiki", "status_page", "federated"}):
            reasons.append("platform-specific long-tail root")
        if memory.seed_packet_id and tags.intersection({"regional", "local_news"}):
            reasons.append("curated regional/local packet root")
        if "directory_scan" in _loads_list(memory.discovery_methods_json):
            reasons.append("curated directory or regional portal root")
        if _is_scheduler_link_graph_candidate(memory, _utc_now()):
            reasons.append("reviewed public root eligible for bounded link-graph expansion")
        if set(_loads_list(memory.structure_hints_json)).intersection({"association_link_page", "blogroll_navigation", "partner_links_navigation"}):
            reasons.append("association or blogroll style root")
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
    contested_event_count: int,
    open_question_count: int,
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
    if contested_event_count > 0:
        score += 2
    if open_question_count > 0:
        score += 1
    if int(memory.adversarial_signal_count or 0) > 0:
        score += 3 if _adversarial_risk_value(memory.adversarial_risk_level) >= _adversarial_risk_value("high") else 2
    if memory.discovery_role == "root":
        tags = set(_loads_list(memory.source_family_tags_json))
        if _loads_list(memory.locale_expansion_basis_json):
            score += 1
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
        if _is_scheduler_link_graph_candidate(memory, _utc_now()):
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


def _is_link_graph_scan_allowed(memory: SourceMemoryORM) -> bool:
    return (
        memory.discovery_role == "root"
        and (memory.policy_state in {"reviewed", "approved"} or memory.lifecycle_state in {"approved-unvalidated", "sandboxed", "validated"})
        and memory.intake_disposition == "public_no_auth"
        and memory.auth_requirement == "no_auth"
        and memory.captcha_requirement == "no_captcha"
        and memory.lifecycle_state not in {"rejected", "archived"}
    )


def _is_scheduler_link_graph_candidate(memory: SourceMemoryORM, now: str) -> bool:
    return (
        _is_link_graph_scan_allowed(memory)
        and _public_discovery_followup_kind(memory) is None
        and _is_due_for_public_discovery(memory.next_discovery_scan_at, now)
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
        "mailing_list_archive",
        "month_index_navigation",
        "thread_navigation",
    }
    if memory.source_type == "dataset" and (
        memory.machine_readable_result in {"yes", "partial"}
        or bool(structure_hints.intersection(catalog_like_hints))
    ):
        return "catalog_scan"
    if memory.source_type in {"web", "unknown"} and bool(
        structure_hints.intersection(
            {
                "catalog_link",
                "status_history_navigation",
                "mastodon_instance_api",
                "mastodon_tag_navigation",
                "mastodon_account_navigation",
                "mailing_list_archive",
                "month_index_navigation",
                "thread_navigation",
            }
        )
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
            "mailing_list_archive",
            "month_index_navigation",
            "thread_navigation",
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
    if _detect_platform_family_from_url(url) == "mailing_list":
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
                "Public mailing-list archive root remains candidate-only until bounded archive structure is confirmed.",
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


def _normalize_archive_target_host(target_host: str) -> str | None:
    value = (target_host or "").strip()
    if not value:
        return None
    parsed = urlparse(value if "://" in value else f"https://{value}")
    host = (parsed.netloc or parsed.path or "").strip().casefold()
    if host.startswith("www."):
        host = host[4:]
    if not host or any(char.isspace() for char in host) or "." not in host:
        return None
    if "/" in host:
        host = host.split("/", 1)[0]
    return host or None


def _archive_seed_url(normalized_host: str | None, url_prefix: str | None) -> str | None:
    if url_prefix and url_prefix.strip():
        value = url_prefix.strip()
        if value.startswith("http://") or value.startswith("https://"):
            return _canonical_source_url(value)
        if normalized_host:
            if not value.startswith("/"):
                value = f"/{value}"
            return _canonical_source_url(f"https://{normalized_host}{value}")
    if normalized_host:
        return _canonical_source_url(f"https://{normalized_host}/")
    return None


def _archive_query_target(normalized_host: str, url_prefix: str | None) -> str:
    prefix = (url_prefix or "").strip()
    if prefix.startswith("http://") or prefix.startswith("https://"):
        return prefix
    if prefix:
        clean_prefix = prefix.lstrip("/")
        return f"{normalized_host}/{clean_prefix}*"
    return f"{normalized_host}/*"


def _fetch_archive_index_document(
    request: SourceDiscoveryArchiveIndexScanRequest,
    normalized_host: str,
) -> tuple[str, int]:
    provider = request.provider
    query_target = _archive_query_target(normalized_host, request.url_prefix)
    if provider == "wayback_cdx":
        params = {
            "url": query_target,
            "output": "json",
            "fl": "timestamp,original,statuscode,digest",
            "limit": str(max(1, request.max_results)),
        }
        if request.from_date:
            params["from"] = request.from_date
        if request.to_date:
            params["to"] = request.to_date
        url = f"https://web.archive.org/cdx/search/cdx?{urlencode(params)}"
        fetched = _fetch_url(url, method="GET", max_bytes=MAX_FETCH_BYTES)
        return str(fetched["body"]), 1
    if provider == "archive_it_cdx":
        params = {
            "url": query_target,
            "output": "json",
            "fl": "timestamp,original,statuscode,digest",
            "limit": str(max(1, request.max_results)),
        }
        if request.from_date:
            params["from"] = request.from_date
        if request.to_date:
            params["to"] = request.to_date
        url = f"https://wayback.archive-it.org/all/timemap/cdx?{urlencode(params)}"
        fetched = _fetch_url(url, method="GET", max_bytes=MAX_FETCH_BYTES)
        return str(fetched["body"]), 1
    if provider == "common_crawl_cdxj":
        meta = _fetch_url("https://index.commoncrawl.org/collinfo.json", method="GET", max_bytes=MAX_FETCH_BYTES)
        try:
            collections = json.loads(str(meta["body"]))
        except json.JSONDecodeError as exc:
            raise ValueError("Unable to parse Common Crawl collection metadata.") from exc
        latest_id = None
        if isinstance(collections, list):
            for item in collections:
                if not isinstance(item, dict):
                    continue
                latest_id = str(item.get("id") or "").strip()
                if latest_id:
                    break
        if not latest_id:
            raise ValueError("Common Crawl collection metadata did not expose a crawl id.")
        params = {
            "url": query_target,
            "output": "json",
            "limit": str(max(1, request.max_results)),
        }
        url = f"https://index.commoncrawl.org/{latest_id}-index?{urlencode(params)}"
        fetched = _fetch_url(url, method="GET", max_bytes=MAX_FETCH_BYTES)
        return str(fetched["body"]), 2
    if provider == "common_crawl_host_index":
        raise ValueError("common_crawl_host_index currently requires fixture_text in this slice.")
    raise ValueError(f"Unsupported archive index provider: {provider}")


def _archive_row_to_record(
    provider: str,
    payload: Any,
    *,
    target_host: str,
    url_prefix: str | None,
) -> _ArchiveDiscoveryRecord | None:
    prefix = (url_prefix or "").strip().casefold()
    original_url: str | None = None
    archive_url: str | None = None
    timestamp: str | None = None
    if isinstance(payload, dict):
        timestamp = _normalize_text(str(payload.get("timestamp") or payload.get("capture_ts") or payload.get("time") or ""))
        for key in ("original", "url", "original_url", "target_url", "homepage", "example_url"):
            value = payload.get(key)
            if isinstance(value, str) and value.strip():
                candidate = value.strip()
                if candidate.startswith("http://") or candidate.startswith("https://"):
                    original_url = candidate
                    break
        for key in ("archive_url", "archive", "capture_url", "wayback_url"):
            value = payload.get(key)
            if isinstance(value, str) and value.strip():
                archive_url = value.strip()
                break
        if original_url is None:
            host = str(payload.get("host") or payload.get("domain") or "").strip().casefold()
            if host and "." in host:
                original_url = f"https://{host}/"
    elif isinstance(payload, list):
        if payload and isinstance(payload[0], str) and any(token in payload[0].casefold() for token in ("timestamp", "original", "url")):
            return None
        values = [str(item).strip() for item in payload if str(item).strip()]
        if len(values) >= 2 and values[0].isdigit():
            timestamp = values[0]
            original_url = values[1]
        elif len(values) >= 2 and values[1].isdigit():
            original_url = values[0]
            timestamp = values[1]
        elif values:
            original_url = values[0]
    elif isinstance(payload, str):
        stripped = payload.strip()
        if not stripped:
            return None
        if stripped.startswith("http://") or stripped.startswith("https://"):
            original_url = stripped
        else:
            parts = stripped.split()
            if len(parts) >= 2 and parts[0].isdigit():
                timestamp = parts[0]
                original_url = parts[1]
            elif len(parts) >= 2 and parts[1].isdigit():
                original_url = parts[0]
                timestamp = parts[1]
            elif parts and "." in parts[0]:
                original_url = parts[0]
    if original_url:
        if not original_url.startswith(("http://", "https://")) and "." in original_url:
            original_url = f"https://{original_url.lstrip('/')}"
        original_url = _canonical_source_url(original_url)
    if archive_url:
        archive_url = _canonical_source_url(archive_url)
    candidate_url = original_url or archive_url
    if not candidate_url:
        return None
    parsed = urlparse(candidate_url)
    host = parsed.netloc.casefold()
    if host.startswith("www."):
        host = host[4:]
    if host and target_host and host != target_host and not host.endswith(f".{target_host}") and target_host not in host:
        return None
    if prefix and prefix not in candidate_url.casefold():
        return None
    return _ArchiveDiscoveryRecord(
        provider=provider,
        original_url=original_url,
        archive_url=archive_url,
        timestamp=timestamp or None,
    )


def _parse_archive_index_records(
    *,
    provider: str,
    text: str,
    target_host: str,
    url_prefix: str | None,
    max_results: int,
) -> list[_ArchiveDiscoveryRecord]:
    payload: Any = None
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        payload = None
    raw_rows: list[Any] = []
    if isinstance(payload, list):
        raw_rows = payload
    elif isinstance(payload, dict):
        for key in ("items", "captures", "records", "results"):
            value = payload.get(key)
            if isinstance(value, list):
                raw_rows = value
                break
        if not raw_rows:
            raw_rows = [payload]
    else:
        for line in text.splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.startswith("{") and stripped.endswith("}"):
                try:
                    raw_rows.append(json.loads(stripped))
                    continue
                except json.JSONDecodeError:
                    pass
            raw_rows.append(stripped)
    records: list[_ArchiveDiscoveryRecord] = []
    seen_urls: set[str] = set()
    for row in raw_rows:
        record = _archive_row_to_record(
            provider,
            row,
            target_host=target_host,
            url_prefix=url_prefix,
        )
        if record is None:
            continue
        unique_url = record.original_url or record.archive_url or ""
        if unique_url in seen_urls:
            continue
        seen_urls.add(unique_url)
        records.append(record)
        if len(records) >= max(0, max_results):
            break
    return records


def _archive_record_caveat(record: _ArchiveDiscoveryRecord) -> str:
    if record.timestamp:
        return f"Archive provenance recorded from {record.provider} capture at {record.timestamp}."
    return f"Archive provenance recorded from {record.provider}."


def _upsert_archive_hit_row(
    session: Session,
    *,
    source_id: str,
    record: _ArchiveDiscoveryRecord,
    now: str,
    caveats: list[str],
) -> SourceArchiveHitORM:
    existing = session.scalar(
        select(SourceArchiveHitORM).where(
            SourceArchiveHitORM.source_id == source_id,
            SourceArchiveHitORM.provider == record.provider,
            SourceArchiveHitORM.original_url == (record.original_url or record.archive_url or ""),
            SourceArchiveHitORM.archive_url == record.archive_url,
            SourceArchiveHitORM.captured_at == record.timestamp,
        )
    )
    row = existing or SourceArchiveHitORM(
        archive_hit_id=f"source-archive-hit:{_safe_id(source_id)}:{hashlib.sha1(json.dumps([record.provider, record.original_url, record.archive_url, record.timestamp]).encode('utf-8')).hexdigest()[:16]}",
        source_id=source_id,
        provider=record.provider,
        original_url=record.original_url or record.archive_url or "",
        archive_url=record.archive_url,
        captured_at=record.timestamp,
        discovered_at=now,
        caveats_json=json.dumps(caveats),
    )
    row.provider = record.provider
    row.original_url = record.original_url or record.archive_url or ""
    row.archive_url = record.archive_url
    row.captured_at = record.timestamp
    row.discovered_at = now
    row.caveats_json = json.dumps(sorted(set(_loads_list(row.caveats_json) + caveats)))
    session.add(row)
    return row


def _accent_fold(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value or "")
    return "".join(char for char in normalized if not unicodedata.combining(char))


def _generate_locale_aliases(raw_terms: list[str]) -> list[str]:
    aliases: list[str] = []
    seen: set[str] = set()
    for raw in raw_terms:
        term = _normalize_text(raw)
        if not term:
            continue
        candidates = {
            term,
            _accent_fold(term),
            term.replace("-", " "),
            term.replace(" ", "-"),
        }
        for candidate in candidates:
            normalized = _normalize_text(candidate)
            if not normalized:
                continue
            key = normalized.casefold()
            if key in seen:
                continue
            seen.add(key)
            aliases.append(normalized)
    return aliases


def _build_locale_queries(
    aliases: list[str],
    *,
    country_codes: list[str],
    language_codes: list[str],
    max_queries: int,
) -> list[str]:
    if max_queries <= 0:
        return []
    countries = [code.strip().casefold() for code in country_codes if code.strip()]
    languages = [code.strip().casefold() for code in language_codes if code.strip()]
    queries: list[str] = []
    for alias in aliases:
        base = f"\"{alias}\""
        variants = [base]
        if countries and languages:
            variants.extend(f"{base} sourcecountry:{country} sourcelang:{language}" for country in countries for language in languages)
        elif countries:
            variants.extend(f"{base} sourcecountry:{country}" for country in countries)
        elif languages:
            variants.extend(f"{base} sourcelang:{language}" for language in languages)
        for variant in variants:
            if variant not in queries:
                queries.append(variant)
            if len(queries) >= max_queries:
                return queries
    return queries[:max_queries]


def _locale_basis_lines(
    *,
    generated_aliases: list[str],
    country_codes: list[str],
    language_codes: list[str],
    place_labels: list[str],
) -> list[str]:
    basis: list[str] = []
    for alias in generated_aliases[:8]:
        basis.append(f"locale-alias:{alias}")
    for country in sorted({code.strip().casefold() for code in country_codes if code.strip()}):
        basis.append(f"source-country:{country}")
    for language in sorted({code.strip().casefold() for code in language_codes if code.strip()}):
        basis.append(f"source-language:{language}")
    for place in sorted({label.strip() for label in place_labels if label.strip()}):
        basis.append(f"place-label:{place}")
    return basis


def _fetch_gdelt_doc_payload(query: str, *, max_records: int) -> str:
    api_url = (
        "https://api.gdeltproject.org/api/v2/doc/doc?"
        + urlencode(
            {
                "query": query,
                "mode": "artlist",
                "format": "json",
                "sort": "datedesc",
                "maxrecords": max(1, min(max_records, 50)),
                "timespan": "1week",
            }
        )
    )
    fetched = _fetch_url(api_url, method="GET", max_bytes=MAX_FETCH_BYTES)
    return str(fetched["body"])


def _parse_gdelt_doc_candidates(text: str, *, max_hits: int) -> list[dict[str, str]]:
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return []
    if isinstance(payload, dict):
        raw_items = payload.get("articles") or payload.get("items") or payload.get("results") or []
    elif isinstance(payload, list):
        raw_items = payload
    else:
        raw_items = []
    candidates: list[dict[str, str]] = []
    for item in raw_items:
        if not isinstance(item, dict):
            continue
        url = (
            item.get("url")
            or item.get("sourceurl")
            or item.get("url_mobile")
            or item.get("urlmobile")
            or item.get("socialimage")
        )
        domain = str(item.get("domain") or "").strip()
        if not isinstance(url, str) or not url.strip():
            if domain:
                url = f"https://{domain}/"
            else:
                continue
        candidates.append(
            {
                "url": _canonical_source_url(url),
                "language": str(item.get("language") or item.get("source_lang") or "").strip().casefold(),
                "sourcecountry": str(item.get("sourcecountry") or item.get("source_country") or "").strip().casefold(),
            }
        )
        if len(candidates) >= max(0, max_hits):
            break
    return candidates


def _looks_like_discovery_surface_url(url: str) -> bool:
    lowered = url.casefold()
    path = urlparse(url).path.casefold()
    return (
        _looks_like_feed_or_data(lowered)
        or any(
            token in lowered
            for token in ("/sitemap", "/feed", "/rss", "/atom", "/api/", "/catalog", "/archive", "/latest", "/tag/", "/category/")
        )
        or path in {"/", "/news", "/latest", "/archive", "/feed", "/rss", "/sitemap.xml"}
    )


def _normalized_site_root(url: str) -> str:
    parsed = urlparse(url)
    return urlunparse((parsed.scheme, parsed.netloc, "/", "", "", ""))


def _locale_candidate_seeds_from_provider_results(
    candidates: list[dict[str, str]],
    *,
    wave_id: str | None,
    wave_title: str | None,
    packet_id: str | None,
    packet_title: str | None,
    source_family_tags: list[str],
    scope_hints: SourceDiscoveryScopeHints,
    locale_basis: list[str],
    max_domains: int,
    max_discovered: int,
    base_caveats: list[str],
) -> list[SourceDiscoveryCandidateSeed]:
    if max_discovered <= 0 or max_domains <= 0:
        return []
    seeds: list[SourceDiscoveryCandidateSeed] = []
    seen_urls: set[str] = set()
    seen_domains: set[str] = set()
    for candidate in candidates:
        raw_url = str(candidate.get("url") or "").strip()
        if not raw_url or _discovery_target_requires_auth_or_captcha(raw_url):
            continue
        target_url = raw_url if _looks_like_discovery_surface_url(raw_url) else _normalized_site_root(raw_url)
        canonical_url = _canonical_source_url(target_url)
        host = urlparse(canonical_url).netloc.casefold()
        if canonical_url in seen_urls:
            continue
        if host not in seen_domains and len(seen_domains) >= max_domains:
            continue
        seed = _candidate_seed_from_extracted_url(
            url=canonical_url,
            source_id=_generated_source_id_for_url(canonical_url),
            title=host or canonical_url,
            wave_id=wave_id,
            wave_title=wave_title,
            discovery_reason="locale/provider expansion",
            caveats=base_caveats + [f"Matched locale-provider article URL: {raw_url}"],
            discovery_methods=["locale_seed_expand"],
            structure_hints=["locale_expanded_root"],
        )
        if seed is None:
            continue
        seen_urls.add(canonical_url)
        seen_domains.add(host)
        language = str(candidate.get("language") or "").strip().casefold()
        merged_scope_hints = _merge_scope_hints(
            scope_hints,
            SourceDiscoveryScopeHints(language=[language] if language else []),
        )
        seeds.append(
            seed.model_copy(
                update={
                    "discovery_role": "root",
                    "seed_packet_id": packet_id,
                    "seed_packet_title": packet_title,
                    "source_family_tags": sorted(set(seed.source_family_tags + list(source_family_tags))),
                    "scope_hints": merged_scope_hints,
                    "locale_expansion_basis": locale_basis,
                    "discovered_from_provider": "gdelt_doc",
                }
            )
        )
        if len(seeds) >= max_discovered:
            break
    return seeds


def _archive_original_url_from_capture_url(url: str) -> str | None:
    value = (url or "").strip()
    if not value:
        return None
    match = re.search(r"/web/\d+(?:[a-z_]+)?/(https?://.+)$", value, flags=re.IGNORECASE)
    if match is not None:
        return _canonical_source_url(match.group(1))
    match = re.search(r"/all/\d+/https?://.+$", value, flags=re.IGNORECASE)
    if match is not None:
        http_index = value.casefold().find("http://")
        https_index = value.casefold().find("https://")
        start = min(index for index in [http_index, https_index] if index >= 0)
        return _canonical_source_url(value[start:])
    return None


def _strip_archive_chrome(html: str) -> str:
    cleaned = re.sub(r"(?is)<(?:script|style)[^>]*>.*?</(?:script|style)>", " ", html)
    cleaned = re.sub(
        r"(?is)<[^>]+(?:id|class)=[\"'][^\"']*(?:wm-ipp|wayback-toolbar|playback|donato)[^\"']*[\"'][^>]*>.*?</[^>]+>",
        " ",
        cleaned,
    )
    return cleaned


def _normalize_archive_capture_html(html: str, archive_url: str) -> tuple[str, str | None, list[str]]:
    notes: list[str] = []
    original_url = _archive_original_url_from_capture_url(archive_url)
    normalized_html = _strip_archive_chrome(html)
    if original_url:
        normalized_html = re.sub(
            r"https?://web\.archive\.org/web/\d+(?:[a-z_]+)?/(https?://[^\s\"'>]+)",
            lambda match: match.group(1),
            normalized_html,
            flags=re.IGNORECASE,
        )
        normalized_html = re.sub(
            r"https?://wayback\.archive-it\.org/\d+/https?://[^\s\"'>]+",
            original_url,
            normalized_html,
            flags=re.IGNORECASE,
        )
        notes.append("Archive wrapper URLs were normalized back to their original target URLs before extraction.")
    notes.append("Archive capture chrome was suppressed before article extraction.")
    return normalized_html, original_url, notes


def _is_allowed_archive_fetch_url(url: str) -> bool:
    host = urlparse(url).netloc.casefold()
    if host.startswith("www."):
        host = host[4:]
    return host in ALLOWED_ARCHIVE_FETCH_HOSTS


def _language_hint_from_url(url: str) -> str | None:
    host = urlparse(url).netloc.casefold()
    if host.endswith(".fr"):
        return "fr"
    if host.endswith(".de"):
        return "de"
    if host.endswith(".es"):
        return "es"
    if host.endswith(".pt"):
        return "pt"
    if host.endswith(".it"):
        return "it"
    if host.endswith(".jp"):
        return "ja"
    if host.endswith(".ru"):
        return "ru"
    if host.endswith(".ua"):
        return "uk"
    return None


def _detect_language_hint(html: str, *, candidate_url: str) -> str | None:
    lowered = html.casefold()
    match = re.search(r"""<html[^>]*\blang=["']([a-z]{2,12}(?:-[a-z]{2,12})?)["']""", lowered, flags=re.IGNORECASE)
    if match is not None:
        return match.group(1).split("-", 1)[0].casefold()
    match = re.search(r"""(?:property|name)=["']og:locale["'][^>]*content=["']([a-z]{2,12}(?:[_-][a-z]{2,12})?)["']""", lowered, flags=re.IGNORECASE)
    if match is not None:
        return match.group(1).split("_", 1)[0].split("-", 1)[0].casefold()
    json_ld_language = re.search(r'''"inLanguage"\s*:\s*"([a-z]{2,12}(?:-[a-z]{2,12})?)"''', html, flags=re.IGNORECASE)
    if json_ld_language is not None:
        return json_ld_language.group(1).split("-", 1)[0].casefold()
    return _language_hint_from_url(candidate_url)


def _discovery_target_requires_auth_or_captcha(url: str) -> bool:
    lowered = f"{urlparse(url).path}?{urlparse(url).query}".casefold()
    return any(
        token in lowered
        for token in (
            "login",
            "signin",
            "sign-in",
            "auth",
            "oauth",
            "captcha",
            "recaptcha",
            "hcaptcha",
            "cf-chl",
            "register",
            "subscribe",
            "private",
        )
    )


def _directory_scan_excluded_url(url: str) -> bool:
    lowered = f"{urlparse(url).path}?{urlparse(url).query}".casefold()
    return any(
        token in lowered
        for token in (
            "login",
            "signin",
            "sign-in",
            "register",
            "auth",
            "oauth",
            "captcha",
            "/search",
            "search?",
            "remote_interaction",
            "share",
            "sharer",
            "intent/tweet",
            "mailto:",
            "javascript:",
        )
    )


def _extract_visible_directory_links(base_url: str, text: str) -> list[str]:
    targets = re.findall(r"""href=["']([^"']+)["']""", text or "", flags=re.IGNORECASE)
    urls: list[str] = []
    for target in targets:
        absolute = urljoin(base_url, target.strip()).split("#", 1)[0]
        if absolute and absolute not in urls:
            urls.append(absolute)
    return urls


def _normalize_directory_seed_target(url: str) -> str:
    parsed = urlparse(url)
    lowered = url.casefold()
    if _looks_like_feed_or_data(lowered) or parsed.path.casefold().startswith("/api/"):
        return _canonical_source_url(url)
    return urlunparse((parsed.scheme, parsed.netloc, "/", "", "", ""))


def _auto_directory_type(base_url: str, text: str) -> str:
    lowered = f"{base_url}\n{text}".casefold()
    if any(token in lowered for token in ("regional", "local news", "county", "city", "town")):
        return "regional_portal"
    if any(token in lowered for token in ("association", "member organizations", "partners", "institutions")):
        return "association_links"
    return "curated_directory"


def _extract_directory_candidate_urls(
    base_url: str,
    text: str,
    *,
    directory_type: str,
    max_external_domains: int,
    max_discovered: int,
) -> tuple[list[str], str, int]:
    resolved_directory_type = directory_type if directory_type != "auto" else _auto_directory_type(base_url, text)
    base_host = urlparse(base_url).netloc.casefold()
    discovered: list[str] = []
    seen_domains: set[str] = set()
    seen_urls: set[str] = set()
    for absolute in _extract_visible_directory_links(base_url, text):
        parsed = urlparse(absolute)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            continue
        host = parsed.netloc.casefold()
        if host == base_host or _directory_scan_excluded_url(absolute):
            continue
        normalized = _normalize_directory_seed_target(absolute)
        normalized_host = urlparse(normalized).netloc.casefold()
        if normalized in seen_urls:
            continue
        if normalized_host not in seen_domains and len(seen_domains) >= max(1, max_external_domains):
            continue
        seen_urls.add(normalized)
        seen_domains.add(normalized_host)
        discovered.append(normalized)
        if len(discovered) >= max(1, max_discovered):
            break
    return discovered, resolved_directory_type, len(seen_domains)


def _link_graph_excluded_url(url: str) -> bool:
    parsed = urlparse(url)
    lowered = f"{parsed.path}?{parsed.query}".casefold()
    if any(
        token in lowered
        for token in (
            "login",
            "signin",
            "sign-in",
            "register",
            "auth",
            "oauth",
            "share",
            "intent/",
            "remote_interaction",
            "/search",
            "search?",
            "captcha",
            "mailto:",
            "javascript:",
        )
    ):
        return True
    return any(parsed.path.casefold().endswith(ext) for ext in (".pdf", ".zip", ".gz", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx"))


def _is_article_like_path(path: str) -> bool:
    lowered = path.casefold()
    if re.search(r"/\d{4}/\d{1,2}/", lowered):
        return True
    if any(token in lowered for token in ("/article", "/articles/", "/story", "/stories/", "/post", "/posts/", "/news/")):
        return True
    if _is_stack_exchange_question_path(lowered) or _is_mastodon_status_path(lowered) or _is_mailing_list_message_path(lowered):
        return True
    return False


def _is_root_like_navigation_path(path: str) -> bool:
    lowered = path.casefold().rstrip("/") or "/"
    return any(
        token in lowered
        for token in (
            "/feed",
            "/rss",
            "/atom",
            "/sitemap",
            "/api/",
            "/catalog",
            "/archive",
            "/latest",
            "/category/",
            "/tag/",
            "/tags/",
            "/forum",
            "/forums",
            "/community",
            "/wiki",
            "/status",
            "/resources",
            "/links",
            "/partners",
            "/members",
            "/sources",
            "/directory",
            "/blogroll",
        )
    )


def _normalize_link_graph_target(url: str) -> str | None:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return None
    if _link_graph_excluded_url(url) or _discovery_target_requires_auth_or_captcha(url):
        return None
    path = parsed.path or "/"
    normalized = _canonical_source_url(url)
    if _looks_like_discovery_surface_url(url) or _is_root_like_navigation_path(path) or _detect_platform_family_from_url(url) != "unknown":
        return normalized
    if _is_article_like_path(path):
        return None
    segments = [segment for segment in path.split("/") if segment]
    if len(segments) <= 2:
        return _normalized_site_root(normalized)
    return None


def _link_graph_page_hints(base_url: str, text: str) -> list[str]:
    lowered = f"{base_url}\n{text}".casefold()
    hints = ["linked_root_candidate", "trusted_root_link_graph"]
    if any(token in lowered for token in ("association", "member organizations", "member sites", "member institutions")):
        hints.append("association_link_page")
    if any(token in lowered for token in ("blogroll", "recommended blogs", "source links", "links page")):
        hints.append("blogroll_navigation")
    if any(token in lowered for token in ("partners", "partner organizations", "resources", "resource links")):
        hints.append("partner_links_navigation")
    return sorted(set(hints))


def _extract_link_graph_candidate_urls(
    base_url: str,
    text: str,
    *,
    max_same_domain: int,
    max_external_domains: int,
    max_discovered: int,
) -> tuple[list[str], int, int, list[str]]:
    if max_discovered <= 0:
        return [], 0, 0, _link_graph_page_hints(base_url, text)
    raw_links = _extract_visible_directory_links(base_url, text)
    base_domain = urlparse(base_url).netloc.casefold()
    discovered: list[str] = []
    seen_urls: set[str] = set()
    seen_external_domains: set[str] = set()
    same_domain_count = 0
    for raw_link in raw_links:
        normalized = _normalize_link_graph_target(raw_link)
        if not normalized or normalized in seen_urls:
            continue
        host = urlparse(normalized).netloc.casefold()
        if host == base_domain:
            if same_domain_count >= max(0, max_same_domain):
                continue
            same_domain_count += 1
        else:
            if host not in seen_external_domains and len(seen_external_domains) >= max(0, max_external_domains):
                continue
            seen_external_domains.add(host)
        seen_urls.add(normalized)
        discovered.append(normalized)
        if len(discovered) >= max_discovered:
            break
    discovered_domain_count = len({urlparse(url).netloc.casefold() for url in discovered})
    return discovered, len(raw_links), discovered_domain_count, _link_graph_page_hints(base_url, text)


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
    if any(token in host for token in ("lists.", "mailman.", "hyperkitty.")) or any(
        token in path
        for token in (
            "/hyperkitty/",
            "/pipermail/",
            "/mailman/",
            "/archives/list/",
            "/archives/public/",
            "/mailman3/",
        )
    ):
        return "mailing_list"
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
    if (
        "hyperkitty" in lowered_html
        or "pipermail" in lowered_html
        or "mailman 3" in lowered_html
        or "mailman archive" in lowered_html
        or "list-id" in lowered_html and "archives" in lowered_html
    ):
        return "mailing_list"
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
    if platform_family in {"discourse", "mediawiki", "mastodon", "stack_exchange", "mailing_list"}:
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


def _mailing_list_excluded_url(url: str) -> bool:
    lowered = f"{urlparse(url).path}?{urlparse(url).query}".casefold()
    return any(
        token in lowered
        for token in (
            "subscribe",
            "unsubscribe",
            "login",
            "auth",
            "private",
            "attachment",
            "reply",
            "post",
            "admin",
            "options",
        )
    )


def _is_mailing_list_list_home_path(path: str) -> bool:
    return re.search(r"^/(?:archives/list/[^/?#]+|hyperkitty/list/[^/?#]+)(?:/)?$", path, flags=re.IGNORECASE) is not None


def _is_mailing_list_month_path(path: str) -> bool:
    return re.search(
        r"^/(?:archives/list/[^/?#]+|hyperkitty/list/[^/?#]+)/(?:\d{4}/\d{1,2}|latest|recent|thread|month|bythread|date\.html)(?:/)?$",
        path,
        flags=re.IGNORECASE,
    ) is not None or re.search(
        r"^/pipermail/[^/?#]+/\d{4}-(?:[A-Za-z]+|\d{1,2})/?$",
        path,
        flags=re.IGNORECASE,
    ) is not None


def _is_mailing_list_thread_path(path: str) -> bool:
    return re.search(
        r"^/(?:archives/list/[^/?#]+|hyperkitty/list/[^/?#]+)/(?:thread|message)/",
        path,
        flags=re.IGNORECASE,
    ) is not None or re.search(
        r"^/pipermail/[^/?#]+/\d{4}-(?:[A-Za-z]+|\d{1,2})/thread\.html$",
        path,
        flags=re.IGNORECASE,
    ) is not None


def _is_mailing_list_message_path(path: str) -> bool:
    return re.search(
        r"^/(?:archives/list/[^/?#]+/message|hyperkitty/list/[^/?#]+/message)/[^/?#]+/?$",
        path,
        flags=re.IGNORECASE,
    ) is not None or re.search(
        r"^/pipermail/[^/?#]+/\d{4}-(?:[A-Za-z]+|\d{1,2})/\d+\.html$",
        path,
        flags=re.IGNORECASE,
    ) is not None


def _mailing_list_archive_key(path: str) -> str | None:
    match = re.search(r"^/(?:archives/list|hyperkitty/list)/([^/?#]+)/", path, flags=re.IGNORECASE)
    if match is not None:
        return match.group(1).casefold()
    match = re.search(r"^/pipermail/([^/?#]+)/", path, flags=re.IGNORECASE)
    if match is not None:
        return match.group(1).casefold()
    return None


def _extract_mailing_list_root_urls(base_url: str, html_text: str) -> list[str]:
    urls: list[str] = []
    for absolute in _same_origin_links(base_url, html_text):
        if _mailing_list_excluded_url(absolute):
            continue
        path = urlparse(absolute).path
        if _is_mailing_list_list_home_path(path) or _is_mailing_list_month_path(path) or _is_mailing_list_thread_path(path):
            urls.append(_canonical_source_url(absolute))
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
        if _is_mailing_list_list_home_path(path):
            hints.update({"catalog_link", "mailing_list_archive"})
        if _is_mailing_list_month_path(path):
            hints.update({"catalog_link", "mailing_list_archive", "month_index_navigation"})
        if _is_mailing_list_thread_path(path):
            hints.update({"catalog_link", "thread_navigation"})
        if _is_mailing_list_message_path(path):
            hints.add("message_navigation")
    return sorted(hints)


def _apply_platform_seed_overrides(
    seed: SourceDiscoveryCandidateSeed,
    *,
    url: str,
    platform_family: str,
    discovery_method: str,
) -> SourceDiscoveryCandidateSeed:
    if platform_family not in {"mastodon", "statuspage", "stack_exchange", "mailing_list"}:
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
    elif platform_family == "mailing_list":
        tags.update({"forum", "archive"})
        hints.update({"platform_mailing_list", "mailing_list_archive"})
        updates["source_class"] = "community"
        if _is_mailing_list_list_home_path(path):
            hints.update({"catalog_link", "mailing_list_archive"})
            updates["discovery_role"] = "root"
        elif _is_mailing_list_month_path(path):
            hints.update({"catalog_link", "mailing_list_archive", "month_index_navigation"})
            updates["discovery_role"] = "root"
        elif _is_mailing_list_thread_path(path):
            hints.update({"catalog_link", "thread_navigation"})
            updates["discovery_role"] = "candidate"
        elif _is_mailing_list_message_path(path):
            hints.add("message_navigation")
            updates["discovery_role"] = "candidate"
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
    if platform_family == "mailing_list":
        return [], _extract_mailing_list_root_urls(target_url, html_text), ["forum_platform", "platform_mailing_list", "mailing_list_archive"]
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
    discovered: list[str] = []
    for value in urls:
        absolute = urljoin(base_url, value.strip())
        if _discovery_target_requires_auth_or_captcha(absolute):
            continue
        discovered.append(absolute)
    return _dedupe_urls(discovered)


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
    if any(_is_mailing_list_list_home_path(urlparse(url).path) for url in navigation_urls):
        hints.append("mailing_list_archive")
    if any(_is_mailing_list_month_path(urlparse(url).path) for url in navigation_urls):
        hints.append("month_index_navigation")
    if any(_is_mailing_list_thread_path(urlparse(url).path) for url in navigation_urls):
        hints.append("thread_navigation")
    if any(_is_mailing_list_message_path(urlparse(url).path) for url in navigation_urls):
        hints.append("message_navigation")
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
    if active_platform_family == "mailing_list":
        urls = _collect_urls_from_object(payload) if payload is not None else _extract_candidate_links(base_url, text)
        return _bounded_mailing_list_candidate_urls(base_url, urls, max_discovered=max_discovered), "json" if payload is not None else "html"
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


def _bounded_mailing_list_candidate_urls(base_url: str, urls: list[str], *, max_discovered: int) -> list[str]:
    discovered: list[str] = []
    parsed_base = urlparse(base_url)
    base_domain = parsed_base.netloc.casefold()
    base_path = parsed_base.path.casefold()
    base_archive_key = _mailing_list_archive_key(base_path)
    for url in urls:
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"} or parsed.netloc.casefold() != base_domain:
            continue
        normalized = _canonical_source_url(url)
        if normalized in discovered or _mailing_list_excluded_url(normalized):
            continue
        path = parsed.path.casefold()
        candidate_archive_key = _mailing_list_archive_key(path)
        if base_archive_key and candidate_archive_key and base_archive_key != candidate_archive_key:
            continue
        same_archive_tree = (
            base_path.rstrip("/") == ""
            or path.startswith(base_path.rstrip("/") + "/")
            or base_path.startswith(path.rstrip("/") + "/")
            or (_is_mailing_list_list_home_path(base_path) and (_is_mailing_list_month_path(path) or _is_mailing_list_thread_path(path) or _is_mailing_list_message_path(path)))
            or (_is_mailing_list_month_path(base_path) and (_is_mailing_list_thread_path(path) or _is_mailing_list_message_path(path)))
        )
        if not same_archive_tree:
            continue
        if not (
            _is_mailing_list_list_home_path(path)
            or _is_mailing_list_month_path(path)
            or _is_mailing_list_thread_path(path)
            or _is_mailing_list_message_path(path)
        ):
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


def _isoformat_utc(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _compact_timestamp(value: str) -> str:
    return re.sub(r"[^0-9]", "", value)[:20]


def _safe_id(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9]+", "-", value).strip("-").lower() or "unknown"
