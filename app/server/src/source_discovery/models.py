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
    auth_requirement: Mapped[str] = mapped_column(String(32), default="unknown", index=True)
    captcha_requirement: Mapped[str] = mapped_column(String(32), default="unknown", index=True)
    intake_disposition: Mapped[str] = mapped_column(String(32), default="hold_review", index=True)
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
    last_discovery_scan_at: Mapped[str | None] = mapped_column(String(64), index=True)
    next_discovery_scan_at: Mapped[str | None] = mapped_column(String(64), index=True)
    discovery_scan_fail_count: Mapped[int] = mapped_column(Integer, default=0)
    discovery_low_yield_count: Mapped[int] = mapped_column(Integer, default=0)
    health_check_fail_count: Mapped[int] = mapped_column(Integer, default=0)
    caveats_json: Mapped[str] = mapped_column(Text, default="[]")
    reputation_basis_json: Mapped[str] = mapped_column(Text, default="[]")
    known_aliases_json: Mapped[str] = mapped_column(Text, default="[]")
    discovery_methods_json: Mapped[str] = mapped_column(Text, default="[]")
    structure_hints_json: Mapped[str] = mapped_column(Text, default="[]")
    discovery_role: Mapped[str] = mapped_column(String(32), default="candidate", index=True)
    seed_family: Mapped[str] = mapped_column(String(64), default="other", index=True)
    seed_packet_id: Mapped[str | None] = mapped_column(String(180), index=True)
    seed_packet_title: Mapped[str | None] = mapped_column(String(300))
    platform_family: Mapped[str] = mapped_column(String(64), default="unknown", index=True)
    source_family_tags_json: Mapped[str] = mapped_column(Text, default="[]")
    scope_hints_json: Mapped[str] = mapped_column(Text, default='{"spatial":[],"language":[],"topic":[]}')
    last_discovery_outcome: Mapped[str | None] = mapped_column(Text)


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


class SourceReviewClaimCandidateORM(SourceDiscoveryBase):
    __tablename__ = "source_review_claim_candidates"
    __table_args__ = (
        UniqueConstraint("review_id", "source_id", "claim_index", name="uq_review_claim_candidate"),
    )

    claim_candidate_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    review_id: Mapped[str] = mapped_column(String(180), index=True)
    task_id: Mapped[str] = mapped_column(String(180), index=True)
    source_id: Mapped[str] = mapped_column(String(160), index=True)
    wave_id: Mapped[str | None] = mapped_column(String(160), index=True)
    snapshot_id: Mapped[str | None] = mapped_column(String(180), index=True)
    knowledge_node_id: Mapped[str | None] = mapped_column(String(180), index=True)
    claim_index: Mapped[int] = mapped_column(Integer, index=True)
    claim_text: Mapped[str] = mapped_column(Text, default="")
    claim_type: Mapped[str] = mapped_column(String(64), default="state", index=True)
    evidence_basis: Mapped[str] = mapped_column(String(64), default="contextual", index=True)
    status: Mapped[str] = mapped_column(String(32), default="pending", index=True)
    confidence_score: Mapped[float] = mapped_column(Float, default=0.5)
    created_at: Mapped[str] = mapped_column(String(64), index=True)
    applied_at: Mapped[str | None] = mapped_column(String(64), index=True)
    confidence_basis_json: Mapped[str] = mapped_column(Text, default="[]")
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
    outcome_summary: Mapped[str | None] = mapped_column(Text)
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
    knowledge_node_id: Mapped[str | None] = mapped_column(String(180), index=True)
    canonical_snapshot_id: Mapped[str | None] = mapped_column(String(180), index=True)
    duplicate_class: Mapped[str | None] = mapped_column(String(64), index=True)
    body_storage_mode: Mapped[str] = mapped_column(String(32), default="full_text", index=True)
    caveats_json: Mapped[str] = mapped_column(Text, default="[]")


class SourceMediaArtifactORM(SourceDiscoveryBase):
    __tablename__ = "source_media_artifacts"

    artifact_id: Mapped[str] = mapped_column(String(180), primary_key=True)
    source_id: Mapped[str] = mapped_column(String(160), index=True)
    origin_url: Mapped[str] = mapped_column(Text)
    canonical_url: Mapped[str] = mapped_column(Text, index=True)
    media_url: Mapped[str] = mapped_column(Text)
    parent_page_url: Mapped[str | None] = mapped_column(Text)
    published_at: Mapped[str | None] = mapped_column(String(64), index=True)
    discovered_at: Mapped[str] = mapped_column(String(64), index=True)
    captured_at: Mapped[str] = mapped_column(String(64), index=True)
    content_hash: Mapped[str] = mapped_column(String(80), index=True)
    perceptual_hash: Mapped[str | None] = mapped_column(String(80), index=True)
    mime_type: Mapped[str | None] = mapped_column(String(255))
    media_kind: Mapped[str] = mapped_column(String(32), default="unknown", index=True)
    width: Mapped[int | None] = mapped_column(Integer)
    height: Mapped[int | None] = mapped_column(Integer)
    byte_length: Mapped[int] = mapped_column(Integer, default=0)
    artifact_path: Mapped[str | None] = mapped_column(Text)
    duplicate_cluster_id: Mapped[str | None] = mapped_column(String(180), index=True)
    sequence_id: Mapped[str | None] = mapped_column(String(180), index=True)
    frame_index: Mapped[int | None] = mapped_column(Integer, index=True)
    sampled_at_ms: Mapped[int | None] = mapped_column(Integer, index=True)
    acquisition_method: Mapped[str] = mapped_column(String(64), default="direct_media_fetch", index=True)
    evidence_basis: Mapped[str] = mapped_column(String(64), default="observed", index=True)
    review_state: Mapped[str] = mapped_column(String(64), default="captured", index=True)
    observed_latitude: Mapped[float | None] = mapped_column(Float)
    observed_longitude: Mapped[float | None] = mapped_column(Float)
    exif_timestamp: Mapped[str | None] = mapped_column(String(64), index=True)
    metadata_json: Mapped[str] = mapped_column(Text, default="{}")
    caveats_json: Mapped[str] = mapped_column(Text, default="[]")


class SourceMediaDuplicateClusterORM(SourceDiscoveryBase):
    __tablename__ = "source_media_duplicate_clusters"

    cluster_id: Mapped[str] = mapped_column(String(180), primary_key=True)
    canonical_artifact_id: Mapped[str] = mapped_column(String(180), index=True)
    canonical_source_id: Mapped[str] = mapped_column(String(160), index=True)
    cluster_kind: Mapped[str] = mapped_column(String(64), default="duplicate_cluster", index=True)
    status: Mapped[str] = mapped_column(String(64), default="active", index=True)
    member_count: Mapped[int] = mapped_column(Integer, default=1)
    confidence_score: Mapped[float] = mapped_column(Float, default=0.5)
    first_seen_at: Mapped[str] = mapped_column(String(64), index=True)
    last_seen_at: Mapped[str] = mapped_column(String(64), index=True)
    confidence_basis_json: Mapped[str] = mapped_column(Text, default="[]")
    member_source_ids_json: Mapped[str] = mapped_column(Text, default="[]")
    caveats_json: Mapped[str] = mapped_column(Text, default="[]")


class SourceMediaComparisonORM(SourceDiscoveryBase):
    __tablename__ = "source_media_comparisons"
    __table_args__ = (
        UniqueConstraint("left_artifact_id", "right_artifact_id", name="uq_source_media_comparison_pair"),
    )

    comparison_id: Mapped[str] = mapped_column(String(180), primary_key=True)
    left_artifact_id: Mapped[str] = mapped_column(String(180), index=True)
    right_artifact_id: Mapped[str] = mapped_column(String(180), index=True)
    left_source_id: Mapped[str] = mapped_column(String(160), index=True)
    right_source_id: Mapped[str] = mapped_column(String(160), index=True)
    comparison_kind: Mapped[str] = mapped_column(String(64), index=True)
    status: Mapped[str] = mapped_column(String(64), index=True)
    algorithm_version: Mapped[str] = mapped_column(String(64), default="media-compare-v1")
    exact_hash_match: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    perceptual_hash_distance: Mapped[int | None] = mapped_column(Integer)
    ssim_score: Mapped[float | None] = mapped_column(Float)
    histogram_similarity: Mapped[float | None] = mapped_column(Float)
    edge_similarity: Mapped[float | None] = mapped_column(Float)
    ocr_text_similarity: Mapped[float | None] = mapped_column(Float)
    time_delta_seconds: Mapped[int | None] = mapped_column(Integer)
    confidence_score: Mapped[float] = mapped_column(Float, default=0.5)
    auto_signal_kind: Mapped[str | None] = mapped_column(String(64), index=True)
    created_at: Mapped[str] = mapped_column(String(64), index=True)
    confidence_basis_json: Mapped[str] = mapped_column(Text, default="[]")
    metadata_json: Mapped[str] = mapped_column(Text, default="{}")
    caveats_json: Mapped[str] = mapped_column(Text, default="[]")


class SourceMediaOcrRunORM(SourceDiscoveryBase):
    __tablename__ = "source_media_ocr_runs"

    ocr_run_id: Mapped[str] = mapped_column(String(180), primary_key=True)
    artifact_id: Mapped[str] = mapped_column(String(180), index=True)
    source_id: Mapped[str] = mapped_column(String(160), index=True)
    engine: Mapped[str] = mapped_column(String(64), index=True)
    engine_version: Mapped[str | None] = mapped_column(String(128))
    status: Mapped[str] = mapped_column(String(64), index=True)
    attempt_index: Mapped[int] = mapped_column(Integer, default=0)
    selected_result: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    preprocessing_json: Mapped[str] = mapped_column(Text, default="[]")
    raw_text: Mapped[str] = mapped_column(Text, default="")
    text_length: Mapped[int] = mapped_column(Integer, default=0)
    mean_confidence: Mapped[float | None] = mapped_column(Float)
    line_count: Mapped[int] = mapped_column(Integer, default=0)
    metadata_json: Mapped[str] = mapped_column(Text, default="{}")
    created_at: Mapped[str] = mapped_column(String(64), index=True)
    caveats_json: Mapped[str] = mapped_column(Text, default="[]")


class SourceMediaInterpretationORM(SourceDiscoveryBase):
    __tablename__ = "source_media_interpretations"

    interpretation_id: Mapped[str] = mapped_column(String(180), primary_key=True)
    artifact_id: Mapped[str] = mapped_column(String(180), index=True)
    source_id: Mapped[str] = mapped_column(String(160), index=True)
    ocr_run_id: Mapped[str | None] = mapped_column(String(180), index=True)
    adapter: Mapped[str] = mapped_column(String(64), index=True)
    model_name: Mapped[str | None] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(64), index=True)
    review_state: Mapped[str] = mapped_column(String(64), default="review_pending", index=True)
    people_analysis_performed: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    uncertainty_ceiling: Mapped[float | None] = mapped_column(Float)
    scene_labels_json: Mapped[str] = mapped_column(Text, default="[]")
    scene_summary: Mapped[str | None] = mapped_column(Text)
    place_hypothesis: Mapped[str | None] = mapped_column(Text)
    place_confidence: Mapped[float | None] = mapped_column(Float)
    place_basis: Mapped[str | None] = mapped_column(Text)
    time_of_day_guess: Mapped[str | None] = mapped_column(String(64), index=True)
    time_of_day_confidence: Mapped[float | None] = mapped_column(Float)
    time_of_day_basis: Mapped[str | None] = mapped_column(Text)
    season_guess: Mapped[str | None] = mapped_column(String(64), index=True)
    season_confidence: Mapped[float | None] = mapped_column(Float)
    season_basis: Mapped[str | None] = mapped_column(Text)
    geolocation_hypothesis: Mapped[str | None] = mapped_column(Text)
    geolocation_confidence: Mapped[float | None] = mapped_column(Float)
    geolocation_basis: Mapped[str | None] = mapped_column(Text)
    observed_latitude: Mapped[float | None] = mapped_column(Float)
    observed_longitude: Mapped[float | None] = mapped_column(Float)
    reasoning_lines_json: Mapped[str] = mapped_column(Text, default="[]")
    metadata_json: Mapped[str] = mapped_column(Text, default="{}")
    created_at: Mapped[str] = mapped_column(String(64), index=True)
    caveats_json: Mapped[str] = mapped_column(Text, default="[]")


class SourceMediaGeolocationRunORM(SourceDiscoveryBase):
    __tablename__ = "source_media_geolocation_runs"

    geolocation_run_id: Mapped[str] = mapped_column(String(180), primary_key=True)
    artifact_id: Mapped[str] = mapped_column(String(180), index=True)
    source_id: Mapped[str] = mapped_column(String(160), index=True)
    ocr_run_id: Mapped[str | None] = mapped_column(String(180), index=True)
    interpretation_id: Mapped[str | None] = mapped_column(String(180), index=True)
    engine: Mapped[str] = mapped_column(String(64), index=True)
    model_name: Mapped[str | None] = mapped_column(String(255))
    analyst_adapter: Mapped[str | None] = mapped_column(String(64), index=True)
    analyst_model_name: Mapped[str | None] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(64), index=True)
    review_state: Mapped[str] = mapped_column(String(64), default="interpret_review_pending", index=True)
    candidate_count: Mapped[int] = mapped_column(Integer, default=0)
    top_label: Mapped[str | None] = mapped_column(Text)
    top_latitude: Mapped[float | None] = mapped_column(Float)
    top_longitude: Mapped[float | None] = mapped_column(Float)
    top_confidence: Mapped[float | None] = mapped_column(Float)
    top_basis: Mapped[str | None] = mapped_column(Text)
    summary: Mapped[str | None] = mapped_column(Text)
    reasoning_lines_json: Mapped[str] = mapped_column(Text, default="[]")
    metadata_json: Mapped[str] = mapped_column(Text, default="{}")
    candidates_json: Mapped[str] = mapped_column(Text, default="[]")
    created_at: Mapped[str] = mapped_column(String(64), index=True)
    caveats_json: Mapped[str] = mapped_column(Text, default="[]")


class SourceMediaSequenceORM(SourceDiscoveryBase):
    __tablename__ = "source_media_sequences"

    sequence_id: Mapped[str] = mapped_column(String(180), primary_key=True)
    source_id: Mapped[str] = mapped_column(String(160), index=True)
    origin_url: Mapped[str] = mapped_column(Text)
    canonical_url: Mapped[str] = mapped_column(Text, index=True)
    parent_page_url: Mapped[str | None] = mapped_column(Text)
    media_kind: Mapped[str] = mapped_column(String(32), default="video_frame", index=True)
    sampler: Mapped[str] = mapped_column(String(64), default="ffmpeg", index=True)
    status: Mapped[str] = mapped_column(String(64), index=True)
    source_span_seconds: Mapped[int] = mapped_column(Integer, default=0)
    frame_count: Mapped[int] = mapped_column(Integer, default=0)
    sample_interval_seconds: Mapped[int] = mapped_column(Integer, default=0)
    request_budget: Mapped[int] = mapped_column(Integer, default=0)
    used_requests: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[str] = mapped_column(String(64), index=True)
    metadata_json: Mapped[str] = mapped_column(Text, default="{}")
    caveats_json: Mapped[str] = mapped_column(Text, default="[]")


class SourceKnowledgeNodeORM(SourceDiscoveryBase):
    __tablename__ = "source_knowledge_nodes"

    node_id: Mapped[str] = mapped_column(String(180), primary_key=True)
    canonical_snapshot_id: Mapped[str] = mapped_column(String(180), index=True)
    canonical_source_id: Mapped[str] = mapped_column(String(160), index=True)
    canonical_text_hash: Mapped[str] = mapped_column(String(80), index=True)
    canonical_url: Mapped[str] = mapped_column(Text)
    canonical_title: Mapped[str | None] = mapped_column(String(300))
    cluster_kind: Mapped[str] = mapped_column(String(64), default="content_cluster", index=True)
    duplicate_posture: Mapped[str] = mapped_column(String(64), default="canonical_only", index=True)
    supporting_record_count: Mapped[int] = mapped_column(Integer, default=1)
    supporting_source_count: Mapped[int] = mapped_column(Integer, default=1)
    independent_source_count: Mapped[int] = mapped_column(Integer, default=1)
    first_seen_at: Mapped[str] = mapped_column(String(64), index=True)
    last_seen_at: Mapped[str] = mapped_column(String(64), index=True)
    member_source_ids_json: Mapped[str] = mapped_column(Text, default="[]")
    as_detailed_in_addition_to_json: Mapped[str] = mapped_column(Text, default="[]")
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
    structure_scans_requested: Mapped[int] = mapped_column(Integer, default=0)
    structure_scans_completed: Mapped[int] = mapped_column(Integer, default=0)
    expansion_jobs_requested: Mapped[int] = mapped_column(Integer, default=0)
    expansion_jobs_completed: Mapped[int] = mapped_column(Integer, default=0)
    knowledge_backfill_jobs_requested: Mapped[int] = mapped_column(Integer, default=0)
    knowledge_backfill_jobs_completed: Mapped[int] = mapped_column(Integer, default=0)
    public_discovery_jobs_requested: Mapped[int] = mapped_column(Integer, default=0)
    public_discovery_jobs_completed: Mapped[int] = mapped_column(Integer, default=0)
    record_extract_jobs_requested: Mapped[int] = mapped_column(Integer, default=0)
    record_extract_jobs_completed: Mapped[int] = mapped_column(Integer, default=0)
    llm_tasks_requested: Mapped[int] = mapped_column(Integer, default=0)
    llm_tasks_completed: Mapped[int] = mapped_column(Integer, default=0)
    duplicate_snapshots_skipped: Mapped[int] = mapped_column(Integer, default=0)
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


class RuntimeServiceInstallationORM(SourceDiscoveryBase):
    __tablename__ = "runtime_service_installations"
    __table_args__ = (
        UniqueConstraint("worker_name", "platform", name="uq_runtime_service_installation_worker_platform"),
    )

    installation_id: Mapped[str] = mapped_column(String(180), primary_key=True)
    worker_name: Mapped[str] = mapped_column(String(64), index=True)
    platform: Mapped[str] = mapped_column(String(32), index=True)
    service_manager: Mapped[str] = mapped_column(String(64), index=True)
    service_name: Mapped[str] = mapped_column(String(180), index=True)
    artifact_file_name: Mapped[str] = mapped_column(String(255), default="")
    artifact_path: Mapped[str | None] = mapped_column(Text)
    target_path: Mapped[str | None] = mapped_column(Text)
    install_state: Mapped[str] = mapped_column(String(32), default="planned", index=True)
    last_action: Mapped[str | None] = mapped_column(String(64), index=True)
    last_action_status: Mapped[str | None] = mapped_column(String(64), index=True)
    last_action_at: Mapped[str | None] = mapped_column(String(64), index=True)
    last_summary: Mapped[str | None] = mapped_column(Text)
    updated_at: Mapped[str] = mapped_column(String(64), index=True)


class RuntimeServiceActionORM(SourceDiscoveryBase):
    __tablename__ = "runtime_service_actions"

    action_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    installation_id: Mapped[str] = mapped_column(String(180), index=True)
    worker_name: Mapped[str] = mapped_column(String(64), index=True)
    platform: Mapped[str] = mapped_column(String(32), index=True)
    action: Mapped[str] = mapped_column(String(64), index=True)
    requested_by: Mapped[str] = mapped_column(String(160), index=True)
    dry_run: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    status: Mapped[str] = mapped_column(String(64), index=True)
    command_json: Mapped[str] = mapped_column(Text, default="[]")
    artifact_path: Mapped[str | None] = mapped_column(Text)
    target_path: Mapped[str | None] = mapped_column(Text)
    stdout_excerpt: Mapped[str | None] = mapped_column(Text)
    stderr_excerpt: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[str] = mapped_column(String(64), index=True)
    finished_at: Mapped[str | None] = mapped_column(String(64), index=True)
