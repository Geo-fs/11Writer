from __future__ import annotations

from sqlalchemy import Boolean, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class WaveMonitorBase(DeclarativeBase):
    pass


class WaveMonitorORM(WaveMonitorBase):
    __tablename__ = "wave_monitors"

    monitor_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    title: Mapped[str] = mapped_column(String(255), index=True)
    description: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(32), default="active", index=True)
    focus_type: Mapped[str] = mapped_column(String(32), default="mixed", index=True)
    source_mode: Mapped[str] = mapped_column(String(32), default="fixture", index=True)
    source_health: Mapped[str] = mapped_column(String(32), default="loaded", index=True)
    evidence_basis: Mapped[str] = mapped_column(String(32), default="contextual")
    last_run_at: Mapped[str | None] = mapped_column(String(64), index=True)
    next_run_at: Mapped[str | None] = mapped_column(String(64), index=True)
    caveats_json: Mapped[str] = mapped_column(Text, default="[]")
    created_at: Mapped[str] = mapped_column(String(64), index=True)
    updated_at: Mapped[str] = mapped_column(String(64), index=True)

    connectors: Mapped[list[WaveConnectorORM]] = relationship(
        back_populates="monitor",
        cascade="all, delete-orphan",
    )
    records: Mapped[list[WaveRecordORM]] = relationship(
        back_populates="monitor",
        cascade="all, delete-orphan",
    )
    signals: Mapped[list[WaveSignalORM]] = relationship(
        back_populates="monitor",
        cascade="all, delete-orphan",
    )
    runs: Mapped[list[WaveRunORM]] = relationship(
        back_populates="monitor",
        cascade="all, delete-orphan",
    )
    source_candidates: Mapped[list[WaveSourceCandidateORM]] = relationship(
        back_populates="monitor",
        cascade="all, delete-orphan",
    )


class WaveConnectorORM(WaveMonitorBase):
    __tablename__ = "wave_connectors"

    connector_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    monitor_id: Mapped[str] = mapped_column(
        ForeignKey("wave_monitors.monitor_id", ondelete="CASCADE"),
        index=True,
    )
    connector_type: Mapped[str] = mapped_column(String(64), index=True)
    name: Mapped[str] = mapped_column(String(255))
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    source_mode: Mapped[str] = mapped_column(String(32), default="fixture", index=True)
    feed_url: Mapped[str | None] = mapped_column(Text)
    fixture_xml: Mapped[str | None] = mapped_column(Text)
    include_keywords_json: Mapped[str] = mapped_column(Text, default="[]")
    exclude_keywords_json: Mapped[str] = mapped_column(Text, default="[]")
    polling_interval_minutes: Mapped[int] = mapped_column(Integer, default=60)
    max_items_per_run: Mapped[int] = mapped_column(Integer, default=20)
    last_run_at: Mapped[str | None] = mapped_column(String(64), index=True)
    last_success_at: Mapped[str | None] = mapped_column(String(64), index=True)
    last_error_at: Mapped[str | None] = mapped_column(String(64), index=True)
    last_error_message: Mapped[str | None] = mapped_column(Text)
    next_run_at: Mapped[str | None] = mapped_column(String(64), index=True)

    monitor: Mapped[WaveMonitorORM] = relationship(back_populates="connectors")


class WaveRecordORM(WaveMonitorBase):
    __tablename__ = "wave_records"
    __table_args__ = (
        UniqueConstraint("connector_id", "external_id", name="uq_wave_record_connector_external_id"),
    )

    record_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    monitor_id: Mapped[str] = mapped_column(
        ForeignKey("wave_monitors.monitor_id", ondelete="CASCADE"),
        index=True,
    )
    connector_id: Mapped[str | None] = mapped_column(
        ForeignKey("wave_connectors.connector_id", ondelete="SET NULL"),
        index=True,
    )
    external_id: Mapped[str] = mapped_column(String(512), index=True)
    title: Mapped[str] = mapped_column(String(300))
    content: Mapped[str] = mapped_column(Text, default="")
    source_id: Mapped[str] = mapped_column(String(128), index=True)
    source_name: Mapped[str] = mapped_column(String(255))
    source_url: Mapped[str | None] = mapped_column(Text)
    event_time: Mapped[str | None] = mapped_column(String(64), index=True)
    collected_at: Mapped[str] = mapped_column(String(64), index=True)
    evidence_basis: Mapped[str] = mapped_column(String(32), default="contextual")
    tags_json: Mapped[str] = mapped_column(Text, default="[]")
    caveats_json: Mapped[str] = mapped_column(Text, default="[]")
    raw_payload_json: Mapped[str] = mapped_column(Text, default="{}")

    monitor: Mapped[WaveMonitorORM] = relationship(back_populates="records")


class WaveSignalORM(WaveMonitorBase):
    __tablename__ = "wave_signals"

    signal_id: Mapped[str] = mapped_column(String(160), primary_key=True)
    monitor_id: Mapped[str] = mapped_column(
        ForeignKey("wave_monitors.monitor_id", ondelete="CASCADE"),
        index=True,
    )
    signal_type: Mapped[str] = mapped_column(String(64), index=True)
    title: Mapped[str] = mapped_column(String(300))
    summary: Mapped[str] = mapped_column(Text, default="")
    severity: Mapped[str] = mapped_column(String(16), default="low", index=True)
    status: Mapped[str] = mapped_column(String(32), default="new", index=True)
    evidence_basis: Mapped[str] = mapped_column(String(32), default="scored")
    source_ids_json: Mapped[str] = mapped_column(Text, default="[]")
    relationship_reasons_json: Mapped[str] = mapped_column(Text, default="[]")
    caveats_json: Mapped[str] = mapped_column(Text, default="[]")
    created_at: Mapped[str] = mapped_column(String(64), index=True)
    dedupe_key: Mapped[str | None] = mapped_column(String(300), index=True)

    monitor: Mapped[WaveMonitorORM] = relationship(back_populates="signals")


class WaveRunORM(WaveMonitorBase):
    __tablename__ = "wave_runs"

    run_id: Mapped[str] = mapped_column(String(160), primary_key=True)
    monitor_id: Mapped[str] = mapped_column(
        ForeignKey("wave_monitors.monitor_id", ondelete="CASCADE"),
        index=True,
    )
    connector_id: Mapped[str | None] = mapped_column(String(128), index=True)
    status: Mapped[str] = mapped_column(String(32), index=True)
    started_at: Mapped[str] = mapped_column(String(64), index=True)
    finished_at: Mapped[str | None] = mapped_column(String(64), index=True)
    records_created: Mapped[int] = mapped_column(Integer, default=0)
    source_checks_completed: Mapped[int] = mapped_column(Integer, default=0)
    error_summary: Mapped[str | None] = mapped_column(Text)

    monitor: Mapped[WaveMonitorORM] = relationship(back_populates="runs")


class WaveSourceCandidateORM(WaveMonitorBase):
    __tablename__ = "wave_source_candidates"

    source_id: Mapped[str] = mapped_column(String(160), primary_key=True)
    monitor_id: Mapped[str] = mapped_column(
        ForeignKey("wave_monitors.monitor_id", ondelete="CASCADE"),
        index=True,
    )
    title: Mapped[str] = mapped_column(String(300))
    url: Mapped[str] = mapped_column(Text)
    source_type: Mapped[str] = mapped_column(String(64), index=True)
    parent_domain: Mapped[str] = mapped_column(String(255), index=True)
    lifecycle_state: Mapped[str] = mapped_column(String(32), default="candidate", index=True)
    source_health: Mapped[str] = mapped_column(String(32), default="unknown", index=True)
    trust_tier: Mapped[str] = mapped_column(String(16), default="tier_4")
    relevance_score: Mapped[float] = mapped_column(Float, default=0.0)
    stability_score: Mapped[float | None] = mapped_column(Float)
    policy_state: Mapped[str] = mapped_column(String(64), default="manual_review")
    caveats_json: Mapped[str] = mapped_column(Text, default="[]")

    monitor: Mapped[WaveMonitorORM] = relationship(back_populates="source_candidates")


class WaveLlmTaskORM(WaveMonitorBase):
    __tablename__ = "wave_llm_tasks"

    task_id: Mapped[str] = mapped_column(String(180), primary_key=True)
    monitor_id: Mapped[str] = mapped_column(String(128), index=True)
    task_type: Mapped[str] = mapped_column(String(64), index=True)
    provider: Mapped[str] = mapped_column(String(64), index=True)
    model: Mapped[str] = mapped_column(String(160), default="")
    status: Mapped[str] = mapped_column(String(64), default="pending_review", index=True)
    input_summary: Mapped[str] = mapped_column(Text, default="")
    source_ids_json: Mapped[str] = mapped_column(Text, default="[]")
    record_ids_json: Mapped[str] = mapped_column(Text, default="[]")
    prompt_contract_json: Mapped[str] = mapped_column(Text, default="{}")
    created_at: Mapped[str] = mapped_column(String(64), index=True)
    completed_at: Mapped[str | None] = mapped_column(String(64), index=True)
    caveats_json: Mapped[str] = mapped_column(Text, default="[]")


class WaveLlmReviewORM(WaveMonitorBase):
    __tablename__ = "wave_llm_reviews"

    review_id: Mapped[str] = mapped_column(String(180), primary_key=True)
    task_id: Mapped[str] = mapped_column(String(180), index=True)
    monitor_id: Mapped[str] = mapped_column(String(128), index=True)
    provider: Mapped[str] = mapped_column(String(64), index=True)
    model: Mapped[str] = mapped_column(String(160), default="")
    raw_output: Mapped[str] = mapped_column(Text, default="")
    parsed_claims_json: Mapped[str] = mapped_column(Text, default="[]")
    proposed_actions_json: Mapped[str] = mapped_column(Text, default="[]")
    validation_state: Mapped[str] = mapped_column(String(64), index=True)
    risk_flags_json: Mapped[str] = mapped_column(Text, default="[]")
    accepted_claim_count: Mapped[int] = mapped_column(Integer, default=0)
    rejected_claim_count: Mapped[int] = mapped_column(Integer, default=0)
    requires_human_review: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    created_at: Mapped[str] = mapped_column(String(64), index=True)
    caveats_json: Mapped[str] = mapped_column(Text, default="[]")
