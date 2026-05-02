from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Literal

from src.adapters.marine import build_marine_adapter
from src.config.settings import Settings
from src.marine.db import session_scope
from src.marine.repository import haversine_meters
from src.marine.gap_detection import MarineGapDetectionService
from src.marine.repository import MarineRepository, MarineSourceUpdate
from src.services.marine_context_service import (
    MarineIrelandOpwWaterLevelService,
    MarineNetherlandsRwsWaterinfoService,
    MarineNdbcService,
    MarineNoaaCoopsService,
    MarineScottishWaterOverflowService,
    MarineVigicruesHydrometryService,
)
from src.services.source_registry import record_source_failure, record_source_success
from src.types.api import (
    FilterSummary,
    MarineAnomalyScore,
    MarineIrelandOpwWaterLevelContextResponse,
    MarineNetherlandsRwsWaterinfoContextResponse,
    MarineNdbcContextResponse,
    MarineNoaaCoopsContextResponse,
    MarineScottishWaterOverflowResponse,
    MarineVigicruesHydrometryContextResponse,
    MarineGapEventsResponse,
    MarineReplayPathResponse,
    MarineChokepointAnalyticalSummaryResponse,
    MarineChokepointSliceSummary,
    MarineReplaySnapshotResponse,
    MarineReplayTimelineResponse,
    MarineReplayViewportResponse,
    MarineObservedWindowSummary,
    MarineViewportAnalyticalSummaryResponse,
    MarineVesselAnalyticalSummaryResponse,
    MarineVesselHistoryResponse,
    MarineVesselMovementSummary,
    MarineVesselsQuery,
    MarineVesselsResponse,
)


class MarineService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._adapter = build_marine_adapter(settings)
        self._gap_detector = MarineGapDetectionService()
        self._noaa_coops = MarineNoaaCoopsService(settings)
        self._ndbc = MarineNdbcService(settings)
        self._scottish_water = MarineScottishWaterOverflowService(settings)
        self._vigicrues_hydrometry = MarineVigicruesHydrometryService(settings)
        self._ireland_opw_waterlevel = MarineIrelandOpwWaterLevelService(settings)
        self._netherlands_rws_waterinfo = MarineNetherlandsRwsWaterinfoService(settings)

    async def ingest_once(self) -> None:
        now = datetime.now(tz=timezone.utc).isoformat()
        cadence_seconds = 60
        stale_after_seconds = 240
        descriptor = self._adapter.descriptor
        cadence_seconds = descriptor.default_cadence_seconds
        stale_after_seconds = descriptor.stale_after_seconds
        try:
            vessels = await self._adapter.fetch()
        except Exception as exc:
            record_source_failure(
                self._adapter.source_name,
                degraded_reason=str(exc),
                stale_after_seconds=stale_after_seconds,
                rate_limited="429" in str(exc),
            )
            raise

        with session_scope(self._settings.marine_database_url) as session:
            repo = MarineRepository(session)
            record_source_success(
                self._adapter.source_name,
                freshness_seconds=cadence_seconds,
                stale_after_seconds=stale_after_seconds,
            )
            repo.upsert_source(
                MarineSourceUpdate(
                    source_key=self._adapter.source_name,
                    display_name=descriptor.display_name,
                    status="healthy",
                    detail=(
                        f"Marine provider mode={self._settings.marine_source_mode}; "
                        f"coverage={descriptor.coverage_scope}; global_claim={descriptor.global_coverage_claimed}."
                    ),
                    cadence_seconds=cadence_seconds,
                    stale_after_seconds=stale_after_seconds,
                    freshness_seconds=cadence_seconds,
                    last_attempt_at=now,
                    last_success_at=now,
                    last_failure_at=None,
                    degraded_reason=None,
                    blocked_reason=None,
                    success_count=1,
                    failure_count=0,
                    warning_count=0,
                    provider_kind=descriptor.provider_kind,
                    coverage_scope=descriptor.coverage_scope,
                    global_coverage_claimed=descriptor.global_coverage_claimed,
                    assumptions=descriptor.assumptions,
                    limitations=descriptor.limitations,
                    source_url=descriptor.external_url,
                    provenance_notes=["Observed vs derived values are explicitly labeled."],
                )
            )

            for vessel in sorted(vessels, key=lambda item: (item.id, item.observed_at or item.timestamp)):
                previous = repo.get_last_position_event(vessel.id)
                expected_interval = self._gap_detector.expected_interval_seconds(
                    speed=vessel.speed,
                    nav_status=vessel.nav_status,
                    cadence_floor=cadence_seconds,
                )
                current = repo.insert_position_event(vessel, expected_interval_seconds=expected_interval)
                repo.upsert_vessel_latest(vessel, last_event_id=current.event_id)
                if previous is not None and previous.event_id != current.event_id:
                    events = self._gap_detector.detect_gap_events(
                        previous=previous,
                        current=current,
                        source_health="healthy",
                        cadence_floor_seconds=cadence_seconds,
                    )
                    repo.insert_gap_events(events)

            repo.ensure_global_snapshot(
                snapshot_at=datetime.now(tz=timezone.utc),
                interval_minutes=self._settings.marine_snapshot_interval_minutes,
            )

    async def list_vessels(self, query: MarineVesselsQuery) -> MarineVesselsResponse:
        await self.ingest_once()
        with session_scope(self._settings.marine_database_url) as session:
            repo = MarineRepository(session)
            vessels, total_candidates = repo.list_live_vessels(
                lamin=query.lamin,
                lamax=query.lamax,
                lomin=query.lomin,
                lomax=query.lomax,
                limit=query.limit,
                q=query.q,
                source=query.source,
                vessel_class=query.vessel_class,
                flag_state=query.flag_state,
                observed_after=query.observed_after,
                observed_before=query.observed_before,
            )
            return MarineVesselsResponse(
                fetched_at=datetime.now(tz=timezone.utc).isoformat(),
                source=self._adapter.source_name,
                count=len(vessels),
                summary=FilterSummary(
                    active_filters={k: str(v) for k, v in query.model_dump().items() if v is not None and v != ""},
                    total_candidates=total_candidates,
                    filtered_count=len(vessels),
                    staleness_warning=None,
                ),
                vessels=vessels,
                sources=repo.list_sources(),
            )

    async def vessel_history(
        self,
        *,
        vessel_id: str,
        start_at: str | None,
        end_at: str | None,
        cursor_after: str | None,
        limit: int,
    ) -> MarineVesselHistoryResponse:
        with session_scope(self._settings.marine_database_url) as session:
            repo = MarineRepository(session)
            points, next_cursor = repo.vessel_history(
                vessel_id=vessel_id,
                start_at=start_at,
                end_at=end_at,
                cursor_after=cursor_after,
                limit=limit,
            )
            return MarineVesselHistoryResponse(
                fetched_at=datetime.now(tz=timezone.utc).isoformat(),
                vessel_id=vessel_id,
                count=len(points),
                points=points,
                next_cursor=next_cursor,
            )

    async def vessel_gaps(
        self,
        *,
        vessel_id: str,
        start_at: str | None,
        end_at: str | None,
        cursor_after: str | None,
        include_derived: bool,
        limit: int,
    ) -> MarineGapEventsResponse:
        with session_scope(self._settings.marine_database_url) as session:
            repo = MarineRepository(session)
            events, next_cursor = repo.vessel_gaps(
                vessel_id=vessel_id,
                start_at=start_at,
                end_at=end_at,
                cursor_after=cursor_after,
                include_derived=include_derived,
                limit=limit,
            )
            return MarineGapEventsResponse(
                fetched_at=datetime.now(tz=timezone.utc).isoformat(),
                vessel_id=vessel_id,
                count=len(events),
                events=events,
                next_cursor=next_cursor,
            )

    async def replay_timeline(
        self, *, start_at: str, end_at: str, cursor_after: str | None, limit: int
    ) -> MarineReplayTimelineResponse:
        with session_scope(self._settings.marine_database_url) as session:
            repo = MarineRepository(session)
            segments, next_cursor = repo.replay_timeline(
                start_at=start_at,
                end_at=end_at,
                cursor_after=cursor_after,
                limit=limit,
            )
            return MarineReplayTimelineResponse(
                fetched_at=datetime.now(tz=timezone.utc).isoformat(),
                start_at=start_at,
                end_at=end_at,
                count=len(segments),
                segments=segments,
                next_cursor=next_cursor,
            )

    async def replay_snapshot(
        self,
        *,
        at_or_before: str,
        lamin: float | None,
        lamax: float | None,
        lomin: float | None,
        lomax: float | None,
    ) -> MarineReplaySnapshotResponse:
        with session_scope(self._settings.marine_database_url) as session:
            repo = MarineRepository(session)
            snapshot, vessels = repo.replay_snapshot(
                at_or_before=at_or_before,
                lamin=lamin,
                lamax=lamax,
                lomin=lomin,
                lomax=lomax,
            )
            return MarineReplaySnapshotResponse(
                fetched_at=datetime.now(tz=timezone.utc).isoformat(),
                at_or_before=at_or_before,
                snapshot=snapshot,
                count=len(vessels),
                vessels=vessels,
            )

    async def replay_viewport(
        self,
        *,
        at_or_before: str,
        lamin: float,
        lamax: float,
        lomin: float,
        lomax: float,
        limit: int,
    ) -> MarineReplayViewportResponse:
        with session_scope(self._settings.marine_database_url) as session:
            repo = MarineRepository(session)
            vessels = repo.replay_viewport(
                at_or_before=at_or_before,
                lamin=lamin,
                lamax=lamax,
                lomin=lomin,
                lomax=lomax,
                limit=limit,
            )
            return MarineReplayViewportResponse(
                fetched_at=datetime.now(tz=timezone.utc).isoformat(),
                at_or_before=at_or_before,
                count=len(vessels),
                vessels=vessels,
            )

    async def replay_path(
        self,
        *,
        vessel_id: str,
        start_at: str | None,
        end_at: str | None,
        cursor_after: str | None,
        include_interpolated: bool,
        limit: int,
    ) -> MarineReplayPathResponse:
        with session_scope(self._settings.marine_database_url) as session:
            repo = MarineRepository(session)
            points, next_cursor = repo.vessel_path(
                vessel_id=vessel_id,
                start_at=start_at,
                end_at=end_at,
                cursor_after=cursor_after,
                include_interpolated=include_interpolated,
                limit=limit,
            )
            return MarineReplayPathResponse(
                fetched_at=datetime.now(tz=timezone.utc).isoformat(),
                vessel_id=vessel_id,
                include_interpolated=include_interpolated,
                count=len(points),
                points=points,
                next_cursor=next_cursor,
            )

    async def vessel_summary(
        self,
        *,
        vessel_id: str,
        start_at: str | None,
        end_at: str | None,
    ) -> MarineVesselAnalyticalSummaryResponse:
        now = datetime.now(tz=timezone.utc)
        effective_end = end_at or now.isoformat()
        effective_start = start_at or (now - timedelta(hours=24)).isoformat()
        with session_scope(self._settings.marine_database_url) as session:
            repo = MarineRepository(session)
            points, _ = repo.vessel_history(
                vessel_id=vessel_id,
                start_at=effective_start,
                end_at=effective_end,
                cursor_after=None,
                limit=20_000,
            )
            gaps, _ = repo.vessel_gaps(
                vessel_id=vessel_id,
                start_at=effective_start,
                end_at=effective_end,
                cursor_after=None,
                include_derived=True,
                limit=20_000,
            )
            live, _ = repo.list_live_vessels(
                lamin=None,
                lamax=None,
                lomin=None,
                lomax=None,
                limit=5000,
                q=None,
                source=None,
                vessel_class=None,
                flag_state=None,
                observed_after=None,
                observed_before=None,
            )
            latest = next((v for v in live if v.id == vessel_id), None)
            movement_distance = 0.0
            observed_points = [p for p in points if p.observed_vs_derived == "observed"]
            for prev, curr in zip(observed_points, observed_points[1:]):
                movement_distance += haversine_meters(prev.latitude, prev.longitude, curr.latitude, curr.longitude)
            avg_speed = None
            speeds = [float(p.speed) for p in observed_points if p.speed is not None]
            if speeds:
                avg_speed = round(sum(speeds) / len(speeds), 2)
            observed_gap_count = sum(
                1 for e in gaps if e.event_kind in {"observed-signal-gap-start", "observed-signal-gap-end", "resumed-observation"}
            )
            suspicious_count = sum(1 for e in gaps if e.event_kind == "possible-transponder-silence-interval")
            longest_gap = max((e.gap_duration_seconds or 0 for e in gaps), default=0) or None
            resumed_events = [e for e in gaps if e.event_kind == "resumed-observation"]
            resumed_latest = resumed_events[-1] if resumed_events else None
            sources = repo.list_sources()
            source_status = sources[0] if sources else None
            longest_suspicious_gap = max(
                (
                    e.gap_duration_seconds or 0
                    for e in gaps
                    if e.event_kind == "possible-transponder-silence-interval"
                ),
                default=0,
            )
            moved_during_suspicious_m = max(
                (
                    e.distance_moved_m or 0.0
                    for e in gaps
                    if e.event_kind == "possible-transponder-silence-interval"
                ),
                default=0.0,
            )
            anomaly = _score_vessel_anomaly(
                suspicious_count=suspicious_count,
                longest_suspicious_gap_seconds=longest_suspicious_gap,
                resumed_count=len(resumed_events),
                movement_during_suspicious_m=moved_during_suspicious_m,
                source_state=(source_status.state if source_status else "unknown"),
                sparse_plausible_count=sum(1 for e in gaps if e.normal_sparse_reporting_plausible),
            )
            return MarineVesselAnalyticalSummaryResponse(
                fetched_at=now.isoformat(),
                vessel_id=vessel_id,
                window=MarineObservedWindowSummary(
                    start_at=effective_start,
                    end_at=effective_end,
                    observed_point_count=len(observed_points),
                ),
                latest_observed=latest,
                movement=MarineVesselMovementSummary(
                    observed_point_count=len(observed_points),
                    distance_moved_m=round(movement_distance, 2),
                    average_speed_kts=avg_speed,
                    observed_start_at=observed_points[0].observed_at if observed_points else None,
                    observed_end_at=observed_points[-1].observed_at if observed_points else None,
                ),
                observed_gap_event_count=observed_gap_count,
                suspicious_gap_event_count=suspicious_count,
                longest_gap_seconds=longest_gap,
                most_recent_resumed_observation=resumed_latest,
                source_status=source_status,
                anomaly=anomaly,
                observed_fields=[
                    "latest_observed",
                    "movement.observed_point_count",
                    "movement.distance_moved_m",
                    "observed_gap_event_count",
                    "longest_gap_seconds",
                ],
                inferred_fields=[
                    "suspicious_gap_event_count",
                    "most_recent_resumed_observation (event semantics)",
                ],
            )

    async def viewport_summary(
        self,
        *,
        at_or_before: str,
        start_at: str | None,
        lamin: float,
        lamax: float,
        lomin: float,
        lomax: float,
    ) -> MarineViewportAnalyticalSummaryResponse:
        with session_scope(self._settings.marine_database_url) as session:
            repo = MarineRepository(session)
            end_dt = _iso(at_or_before)
            start_dt = _iso(start_at) if start_at else (end_dt - timedelta(hours=1))
            now_vessels = repo.replay_viewport(
                at_or_before=end_dt.isoformat(),
                lamin=lamin,
                lamax=lamax,
                lomin=lomin,
                lomax=lomax,
                limit=5000,
            )
            then_vessels = repo.replay_viewport(
                at_or_before=start_dt.isoformat(),
                lamin=lamin,
                lamax=lamax,
                lomin=lomin,
                lomax=lomax,
                limit=5000,
            )
            current_ids = {v.id for v in now_vessels}
            previous_ids = {v.id for v in then_vessels}
            entry_count = len(current_ids - previous_ids)
            exit_count = len(previous_ids - current_ids)
            active_count = sum(1 for v in now_vessels if (v.speed or 0.0) >= 1.0)
            observed_gap_count = 0
            suspicious_count = 0
            for vessel in now_vessels:
                events, _ = repo.vessel_gaps(
                    vessel_id=vessel.id,
                    start_at=start_dt.isoformat(),
                    end_at=end_dt.isoformat(),
                    cursor_after=None,
                    include_derived=True,
                    limit=5000,
                )
                for event in events:
                    if event.start_latitude is None or event.start_longitude is None:
                        continue
                    if not (lamin <= event.start_latitude <= lamax and lomin <= event.start_longitude <= lomax):
                        continue
                    if event.event_kind in {"observed-signal-gap-start", "observed-signal-gap-end", "resumed-observation"}:
                        observed_gap_count += 1
                    if event.event_kind == "possible-transponder-silence-interval":
                        suspicious_count += 1
            density = 0.0
            if now_vessels:
                density = suspicious_count / max(len(now_vessels), 1)
            anomaly = _score_viewport_anomaly(
                suspicious_gap_density=density,
                observed_gap_count=observed_gap_count,
                entry_count=entry_count,
                exit_count=exit_count,
                vessel_count=len(now_vessels),
            )
            return MarineViewportAnalyticalSummaryResponse(
                fetched_at=datetime.now(tz=timezone.utc).isoformat(),
                at_or_before=end_dt.isoformat(),
                window=MarineObservedWindowSummary(
                    start_at=start_dt.isoformat(),
                    end_at=end_dt.isoformat(),
                    observed_point_count=len(now_vessels),
                ),
                vessel_count=len(now_vessels),
                active_vessel_count=active_count,
                observed_gap_event_count=observed_gap_count,
                suspicious_gap_event_count=suspicious_count,
                viewport_entry_count=entry_count,
                viewport_exit_count=exit_count,
                anomaly=anomaly,
                observed_fields=[
                    "vessel_count",
                    "active_vessel_count",
                    "observed_gap_event_count",
                    "viewport_entry_count",
                    "viewport_exit_count",
                ],
                inferred_fields=["suspicious_gap_event_count"],
            )

    async def chokepoint_summary(
        self,
        *,
        start_at: str,
        end_at: str,
        lamin: float,
        lamax: float,
        lomin: float,
        lomax: float,
        slice_minutes: int,
    ) -> MarineChokepointAnalyticalSummaryResponse:
        start_dt = _iso(start_at)
        end_dt = _iso(end_at)
        slices: list[MarineChokepointSliceSummary] = []
        total_vessel_obs = 0
        total_observed_gaps = 0
        total_suspicious = 0
        with session_scope(self._settings.marine_database_url) as session:
            repo = MarineRepository(session)
            cursor = start_dt
            while cursor < end_dt:
                next_cursor = min(cursor + timedelta(minutes=slice_minutes), end_dt)
                vessels = repo.replay_viewport(
                    at_or_before=next_cursor.isoformat(),
                    lamin=lamin,
                    lamax=lamax,
                    lomin=lomin,
                    lomax=lomax,
                    limit=5000,
                )
                active_count = sum(1 for v in vessels if (v.speed or 0.0) >= 1.0)
                observed_gap_count = 0
                suspicious_count = 0
                for vessel in vessels:
                    events, _ = repo.vessel_gaps(
                        vessel_id=vessel.id,
                        start_at=cursor.isoformat(),
                        end_at=next_cursor.isoformat(),
                        cursor_after=None,
                        include_derived=True,
                        limit=2000,
                    )
                    for event in events:
                        if event.start_latitude is None or event.start_longitude is None:
                            continue
                        if not (lamin <= event.start_latitude <= lamax and lomin <= event.start_longitude <= lomax):
                            continue
                        if event.event_kind in {"observed-signal-gap-start", "observed-signal-gap-end", "resumed-observation"}:
                            observed_gap_count += 1
                        if event.event_kind == "possible-transponder-silence-interval":
                            suspicious_count += 1
                total_vessel_obs += len(vessels)
                total_observed_gaps += observed_gap_count
                total_suspicious += suspicious_count
                slice_density = suspicious_count / max(len(vessels), 1) if vessels else 0.0
                slices.append(
                    MarineChokepointSliceSummary(
                        slice_start_at=cursor.isoformat(),
                        slice_end_at=next_cursor.isoformat(),
                        vessel_count=len(vessels),
                        active_vessel_count=active_count,
                        observed_gap_event_count=observed_gap_count,
                        suspicious_gap_event_count=suspicious_count,
                        anomaly=_score_chokepoint_slice_anomaly(
                            suspicious_gap_density=slice_density,
                            observed_gap_count=observed_gap_count,
                            vessel_count=len(vessels),
                        ),
                    )
                )
                cursor = next_cursor
        ranked = sorted(slices, key=lambda item: item.anomaly.score, reverse=True)
        for idx, item in enumerate(ranked, start=1):
            item.anomaly.priority_rank = idx
        return MarineChokepointAnalyticalSummaryResponse(
            fetched_at=datetime.now(tz=timezone.utc).isoformat(),
            start_at=start_dt.isoformat(),
            end_at=end_dt.isoformat(),
            slice_minutes=slice_minutes,
            slice_count=len(slices),
            total_vessel_observations=total_vessel_obs,
            total_observed_gap_events=total_observed_gaps,
            total_suspicious_gap_events=total_suspicious,
            anomaly=_score_chokepoint_overall_anomaly(
                total_vessel_observations=total_vessel_obs,
                total_observed_gap_events=total_observed_gaps,
                total_suspicious_gap_events=total_suspicious,
            ),
            slices=slices,
            observed_fields=[
                "slices.vessel_count",
                "slices.active_vessel_count",
                "slices.observed_gap_event_count",
                "total_vessel_observations",
                "total_observed_gap_events",
            ],
            inferred_fields=["slices.suspicious_gap_event_count", "total_suspicious_gap_events"],
        )

    async def noaa_coops_context(
        self,
        *,
        center_lat: float,
        center_lon: float,
        radius_km: float,
        limit: int,
        context_kind: str,
    ) -> MarineNoaaCoopsContextResponse:
        return await self._noaa_coops.context(
            center_lat=center_lat,
            center_lon=center_lon,
            radius_km=radius_km,
            limit=limit,
            context_kind="chokepoint" if context_kind == "chokepoint" else "viewport",
        )

    async def ndbc_context(
        self,
        *,
        center_lat: float,
        center_lon: float,
        radius_km: float,
        limit: int,
        context_kind: str,
    ) -> MarineNdbcContextResponse:
        return await self._ndbc.context(
            center_lat=center_lat,
            center_lon=center_lon,
            radius_km=radius_km,
            limit=limit,
            context_kind="chokepoint" if context_kind == "chokepoint" else "viewport",
        )

    async def scottish_water_overflows_context(
        self,
        *,
        center_lat: float,
        center_lon: float,
        radius_km: float,
        limit: int,
        status: str,
    ) -> MarineScottishWaterOverflowResponse:
        return await self._scottish_water.context(
            center_lat=center_lat,
            center_lon=center_lon,
            radius_km=radius_km,
            limit=limit,
            status="inactive" if status == "inactive" else "active" if status == "active" else "all",
        )

    async def vigicrues_hydrometry_context(
        self,
        *,
        center_lat: float,
        center_lon: float,
        radius_km: float,
        limit: int,
        parameter_filter: Literal["all", "water-height", "flow"],
    ) -> MarineVigicruesHydrometryContextResponse:
        return await self._vigicrues_hydrometry.context(
            center_lat=center_lat,
            center_lon=center_lon,
            radius_km=radius_km,
            limit=limit,
            parameter_filter=parameter_filter,
        )

    async def ireland_opw_waterlevel_context(
        self,
        *,
        center_lat: float,
        center_lon: float,
        radius_km: float,
        limit: int,
    ) -> MarineIrelandOpwWaterLevelContextResponse:
        return await self._ireland_opw_waterlevel.context(
            center_lat=center_lat,
            center_lon=center_lon,
            radius_km=radius_km,
            limit=limit,
        )

    async def netherlands_rws_waterinfo_context(
        self,
        *,
        center_lat: float,
        center_lon: float,
        radius_km: float,
        limit: int,
    ) -> MarineNetherlandsRwsWaterinfoContextResponse:
        return await self._netherlands_rws_waterinfo.context(
            center_lat=center_lat,
            center_lon=center_lon,
            radius_km=radius_km,
            limit=limit,
        )


def _iso(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def _score_vessel_anomaly(
    *,
    suspicious_count: int,
    longest_suspicious_gap_seconds: int,
    resumed_count: int,
    movement_during_suspicious_m: float,
    source_state: str,
    sparse_plausible_count: int,
) -> MarineAnomalyScore:
    score = 0.0
    reasons: list[str] = []
    caveats: list[str] = []
    score += min(suspicious_count * 18.0, 45.0)
    if suspicious_count > 0:
        reasons.append(f"{suspicious_count} suspicious gap interval(s) observed")
    score += min(longest_suspicious_gap_seconds / 1800.0 * 8.0, 25.0)
    if longest_suspicious_gap_seconds > 0:
        reasons.append(f"longest suspicious interval {longest_suspicious_gap_seconds}s")
    score += min(movement_during_suspicious_m / 25_000.0 * 10.0, 20.0)
    if movement_during_suspicious_m > 0:
        reasons.append(f"movement during suspicious interval up to {int(movement_during_suspicious_m)}m")
    score += min(resumed_count * 3.0, 10.0)
    if resumed_count > 0:
        reasons.append("resumed-observation events present")
    if sparse_plausible_count > 0:
        score -= min(sparse_plausible_count * 7.0, 20.0)
        caveats.append("sparse reporting plausibility reduced anomaly priority")
    if source_state in {"degraded", "stale"}:
        score -= 12.0
        caveats.append("source health degraded/stale; anomaly confidence reduced")
    clamped = max(0.0, min(score, 100.0))
    level = "low" if clamped < 35 else ("medium" if clamped < 70 else "high")
    return MarineAnomalyScore(
        score=round(clamped, 2),
        level=level,
        priority_rank=None,
        display_label=f"{level.capitalize()} anomaly priority",
        reasons=reasons,
        caveats=caveats,
        observed_signals=["observed-signal-gap-start", "observed-signal-gap-end", "resumed-observation"],
        inferred_signals=["possible-transponder-silence-interval"],
        scored_signals=[
            "suspicious_gap_count",
            "longest_suspicious_gap_seconds",
            "movement_during_suspicious_gap_m",
            "resumed_observation_count",
            "sparse_reporting_penalty",
            "source_health_penalty",
        ],
    )


def _score_viewport_anomaly(
    *,
    suspicious_gap_density: float,
    observed_gap_count: int,
    entry_count: int,
    exit_count: int,
    vessel_count: int,
) -> MarineAnomalyScore:
    score = 0.0
    reasons: list[str] = []
    score += min(suspicious_gap_density * 100.0, 45.0)
    if suspicious_gap_density > 0:
        reasons.append(f"suspicious-gap density {suspicious_gap_density:.2f} per vessel")
    score += min(observed_gap_count * 4.0, 30.0)
    if observed_gap_count > 0:
        reasons.append(f"{observed_gap_count} observed gap events")
    churn = (entry_count + exit_count) / max(vessel_count, 1) if vessel_count else 0.0
    score += min(churn * 20.0, 20.0)
    if churn > 0.5:
        reasons.append("high entry/exit churn for window")
    clamped = max(0.0, min(score, 100.0))
    level = "low" if clamped < 30 else ("medium" if clamped < 65 else "high")
    caveats = ["low-sample viewport window"] if vessel_count < 3 else []
    return MarineAnomalyScore(
        score=round(clamped, 2),
        level=level,
        priority_rank=None,
        display_label=f"{level.capitalize()} viewport anomaly",
        reasons=reasons,
        caveats=caveats,
        observed_signals=["observed_gap_event_count", "viewport_entry_count", "viewport_exit_count"],
        inferred_signals=["suspicious_gap_density"],
        scored_signals=["suspicious_gap_density", "observed_gap_count", "entry_exit_churn"],
    )


def _score_chokepoint_slice_anomaly(
    *, suspicious_gap_density: float, observed_gap_count: int, vessel_count: int
) -> MarineAnomalyScore:
    score = min(suspicious_gap_density * 90.0, 55.0) + min(observed_gap_count * 5.0, 35.0)
    level = "low" if score < 30 else ("medium" if score < 65 else "high")
    caveats = ["low-sample slice"] if vessel_count < 2 else []
    reasons = []
    if suspicious_gap_density > 0:
        reasons.append(f"suspicious-gap density {suspicious_gap_density:.2f}")
    if observed_gap_count > 0:
        reasons.append(f"{observed_gap_count} observed gap events")
    return MarineAnomalyScore(
        score=round(max(0.0, min(score, 100.0)), 2),
        level=level,
        priority_rank=None,
        display_label=f"{level.capitalize()} slice anomaly",
        reasons=reasons,
        caveats=caveats,
        observed_signals=["observed_gap_event_count"],
        inferred_signals=["suspicious_gap_density"],
        scored_signals=["suspicious_gap_density", "observed_gap_count"],
    )


def _score_chokepoint_overall_anomaly(
    *, total_vessel_observations: int, total_observed_gap_events: int, total_suspicious_gap_events: int
) -> MarineAnomalyScore:
    density = total_suspicious_gap_events / max(total_vessel_observations, 1) if total_vessel_observations else 0.0
    score = min(density * 120.0, 60.0) + min(total_observed_gap_events * 2.0, 30.0)
    level = "low" if score < 30 else ("medium" if score < 65 else "high")
    return MarineAnomalyScore(
        score=round(max(0.0, min(score, 100.0)), 2),
        level=level,
        priority_rank=None,
        display_label=f"{level.capitalize()} chokepoint anomaly",
        reasons=[
            f"total suspicious-gap events: {total_suspicious_gap_events}",
            f"total observed gap events: {total_observed_gap_events}",
        ],
        caveats=[],
        observed_signals=["total_observed_gap_events"],
        inferred_signals=["total_suspicious_gap_events"],
        scored_signals=["suspicious_gap_density", "observed_gap_total"],
    )
