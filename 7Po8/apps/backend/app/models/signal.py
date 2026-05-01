from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, Column, Index
from sqlmodel import Field, Relationship, SQLModel

from app.models.common import SignalSeverity, SignalStatus
from app.models.wave import utc_now

if TYPE_CHECKING:
    from app.models.connector import Connector
    from app.models.wave import Wave


class Signal(SQLModel, table=True):
    __table_args__ = (
        Index("ix_signal_wave_created_at", "wave_id", "created_at"),
        Index("ix_signal_connector_created_at", "connector_id", "created_at"),
        Index("ix_signal_wave_status", "wave_id", "status"),
        Index("ix_signal_wave_severity", "wave_id", "severity"),
        Index("ix_signal_wave_type", "wave_id", "type"),
        Index("ix_signal_dedupe_key", "dedupe_key"),
    )

    id: int | None = Field(default=None, primary_key=True)
    wave_id: int = Field(foreign_key="wave.id", index=True)
    connector_id: int | None = Field(default=None, foreign_key="connector.id", index=True)
    type: str = Field(min_length=1, max_length=100, index=True)
    severity: SignalSeverity = Field(default=SignalSeverity.LOW, index=True)
    title: str = Field(min_length=1, max_length=300)
    summary: str = Field(default="", max_length=2000)
    status: SignalStatus = Field(default=SignalStatus.NEW, index=True)
    created_at: datetime = Field(default_factory=utc_now, nullable=False, index=True)
    metadata_json: dict[str, Any] | None = Field(default=None, sa_column=Column(JSON))
    dedupe_key: str | None = Field(default=None, max_length=300)

    wave: "Wave" = Relationship(back_populates="signals")
    connector: "Connector" = Relationship(back_populates="signals")
