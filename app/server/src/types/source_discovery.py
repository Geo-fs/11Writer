from __future__ import annotations

from typing import Literal

from pydantic import Field

from src.types.api import CamelModel
from src.types.wave_monitor import WaveLlmExecutionSummary


SourceClass = Literal[
    "static",
    "live",
    "article",
    "social_image",
    "official",
    "community",
    "dataset",
    "unknown",
]
ClaimOutcome = Literal[
    "confirmed",
    "contradicted",
    "corrected",
    "outdated",
    "unresolved",
    "not_applicable",
]


class SourceDiscoveryMemory(CamelModel):
    source_id: str
    title: str
    url: str
    canonical_url: str
    parent_domain: str
    domain_scope: str
    owner_lane: str | None = None
    source_type: str
    source_class: SourceClass
    lifecycle_state: str
    source_health: str
    policy_state: str
    access_result: str
    machine_readable_result: str
    global_reputation_score: float
    domain_reputation_score: float
    source_health_score: float
    timeliness_score: float
    correction_score: float
    confidence_level: str
    claim_outcomes: dict[str, int]
    caveats: list[str] = Field(default_factory=list)
    reputation_basis: list[str] = Field(default_factory=list)
    known_aliases: list[str] = Field(default_factory=list)
    first_seen_at: str
    last_seen_at: str
    last_reputation_event_at: str | None = None
    next_check_at: str | None = None
    health_check_fail_count: int = 0


class SourceDiscoveryWaveFit(CamelModel):
    source_id: str
    wave_id: str
    wave_title: str
    fit_score: float
    fit_state: str
    relevance_basis: list[str] = Field(default_factory=list)
    last_seen_at: str


class SourceDiscoveryClaimOutcomeRequest(CamelModel):
    source_id: str
    wave_id: str | None = None
    claim_text: str
    claim_type: str = "state"
    outcome: ClaimOutcome
    evidence_basis: str = "contextual"
    observed_at: str | None = None
    corroborating_source_ids: list[str] = Field(default_factory=list)
    contradiction_source_ids: list[str] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


class SourceDiscoveryCandidateSeed(CamelModel):
    source_id: str
    title: str
    url: str
    parent_domain: str
    source_type: str
    source_class: SourceClass = "unknown"
    wave_id: str | None = None
    wave_title: str | None = None
    lifecycle_state: str = "candidate"
    source_health: str = "unknown"
    policy_state: str = "manual_review"
    access_result: str = "unknown"
    machine_readable_result: str = "unknown"
    wave_fit_score: float = 0.5
    relevance_basis: list[str] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


class SourceDiscoverySeedUrlJobRequest(CamelModel):
    seed_url: str
    wave_id: str | None = None
    wave_title: str | None = None
    discovery_reason: str = "explicit seed URL"
    source_id: str | None = None
    title: str | None = None
    request_budget: int = 1
    caveats: list[str] = Field(default_factory=list)


class SourceDiscoveryJobSummary(CamelModel):
    job_id: str
    job_type: str
    status: str
    seed_url: str | None = None
    wave_id: str | None = None
    wave_title: str | None = None
    discovered_source_ids: list[str] = Field(default_factory=list)
    rejected_reason: str | None = None
    request_budget: int
    used_requests: int
    started_at: str
    finished_at: str | None = None
    caveats: list[str] = Field(default_factory=list)


class SourceDiscoveryFeedLinkScanRequest(CamelModel):
    feed_url: str
    wave_id: str | None = None
    wave_title: str | None = None
    discovery_reason: str = "bounded feed link scan"
    fixture_text: str | None = None
    max_items: int = 10
    max_discovered: int = 10
    capture_item_summaries: bool = True
    request_budget: int = 1
    caveats: list[str] = Field(default_factory=list)


class SourceDiscoveryFeedLinkScanResponse(CamelModel):
    job: SourceDiscoveryJobSummary
    memories: list[SourceDiscoveryMemory] = Field(default_factory=list)
    snapshots: list["SourceDiscoveryContentSnapshotSummary"] = Field(default_factory=list)
    feed_type: str
    feed_title: str | None = None
    scanned_item_count: int = 0
    extracted_url_count: int = 0
    caveats: list[str] = Field(default_factory=list)


class SourceDiscoveryCatalogScanRequest(CamelModel):
    catalog_url: str
    wave_id: str | None = None
    wave_title: str | None = None
    discovery_reason: str = "bounded catalog scan"
    fixture_text: str | None = None
    max_discovered: int = 10
    request_budget: int = 1
    caveats: list[str] = Field(default_factory=list)


class SourceDiscoveryCatalogScanResponse(CamelModel):
    job: SourceDiscoveryJobSummary
    memories: list[SourceDiscoveryMemory] = Field(default_factory=list)
    catalog_type: str
    extracted_url_count: int = 0
    caveats: list[str] = Field(default_factory=list)


class SourceDiscoveryHealthCheckRequest(CamelModel):
    source_id: str
    request_budget: int = 1
    next_check_after: str | None = None
    caveats: list[str] = Field(default_factory=list)


class SourceDiscoveryHealthCheckSummary(CamelModel):
    check_id: str
    source_id: str
    url: str
    status: str
    http_status: int | None = None
    content_type: str | None = None
    access_result: str
    machine_readable_result: str
    source_health: str
    source_health_score: float
    request_budget: int
    used_requests: int
    checked_at: str
    next_check_after: str | None = None
    error_summary: str | None = None
    caveats: list[str] = Field(default_factory=list)


class SourceDiscoveryHealthCheckResponse(CamelModel):
    health_check: SourceDiscoveryHealthCheckSummary
    memory: SourceDiscoveryMemory
    caveats: list[str] = Field(default_factory=list)


class SourceDiscoveryExpansionJobRequest(CamelModel):
    seed_url: str
    wave_id: str | None = None
    wave_title: str | None = None
    discovery_reason: str = "bounded feed/catalog expansion"
    candidate_urls: list[str] = Field(default_factory=list)
    fixture_text: str | None = None
    max_discovered: int = 10
    request_budget: int = 1
    caveats: list[str] = Field(default_factory=list)


class SourceDiscoveryExpansionJobResponse(CamelModel):
    job: SourceDiscoveryJobSummary
    memories: list[SourceDiscoveryMemory] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


class SourceDiscoveryRecordSourceExtractRequest(CamelModel):
    wave_monitor_limit: int = 10
    wave_monitor_monitor_id: str | None = None
    data_ai_limit: int = 0
    data_ai_source_ids: list[str] = Field(default_factory=list)
    request_budget: int = 0
    caveats: list[str] = Field(default_factory=list)


class SourceDiscoveryRecordSourceExtractResponse(CamelModel):
    job: SourceDiscoveryJobSummary
    memories: list[SourceDiscoveryMemory] = Field(default_factory=list)
    scanned_record_count: int = 0
    extracted_url_count: int = 0
    caveats: list[str] = Field(default_factory=list)


class SourceDiscoveryContentSnapshotRequest(CamelModel):
    source_id: str
    url: str | None = None
    title: str | None = None
    raw_text: str | None = None
    html_text: str | None = None
    author: str | None = None
    published_at: str | None = None
    content_type: str | None = None
    request_budget: int = 1
    caveats: list[str] = Field(default_factory=list)


class SourceDiscoveryContentSnapshotSummary(CamelModel):
    snapshot_id: str
    source_id: str
    url: str
    title: str | None = None
    content_type: str | None = None
    extraction_method: str
    text_hash: str
    text_length: int
    author: str | None = None
    published_at: str | None = None
    fetched_at: str
    request_budget: int
    used_requests: int
    extraction_confidence: float
    caveats: list[str] = Field(default_factory=list)


class SourceDiscoveryContentSnapshotResponse(CamelModel):
    snapshot: SourceDiscoveryContentSnapshotSummary
    memory: SourceDiscoveryMemory
    caveats: list[str] = Field(default_factory=list)


class SourceDiscoveryArticleFetchRequest(CamelModel):
    source_id: str
    fixture_html: str | None = None
    fixture_text: str | None = None
    request_budget: int = 1
    caveats: list[str] = Field(default_factory=list)


class SourceDiscoveryArticleFetchResponse(CamelModel):
    job: SourceDiscoveryJobSummary
    snapshot: SourceDiscoveryContentSnapshotSummary | None = None
    memory: SourceDiscoveryMemory | None = None
    caveats: list[str] = Field(default_factory=list)


class SourceDiscoverySocialMetadataJobRequest(CamelModel):
    url: str
    source_id: str | None = None
    title: str | None = None
    wave_id: str | None = None
    wave_title: str | None = None
    fixture_html: str | None = None
    fixture_text: str | None = None
    request_budget: int = 1
    caveats: list[str] = Field(default_factory=list)


class SourceDiscoverySocialMetadataSummary(CamelModel):
    display_title: str | None = None
    description: str | None = None
    author: str | None = None
    published_at: str | None = None
    image_url: str | None = None
    media_hints: list[str] = Field(default_factory=list)
    media_urls: list[str] = Field(default_factory=list)
    alt_texts: list[str] = Field(default_factory=list)
    captions: list[str] = Field(default_factory=list)
    evidence_text: str | None = None
    canonical_url: str | None = None
    extraction_method: str | None = None


class SourceDiscoverySocialMetadataJobResponse(CamelModel):
    job: SourceDiscoveryJobSummary
    memory: SourceDiscoveryMemory | None = None
    snapshot: SourceDiscoveryContentSnapshotSummary | None = None
    metadata: SourceDiscoverySocialMetadataSummary
    caveats: list[str] = Field(default_factory=list)


class SourceDiscoveryReviewQueueItem(CamelModel):
    source_id: str
    title: str
    url: str
    source_class: SourceClass
    lifecycle_state: str
    policy_state: str
    source_health: str
    owner_lane: str | None = None
    priority: Literal["high", "medium", "low"]
    review_reasons: list[str] = Field(default_factory=list)
    recommended_actions: list[str] = Field(default_factory=list)
    global_reputation_score: float
    domain_reputation_score: float
    source_health_score: float
    timeliness_score: float
    confidence_level: str
    best_wave_id: str | None = None
    best_wave_title: str | None = None
    best_wave_fit_score: float | None = None
    next_check_at: str | None = None


class SourceDiscoveryReviewQueueResponse(CamelModel):
    metadata: dict[str, object]
    items: list[SourceDiscoveryReviewQueueItem] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


SourceDiscoveryReviewAction = Literal[
    "mark_reviewed",
    "approve_candidate",
    "sandbox_check",
    "reject",
    "archive",
    "assign_owner",
]


class SourceDiscoveryReviewActionRequest(CamelModel):
    source_id: str
    action: SourceDiscoveryReviewAction
    reviewed_by: str
    reason: str
    owner_lane: str | None = None


class SourceDiscoveryReviewActionSummary(CamelModel):
    review_action_id: int
    source_id: str
    action: SourceDiscoveryReviewAction
    reviewed_by: str
    reason: str
    owner_lane: str | None = None
    previous_lifecycle_state: str
    new_lifecycle_state: str
    previous_policy_state: str
    new_policy_state: str
    created_at: str


class SourceDiscoveryReviewActionResponse(CamelModel):
    action: SourceDiscoveryReviewActionSummary
    memory: SourceDiscoveryMemory
    caveats: list[str] = Field(default_factory=list)


class SourceDiscoveryReputationEventSummary(CamelModel):
    event_id: int
    source_id: str
    wave_id: str | None = None
    event_type: str
    outcome: str | None = None
    score_before: float
    score_after: float
    reason: str
    created_at: str
    reversed_at: str | None = None
    reversal_reason: str | None = None


class SourceDiscoveryReputationReversalRequest(CamelModel):
    event_id: int
    reason: str


class SourceDiscoveryReputationReversalResponse(CamelModel):
    reversed_event: SourceDiscoveryReputationEventSummary
    reversal_event: SourceDiscoveryReputationEventSummary | None = None
    memory: SourceDiscoveryMemory
    caveats: list[str] = Field(default_factory=list)


class SourceDiscoveryClaimOutcomeSummary(CamelModel):
    outcome_id: int
    source_id: str
    wave_id: str | None = None
    claim_text: str
    claim_type: str
    outcome: ClaimOutcome
    evidence_basis: str
    observed_at: str
    assessed_at: str
    corroborating_source_ids: list[str] = Field(default_factory=list)
    contradiction_source_ids: list[str] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


class SourceDiscoveryMemoryListResponse(CamelModel):
    metadata: dict[str, object]
    memories: list[SourceDiscoveryMemory] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


class SourceDiscoveryMemoryDetailResponse(CamelModel):
    memory: SourceDiscoveryMemory
    wave_fits: list[SourceDiscoveryWaveFit] = Field(default_factory=list)
    snapshots: list[SourceDiscoveryContentSnapshotSummary] = Field(default_factory=list)
    health_checks: list[SourceDiscoveryHealthCheckSummary] = Field(default_factory=list)
    review_actions: list[SourceDiscoveryReviewActionSummary] = Field(default_factory=list)
    reputation_events: list[SourceDiscoveryReputationEventSummary] = Field(default_factory=list)
    claim_outcomes: list[SourceDiscoveryClaimOutcomeSummary] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


class SourceDiscoveryMemoryExportPacket(CamelModel):
    export_type: str
    generated_at: str
    memory: SourceDiscoveryMemory
    wave_fits: list[SourceDiscoveryWaveFit] = Field(default_factory=list)
    snapshots: list[SourceDiscoveryContentSnapshotSummary] = Field(default_factory=list)
    health_checks: list[SourceDiscoveryHealthCheckSummary] = Field(default_factory=list)
    review_actions: list[SourceDiscoveryReviewActionSummary] = Field(default_factory=list)
    reputation_events: list[SourceDiscoveryReputationEventSummary] = Field(default_factory=list)
    claim_outcomes: list[SourceDiscoveryClaimOutcomeSummary] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


class SourceDiscoveryMemoryExportResponse(CamelModel):
    packet: SourceDiscoveryMemoryExportPacket
    caveats: list[str] = Field(default_factory=list)


class SourceDiscoverySchedulerTickRequest(CamelModel):
    health_check_limit: int = 5
    expansion_job_limit: int = 0
    record_source_extract_limit: int = 0
    llm_task_limit: int = 0
    llm_provider: str | None = None
    llm_allow_network: bool = False
    request_budget: int = 0
    caveats: list[str] = Field(default_factory=list)


class SourceDiscoverySchedulerTickResponse(CamelModel):
    tick_id: str
    status: str
    requested_at: str
    finished_at: str
    health_checks_completed: int
    expansion_jobs_completed: int
    record_extract_jobs_completed: int
    llm_tasks_completed: int
    request_budget: int
    used_requests: int
    health_checks: list[SourceDiscoveryHealthCheckSummary] = Field(default_factory=list)
    jobs: list[SourceDiscoveryJobSummary] = Field(default_factory=list)
    llm_executions: list[WaveLlmExecutionSummary] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


class SourceDiscoverySeedUrlJobResponse(CamelModel):
    job: SourceDiscoveryJobSummary
    memory: SourceDiscoveryMemory | None = None
    wave_fits: list[SourceDiscoveryWaveFit] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


class SourceDiscoveryMemoryOverviewResponse(CamelModel):
    metadata: dict[str, object]
    memories: list[SourceDiscoveryMemory]
    wave_fits: list[SourceDiscoveryWaveFit]
    recent_jobs: list[SourceDiscoveryJobSummary] = Field(default_factory=list)
    recent_reputation_events: list[SourceDiscoveryReputationEventSummary] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


class SourceDiscoveryClaimOutcomeResponse(CamelModel):
    memory: SourceDiscoveryMemory
    wave_fits: list[SourceDiscoveryWaveFit] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


SourceDiscoveryRuntimeWorkerName = Literal["source_discovery", "wave_monitor"]
SourceDiscoveryRuntimeWorkerDesiredState = Literal["running", "paused", "stopped"]
SourceDiscoveryRuntimeControlAction = Literal["pause", "resume", "stop", "run_now"]
SourceDiscoveryRuntimeServicePlatform = Literal["windows", "macos", "linux"]
SourceDiscoveryRuntimeServiceManager = Literal["task-scheduler", "launchd", "systemd-user"]


class SourceDiscoveryRuntimeRunSummary(CamelModel):
    run_id: str
    worker_name: SourceDiscoveryRuntimeWorkerName
    trigger_kind: str
    status: str
    requested_by: str | None = None
    lease_owner: str | None = None
    started_at: str
    finished_at: str | None = None
    summary: str | None = None
    error_summary: str | None = None


class SourceDiscoveryRuntimeWorkerSummary(CamelModel):
    worker_name: SourceDiscoveryRuntimeWorkerName
    desired_state: SourceDiscoveryRuntimeWorkerDesiredState
    enabled_by_config: bool
    poll_seconds: int
    loop_active_in_process: bool
    lease_owner: str | None = None
    lease_expires_at: str | None = None
    last_tick_requested_at: str | None = None
    last_tick_started_at: str | None = None
    last_tick_finished_at: str | None = None
    last_status: str | None = None
    last_error: str | None = None
    last_summary: str | None = None
    recent_runs: list[SourceDiscoveryRuntimeRunSummary] = Field(default_factory=list)


class SourceDiscoveryRuntimeControlRequest(CamelModel):
    action: SourceDiscoveryRuntimeControlAction
    requested_by: str
    caveats: list[str] = Field(default_factory=list)


class SourceDiscoveryRuntimeControlResponse(CamelModel):
    worker: SourceDiscoveryRuntimeWorkerSummary
    run: SourceDiscoveryRuntimeRunSummary | None = None
    caveats: list[str] = Field(default_factory=list)


class SourceDiscoveryRuntimeStatusResponse(CamelModel):
    runtime_mode: str
    recommended_runtime_deployment: str
    service_worker_entrypoint: str
    supported_service_managers: list[str] = Field(default_factory=list)
    source_discovery_scheduler_enabled: bool
    source_discovery_scheduler_running: bool
    source_discovery_scheduler_poll_seconds: int
    source_discovery_scheduler_last_tick_at: str | None = None
    source_discovery_scheduler_last_error: str | None = None
    source_discovery_scheduler_last_summary: str | None = None
    wave_monitor_scheduler_enabled: bool
    wave_monitor_scheduler_running: bool
    wave_monitor_scheduler_poll_seconds: int
    wave_monitor_scheduler_last_tick_at: str | None = None
    wave_monitor_scheduler_last_error: str | None = None
    wave_monitor_scheduler_last_summary: str | None = None
    workers: list[SourceDiscoveryRuntimeWorkerSummary] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


class SourceDiscoveryRuntimeServiceSpec(CamelModel):
    worker_name: SourceDiscoveryRuntimeWorkerName
    platform: SourceDiscoveryRuntimeServicePlatform
    service_manager: SourceDiscoveryRuntimeServiceManager
    service_name: str
    working_directory: str
    artifact_file_name: str
    artifact_text: str
    entry_command: list[str] = Field(default_factory=list)
    install_command: list[str] = Field(default_factory=list)
    uninstall_command: list[str] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


class SourceDiscoveryRuntimeServiceBundleResponse(CamelModel):
    runtime_mode: str
    current_platform: SourceDiscoveryRuntimeServicePlatform
    entrypoint_module: str
    services: list[SourceDiscoveryRuntimeServiceSpec] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


class SourceDiscoveryReviewClaimApplicationItem(CamelModel):
    claim_index: int
    outcome: ClaimOutcome
    caveats: list[str] = Field(default_factory=list)


class SourceDiscoveryReviewClaimApplicationRequest(CamelModel):
    review_id: str
    source_id: str | None = None
    approved_by: str
    approval_reason: str
    applications: list[SourceDiscoveryReviewClaimApplicationItem] = Field(default_factory=list)


class SourceDiscoveryReviewClaimApplicationSummary(CamelModel):
    application_id: int
    review_id: str
    task_id: str
    source_id: str
    wave_id: str | None = None
    claim_index: int
    claim_text: str
    outcome: ClaimOutcome
    applied_by: str
    approval_reason: str
    created_at: str


class SourceDiscoveryReviewClaimApplicationResponse(CamelModel):
    memory: SourceDiscoveryMemory
    applications: list[SourceDiscoveryReviewClaimApplicationSummary] = Field(default_factory=list)
    wave_fits: list[SourceDiscoveryWaveFit] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)
