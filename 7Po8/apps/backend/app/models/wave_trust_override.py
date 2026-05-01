from datetime import datetime

from sqlalchemy import Index
from sqlmodel import Field, SQLModel

from app.models.common import DomainApprovalPolicy, DomainTrustLevel
from app.models.wave import utc_now


class WaveDomainTrustOverride(SQLModel, table=True):
    __table_args__ = (
        Index("ix_wave_trust_override_wave_domain_unique", "wave_id", "domain", unique=True),
        Index("ix_wave_trust_override_wave_updated", "wave_id", "updated_at"),
    )

    id: int | None = Field(default=None, primary_key=True)
    wave_id: int = Field(foreign_key="wave.id", index=True)
    domain: str = Field(min_length=1, max_length=255, index=True)
    trust_level: DomainTrustLevel | None = Field(default=None, index=True)
    approval_policy: DomainApprovalPolicy | None = Field(default=None, index=True)
    notes: str | None = Field(default=None, max_length=2000)
    created_at: datetime = Field(default_factory=utc_now, nullable=False)
    updated_at: datetime = Field(default_factory=utc_now, nullable=False, index=True)
