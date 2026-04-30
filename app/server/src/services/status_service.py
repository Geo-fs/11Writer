from __future__ import annotations

from datetime import datetime, timezone

from src.config.settings import Settings
from src.services.camera_registry import build_camera_source_registry
from src.services.source_registry import get_source_runtime_status
from src.types.api import SourceStatus, SourceStatusResponse
from src.webcam.db import session_scope
from src.webcam.repository import WebcamRepository


def build_source_status(settings: Settings) -> SourceStatusResponse:
    google_enabled = bool(settings.google_maps_api_key)
    aircraft_runtime = get_source_runtime_status("opensky-network")
    opensky_anonymous_runtime = get_source_runtime_status("opensky-anonymous-states")
    satellite_runtime = get_source_runtime_status("celestrak-active")
    aviation_weather_runtime = get_source_runtime_status("noaa-awc")
    faa_nas_runtime = get_source_runtime_status("faa-nas-status")
    cneos_runtime = get_source_runtime_status("cneos-space-events")
    swpc_runtime = get_source_runtime_status("noaa-swpc")
    anchorage_vaac_runtime = get_source_runtime_status("anchorage-vaac-advisories")
    tokyo_vaac_runtime = get_source_runtime_status("tokyo-vaac-advisories")
    washington_vaac_runtime = get_source_runtime_status("washington-vaac-advisories")
    marine_runtime = get_source_runtime_status("ais-fixture-global")
    persisted_camera_sources = _camera_source_map(settings)

    sources = [
        SourceStatus(
            name="terrain",
            state="healthy",
            enabled=True,
            healthy=True,
            freshness_seconds=None,
            stale_after_seconds=None,
            last_success_at=None,
            degraded_reason=None,
            rate_limited=False,
            hidden_reason=None,
            detail="Client-side Cesium terrain and imagery are available.",
        ),
        SourceStatus(
            name="google-photorealistic-3d",
            state="healthy" if google_enabled else "disabled",
            enabled=google_enabled,
            healthy=google_enabled,
            freshness_seconds=None,
            stale_after_seconds=None,
            last_success_at=None,
            degraded_reason=None if google_enabled else "Google tiles are not configured.",
            rate_limited=False,
            hidden_reason=None if google_enabled else "disabled-by-configuration",
            detail=(
                "Google API key detected for the primary city layer."
                if google_enabled
                else "Enable GOOGLE_MAPS_API_KEY to activate the primary city layer."
            ),
            credentials_configured=google_enabled,
        ),
        _runtime_to_status(
            name="aircraft",
            runtime=aircraft_runtime,
            default_freshness=15,
            default_stale_after=120,
            detail="OpenSky-backed aircraft endpoint is available for bounded polling and attribution.",
        ),
        _runtime_to_status(
            name="opensky-anonymous-states",
            runtime=opensky_anonymous_runtime,
            default_freshness=60,
            default_stale_after=300,
            detail="Optional OpenSky anonymous state-vector context is available for selected-aircraft source review; coverage is rate-limited and not guaranteed complete.",
        ),
        _runtime_to_status(
            name="satellites",
            runtime=satellite_runtime,
            default_freshness=900,
            default_stale_after=43_200,
            detail="CelesTrak-backed satellite catalog and orbit traces are available for OSINT context.",
        ),
        _runtime_to_status(
            name="noaa-awc",
            runtime=aviation_weather_runtime,
            default_freshness=300,
            default_stale_after=1_800,
            detail="NOAA AWC METAR/TAF airport context is available for selected-target aviation weather evidence.",
        ),
        _runtime_to_status(
            name="faa-nas-status",
            runtime=faa_nas_runtime,
            default_freshness=60,
            default_stale_after=300,
            detail="FAA NAS airport-status context is available for selected-target airport operational advisories.",
        ),
        _runtime_to_status(
            name="cneos-space-events",
            runtime=cneos_runtime,
            default_freshness=3_600,
            default_stale_after=86_400,
            detail="NASA/JPL CNEOS close-approach and fireball context is available for selected-target space-event review.",
        ),
        _runtime_to_status(
            name="noaa-swpc",
            runtime=swpc_runtime,
            default_freshness=1_800,
            default_stale_after=21_600,
            detail="NOAA SWPC space-weather advisory context is available for selected-target aerospace situational awareness.",
        ),
        _runtime_to_status(
            name="anchorage-vaac-advisories",
            runtime=anchorage_vaac_runtime,
            default_freshness=1_800,
            default_stale_after=21_600,
            detail="Anchorage VAAC volcanic-ash advisories are available as advisory/contextual aerospace hazard context and do not by themselves determine route impact or aircraft exposure.",
        ),
        _runtime_to_status(
            name="tokyo-vaac-advisories",
            runtime=tokyo_vaac_runtime,
            default_freshness=1_800,
            default_stale_after=21_600,
            detail="Tokyo VAAC volcanic-ash advisories are available as advisory/contextual aerospace hazard context and do not by themselves determine route impact or aircraft exposure.",
        ),
        _runtime_to_status(
            name="washington-vaac-advisories",
            runtime=washington_vaac_runtime,
            default_freshness=1_800,
            default_stale_after=21_600,
            detail="Washington VAAC volcanic-ash advisories are available as advisory/contextual aerospace hazard context and do not by themselves determine route impact or aircraft exposure.",
        ),
        _runtime_to_status(
            name="marine",
            runtime=marine_runtime,
            default_freshness=60,
            default_stale_after=240,
            detail="Marine AIS evidence layer supports observed vessel tracking, gap detection, and replay.",
        ),
    ]
    for camera_source in build_camera_source_registry(settings):
        persisted = persisted_camera_sources.get(camera_source.key)
        sources.append(
            _camera_source_to_status(
                persisted or camera_source,
                fallback_detail=(
                    f"{camera_source.display_name} camera feed is configured."
                    if camera_source.enabled
                    else f"{camera_source.display_name} requires {camera_source.authentication} configuration."
                ),
            )
        )
    return SourceStatusResponse(sources=sources)


def _camera_source_map(settings: Settings) -> dict[str, object]:
    try:
        with session_scope(settings.camera_database_url) as session:
            return {source.key: source for source in WebcamRepository(session).list_sources()}
    except Exception:
        return {}


def _camera_source_to_status(source, *, fallback_detail: str) -> SourceStatus:
    state = source.status
    cadence_seconds = source.cadence_seconds or source.default_refresh_interval_seconds
    stale_after_seconds = cadence_seconds * 3
    if state in {"healthy", "needs-review", "degraded"} and source.last_success_at:
        elapsed = int((datetime.now(tz=timezone.utc) - _parse_iso(source.last_success_at)).total_seconds())
        if elapsed > stale_after_seconds:
            state = "stale"
    return SourceStatus(
        name=source.key,
        state=state,
        enabled=source.enabled,
        healthy=state == "healthy",
        freshness_seconds=cadence_seconds,
        stale_after_seconds=stale_after_seconds,
        last_success_at=source.last_success_at,
        degraded_reason=source.degraded_reason,
        rate_limited=state == "rate-limited",
        hidden_reason="disabled-by-configuration" if not source.enabled else None,
        detail=source.detail or fallback_detail,
        credentials_configured=source.credentials_configured,
        blocked_reason=source.blocked_reason,
        review_required=source.review_required,
        last_attempt_at=source.last_attempt_at,
        last_failure_at=source.last_failure_at,
        success_count=source.success_count,
        failure_count=source.failure_count,
        warning_count=source.warning_count,
        next_refresh_at=source.next_refresh_at,
        backoff_until=source.backoff_until,
        retry_count=source.retry_count,
        last_http_status=source.last_http_status,
        last_started_at=source.last_started_at,
        last_completed_at=source.last_completed_at,
        cadence_seconds=source.cadence_seconds,
        cadence_reason=source.cadence_reason,
        last_run_mode=source.last_run_mode,
        last_validation_at=source.last_validation_at,
        last_frame_probe_count=source.last_frame_probe_count,
        last_frame_status_summary=source.last_frame_status_summary,
        last_metadata_uncertainty_count=source.last_metadata_uncertainty_count,
        last_cadence_observation=source.last_cadence_observation,
    )


def _runtime_to_status(
    *,
    name: str,
    runtime,
    default_freshness: int,
    default_stale_after: int,
    detail: str,
) -> SourceStatus:
    if runtime is None:
        return SourceStatus(
            name=name,
            state="never-fetched",
            enabled=True,
            healthy=False,
            freshness_seconds=default_freshness,
            stale_after_seconds=default_stale_after,
            last_success_at=None,
            degraded_reason=None,
            rate_limited=False,
            hidden_reason=None,
            detail=f"{detail} No successful fetch has been recorded yet.",
        )

    state = runtime.state
    if state == "healthy" and runtime.last_success_at and runtime.stale_after_seconds is not None:
        elapsed = int((datetime.now(tz=timezone.utc) - _parse_iso(runtime.last_success_at)).total_seconds())
        if elapsed > runtime.stale_after_seconds:
            state = "stale"

    return SourceStatus(
        name=name,
        state=state,
        enabled=state != "disabled",
        healthy=state == "healthy",
        freshness_seconds=runtime.freshness_seconds if runtime.freshness_seconds is not None else default_freshness,
        stale_after_seconds=runtime.stale_after_seconds if runtime.stale_after_seconds is not None else default_stale_after,
        last_success_at=runtime.last_success_at,
        degraded_reason=runtime.degraded_reason,
        rate_limited=runtime.rate_limited,
        hidden_reason=runtime.hidden_reason,
        detail=detail,
        credentials_configured=runtime.credentials_configured,
        blocked_reason=runtime.blocked_reason,
        review_required=runtime.review_required,
        last_attempt_at=runtime.last_attempt_at,
        last_failure_at=runtime.last_failure_at,
        success_count=runtime.success_count,
        failure_count=runtime.failure_count,
        warning_count=runtime.warning_count,
        next_refresh_at=None,
        backoff_until=None,
        retry_count=None,
        last_http_status=None,
        last_started_at=None,
        last_completed_at=None,
        cadence_seconds=runtime.freshness_seconds,
        cadence_reason="runtime registry freshness cadence",
    )


def _parse_iso(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
