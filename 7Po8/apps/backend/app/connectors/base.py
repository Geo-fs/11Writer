from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Protocol


class ConnectorConfigError(ValueError):
    """Raised when connector type or connector config is invalid."""


@dataclass
class CollectedRecord:
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


class ConnectorRunner(Protocol):
    type_name: str

    def validate_config(self, config: dict[str, Any]) -> dict[str, Any]:
        ...

    def collect(
        self,
        wave_name: str,
        focus_type: str,
        config: dict[str, Any],
    ) -> list[CollectedRecord]:
        ...
