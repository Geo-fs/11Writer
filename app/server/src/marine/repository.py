from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from math import asin, cos, radians, sin, sqrt

from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session

from src.marine.models import (
    MarineGapEventORM,
    MarinePositionEventORM,
    MarineReplaySnapshotMemberORM,
    MarineReplaySnapshotORM,
    MarineSourceORM,
    MarineTimelineSegmentORM,
    MarineVesselLatestORM,
)
from src.types.api import (
    MarineGapEvent,
    MarineReplayPathPoint,
    MarineReplaySnapshotRef,
    MarineReplayTimelineSegment,
    MarineSourceStatus,
)
from src.types.entities import MarineQualityMetadata, MarineVesselEntity


@dataclass
class MarineSourceUpdate:
    source_key: str
    display_name: str
    status: str
    detail: str
    cadence_seconds: int
    stale_after_seconds: int
    freshness_seconds: int | None
    last_attempt_at: str
    last_success_at: str | None
    last_failure_at: str | None
    degraded_reason: str | None
    blocked_reason: str | None
    success_count: int
    failure_count: int
    warning_count: int
    provider_kind: str = "unknown"
    coverage_scope: str = "unknown"
    global_coverage_claimed: bool = False
    assumptions: list[str] | None = None
    limitations: list[str] | None = None
    source_url: str | None = None
    enabled: bool = True
    provenance_notes: list[str] | None = None


@dataclass
class GapEventInput:
    vessel_id: str
    source_key: str
    event_kind: str
    gap_start_observed_at: str
    gap_end_observed_at: str | None
    gap_duration_seconds: int | None
    start_latitude: float | None
    start_longitude: float | None
    end_latitude: float | None
    end_longitude: float | None
    distance_moved_m: float | None
    expected_interval_seconds: int | None
    exceeds_expected_cadence: bool
    confidence_class: str
    confidence_score: float | None
    normal_sparse_reporting_plausible: bool
    confidence_breakdown: dict[str, float]
    derivation_method: str
    input_event_ids: list[int]
    uncertainty_notes: list[str]
    evidence_summary: str | None
    created_at: str


class MarineRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def upsert_source(self, update: MarineSourceUpdate) -> None:
        row = self._session.get(MarineSourceORM, update.source_key)
        if row is None:
            row = MarineSourceORM(source_key=update.source_key)
            self._session.add(row)
        row.display_name = update.display_name
        row.enabled = update.enabled
        row.status = update.status
        row.detail = update.detail
        row.cadence_seconds = update.cadence_seconds
        row.stale_after_seconds = update.stale_after_seconds
        row.freshness_seconds = update.freshness_seconds
        row.last_attempt_at = update.last_attempt_at
        row.last_success_at = update.last_success_at
        row.last_failure_at = update.last_failure_at
        row.degraded_reason = update.degraded_reason
        row.blocked_reason = update.blocked_reason
        row.success_count = update.success_count
        row.failure_count = update.failure_count
        row.warning_count = update.warning_count
        row.provider_kind = update.provider_kind
        row.coverage_scope = update.coverage_scope
        row.global_coverage_claimed = update.global_coverage_claimed
        row.assumptions_json = json.dumps(update.assumptions or [])
        row.limitations_json = json.dumps(update.limitations or [])
        row.source_url = update.source_url
        row.provenance_notes_json = json.dumps(update.provenance_notes or [])
        self._session.flush()

    def get_last_position_event(self, vessel_id: str) -> MarinePositionEventORM | None:
        return self._session.execute(
            select(MarinePositionEventORM)
            .where(MarinePositionEventORM.vessel_id == vessel_id)
            .order_by(MarinePositionEventORM.observed_at.desc(), MarinePositionEventORM.event_id.desc())
            .limit(1)
        ).scalar_one_or_none()

    def insert_position_event(self, vessel: MarineVesselEntity, expected_interval_seconds: int | None) -> MarinePositionEventORM:
        observed_at = vessel.observed_at or vessel.timestamp
        existing = self._session.execute(
            select(MarinePositionEventORM)
            .where(MarinePositionEventORM.vessel_id == vessel.id)
            .where(MarinePositionEventORM.source_key == vessel.source)
            .where(MarinePositionEventORM.observed_at == observed_at)
            .limit(1)
        ).scalar_one_or_none()
        if existing is not None:
            return existing

        dt = _parse_iso(observed_at)
        row = MarinePositionEventORM(
            vessel_id=vessel.id,
            source_key=vessel.source,
            mmsi=vessel.mmsi,
            imo=vessel.imo,
            callsign=vessel.callsign,
            vessel_name=vessel.vessel_name,
            flag_state=vessel.flag_state,
            vessel_class=vessel.vessel_class,
            nav_status=vessel.nav_status,
            destination=vessel.destination,
            eta=vessel.eta,
            latitude=vessel.latitude,
            longitude=vessel.longitude,
            course=vessel.course,
            heading=vessel.heading,
            speed=vessel.speed,
            observed_at=observed_at,
            fetched_at=vessel.fetched_at or vessel.timestamp,
            source_detail=vessel.source_detail,
            external_url=vessel.external_url,
            confidence=vessel.confidence,
            quality_score=vessel.quality.score if vessel.quality else None,
            quality_label=vessel.quality.label if vessel.quality else None,
            quality_notes_json=json.dumps(vessel.quality.notes if vessel.quality else []),
            observed_vs_derived=vessel.observed_vs_derived,
            geometry_provenance=vessel.geometry_provenance,
            status=vessel.status,
            expected_reporting_interval_seconds=expected_interval_seconds,
            metadata_json=json.dumps(vessel.metadata),
            bucket_date=dt.date().isoformat(),
            bucket_hour=dt.hour,
            vessel_shard=_vessel_shard(vessel.id),
        )
        self._session.add(row)
        self._session.flush()
        return row
    def upsert_vessel_latest(self, vessel: MarineVesselEntity, last_event_id: int | None) -> None:
        dt = _parse_iso(vessel.observed_at or vessel.timestamp)
        row = self._session.get(MarineVesselLatestORM, vessel.id)
        if row is None:
            row = MarineVesselLatestORM(vessel_id=vessel.id)
            self._session.add(row)
        row.source_key = vessel.source
        row.mmsi = vessel.mmsi
        row.imo = vessel.imo
        row.callsign = vessel.callsign
        row.vessel_name = vessel.vessel_name
        row.flag_state = vessel.flag_state
        row.vessel_class = vessel.vessel_class
        row.nav_status = vessel.nav_status
        row.destination = vessel.destination
        row.eta = vessel.eta
        row.latitude = vessel.latitude
        row.longitude = vessel.longitude
        row.course = vessel.course
        row.heading = vessel.heading
        row.speed = vessel.speed
        row.observed_at = vessel.observed_at or vessel.timestamp
        row.fetched_at = vessel.fetched_at or vessel.timestamp
        row.status = vessel.status
        row.source_detail = vessel.source_detail
        row.external_url = vessel.external_url
        row.confidence = vessel.confidence
        row.quality_score = vessel.quality.score if vessel.quality else None
        row.quality_label = vessel.quality.label if vessel.quality else None
        row.quality_notes_json = json.dumps(vessel.quality.notes if vessel.quality else [])
        row.stale = vessel.stale
        row.degraded = vessel.degraded
        row.degraded_reason = vessel.degraded_reason
        row.source_health = vessel.source_health
        row.observed_vs_derived = vessel.observed_vs_derived
        row.geometry_provenance = vessel.geometry_provenance
        row.reference_ref_id = vessel.reference_ref_id
        row.metadata_json = json.dumps(vessel.metadata)
        row.bucket_date = dt.date().isoformat()
        row.bucket_hour = dt.hour
        row.vessel_shard = _vessel_shard(vessel.id)
        row.last_event_id = last_event_id
        self._session.flush()

    def insert_gap_events(self, events: list[GapEventInput]) -> None:
        for event in events:
            dt = _parse_iso(event.gap_start_observed_at)
            self._session.add(
                MarineGapEventORM(
                    vessel_id=event.vessel_id,
                    source_key=event.source_key,
                    event_kind=event.event_kind,
                    gap_start_observed_at=event.gap_start_observed_at,
                    gap_end_observed_at=event.gap_end_observed_at,
                    gap_duration_seconds=event.gap_duration_seconds,
                    start_latitude=event.start_latitude,
                    start_longitude=event.start_longitude,
                    end_latitude=event.end_latitude,
                    end_longitude=event.end_longitude,
                    distance_moved_m=event.distance_moved_m,
                    expected_interval_seconds=event.expected_interval_seconds,
                    exceeds_expected_cadence=event.exceeds_expected_cadence,
                    confidence_class=event.confidence_class,
                    confidence_score=event.confidence_score,
                    normal_sparse_reporting_plausible=event.normal_sparse_reporting_plausible,
                    confidence_breakdown_json=json.dumps(event.confidence_breakdown),
                    derivation_method=event.derivation_method,
                    input_event_ids_json=json.dumps(event.input_event_ids),
                    uncertainty_notes_json=json.dumps(event.uncertainty_notes),
                    evidence_summary=event.evidence_summary,
                    created_at=event.created_at,
                    bucket_date=dt.date().isoformat(),
                    bucket_hour=dt.hour,
                    vessel_shard=_vessel_shard(event.vessel_id),
                )
            )
        self._session.flush()

    def ensure_global_snapshot(self, *, snapshot_at: datetime, interval_minutes: int) -> MarineReplaySnapshotORM | None:
        bucket_minute = (snapshot_at.minute // interval_minutes) * interval_minutes
        aligned = snapshot_at.replace(minute=bucket_minute, second=0, microsecond=0)
        aligned_iso = aligned.isoformat()

        existing = self._session.execute(
            select(MarineReplaySnapshotORM)
            .where(MarineReplaySnapshotORM.scope_kind == "global")
            .where(MarineReplaySnapshotORM.snapshot_at == aligned_iso)
            .limit(1)
        ).scalar_one_or_none()
        if existing is not None:
            return None

        vessel_rows = self._session.execute(select(MarineVesselLatestORM)).scalars().all()
        snapshot = MarineReplaySnapshotORM(
            snapshot_at=aligned_iso,
            bucket_date=aligned.date().isoformat(),
            bucket_hour=aligned.hour,
            scope_kind="global",
            vessel_count=len(vessel_rows),
            position_event_count=self._session.execute(select(func.count(MarinePositionEventORM.event_id))).scalar_one(),
            storage_key=f"marine/global/{aligned.date().isoformat()}/{aligned.hour:02d}/{aligned.minute:02d}",
            chunk_id=f"global-{aligned.date().isoformat()}-{aligned.hour:02d}{aligned.minute:02d}",
            derived_from_event_id=max((row.last_event_id or 0) for row in vessel_rows) if vessel_rows else None,
            created_at=datetime.now(tz=timezone.utc).isoformat(),
        )
        self._session.add(snapshot)
        self._session.flush()

        for vessel in vessel_rows:
            self._session.add(
                MarineReplaySnapshotMemberORM(
                    snapshot_id=snapshot.snapshot_id,
                    vessel_id=vessel.vessel_id,
                    source_key=vessel.source_key,
                    mmsi=vessel.mmsi,
                    vessel_name=vessel.vessel_name,
                    latitude=vessel.latitude,
                    longitude=vessel.longitude,
                    course=vessel.course,
                    heading=vessel.heading,
                    speed=vessel.speed,
                    observed_at=vessel.observed_at,
                    fetched_at=vessel.fetched_at,
                    status=vessel.status,
                    confidence=vessel.confidence,
                    geometry_provenance=vessel.geometry_provenance,
                    metadata_json=vessel.metadata_json,
                )
            )
        gaps_count = self._session.execute(select(func.count(MarineGapEventORM.gap_event_id))).scalar_one()
        self._session.add(
            MarineTimelineSegmentORM(
                segment_start_at=aligned_iso,
                segment_end_at=(aligned + timedelta(minutes=interval_minutes)).isoformat(),
                bucket_date=aligned.date().isoformat(),
                bucket_hour=aligned.hour,
                scope_kind="global",
                vessel_count=len(vessel_rows),
                position_event_count=snapshot.position_event_count,
                gap_event_count=gaps_count,
                snapshot_id=snapshot.snapshot_id,
                chunk_id=snapshot.chunk_id,
                metadata_json=json.dumps({"intervalMinutes": interval_minutes}),
            )
        )
        self._session.flush()
        return snapshot

    def list_live_vessels(
        self,
        *,
        lamin: float | None,
        lamax: float | None,
        lomin: float | None,
        lomax: float | None,
        limit: int,
        q: str | None,
        source: str | None,
        vessel_class: str | None,
        flag_state: str | None,
        observed_after: str | None,
        observed_before: str | None,
    ) -> tuple[list[MarineVesselEntity], int]:
        query = select(MarineVesselLatestORM)
        if lamin is not None and lamax is not None:
            query = query.where(MarineVesselLatestORM.latitude >= min(lamin, lamax)).where(MarineVesselLatestORM.latitude <= max(lamin, lamax))
        if lomin is not None and lomax is not None:
            query = query.where(MarineVesselLatestORM.longitude >= min(lomin, lomax)).where(MarineVesselLatestORM.longitude <= max(lomin, lomax))
        if source:
            query = query.where(MarineVesselLatestORM.source_key == source)
        if vessel_class:
            query = query.where(MarineVesselLatestORM.vessel_class == vessel_class)
        if flag_state:
            query = query.where(MarineVesselLatestORM.flag_state == flag_state)
        if observed_after:
            query = query.where(MarineVesselLatestORM.observed_at >= observed_after)
        if observed_before:
            query = query.where(MarineVesselLatestORM.observed_at <= observed_before)
        if q:
            like = f"%{q}%"
            query = query.where(
                or_(
                    MarineVesselLatestORM.vessel_name.ilike(like),
                    MarineVesselLatestORM.callsign.ilike(like),
                    MarineVesselLatestORM.mmsi.ilike(like),
                    MarineVesselLatestORM.imo.ilike(like),
                )
            )

        total = self._session.execute(select(func.count()).select_from(query.subquery())).scalar_one()
        rows = self._session.execute(query.order_by(MarineVesselLatestORM.observed_at.desc()).limit(limit)).scalars().all()
        return [self._entity_from_latest(row) for row in rows], int(total)

    def list_sources(self) -> list[MarineSourceStatus]:
        rows = self._session.execute(select(MarineSourceORM).order_by(MarineSourceORM.source_key)).scalars().all()
        return [
            MarineSourceStatus(
                source_key=row.source_key,
                display_name=row.display_name,
                enabled=row.enabled,
                state=row.status,
                detail=row.detail,
                freshness_seconds=row.freshness_seconds,
                stale_after_seconds=row.stale_after_seconds,
                last_success_at=row.last_success_at,
                last_attempt_at=row.last_attempt_at,
                last_failure_at=row.last_failure_at,
                degraded_reason=row.degraded_reason,
                blocked_reason=row.blocked_reason,
                success_count=row.success_count,
                failure_count=row.failure_count,
                warning_count=row.warning_count,
                cadence_seconds=row.cadence_seconds,
                provider_kind=row.provider_kind,
                coverage_scope=row.coverage_scope,
                global_coverage_claimed=row.global_coverage_claimed,
                assumptions=_loads_list(row.assumptions_json),
                limitations=_loads_list(row.limitations_json),
                source_url=row.source_url,
            )
            for row in rows
        ]

    def vessel_history(
        self,
        *,
        vessel_id: str,
        start_at: str | None,
        end_at: str | None,
        cursor_after: str | None,
        limit: int,
    ) -> tuple[list[MarineReplayPathPoint], str | None]:
        query = select(MarinePositionEventORM).where(MarinePositionEventORM.vessel_id == vessel_id)
        if start_at:
            query = query.where(MarinePositionEventORM.observed_at >= start_at)
        if end_at:
            query = query.where(MarinePositionEventORM.observed_at <= end_at)
        if cursor_after:
            query = query.where(MarinePositionEventORM.observed_at > cursor_after)
        rows = self._session.execute(
            query.order_by(MarinePositionEventORM.observed_at.asc()).limit(limit + 1)
        ).scalars().all()
        next_cursor = rows[-1].observed_at if len(rows) > limit else None
        usable = rows[:limit]
        return [self._path_point_from_event(row) for row in usable], next_cursor

    def vessel_gaps(
        self,
        *,
        vessel_id: str,
        start_at: str | None,
        end_at: str | None,
        cursor_after: str | None,
        include_derived: bool,
        limit: int,
    ) -> tuple[list[MarineGapEvent], str | None]:
        query = select(MarineGapEventORM).where(MarineGapEventORM.vessel_id == vessel_id)
        if start_at:
            query = query.where(MarineGapEventORM.gap_start_observed_at >= start_at)
        if end_at:
            query = query.where(MarineGapEventORM.gap_start_observed_at <= end_at)
        if cursor_after:
            query = query.where(MarineGapEventORM.gap_start_observed_at > cursor_after)
        if not include_derived:
            query = query.where(MarineGapEventORM.event_kind != "possible-transponder-silence-interval")
        rows = self._session.execute(
            query.order_by(MarineGapEventORM.gap_start_observed_at.asc()).limit(limit + 1)
        ).scalars().all()
        next_cursor = rows[-1].gap_start_observed_at if len(rows) > limit else None
        usable = rows[:limit]
        return [self._gap_from_row(row) for row in usable], next_cursor

    def replay_timeline(
        self,
        *,
        start_at: str,
        end_at: str,
        cursor_after: str | None,
        limit: int,
    ) -> tuple[list[MarineReplayTimelineSegment], str | None]:
        rows = self._session.execute(
            select(MarineTimelineSegmentORM)
            .where(and_(MarineTimelineSegmentORM.segment_start_at >= start_at, MarineTimelineSegmentORM.segment_start_at <= end_at))
            .where(MarineTimelineSegmentORM.segment_start_at > (cursor_after or "0000-00-00T00:00:00+00:00"))
            .order_by(MarineTimelineSegmentORM.segment_start_at.asc())
            .limit(limit + 1)
        ).scalars().all()
        next_cursor = rows[-1].segment_start_at if len(rows) > limit else None
        usable = rows[:limit]
        return [
            MarineReplayTimelineSegment(
                segment_start_at=row.segment_start_at,
                segment_end_at=row.segment_end_at,
                scope_kind=row.scope_kind,
                vessel_count=row.vessel_count,
                position_event_count=row.position_event_count,
                gap_event_count=row.gap_event_count,
                snapshot_id=row.snapshot_id,
                chunk_id=row.chunk_id,
                metadata=_loads_dict(row.metadata_json),
            )
            for row in usable
        ], next_cursor
    def replay_snapshot(self, *, at_or_before: str, lamin: float | None, lamax: float | None, lomin: float | None, lomax: float | None) -> tuple[MarineReplaySnapshotRef | None, list[MarineVesselEntity]]:
        snapshot = self._session.execute(
            select(MarineReplaySnapshotORM)
            .where(MarineReplaySnapshotORM.scope_kind == "global")
            .where(MarineReplaySnapshotORM.snapshot_at <= at_or_before)
            .order_by(MarineReplaySnapshotORM.snapshot_at.desc())
            .limit(1)
        ).scalar_one_or_none()
        if snapshot is None:
            return None, []

        query = select(MarineReplaySnapshotMemberORM).where(MarineReplaySnapshotMemberORM.snapshot_id == snapshot.snapshot_id)
        if lamin is not None and lamax is not None:
            query = query.where(MarineReplaySnapshotMemberORM.latitude >= min(lamin, lamax)).where(MarineReplaySnapshotMemberORM.latitude <= max(lamin, lamax))
        if lomin is not None and lomax is not None:
            query = query.where(MarineReplaySnapshotMemberORM.longitude >= min(lomin, lomax)).where(MarineReplaySnapshotMemberORM.longitude <= max(lomin, lomax))
        members = self._session.execute(query).scalars().all()
        return (
            MarineReplaySnapshotRef(
                snapshot_id=snapshot.snapshot_id,
                snapshot_at=snapshot.snapshot_at,
                scope_kind=snapshot.scope_kind,
                vessel_count=snapshot.vessel_count,
                position_event_count=snapshot.position_event_count,
                storage_key=snapshot.storage_key,
                chunk_id=snapshot.chunk_id,
            ),
            [self._entity_from_snapshot_member(member) for member in members],
        )

    def replay_viewport(self, *, at_or_before: str, lamin: float, lamax: float, lomin: float, lomax: float, limit: int) -> list[MarineVesselEntity]:
        bounded = (
            select(
                MarinePositionEventORM.vessel_id.label("vessel_id"),
                func.max(MarinePositionEventORM.observed_at).label("observed_at"),
            )
            .where(MarinePositionEventORM.observed_at <= at_or_before)
            .where(MarinePositionEventORM.latitude >= min(lamin, lamax))
            .where(MarinePositionEventORM.latitude <= max(lamin, lamax))
            .where(MarinePositionEventORM.longitude >= min(lomin, lomax))
            .where(MarinePositionEventORM.longitude <= max(lomin, lomax))
            .group_by(MarinePositionEventORM.vessel_id)
            .subquery()
        )
        rows = self._session.execute(
            select(MarinePositionEventORM)
            .join(
                bounded,
                and_(
                    MarinePositionEventORM.vessel_id == bounded.c.vessel_id,
                    MarinePositionEventORM.observed_at == bounded.c.observed_at,
                ),
            )
            .order_by(MarinePositionEventORM.observed_at.desc())
            .limit(limit)
        ).scalars().all()
        return [self._entity_from_event(row) for row in rows]

    def vessel_path(
        self,
        *,
        vessel_id: str,
        start_at: str | None,
        end_at: str | None,
        cursor_after: str | None,
        include_interpolated: bool,
        limit: int,
    ) -> tuple[list[MarineReplayPathPoint], str | None]:
        points, next_cursor = self.vessel_history(
            vessel_id=vessel_id,
            start_at=start_at,
            end_at=end_at,
            cursor_after=cursor_after,
            limit=limit,
        )
        if not include_interpolated or len(points) < 2:
            return points, next_cursor
        enriched: list[MarineReplayPathPoint] = [points[0]]
        for previous, current in zip(points, points[1:]):
            prev_dt = _parse_iso(previous.observed_at)
            curr_dt = _parse_iso(current.observed_at)
            delta = int((curr_dt - prev_dt).total_seconds())
            if delta > 600:
                midpoint = prev_dt + timedelta(seconds=delta // 2)
                enriched.append(
                    MarineReplayPathPoint(
                        latitude=(previous.latitude + current.latitude) / 2.0,
                        longitude=(previous.longitude + current.longitude) / 2.0,
                        course=current.course,
                        heading=current.heading,
                        speed=current.speed,
                        observed_at=midpoint.isoformat(),
                        fetched_at=current.fetched_at,
                        source=current.source,
                        source_detail="interpolated between observed points",
                        observed_vs_derived="derived",
                        geometry_provenance="interpolated",
                        path_segment_kind="derived-interpolated-position",
                        confidence=max((previous.confidence or 0.0) * 0.7, (current.confidence or 0.0) * 0.7),
                        metadata={"interpolation": "linear-midpoint", "gapSeconds": delta},
                    )
                )
            enriched.append(current)
        return enriched, next_cursor

    def _entity_from_latest(self, row: MarineVesselLatestORM) -> MarineVesselEntity:
        return _entity_from_row(
            vessel_id=row.vessel_id,
            source=row.source_key,
            label=row.vessel_name or row.mmsi,
            latitude=row.latitude,
            longitude=row.longitude,
            heading=row.heading,
            speed=row.speed,
            observed_at=row.observed_at,
            fetched_at=row.fetched_at,
            status=row.status,
            source_detail=row.source_detail,
            external_url=row.external_url,
            confidence=row.confidence,
            mmsi=row.mmsi,
            imo=row.imo,
            callsign=row.callsign,
            vessel_name=row.vessel_name,
            flag_state=row.flag_state,
            vessel_class=row.vessel_class,
            course=row.course,
            nav_status=row.nav_status,
            destination=row.destination,
            eta=row.eta,
            observed_vs_derived=row.observed_vs_derived,
            geometry_provenance=row.geometry_provenance,
            source_health=row.source_health,
            stale=row.stale,
            degraded=row.degraded,
            degraded_reason=row.degraded_reason,
            reference_ref_id=row.reference_ref_id,
            quality_score=row.quality_score,
            quality_label=row.quality_label,
            quality_notes_json=row.quality_notes_json,
            metadata_json=row.metadata_json,
        )

    def _entity_from_event(self, row: MarinePositionEventORM) -> MarineVesselEntity:
        return _entity_from_row(
            vessel_id=row.vessel_id,
            source=row.source_key,
            label=row.vessel_name or row.mmsi,
            latitude=row.latitude,
            longitude=row.longitude,
            heading=row.heading,
            speed=row.speed,
            observed_at=row.observed_at,
            fetched_at=row.fetched_at,
            status=row.status,
            source_detail=row.source_detail,
            external_url=row.external_url,
            confidence=row.confidence,
            mmsi=row.mmsi,
            imo=row.imo,
            callsign=row.callsign,
            vessel_name=row.vessel_name,
            flag_state=row.flag_state,
            vessel_class=row.vessel_class,
            course=row.course,
            nav_status=row.nav_status,
            destination=row.destination,
            eta=row.eta,
            observed_vs_derived=row.observed_vs_derived,
            geometry_provenance=row.geometry_provenance,
            source_health="historical",
            stale=False,
            degraded=False,
            degraded_reason=None,
            reference_ref_id=None,
            quality_score=row.quality_score,
            quality_label=row.quality_label,
            quality_notes_json=row.quality_notes_json,
            metadata_json=row.metadata_json,
        )

    def _path_point_from_event(self, row: MarinePositionEventORM) -> MarineReplayPathPoint:
        return MarineReplayPathPoint(
            latitude=row.latitude,
            longitude=row.longitude,
            course=row.course,
            heading=row.heading,
            speed=row.speed,
            observed_at=row.observed_at,
            fetched_at=row.fetched_at,
            source=row.source_key,
            source_detail=row.source_detail,
            observed_vs_derived=row.observed_vs_derived,
            geometry_provenance=row.geometry_provenance,
            path_segment_kind=self._path_segment_kind(
                observed_vs_derived=row.observed_vs_derived,
                geometry_provenance=row.geometry_provenance,
            ),
            confidence=row.confidence,
            metadata=_loads_dict(row.metadata_json),
        )

    def _gap_from_row(self, row: MarineGapEventORM) -> MarineGapEvent:
        return MarineGapEvent(
            gap_event_id=row.gap_event_id,
            vessel_id=row.vessel_id,
            source=row.source_key,
            event_kind=row.event_kind,
            event_marker_type=self._event_marker_type(row.event_kind),
            gap_start_observed_at=row.gap_start_observed_at,
            gap_end_observed_at=row.gap_end_observed_at,
            gap_duration_seconds=row.gap_duration_seconds,
            start_latitude=row.start_latitude,
            start_longitude=row.start_longitude,
            end_latitude=row.end_latitude,
            end_longitude=row.end_longitude,
            distance_moved_m=row.distance_moved_m,
            expected_interval_seconds=row.expected_interval_seconds,
            exceeds_expected_cadence=row.exceeds_expected_cadence,
            confidence_class=row.confidence_class,
            confidence_display=self._confidence_display(
                row.confidence_class,
                bool(row.normal_sparse_reporting_plausible),
            ),
            confidence_score=row.confidence_score,
            normal_sparse_reporting_plausible=row.normal_sparse_reporting_plausible,
            confidence_breakdown=_loads_float_dict(row.confidence_breakdown_json),
            derivation_method=row.derivation_method,
            input_event_ids=_loads_int_list(row.input_event_ids_json),
            uncertainty_notes=_loads_list(row.uncertainty_notes_json),
            evidence_summary=row.evidence_summary,
            created_at=row.created_at,
        )

    def _event_marker_type(self, event_kind: str) -> str:
        if event_kind == "observed-signal-gap-start":
            return "gap-start"
        if event_kind == "observed-signal-gap-end":
            return "gap-end"
        if event_kind == "resumed-observation":
            return "resumed"
        return "possible-dark-interval"

    def _confidence_display(self, confidence_class: str, sparse_plausible: bool) -> str:
        base = {
            "high": "High confidence",
            "medium": "Medium confidence",
            "low": "Low confidence",
        }.get(confidence_class, "Low confidence")
        if sparse_plausible:
            return f"{base} (sparse reporting plausible)"
        return base

    def _path_segment_kind(self, observed_vs_derived: str, geometry_provenance: str) -> str:
        if observed_vs_derived == "observed":
            return "observed-position"
        if geometry_provenance == "interpolated":
            return "derived-interpolated-position"
        return "derived-reconstructed-position"
    def _entity_from_snapshot_member(self, row: MarineReplaySnapshotMemberORM) -> MarineVesselEntity:
        metadata = _loads_dict(row.metadata_json)
        return _entity_from_row(
            vessel_id=row.vessel_id,
            source=row.source_key,
            label=row.vessel_name or row.mmsi,
            latitude=row.latitude,
            longitude=row.longitude,
            heading=row.heading,
            speed=row.speed,
            observed_at=row.observed_at,
            fetched_at=row.fetched_at,
            status=row.status,
            source_detail="replay snapshot",
            external_url=None,
            confidence=row.confidence,
            mmsi=row.mmsi,
            imo=None,
            callsign=None,
            vessel_name=row.vessel_name,
            flag_state=metadata.get("flagState"),
            vessel_class=metadata.get("vesselClass"),
            course=row.course,
            nav_status=metadata.get("navStatus"),
            destination=metadata.get("destination"),
            eta=metadata.get("eta"),
            observed_vs_derived="observed",
            geometry_provenance=row.geometry_provenance,
            source_health="snapshot",
            stale=False,
            degraded=False,
            degraded_reason=None,
            reference_ref_id=metadata.get("referenceRefId"),
            quality_score=row.confidence,
            quality_label="snapshot",
            quality_notes_json="[]",
            metadata_json=row.metadata_json,
        )


def _entity_from_row(**kwargs: object) -> MarineVesselEntity:
    quality = MarineQualityMetadata(
        score=kwargs["quality_score"],
        label=kwargs["quality_label"],
        source_freshness_seconds=None,
        observed_vs_derived=kwargs["observed_vs_derived"],
        geometry_provenance=kwargs["geometry_provenance"],
        stale=kwargs["stale"],
        degraded=kwargs["degraded"],
        source_health=kwargs["source_health"],
        notes=_loads_list(kwargs["quality_notes_json"]),
    )
    return MarineVesselEntity(
        id=str(kwargs["vessel_id"]),
        type="marine-vessel",
        source=str(kwargs["source"]),
        label=str(kwargs["label"]),
        latitude=float(kwargs["latitude"]),
        longitude=float(kwargs["longitude"]),
        altitude=0.0,
        heading=kwargs["heading"],
        speed=kwargs["speed"],
        timestamp=str(kwargs["observed_at"]),
        observed_at=str(kwargs["observed_at"]),
        fetched_at=str(kwargs["fetched_at"]),
        status=str(kwargs["status"]),
        source_detail=kwargs["source_detail"],
        external_url=kwargs["external_url"],
        confidence=kwargs["confidence"],
        history_available=True,
        canonical_ids={"mmsi": str(kwargs["mmsi"]), "vesselId": str(kwargs["vessel_id"])},
        raw_identifiers={"imo": str(kwargs["imo"] or ""), "callsign": str(kwargs["callsign"] or "")},
        quality=quality,
        derived_fields=[],
        history_summary=None,
        link_targets=[],
        metadata=_loads_dict(kwargs["metadata_json"]),
        mmsi=str(kwargs["mmsi"]),
        imo=kwargs["imo"],
        callsign=kwargs["callsign"],
        vessel_name=kwargs["vessel_name"],
        flag_state=kwargs["flag_state"],
        vessel_class=kwargs["vessel_class"],
        course=kwargs["course"],
        nav_status=kwargs["nav_status"],
        destination=kwargs["destination"],
        eta=kwargs["eta"],
        stale=bool(kwargs["stale"]),
        degraded=bool(kwargs["degraded"]),
        degraded_reason=kwargs["degraded_reason"],
        source_health=kwargs["source_health"],
        observed_vs_derived=str(kwargs["observed_vs_derived"]),
        geometry_provenance=str(kwargs["geometry_provenance"]),
        reference_ref_id=kwargs["reference_ref_id"],
    )


def haversine_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius_m = 6_371_000.0
    lat1_rad = radians(lat1)
    lat2_rad = radians(lat2)
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2) ** 2
    return 2 * radius_m * asin(sqrt(a))


def _vessel_shard(vessel_id: str) -> int:
    return abs(hash(vessel_id)) % 256


def _loads_list(value: object) -> list[str]:
    if value is None:
        return []
    loaded = json.loads(str(value)) if isinstance(value, str) else value
    return [str(item) for item in loaded] if isinstance(loaded, list) else []


def _loads_int_list(value: str | None) -> list[int]:
    if not value:
        return []
    loaded = json.loads(value)
    if not isinstance(loaded, list):
        return []
    return [int(item) for item in loaded if isinstance(item, int) or (isinstance(item, str) and item.isdigit())]


def _loads_dict(value: object) -> dict[str, object]:
    if value is None:
        return {}
    loaded = json.loads(str(value)) if isinstance(value, str) else value
    return {str(k): v for k, v in loaded.items()} if isinstance(loaded, dict) else {}


def _loads_float_dict(value: object) -> dict[str, float]:
    raw = _loads_dict(value)
    parsed: dict[str, float] = {}
    for key, item in raw.items():
        try:
            parsed[key] = float(item)
        except (TypeError, ValueError):
            continue
    return parsed


def _parse_iso(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
