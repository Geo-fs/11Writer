from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, Column, Index
from sqlmodel import Field, Relationship, SQLModel

from app.models.wave import utc_now

if TYPE_CHECKING:
    from app.models.record import Record
    from app.models.run_history import RunHistory
    from app.models.signal import Signal
    from app.models.wave import Wave


class Connector(SQLModel, table=True):
    __table_args__ = (Index("ix_connector_wave_enabled", "wave_id", "enabled"),)

    id: int | None = Field(default=None, primary_key=True)
    wave_id: int = Field(foreign_key="wave.id", index=True)
    type: str = Field(index=True, min_length=1, max_length=100)
    name: str = Field(min_length=1, max_length=200)
    enabled: bool = Field(default=True, index=True)
    config_json: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    polling_interval_minutes: int = Field(default=60, ge=1, le=1440)
    created_at: datetime = Field(default_factory=utc_now, nullable=False)
    updated_at: datetime = Field(default_factory=utc_now, nullable=False)
    last_run_at: datetime | None = Field(default=None, index=True)
    last_success_at: datetime | None = Field(default=None, index=True)
    last_error_at: datetime | None = Field(default=None, index=True)
    last_error_message: str | None = Field(default=None, max_length=2000)
    next_run_at: datetime | None = Field(default=None, index=True)

    wave: "Wave" = Relationship(back_populates="connectors")
    records: list["Record"] = Relationship(back_populates="connector")
    run_history: list["RunHistory"] = Relationship(back_populates="connector")
    signals: list["Signal"] = Relationship(back_populates="connector")
