from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.common import FocusType, WaveStatus


class WaveCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=2000)
    status: WaveStatus = WaveStatus.ACTIVE
    focus_type: FocusType = FocusType.MIXED


class WaveUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    status: WaveStatus | None = None
    focus_type: FocusType | None = None


class WaveRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str
    status: WaveStatus
    focus_type: FocusType
    created_at: datetime
    updated_at: datetime
    last_run_at: datetime | None
    last_success_at: datetime | None
    last_error_at: datetime | None
    last_error_message: str | None
    connector_count: int = 0
    record_count: int = 0
