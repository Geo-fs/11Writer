from __future__ import annotations

from sqlalchemy import Boolean, Float, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class SourceDiscoveryBase(DeclarativeBase):
    pass


class SourceMemoryORM(SourceDiscoveryBase):
    __tablename__ = "source_memories"

    source_id: Mapped[str] = mapped_column(String(160), primary_key=True)
    title: Mapped[str] = mapped_column(String(300))
    url: Mapped[str] = mapped_column(Text)
    canonical_url: Mapped[str] = mapped_column(String(1024), index=True)
    parent_domain: Mapped[str] = mapped_column(String(255), index=True)
    domain_scope: Mapped[str] = mapped_column(String(255), default="unknown", index=True)
    owner_lane: Mapped[str | None] = mapped_column(String(64), index=True)
    source_type: Mapped[str] = mapped_column(String(64), index=True)
    source_class: Mapped[str] = mapped_column(String(64), default="unknown", index=True)
    lifecycle_state: Mapped[str] = mapped_column(String(64), default="discovered", index=True)
    source_health: Mapped[str] = mapped_column(String(64), default="unknown", index=True)
    policy_state: Mapped[str] = mapped_column(String(64), default="manual_review", index=True)
    access_result: Mapped[str] = mapped_column(String(64), default="unknown", index=True)
    machine_readable_result: Mapped[str] = mapped_column(String(64), default="unknown", index=True)
    global_reputation_score: Mapped[float] = mapped_column(Float, default=0.5)
    domain_reputation_score: Mapped[float] = mapped_column(Float, default=0.5)
    source_health_score: Mapped[float] = mapped_column(Float, default=0.5)
    timeliness_score: Mapped[float] = mapped_column(Float, default=0.5)
    correction_score: Mapped[float] = mapped_column(Float, default=0.5)
    confidence_level: Mapped[str] = mapped_column(String(32), default="thin", index=True)
    confirmed_claim_count: Mapped[int] = mapped_column(Integer, default=0)
    contradicted_claim_count: Mapped[int] = mapped_column(Integer, default=0)
    corrected_claim_count: Mapped[int] = mapped_column(Integer, default=0)
    outdated_claim_count: Mapped[int] = mapped_column(Integer, default=0)
    unresolved_claim_count: Mapped[int] = mapped_column(Integer, default=0)
    not_applicable_claim_count: Mapped[int] = mapped_column(Integer, default=0)
    first_seen_at: Mapped[str] = mapped_column(String(64), index=True)
    last_seen_at: Mapped[str] = mapped_column(String(64), index=True)
    last_reputation_event_at: Mapped[str | None] = mapped_column(String(64), index=True)
    next_check_at: Mapped[str | None] = mapped_column(String(64), index=True)
    health_check_fail_count: Mapped[int] = mapped_column(Integer, default=0)
    caveats_json: Mapped[str] = mapped_column(Text, default="[]")
    reputation_basis_json: Mapped[str] = mapped_column(Text, default="[]")
    known_aliases_json: Mapped[str] = mapped_column(Text, default="[]")


class SourceWaveFitORM(SourceDiscoveryBase):
    __tablename__ = "source_wave_fits"
    __table_args__ = (
        UniqueConstraint("source_id", "wave_id", name="uq_source_wave_fit_source_wave"),
    )

    fit_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_id: Mapped[str] = mapped_column(String(160), index=True)
    wave_id: Mapped[str] = mapped_column(String(160), index=True)
    wave_title: Mapped[str] = mapped_column(String(300), default="")
    fit_score: Mapped[float] = mapped_column(Float, default=0.5)
    fit_state: Mapped[str] = mapped_column(String(64), default="candidate", index=True)
    relevance_basis_json: Mapped[str] = mapped_column(Text, default="[]")
    last_seen_at: Mapped[str] = mapped_column(String(64), index=True)


class SourceClaimOutcomeORM(SourceDiscoveryBase):
    __tablename__ = "source_claim_outcomes"

    outcome_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_id: Mapped[str] = mapped_column(String(160), index=True)
    wave_id: Mapped[str | None] = mapped_column(String(160), index=True)
    claim_text: Mapped[str] = mapped_column(Text)
    claim_type: Mapped[str] = mapped_column(String(64), default="state", index=True)
    outcome: Mapped[str] = mapped_column(String(64), index=True)
    evidence_basis: Mapped[str] = mapped_column(String(64), default="contextual", index=True)
    observed_at: Mapped[str] = mapped_column(String(64), index=True)
    assessed_at: Mapped[str] = mapped_column(String(64), index=True)
    corroborating_source_ids_json: Mapped[str] = mapped_column(Text, default="[]")
    contradiction_source_ids_json: Mapped[str] = mapped_column(Text, default="[]")
    caveats_json: Mapped[str] = mapped_column(Text, default="[]")


class SourceReviewClaimApplicationORM(SourceDiscoveryBase):
    __tablename__ = "source_review_claim_applications"
    __table_args__ = (
        UniqueConstraint("review_id", "source_id", "claim_index", name="uq_review_claim_application"),
    )

    application_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    review_id: Mapped[str] = mapped_column(String(180), index=True)
    task_id: Mapped[str] = mapped_column(String(180), index=True)
    source_id: Mapped[str] = mapped_column(String(160), index=True)
    wave_id: Mapped[str | None] = mapped_column(String(160), index=True)
    claim_index: Mapped[int] = mapped_column(Integer, index=True)
    claim_text: Mapped[str] = mapped_column(Text, default="")
    outcome: Mapped[str] = mapped_column(String(64), index=True)
    applied_by: Mapped[str] = mapped_column(String(160), index=True)
    approval_reason: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[str] = mapped_column(String(64), index=True)
    caveats_json: Mapped[str] = mapped_column(Text, default="[]")


class SourceReputationEventORM(SourceDiscoveryBase):
    __tablename__ = "source_reputation_events"

    event_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_id: Mapped[str] = mapped_column(String(160), index=True)
    wave_id: Mapped[str | None] = mapped_column(String(160), index=True)
    event_type: Mapped[str] = mapped_column(String(64), index=True)
    outcome: Mapped[str | None] = mapped_column(String(64), index=True)
    score_before: Mapped[float] = mapped_column(Float)
    score_after: Mapped[float] = mapped_column(Float)
    reason: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[str] = mapped_column(String(64), index=True)
    reversed_at: Mapped[str | None] = mapped_column(String(64), index=True)
    reversal_reason: Mapped[str | None] = mapped_column(Text)


class SourceDiscoveryJobORM(SourceDiscoveryBase):
    __tablename__ = "source_discovery_jobs"

    job_id: Mapped[str] = mapped_column(String(180), primary_key=True)
    job_type: Mapped[str] = mapped_column(String(64), index=True)
    status: Mapped[str] = mapped_column(String(64), index=True)
    seed_url: Mapped[str | None] = mapped_column(Text)
    wave_id: Mapped[str | None] = mapped_column(String(160), index=True)
    wave_title: Mapped[str | None] = mapped_column(String(300))
    discovered_source_ids_json: Mapped[str] = mapped_column(Text, default="[]")
    rejected_reason: Mapped[str | None] = mapped_column(Text)
    request_budget: Mapped[int] = mapped_column(Integer, default=1)
    used_requests: Mapped[int] = mapped_column(Integer, default=0)
    started_at: Mapped[str] = mapped_column(String(64), index=True)
    finished_at: Mapped[str | None] = mapped_column(String(64), index=True)
    caveats_json: Mapped[str] = mapped_column(Text, default="[]")


class SourceHealthCheckORM(SourceDiscoveryBase):
    __tablename__ = "source_health_checks"

    check_id: Mapped[str] = mapped_column(String(180), primary_key=True)
    source_id: Mapped[str] = mapped_column(String(160), index=True)
    url: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(64), index=True)
    http_status: Mapped[int | None] = mapped_column(Integer)
    content_type: Mapped[str | None] = mapped_column(String(255))
    access_result: Mapped[str] = mapped_column(String(64), index=True)
    machine_readable_result: Mapped[str] = mapped_column(String(64), index=True)
    source_health: Mapped[str] = mapped_column(String(64), index=True)
    source_health_score: Mapped[float] = mapped_column(Float, default=0.5)
    request_budget: Mapped[int] = mapped_column(Integer, default=1)
    used_requests: Mapped[int] = mapped_column(Integer, default=0)
    checked_at: Mapped[str] = mapped_column(String(64), index=True)
    next_check_after: Mapped[str | None] = mapped_column(String(64), index=True)
    error_summary: Mapped[str | None] = mapped_column(Text)
    caveats_json: Mapped[str] = mapped_column(Text, default="[]")


class SourceContentSnapshotORM(SourceDiscoveryBase):
    __tablename__ = "source_content_snapshots"

    snapshot_id: Mapped[str] = mapped_column(String(180), primary_key=True)
    source_id: Mapped[str] = mapped_column(String(160), index=True)
    url: Mapped[str] = mapped_column(Text)
    title: Mapped[str | None] = mapped_column(String(300))
    content_type: Mapped[str | None] = mapped_column(String(255))
    extraction_method: Mapped[str] = mapped_column(String(64), index=True)
    text_hash: Mapped[str] = mapped_column(String(80), index=True)
    text_length: Mapped[int] = mapped_column(Integer, default=0)
    full_text: Mapped[str] = mapped_column(Text, default="")
    author: Mapped[str | None] = mapped_column(String(255))
    published_at: Mapped[str | None] = mapped_column(String(64), index=True)
    fetched_at: Mapped[str] = mapped_column(String(64), index=True)
    request_budget: Mapped[int] = mapped_column(Integer, default=1)
    used_requests: Mapped[int] = mapped_column(Integer, default=0)
    extraction_confidence: Mapped[float] = mapped_column(Float, default=0.5)
    caveats_json: Mapped[str] = mapped_column(Text, default="[]")


class SourceReviewActionORM(SourceDiscoveryBase):
    __tablename__ = "source_review_actions"

    review_action_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_id: Mapped[str] = mapped_column(String(160), index=True)
    action: Mapped[str] = mapped_column(String(64), index=True)
    reviewed_by: Mapped[str] = mapped_column(String(160), index=True)
    reason: Mapped[str] = mapped_column(Text, default="")
    owner_lane: Mapped[str | None] = mapped_column(String(64), index=True)
    previous_lifecycle_state: Mapped[str] = mapped_column(String(64), default="")
    new_lifecycle_state: Mapped[str] = mapped_column(String(64), default="")
    previous_policy_state: Mapped[str] = mapped_column(String(64), default="")
    new_policy_state: Mapped[str] = mapped_column(String(64), default="")
    created_at: Mapped[str] = mapped_column(String(64), index=True)


class SourceSchedulerTickORM(SourceDiscoveryBase):
    __tablename__ = "source_scheduler_ticks"

    tick_id: Mapped[str] = mapped_column(String(180), primary_key=True)
    status: Mapped[str] = mapped_column(String(64), index=True)
    requested_at: Mapped[str] = mapped_column(String(64), index=True)
    finished_at: Mapped[str | None] = mapped_column(String(64), index=True)
    health_checks_requested: Mapped[int] = mapped_column(Integer, default=0)
    health_checks_completed: Mapped[int] = mapped_column(Integer, default=0)
    expansion_jobs_requested: Mapped[int] = mapped_column(Integer, default=0)
    expansion_jobs_completed: Mapped[int] = mapped_column(Integer, default=0)
    record_extract_jobs_requested: Mapped[int] = mapped_column(Integer, default=0)
    record_extract_jobs_completed: Mapped[int] = mapped_column(Integer, default=0)
    llm_tasks_requested: Mapped[int] = mapped_column(Integer, default=0)
    llm_tasks_completed: Mapped[int] = mapped_column(Integer, default=0)
    request_budget: Mapped[int] = mapped_column(Integer, default=0)
    used_requests: Mapped[int] = mapped_column(Integer, default=0)
    caveats_json: Mapped[str] = mapped_column(Text, default="[]")


class RuntimeSchedulerWorkerORM(SourceDiscoveryBase):
    __tablename__ = "runtime_scheduler_workers"

    worker_name: Mapped[str] = mapped_column(String(64), primary_key=True)
    desired_state: Mapped[str] = mapped_column(String(32), default="stopped", index=True)
    enabled_by_config: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    poll_seconds: Mapped[int] = mapped_column(Integer, default=300)
    lease_owner: Mapped[str | None] = mapped_column(String(160), index=True)
    lease_expires_at: Mapped[str | None] = mapped_column(String(64), index=True)
    last_tick_requested_at: Mapped[str | None] = mapped_column(String(64), index=True)
    last_tick_started_at: Mapped[str | None] = mapped_column(String(64), index=True)
    last_tick_finished_at: Mapped[str | None] = mapped_column(String(64), index=True)
    last_status: Mapped[str | None] = mapped_column(String(64), index=True)
    last_error: Mapped[str | None] = mapped_column(Text)
    last_summary: Mapped[str | None] = mapped_column(Text)
    updated_at: Mapped[str] = mapped_column(String(64), index=True)


class RuntimeSchedulerRunORM(SourceDiscoveryBase):
    __tablename__ = "runtime_scheduler_runs"

    run_id: Mapped[str] = mapped_column(String(180), primary_key=True)
    worker_name: Mapped[str] = mapped_column(String(64), index=True)
    trigger_kind: Mapped[str] = mapped_column(String(64), index=True)
    status: Mapped[str] = mapped_column(String(64), index=True)
    requested_by: Mapped[str | None] = mapped_column(String(160), index=True)
    lease_owner: Mapped[str | None] = mapped_column(String(160), index=True)
    started_at: Mapped[str] = mapped_column(String(64), index=True)
    finished_at: Mapped[str | None] = mapped_column(String(64), index=True)
    summary: Mapped[str | None] = mapped_column(Text)
    error_summary: Mapped[str | None] = mapped_column(Text)
