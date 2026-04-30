from __future__ import annotations

from sqlalchemy import Boolean, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class WebcamBase(DeclarativeBase):
    pass


class CameraSourceORM(WebcamBase):
    __tablename__ = "camera_sources"

    source_key: Mapped[str] = mapped_column(String(128), primary_key=True)
    display_name: Mapped[str] = mapped_column(String(255))
    owner: Mapped[str] = mapped_column(String(255))
    source_type: Mapped[str] = mapped_column(String(64), index=True)
    coverage: Mapped[str] = mapped_column(String(255))
    priority: Mapped[int] = mapped_column(Integer, default=0)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    authentication: Mapped[str] = mapped_column(String(32))
    default_refresh_interval_seconds: Mapped[int] = mapped_column(Integer, default=60)
    status: Mapped[str] = mapped_column(String(32), default="never-fetched", index=True)
    detail: Mapped[str] = mapped_column(Text, default="")
    credentials_configured: Mapped[bool] = mapped_column(Boolean, default=True)
    blocked_reason: Mapped[str | None] = mapped_column(Text)
    degraded_reason: Mapped[str | None] = mapped_column(Text)
    review_required: Mapped[bool] = mapped_column(Boolean, default=False)
    last_attempt_at: Mapped[str | None] = mapped_column(String(64))
    last_success_at: Mapped[str | None] = mapped_column(String(64))
    last_failure_at: Mapped[str | None] = mapped_column(String(64))
    last_started_at: Mapped[str | None] = mapped_column(String(64))
    last_completed_at: Mapped[str | None] = mapped_column(String(64))
    next_refresh_at: Mapped[str | None] = mapped_column(String(64), index=True)
    backoff_until: Mapped[str | None] = mapped_column(String(64), index=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    last_http_status: Mapped[int | None] = mapped_column(Integer)
    cadence_seconds: Mapped[int | None] = mapped_column(Integer)
    cadence_reason: Mapped[str | None] = mapped_column(Text)
    success_count: Mapped[int] = mapped_column(Integer, default=0)
    failure_count: Mapped[int] = mapped_column(Integer, default=0)
    warning_count: Mapped[int] = mapped_column(Integer, default=0)
    last_camera_count: Mapped[int] = mapped_column(Integer, default=0)
    notes_json: Mapped[str] = mapped_column(Text, default="[]")
    attribution_text: Mapped[str] = mapped_column(Text)
    attribution_url: Mapped[str | None] = mapped_column(Text)
    terms_url: Mapped[str | None] = mapped_column(Text)
    license_summary: Mapped[str | None] = mapped_column(Text)
    requires_authentication: Mapped[bool] = mapped_column(Boolean, default=False)
    supports_embedding: Mapped[bool] = mapped_column(Boolean, default=False)
    supports_frame_storage: Mapped[bool] = mapped_column(Boolean, default=False)
    compliance_review_required: Mapped[bool] = mapped_column(Boolean, default=False)
    provenance_notes_json: Mapped[str] = mapped_column(Text, default="[]")
    compliance_notes_json: Mapped[str] = mapped_column(Text, default="[]")

    cameras: Mapped[list[CameraRecordORM]] = relationship(
        back_populates="source",
        cascade="all, delete-orphan",
    )


class CameraSourceInventoryORM(WebcamBase):
    __tablename__ = "camera_source_inventory"

    source_key: Mapped[str] = mapped_column(String(128), primary_key=True)
    source_name: Mapped[str] = mapped_column(String(255), index=True)
    source_family: Mapped[str] = mapped_column(String(64), index=True)
    source_type: Mapped[str] = mapped_column(String(64), index=True)
    access_method: Mapped[str] = mapped_column(String(32), index=True)
    onboarding_state: Mapped[str] = mapped_column(String(32), index=True)
    owner: Mapped[str] = mapped_column(String(255))
    authentication: Mapped[str] = mapped_column(String(32))
    credentials_configured: Mapped[bool] = mapped_column(Boolean, default=False)
    rate_limit_notes_json: Mapped[str] = mapped_column(Text, default="[]")
    coverage_geography: Mapped[str] = mapped_column(Text)
    coverage_states_json: Mapped[str] = mapped_column(Text, default="[]")
    coverage_regions_json: Mapped[str] = mapped_column(Text, default="[]")
    provides_exact_coordinates: Mapped[bool] = mapped_column(Boolean, default=False)
    provides_direction_text: Mapped[bool] = mapped_column(Boolean, default=False)
    provides_numeric_heading: Mapped[bool] = mapped_column(Boolean, default=False)
    provides_direct_image: Mapped[bool] = mapped_column(Boolean, default=False)
    provides_viewer_only: Mapped[bool] = mapped_column(Boolean, default=False)
    supports_embed: Mapped[bool] = mapped_column(Boolean, default=False)
    supports_storage: Mapped[bool] = mapped_column(Boolean, default=False)
    attribution_text: Mapped[str] = mapped_column(Text)
    attribution_url: Mapped[str | None] = mapped_column(Text)
    terms_url: Mapped[str | None] = mapped_column(Text)
    license_summary: Mapped[str | None] = mapped_column(Text)
    requires_authentication: Mapped[bool] = mapped_column(Boolean, default=False)
    compliance_review_required: Mapped[bool] = mapped_column(Boolean, default=False)
    provenance_notes_json: Mapped[str] = mapped_column(Text, default="[]")
    compliance_notes_json: Mapped[str] = mapped_column(Text, default="[]")
    source_quality_notes_json: Mapped[str] = mapped_column(Text, default="[]")
    source_stability_notes_json: Mapped[str] = mapped_column(Text, default="[]")
    page_structure: Mapped[str | None] = mapped_column(String(64), index=True)
    likely_camera_count: Mapped[int | None] = mapped_column(Integer)
    compliance_risk: Mapped[str | None] = mapped_column(String(16), index=True)
    extraction_feasibility: Mapped[str | None] = mapped_column(String(16), index=True)
    endpoint_verification_status: Mapped[str | None] = mapped_column(String(32), index=True)
    candidate_endpoint_url: Mapped[str | None] = mapped_column(Text)
    machine_readable_endpoint_url: Mapped[str | None] = mapped_column(Text)
    last_endpoint_check_at: Mapped[str | None] = mapped_column(String(64), index=True)
    last_endpoint_http_status: Mapped[int | None] = mapped_column(Integer)
    last_endpoint_content_type: Mapped[str | None] = mapped_column(String(255))
    last_endpoint_result: Mapped[str | None] = mapped_column(Text)
    last_endpoint_notes_json: Mapped[str] = mapped_column(Text, default="[]")
    verification_caveat: Mapped[str | None] = mapped_column(Text)
    blocked_reason: Mapped[str | None] = mapped_column(Text)
    approximate_camera_count: Mapped[int | None] = mapped_column(Integer)
    last_catalog_import_at: Mapped[str | None] = mapped_column(String(64), index=True)
    last_catalog_import_status: Mapped[str | None] = mapped_column(String(32))
    last_catalog_import_detail: Mapped[str | None] = mapped_column(Text)


class CameraSourceInventoryRunORM(WebcamBase):
    __tablename__ = "camera_source_inventory_runs"

    run_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_key: Mapped[str] = mapped_column(
        ForeignKey("camera_source_inventory.source_key", ondelete="CASCADE"),
        index=True,
    )
    started_at: Mapped[str] = mapped_column(String(64), index=True)
    completed_at: Mapped[str | None] = mapped_column(String(64), index=True)
    status: Mapped[str] = mapped_column(String(32), index=True)
    discovered_camera_count: Mapped[int] = mapped_column(Integer, default=0)
    imported_camera_count: Mapped[int] = mapped_column(Integer, default=0)
    detail: Mapped[str | None] = mapped_column(Text)


class CameraRecordORM(WebcamBase):
    __tablename__ = "camera_records"

    camera_id: Mapped[str] = mapped_column(String(255), primary_key=True)
    source_key: Mapped[str] = mapped_column(
        ForeignKey("camera_sources.source_key", ondelete="CASCADE"),
        index=True,
    )
    source_camera_id: Mapped[str | None] = mapped_column(String(255), index=True)
    label: Mapped[str] = mapped_column(String(255), index=True)
    owner: Mapped[str | None] = mapped_column(String(255))
    state: Mapped[str | None] = mapped_column(String(32), index=True)
    county: Mapped[str | None] = mapped_column(String(128))
    region: Mapped[str | None] = mapped_column(String(128))
    roadway: Mapped[str | None] = mapped_column(String(255), index=True)
    direction: Mapped[str | None] = mapped_column(String(64))
    location_description: Mapped[str | None] = mapped_column(Text)
    latitude: Mapped[float] = mapped_column(Float, index=True)
    longitude: Mapped[float] = mapped_column(Float, index=True)
    altitude: Mapped[float] = mapped_column(Float, default=0.0)
    heading: Mapped[float | None] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(32), index=True)
    feed_type: Mapped[str | None] = mapped_column(String(32))
    access_policy: Mapped[str | None] = mapped_column(String(64))
    external_url: Mapped[str | None] = mapped_column(Text)
    confidence: Mapped[float | None] = mapped_column(Float)
    position_kind: Mapped[str] = mapped_column(String(32), index=True)
    position_confidence: Mapped[float | None] = mapped_column(Float)
    position_source: Mapped[str | None] = mapped_column(Text)
    position_notes_json: Mapped[str] = mapped_column(Text, default="[]")
    orientation_kind: Mapped[str] = mapped_column(String(32), index=True)
    orientation_degrees: Mapped[float | None] = mapped_column(Float)
    orientation_cardinal_direction: Mapped[str | None] = mapped_column(String(64))
    orientation_confidence: Mapped[float | None] = mapped_column(Float)
    orientation_source: Mapped[str | None] = mapped_column(Text)
    orientation_is_ptz: Mapped[bool] = mapped_column(Boolean, default=False)
    orientation_notes_json: Mapped[str] = mapped_column(Text, default="[]")
    frame_status: Mapped[str] = mapped_column(String(32))
    frame_refresh_interval_seconds: Mapped[int | None] = mapped_column(Integer)
    frame_image_url: Mapped[str | None] = mapped_column(Text)
    frame_thumbnail_url: Mapped[str | None] = mapped_column(Text)
    frame_stream_url: Mapped[str | None] = mapped_column(Text)
    frame_viewer_url: Mapped[str | None] = mapped_column(Text)
    frame_width: Mapped[int | None] = mapped_column(Integer)
    frame_height: Mapped[int | None] = mapped_column(Integer)
    last_frame_at: Mapped[str | None] = mapped_column(String(64), index=True)
    last_metadata_refresh_at: Mapped[str | None] = mapped_column(String(64), index=True)
    health_state: Mapped[str | None] = mapped_column(String(32), index=True)
    degraded_reason: Mapped[str | None] = mapped_column(Text)
    review_status: Mapped[str] = mapped_column(String(32), index=True)
    review_reason: Mapped[str | None] = mapped_column(Text)
    review_required_actions_json: Mapped[str] = mapped_column(Text, default="[]")
    review_issue_categories_json: Mapped[str] = mapped_column(Text, default="[]")
    nearest_reference_ref_id: Mapped[str | None] = mapped_column(String(255), index=True)
    reference_link_status: Mapped[str | None] = mapped_column(String(64))
    link_candidate_count: Mapped[int] = mapped_column(Integer, default=0)
    reference_hint_text: Mapped[str | None] = mapped_column(Text)
    facility_code_hint: Mapped[str | None] = mapped_column(String(64))
    raw_payload_json: Mapped[str] = mapped_column(Text, default="{}")

    source: Mapped[CameraSourceORM] = relationship(back_populates="cameras")
    health: Mapped[CameraHealthORM | None] = relationship(back_populates="camera", uselist=False, cascade="all, delete-orphan")
    review_items: Mapped[list[CameraReviewQueueORM]] = relationship(back_populates="camera", cascade="all, delete-orphan")
    frames: Mapped[list[CameraFrameORM]] = relationship(back_populates="camera", cascade="all, delete-orphan")


class CameraFrameORM(WebcamBase):
    __tablename__ = "camera_frames"

    frame_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    camera_id: Mapped[str] = mapped_column(
        ForeignKey("camera_records.camera_id", ondelete="CASCADE"),
        index=True,
    )
    fetched_at: Mapped[str] = mapped_column(String(64), index=True)
    captured_at: Mapped[str | None] = mapped_column(String(64), index=True)
    source_frame_url: Mapped[str | None] = mapped_column(Text)
    frame_hash: Mapped[str | None] = mapped_column(String(128), index=True)
    status: Mapped[str] = mapped_column(String(32), index=True)
    width: Mapped[int | None] = mapped_column(Integer)
    height: Mapped[int | None] = mapped_column(Integer)
    age_seconds: Mapped[int | None] = mapped_column(Integer)

    camera: Mapped[CameraRecordORM] = relationship(back_populates="frames")


class CameraHealthORM(WebcamBase):
    __tablename__ = "camera_health"

    camera_id: Mapped[str] = mapped_column(
        ForeignKey("camera_records.camera_id", ondelete="CASCADE"),
        primary_key=True,
    )
    source_key: Mapped[str] = mapped_column(String(128), index=True)
    health_state: Mapped[str] = mapped_column(String(32), index=True)
    last_attempt_at: Mapped[str | None] = mapped_column(String(64))
    last_success_at: Mapped[str | None] = mapped_column(String(64))
    last_failure_at: Mapped[str | None] = mapped_column(String(64))
    freshness_seconds: Mapped[int | None] = mapped_column(Integer)
    stale_after_seconds: Mapped[int | None] = mapped_column(Integer)
    last_metadata_refresh_at: Mapped[str | None] = mapped_column(String(64), index=True)
    next_frame_refresh_at: Mapped[str | None] = mapped_column(String(64), index=True)
    backoff_until: Mapped[str | None] = mapped_column(String(64), index=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    consecutive_failures: Mapped[int] = mapped_column(Integer, default=0)
    degraded_reason: Mapped[str | None] = mapped_column(Text)
    blocked_reason: Mapped[str | None] = mapped_column(Text)
    last_http_status: Mapped[int | None] = mapped_column(Integer)

    camera: Mapped[CameraRecordORM] = relationship(back_populates="health")


class CameraSourceRunORM(WebcamBase):
    __tablename__ = "camera_source_runs"

    run_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_key: Mapped[str] = mapped_column(
        ForeignKey("camera_sources.source_key", ondelete="CASCADE"),
        index=True,
    )
    started_at: Mapped[str] = mapped_column(String(64), index=True)
    completed_at: Mapped[str | None] = mapped_column(String(64), index=True)
    run_mode: Mapped[str] = mapped_column(String(32), default="scheduled", index=True)
    status: Mapped[str] = mapped_column(String(32), index=True)
    camera_count: Mapped[int] = mapped_column(Integer, default=0)
    normalized_count: Mapped[int] = mapped_column(Integer, default=0)
    partial_failure_count: Mapped[int] = mapped_column(Integer, default=0)
    warning_count: Mapped[int] = mapped_column(Integer, default=0)
    frame_probe_count: Mapped[int] = mapped_column(Integer, default=0)
    frame_status_counts_json: Mapped[str] = mapped_column(Text, default="{}")
    metadata_uncertainty_count: Mapped[int] = mapped_column(Integer, default=0)
    http_status: Mapped[int | None] = mapped_column(Integer)
    error_text: Mapped[str | None] = mapped_column(Text)
    cadence_observation: Mapped[str | None] = mapped_column(Text)


class CameraReviewQueueORM(WebcamBase):
    __tablename__ = "camera_review_queue"
    __table_args__ = (
        UniqueConstraint("camera_id", "issue_category", "reason", name="uq_camera_review_issue"),
    )

    review_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    camera_id: Mapped[str] = mapped_column(
        ForeignKey("camera_records.camera_id", ondelete="CASCADE"),
        index=True,
    )
    source_key: Mapped[str] = mapped_column(String(128), index=True)
    priority: Mapped[str] = mapped_column(String(16), index=True)
    issue_category: Mapped[str] = mapped_column(String(64), index=True)
    reason: Mapped[str] = mapped_column(Text)
    required_action: Mapped[str] = mapped_column(Text)
    context_json: Mapped[str] = mapped_column(Text, default="{}")
    status: Mapped[str] = mapped_column(String(32), default="open", index=True)
    created_at: Mapped[str] = mapped_column(String(64), index=True)
    updated_at: Mapped[str] = mapped_column(String(64))

    camera: Mapped[CameraRecordORM] = relationship(back_populates="review_items")
