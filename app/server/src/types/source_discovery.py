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
SourceDiscoveryRole = Literal["root", "candidate", "derived"]
SourceDiscoverySeedFamily = Literal[
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
    "record_extract",
    "other",
]
SourceDiscoveryPlatformFamily = Literal[
    "unknown",
    "discourse",
    "mediawiki",
    "mastodon",
    "stack_exchange",
    "statuspage",
]
SourceAuthRequirement = Literal["no_auth", "login_required", "unknown"]
SourceCaptchaRequirement = Literal["no_captcha", "captcha_required", "unknown"]
SourceIntakeDisposition = Literal["public_no_auth", "hold_review", "blocked"]
SourceDiscoveryPriority = Literal["high", "medium", "low"]
SourceDiscoveryNextAction = Literal["structure_scan", "feed_link_scan", "sitemap_scan", "catalog_scan", "none"]
SourceDiscoveryDuplicateClass = Literal[
    "canonical",
    "exact_duplicate",
    "wire_syndication",
    "near_duplicate",
    "follow_up",
    "independent_corroboration",
    "correction_or_contradiction",
]
SourceDiscoveryStorageMode = Literal["full_text", "compacted_duplicate", "metadata_only"]
SourceDiscoveryKnowledgeBackfillMode = Literal["missing_only", "recompute_selected"]
SourceDiscoveryReviewClaimCandidateStatus = Literal["pending", "applied"]
ClaimOutcome = Literal[
    "confirmed",
    "contradicted",
    "corrected",
    "outdated",
    "unresolved",
    "not_applicable",
]
MediaEvidenceBasis = Literal["observed", "derived", "contextual", "source-reported", "model-interpreted"]
SourceDiscoveryMediaKind = Literal["image", "video_frame", "unknown"]
SourceDiscoveryMediaReviewState = Literal[
    "captured",
    "ocr_review_pending",
    "interpret_review_pending",
    "reviewed",
    "rejected",
]
SourceDiscoveryMediaComparisonKind = Literal[
    "exact_duplicate",
    "near_duplicate",
    "same_scene_minor_change",
    "same_location_major_change",
    "different_scene",
    "uncertain",
]
SourceDiscoveryMediaComparisonStatus = Literal["completed", "failed", "unavailable", "rejected"]
SourceDiscoveryAutoMediaSignalKind = Literal[
    "duplicate_cluster_joined",
    "minor_change_detected",
    "major_change_detected",
    "different_scene_conflict",
]
SourceDiscoveryMediaGeolocationEngine = Literal["auto", "deterministic", "fixture", "geoclip", "streetclip", "fusion"]
SourceDiscoveryMediaGeolocationAnalystAdapter = Literal[
    "none",
    "auto",
    "deterministic",
    "ollama",
    "openai_compat_local",
    "qwen_vl_local",
    "internvl_local",
    "llava_local",
]
SourceDiscoveryMediaGeolocationStatus = Literal["completed", "failed", "unavailable", "rejected"]
SourceDiscoveryMediaGeolocationCandidateKind = Literal["gps_point", "place_label", "country_region", "model_hypothesis"]


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
    auth_requirement: SourceAuthRequirement
    captcha_requirement: SourceCaptchaRequirement
    intake_disposition: SourceIntakeDisposition
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
    discovery_methods: list[str] = Field(default_factory=list)
    structure_hints: list[str] = Field(default_factory=list)
    discovery_role: SourceDiscoveryRole = "candidate"
    seed_family: SourceDiscoverySeedFamily = "other"
    seed_packet_id: str | None = None
    seed_packet_title: str | None = None
    platform_family: SourceDiscoveryPlatformFamily = "unknown"
    source_family_tags: list[str] = Field(default_factory=list)
    scope_hints: "SourceDiscoveryScopeHints" = Field(default_factory=lambda: SourceDiscoveryScopeHints())
    first_seen_at: str
    last_seen_at: str
    last_reputation_event_at: str | None = None
    next_check_at: str | None = None
    last_discovery_scan_at: str | None = None
    next_discovery_scan_at: str | None = None
    discovery_scan_fail_count: int = 0
    health_check_fail_count: int = 0
    next_discovery_action: SourceDiscoveryNextAction = "none"
    discovery_priority_score: int = 0
    discovery_priority: SourceDiscoveryPriority = "low"
    discovery_priority_basis: list[str] = Field(default_factory=list)
    last_discovery_outcome: str | None = None


class SourceDiscoveryScopeHints(CamelModel):
    spatial: list[str] = Field(default_factory=list)
    language: list[str] = Field(default_factory=list)
    topic: list[str] = Field(default_factory=list)


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
    auth_requirement: SourceAuthRequirement = "unknown"
    captcha_requirement: SourceCaptchaRequirement = "unknown"
    intake_disposition: SourceIntakeDisposition = "hold_review"
    wave_fit_score: float = 0.5
    relevance_basis: list[str] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)
    discovery_methods: list[str] = Field(default_factory=list)
    structure_hints: list[str] = Field(default_factory=list)
    discovery_role: SourceDiscoveryRole | None = None
    seed_family: SourceDiscoverySeedFamily | None = None
    seed_packet_id: str | None = None
    seed_packet_title: str | None = None
    platform_family: SourceDiscoveryPlatformFamily | None = None
    source_family_tags: list[str] = Field(default_factory=list)
    scope_hints: SourceDiscoveryScopeHints = Field(default_factory=SourceDiscoveryScopeHints)


class SourceDiscoverySeedUrlJobRequest(CamelModel):
    seed_url: str
    wave_id: str | None = None
    wave_title: str | None = None
    discovery_reason: str = "explicit seed URL"
    source_id: str | None = None
    title: str | None = None
    request_budget: int = 1
    caveats: list[str] = Field(default_factory=list)
    discovery_role: SourceDiscoveryRole | None = None
    seed_family: SourceDiscoverySeedFamily | None = None
    platform_family: SourceDiscoveryPlatformFamily | None = None
    source_family_tags: list[str] = Field(default_factory=list)
    scope_hints: SourceDiscoveryScopeHints = Field(default_factory=SourceDiscoveryScopeHints)


class SourceDiscoverySeedBatchRequest(CamelModel):
    seeds: list[SourceDiscoveryCandidateSeed] = Field(default_factory=list)
    packet_id: str | None = None
    packet_title: str | None = None
    packet_provenance: str | None = None
    imported_by: str | None = None
    packet_caveats: list[str] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


class SourceDiscoverySeedBatchResponse(CamelModel):
    memories: list[SourceDiscoveryMemory] = Field(default_factory=list)
    created_count: int = 0
    updated_count: int = 0
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


class SourceDiscoverySitemapScanRequest(CamelModel):
    sitemap_url: str
    wave_id: str | None = None
    wave_title: str | None = None
    discovery_reason: str = "bounded sitemap scan"
    fixture_text: str | None = None
    max_discovered: int = 25
    request_budget: int = 1
    caveats: list[str] = Field(default_factory=list)


class SourceDiscoverySitemapScanResponse(CamelModel):
    job: SourceDiscoveryJobSummary
    memories: list[SourceDiscoveryMemory] = Field(default_factory=list)
    sitemap_type: str
    scanned_url_count: int = 0
    extracted_url_count: int = 0
    discovered_sitemap_urls: list[str] = Field(default_factory=list)
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


class SourceDiscoveryStructureScanRequest(CamelModel):
    target_url: str
    wave_id: str | None = None
    wave_title: str | None = None
    discovery_reason: str = "public site structure scan"
    fixture_html: str | None = None
    fixture_robots_txt: str | None = None
    request_budget: int = 1
    max_discovered: int = 10
    caveats: list[str] = Field(default_factory=list)


class SourceDiscoveryStructureScanResponse(CamelModel):
    job: SourceDiscoveryJobSummary
    memory: SourceDiscoveryMemory | None = None
    memories: list[SourceDiscoveryMemory] = Field(default_factory=list)
    discovered_feed_urls: list[str] = Field(default_factory=list)
    discovered_sitemap_urls: list[str] = Field(default_factory=list)
    discovered_navigation_urls: list[str] = Field(default_factory=list)
    platform_family: SourceDiscoveryPlatformFamily = "unknown"
    auth_signals: list[str] = Field(default_factory=list)
    captcha_signals: list[str] = Field(default_factory=list)
    intake_disposition: SourceIntakeDisposition
    structure_hints: list[str] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


class SourceDiscoveryKnowledgeBackfillRequest(CamelModel):
    source_ids: list[str] = Field(default_factory=list)
    snapshot_ids: list[str] = Field(default_factory=list)
    max_snapshots: int = 100
    mode: SourceDiscoveryKnowledgeBackfillMode = "missing_only"
    caveats: list[str] = Field(default_factory=list)


class SourceDiscoveryKnowledgeBackfillResponse(CamelModel):
    job: SourceDiscoveryJobSummary
    processed_snapshot_count: int
    created_node_count: int
    updated_node_count: int
    compacted_snapshot_count: int
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
    knowledge_node_id: str | None = None
    canonical_snapshot_id: str | None = None
    duplicate_class: SourceDiscoveryDuplicateClass | None = None
    body_storage_mode: SourceDiscoveryStorageMode = "full_text"
    supporting_source_count: int = 1
    independent_source_count: int = 1
    as_detailed_in_addition_to: list[str] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


class SourceDiscoveryKnowledgeNodeSummary(CamelModel):
    node_id: str
    canonical_snapshot_id: str
    canonical_source_id: str
    canonical_url: str
    canonical_title: str | None = None
    cluster_kind: str
    duplicate_posture: str
    supporting_record_count: int
    supporting_source_count: int
    independent_source_count: int
    first_seen_at: str
    last_seen_at: str
    member_source_ids: list[str] = Field(default_factory=list)
    as_detailed_in_addition_to: list[str] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


class SourceDiscoveryKnowledgeNodeMember(CamelModel):
    snapshot_id: str
    source_id: str
    url: str
    title: str | None = None
    source_domain: str
    duplicate_class: SourceDiscoveryDuplicateClass
    body_storage_mode: SourceDiscoveryStorageMode
    is_canonical: bool
    published_at: str | None = None
    fetched_at: str


class SourceDiscoveryKnowledgeNodeDetailResponse(CamelModel):
    node: SourceDiscoveryKnowledgeNodeSummary
    members: list[SourceDiscoveryKnowledgeNodeMember] = Field(default_factory=list)
    pending_claim_count: int = 0
    latest_review_claim_at: str | None = None
    caveats: list[str] = Field(default_factory=list)


class SourceDiscoveryKnowledgeNodeListResponse(CamelModel):
    metadata: dict[str, object]
    nodes: list[SourceDiscoveryKnowledgeNodeSummary] = Field(default_factory=list)
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


class SourceDiscoveryMediaArtifactSummary(CamelModel):
    artifact_id: str
    source_id: str
    origin_url: str
    canonical_url: str
    media_url: str
    parent_page_url: str | None = None
    published_at: str | None = None
    discovered_at: str
    captured_at: str
    content_hash: str
    perceptual_hash: str | None = None
    mime_type: str | None = None
    media_kind: SourceDiscoveryMediaKind = "unknown"
    width: int | None = None
    height: int | None = None
    byte_length: int = 0
    artifact_path: str | None = None
    duplicate_cluster_id: str | None = None
    sequence_id: str | None = None
    frame_index: int | None = None
    sampled_at_ms: int | None = None
    acquisition_method: str
    evidence_basis: MediaEvidenceBasis
    review_state: SourceDiscoveryMediaReviewState = "captured"
    observed_latitude: float | None = None
    observed_longitude: float | None = None
    exif_timestamp: str | None = None
    metadata: dict[str, object] = Field(default_factory=dict)
    caveats: list[str] = Field(default_factory=list)


class SourceDiscoveryMediaOcrBlock(CamelModel):
    block_index: int
    text: str
    confidence: float | None = None
    left: int | None = None
    top: int | None = None
    width: int | None = None
    height: int | None = None


class SourceDiscoveryMediaOcrRunSummary(CamelModel):
    ocr_run_id: str
    artifact_id: str
    source_id: str
    engine: str
    engine_version: str | None = None
    status: str
    attempt_index: int = 0
    selected_result: bool = False
    preprocessing: list[str] = Field(default_factory=list)
    raw_text: str = ""
    text_length: int = 0
    mean_confidence: float | None = None
    line_count: int = 0
    metadata: dict[str, object] = Field(default_factory=dict)
    created_at: str
    caveats: list[str] = Field(default_factory=list)
    blocks: list[SourceDiscoveryMediaOcrBlock] = Field(default_factory=list)


class SourceDiscoveryMediaInterpretationSummary(CamelModel):
    interpretation_id: str
    artifact_id: str
    source_id: str
    ocr_run_id: str | None = None
    adapter: str
    model_name: str | None = None
    status: str
    review_state: SourceDiscoveryMediaReviewState = "interpret_review_pending"
    people_analysis_performed: bool = False
    uncertainty_ceiling: float | None = None
    scene_labels: list[str] = Field(default_factory=list)
    scene_summary: str | None = None
    place_hypothesis: str | None = None
    place_confidence: float | None = None
    place_basis: str | None = None
    time_of_day_guess: str | None = None
    time_of_day_confidence: float | None = None
    time_of_day_basis: str | None = None
    season_guess: str | None = None
    season_confidence: float | None = None
    season_basis: str | None = None
    geolocation_hypothesis: str | None = None
    geolocation_confidence: float | None = None
    geolocation_basis: str | None = None
    observed_latitude: float | None = None
    observed_longitude: float | None = None
    reasoning_lines: list[str] = Field(default_factory=list)
    metadata: dict[str, object] = Field(default_factory=dict)
    created_at: str
    caveats: list[str] = Field(default_factory=list)


class SourceDiscoveryMediaDuplicateClusterSummary(CamelModel):
    cluster_id: str
    canonical_artifact_id: str
    canonical_source_id: str
    cluster_kind: str
    status: str
    member_count: int = 0
    confidence_score: float = 0.5
    first_seen_at: str
    last_seen_at: str
    confidence_basis: list[str] = Field(default_factory=list)
    member_source_ids: list[str] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


class SourceDiscoveryMediaComparisonSummary(CamelModel):
    comparison_id: str
    left_artifact_id: str
    right_artifact_id: str
    left_source_id: str
    right_source_id: str
    comparison_kind: SourceDiscoveryMediaComparisonKind
    status: SourceDiscoveryMediaComparisonStatus
    algorithm_version: str
    exact_hash_match: bool = False
    perceptual_hash_distance: int | None = None
    ssim_score: float | None = None
    histogram_similarity: float | None = None
    edge_similarity: float | None = None
    ocr_text_similarity: float | None = None
    time_delta_seconds: int | None = None
    confidence_score: float = 0.5
    confidence_basis: list[str] = Field(default_factory=list)
    auto_signal_kind: SourceDiscoveryAutoMediaSignalKind | None = None
    metadata: dict[str, object] = Field(default_factory=dict)
    created_at: str
    caveats: list[str] = Field(default_factory=list)


class SourceDiscoveryMediaGeolocationCandidateSummary(CamelModel):
    rank: int
    candidate_kind: SourceDiscoveryMediaGeolocationCandidateKind = "gps_point"
    label: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    confidence: float | None = None
    confidence_score: float | None = None
    confidence_ceiling: float | None = None
    engine: str
    basis: list[str] = Field(default_factory=list)
    supporting_evidence: list[str] = Field(default_factory=list)
    contradicting_evidence: list[str] = Field(default_factory=list)
    engine_agreement: dict[str, object] = Field(default_factory=dict)
    provenance_chain: list[str] = Field(default_factory=list)
    inherited: bool = False
    inherited_from_artifact_ids: list[str] = Field(default_factory=list)
    metadata: dict[str, object] = Field(default_factory=dict)
    caveats: list[str] = Field(default_factory=list)


class SourceDiscoveryMediaGeolocationClueSummary(CamelModel):
    clue_type: str
    text: str
    confidence: float | None = None
    normalized_value: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    reason: str | None = None
    inherited: bool = False
    inherited_from_artifact_id: str | None = None
    inherited_from_geolocation_run_id: str | None = None
    inherited_from_comparison_id: str | None = None
    metadata: dict[str, object] = Field(default_factory=dict)


class SourceDiscoveryMediaGeolocationCluePacket(CamelModel):
    coordinate_clues: list[SourceDiscoveryMediaGeolocationClueSummary] = Field(default_factory=list)
    place_text_clues: list[SourceDiscoveryMediaGeolocationClueSummary] = Field(default_factory=list)
    script_language_clues: list[SourceDiscoveryMediaGeolocationClueSummary] = Field(default_factory=list)
    environment_clues: list[SourceDiscoveryMediaGeolocationClueSummary] = Field(default_factory=list)
    time_clues: list[SourceDiscoveryMediaGeolocationClueSummary] = Field(default_factory=list)
    rejected_clues: list[SourceDiscoveryMediaGeolocationClueSummary] = Field(default_factory=list)


class SourceDiscoveryMediaGeolocationEngineAttemptSummary(CamelModel):
    engine: str
    role: str
    status: str
    model_name: str | None = None
    warm_state: str | None = None
    availability_reason: str | None = None
    produced_candidate_count: int = 0
    metadata: dict[str, object] = Field(default_factory=dict)
    caveats: list[str] = Field(default_factory=list)


class SourceDiscoveryMediaGeolocationRunSummary(CamelModel):
    geolocation_run_id: str
    artifact_id: str
    source_id: str
    ocr_run_id: str | None = None
    interpretation_id: str | None = None
    engine: SourceDiscoveryMediaGeolocationEngine
    model_name: str | None = None
    analyst_adapter: SourceDiscoveryMediaGeolocationAnalystAdapter | None = None
    analyst_model_name: str | None = None
    status: SourceDiscoveryMediaGeolocationStatus
    review_state: SourceDiscoveryMediaReviewState = "interpret_review_pending"
    candidate_count: int = 0
    top_label: str | None = None
    top_latitude: float | None = None
    top_longitude: float | None = None
    top_confidence: float | None = None
    top_confidence_ceiling: float | None = None
    top_basis: str | None = None
    summary: str | None = None
    confidence_ceiling: float | None = None
    supporting_evidence: list[str] = Field(default_factory=list)
    contradicting_evidence: list[str] = Field(default_factory=list)
    engine_agreement: dict[str, object] = Field(default_factory=dict)
    provenance_chain: list[str] = Field(default_factory=list)
    inherited_from_artifact_ids: list[str] = Field(default_factory=list)
    clue_packet: SourceDiscoveryMediaGeolocationCluePacket = Field(default_factory=SourceDiscoveryMediaGeolocationCluePacket)
    engine_attempts: list[SourceDiscoveryMediaGeolocationEngineAttemptSummary] = Field(default_factory=list)
    reasoning_lines: list[str] = Field(default_factory=list)
    metadata: dict[str, object] = Field(default_factory=dict)
    candidates: list[SourceDiscoveryMediaGeolocationCandidateSummary] = Field(default_factory=list)
    created_at: str
    caveats: list[str] = Field(default_factory=list)


class SourceDiscoveryAutoMediaSignalSummary(CamelModel):
    comparison_id: str
    signal_kind: SourceDiscoveryAutoMediaSignalKind
    artifact_ids: list[str] = Field(default_factory=list)
    confidence_score: float = 0.5
    confidence_basis: list[str] = Field(default_factory=list)
    created_at: str
    caveats: list[str] = Field(default_factory=list)


class SourceDiscoveryMediaSequenceSummary(CamelModel):
    sequence_id: str
    source_id: str
    origin_url: str
    canonical_url: str
    parent_page_url: str | None = None
    media_kind: SourceDiscoveryMediaKind = "video_frame"
    sampler: str
    status: str
    source_span_seconds: int = 0
    frame_count: int = 0
    sample_interval_seconds: int = 0
    request_budget: int = 0
    used_requests: int = 0
    created_at: str
    metadata: dict[str, object] = Field(default_factory=dict)
    caveats: list[str] = Field(default_factory=list)


class SourceDiscoveryMediaArtifactFetchRequest(CamelModel):
    source_id: str
    media_url: str
    origin_url: str | None = None
    parent_page_url: str | None = None
    published_at: str | None = None
    fixture_bytes_base64: str | None = None
    fixture_content_type: str | None = None
    request_budget: int = 1
    caveats: list[str] = Field(default_factory=list)


class SourceDiscoveryMediaArtifactFetchResponse(CamelModel):
    job: SourceDiscoveryJobSummary
    memory: SourceDiscoveryMemory | None = None
    artifact: SourceDiscoveryMediaArtifactSummary | None = None
    caveats: list[str] = Field(default_factory=list)


class SourceDiscoveryMediaArtifactListResponse(CamelModel):
    metadata: dict[str, object]
    artifacts: list[SourceDiscoveryMediaArtifactSummary] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


class SourceDiscoveryMediaArtifactDetailResponse(CamelModel):
    artifact: SourceDiscoveryMediaArtifactSummary
    ocr_runs: list[SourceDiscoveryMediaOcrRunSummary] = Field(default_factory=list)
    interpretations: list[SourceDiscoveryMediaInterpretationSummary] = Field(default_factory=list)
    geolocation_runs: list[SourceDiscoveryMediaGeolocationRunSummary] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


class SourceDiscoveryMediaOcrJobRequest(CamelModel):
    artifact_id: str
    engine: Literal["auto", "fixture", "tesseract", "rapidocr_onnx"] = "auto"
    preprocess_mode: Literal["none", "auto", "grayscale", "high_contrast", "threshold", "sharpen", "text_region_crop"] = "auto"
    fixture_text: str | None = None
    fixture_blocks: list[SourceDiscoveryMediaOcrBlock] = Field(default_factory=list)
    request_budget: int = 0
    caveats: list[str] = Field(default_factory=list)


class SourceDiscoveryMediaOcrJobResponse(CamelModel):
    job: SourceDiscoveryJobSummary
    artifact: SourceDiscoveryMediaArtifactSummary | None = None
    ocr_run: SourceDiscoveryMediaOcrRunSummary | None = None
    snapshot: SourceDiscoveryContentSnapshotSummary | None = None
    caveats: list[str] = Field(default_factory=list)


class SourceDiscoveryMediaInterpretationJobRequest(CamelModel):
    artifact_id: str
    adapter: Literal["auto", "deterministic", "fixture", "ollama", "openai_compat_local"] = "auto"
    model: str | None = None
    allow_local_ai: bool = True
    fixture_result: dict[str, object] | None = None
    request_budget: int = 0
    caveats: list[str] = Field(default_factory=list)


class SourceDiscoveryMediaInterpretationJobResponse(CamelModel):
    job: SourceDiscoveryJobSummary
    artifact: SourceDiscoveryMediaArtifactSummary | None = None
    interpretation: SourceDiscoveryMediaInterpretationSummary | None = None
    caveats: list[str] = Field(default_factory=list)


class SourceDiscoveryMediaGeolocateJobRequest(CamelModel):
    artifact_id: str
    engine: SourceDiscoveryMediaGeolocationEngine = "fusion"
    analyst_adapter: SourceDiscoveryMediaGeolocationAnalystAdapter = "auto"
    model: str | None = None
    analyst_model: str | None = None
    candidate_labels: list[str] = Field(default_factory=list)
    allow_local_ai: bool = True
    fixture_result: dict[str, object] | None = None
    request_budget: int = 0
    caveats: list[str] = Field(default_factory=list)


class SourceDiscoveryMediaGeolocateJobResponse(CamelModel):
    job: SourceDiscoveryJobSummary
    artifact: SourceDiscoveryMediaArtifactSummary | None = None
    geolocation_run: SourceDiscoveryMediaGeolocationRunSummary | None = None
    caveats: list[str] = Field(default_factory=list)


class SourceDiscoveryMediaGeolocationDetailResponse(CamelModel):
    geolocation_run: SourceDiscoveryMediaGeolocationRunSummary
    artifact: SourceDiscoveryMediaArtifactSummary | None = None
    ocr_run: SourceDiscoveryMediaOcrRunSummary | None = None
    interpretation: SourceDiscoveryMediaInterpretationSummary | None = None
    caveats: list[str] = Field(default_factory=list)


class SourceDiscoveryMediaCompareJobRequest(CamelModel):
    left_artifact_id: str
    right_artifact_id: str
    request_budget: int = 0
    caveats: list[str] = Field(default_factory=list)


class SourceDiscoveryMediaCompareJobResponse(CamelModel):
    job: SourceDiscoveryJobSummary
    comparison: SourceDiscoveryMediaComparisonSummary | None = None
    left_artifact: SourceDiscoveryMediaArtifactSummary | None = None
    right_artifact: SourceDiscoveryMediaArtifactSummary | None = None
    cluster: SourceDiscoveryMediaDuplicateClusterSummary | None = None
    caveats: list[str] = Field(default_factory=list)


class SourceDiscoveryMediaComparisonDetailResponse(CamelModel):
    comparison: SourceDiscoveryMediaComparisonSummary
    left_artifact: SourceDiscoveryMediaArtifactSummary | None = None
    right_artifact: SourceDiscoveryMediaArtifactSummary | None = None
    cluster: SourceDiscoveryMediaDuplicateClusterSummary | None = None
    caveats: list[str] = Field(default_factory=list)


class SourceDiscoveryMediaFrameSampleJobRequest(CamelModel):
    source_id: str
    media_url: str
    origin_url: str | None = None
    parent_page_url: str | None = None
    source_span_seconds: int = 60
    max_frames: int = 12
    sample_interval_seconds: int = 5
    fixture_frames_base64: list[str] = Field(default_factory=list)
    fixture_content_type: str | None = None
    request_budget: int = 1
    caveats: list[str] = Field(default_factory=list)


class SourceDiscoveryMediaFrameSampleJobResponse(CamelModel):
    job: SourceDiscoveryJobSummary
    sequence: SourceDiscoveryMediaSequenceSummary | None = None
    artifacts: list[SourceDiscoveryMediaArtifactSummary] = Field(default_factory=list)
    comparisons: list[SourceDiscoveryMediaComparisonSummary] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


class SourceDiscoveryMediaSequenceDetailResponse(CamelModel):
    sequence: SourceDiscoveryMediaSequenceSummary
    artifacts: list[SourceDiscoveryMediaArtifactSummary] = Field(default_factory=list)
    comparisons: list[SourceDiscoveryMediaComparisonSummary] = Field(default_factory=list)
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
    auth_requirement: SourceAuthRequirement
    captcha_requirement: SourceCaptchaRequirement
    intake_disposition: SourceIntakeDisposition
    priority: Literal["high", "medium", "low"]
    review_reasons: list[str] = Field(default_factory=list)
    recommended_actions: list[str] = Field(default_factory=list)
    structure_hints: list[str] = Field(default_factory=list)
    discovery_role: SourceDiscoveryRole = "candidate"
    seed_family: SourceDiscoverySeedFamily = "other"
    seed_packet_id: str | None = None
    seed_packet_title: str | None = None
    platform_family: SourceDiscoveryPlatformFamily = "unknown"
    source_family_tags: list[str] = Field(default_factory=list)
    scope_hints: SourceDiscoveryScopeHints = Field(default_factory=SourceDiscoveryScopeHints)
    global_reputation_score: float
    domain_reputation_score: float
    source_health_score: float
    timeliness_score: float
    confidence_level: str
    best_wave_id: str | None = None
    best_wave_title: str | None = None
    best_wave_fit_score: float | None = None
    next_check_at: str | None = None
    pending_claim_count: int = 0
    next_discovery_action: SourceDiscoveryNextAction = "none"
    discovery_priority_score: int = 0
    discovery_priority: SourceDiscoveryPriority = "low"
    discovery_priority_basis: list[str] = Field(default_factory=list)
    last_discovery_outcome: str | None = None


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
    knowledge_nodes: list[SourceDiscoveryKnowledgeNodeSummary] = Field(default_factory=list)
    media_artifacts: list[SourceDiscoveryMediaArtifactSummary] = Field(default_factory=list)
    media_clusters: list[SourceDiscoveryMediaDuplicateClusterSummary] = Field(default_factory=list)
    media_comparisons: list[SourceDiscoveryMediaComparisonSummary] = Field(default_factory=list)
    auto_media_signals: list[SourceDiscoveryAutoMediaSignalSummary] = Field(default_factory=list)
    media_sequences: list[SourceDiscoveryMediaSequenceSummary] = Field(default_factory=list)
    media_ocr_runs: list[SourceDiscoveryMediaOcrRunSummary] = Field(default_factory=list)
    media_interpretations: list[SourceDiscoveryMediaInterpretationSummary] = Field(default_factory=list)
    media_geolocations: list[SourceDiscoveryMediaGeolocationRunSummary] = Field(default_factory=list)
    health_checks: list[SourceDiscoveryHealthCheckSummary] = Field(default_factory=list)
    review_actions: list[SourceDiscoveryReviewActionSummary] = Field(default_factory=list)
    reputation_events: list[SourceDiscoveryReputationEventSummary] = Field(default_factory=list)
    claim_outcomes: list[SourceDiscoveryClaimOutcomeSummary] = Field(default_factory=list)
    pending_review_claims: list["SourceDiscoveryReviewClaimCandidateSummary"] = Field(default_factory=list)
    pending_claim_count: int = 0
    latest_review_claim_at: str | None = None
    caveats: list[str] = Field(default_factory=list)


class SourceDiscoveryMemoryExportPacket(CamelModel):
    export_type: str
    generated_at: str
    memory: SourceDiscoveryMemory
    wave_fits: list[SourceDiscoveryWaveFit] = Field(default_factory=list)
    snapshots: list[SourceDiscoveryContentSnapshotSummary] = Field(default_factory=list)
    knowledge_nodes: list[SourceDiscoveryKnowledgeNodeSummary] = Field(default_factory=list)
    media_artifacts: list[SourceDiscoveryMediaArtifactSummary] = Field(default_factory=list)
    media_clusters: list[SourceDiscoveryMediaDuplicateClusterSummary] = Field(default_factory=list)
    media_comparisons: list[SourceDiscoveryMediaComparisonSummary] = Field(default_factory=list)
    auto_media_signals: list[SourceDiscoveryAutoMediaSignalSummary] = Field(default_factory=list)
    media_sequences: list[SourceDiscoveryMediaSequenceSummary] = Field(default_factory=list)
    media_ocr_runs: list[SourceDiscoveryMediaOcrRunSummary] = Field(default_factory=list)
    media_interpretations: list[SourceDiscoveryMediaInterpretationSummary] = Field(default_factory=list)
    media_geolocations: list[SourceDiscoveryMediaGeolocationRunSummary] = Field(default_factory=list)
    health_checks: list[SourceDiscoveryHealthCheckSummary] = Field(default_factory=list)
    review_actions: list[SourceDiscoveryReviewActionSummary] = Field(default_factory=list)
    reputation_events: list[SourceDiscoveryReputationEventSummary] = Field(default_factory=list)
    claim_outcomes: list[SourceDiscoveryClaimOutcomeSummary] = Field(default_factory=list)
    pending_review_claims: list["SourceDiscoveryReviewClaimCandidateSummary"] = Field(default_factory=list)
    pending_claim_count: int = 0
    latest_review_claim_at: str | None = None
    caveats: list[str] = Field(default_factory=list)


class SourceDiscoveryMemoryExportResponse(CamelModel):
    packet: SourceDiscoveryMemoryExportPacket
    caveats: list[str] = Field(default_factory=list)


class SourceDiscoverySchedulerTickRequest(CamelModel):
    health_check_limit: int = 5
    structure_scan_limit: int = 0
    public_discovery_job_limit: int = 0
    expansion_job_limit: int = 0
    knowledge_backfill_limit: int = 0
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
    structure_scans_completed: int
    public_discovery_jobs_completed: int
    expansion_jobs_completed: int
    knowledge_backfill_jobs_completed: int
    record_extract_jobs_completed: int
    llm_tasks_completed: int
    duplicate_snapshots_skipped: int
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


class SourceDiscoveryDiscoveryRunSummary(CamelModel):
    job_id: str
    job_type: str
    root_source_id: str | None = None
    root_url: str | None = None
    status: str
    discovered_candidate_count: int = 0
    used_requests: int = 0
    rejected_reason: str | None = None
    outcome_summary: str | None = None
    started_at: str
    finished_at: str | None = None
    caveats: list[str] = Field(default_factory=list)


class SourceDiscoveryDiscoveryOverviewResponse(CamelModel):
    metadata: dict[str, object]
    total_root_count: int = 0
    due_root_count: int = 0
    pending_structure_scan_count: int = 0
    eligible_public_followup_count: int = 0
    blocked_root_count: int = 0
    hold_review_root_count: int = 0
    counts_by_seed_family: dict[str, int] = Field(default_factory=dict)
    counts_by_platform_family: dict[str, int] = Field(default_factory=dict)
    counts_by_next_action: dict[str, int] = Field(default_factory=dict)
    counts_by_intake_disposition: dict[str, int] = Field(default_factory=dict)
    counts_by_owner_lane: dict[str, int] = Field(default_factory=dict)
    recent_runs: list[SourceDiscoveryDiscoveryRunSummary] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


class SourceDiscoveryDiscoveryQueueItem(CamelModel):
    source_id: str
    title: str
    url: str
    owner_lane: str | None = None
    source_type: str
    source_class: SourceClass
    lifecycle_state: str
    policy_state: str
    intake_disposition: SourceIntakeDisposition
    auth_requirement: SourceAuthRequirement
    captcha_requirement: SourceCaptchaRequirement
    discovery_role: SourceDiscoveryRole
    seed_family: SourceDiscoverySeedFamily
    seed_packet_id: str | None = None
    seed_packet_title: str | None = None
    platform_family: SourceDiscoveryPlatformFamily = "unknown"
    source_family_tags: list[str] = Field(default_factory=list)
    scope_hints: SourceDiscoveryScopeHints = Field(default_factory=SourceDiscoveryScopeHints)
    structure_hints: list[str] = Field(default_factory=list)
    source_health: str
    source_health_score: float
    global_reputation_score: float
    domain_reputation_score: float
    best_wave_id: str | None = None
    best_wave_title: str | None = None
    best_wave_fit_score: float | None = None
    next_discovery_action: SourceDiscoveryNextAction = "none"
    discovery_priority_score: int = 0
    discovery_priority: SourceDiscoveryPriority = "low"
    discovery_priority_basis: list[str] = Field(default_factory=list)
    why_eligible: list[str] = Field(default_factory=list)
    why_prioritized: list[str] = Field(default_factory=list)
    blocked_reasons: list[str] = Field(default_factory=list)
    last_discovery_outcome: str | None = None
    last_discovery_scan_at: str | None = None
    next_discovery_scan_at: str | None = None
    discovery_scan_fail_count: int = 0


class SourceDiscoveryDiscoveryQueueResponse(CamelModel):
    metadata: dict[str, object]
    items: list[SourceDiscoveryDiscoveryQueueItem] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


class SourceDiscoveryDiscoveryRunsResponse(CamelModel):
    metadata: dict[str, object]
    runs: list[SourceDiscoveryDiscoveryRunSummary] = Field(default_factory=list)
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
SourceDiscoveryRuntimeServiceAction = Literal[
    "materialize",
    "install",
    "start",
    "stop",
    "restart",
    "uninstall",
    "status",
]


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


class SourceDiscoveryRuntimePathSummary(CamelModel):
    resource_dir: str
    user_data_dir: str
    log_dir: str
    cache_dir: str
    service_artifact_dir: str


class SourceDiscoveryRuntimeServiceInstallationSummary(CamelModel):
    installation_id: str
    worker_name: SourceDiscoveryRuntimeWorkerName
    platform: SourceDiscoveryRuntimeServicePlatform
    service_manager: SourceDiscoveryRuntimeServiceManager
    service_name: str
    artifact_file_name: str
    artifact_path: str | None = None
    target_path: str | None = None
    install_state: str
    last_action: str | None = None
    last_action_status: str | None = None
    last_action_at: str | None = None
    last_summary: str | None = None


class SourceDiscoveryRuntimeStatusResponse(CamelModel):
    runtime_mode: str
    recommended_runtime_deployment: str
    service_worker_entrypoint: str
    runtime_paths: SourceDiscoveryRuntimePathSummary
    supported_service_managers: list[str] = Field(default_factory=list)
    source_discovery_scheduler_enabled: bool
    source_discovery_scheduler_running: bool
    source_discovery_scheduler_poll_seconds: int
    source_discovery_scheduler_last_tick_at: str | None = None
    source_discovery_scheduler_last_error: str | None = None
    source_discovery_scheduler_last_summary: str | None = None
    discovery_root_count: int = 0
    due_discovery_root_count: int = 0
    pending_structure_scan_count: int = 0
    eligible_public_followup_count: int = 0
    last_discovery_run_summary: str | None = None
    wave_monitor_scheduler_enabled: bool
    wave_monitor_scheduler_running: bool
    wave_monitor_scheduler_poll_seconds: int
    wave_monitor_scheduler_last_tick_at: str | None = None
    wave_monitor_scheduler_last_error: str | None = None
    wave_monitor_scheduler_last_summary: str | None = None
    workers: list[SourceDiscoveryRuntimeWorkerSummary] = Field(default_factory=list)
    service_installations: list[SourceDiscoveryRuntimeServiceInstallationSummary] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


class SourceDiscoveryRuntimeServiceSpec(CamelModel):
    worker_name: SourceDiscoveryRuntimeWorkerName
    platform: SourceDiscoveryRuntimeServicePlatform
    service_manager: SourceDiscoveryRuntimeServiceManager
    service_name: str
    working_directory: str
    artifact_file_name: str
    artifact_text: str
    artifact_path: str | None = None
    target_path: str | None = None
    entry_command: list[str] = Field(default_factory=list)
    install_command: list[str] = Field(default_factory=list)
    start_command: list[str] = Field(default_factory=list)
    stop_command: list[str] = Field(default_factory=list)
    status_command: list[str] = Field(default_factory=list)
    uninstall_command: list[str] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


class SourceDiscoveryRuntimeServiceBundleResponse(CamelModel):
    runtime_mode: str
    current_platform: SourceDiscoveryRuntimeServicePlatform
    entrypoint_module: str
    runtime_paths: SourceDiscoveryRuntimePathSummary
    services: list[SourceDiscoveryRuntimeServiceSpec] = Field(default_factory=list)
    installations: list[SourceDiscoveryRuntimeServiceInstallationSummary] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)


class SourceDiscoveryRuntimeServiceActionRequest(CamelModel):
    action: SourceDiscoveryRuntimeServiceAction
    requested_by: str
    platform_name: SourceDiscoveryRuntimeServicePlatform | None = None
    dry_run: bool = False
    overwrite_artifact: bool = False
    timeout_seconds: int = 20
    caveats: list[str] = Field(default_factory=list)


class SourceDiscoveryRuntimeServiceActionSummary(CamelModel):
    action_id: int
    installation_id: str
    worker_name: SourceDiscoveryRuntimeWorkerName
    platform: SourceDiscoveryRuntimeServicePlatform
    action: SourceDiscoveryRuntimeServiceAction
    requested_by: str
    dry_run: bool
    status: str
    command: list[str] = Field(default_factory=list)
    artifact_path: str | None = None
    target_path: str | None = None
    stdout_excerpt: str | None = None
    stderr_excerpt: str | None = None
    created_at: str
    finished_at: str | None = None


class SourceDiscoveryRuntimeServiceActionResponse(CamelModel):
    installation: SourceDiscoveryRuntimeServiceInstallationSummary
    action: SourceDiscoveryRuntimeServiceActionSummary
    caveats: list[str] = Field(default_factory=list)


class SourceDiscoveryReviewClaimCandidateSummary(CamelModel):
    claim_candidate_id: int
    review_id: str
    task_id: str
    source_id: str
    wave_id: str | None = None
    snapshot_id: str | None = None
    knowledge_node_id: str | None = None
    claim_index: int
    claim_text: str
    claim_type: str
    evidence_basis: str
    status: SourceDiscoveryReviewClaimCandidateStatus
    confidence_score: float = 0.5
    confidence_basis: list[str] = Field(default_factory=list)
    created_at: str
    applied_at: str | None = None
    caveats: list[str] = Field(default_factory=list)


class SourceDiscoveryReviewClaimImportRequest(CamelModel):
    review_id: str
    source_id: str | None = None
    imported_by: str
    caveats: list[str] = Field(default_factory=list)


class SourceDiscoveryReviewClaimImportResponse(CamelModel):
    memory: SourceDiscoveryMemory
    claims: list[SourceDiscoveryReviewClaimCandidateSummary] = Field(default_factory=list)
    wave_fits: list[SourceDiscoveryWaveFit] = Field(default_factory=list)
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
