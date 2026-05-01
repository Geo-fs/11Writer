from datetime import datetime
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from app.models.common import RunStatus
from app.models.wave import utc_now

if TYPE_CHECKING:
    from app.models.connector import Connector
    from app.models.wave import Wave


class RunHistory(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    wave_id: int = Field(foreign_key="wave.id", index=True)
    connector_id: int = Field(foreign_key="connector.id", index=True)
    started_at: datetime = Field(default_factory=utc_now, nullable=False, index=True)
    finished_at: datetime | None = Field(default=None, index=True)
    status: RunStatus = Field(default=RunStatus.RUNNING, index=True)
    records_created: int = Field(default=0, ge=0)
    error_message: str | None = Field(default=None, max_length=2000)

    wave: "Wave" = Relationship(back_populates="run_history")
    connector: "Connector" = Relationship(back_populates="run_history")
