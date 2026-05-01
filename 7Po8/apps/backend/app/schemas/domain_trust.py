from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.common import DomainApprovalPolicy, DomainTrustLevel


class DomainTrustProfileRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    domain: str
    trust_level: DomainTrustLevel
    approval_policy: DomainApprovalPolicy
    notes: str | None
    created_at: datetime
    updated_at: datetime
    source_count: int
    approved_source_count: int
    blocked_source_count: int
    average_stability_score: float | None
    last_seen_at: datetime | None


class DomainTrustProfileCreate(BaseModel):
    domain: str = Field(min_length=1, max_length=255)
    trust_level: DomainTrustLevel = DomainTrustLevel.NEUTRAL
    approval_policy: DomainApprovalPolicy = DomainApprovalPolicy.MANUAL_REVIEW
    notes: str | None = Field(default=None, max_length=2000)


class DomainTrustProfileUpdate(BaseModel):
    trust_level: DomainTrustLevel | None = None
    approval_policy: DomainApprovalPolicy | None = None
    notes: str | None = Field(default=None, max_length=2000)


class DomainPolicyReevaluationResponse(BaseModel):
    profile_id: int
    domain: str
    evaluated_count: int
    changed_count: int
    auto_approved_count: int
    blocked_count: int
    reviewable_count: int
    preserved_count: int
