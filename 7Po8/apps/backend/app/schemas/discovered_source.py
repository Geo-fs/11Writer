from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from app.models.common import (
    DomainApprovalPolicy,
    DomainTrustLevel,
    PolicyResolutionSource,
    SourceCheckStatus,
    SourceLifecycleState,
    SourcePolicyState,
    SourceTrustTier,
)


class DiscoveredSourceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    wave_id: int | None
    url: str
    title: str
    source_type: str
    parent_domain: str | None
    status: SourceLifecycleState
    trust_tier: SourceTrustTier
    discovery_method: str
    relevance_score: float
    stability_score: float | None
    free_access: bool | None
    suggested_connector_type: str | None
    description_summary: str | None
    metadata_json: dict[str, Any] | None
    discovered_at: datetime
    last_checked_at: datetime | None
    last_success_at: datetime | None
    failure_count: int
    consecutive_failures: int
    last_http_status: int | None
    last_content_type: str | None
    auto_check_enabled: bool
    check_interval_minutes: int
    next_check_at: datetime | None
    degradation_reason: str | None
    sandbox_progress: dict[str, Any] | None
    domain_trust_level: DomainTrustLevel
    domain_approval_policy: DomainApprovalPolicy
    policy_state: SourcePolicyState
    policy_reason: str
    approval_origin: str | None
    policy_source: PolicyResolutionSource
    wave_trust_override_id: int | None
    global_domain_trust_profile_id: int | None


class SourceCheckRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    discovered_source_id: int
    checked_at: datetime
    status: SourceCheckStatus
    http_status: int | None
    content_type: str | None
    latency_ms: int | None
    reachable: bool
    parseable: bool
    metadata_json: dict[str, Any] | None


class DiscoverSourcesRequest(BaseModel):
    seed_urls: list[HttpUrl] = Field(default_factory=list, max_length=20)


class DiscoverSourcesResponse(BaseModel):
    wave_id: int
    discovered_count: int
    deduped_count: int


class DiscoveredSourceUpdate(BaseModel):
    status: SourceLifecycleState | None = None
    relevance_score: float | None = Field(default=None, ge=0.0, le=1.0)
    suggested_connector_type: str | None = Field(default=None, max_length=80)
    title: str | None = Field(default=None, max_length=300)
    description_summary: str | None = Field(default=None, max_length=2000)
    auto_check_enabled: bool | None = None
    check_interval_minutes: int | None = Field(default=None, ge=5, le=1440)


class ApproveSourceResponse(BaseModel):
    source_id: int
    status: SourceLifecycleState
    connector_id: int | None = None


class BatchSourceCheckResponse(BaseModel):
    wave_id: int
    checked_count: int
    success_count: int
    failed_count: int
    skipped_count: int
