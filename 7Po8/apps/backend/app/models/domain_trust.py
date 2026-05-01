from datetime import datetime

from sqlalchemy import Index
from sqlmodel import Field, SQLModel

from app.models.common import DomainApprovalPolicy, DomainTrustLevel
from app.models.wave import utc_now


class DomainTrustProfile(SQLModel, table=True):
    __table_args__ = (
        Index("ix_domain_trust_domain_unique", "domain", unique=True),
        Index("ix_domain_trust_level_policy", "trust_level", "approval_policy"),
    )

    id: int | None = Field(default=None, primary_key=True)
    domain: str = Field(min_length=1, max_length=255, index=True)
    trust_level: DomainTrustLevel = Field(default=DomainTrustLevel.NEUTRAL, index=True)
    approval_policy: DomainApprovalPolicy = Field(
        default=DomainApprovalPolicy.MANUAL_REVIEW,
        index=True,
    )
    notes: str | None = Field(default=None, max_length=2000)
    created_at: datetime = Field(default_factory=utc_now, nullable=False)
    updated_at: datetime = Field(default_factory=utc_now, nullable=False, index=True)
