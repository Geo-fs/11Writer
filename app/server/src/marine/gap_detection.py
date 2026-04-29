from __future__ import annotations

from datetime import datetime, timezone

from src.marine.repository import GapEventInput, MarinePositionEventORM, haversine_meters


class MarineGapDetectionService:
    def expected_interval_seconds(self, *, speed: float | None, nav_status: str | None, cadence_floor: int) -> int:
        if nav_status in {"at-anchor", "moored"}:
            return max(cadence_floor, 600)
        if speed is None:
            return max(cadence_floor, 180)
        if speed < 1.0:
            return max(cadence_floor, 300)
        return max(cadence_floor, 120)

    def detect_gap_events(
        self,
        *,
        previous: MarinePositionEventORM,
        current: MarinePositionEventORM,
        source_health: str,
        cadence_floor_seconds: int,
    ) -> list[GapEventInput]:
        start_dt = _parse_iso(previous.observed_at)
        end_dt = _parse_iso(current.observed_at)
        duration = int((end_dt - start_dt).total_seconds())
        expected = self.expected_interval_seconds(
            speed=previous.speed,
            nav_status=previous.nav_status,
            cadence_floor=cadence_floor_seconds,
        )
        exceeds = duration > (expected * 2)
        if not exceeds:
            return []

        distance_m = haversine_meters(previous.latitude, previous.longitude, current.latitude, current.longitude)
        confidence_class, confidence_score, sparse_plausible, breakdown = _confidence(
            duration,
            expected,
            distance_m,
            source_health,
            previous.nav_status,
            previous.speed,
        )
        created_at = datetime.now(tz=timezone.utc).isoformat()
        summary = (
            f"Last observed at {previous.observed_at} ({previous.latitude:.4f},{previous.longitude:.4f}); "
            f"next observed at {current.observed_at} ({current.latitude:.4f},{current.longitude:.4f}); "
            f"gap duration {duration}s; exceeds expected cadence {expected}s."
        )
        uncertainty = [
            "Observed gap reflects missing observations, not direct proof of transponder operator intent.",
            f"Source health at detection: {source_health}",
        ]
        base_events = [
            GapEventInput(
                vessel_id=current.vessel_id,
                source_key=current.source_key,
                event_kind="observed-signal-gap-start",
                gap_start_observed_at=previous.observed_at,
                gap_end_observed_at=current.observed_at,
                gap_duration_seconds=duration,
                start_latitude=previous.latitude,
                start_longitude=previous.longitude,
                end_latitude=current.latitude,
                end_longitude=current.longitude,
                distance_moved_m=distance_m,
                expected_interval_seconds=expected,
                exceeds_expected_cadence=True,
                confidence_class=confidence_class,
                confidence_score=confidence_score,
                normal_sparse_reporting_plausible=sparse_plausible,
                confidence_breakdown=breakdown,
                derivation_method="first-pass-cadence-threshold",
                input_event_ids=[previous.event_id, current.event_id],
                uncertainty_notes=uncertainty,
                evidence_summary=summary,
                created_at=created_at,
            ),
            GapEventInput(
                vessel_id=current.vessel_id,
                source_key=current.source_key,
                event_kind="observed-signal-gap-end",
                gap_start_observed_at=previous.observed_at,
                gap_end_observed_at=current.observed_at,
                gap_duration_seconds=duration,
                start_latitude=previous.latitude,
                start_longitude=previous.longitude,
                end_latitude=current.latitude,
                end_longitude=current.longitude,
                distance_moved_m=distance_m,
                expected_interval_seconds=expected,
                exceeds_expected_cadence=True,
                confidence_class=confidence_class,
                confidence_score=confidence_score,
                normal_sparse_reporting_plausible=sparse_plausible,
                confidence_breakdown=breakdown,
                derivation_method="first-pass-cadence-threshold",
                input_event_ids=[previous.event_id, current.event_id],
                uncertainty_notes=uncertainty,
                evidence_summary=summary,
                created_at=created_at,
            ),
            GapEventInput(
                vessel_id=current.vessel_id,
                source_key=current.source_key,
                event_kind="resumed-observation",
                gap_start_observed_at=previous.observed_at,
                gap_end_observed_at=current.observed_at,
                gap_duration_seconds=duration,
                start_latitude=previous.latitude,
                start_longitude=previous.longitude,
                end_latitude=current.latitude,
                end_longitude=current.longitude,
                distance_moved_m=distance_m,
                expected_interval_seconds=expected,
                exceeds_expected_cadence=True,
                confidence_class=confidence_class,
                confidence_score=confidence_score,
                normal_sparse_reporting_plausible=sparse_plausible,
                confidence_breakdown=breakdown,
                derivation_method="first-pass-cadence-threshold",
                input_event_ids=[previous.event_id, current.event_id],
                uncertainty_notes=uncertainty,
                evidence_summary=summary,
                created_at=created_at,
            ),
        ]
        if duration > (expected * 4):
            base_events.append(
                GapEventInput(
                    vessel_id=current.vessel_id,
                    source_key=current.source_key,
                    event_kind="possible-transponder-silence-interval",
                    gap_start_observed_at=previous.observed_at,
                    gap_end_observed_at=current.observed_at,
                    gap_duration_seconds=duration,
                    start_latitude=previous.latitude,
                    start_longitude=previous.longitude,
                    end_latitude=current.latitude,
                    end_longitude=current.longitude,
                    distance_moved_m=distance_m,
                    expected_interval_seconds=expected,
                    exceeds_expected_cadence=True,
                    confidence_class=confidence_class,
                    confidence_score=confidence_score,
                    normal_sparse_reporting_plausible=sparse_plausible,
                    confidence_breakdown=breakdown,
                    derivation_method="derived-interpretation-from-observed-gap",
                    input_event_ids=[previous.event_id, current.event_id],
                    uncertainty_notes=uncertainty,
                    evidence_summary=summary,
                    created_at=created_at,
                )
            )
        return base_events


def _parse_iso(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def _confidence(
    duration: int,
    expected: int,
    distance_m: float,
    source_health: str,
    nav_status: str | None,
    speed: float | None,
) -> tuple[str, float, bool, dict[str, float]]:
    ratio = duration / max(expected, 1)
    duration_factor = min(1.0, ratio / 8.0)
    cadence_factor = min(1.0, max(0.0, (duration - expected) / max(expected * 6, 1)))
    distance_factor = min(1.0, distance_m / 300_000.0)
    freshness_penalty = 0.2 if source_health in {"degraded", "stale", "rate-limited"} else 0.0
    sparse_plausible = bool(
        nav_status in {"at-anchor", "moored"} or (speed is not None and speed < 0.8 and distance_m < 2000.0)
    )
    sparse_penalty = 0.2 if sparse_plausible else 0.0
    score = min(
        1.0,
        max(
            0.05,
            0.15 + (duration_factor * 0.35) + (cadence_factor * 0.25) + (distance_factor * 0.25) - freshness_penalty - sparse_penalty,
        ),
    )
    breakdown = {
        "duration_factor": round(duration_factor, 4),
        "cadence_factor": round(cadence_factor, 4),
        "distance_factor": round(distance_factor, 4),
        "freshness_penalty": round(freshness_penalty, 4),
        "sparse_reporting_penalty": round(sparse_penalty, 4),
        "score": round(score, 4),
    }
    if score >= 0.75:
        return "high", round(score, 3), sparse_plausible, breakdown
    if score >= 0.45:
        return "medium", round(score, 3), sparse_plausible, breakdown
    return "low", round(score, 3), sparse_plausible, breakdown
