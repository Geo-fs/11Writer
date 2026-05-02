from typing import Literal

from pydantic import Field

from src.types.api import CamelModel


WaveMonitorStatus = Literal["active", "paused", "archived"]
WaveMonitorFocusType = Literal["location", "keyword", "event", "mixed"]
WaveMonitorSourceHealth = Literal["loaded", "empty", "stale", "degraded", "error", "unknown"]
WaveMonitorEvidenceBasis = Literal[
    "observed",
    "derived",
    "scored",
    "advisory",
    "contextual",
    "fixture-local",
]
WaveMonitorSignalStatus = Literal["new", "reviewed", "tracked", "muted", "resolved"]
WaveMonitorSignalSeverity = Literal["low", "medium", "high"]
WaveMonitorLifecycleState = Literal[
    "candidate",
    "sandboxed",
    "approved-unvalidated",
    "validated",
    "degraded",
    "rejected",
    "archived",
]
WaveMonitorAction = Literal[
    "open-monitor",
    "inspect-evidence",
    "run-now",
    "pause",
    "resume",
    "approve-source",
    "reject-source",
    "mark-reviewed",
    "track",
    "export-packet",
    "move-on",
]
WaveLlmProvider = Literal[
    "fixture",
    "openai",
    "anthropic",
    "xai",
    "google",
    "openrouter",
    "ollama",
    "openclaw",
    "custom",
]


class WaveLlmProviderStatus(CamelModel):
    provider: WaveLlmProvider
    configured: bool
    key_source: str
    local: bool = False
    caveats: list[str] = Field(default_factory=list)


class WaveLlmCapabilityResponse(CamelModel):
    enabled: bool
    default_provider: str
    default_model: str
    providers: list[WaveLlmProviderStatus]
    guardrails: list[str] = Field(default_factory=list)


class WaveLlmInterpretationTaskRequest(CamelModel):
    monitor_id: str
    task_type: Literal["article_claim_extraction", "source_summary", "relationship_hypothesis"] = "article_claim_extraction"
    provider: WaveLlmProvider = "fixture"
    model: str | None = None
    input_text: str
    source_ids: list[str] = Field(default_factory=list)
    record_ids: list[str] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


class WaveLlmTaskSummary(CamelModel):
    task_id: str
    monitor_id: str
    task_type: str
    provider: str
    model: str
    status: str
    input_summary: str
    source_ids: list[str] = Field(default_factory=list)
    record_ids: list[str] = Field(default_factory=list)
    created_at: str
    completed_at: str | None = None
    caveats: list[str] = Field(default_factory=list)


class WaveLlmValidatedClaim(CamelModel):
    claim_text: str
    claim_type: str
    evidence_basis: str
    confidence: float
    status: Literal["accepted_for_review", "rejected"]
    rejection_reason: str | None = None


class WaveLlmReviewRequest(CamelModel):
    task_id: str
    raw_output: str
    provider: WaveLlmProvider = "fixture"
    model: str | None = None
    caveats: list[str] = Field(default_factory=list)


class WaveLlmTaskExecuteRequest(CamelModel):
    task_id: str
    allow_network: bool = False
    request_budget: int = 0
    max_retries: int | None = None
    caveats: list[str] = Field(default_factory=list)


class WaveLlmReviewSummary(CamelModel):
    review_id: str
    task_id: str
    monitor_id: str
    provider: str
    model: str
    validation_state: str
    claims: list[WaveLlmValidatedClaim] = Field(default_factory=list)
    proposed_actions: list[str] = Field(default_factory=list)
    risk_flags: list[str] = Field(default_factory=list)
    accepted_claim_count: int
    rejected_claim_count: int
    requires_human_review: bool
    created_at: str
    caveats: list[str] = Field(default_factory=list)


class WaveLlmInterpretationTaskResponse(CamelModel):
    task: WaveLlmTaskSummary
    guardrails: list[str] = Field(default_factory=list)


class WaveLlmReviewResponse(CamelModel):
    task: WaveLlmTaskSummary
    review: WaveLlmReviewSummary
    guardrails: list[str] = Field(default_factory=list)


class WaveLlmExecutionSummary(CamelModel):
    task_id: str
    provider: str
    model: str
    status: str
    adapter_status: str
    request_budget: int
    used_requests: int
    retry_count: int
    raw_output: str
    error_summary: str | None = None
    caveats: list[str] = Field(default_factory=list)


class WaveLlmExecutionResponse(CamelModel):
    task: WaveLlmTaskSummary
    execution: WaveLlmExecutionSummary
    review: WaveLlmReviewSummary | None = None
    guardrails: list[str] = Field(default_factory=list)


class WaveMonitorRuntimeIntegration(CamelModel):
    tool_name: str
    imported_project: str
    standalone_runtime_enabled: bool
    route_prefix: str
    storage_mode: str
    scheduler_mode: Literal["fixture-preview", "manual", "backend-only-ready"]
    caveats: list[str] = Field(default_factory=list)


class WaveMonitorSourceCandidate(CamelModel):
    source_id: str
    title: str
    url: str
    source_type: str
    parent_domain: str
    lifecycle_state: WaveMonitorLifecycleState
    source_health: WaveMonitorSourceHealth
    trust_tier: str
    relevance_score: float
    stability_score: float | None = None
    policy_state: str
    caveats: list[str] = Field(default_factory=list)


class WaveMonitorSignal(CamelModel):
    signal_id: str
    signal_type: str
    title: str
    summary: str
    severity: WaveMonitorSignalSeverity
    status: WaveMonitorSignalStatus
    evidence_basis: WaveMonitorEvidenceBasis
    source_ids: list[str] = Field(default_factory=list)
    relationship_reasons: list[str] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)
    available_actions: list[WaveMonitorAction] = Field(default_factory=list)


class WaveMonitorRunSummary(CamelModel):
    run_id: str
    status: Literal["success", "failed", "skipped"]
    started_at: str
    finished_at: str | None = None
    records_created: int
    source_checks_completed: int
    error_summary: str | None = None


class WaveMonitorRecordPreview(CamelModel):
    record_id: str
    title: str
    source_id: str
    source_name: str
    source_url: str | None = None
    event_time: str | None = None
    collected_at: str
    evidence_basis: WaveMonitorEvidenceBasis
    tags: list[str] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


class WaveMonitor(CamelModel):
    monitor_id: str
    title: str
    description: str
    status: WaveMonitorStatus
    focus_type: WaveMonitorFocusType
    source_mode: Literal["fixture", "live", "mixed", "disabled"]
    source_health: WaveMonitorSourceHealth
    evidence_basis: WaveMonitorEvidenceBasis
    connector_count: int
    record_count: int
    signal_count: int
    discovered_source_count: int
    last_run_at: str | None = None
    next_run_at: str | None = None
    caveats: list[str] = Field(default_factory=list)
    available_actions: list[WaveMonitorAction] = Field(default_factory=list)
    signals: list[WaveMonitorSignal] = Field(default_factory=list)
    source_candidates: list[WaveMonitorSourceCandidate] = Field(default_factory=list)
    recent_runs: list[WaveMonitorRunSummary] = Field(default_factory=list)
    recent_records: list[WaveMonitorRecordPreview] = Field(default_factory=list)


class WaveMonitorOverviewSummary(CamelModel):
    total_monitors: int
    active_monitors: int
    paused_monitors: int
    total_signals: int
    new_signals: int
    discovered_sources: int
    source_issues: int


class WaveMonitorOverviewResponse(CamelModel):
    metadata: dict[str, object]
    runtime: WaveMonitorRuntimeIntegration
    summary: WaveMonitorOverviewSummary
    monitors: list[WaveMonitor]
    caveats: list[str] = Field(default_factory=list)
    next_steps: list[str] = Field(default_factory=list)


class WaveMonitorRunResponse(CamelModel):
    monitor_id: str
    status: Literal["success", "failed", "skipped"]
    runs: list[WaveMonitorRunSummary] = Field(default_factory=list)
    records_created: int
    signals_created: int
    caveats: list[str] = Field(default_factory=list)


class WaveMonitorSchedulerTickResponse(CamelModel):
    scanned_connectors: int
    eligible_connectors: int
    successful_runs: int
    failed_runs: int
    records_created: int
    signals_created: int
    caveats: list[str] = Field(default_factory=list)
