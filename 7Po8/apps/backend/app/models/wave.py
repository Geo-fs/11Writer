from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from app.models.common import FocusType, WaveStatus

if TYPE_CHECKING:
    from app.models.connector import Connector
    from app.models.discovered_source import DiscoveredSource
    from app.models.policy_action_log import PolicyActionLog
    from app.models.record import Record
    from app.models.run_history import RunHistory
    from app.models.signal import Signal
    from app.models.wave_trust_override import WaveDomainTrustOverride


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Wave(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, min_length=1, max_length=200)
    description: str = Field(default="", max_length=2000)
    status: WaveStatus = Field(default=WaveStatus.ACTIVE, index=True)
    focus_type: FocusType = Field(default=FocusType.MIXED, index=True)
    created_at: datetime = Field(default_factory=utc_now, nullable=False)
    updated_at: datetime = Field(default_factory=utc_now, nullable=False)
    last_run_at: datetime | None = Field(default=None, index=True)
    last_success_at: datetime | None = Field(default=None, index=True)
    last_error_at: datetime | None = Field(default=None, index=True)
    last_error_message: str | None = Field(default=None, max_length=2000)

    connectors: list["Connector"] = Relationship(
        back_populates="wave",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    records: list["Record"] = Relationship(
        back_populates="wave",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    run_history: list["RunHistory"] = Relationship(
        back_populates="wave",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    signals: list["Signal"] = Relationship(
        back_populates="wave",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    discovered_sources: list["DiscoveredSource"] = Relationship(
        back_populates="wave",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    trust_overrides: list["WaveDomainTrustOverride"] = Relationship(
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    policy_actions: list["PolicyActionLog"] = Relationship(
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
