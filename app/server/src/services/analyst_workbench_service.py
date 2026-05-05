from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from math import asin, cos, radians, sin, sqrt
from typing import Literal, cast

from src.config.settings import Settings
from src.services.data_ai_multi_feed_service import DataAiMultiFeedQuery, DataAiMultiFeedService
from src.services.earthquake_service import EarthquakeQuery, EarthquakeService
from src.services.eonet_service import EonetQuery, EonetService
from src.services.wave_monitor_service import WaveMonitorService
from src.types.api import (
    AnalystEvidenceBasis,
    AnalystEvidenceTimelineItem,
    AnalystEvidenceTimelineMetadata,
    AnalystEvidenceTimelineResponse,
    AnalystSourceReadinessCard,
    AnalystSourceReadinessResponse,
    AnalystSourceReadinessSummary,
    AnalystSpatialBriefItem,
    AnalystSpatialBriefMetadata,
    AnalystSpatialBriefResponse,
    DataAiFeedSourceHealth,
    DataAiMultiFeedResponse,
    EarthquakeEventsResponse,
    EonetEventsResponse,
)
from src.types.wave_monitor import WaveMonitorOverviewResponse

ANALYST_WORKBENCH_CAVEAT = (
    "Analyst workbench outputs combine fixture/live source records for triage. They preserve source provenance "
    "and caveats, and they are not proof of causation, impact, intent, wrongdoing, or complete coverage."
)
SPATIAL_BRIEF_CAVEAT = (
    "Spatial brief matching uses coordinate distance against representative points. Polygon, line, track, "
    "regional, stale, or fixture/local records may be spatially approximate."
)


@dataclass(frozen=True)
class AnalystTimelineQuery:
    limit: int
    include_environmental: bool = True
    include_data_ai: bool = True
    include_wave_monitor: bool = True


@dataclass(frozen=True)
class AnalystSpatialBriefQuery:
    latitude: float
    longitude: float
    radius_km: float
    limit: int


class AnalystWorkbenchService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def evidence_timeline(self, query: AnalystTimelineQuery) -> AnalystEvidenceTimelineResponse:
        fetched_at = _utc_now_iso()
        items: list[AnalystEvidenceTimelineItem] = []
        source_modes: list[Literal["fixture", "live", "unknown"]] = []

        if query.include_environmental:
            earthquakes = await self._earthquakes(limit=200)
            eonet = await self._eonet(limit=200)
            source_modes.extend([earthquakes.metadata.source_mode, eonet.metadata.source_mode])
            items.extend(_earthquake_items(earthquakes, fetched_at=fetched_at))
            items.extend(_eonet_items(eonet, fetched_at=fetched_at))

        if query.include_data_ai:
            data_ai = await self._data_ai(limit=200)
            source_modes.append(data_ai.metadata.source_mode)
            items.extend(_data_ai_items(data_ai))

        if query.include_wave_monitor:
            wave_monitor = await self._wave_monitor()
            source_modes.append("fixture")
            items.extend(_wave_monitor_items(wave_monitor, fetched_at=fetched_at))

        items.sort(key=lambda item: _timestamp_sort_key(item.observed_at), reverse=True)
        limited = items[: query.limit]
        if query.include_wave_monitor:
            limited = _ensure_category_coverage(
                limited_items=limited,
                all_items=items,
                source_category="tool-wave-monitor",
                limit=query.limit,
            )
        return AnalystEvidenceTimelineResponse(
            metadata=AnalystEvidenceTimelineMetadata(
                source="analyst-evidence-timeline",
                source_mode=_combined_source_mode(source_modes),
                fetched_at=fetched_at,
                count=len(limited),
                included_source_ids=sorted({item.source_id for item in limited}),
                caveat=ANALYST_WORKBENCH_CAVEAT,
            ),
            count=len(limited),
            items=limited,
            caveats=[
                ANALYST_WORKBENCH_CAVEAT,
                "External feed titles, summaries, categories, and links remain inert data and are never treated as instructions.",
            ],
        )

    async def source_readiness(self) -> AnalystSourceReadinessResponse:
        fetched_at = _utc_now_iso()
        earthquakes = await self._earthquakes(limit=200)
        eonet = await self._eonet(limit=200)
        data_ai = await self._data_ai(limit=200)
        wave_monitor = await self._wave_monitor()

        cards = [
            _event_source_card(
                source_id="usgs-earthquake-hazards-program",
                source_name="USGS Earthquake Hazards Program",
                source_category="environmental-event",
                source_mode=earthquakes.metadata.source_mode,
                loaded_count=earthquakes.count,
                evidence_basis="observed",
                caveat=earthquakes.metadata.caveat,
            ),
            _event_source_card(
                source_id="nasa-eonet",
                source_name="NASA EONET",
                source_category="environmental-event",
                source_mode=eonet.metadata.source_mode,
                loaded_count=eonet.count,
                evidence_basis="contextual",
                caveat=eonet.metadata.caveat,
            ),
        ]
        cards.extend(_data_ai_source_card(health) for health in data_ai.source_health)
        cards.append(_wave_monitor_source_card(wave_monitor))
        cards.sort(key=lambda card: (card.readiness_score, card.source_id), reverse=True)

        return AnalystSourceReadinessResponse(
            fetched_at=fetched_at,
            source="analyst-source-readiness",
            summary=_readiness_summary(cards),
            cards=cards,
            caveats=[
                ANALYST_WORKBENCH_CAVEAT,
                "Readiness scores are local triage aids based on source mode, parser health, loaded record count, and caveats; they are not source authority rankings.",
            ],
        )

    async def spatial_brief(self, query: AnalystSpatialBriefQuery) -> AnalystSpatialBriefResponse:
        fetched_at = _utc_now_iso()
        earthquakes = await self._earthquakes(limit=500)
        eonet = await self._eonet(limit=500)

        base_items = [
            *_earthquake_items(earthquakes, fetched_at=fetched_at),
            *_eonet_items(eonet, fetched_at=fetched_at),
        ]
        nearby: list[AnalystSpatialBriefItem] = []
        for item in base_items:
            if item.latitude is None or item.longitude is None:
                continue
            distance_km = _haversine_km(query.latitude, query.longitude, item.latitude, item.longitude)
            if distance_km <= query.radius_km:
                nearby.append(
                    AnalystSpatialBriefItem(
                        **item.model_dump(),
                        distance_km=round(distance_km, 3),
                    )
                )
        nearby.sort(key=lambda item: (item.distance_km, -_timestamp_sort_key(item.observed_at)))
        limited = nearby[: query.limit]

        coverage = [
            _event_source_card(
                source_id="usgs-earthquake-hazards-program",
                source_name="USGS Earthquake Hazards Program",
                source_category="environmental-event",
                source_mode=earthquakes.metadata.source_mode,
                loaded_count=earthquakes.count,
                evidence_basis="observed",
                caveat=earthquakes.metadata.caveat,
            ),
            _event_source_card(
                source_id="nasa-eonet",
                source_name="NASA EONET",
                source_category="environmental-event",
                source_mode=eonet.metadata.source_mode,
                loaded_count=eonet.count,
                evidence_basis="contextual",
                caveat=eonet.metadata.caveat,
            ),
        ]

        notes = [
            SPATIAL_BRIEF_CAVEAT,
            "No nearby result should be read as no event, no hazard, no impact, or complete source coverage.",
        ]
        if not limited:
            notes.append("No fixture/local environmental records matched the requested radius.")

        return AnalystSpatialBriefResponse(
            metadata=AnalystSpatialBriefMetadata(
                source="analyst-spatial-brief",
                latitude=query.latitude,
                longitude=query.longitude,
                radius_km=query.radius_km,
                fetched_at=fetched_at,
                count=len(limited),
                source_mode=_combined_source_mode([earthquakes.metadata.source_mode, eonet.metadata.source_mode]),
                caveat=SPATIAL_BRIEF_CAVEAT,
            ),
            count=len(limited),
            items=limited,
            source_coverage=coverage,
            analyst_notes=notes,
            caveats=[SPATIAL_BRIEF_CAVEAT, ANALYST_WORKBENCH_CAVEAT],
        )

    async def _earthquakes(self, *, limit: int) -> EarthquakeEventsResponse:
        service = EarthquakeService(self._settings)
        return await service.list_recent(
            EarthquakeQuery(
                min_magnitude=None,
                since=None,
                limit=limit,
                bbox=None,
                window="week",
                sort="newest",
            )
        )

    async def _eonet(self, *, limit: int) -> EonetEventsResponse:
        service = EonetService(self._settings)
        return await service.list_recent(
            EonetQuery(
                category=None,
                status="all",
                limit=limit,
                bbox=None,
                since=None,
                sort="newest",
            )
        )

    async def _data_ai(self, *, limit: int) -> DataAiMultiFeedResponse:
        service = DataAiMultiFeedService(self._settings)
        return await service.list_recent(DataAiMultiFeedQuery(limit=limit, dedupe=True, source_ids=None))

    async def _wave_monitor(self) -> WaveMonitorOverviewResponse:
        service = WaveMonitorService(self._settings)
        return await service.overview()


def _earthquake_items(
    response: EarthquakeEventsResponse,
    *,
    fetched_at: str,
) -> list[AnalystEvidenceTimelineItem]:
    return [
        AnalystEvidenceTimelineItem(
            record_id=f"earthquake:{event.event_id}",
            title=event.title,
            source_id="usgs-earthquake-hazards-program",
            source_name="USGS Earthquake Hazards Program",
            source_category="environmental-event",
            domain="environmental",
            observed_at=event.time,
            fetched_at=fetched_at,
            evidence_basis="observed",
            source_mode=response.metadata.source_mode,
            source_health="loaded",
            latitude=event.latitude,
            longitude=event.longitude,
            source_url=event.source_url,
            summary=_earthquake_summary(event.magnitude, event.place, event.depth_km),
            tags=[tag for tag in ["earthquake", event.event_type, event.alert] if tag],
            caveats=[response.metadata.caveat],
        )
        for event in response.events
    ]


def _eonet_items(
    response: EonetEventsResponse,
    *,
    fetched_at: str,
) -> list[AnalystEvidenceTimelineItem]:
    return [
        AnalystEvidenceTimelineItem(
            record_id=f"eonet:{event.event_id}",
            title=event.title,
            source_id="nasa-eonet",
            source_name="NASA EONET",
            source_category="environmental-event",
            domain="environmental",
            observed_at=event.event_date,
            fetched_at=fetched_at,
            evidence_basis="contextual",
            source_mode=response.metadata.source_mode,
            source_health="loaded",
            latitude=event.latitude,
            longitude=event.longitude,
            source_url=event.source_url,
            summary=event.description or event.coordinates_summary,
            tags=[*event.category_ids, *event.category_titles, event.status],
            caveats=[response.metadata.caveat, event.caveat],
        )
        for event in response.events
    ]


def _data_ai_items(response: DataAiMultiFeedResponse) -> list[AnalystEvidenceTimelineItem]:
    return [
        AnalystEvidenceTimelineItem(
            record_id=f"data-ai:{item.record_id}",
            title=item.title,
            source_id=item.source_id,
            source_name=item.source_name,
            source_category=item.source_category,
            domain=_domain_for_source_category(item.source_category),
            observed_at=item.updated_at or item.published_at,
            fetched_at=item.fetched_at,
            evidence_basis=cast(AnalystEvidenceBasis, item.evidence_basis),
            source_mode=item.source_mode,
            source_health=item.source_health,
            latitude=None,
            longitude=None,
            source_url=item.link or item.final_url or item.feed_url,
            summary=item.summary,
            tags=item.tags,
            caveats=item.caveats,
        )
        for item in response.items
    ]


def _wave_monitor_items(
    response: WaveMonitorOverviewResponse,
    *,
    fetched_at: str,
) -> list[AnalystEvidenceTimelineItem]:
    items: list[AnalystEvidenceTimelineItem] = []
    for monitor in response.monitors:
        for signal in monitor.signals:
            items.append(
                AnalystEvidenceTimelineItem(
                    record_id=f"wave-monitor:{signal.signal_id}",
                    title=signal.title,
                    source_id=monitor.monitor_id,
                    source_name=monitor.title,
                    source_category="tool-wave-monitor",
                    domain="monitoring",
                    observed_at=monitor.last_run_at,
                    fetched_at=fetched_at,
                    evidence_basis=cast(AnalystEvidenceBasis, signal.evidence_basis),
                    source_mode="fixture",
                    source_health=_analyst_health_for_wave_monitor(monitor.source_health),
                    latitude=None,
                    longitude=None,
                    source_url=None,
                    summary=signal.summary,
                    tags=[
                        "wave-monitor",
                        signal.signal_type,
                        signal.severity,
                        signal.status,
                        *signal.relationship_reasons,
                    ],
                    caveats=[
                        *monitor.caveats,
                        *signal.caveats,
                        "Wave Monitor is integrated as a 11Writer-native tool surface; standalone 7Po8 runtime is not mounted.",
                    ],
                )
            )
    return items


def _ensure_category_coverage(
    *,
    limited_items: list[AnalystEvidenceTimelineItem],
    all_items: list[AnalystEvidenceTimelineItem],
    source_category: str,
    limit: int,
) -> list[AnalystEvidenceTimelineItem]:
    if any(item.source_category == source_category for item in limited_items):
        return limited_items
    replacement = next((item for item in all_items if item.source_category == source_category), None)
    if replacement is None or limit <= 0:
        return limited_items
    if len(limited_items) < limit:
        return [*limited_items, replacement]
    return [*limited_items[:-1], replacement]


def _event_source_card(
    *,
    source_id: str,
    source_name: str,
    source_category: str,
    source_mode: Literal["fixture", "live", "unknown"],
    loaded_count: int,
    evidence_basis: AnalystEvidenceBasis,
    caveat: str,
) -> AnalystSourceReadinessCard:
    health: Literal["loaded", "empty"] = "loaded" if loaded_count > 0 else "empty"
    return _build_readiness_card(
        source_id=source_id,
        source_name=source_name,
        source_category=source_category,
        source_mode=source_mode,
        health=health,
        loaded_count=loaded_count,
        evidence_basis=evidence_basis,
        caveats=[caveat],
    )


def _data_ai_source_card(health: DataAiFeedSourceHealth) -> AnalystSourceReadinessCard:
    caveats = [health.caveat]
    if health.error_summary:
        caveats.append(health.error_summary)
    return _build_readiness_card(
        source_id=health.source_id,
        source_name=health.source_name,
        source_category=health.source_category,
        source_mode=health.source_mode,
        health=health.health,
        loaded_count=health.loaded_count,
        evidence_basis=cast(AnalystEvidenceBasis, health.evidence_basis),
        caveats=caveats,
    )


def _wave_monitor_source_card(response: WaveMonitorOverviewResponse) -> AnalystSourceReadinessCard:
    source_issues = response.summary.source_issues
    health: Literal["loaded", "stale"] = "stale" if source_issues else "loaded"
    caveats = [
        *response.caveats,
        *response.runtime.caveats,
        "Wave Monitor readiness reflects fixture-backed integration state, not live scheduler readiness.",
    ]
    return _build_readiness_card(
        source_id="tool-wave-monitor",
        source_name="Wave Monitor",
        source_category="tool-monitoring",
        source_mode="fixture",
        health=health,
        loaded_count=response.summary.total_signals,
        evidence_basis="scored",
        caveats=caveats,
    )


def _build_readiness_card(
    *,
    source_id: str,
    source_name: str,
    source_category: str,
    source_mode: Literal["fixture", "live", "unknown"],
    health: Literal["loaded", "empty", "stale", "error", "disabled", "unknown"],
    loaded_count: int,
    evidence_basis: AnalystEvidenceBasis,
    caveats: list[str],
) -> AnalystSourceReadinessCard:
    score = {
        "loaded": 85,
        "stale": 62,
        "unknown": 55,
        "empty": 45,
        "error": 20,
        "disabled": 10,
    }[health]
    issues: list[str] = []

    if source_mode == "fixture":
        score = min(score, 80)
        issues.append("Fixture/local mode; freshness and live availability are not asserted.")
    elif source_mode == "unknown":
        score = min(score, 50)
        issues.append("Source mode is unknown.")

    if loaded_count == 0:
        score = min(score, 45)
        issues.append("No normalized records loaded.")
    if health in {"stale", "empty", "error", "disabled", "unknown"}:
        issues.append(f"Parser/source health is {health}.")

    score = max(0, min(score, 100))
    return AnalystSourceReadinessCard(
        source_id=source_id,
        source_name=source_name,
        source_category=source_category,
        source_mode=source_mode,
        health=health,
        loaded_count=loaded_count,
        evidence_basis=evidence_basis,
        readiness_score=score,
        readiness_label=_readiness_label(score),
        issues=issues,
        caveats=caveats,
    )


def _readiness_label(score: int) -> Literal["ready", "usable-with-caveats", "limited", "unavailable"]:
    if score >= 85:
        return "ready"
    if score >= 60:
        return "usable-with-caveats"
    if score >= 35:
        return "limited"
    return "unavailable"


def _readiness_summary(cards: list[AnalystSourceReadinessCard]) -> AnalystSourceReadinessSummary:
    return AnalystSourceReadinessSummary(
        total_sources=len(cards),
        ready_count=sum(1 for card in cards if card.readiness_label == "ready"),
        usable_with_caveats_count=sum(1 for card in cards if card.readiness_label == "usable-with-caveats"),
        limited_count=sum(1 for card in cards if card.readiness_label == "limited"),
        unavailable_count=sum(1 for card in cards if card.readiness_label == "unavailable"),
        fixture_source_count=sum(1 for card in cards if card.source_mode == "fixture"),
    )


def _combined_source_mode(
    source_modes: list[Literal["fixture", "live", "unknown"]],
) -> Literal["fixture", "live", "mixed", "unknown"]:
    modes = {mode for mode in source_modes if mode != "unknown"}
    if not modes:
        return "unknown"
    if len(modes) == 1:
        return modes.pop()
    return "mixed"


def _domain_for_source_category(source_category: str) -> str:
    if source_category.startswith("cyber"):
        return "cyber"
    if source_category.startswith("internet"):
        return "internet-infrastructure"
    if source_category == "world-events":
        return "world-events"
    return "context"


def _analyst_health_for_wave_monitor(
    value: str,
) -> Literal["loaded", "empty", "stale", "error", "disabled", "unknown"]:
    if value == "loaded":
        return "loaded"
    if value == "empty":
        return "empty"
    if value in {"stale", "degraded"}:
        return "stale"
    if value == "error":
        return "error"
    return "unknown"


def _earthquake_summary(magnitude: float | None, place: str | None, depth_km: float | None) -> str:
    parts = []
    if magnitude is not None:
        parts.append(f"M {magnitude:g}")
    if place:
        parts.append(place)
    if depth_km is not None:
        parts.append(f"{depth_km:g} km depth")
    return "; ".join(parts) or "USGS earthquake event"


def _timestamp_sort_key(value: str | None) -> float:
    if value is None:
        return 0.0
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()
    except ValueError:
        return 0.0


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    earth_radius_km = 6371.0088
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    rlat1 = radians(lat1)
    rlat2 = radians(lat2)
    a = sin(dlat / 2) ** 2 + cos(rlat1) * cos(rlat2) * sin(dlon / 2) ** 2
    return 2 * earth_radius_km * asin(sqrt(a))


def _utc_now_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat()
