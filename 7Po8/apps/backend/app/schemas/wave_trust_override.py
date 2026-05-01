from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.common import DomainApprovalPolicy, DomainTrustLevel


class WaveDomainTrustOverrideRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    wave_id: int
    domain: str
    trust_level: DomainTrustLevel | None
    approval_policy: DomainApprovalPolicy | None
    notes: str | None
    created_at: datetime
    updated_at: datetime
    source_count: int
    approved_source_count: int
    rejected_source_count: int


class WaveDomainTrustOverrideCreate(BaseModel):
    domain: str = Field(min_length=1, max_length=255)
    trust_level: DomainTrustLevel | None = None
    approval_policy: DomainApprovalPolicy | None = None
    notes: str | None = Field(default=None, max_length=2000)

    @model_validator(mode="after")
    def validate_override_fields(self) -> "WaveDomainTrustOverrideCreate":
        if self.trust_level is None and self.approval_policy is None:
            raise ValueError("At least one override field must be provided.")
        return self


class WaveDomainTrustOverrideUpdate(BaseModel):
    trust_level: DomainTrustLevel | None = None
    approval_policy: DomainApprovalPolicy | None = None
    notes: str | None = Field(default=None, max_length=2000)
