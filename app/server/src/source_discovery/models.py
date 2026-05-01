from __future__ import annotations

from sqlalchemy import Float, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class SourceDiscoveryBase(DeclarativeBase):
    pass


class SourceMemoryORM(SourceDiscoveryBase):
    __tablename__ = "source_memories"

    source_id: Mapped[str] = mapped_column(String(160), primary_key=True)
    title: Mapped[str] = mapped_column(String(300))
    url: Mapped[str] = mapped_column(Text)
    parent_domain: Mapped[str] = mapped_column(String(255), index=True)
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
