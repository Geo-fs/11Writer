from __future__ import annotations

from datetime import datetime, timedelta, timezone
from hashlib import sha256
from typing import Annotated, Any

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    ValidationError,
)

from app.connectors.base import CollectedRecord, ConnectorConfigError

Keyword = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=64)]


class SampleNewsConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    keywords: list[Keyword] = Field(default_factory=list, max_length=10)


class SampleNewsConnector:
    type_name = "sample_news"

    def validate_config(self, config: dict[str, Any]) -> dict[str, Any]:
        try:
            parsed = SampleNewsConfig.model_validate(config)
            return parsed.model_dump()
        except ValidationError as exc:
            first_error = exc.errors()[0]
            location = ".".join(str(part) for part in first_error.get("loc", [])) or "config_json"
            message = first_error.get("msg", "Invalid connector config")
            raise ConnectorConfigError(
                f"Invalid config for '{self.type_name}' at '{location}': {message}"
            ) from exc

    def collect(
        self,
        wave_name: str,
        focus_type: str,
        config: dict[str, Any],
    ) -> list[CollectedRecord]:
        normalized_config = self.validate_config(config)
        keywords = normalized_config.get("keywords", [])
        if not keywords:
            keywords = [focus_type, "local-monitoring"]
        if isinstance(keywords, str):
            keywords = [keywords]

        now = datetime.now(timezone.utc)
        records: list[CollectedRecord] = []
        for index, keyword in enumerate(keywords[:3], start=1):
            digest = sha256(f"{wave_name}:{keyword}".encode()).hexdigest()
            score = int(digest[:6], 16) % 100
            records.append(
                CollectedRecord(
                    external_id=f"sample-news:{digest}",
                    title=f"{wave_name} signal for '{keyword}'",
                    content=f"Deterministic sample item #{index} with relevance score {score}.",
                    source_type="sample_news",
                    source_name="7Po8 Sample Feed",
                    source_url=f"https://example.local/{keyword}",
                    collected_at=now,
                    event_time=now - timedelta(minutes=index * 5),
                    latitude=None,
                    longitude=None,
                    tags_json=[keyword, "sample", "deterministic"],
                    raw_payload_json={"score": score, "keyword": keyword, "wave": wave_name},
                )
            )
        return records
