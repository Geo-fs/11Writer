from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, Column, Index
from sqlmodel import Field, Relationship, SQLModel

from app.models.wave import utc_now

if TYPE_CHECKING:
    from app.models.connector import Connector
    from app.models.wave import Wave


class Record(SQLModel, table=True):
    __table_args__ = (
        Index("ix_record_wave_collected_at", "wave_id", "collected_at"),
        Index("ix_record_connector_collected_at", "connector_id", "collected_at"),
        Index("ix_record_wave_source_type_collected", "wave_id", "source_type", "collected_at"),
        Index("ux_record_connector_external_id", "connector_id", "external_id", unique=True),
    )

    id: int | None = Field(default=None, primary_key=True)
    wave_id: int = Field(foreign_key="wave.id", index=True)
    connector_id: int | None = Field(default=None, foreign_key="connector.id", index=True)
    external_id: str | None = Field(default=None, max_length=512, index=True)
    title: str = Field(min_length=1, max_length=300)
    content: str = Field(default="", max_length=10000)
    source_type: str = Field(min_length=1, max_length=100)
    source_name: str = Field(min_length=1, max_length=200)
    source_url: str | None = Field(default=None, max_length=1000)
    collected_at: datetime = Field(default_factory=utc_now, nullable=False, index=True)
    event_time: datetime | None = Field(default=None, index=True)
    latitude: float | None = Field(default=None)
    longitude: float | None = Field(default=None)
    tags_json: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    raw_payload_json: dict[str, Any] | None = Field(default=None, sa_column=Column(JSON))

    wave: "Wave" = Relationship(back_populates="records")
    connector: "Connector" = Relationship(back_populates="records")
