from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from sqlmodel import Session, select

from app.connectors.base import ConnectorRunner
from app.connectors.registry import registry
from app.models.common import RunStatus
from app.models.connector import Connector
from app.models.discovered_source import DiscoveredSource
from app.models.record import Record
from app.models.run_history import RunHistory
from app.models.wave import Wave
from app.scheduler.runner import run_connector_once
from app.services.signal_service import generate_signals_for_run, generate_signals_for_source_check
from app.services.source_check_service import check_discovered_source, is_source_due

logger = logging.getLogger(__name__)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _normalize_dt(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value
    return value.astimezone(timezone.utc).replace(tzinfo=None)


@dataclass
class SchedulerTickResult:
    scanned_connectors: int
    eligible_connectors: int
    successful_runs: int
    failed_runs: int
    scanned_sources: int
    eligible_sources: int
    successful_source_checks: int
    failed_source_checks: int
    skipped_source_checks: int


def is_connector_due(connector: Connector, now: datetime) -> bool:
    normalized_now = _normalize_dt(now)
    if not connector.enabled:
        return False
    if connector.next_run_at is not None:
        return _normalize_dt(connector.next_run_at) <= normalized_now
    if connector.last_run_at is None:
        return True
    due_at = _normalize_dt(connector.last_run_at) + timedelta(
        minutes=connector.polling_interval_minutes
    )
    return due_at <= normalized_now


def run_connector_with_history(
    session: Session,
    wave: Wave,
    connector: Connector,
    connector_lookup: Callable[[str], ConnectorRunner | None] = registry.get,
    now_fn: Callable[[], datetime] = utc_now,
) -> RunHistory:
    started = now_fn()
    run_history = RunHistory(
        wave_id=wave.id,
        connector_id=connector.id,
        started_at=started,
        status=RunStatus.RUNNING,
    )

    connector.last_run_at = started
    wave.last_run_at = started
    session.add(run_history)
    session.add(connector)
    session.add(wave)
    session.commit()
    session.refresh(run_history)

    records: list[Record] = []
    try:
        records = run_connector_once(
            session=session,
            wave=wave,
            connector=connector,
            connector_lookup=connector_lookup,
        )
        finished = now_fn()

        run_history.status = RunStatus.SUCCESS
        run_history.finished_at = finished
        run_history.records_created = len(records)
        run_history.error_message = None

        connector.last_success_at = finished
        connector.last_error_at = None
        connector.last_error_message = None
        connector.next_run_at = finished + timedelta(minutes=connector.polling_interval_minutes)

        wave.last_success_at = finished
        wave.last_error_at = None
        wave.last_error_message = None
    except Exception as exc:  # noqa: BLE001
        session.rollback()
        finished = now_fn()
        message = str(exc)[:2000]

        run_history.status = RunStatus.FAILED
        run_history.finished_at = finished
        run_history.records_created = 0
        run_history.error_message = message

        connector.last_error_at = finished
        connector.last_error_message = message
        connector.next_run_at = finished + timedelta(minutes=connector.polling_interval_minutes)

        wave.last_error_at = finished
        wave.last_error_message = message
        logger.exception(
            "Connector run failed for connector_id=%s wave_id=%s",
            connector.id,
            wave.id,
        )

    session.add(run_history)
    session.add(connector)
    session.add(wave)
    session.commit()
    session.refresh(run_history)
    generate_signals_for_run(session, wave, connector, run_history, records)
    return run_history


def run_wave_now(
    session: Session,
    wave: Wave,
    connector_lookup: Callable[[str], ConnectorRunner | None] = registry.get,
    now_fn: Callable[[], datetime] = utc_now,
) -> list[RunHistory]:
    runs: list[RunHistory] = []
    for connector in wave.connectors:
        if not connector.enabled:
            continue
        run = run_connector_with_history(
            session=session,
            wave=wave,
            connector=connector,
            connector_lookup=connector_lookup,
            now_fn=now_fn,
        )
        runs.append(run)
    return runs


def run_scheduler_tick(
    session: Session,
    connector_lookup: Callable[[str], ConnectorRunner | None] = registry.get,
    now_fn: Callable[[], datetime] = utc_now,
) -> SchedulerTickResult:
    now = now_fn()
    connectors = list(
        session.exec(
            select(Connector).where(Connector.enabled.is_(True)).order_by(Connector.id)
        )
    )
    eligible = [connector for connector in connectors if is_connector_due(connector, now)]

    success_count = 0
    failed_count = 0
    for connector in eligible:
        wave = session.get(Wave, connector.wave_id)
        if wave is None:
            logger.warning(
                "Skipping connector_id=%s because wave_id=%s is missing",
                connector.id,
                connector.wave_id,
            )
            continue
        run = run_connector_with_history(
            session=session,
            wave=wave,
            connector=connector,
            connector_lookup=connector_lookup,
            now_fn=now_fn,
        )
        if run.status == RunStatus.SUCCESS:
            success_count += 1
        else:
            failed_count += 1

    sources = list(
        session.exec(
            select(DiscoveredSource)
            .where(DiscoveredSource.auto_check_enabled.is_(True))
            .order_by(DiscoveredSource.id)
        )
    )
    eligible_sources = [source for source in sources if is_source_due(source, now)]
    source_success = 0
    source_failed = 0
    source_skipped = 0
    for source in eligible_sources:
        prev_consecutive_failures = source.consecutive_failures
        prev_content_type = source.last_content_type
        prev_stability = source.stability_score
        check = check_discovered_source(
            session,
            source,
            automated=True,
            checked_at=now_fn(),
        )
        if check.status.value == "success":
            source_success += 1
        elif check.status.value == "failed":
            source_failed += 1
        else:
            source_skipped += 1
        generate_signals_for_source_check(
            session,
            source,
            check,
            previous_consecutive_failures=prev_consecutive_failures,
            previous_content_type=prev_content_type,
            previous_stability_score=prev_stability,
            now=now_fn(),
        )

    return SchedulerTickResult(
        scanned_connectors=len(connectors),
        eligible_connectors=len(eligible),
        successful_runs=success_count,
        failed_runs=failed_count,
        scanned_sources=len(sources),
        eligible_sources=len(eligible_sources),
        successful_source_checks=source_success,
        failed_source_checks=source_failed,
        skipped_source_checks=source_skipped,
    )
