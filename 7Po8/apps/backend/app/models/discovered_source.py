from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, Column, Index, String
from sqlmodel import Field, Relationship, SQLModel

from app.models.common import SourceLifecycleState, SourceTrustTier
from app.models.wave import utc_now

if TYPE_CHECKING:
    from app.models.policy_action_log import PolicyActionLog
    from app.models.source_check import SourceCheck
    from app.models.wave import Wave


class DiscoveredSource(SQLModel, table=True):
    __table_args__ = (
        Index("ix_discovered_source_wave_status", "wave_id", "status"),
        Index("ix_discovered_source_wave_relevance", "wave_id", "relevance_score"),
        Index("ix_discovered_source_wave_stability", "wave_id", "stability_score"),
        Index("ix_discovered_source_wave_source_type", "wave_id", "source_type"),
        Index("ix_discovered_source_wave_url_unique", "wave_id", "url", unique=True),
        Index("ix_discovered_source_parent_domain", "parent_domain"),
    )

    id: int | None = Field(default=None, primary_key=True)
    wave_id: int | None = Field(default=None, foreign_key="wave.id", index=True)
    url: str = Field(min_length=1, max_length=2000)
    title: str = Field(default="", max_length=300)
    source_type: str = Field(default="unknown", max_length=80, index=True)
    parent_domain: str | None = Field(default=None, max_length=255, index=True)
    status: SourceLifecycleState = Field(
        default=SourceLifecycleState.CANDIDATE,
        sa_column=Column(String(length=16), nullable=False, index=True),
    )
    trust_tier: SourceTrustTier = Field(
        default=SourceTrustTier.TIER_4,
        sa_column=Column(String(length=6), nullable=False, index=True),
    )
    discovery_method: str = Field(default="heuristic", max_length=120)
    relevance_score: float = Field(default=0.0, ge=0.0, le=1.0, index=True)
    stability_score: float | None = Field(default=None, ge=0.0, le=1.0)
    free_access: bool | None = Field(default=None, index=True)
    suggested_connector_type: str | None = Field(default=None, max_length=80)
    description_summary: str | None = Field(default=None, max_length=2000)
    metadata_json: dict[str, Any] | None = Field(default=None, sa_column=Column(JSON))
    discovered_at: datetime = Field(default_factory=utc_now, nullable=False, index=True)
    last_checked_at: datetime | None = Field(default=None, index=True)
    last_success_at: datetime | None = Field(default=None, index=True)
    failure_count: int = Field(default=0, ge=0, index=True)
    consecutive_failures: int = Field(default=0, ge=0, index=True)
    last_http_status: int | None = Field(default=None, ge=100, le=599, index=True)
    last_content_type: str | None = Field(default=None, max_length=200, index=True)
    auto_check_enabled: bool = Field(default=True, index=True)
    check_interval_minutes: int = Field(default=60, ge=5, le=1440)
    next_check_at: datetime | None = Field(default=None, index=True)
    degradation_reason: str | None = Field(default=None, max_length=500)

    wave: "Wave" = Relationship(back_populates="discovered_sources")
    checks: list["SourceCheck"] = Relationship(
        back_populates="discovered_source",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    policy_actions: list["PolicyActionLog"] = Relationship(
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
