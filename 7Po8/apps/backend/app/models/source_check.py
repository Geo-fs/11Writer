from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, Column, Index
from sqlmodel import Field, Relationship, SQLModel

from app.models.common import SourceCheckStatus
from app.models.wave import utc_now

if TYPE_CHECKING:
    from app.models.discovered_source import DiscoveredSource


class SourceCheck(SQLModel, table=True):
    __table_args__ = (
        Index("ix_source_check_source_checked_at", "discovered_source_id", "checked_at"),
        Index("ix_source_check_source_status", "discovered_source_id", "status"),
        Index(
            "ix_source_check_source_reach_parse",
            "discovered_source_id",
            "reachable",
            "parseable",
        ),
    )

    id: int | None = Field(default=None, primary_key=True)
    discovered_source_id: int = Field(foreign_key="discoveredsource.id", index=True)
    checked_at: datetime = Field(default_factory=utc_now, nullable=False, index=True)
    status: SourceCheckStatus = Field(default=SourceCheckStatus.SKIPPED, index=True)
    http_status: int | None = Field(default=None, ge=100, le=599)
    content_type: str | None = Field(default=None, max_length=200)
    latency_ms: int | None = Field(default=None, ge=0)
    reachable: bool = Field(default=False, index=True)
    parseable: bool = Field(default=False, index=True)
    metadata_json: dict[str, Any] | None = Field(default=None, sa_column=Column(JSON))

    discovered_source: "DiscoveredSource" = Relationship(back_populates="checks")
