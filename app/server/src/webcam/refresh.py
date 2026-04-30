from __future__ import annotations

import asyncio
import logging
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from hashlib import sha1
from typing import Awaitable, Callable

import httpx

from src.adapters.cameras import CameraConnector, CameraSourceFetchResult, build_camera_connectors
from src.config.settings import Settings
from src.services.camera_registry import (
    RefreshPolicy,
    build_camera_source_inventory,
    build_camera_source_registry,
    get_refresh_policy,
    is_camera_source_sandbox_importable,
)
from src.services.source_registry import record_source_failure, record_source_success
from src.types.api import CameraSourceRegistryEntry, ReviewQueueIssue, ReviewQueueItem
from src.types.entities import CameraEntity
from src.webcam.db import session_scope
from src.webcam.repository import (
    CameraFrameUpdate,
    PersistedSourceUpdate,
    SourceInventoryRunRecord,
    SourceRunRecord,
    WebcamRepository,
)

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class FrameProbeResult:
    status: str
    fetched_at: str
    captured_at: str | None
    width: int | None
    height: int | None
    http_status: int | None
    frame_hash: str | None
    degraded_reason: str | None
    blocked_reason: str | None
    retry_count: int
    backoff_until: str | None


@dataclass(frozen=True)
class RefreshCycleResult:
    refreshed_sources: int
    refreshed_frames: int


@dataclass(frozen=True)
class SourceRefreshOutcome:
    source_key: str
    started_at: str
    completed_at: str | None
    status: str
    camera_count: int
    normalized_count: int
    partial_failure_count: int
    warning_count: int
    http_status: int | None
    error_text: str | None


@dataclass(frozen=True)
class FrameRefreshSummary:
    refreshed_frames: int
    frame_probe_count: int
    status_counts: dict[str, int]


class WebcamWorker:
    def __init__(self, refresh_service: WebcamRefreshService, *, poll_seconds: int) -> None:
        self._refresh_service = refresh_service
        self._poll_seconds = poll_seconds

    async def run_once(self) -> RefreshCycleResult:
        return await self._refresh_service.run_due_work()

    async def run_live_validation(
        self,
        *,
        source_keys: list[str] | None = None,
        include_blocked: bool = False,
    ) -> RefreshCycleResult:
        return await self._refresh_service.run_live_validation(
            source_keys=source_keys,
            include_blocked=include_blocked,
        )

    async def run_loop(self, *, stop_event: asyncio.Event | None = None) -> None:
        while True:
            await self.run_once()
            if stop_event is None:
                await asyncio.sleep(self._poll_seconds)
                continue
            try:
                await asyncio.wait_for(stop_event.wait(), timeout=self._poll_seconds)
                break
            except asyncio.TimeoutError:
                continue


class WebcamRefreshService:
    def __init__(
        self,
        settings: Settings,
        *,
        connectors: list[CameraConnector] | None = None,
        frame_probe: Callable[[CameraEntity, RefreshPolicy], Awaitable[FrameProbeResult]] | None = None,
    ) -> None:
        connector_list = connectors if connectors is not None else build_camera_connectors(settings)
        self._settings = settings
        self._connectors = {connector.source_name: connector for connector in connector_list}
        self._database_url = settings.camera_database_url
        self._frame_probe = frame_probe or self._probe_frame

    async def bootstrap_sources(self) -> None:
        await self.bootstrap_inventory()
        source_definitions = build_camera_source_registry(self._settings)
        with session_scope(self._database_url) as session:
            repository = WebcamRepository(session)
            existing = {source.key: source for source in repository.list_sources()}
            now = _now_iso()
            for source in source_definitions:
                sandbox_importable = is_camera_source_sandbox_importable(source.key, self._settings)
                if source.onboarding_state not in {"approved", "active"} and not sandbox_importable:
                    continue
                policy = get_refresh_policy(source.key)
                if policy is None:
                    continue
                previous = existing.get(source.key)
                persisted = source if previous is None else previous.model_copy(
                    update={
                        "display_name": source.display_name,
                        "owner": source.owner,
                        "source_type": source.source_type,
                        "coverage": source.coverage,
                        "priority": source.priority,
                        "enabled": source.enabled,
                        "authentication": source.authentication,
                        "default_refresh_interval_seconds": source.default_refresh_interval_seconds,
                        "notes": source.notes,
                        "compliance": source.compliance,
                        "credentials_configured": source.credentials_configured,
                        "cadence_seconds": policy.catalog_refresh_seconds,
                        "cadence_reason": "source policy catalog refresh cadence",
                    }
                )
                next_refresh_at = previous.next_refresh_at if previous is not None else (
                    now if source.credentials_configured else None
                )
                repository.upsert_source(
                    PersistedSourceUpdate(
                        source=persisted,
                        detail=previous.detail if previous is not None else source.detail,
                        credentials_configured=source.credentials_configured,
                        blocked_reason=previous.blocked_reason if previous is not None else source.blocked_reason,
                        degraded_reason=previous.degraded_reason if previous is not None else source.degraded_reason,
                        last_attempt_at=previous.last_attempt_at if previous is not None else source.last_attempt_at,
                        last_success_at=previous.last_success_at if previous is not None else source.last_success_at,
                        last_failure_at=previous.last_failure_at if previous is not None else source.last_failure_at,
                        success_count=previous.success_count if previous is not None else source.success_count,
                        failure_count=previous.failure_count if previous is not None else source.failure_count,
                        warning_count=previous.warning_count if previous is not None else source.warning_count,
                        last_camera_count=previous.last_camera_count if previous is not None else source.last_camera_count,
                        next_refresh_at=next_refresh_at,
                        backoff_until=previous.backoff_until if previous is not None else None,
                        retry_count=previous.retry_count if previous is not None else 0,
                        last_http_status=previous.last_http_status if previous is not None else None,
                        last_started_at=previous.last_started_at if previous is not None else None,
                        last_completed_at=previous.last_completed_at if previous is not None else None,
                        cadence_seconds=policy.catalog_refresh_seconds,
                        cadence_reason="source policy catalog refresh cadence",
                    )
                )

    async def bootstrap_inventory(self) -> None:
        inventory_entries = build_camera_source_inventory(self._settings)
        with session_scope(self._database_url) as session:
            repository = WebcamRepository(session)
            for entry in inventory_entries:
                repository.upsert_source_inventory(entry)

    async def run_due_work(
        self,
        *,
        max_sources: int | None = None,
        max_frames: int | None = None,
        run_mode: str = "scheduled",
    ) -> RefreshCycleResult:
        await self.bootstrap_sources()
        refreshed_sources = await self.refresh_due_sources(max_sources=max_sources, run_mode=run_mode)
        refreshed_frames = await self.refresh_due_frames(max_frames=max_frames, run_mode=run_mode)
        return RefreshCycleResult(refreshed_sources=refreshed_sources, refreshed_frames=refreshed_frames)

    async def run_live_validation(
        self,
        *,
        source_keys: list[str] | None = None,
        include_blocked: bool = False,
    ) -> RefreshCycleResult:
        await self.bootstrap_sources()
        with session_scope(self._database_url) as session:
            repository = WebcamRepository(session)
            all_sources = repository.list_sources()

        selected_sources = _select_validation_sources(
            all_sources,
            source_keys=source_keys,
            include_blocked=include_blocked,
        )
        refreshed_sources = 0
        refreshed_frames = 0
        if not selected_sources:
            logger.info("webcam.validation.no_sources", extra={"selected_sources": source_keys or []})
            return RefreshCycleResult(refreshed_sources=0, refreshed_frames=0)

        for source in selected_sources:
            outcome = await self.refresh_source(source.key, run_mode="validation")
            if outcome is None:
                continue
            refreshed_sources += 1
            frame_summary = await self.refresh_frames_for_source(source.key, run_mode="validation")
            refreshed_frames += frame_summary.refreshed_frames
            with session_scope(self._database_url) as session:
                repository = WebcamRepository(session)
                repository.update_source_run_summary(
                    source_key=source.key,
                    started_at=outcome.started_at,
                    run_mode="validation",
                    frame_probe_count=frame_summary.frame_probe_count,
                    frame_status_counts=frame_summary.status_counts,
                    metadata_uncertainty_count=_metadata_uncertainty_count(repository.list_cameras(), source.key),
                    cadence_observation=_cadence_observation(source.key, outcome.status, frame_summary),
                )
            logger.info(
                "webcam.validation.completed",
                extra={
                    "source_key": source.key,
                    "status": outcome.status,
                    "frame_probe_count": frame_summary.frame_probe_count,
                    "frame_status_counts": frame_summary.status_counts,
                },
            )
        return RefreshCycleResult(refreshed_sources=refreshed_sources, refreshed_frames=refreshed_frames)

    async def refresh_due_sources(self, *, max_sources: int | None = None, run_mode: str = "scheduled") -> int:
        with session_scope(self._database_url) as session:
            sources = WebcamRepository(session).list_sources()
        due_sources = [source for source in sources if _source_is_due(source)]
        refreshed = 0
        for source in due_sources[: max_sources or len(due_sources)]:
            await self.refresh_source(source.key, run_mode=run_mode)
            refreshed += 1
        return refreshed

    async def refresh_due_frames(
        self,
        *,
        max_frames: int | None = None,
        run_mode: str = "scheduled",
        source_keys: set[str] | None = None,
    ) -> int:
        summary = await self._refresh_due_frames_internal(
            max_frames=max_frames,
            run_mode=run_mode,
            source_keys=source_keys,
        )
        return summary.refreshed_frames

    async def refresh_frames_for_source(self, source_key: str, *, run_mode: str = "scheduled") -> FrameRefreshSummary:
        return await self._refresh_due_frames_internal(
            run_mode=run_mode,
            source_keys={source_key},
        )

    async def _refresh_due_frames_internal(
        self,
        *,
        max_frames: int | None = None,
        run_mode: str = "scheduled",
        source_keys: set[str] | None = None,
    ) -> FrameRefreshSummary:
        with session_scope(self._database_url) as session:
            repository = WebcamRepository(session)
            cameras = repository.list_cameras()
            sources = {source.key: source for source in repository.list_sources()}
        refreshed = 0
        direct_frame_probes = 0
        statuses: Counter[str] = Counter()
        for camera in cameras:
            if max_frames is not None and refreshed >= max_frames:
                break
            if source_keys is not None and camera.source not in source_keys:
                continue
            source = sources.get(camera.source)
            policy = get_refresh_policy(camera.source)
            if source is None or policy is None:
                continue
            if not _camera_frame_is_due(camera, source, policy):
                continue
            result = await self.refresh_camera_frame(camera, source, policy, run_mode=run_mode)
            refreshed += 1
            statuses[result.status] += 1
            if camera.frame.image_url and policy.supports_direct_frame_refresh:
                direct_frame_probes += 1
        return FrameRefreshSummary(
            refreshed_frames=refreshed,
            frame_probe_count=direct_frame_probes,
            status_counts=dict(statuses),
        )

    async def refresh_source(self, source_key: str, *, run_mode: str = "scheduled") -> SourceRefreshOutcome | None:
        with session_scope(self._database_url) as session:
            repository = WebcamRepository(session)
            sources = {source.key: source for source in repository.list_sources()}
        source = sources.get(source_key)
        connector = self._connectors.get(source_key)
        policy = get_refresh_policy(source_key)
        if source is None or connector is None or policy is None:
            return None

        started_at = _now_iso()
        if not source.credentials_configured:
            return await self._persist_source_exception(
                source,
                RuntimeError("Credentials are missing for this source."),
                started_at=started_at,
                policy=policy,
                forced_state="credentials-missing",
                run_mode=run_mode,
            )

        claimed = source.model_copy(update={"last_started_at": started_at, "detail": f"{source.display_name} refresh started."})
        with session_scope(self._database_url) as session:
            WebcamRepository(session).upsert_source(_persisted_source_update(claimed, policy))

        try:
            result = await connector.fetch()
        except Exception as exc:
            return await self._persist_source_exception(
                source,
                exc,
                started_at=started_at,
                policy=policy,
                run_mode=run_mode,
            )
        return await self._persist_fetch_result(
            source,
            result,
            started_at=started_at,
            policy=policy,
            run_mode=run_mode,
        )

    async def refresh_camera_frame(
        self,
        camera: CameraEntity,
        source: CameraSourceRegistryEntry,
        policy: RefreshPolicy,
        *,
        run_mode: str = "scheduled",
    ) -> FrameProbeResult:
        if camera.frame.image_url and policy.supports_direct_frame_refresh:
            result = await self._frame_probe(camera, policy)
        else:
            result = FrameProbeResult(
                status="viewer-page-only" if camera.frame.viewer_url else camera.frame.status,
                fetched_at=_now_iso(),
                captured_at=camera.frame.last_frame_at,
                width=camera.frame.width,
                height=camera.frame.height,
                http_status=None,
                frame_hash=None,
                degraded_reason=(
                    "Viewer fallback only; direct frame refresh is not available."
                    if camera.frame.viewer_url
                    else camera.degraded_reason or "Direct frame refresh is unavailable."
                ),
                blocked_reason=None,
                retry_count=0,
                backoff_until=None,
            )

        next_refresh_at = _next_frame_refresh_at(camera, policy, result.fetched_at, result.status)
        health_state = _camera_health_state(camera, result.status)
        with session_scope(self._database_url) as session:
            repository = WebcamRepository(session)
            repository.update_camera_frame_metadata(
                CameraFrameUpdate(
                    camera_id=camera.id,
                    fetched_at=result.fetched_at,
                    captured_at=result.captured_at,
                    source_frame_url=camera.frame.image_url or camera.frame.viewer_url,
                    frame_hash=result.frame_hash,
                    status=result.status,
                    width=result.width,
                    height=result.height,
                    age_seconds=0 if result.status == "live" else camera.frame.age_seconds,
                    health_state=health_state,
                    degraded_reason=result.degraded_reason,
                    blocked_reason=result.blocked_reason,
                    next_frame_refresh_at=next_refresh_at,
                    backoff_until=result.backoff_until,
                    retry_count=result.retry_count,
                    last_http_status=result.http_status,
                    last_metadata_refresh_at=result.fetched_at,
                )
            )
            current_source = {item.key: item for item in repository.list_sources()}.get(source.key, source)
            repository.upsert_source(_persisted_source_update(_update_source_after_frame(current_source, policy, probe=result), policy))
        logger.info(
            "webcam.frame_refresh",
            extra={
                "source_key": source.key,
                "camera_id": camera.id,
                "run_mode": run_mode,
                "status": result.status,
                "http_status": result.http_status,
            },
        )
        return result

    async def _persist_fetch_result(
        self,
        source: CameraSourceRegistryEntry,
        result: CameraSourceFetchResult,
        *,
        started_at: str,
        policy: RefreshPolicy,
        run_mode: str,
    ) -> SourceRefreshOutcome:
        normalized_cameras = [_camera_with_schedule(camera, policy, result.fetched_at) for camera in result.cameras]
        next_source = _update_source_after_fetch(source, result, started_at, policy)
        _record_runtime_status(source.key, next_source)
        with session_scope(self._database_url) as session:
            repository = WebcamRepository(session)
            repository.upsert_source(_persisted_source_update(next_source, policy))
            repository.upsert_source_inventory(_inventory_entry_for_source(self._settings, source.key, result))
            repository.replace_cameras_for_source(
                source.key,
                normalized_cameras,
                fetched_at=result.fetched_at,
                last_attempt_at=result.fetched_at,
                last_success_at=next_source.last_success_at,
                stale_after_seconds=policy.catalog_refresh_seconds * 3,
            )
            repository.replace_review_queue(build_review_items(repository.list_cameras()))
            repository.record_source_run(
                SourceRunRecord(
                    source_key=source.key,
                    started_at=started_at,
                    completed_at=result.fetched_at,
                    run_mode=run_mode,
                    status=result.status,
                    camera_count=result.total_records,
                    normalized_count=result.normalized_records,
                    partial_failure_count=result.partial_failure_count,
                    warning_count=len(result.warnings),
                    http_status=result.last_http_status,
                    error_text=result.degraded_reason,
                    metadata_uncertainty_count=_metadata_uncertainty_count(normalized_cameras, source.key),
                    cadence_observation=_cadence_observation(source.key, result.status, None),
                )
            )
            repository.record_source_inventory_run(
                SourceInventoryRunRecord(
                    source_key=source.key,
                    started_at=started_at,
                    completed_at=result.fetched_at,
                    status=result.status,
                    discovered_camera_count=result.total_records,
                    imported_camera_count=result.normalized_records,
                    detail=result.detail,
                )
            )
        logger.info(
            "webcam.source_refresh",
            extra={
                "source_key": source.key,
                "run_mode": run_mode,
                "status": result.status,
                "http_status": result.last_http_status,
                "normalized_count": result.normalized_records,
                "partial_failure_count": result.partial_failure_count,
            },
        )
        return SourceRefreshOutcome(
            source_key=source.key,
            started_at=started_at,
            completed_at=result.fetched_at,
            status=result.status,
            camera_count=result.total_records,
            normalized_count=result.normalized_records,
            partial_failure_count=result.partial_failure_count,
            warning_count=len(result.warnings),
            http_status=result.last_http_status,
            error_text=result.degraded_reason,
        )

    async def _persist_source_exception(
        self,
        source: CameraSourceRegistryEntry,
        exc: Exception,
        *,
        started_at: str,
        policy: RefreshPolicy,
        forced_state: str | None = None,
        run_mode: str,
    ) -> SourceRefreshOutcome:
        message = str(exc)
        next_source = _update_source_after_exception(
            source,
            message,
            started_at=started_at,
            policy=policy,
            forced_state=forced_state,
        )
        _record_runtime_status(source.key, next_source)
        with session_scope(self._database_url) as session:
            repository = WebcamRepository(session)
            repository.upsert_source(_persisted_source_update(next_source, policy))
            repository.upsert_source_inventory(_inventory_entry_for_exception(self._settings, source.key, next_source))
            repository.record_source_run(
                SourceRunRecord(
                    source_key=source.key,
                    started_at=started_at,
                    completed_at=next_source.last_completed_at,
                    run_mode=run_mode,
                    status=next_source.status,
                    camera_count=0,
                    normalized_count=0,
                    partial_failure_count=0,
                    warning_count=0,
                    http_status=next_source.last_http_status,
                    error_text=message,
                    cadence_observation=_cadence_observation(source.key, next_source.status, None),
                )
            )
            repository.record_source_inventory_run(
                SourceInventoryRunRecord(
                    source_key=source.key,
                    started_at=started_at,
                    completed_at=next_source.last_completed_at,
                    status=next_source.status,
                    discovered_camera_count=0,
                    imported_camera_count=0,
                    detail=message,
                )
            )
        logger.info(
            "webcam.source_refresh_failed",
            extra={
                "source_key": source.key,
                "run_mode": run_mode,
                "status": next_source.status,
                "http_status": next_source.last_http_status,
                "error_text": message,
            },
        )
        return SourceRefreshOutcome(
            source_key=source.key,
            started_at=started_at,
            completed_at=next_source.last_completed_at,
            status=next_source.status,
            camera_count=0,
            normalized_count=0,
            partial_failure_count=0,
            warning_count=0,
            http_status=next_source.last_http_status,
            error_text=message,
        )

    async def _probe_frame(self, camera: CameraEntity, policy: RefreshPolicy) -> FrameProbeResult:
        fetched_at = _now_iso()
        image_url = camera.frame.image_url
        if not image_url:
            return FrameProbeResult(
                status="unavailable",
                fetched_at=fetched_at,
                captured_at=camera.frame.last_frame_at,
                width=camera.frame.width,
                height=camera.frame.height,
                http_status=None,
                frame_hash=None,
                degraded_reason="No direct image URL is available for this camera.",
                blocked_reason=None,
                retry_count=(camera.retry_count or 0) + 1,
                backoff_until=None,
            )

        async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
            response = await client.get(image_url)

        retry_count = 0
        backoff_until = None
        degraded_reason = None
        blocked_reason = None
        status = "live"
        if response.status_code == 429:
            status = "stale"
            retry_count = (camera.retry_count or 0) + 1
            backoff_until = _compute_backoff_iso(fetched_at, retry_count, policy)
            degraded_reason = "Upstream source rate-limited frame refresh requests."
        elif response.status_code in {401, 403}:
            status = "blocked"
            retry_count = (camera.retry_count or 0) + 1
            backoff_until = _compute_backoff_iso(fetched_at, retry_count, policy)
            blocked_reason = "Frame access blocked by upstream authentication or terms."
            degraded_reason = blocked_reason
        elif response.status_code >= 400:
            status = "stale"
            retry_count = (camera.retry_count or 0) + 1
            degraded_reason = f"Frame refresh returned HTTP {response.status_code}."
        elif not str(response.headers.get("content-type", "")).lower().startswith("image/"):
            status = "unavailable"
            retry_count = (camera.retry_count or 0) + 1
            degraded_reason = "Frame refresh did not return an image payload."

        frame_hash = sha1(response.content).hexdigest()[:16] if status == "live" else None
        return FrameProbeResult(
            status=status,
            fetched_at=fetched_at,
            captured_at=fetched_at if status == "live" else camera.frame.last_frame_at,
            width=camera.frame.width,
            height=camera.frame.height,
            http_status=response.status_code,
            frame_hash=frame_hash,
            degraded_reason=degraded_reason,
            blocked_reason=blocked_reason,
            retry_count=retry_count,
            backoff_until=backoff_until,
        )


def build_review_items(cameras: list[CameraEntity]) -> list[ReviewQueueItem]:
    items: list[ReviewQueueItem] = []
    for camera in cameras:
        issues = [
            ReviewQueueIssue(category=category, reason=reason, required_action=action)
            for category, reason, action in zip(
                camera.review.issue_categories,
                [camera.review.reason or category for category in camera.review.issue_categories],
                camera.review.required_actions,
                strict=False,
            )
        ]
        if not issues and camera.review.status == "verified":
            continue
        if not issues:
            issues = [
                ReviewQueueIssue(
                    category="review",
                    reason=camera.review.reason or "Camera metadata requires review.",
                    required_action="Verify camera metadata and compliance notes.",
                )
            ]
        items.append(
            ReviewQueueItem(
                queue_id=f"review:{camera.id}",
                priority=_review_priority(camera),
                source_key=camera.source,
                camera=camera,
                issues=issues,
                context=_review_context(camera),
            )
        )
    items.sort(key=_review_sort_key)
    return items


def _persisted_source_update(source: CameraSourceRegistryEntry, policy: RefreshPolicy) -> PersistedSourceUpdate:
    return PersistedSourceUpdate(
        source=source,
        detail=source.detail,
        credentials_configured=source.credentials_configured,
        blocked_reason=source.blocked_reason,
        degraded_reason=source.degraded_reason,
        last_attempt_at=source.last_attempt_at,
        last_success_at=source.last_success_at,
        last_failure_at=source.last_failure_at,
        success_count=source.success_count,
        failure_count=source.failure_count,
        warning_count=source.warning_count,
        last_camera_count=source.last_camera_count,
        next_refresh_at=source.next_refresh_at,
        backoff_until=source.backoff_until,
        retry_count=source.retry_count,
        last_http_status=source.last_http_status,
        last_started_at=source.last_started_at,
        last_completed_at=source.last_completed_at,
        cadence_seconds=source.cadence_seconds or policy.catalog_refresh_seconds,
        cadence_reason=source.cadence_reason or "source policy catalog refresh cadence",
    )


def _source_is_due(source: CameraSourceRegistryEntry) -> bool:
    if not source.enabled or not source.credentials_configured or source.status == "blocked":
        return False
    now = datetime.now(tz=timezone.utc)
    if source.backoff_until and _parse_iso(source.backoff_until) > now:
        return False
    if source.next_refresh_at is None:
        return True
    return _parse_iso(source.next_refresh_at) <= now


def _camera_frame_is_due(camera: CameraEntity, source: CameraSourceRegistryEntry, policy: RefreshPolicy) -> bool:
    if source.status in {"blocked", "credentials-missing"}:
        return False
    if camera.backoff_until and _parse_iso(camera.backoff_until) > datetime.now(tz=timezone.utc):
        return False
    if camera.frame.image_url and policy.supports_direct_frame_refresh:
        return camera.next_frame_refresh_at is None or _parse_iso(camera.next_frame_refresh_at) <= datetime.now(tz=timezone.utc)
    if camera.frame.viewer_url:
        return camera.next_frame_refresh_at is None or _parse_iso(camera.next_frame_refresh_at) <= datetime.now(tz=timezone.utc)
    return False


def _camera_with_schedule(camera: CameraEntity, policy: RefreshPolicy, fetched_at: str) -> CameraEntity:
    immediate_refresh = fetched_at if camera.frame.image_url or camera.frame.viewer_url else _next_frame_refresh_at(
        camera,
        policy,
        fetched_at,
        camera.frame.status,
    )
    return camera.model_copy(
        update={
            "last_metadata_refresh_at": fetched_at,
            "next_frame_refresh_at": immediate_refresh,
            "backoff_until": None,
            "retry_count": 0,
            "last_http_status": None,
        }
    )


def _next_frame_refresh_at(camera: CameraEntity, policy: RefreshPolicy, fetched_at: str, frame_status: str) -> str | None:
    base = _parse_iso(fetched_at)
    if camera.frame.image_url and policy.supports_direct_frame_refresh:
        seconds = policy.min_frame_refresh_seconds
    elif camera.frame.viewer_url:
        seconds = policy.viewer_only_validation_seconds
    else:
        seconds = policy.max_frame_refresh_seconds
    if frame_status == "blocked":
        return None
    return (base + timedelta(seconds=seconds)).isoformat()


def _update_source_after_fetch(
    source: CameraSourceRegistryEntry,
    result: CameraSourceFetchResult,
    started_at: str,
    policy: RefreshPolicy,
) -> CameraSourceRegistryEntry:
    status = result.status
    retry_count = 0
    backoff_until = None
    if status == "rate-limited":
        retry_count = source.retry_count + 1
        backoff_until = _compute_backoff_iso(result.fetched_at, retry_count, policy)
    elif status == "blocked":
        retry_count = source.retry_count + 1
    next_refresh_at = None if status in {"blocked", "credentials-missing"} else (
        backoff_until or (_parse_iso(result.fetched_at) + timedelta(seconds=policy.catalog_refresh_seconds)).isoformat()
    )
    return source.model_copy(
        update={
            "status": status,
            "detail": _source_detail(result),
            "credentials_configured": result.credentials_configured,
            "blocked_reason": result.blocked_reason,
            "review_required": result.review_required,
            "degraded_reason": result.degraded_reason,
            "last_attempt_at": result.fetched_at,
            "last_success_at": result.fetched_at if status in {"healthy", "needs-review", "degraded"} else source.last_success_at,
            "last_failure_at": result.fetched_at if status not in {"healthy", "needs-review", "degraded"} else source.last_failure_at,
            "success_count": source.success_count + (1 if status in {"healthy", "needs-review", "degraded"} else 0),
            "failure_count": source.failure_count + (0 if status in {"healthy", "needs-review", "degraded"} else 1),
            "warning_count": len(result.warnings),
            "last_camera_count": len(result.cameras),
            "next_refresh_at": next_refresh_at,
            "backoff_until": backoff_until,
            "retry_count": retry_count,
            "last_http_status": result.last_http_status,
            "last_started_at": started_at,
            "last_completed_at": result.fetched_at,
            "cadence_seconds": policy.catalog_refresh_seconds,
            "cadence_reason": "source policy catalog refresh cadence",
        }
    )


def _update_source_after_exception(
    source: CameraSourceRegistryEntry,
    message: str,
    *,
    started_at: str,
    policy: RefreshPolicy,
    forced_state: str | None = None,
) -> CameraSourceRegistryEntry:
    now = _now_iso()
    state = forced_state or "degraded"
    blocked_reason = None
    last_http_status = source.last_http_status
    if forced_state is None:
        if "429" in message:
            state = "rate-limited"
            last_http_status = 429
        elif "401" in message or "403" in message:
            state = "blocked"
            blocked_reason = "Access blocked by upstream source."
            last_http_status = 403 if "403" in message else 401
    retry_count = 0 if state == "credentials-missing" else source.retry_count + 1
    backoff_until = None
    if state in {"rate-limited", "blocked"}:
        backoff_until = _compute_backoff_iso(now, retry_count, policy)
    next_refresh_at = None if state in {"blocked", "credentials-missing"} else (
        backoff_until or (_parse_iso(now) + timedelta(seconds=policy.catalog_refresh_seconds)).isoformat()
    )
    return source.model_copy(
        update={
            "status": state,
            "detail": f"{source.display_name} refresh failed. {message}",
            "blocked_reason": blocked_reason,
            "degraded_reason": message,
            "last_attempt_at": now,
            "last_failure_at": now,
            "failure_count": source.failure_count + 1,
            "next_refresh_at": next_refresh_at,
            "backoff_until": backoff_until,
            "retry_count": retry_count,
            "last_http_status": last_http_status,
            "last_started_at": started_at,
            "last_completed_at": now,
            "cadence_seconds": policy.catalog_refresh_seconds,
            "cadence_reason": "source policy catalog refresh cadence",
            "credentials_configured": state != "credentials-missing",
        }
    )


def _update_source_after_frame(
    source: CameraSourceRegistryEntry,
    policy: RefreshPolicy,
    *,
    probe: FrameProbeResult,
) -> CameraSourceRegistryEntry:
    if probe.http_status == 429:
        retry_count = source.retry_count + 1
        backoff_until = probe.backoff_until or _compute_backoff_iso(probe.fetched_at, retry_count, policy)
        return source.model_copy(
            update={
                "status": "rate-limited",
                "detail": probe.degraded_reason or source.detail,
                "degraded_reason": probe.degraded_reason,
                "backoff_until": backoff_until,
                "next_refresh_at": backoff_until,
                "retry_count": retry_count,
                "last_http_status": probe.http_status,
                "last_attempt_at": probe.fetched_at,
                "last_failure_at": probe.fetched_at,
            }
        )
    if probe.http_status in {401, 403}:
        return source.model_copy(
            update={
                "status": "blocked",
                "detail": probe.blocked_reason or source.detail,
                "blocked_reason": probe.blocked_reason,
                "retry_count": source.retry_count + 1,
                "last_http_status": probe.http_status,
                "last_attempt_at": probe.fetched_at,
                "last_failure_at": probe.fetched_at,
            }
        )
    if probe.status == "live" and source.status in {"degraded", "stale", "rate-limited"}:
        return source.model_copy(
            update={
                "status": "needs-review" if source.review_required else "healthy",
                "degraded_reason": None,
                "blocked_reason": None,
                "backoff_until": None,
                "retry_count": 0,
                "last_http_status": probe.http_status,
                "last_attempt_at": probe.fetched_at,
                "last_success_at": probe.fetched_at,
                "last_completed_at": probe.fetched_at,
                "next_refresh_at": source.next_refresh_at or (_parse_iso(probe.fetched_at) + timedelta(seconds=policy.catalog_refresh_seconds)).isoformat(),
            }
        )
    if probe.status != "live":
        return source.model_copy(
            update={
                "status": source.status if source.status in {"needs-review", "blocked", "credentials-missing", "rate-limited"} else "degraded",
                "degraded_reason": probe.degraded_reason or source.degraded_reason,
                "last_http_status": probe.http_status,
                "last_attempt_at": probe.fetched_at,
                "last_failure_at": probe.fetched_at,
            }
        )
    return source


def _source_detail(result: CameraSourceFetchResult) -> str:
    details = [result.detail]
    if result.partial_failure_count:
        details.append(f"{result.partial_failure_count} records failed normalization.")
    if result.warnings:
        details.append(f"{len(result.warnings)} warnings.")
    if result.status == "credentials-missing":
        details.append("Credentials are required before this source can refresh.")
    if result.status == "blocked" and result.blocked_reason:
        details.append(result.blocked_reason)
    return " ".join(details)


def _record_runtime_status(source_key: str, source: CameraSourceRegistryEntry) -> None:
    if source.status in {"healthy", "needs-review", "degraded"}:
        record_source_success(
            source_key,
            freshness_seconds=source.cadence_seconds,
            stale_after_seconds=(source.cadence_seconds or 60) * 3,
            review_required=source.review_required or source.status == "needs-review",
            warning_count=source.warning_count,
        )
        return
    record_source_failure(
        source_key,
        degraded_reason=source.degraded_reason or source.detail,
        state=source.status,
        freshness_seconds=source.cadence_seconds,
        stale_after_seconds=(source.cadence_seconds or 60) * 3,
        rate_limited=source.status == "rate-limited",
        hidden_reason=None if source.status != "credentials-missing" else "disabled-by-configuration",
        blocked_reason=source.blocked_reason,
        credentials_configured=source.credentials_configured,
        review_required=source.review_required,
        warning_count=source.warning_count,
    )


def _select_validation_sources(
    sources: list[CameraSourceRegistryEntry],
    *,
    source_keys: list[str] | None,
    include_blocked: bool,
) -> list[CameraSourceRegistryEntry]:
    allowed = set(source_keys or [])
    selected: list[CameraSourceRegistryEntry] = []
    for source in sources:
        if allowed and source.key not in allowed:
            continue
        explicit_target = bool(allowed and source.key in allowed)
        if not source.enabled and not explicit_target:
            continue
        if not source.credentials_configured and not explicit_target:
            continue
        if source.status == "blocked" and not include_blocked:
            continue
        if source.backoff_until and _parse_iso(source.backoff_until) > datetime.now(tz=timezone.utc):
            continue
        selected.append(source)
    return selected


def _metadata_uncertainty_count(cameras: list[CameraEntity], source_key: str) -> int:
    count = 0
    for camera in cameras:
        if camera.source != source_key:
            continue
        if camera.position.kind != "exact" or camera.orientation.kind != "exact" or camera.review.status != "verified":
            count += 1
    return count


def _cadence_observation(
    source_key: str,
    status: str,
    frame_summary: FrameRefreshSummary | None,
) -> str:
    policy = get_refresh_policy(source_key)
    if policy is None:
        return "No cadence policy is registered."
    if status == "rate-limited":
        return (
            "Observed upstream rate limiting; consider increasing the effective cadence or base backoff "
            f"beyond {policy.catalog_refresh_seconds}s."
        )
    if status == "blocked":
        return "Observed upstream blocking/auth failure; cadence remains paused until credentials or terms are corrected."
    if frame_summary is not None and frame_summary.frame_probe_count == 0:
        return "Validation observed metadata-only or viewer-only behavior; direct frame cadence remains disabled."
    return f"Validated against the baseline source policy cadence of {policy.catalog_refresh_seconds}s."


def _inventory_entry_for_source(
    settings: Settings,
    source_key: str,
    result: CameraSourceFetchResult,
):
    template = next((entry for entry in build_camera_source_inventory(settings) if entry.key == source_key), None)
    if template is None:
        raise RuntimeError(f"Missing source inventory template for {source_key}")
    return template.model_copy(
        update={
            "credentials_configured": result.credentials_configured,
            "onboarding_state": (
                template.onboarding_state
                if template.onboarding_state == "candidate"
                else ("active" if result.credentials_configured else template.onboarding_state)
            ),
            "approximate_camera_count": result.normalized_records,
            "last_catalog_import_at": result.fetched_at,
            "last_catalog_import_status": result.status,
            "last_catalog_import_detail": _source_detail(result),
            "blocked_reason": result.blocked_reason,
        }
    )


def _inventory_entry_for_exception(
    settings: Settings,
    source_key: str,
    source: CameraSourceRegistryEntry,
):
    template = next((entry for entry in build_camera_source_inventory(settings) if entry.key == source_key), None)
    if template is None:
        raise RuntimeError(f"Missing source inventory template for {source_key}")
    return template.model_copy(
        update={
            "credentials_configured": source.credentials_configured,
            "onboarding_state": (
                template.onboarding_state
                if template.onboarding_state == "candidate" or not source.credentials_configured
                else "active"
            ),
            "approximate_camera_count": source.last_camera_count or template.approximate_camera_count,
            "last_catalog_import_at": source.last_completed_at,
            "last_catalog_import_status": source.status,
            "last_catalog_import_detail": source.detail,
            "blocked_reason": source.blocked_reason or source.degraded_reason,
        }
    )


def _compute_backoff_iso(base_time: str, retry_count: int, policy: RefreshPolicy) -> str:
    seconds = min(
        policy.max_backoff_seconds,
        policy.rate_limit_backoff_base_seconds * (2 ** max(retry_count - 1, 0)),
    )
    return (_parse_iso(base_time) + timedelta(seconds=seconds)).isoformat()


def _camera_health_state(camera: CameraEntity, frame_status: str) -> str:
    if frame_status == "live":
        return "healthy" if camera.review.status == "verified" else "needs-review"
    if frame_status == "blocked":
        return "blocked"
    if camera.review.status == "needs-review":
        return "needs-review"
    return "degraded"


def _review_priority(camera: CameraEntity) -> str:
    if "compliance-review" in camera.review.issue_categories or camera.review.status == "blocked":
        return "high"
    if camera.position.kind != "exact":
        return "high"
    if camera.orientation.kind in {"unknown", "ptz"}:
        return "medium"
    if camera.orientation.kind == "approximate" or camera.frame.status in {"viewer-page-only", "unavailable"}:
        return "medium"
    return "low"


def _review_context(camera: CameraEntity) -> dict[str, str]:
    return {
        "sourceKey": camera.source,
        "cameraId": camera.camera_id or camera.id,
        "sourceCameraId": camera.source_camera_id or "",
        "rawLocationText": camera.location_description or "",
        "roadway": camera.roadway or "",
        "state": camera.state or "",
        "region": camera.region or "",
        "coordinateKind": camera.position.kind,
        "coordinateConfidence": f"{camera.position.confidence:.2f}" if camera.position.confidence is not None else "",
        "orientationKind": camera.orientation.kind,
        "directionText": camera.direction or camera.orientation.cardinal_direction or "",
        "heading": f"{camera.orientation.degrees:.1f}" if camera.orientation.degrees is not None else "",
        "viewerUrl": camera.frame.viewer_url or "",
        "imageUrl": camera.frame.image_url or "",
        "attributionUrl": camera.compliance.attribution_url or "",
        "termsUrl": camera.compliance.terms_url or "",
        "lastFrameAt": camera.frame.last_frame_at or "",
        "lastMetadataRefreshAt": camera.last_metadata_refresh_at or "",
        "latestFailureReason": camera.degraded_reason or "",
    }


def _review_sort_key(item: ReviewQueueItem) -> tuple[int, str, str]:
    priority_rank = {"high": 0, "medium": 1, "low": 2}
    return (priority_rank[item.priority], item.source_key, item.camera.label)


def _parse_iso(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def _now_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat()
