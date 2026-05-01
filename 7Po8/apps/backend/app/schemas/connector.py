from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ConnectorCreate(BaseModel):
    type: str = Field(min_length=1, max_length=100)
    name: str = Field(min_length=1, max_length=200)
    enabled: bool = True
    config_json: dict[str, Any] = Field(default_factory=dict)
    polling_interval_minutes: int = Field(default=60, ge=1, le=1440)


class ConnectorUpdate(BaseModel):
    type: str | None = Field(default=None, min_length=1, max_length=100)
    name: str | None = Field(default=None, min_length=1, max_length=200)
    enabled: bool | None = None
    config_json: dict[str, Any] | None = None
    polling_interval_minutes: int | None = Field(default=None, ge=1, le=1440)


class ConnectorRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    wave_id: int
    type: str
    name: str
    enabled: bool
    config_json: dict[str, Any]
    polling_interval_minutes: int
    created_at: datetime
    updated_at: datetime
    last_run_at: datetime | None
    last_success_at: datetime | None
    last_error_at: datetime | None
    last_error_message: str | None
    next_run_at: datetime | None
