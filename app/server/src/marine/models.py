from __future__ import annotations

from sqlalchemy import Boolean, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class MarineBase(DeclarativeBase):
    pass


class MarineSourceORM(MarineBase):
    __tablename__ = "marine_sources"

    source_key: Mapped[str] = mapped_column(String(128), primary_key=True)
    display_name: Mapped[str] = mapped_column(String(255))
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    status: Mapped[str] = mapped_column(String(32), default="never-fetched", index=True)
    detail: Mapped[str] = mapped_column(Text, default="")
    stale_after_seconds: Mapped[int | None] = mapped_column(Integer)
    cadence_seconds: Mapped[int | None] = mapped_column(Integer)
    freshness_seconds: Mapped[int | None] = mapped_column(Integer)
    last_success_at: Mapped[str | None] = mapped_column(String(64), index=True)
    last_attempt_at: Mapped[str | None] = mapped_column(String(64))
    last_failure_at: Mapped[str | None] = mapped_column(String(64))
    degraded_reason: Mapped[str | None] = mapped_column(Text)
    blocked_reason: Mapped[str | None] = mapped_column(Text)
    success_count: Mapped[int] = mapped_column(Integer, default=0)
    failure_count: Mapped[int] = mapped_column(Integer, default=0)
    warning_count: Mapped[int] = mapped_column(Integer, default=0)
    provenance_notes_json: Mapped[str] = mapped_column(Text, default="[]")
    provider_kind: Mapped[str] = mapped_column(String(32), default="unknown")
    coverage_scope: Mapped[str] = mapped_column(String(64), default="unknown")
    global_coverage_claimed: Mapped[bool] = mapped_column(Boolean, default=False)
    assumptions_json: Mapped[str] = mapped_column(Text, default="[]")
    limitations_json: Mapped[str] = mapped_column(Text, default="[]")
    source_url: Mapped[str | None] = mapped_column(Text)


class MarineVesselLatestORM(MarineBase):
    __tablename__ = "marine_vessel_latest"

    vessel_id: Mapped[str] = mapped_column(String(255), primary_key=True)
    source_key: Mapped[str] = mapped_column(String(128), index=True)
    mmsi: Mapped[str] = mapped_column(String(32), index=True)
    imo: Mapped[str | None] = mapped_column(String(32), index=True)
    callsign: Mapped[str | None] = mapped_column(String(64), index=True)
    vessel_name: Mapped[str | None] = mapped_column(String(255), index=True)
    flag_state: Mapped[str | None] = mapped_column(String(16), index=True)
    vessel_class: Mapped[str | None] = mapped_column(String(64), index=True)
    nav_status: Mapped[str | None] = mapped_column(String(64), index=True)
    destination: Mapped[str | None] = mapped_column(String(255))
    eta: Mapped[str | None] = mapped_column(String(64), index=True)
    latitude: Mapped[float] = mapped_column(Float, index=True)
    longitude: Mapped[float] = mapped_column(Float, index=True)
    course: Mapped[float | None] = mapped_column(Float)
    heading: Mapped[float | None] = mapped_column(Float)
    speed: Mapped[float | None] = mapped_column(Float)
    observed_at: Mapped[str] = mapped_column(String(64), index=True)
    fetched_at: Mapped[str] = mapped_column(String(64), index=True)
    status: Mapped[str] = mapped_column(String(64), index=True)
    source_detail: Mapped[str | None] = mapped_column(Text)
    external_url: Mapped[str | None] = mapped_column(Text)
    confidence: Mapped[float | None] = mapped_column(Float)
    quality_score: Mapped[float | None] = mapped_column(Float)
    quality_label: Mapped[str | None] = mapped_column(String(64))
    quality_notes_json: Mapped[str] = mapped_column(Text, default="[]")
    stale: Mapped[bool] = mapped_column(Boolean, default=False)
    degraded: Mapped[bool] = mapped_column(Boolean, default=False)
    degraded_reason: Mapped[str | None] = mapped_column(Text)
    source_health: Mapped[str | None] = mapped_column(String(32))
    observed_vs_derived: Mapped[str] = mapped_column(String(32), default="observed")
    geometry_provenance: Mapped[str] = mapped_column(String(32), default="raw_observed")
    reference_ref_id: Mapped[str | None] = mapped_column(String(255), index=True)
    metadata_json: Mapped[str] = mapped_column(Text, default="{}")
    bucket_date: Mapped[str] = mapped_column(String(10), index=True)
    bucket_hour: Mapped[int] = mapped_column(Integer, index=True)
    vessel_shard: Mapped[int] = mapped_column(Integer, index=True)
    last_event_id: Mapped[int | None] = mapped_column(Integer, index=True)


class MarinePositionEventORM(MarineBase):
    __tablename__ = "marine_position_events"
    __table_args__ = (
        UniqueConstraint("vessel_id", "source_key", "observed_at", name="uq_marine_position_observation"),
    )

    event_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    vessel_id: Mapped[str] = mapped_column(String(255), index=True)
    source_key: Mapped[str] = mapped_column(String(128), index=True)
    mmsi: Mapped[str] = mapped_column(String(32), index=True)
    imo: Mapped[str | None] = mapped_column(String(32), index=True)
    callsign: Mapped[str | None] = mapped_column(String(64), index=True)
    vessel_name: Mapped[str | None] = mapped_column(String(255), index=True)
    flag_state: Mapped[str | None] = mapped_column(String(16), index=True)
    vessel_class: Mapped[str | None] = mapped_column(String(64), index=True)
    nav_status: Mapped[str | None] = mapped_column(String(64), index=True)
    destination: Mapped[str | None] = mapped_column(String(255))
    eta: Mapped[str | None] = mapped_column(String(64), index=True)
    latitude: Mapped[float] = mapped_column(Float, index=True)
    longitude: Mapped[float] = mapped_column(Float, index=True)
    course: Mapped[float | None] = mapped_column(Float)
    heading: Mapped[float | None] = mapped_column(Float)
    speed: Mapped[float | None] = mapped_column(Float)
    observed_at: Mapped[str] = mapped_column(String(64), index=True)
    fetched_at: Mapped[str] = mapped_column(String(64), index=True)
    source_detail: Mapped[str | None] = mapped_column(Text)
    external_url: Mapped[str | None] = mapped_column(Text)
    confidence: Mapped[float | None] = mapped_column(Float)
    quality_score: Mapped[float | None] = mapped_column(Float)
    quality_label: Mapped[str | None] = mapped_column(String(64))
    quality_notes_json: Mapped[str] = mapped_column(Text, default="[]")
    observed_vs_derived: Mapped[str] = mapped_column(String(32), default="observed")
    geometry_provenance: Mapped[str] = mapped_column(String(32), default="raw_observed")
    status: Mapped[str] = mapped_column(String(64), index=True)
    expected_reporting_interval_seconds: Mapped[int | None] = mapped_column(Integer)
    metadata_json: Mapped[str] = mapped_column(Text, default="{}")
    bucket_date: Mapped[str] = mapped_column(String(10), index=True)
    bucket_hour: Mapped[int] = mapped_column(Integer, index=True)
    vessel_shard: Mapped[int] = mapped_column(Integer, index=True)


class MarineGapEventORM(MarineBase):
    __tablename__ = "marine_gap_events"

    gap_event_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    vessel_id: Mapped[str] = mapped_column(String(255), index=True)
    source_key: Mapped[str] = mapped_column(String(128), index=True)
    event_kind: Mapped[str] = mapped_column(String(64), index=True)
    gap_start_observed_at: Mapped[str] = mapped_column(String(64), index=True)
    gap_end_observed_at: Mapped[str | None] = mapped_column(String(64), index=True)
    gap_duration_seconds: Mapped[int | None] = mapped_column(Integer)
    start_latitude: Mapped[float | None] = mapped_column(Float)
    start_longitude: Mapped[float | None] = mapped_column(Float)
    end_latitude: Mapped[float | None] = mapped_column(Float)
    end_longitude: Mapped[float | None] = mapped_column(Float)
    distance_moved_m: Mapped[float | None] = mapped_column(Float)
    expected_interval_seconds: Mapped[int | None] = mapped_column(Integer)
    exceeds_expected_cadence: Mapped[bool] = mapped_column(Boolean, default=False)
    confidence_class: Mapped[str] = mapped_column(String(16), index=True)
    confidence_score: Mapped[float | None] = mapped_column(Float)
    normal_sparse_reporting_plausible: Mapped[bool] = mapped_column(Boolean, default=False)
    confidence_breakdown_json: Mapped[str] = mapped_column(Text, default="{}")
    derivation_method: Mapped[str] = mapped_column(String(64))
    input_event_ids_json: Mapped[str] = mapped_column(Text, default="[]")
    uncertainty_notes_json: Mapped[str] = mapped_column(Text, default="[]")
    evidence_summary: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[str] = mapped_column(String(64), index=True)
    bucket_date: Mapped[str] = mapped_column(String(10), index=True)
    bucket_hour: Mapped[int] = mapped_column(Integer, index=True)
    vessel_shard: Mapped[int] = mapped_column(Integer, index=True)


class MarineReplaySnapshotORM(MarineBase):
    __tablename__ = "marine_replay_snapshots"

    snapshot_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    snapshot_at: Mapped[str] = mapped_column(String(64), index=True)
    bucket_date: Mapped[str] = mapped_column(String(10), index=True)
    bucket_hour: Mapped[int] = mapped_column(Integer, index=True)
    scope_kind: Mapped[str] = mapped_column(String(16), default="global", index=True)
    bbox_min_lat: Mapped[float | None] = mapped_column(Float)
    bbox_min_lon: Mapped[float | None] = mapped_column(Float)
    bbox_max_lat: Mapped[float | None] = mapped_column(Float)
    bbox_max_lon: Mapped[float | None] = mapped_column(Float)
    vessel_count: Mapped[int] = mapped_column(Integer, default=0)
    position_event_count: Mapped[int] = mapped_column(Integer, default=0)
    storage_key: Mapped[str | None] = mapped_column(String(255), index=True)
    chunk_id: Mapped[str | None] = mapped_column(String(128), index=True)
    derived_from_event_id: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[str] = mapped_column(String(64), index=True)

    members: Mapped[list[MarineReplaySnapshotMemberORM]] = relationship(
        back_populates="snapshot",
        cascade="all, delete-orphan",
    )


class MarineReplaySnapshotMemberORM(MarineBase):
    __tablename__ = "marine_replay_snapshot_members"

    member_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    snapshot_id: Mapped[int] = mapped_column(
        ForeignKey("marine_replay_snapshots.snapshot_id", ondelete="CASCADE"),
        index=True,
    )
    vessel_id: Mapped[str] = mapped_column(String(255), index=True)
    source_key: Mapped[str] = mapped_column(String(128), index=True)
    mmsi: Mapped[str] = mapped_column(String(32), index=True)
    vessel_name: Mapped[str | None] = mapped_column(String(255), index=True)
    latitude: Mapped[float] = mapped_column(Float, index=True)
    longitude: Mapped[float] = mapped_column(Float, index=True)
    course: Mapped[float | None] = mapped_column(Float)
    heading: Mapped[float | None] = mapped_column(Float)
    speed: Mapped[float | None] = mapped_column(Float)
    observed_at: Mapped[str] = mapped_column(String(64), index=True)
    fetched_at: Mapped[str] = mapped_column(String(64), index=True)
    status: Mapped[str] = mapped_column(String(64), index=True)
    confidence: Mapped[float | None] = mapped_column(Float)
    geometry_provenance: Mapped[str] = mapped_column(String(32), default="raw_observed")
    metadata_json: Mapped[str] = mapped_column(Text, default="{}")

    snapshot: Mapped[MarineReplaySnapshotORM] = relationship(back_populates="members")


class MarineTimelineSegmentORM(MarineBase):
    __tablename__ = "marine_timeline_segments"

    segment_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    segment_start_at: Mapped[str] = mapped_column(String(64), index=True)
    segment_end_at: Mapped[str] = mapped_column(String(64), index=True)
    bucket_date: Mapped[str] = mapped_column(String(10), index=True)
    bucket_hour: Mapped[int] = mapped_column(Integer, index=True)
    scope_kind: Mapped[str] = mapped_column(String(16), default="global", index=True)
    bbox_min_lat: Mapped[float | None] = mapped_column(Float)
    bbox_min_lon: Mapped[float | None] = mapped_column(Float)
    bbox_max_lat: Mapped[float | None] = mapped_column(Float)
    bbox_max_lon: Mapped[float | None] = mapped_column(Float)
    vessel_count: Mapped[int] = mapped_column(Integer, default=0)
    position_event_count: Mapped[int] = mapped_column(Integer, default=0)
    gap_event_count: Mapped[int] = mapped_column(Integer, default=0)
    snapshot_id: Mapped[int | None] = mapped_column(Integer, index=True)
    chunk_id: Mapped[str | None] = mapped_column(String(128), index=True)
    metadata_json: Mapped[str] = mapped_column(Text, default="{}")
