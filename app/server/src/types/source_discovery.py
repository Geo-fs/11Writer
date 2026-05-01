from __future__ import annotations

from typing import Literal

from pydantic import Field

from src.types.api import CamelModel


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
    parent_domain: str
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
    caveats: list[str] = Field(default_factory=list)


class SourceDiscoveryClaimOutcomeResponse(CamelModel):
    memory: SourceDiscoveryMemory
    wave_fits: list[SourceDiscoveryWaveFit] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)
