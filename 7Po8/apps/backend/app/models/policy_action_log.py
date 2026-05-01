from datetime import datetime
from typing import Any

from sqlalchemy import JSON, Column, Index, String
from sqlmodel import Field, SQLModel

from app.models.common import SourceLifecycleState, SourceTrustTier
from app.models.wave import utc_now


class PolicyActionLog(SQLModel, table=True):
    __table_args__ = (
        Index("ix_policy_action_log_wave_created", "wave_id", "created_at"),
        Index("ix_policy_action_log_source_created", "discovered_source_id", "created_at"),
    )

    id: int | None = Field(default=None, primary_key=True)
    wave_id: int = Field(foreign_key="wave.id", index=True)
    discovered_source_id: int = Field(foreign_key="discoveredsource.id", index=True)
    domain: str | None = Field(default=None, max_length=255, index=True)
    action_type: str = Field(min_length=1, max_length=80, index=True)
    previous_status: SourceLifecycleState = Field(
        sa_column=Column(String(length=16), nullable=False, index=True)
    )
    new_status: SourceLifecycleState = Field(
        sa_column=Column(String(length=16), nullable=False, index=True)
    )
    previous_lifecycle_state: SourceLifecycleState = Field(
        sa_column=Column(String(length=9), nullable=False, index=True)
    )
    new_lifecycle_state: SourceLifecycleState = Field(
        sa_column=Column(String(length=9), nullable=False, index=True)
    )
    previous_trust_tier: SourceTrustTier = Field(
        sa_column=Column(String(length=6), nullable=False, index=True)
    )
    new_trust_tier: SourceTrustTier = Field(
        sa_column=Column(String(length=6), nullable=False, index=True)
    )
    previous_policy_context: dict[str, Any] | None = Field(default=None, sa_column=Column(JSON))
    new_policy_context: dict[str, Any] | None = Field(default=None, sa_column=Column(JSON))
    reason: str = Field(min_length=1, max_length=2000)
    triggered_by: str = Field(min_length=1, max_length=80, index=True)
    created_at: datetime = Field(default_factory=utc_now, nullable=False, index=True)
