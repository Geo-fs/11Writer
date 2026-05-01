from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.models.common import SignalSeverity, SignalStatus


class SignalRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    wave_id: int
    connector_id: int | None
    type: str
    severity: SignalSeverity
    title: str
    summary: str
    status: SignalStatus
    created_at: datetime
    metadata_json: dict[str, Any] | None


class SignalUpdate(BaseModel):
    status: SignalStatus | None = None
    severity: SignalSeverity | None = None
    title: str | None = Field(default=None, min_length=1, max_length=300)
    summary: str | None = Field(default=None, max_length=2000)
