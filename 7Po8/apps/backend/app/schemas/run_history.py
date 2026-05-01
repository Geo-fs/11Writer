from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.common import RunStatus


class RunHistoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    wave_id: int
    connector_id: int
    connector_name: str | None = None
    started_at: datetime
    finished_at: datetime | None
    status: RunStatus
    records_created: int
    error_message: str | None
