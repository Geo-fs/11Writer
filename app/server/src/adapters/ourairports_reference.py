from __future__ import annotations

import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import httpx

from src.adapters.base import Adapter
from src.config.settings import Settings
from src.reference.ingest.parsers.ourairports import parse_ourairports_dataset
from src.reference.schemas import ReferenceRecord


OurAirportsReferenceSourceMode = Literal["fixture", "live", "unknown"]


@dataclass(frozen=True)
class OurAirportsReferenceFetchResult:
    records: list[ReferenceRecord]
    source_mode: OurAirportsReferenceSourceMode
    airports_source_url: str
    runways_source_url: str
    last_updated_at: str | None
    caveats: list[str]


class OurAirportsReferenceUpstreamError(RuntimeError):
    pass


class OurAirportsReferenceAdapter(Adapter[OurAirportsReferenceFetchResult]):
    source_name = "ourairports-reference"

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def fetch(self) -> OurAirportsReferenceFetchResult:
        with tempfile.TemporaryDirectory(prefix="ourairports-reference-") as temp_dir:
            source_dir = Path(temp_dir)
            async with httpx.AsyncClient(
                timeout=self._settings.ourairports_reference_http_timeout_seconds,
                headers={"User-Agent": "11Writer-Aerospace/0.1"},
            ) as client:
                airports_response = await client.get(self._settings.ourairports_reference_airports_url)
                runways_response = await client.get(self._settings.ourairports_reference_runways_url)
            if airports_response.status_code >= 400:
                raise OurAirportsReferenceUpstreamError(
                    f"OurAirports airports CSV returned HTTP {airports_response.status_code}."
                )
            if runways_response.status_code >= 400:
                raise OurAirportsReferenceUpstreamError(
                    f"OurAirports runways CSV returned HTTP {runways_response.status_code}."
                )
            (source_dir / "airports.csv").write_text(airports_response.text, encoding="utf-8")
            (source_dir / "runways.csv").write_text(runways_response.text, encoding="utf-8")
            records = parse_ourairports_dataset(source_dir, "live")
        return OurAirportsReferenceFetchResult(
            records=records,
            source_mode="live",
            airports_source_url=self._settings.ourairports_reference_airports_url,
            runways_source_url=self._settings.ourairports_reference_runways_url,
            last_updated_at=None,
            caveats=_base_caveats(),
        )

    def load_fixture(self) -> OurAirportsReferenceFetchResult:
        fixture_path = Path(self._settings.ourairports_reference_fixture_path)
        if not fixture_path.is_absolute():
            fixture_path = Path(__file__).resolve().parents[2] / fixture_path
        records = parse_ourairports_dataset(fixture_path, "fixture")
        return OurAirportsReferenceFetchResult(
            records=records,
            source_mode=self._source_mode_label(),
            airports_source_url=self._settings.ourairports_reference_airports_url,
            runways_source_url=self._settings.ourairports_reference_runways_url,
            last_updated_at=None,
            caveats=_base_caveats(),
        )

    def _source_mode_label(self) -> OurAirportsReferenceSourceMode:
        mode = self._settings.ourairports_reference_source_mode.strip().lower()
        if mode == "fixture":
            return "fixture"
        if mode == "live":
            return "live"
        return "unknown"


def _base_caveats() -> list[str]:
    return [
        "OurAirports reference data is public baseline facility metadata, not live airport status or operational availability.",
        "Reference coordinates and runway geometry are source-provided baseline fields and should not be treated as survey-grade precision.",
        "Reference enrichment must remain separate from live aircraft or satellite evidence and must not replace selected-target source truth.",
    ]
