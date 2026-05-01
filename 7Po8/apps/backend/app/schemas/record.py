from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class RecordRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    wave_id: int
    connector_id: int | None
    external_id: str | None
    title: str
    content: str
    source_type: str
    source_name: str
    source_url: str | None
    collected_at: datetime
    event_time: datetime | None
    latitude: float | None
    longitude: float | None
    tags_json: list[str]
    raw_payload_json: dict[str, Any] | None
