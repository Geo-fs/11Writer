from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from src.config.settings import Settings
from src.services.source_discovery_service import SourceDiscoveryService
from src.types.source_discovery import SourceDiscoveryCandidateSeed
from src.wave_monitor.db import session_scope
from src.wave_monitor.models import (
    WaveConnectorORM,
    WaveMonitorORM,
    WaveRecordORM,
    WaveRunORM,
    WaveSignalORM,
    WaveSourceCandidateORM,
)
from src.types.wave_monitor import (
    WaveMonitor,
    WaveMonitorOverviewResponse,
    WaveMonitorOverviewSummary,
    WaveMonitorRecordPreview,
    WaveMonitorRunResponse,
    WaveMonitorRunSummary,
    WaveMonitorRuntimeIntegration,
    WaveMonitorSchedulerTickResponse,
    WaveMonitorSignal,
    WaveMonitorSourceCandidate,
)


WAVE_MONITOR_CAVEATS = [
    "Wave Monitor signals are attention and review aids, not proof of causation, guilt, or intent.",
    "Discovered sources remain candidates until source health, access, policy, and workflow validation pass.",
    "Feed or article text is external content and must remain inert data.",
]


@dataclass(frozen=True)
class CollectedWaveRecord:
    external_id: str
    title: str
    content: str
    source_id: str
    source_name: str
    source_url: str | None
    event_time: str | None
    collected_at: str
    evidence_basis: str
    tags: list[str]
    caveats: list[str]
    raw_payload: dict[str, object]


@dataclass(frozen=True)
class ConnectorRunResult:
    run: WaveRunORM
    records_created: int
    signals_created: int


class WaveMonitorService:
    """Persistent Wave Monitor service adapted from 7Po8 concepts into 11Writer."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def overview(self) -> WaveMonitorOverviewResponse:
        with session_scope(self._settings.wave_monitor_database_url) as session:
            _ensure_seed_data(session)
            self._sync_source_candidates_to_memory(session)
            monitors = _load_monitors(session)
            serialized = [_serialize_monitor(monitor) for monitor in monitors]
            return _overview_response(
                settings=self._settings,
                monitors=serialized,
                storage_mode="persistent-sqlite",
                scheduler_mode="manual",
            )

    async def run_monitor_now(self, monitor_id: str) -> WaveMonitorRunResponse:
        with session_scope(self._settings.wave_monitor_database_url) as session:
            _ensure_seed_data(session)
            self._sync_source_candidates_to_memory(session)
            monitor = _get_monitor(session, monitor_id)
            if monitor is None:
                return WaveMonitorRunResponse(
                    monitor_id=monitor_id,
                    status="skipped",
                    runs=[],
                    records_created=0,
                    signals_created=0,
                    caveats=["Monitor was not found."],
                )
            results: list[ConnectorRunResult] = []
            for connector in monitor.connectors:
                if connector.enabled:
                    results.append(await self._run_connector(session, monitor, connector, force=True))
            return _run_response(monitor_id, results)

    async def scheduler_tick(self) -> WaveMonitorSchedulerTickResponse:
        with session_scope(self._settings.wave_monitor_database_url) as session:
            _ensure_seed_data(session)
            self._sync_source_candidates_to_memory(session)
            now = _utc_now()
            connectors = list(
                session.scalars(
                    select(WaveConnectorORM)
                    .where(WaveConnectorORM.enabled.is_(True))
                    .order_by(WaveConnectorORM.connector_id)
                )
            )
            eligible = [
                connector
                for connector in connectors
                if _is_connector_due(connector, now)
                and (monitor := session.get(WaveMonitorORM, connector.monitor_id)) is not None
                and monitor.status == "active"
            ]
            results: list[ConnectorRunResult] = []
            for connector in eligible:
                monitor = session.get(WaveMonitorORM, connector.monitor_id)
                if monitor is None:
                    continue
                results.append(await self._run_connector(session, monitor, connector, force=False))

            return WaveMonitorSchedulerTickResponse(
                scanned_connectors=len(connectors),
                eligible_connectors=len(eligible),
                successful_runs=sum(1 for result in results if result.run.status == "success"),
                failed_runs=sum(1 for result in results if result.run.status == "failed"),
                records_created=sum(result.records_created for result in results),
                signals_created=sum(result.signals_created for result in results),
                caveats=[
                    "Scheduler tick is manual/API-triggered in this Phase 2 slice; no hidden background loop is enabled.",
                    "Only enabled connectors on active monitors are eligible.",
                ],
            )

    async def _run_connector(
        self,
        session: Session,
        monitor: WaveMonitorORM,
        connector: WaveConnectorORM,
        *,
        force: bool,
    ) -> ConnectorRunResult:
        started_at = _utc_now()
        run = WaveRunORM(
            run_id=f"run:{connector.connector_id}:{_compact_timestamp(started_at)}",
            monitor_id=monitor.monitor_id,
            connector_id=connector.connector_id,
            status="success",
            started_at=started_at,
            finished_at=None,
            records_created=0,
            source_checks_completed=0,
            error_summary=None,
        )
        session.add(run)
        session.flush()

        try:
            if not force and not _is_connector_due(connector, started_at):
                run.status = "skipped"
                run.finished_at = _utc_now()
                run.error_summary = "Connector is not due."
                session.flush()
                return ConnectorRunResult(run=run, records_created=0, signals_created=0)

            records = await self._collect_records(connector)
            created_records = _persist_records(session, monitor, connector, records)
            finished_at = _utc_now()
            signal_count = _generate_run_signals(
                session,
                monitor,
                connector,
                created_records=created_records,
                finished_at=finished_at,
            )

            run.status = "success"
            run.finished_at = finished_at
            run.records_created = len(created_records)
            connector.last_run_at = started_at
            connector.last_success_at = finished_at
            connector.last_error_at = None
            connector.last_error_message = None
            connector.next_run_at = _add_minutes(finished_at, connector.polling_interval_minutes)
            monitor.last_run_at = started_at
            monitor.next_run_at = _next_monitor_run_at(monitor)
            monitor.source_health = "loaded"
            monitor.updated_at = finished_at
            session.flush()
            return ConnectorRunResult(run=run, records_created=len(created_records), signals_created=signal_count)
        except Exception as exc:  # noqa: BLE001
            finished_at = _utc_now()
            message = str(exc)[:2000]
            run.status = "failed"
            run.finished_at = finished_at
            run.error_summary = message
            connector.last_run_at = started_at
            connector.last_error_at = finished_at
            connector.last_error_message = message
            connector.next_run_at = _add_minutes(finished_at, connector.polling_interval_minutes)
            monitor.last_run_at = started_at
            monitor.next_run_at = _next_monitor_run_at(monitor)
            monitor.source_health = "degraded"
            monitor.updated_at = finished_at
            signal = _upsert_signal(
                session,
                monitor_id=monitor.monitor_id,
                signal_type="connector_run_failed",
                title=f"Connector run failed: {connector.name}",
                summary=message,
                severity="medium",
                evidence_basis="derived",
                source_ids=[connector.connector_id],
                relationship_reasons=["connector run failure"],
                caveats=[
                    "A connector failure is source-health context, not evidence about the monitored topic.",
                ],
                dedupe_key=f"connector_run_failed:{connector.connector_id}",
                now=finished_at,
            )
            session.flush()
            return ConnectorRunResult(run=run, records_created=0, signals_created=1 if signal else 0)

    async def _collect_records(self, connector: WaveConnectorORM) -> list[CollectedWaveRecord]:
        if connector.connector_type != "rss":
            raise ValueError(f"Unsupported Wave Monitor connector type: {connector.connector_type}")
        if connector.source_mode == "fixture":
            if not connector.fixture_xml:
                raise ValueError("Fixture RSS connector is missing fixture XML.")
            return _parse_rss_payload(
                connector.fixture_xml.encode("utf-8"),
                connector=connector,
                fetched_at=_utc_now(),
            )
        if connector.source_mode == "live":
            if not connector.feed_url:
                raise ValueError("Live RSS connector is missing feed_url.")
            async with httpx.AsyncClient(
                timeout=self._settings.wave_monitor_http_timeout_seconds,
                follow_redirects=True,
                headers={"User-Agent": "11Writer-WaveMonitor/phase2"},
            ) as client:
                response = await client.get(connector.feed_url)
                response.raise_for_status()
                return _parse_rss_payload(response.content, connector=connector, fetched_at=_utc_now())
        raise ValueError(f"Unsupported Wave Monitor connector source mode: {connector.source_mode}")

    def _sync_source_candidates_to_memory(self, session: Session) -> None:
        candidates = list(session.scalars(select(WaveSourceCandidateORM).order_by(WaveSourceCandidateORM.source_id)))
        if not candidates:
            return
        monitors = {
            monitor.monitor_id: monitor
            for monitor in session.scalars(select(WaveMonitorORM).order_by(WaveMonitorORM.monitor_id))
        }
        seeds: list[SourceDiscoveryCandidateSeed] = []
        for candidate in candidates:
            monitor = monitors.get(candidate.monitor_id)
            seeds.append(
                SourceDiscoveryCandidateSeed(
                    source_id=candidate.source_id,
                    title=candidate.title,
                    url=candidate.url,
                    parent_domain=candidate.parent_domain,
                    source_type=candidate.source_type,
                    source_class="live" if candidate.source_type in {"rss", "atom", "api"} else "unknown",
                    wave_id=candidate.monitor_id,
                    wave_title=monitor.title if monitor else candidate.monitor_id,
                    lifecycle_state=candidate.lifecycle_state,
                    source_health=candidate.source_health,
                    policy_state=candidate.policy_state,
                    access_result="unknown",
                    machine_readable_result="partial" if candidate.source_type in {"rss", "atom", "api"} else "unknown",
                    wave_fit_score=candidate.relevance_score,
                    relevance_basis=[
                        "Wave Monitor discovered source candidate",
                        "Wave fit is separate from global correctness reputation",
                    ],
                    caveats=_loads_list(candidate.caveats_json),
                )
            )
        SourceDiscoveryService(self._settings).upsert_candidates(seeds)


def _overview_response(
    *,
    settings: Settings,
    monitors: list[WaveMonitor],
    storage_mode: str,
    scheduler_mode: str,
) -> WaveMonitorOverviewResponse:
    new_signals = sum(
        1
        for monitor in monitors
        for signal in monitor.signals
        if signal.status == "new"
    )
    source_issues = sum(
        1
        for monitor in monitors
        for source in monitor.source_candidates
        if source.source_health in {"degraded", "error", "stale"}
    )
    return WaveMonitorOverviewResponse(
        metadata={
            "source": "wave-monitor-overview",
            "sourceMode": "mixed" if any(monitor.source_mode == "live" for monitor in monitors) else "fixture",
            "importedProject": "7Po8",
            "runtimeMode": settings.app_env,
            "toolStatus": "persistent-backend-preview",
        },
        runtime=WaveMonitorRuntimeIntegration(
            tool_name="Wave Monitor",
            imported_project="7Po8",
            standalone_runtime_enabled=False,
            route_prefix="/api/tools/waves",
            storage_mode=storage_mode,
            scheduler_mode=scheduler_mode,  # type: ignore[arg-type]
            caveats=[
                "7Po8 standalone FastAPI, Vite, CORS, and local database runtime are not mounted here.",
                "Wave Monitor state is persisted through 11Writer backend storage.",
                "Background scheduling is not automatically enabled in this Phase 2 slice.",
            ],
        ),
        summary=WaveMonitorOverviewSummary(
            total_monitors=len(monitors),
            active_monitors=sum(1 for monitor in monitors if monitor.status == "active"),
            paused_monitors=sum(1 for monitor in monitors if monitor.status == "paused"),
            total_signals=sum(len(monitor.signals) for monitor in monitors),
            new_signals=new_signals,
            discovered_sources=sum(len(monitor.source_candidates) for monitor in monitors),
            source_issues=source_issues,
        ),
        monitors=monitors,
        caveats=WAVE_MONITOR_CAVEATS,
        next_steps=[
            "Add create/update APIs for monitors and connectors.",
            "Add source-check persistence for discovered sources.",
            "Wire scheduler tick into backend-only runtime controls when that runtime mode lands.",
        ],
    )


def _run_response(monitor_id: str, results: list[ConnectorRunResult]) -> WaveMonitorRunResponse:
    return WaveMonitorRunResponse(
        monitor_id=monitor_id,
        status="failed" if any(result.run.status == "failed" for result in results) else "success",
        runs=[_serialize_run(result.run) for result in results],
        records_created=sum(result.records_created for result in results),
        signals_created=sum(result.signals_created for result in results),
        caveats=[
            "Run-now is user/API-triggered and bounded to enabled connectors on the selected monitor.",
            "Connector output remains source-scoped review context.",
        ],
    )


def _load_monitors(session: Session) -> list[WaveMonitorORM]:
    return list(
        session.scalars(
            select(WaveMonitorORM)
            .options(
                selectinload(WaveMonitorORM.connectors),
                selectinload(WaveMonitorORM.records),
                selectinload(WaveMonitorORM.signals),
                selectinload(WaveMonitorORM.runs),
                selectinload(WaveMonitorORM.source_candidates),
            )
            .order_by(WaveMonitorORM.monitor_id)
        )
    )


def _get_monitor(session: Session, monitor_id: str) -> WaveMonitorORM | None:
    return session.scalar(
        select(WaveMonitorORM)
        .where(WaveMonitorORM.monitor_id == monitor_id)
        .options(
            selectinload(WaveMonitorORM.connectors),
            selectinload(WaveMonitorORM.records),
            selectinload(WaveMonitorORM.signals),
            selectinload(WaveMonitorORM.runs),
            selectinload(WaveMonitorORM.source_candidates),
        )
    )


def _serialize_monitor(monitor: WaveMonitorORM) -> WaveMonitor:
    signals = sorted(monitor.signals, key=lambda row: row.created_at, reverse=True)
    records = sorted(monitor.records, key=lambda row: row.collected_at, reverse=True)
    runs = sorted(monitor.runs, key=lambda row: row.started_at, reverse=True)
    return WaveMonitor(
        monitor_id=monitor.monitor_id,
        title=monitor.title,
        description=monitor.description,
        status=monitor.status,  # type: ignore[arg-type]
        focus_type=monitor.focus_type,  # type: ignore[arg-type]
        source_mode=monitor.source_mode,  # type: ignore[arg-type]
        source_health=monitor.source_health,  # type: ignore[arg-type]
        evidence_basis=monitor.evidence_basis,  # type: ignore[arg-type]
        connector_count=len(monitor.connectors),
        record_count=len(monitor.records),
        signal_count=len(monitor.signals),
        discovered_source_count=len(monitor.source_candidates),
        last_run_at=monitor.last_run_at,
        next_run_at=monitor.next_run_at,
        caveats=_loads_list(monitor.caveats_json),
        available_actions=_monitor_actions(monitor),
        signals=[_serialize_signal(signal) for signal in signals[:20]],
        source_candidates=[_serialize_source(source) for source in monitor.source_candidates[:20]],
        recent_runs=[_serialize_run(run) for run in runs[:20]],
        recent_records=[_serialize_record(record) for record in records[:20]],
    )


def _serialize_signal(signal: WaveSignalORM) -> WaveMonitorSignal:
    return WaveMonitorSignal(
        signal_id=signal.signal_id,
        signal_type=signal.signal_type,
        title=signal.title,
        summary=signal.summary,
        severity=signal.severity,  # type: ignore[arg-type]
        status=signal.status,  # type: ignore[arg-type]
        evidence_basis=signal.evidence_basis,  # type: ignore[arg-type]
        source_ids=_loads_list(signal.source_ids_json),
        relationship_reasons=_loads_list(signal.relationship_reasons_json),
        caveats=_loads_list(signal.caveats_json),
        available_actions=[
            "inspect-evidence",
            "track",
            "mark-reviewed",
            "export-packet",
            "move-on",
        ],
    )


def _serialize_source(source: WaveSourceCandidateORM) -> WaveMonitorSourceCandidate:
    return WaveMonitorSourceCandidate(
        source_id=source.source_id,
        title=source.title,
        url=source.url,
        source_type=source.source_type,
        parent_domain=source.parent_domain,
        lifecycle_state=source.lifecycle_state,  # type: ignore[arg-type]
        source_health=source.source_health,  # type: ignore[arg-type]
        trust_tier=source.trust_tier,
        relevance_score=source.relevance_score,
        stability_score=source.stability_score,
        policy_state=source.policy_state,
        caveats=_loads_list(source.caveats_json),
    )


def _serialize_run(run: WaveRunORM) -> WaveMonitorRunSummary:
    return WaveMonitorRunSummary(
        run_id=run.run_id,
        status=run.status,  # type: ignore[arg-type]
        started_at=run.started_at,
        finished_at=run.finished_at,
        records_created=run.records_created,
        source_checks_completed=run.source_checks_completed,
        error_summary=run.error_summary,
    )


def _serialize_record(record: WaveRecordORM) -> WaveMonitorRecordPreview:
    return WaveMonitorRecordPreview(
        record_id=f"record:{record.record_id}",
        title=record.title,
        source_id=record.source_id,
        source_name=record.source_name,
        source_url=record.source_url,
        event_time=record.event_time,
        collected_at=record.collected_at,
        evidence_basis=record.evidence_basis,  # type: ignore[arg-type]
        tags=_loads_list(record.tags_json),
        caveats=_loads_list(record.caveats_json),
    )


def _monitor_actions(monitor: WaveMonitorORM) -> list[str]:
    actions = ["open-monitor", "inspect-evidence", "run-now", "track", "export-packet", "move-on"]
    if monitor.status == "active":
        actions.append("pause")
    elif monitor.status == "paused":
        actions.append("resume")
    return actions


def _persist_records(
    session: Session,
    monitor: WaveMonitorORM,
    connector: WaveConnectorORM,
    records: list[CollectedWaveRecord],
) -> list[WaveRecordORM]:
    created: list[WaveRecordORM] = []
    for record in records:
        existing = session.scalar(
            select(WaveRecordORM).where(
                WaveRecordORM.connector_id == connector.connector_id,
                WaveRecordORM.external_id == record.external_id,
            )
        )
        if existing is not None:
            continue
        row = WaveRecordORM(
            monitor_id=monitor.monitor_id,
            connector_id=connector.connector_id,
            external_id=record.external_id,
            title=record.title,
            content=record.content,
            source_id=record.source_id,
            source_name=record.source_name,
            source_url=record.source_url,
            event_time=record.event_time,
            collected_at=record.collected_at,
            evidence_basis=record.evidence_basis,
            tags_json=json.dumps(record.tags),
            caveats_json=json.dumps(record.caveats),
            raw_payload_json=json.dumps(record.raw_payload),
        )
        session.add(row)
        created.append(row)
    session.flush()
    return created


def _generate_run_signals(
    session: Session,
    monitor: WaveMonitorORM,
    connector: WaveConnectorORM,
    *,
    created_records: list[WaveRecordORM],
    finished_at: str,
) -> int:
    signal_count = 0
    if created_records:
        signal = _upsert_signal(
            session,
            monitor_id=monitor.monitor_id,
            signal_type="matching_record",
            title=f"New records collected for {connector.name}",
            summary=f"{len(created_records)} new records were collected by the connector.",
            severity="medium",
            evidence_basis="scored",
            source_ids=[connector.connector_id],
            relationship_reasons=["new records collected", "monitor connector run"],
            caveats=[
                "New records are review leads, not proof that the records are related.",
            ],
            dedupe_key=f"matching_record:{connector.connector_id}",
            now=finished_at,
        )
        signal_count += 1 if signal else 0
    else:
        signal = _upsert_signal(
            session,
            monitor_id=monitor.monitor_id,
            signal_type="source_silence",
            title=f"No new records for {connector.name}",
            summary="Connector ran successfully but did not collect new records.",
            severity="low",
            evidence_basis="derived",
            source_ids=[connector.connector_id],
            relationship_reasons=["successful run", "no new records"],
            caveats=[
                "No new records does not prove no relevant events or complete source coverage.",
            ],
            dedupe_key=f"source_silence:{connector.connector_id}",
            now=finished_at,
        )
        signal_count += 1 if signal else 0
    return signal_count


def _upsert_signal(
    session: Session,
    *,
    monitor_id: str,
    signal_type: str,
    title: str,
    summary: str,
    severity: str,
    evidence_basis: str,
    source_ids: list[str],
    relationship_reasons: list[str],
    caveats: list[str],
    dedupe_key: str,
    now: str,
) -> WaveSignalORM | None:
    existing = session.scalar(
        select(WaveSignalORM).where(
            WaveSignalORM.monitor_id == monitor_id,
            WaveSignalORM.dedupe_key == dedupe_key,
            WaveSignalORM.status != "resolved",
        )
    )
    if existing is not None:
        existing.summary = summary
        existing.created_at = now
        return None
    signal = WaveSignalORM(
        signal_id=f"signal:{signal_type}:{_safe_id(monitor_id)}:{_compact_timestamp(now)}",
        monitor_id=monitor_id,
        signal_type=signal_type,
        title=title,
        summary=summary,
        severity=severity,
        status="new",
        evidence_basis=evidence_basis,
        source_ids_json=json.dumps(source_ids),
        relationship_reasons_json=json.dumps(relationship_reasons),
        caveats_json=json.dumps(caveats),
        created_at=now,
        dedupe_key=dedupe_key,
    )
    session.add(signal)
    return signal


def _parse_rss_payload(
    payload: bytes,
    *,
    connector: WaveConnectorORM,
    fetched_at: str,
) -> list[CollectedWaveRecord]:
    root = ET.fromstring(payload)
    include = [term.casefold() for term in _loads_list(connector.include_keywords_json)]
    exclude = [term.casefold() for term in _loads_list(connector.exclude_keywords_json)]
    items = list(root.findall(".//item"))
    atom_entries = list(root.findall(".//{http://www.w3.org/2005/Atom}entry"))
    records: list[CollectedWaveRecord] = []
    if items:
        for item in items[: connector.max_items_per_run]:
            title = _node_text(item, "title") or "(untitled)"
            summary = _node_text(item, "description") or _node_text(item, "summary") or ""
            link = _node_text(item, "link")
            published = _node_text(item, "pubDate") or _node_text(item, "updated")
            guid = _node_text(item, "guid") or link or f"{title}|{published or fetched_at}"
            if not _keyword_allowed(title, summary, include, exclude):
                continue
            records.append(_collected_record(connector, guid, title, summary, link, published, fetched_at))
    elif atom_entries:
        for entry in atom_entries[: connector.max_items_per_run]:
            title = _atom_text(entry, "title") or "(untitled)"
            summary = _atom_text(entry, "summary") or _atom_text(entry, "content") or ""
            link = _atom_link(entry)
            published = _atom_text(entry, "published") or _atom_text(entry, "updated")
            guid = _atom_text(entry, "id") or link or f"{title}|{published or fetched_at}"
            if not _keyword_allowed(title, summary, include, exclude):
                continue
            records.append(_collected_record(connector, guid, title, summary, link, published, fetched_at))
    return records


def _collected_record(
    connector: WaveConnectorORM,
    guid: str,
    title: str,
    summary: str,
    link: str | None,
    published: str | None,
    fetched_at: str,
) -> CollectedWaveRecord:
    return CollectedWaveRecord(
        external_id=f"rss:{guid}",
        title=title,
        content=_strip_markup(summary),
        source_id=connector.connector_id,
        source_name=connector.name,
        source_url=link,
        event_time=published,
        collected_at=fetched_at,
        evidence_basis="contextual",
        tags=["wave-monitor", "rss"],
        caveats=[
            "RSS item is contextual source-reported text and remains inert data.",
        ],
        raw_payload={"guid": guid, "feedUrl": connector.feed_url or "fixture"},
    )


def _keyword_allowed(title: str, summary: str, include: list[str], exclude: list[str]) -> bool:
    text = f"{title}\n{summary}".casefold()
    if include and not any(term in text for term in include):
        return False
    return not any(term in text for term in exclude)


def _node_text(element: ET.Element, name: str) -> str | None:
    node = element.find(name)
    if node is None or node.text is None:
        return None
    return node.text.strip()


def _atom_text(element: ET.Element, name: str) -> str | None:
    node = element.find(f"{{http://www.w3.org/2005/Atom}}{name}")
    if node is None or node.text is None:
        return None
    return node.text.strip()


def _atom_link(element: ET.Element) -> str | None:
    node = element.find("{http://www.w3.org/2005/Atom}link")
    if node is None:
        return None
    href = node.attrib.get("href")
    return href.strip() if href else None


def _strip_markup(value: str) -> str:
    return re.sub(r"<[^>]+>", "", value).strip()


def _ensure_seed_data(session: Session) -> None:
    existing = session.get(WaveMonitorORM, "wave:scam-ecosystem-watch")
    if existing is not None:
        return
    now = _utc_now()
    scam = WaveMonitorORM(
        monitor_id="wave:scam-ecosystem-watch",
        title="Scam ecosystem watch",
        description="Persistent monitor for scam, cyber advisory, investigation, and source-health signals.",
        status="active",
        focus_type="mixed",
        source_mode="fixture",
        source_health="loaded",
        evidence_basis="contextual",
        last_run_at=None,
        next_run_at=now,
        caveats_json=json.dumps([
            "Contextual monitor only; it does not identify suspects or prove coordination.",
            "Relationship candidates require explicit basis and user review before export.",
        ]),
        created_at=now,
        updated_at=now,
    )
    health = WaveMonitorORM(
        monitor_id="wave:source-health-watch",
        title="Source health watch",
        description="Persistent monitor for source checks, degraded feeds, and recovery signals.",
        status="paused",
        focus_type="event",
        source_mode="fixture",
        source_health="degraded",
        evidence_basis="derived",
        last_run_at=None,
        next_run_at=None,
        caveats_json=json.dumps(["Paused fixture monitor; no live checks are running."]),
        created_at=now,
        updated_at=now,
    )
    session.add_all([scam, health])
    session.flush()
    session.add_all(
        [
            WaveConnectorORM(
                connector_id="connector:scam-fixture-rss",
                monitor_id=scam.monitor_id,
                connector_type="rss",
                name="Scam Watch Fixture RSS",
                enabled=True,
                source_mode="fixture",
                feed_url=None,
                fixture_xml=_seed_rss_fixture(),
                include_keywords_json=json.dumps(["scam", "fraud", "investigation", "call-center"]),
                exclude_keywords_json=json.dumps([]),
                polling_interval_minutes=60,
                max_items_per_run=20,
                next_run_at=now,
            ),
            WaveConnectorORM(
                connector_id="connector:source-health-fixture-rss",
                monitor_id=health.monitor_id,
                connector_type="rss",
                name="Source Health Fixture RSS",
                enabled=False,
                source_mode="fixture",
                feed_url=None,
                fixture_xml=_seed_rss_fixture(),
                include_keywords_json=json.dumps(["source", "health"]),
                exclude_keywords_json=json.dumps([]),
                polling_interval_minutes=60,
                max_items_per_run=20,
                next_run_at=None,
            ),
        ]
    )
    session.flush()
    session.add_all(
        [
            WaveSourceCandidateORM(
                source_id="source:consumer-warning-rss",
                monitor_id=scam.monitor_id,
                title="Consumer warning RSS candidate",
                url="https://example.invalid/consumer-warning/rss",
                source_type="rss",
                parent_domain="example.invalid",
                lifecycle_state="candidate",
                source_health="loaded",
                trust_tier="tier_3",
                relevance_score=0.82,
                stability_score=0.88,
                policy_state="manual_review",
                caveats_json=json.dumps([
                    "Fixture placeholder URL; use only as contract shape.",
                    "Manual review required before approval.",
                ]),
            ),
            WaveSourceCandidateORM(
                source_id="source:regional-news-feed",
                monitor_id=scam.monitor_id,
                title="Regional news feed candidate",
                url="https://example.invalid/regional/rss",
                source_type="rss",
                parent_domain="example.invalid",
                lifecycle_state="candidate",
                source_health="stale",
                trust_tier="tier_4",
                relevance_score=0.61,
                stability_score=0.42,
                policy_state="manual_review",
                caveats_json=json.dumps([
                    "Stale fixture source; should not be used for current event confidence.",
                ]),
            ),
        ]
    )
    session.flush()
    session.add_all(
        [
            WaveRunORM(
                run_id="run:seed:scam-ecosystem-watch",
                monitor_id=scam.monitor_id,
                connector_id="connector:scam-fixture-rss",
                status="success",
                started_at=now,
                finished_at=now,
                records_created=1,
                source_checks_completed=1,
                error_summary=None,
            ),
            WaveRecordORM(
                monitor_id=scam.monitor_id,
                connector_id="connector:scam-fixture-rss",
                external_id="seed:wave-monitor-fixture-001",
                title="Seeded fixture advisory mentioning fraud technique",
                content="Seeded persistent preview record for scam ecosystem review workflows.",
                source_id="connector:scam-fixture-rss",
                source_name="Scam Watch Fixture RSS",
                source_url="https://example.invalid/advisory",
                event_time="2026-05-01T17:45:00Z",
                collected_at=now,
                evidence_basis="contextual",
                tags_json=json.dumps(["wave-monitor", "rss", "seed"]),
                caveats_json=json.dumps([
                    "Seeded fixture record keeps Analyst Workbench context available without running connectors.",
                ]),
                raw_payload_json=json.dumps({"fixture": True}),
            ),
            WaveSignalORM(
                signal_id="signal:matching-records:scam-watch",
                monitor_id=scam.monitor_id,
                signal_type="matching_record",
                title="Matching records detected",
                summary=(
                    "Fixture records share scam, investigation, and call-center terms. "
                    "This is a review lead, not proof of coordination."
                ),
                severity="medium",
                status="new",
                evidence_basis="scored",
                source_ids_json=json.dumps(["connector:scam-fixture-rss"]),
                relationship_reasons_json=json.dumps([
                    "shared topic terms",
                    "same monitor focus",
                    "source-reported context",
                ]),
                caveats_json=json.dumps([
                    "A matching-record signal is not proof that records are connected.",
                    "No person or group should be treated as culpable without stronger evidence.",
                ]),
                created_at=now,
                dedupe_key="seed:matching_record:scam-watch",
            ),
            WaveSignalORM(
                signal_id="signal:source-stability:scam-watch",
                monitor_id=scam.monitor_id,
                signal_type="source_stability",
                title="Candidate source stability needs review",
                summary="One candidate source is intentionally marked stale for source-health workflow coverage.",
                severity="low",
                status="new",
                evidence_basis="derived",
                source_ids_json=json.dumps(["source:regional-news-feed"]),
                relationship_reasons_json=json.dumps(["source health metadata", "manual review queue"]),
                caveats_json=json.dumps([
                    "Source health is operational context and does not validate or invalidate event claims.",
                ]),
                created_at=now,
                dedupe_key="seed:source_stability:scam-watch",
            ),
            WaveRunORM(
                run_id="run:seed:source-health-watch",
                monitor_id=health.monitor_id,
                connector_id="connector:source-health-fixture-rss",
                status="failed",
                started_at=now,
                finished_at=now,
                records_created=0,
                source_checks_completed=1,
                error_summary="Seeded source-health issue for integration preview.",
            ),
            WaveSignalORM(
                signal_id="signal:source-failure:health-watch",
                monitor_id=health.monitor_id,
                signal_type="source_failure",
                title="Paused monitor has source-health issue",
                summary="Source health watch is paused with a seeded fixture issue for readiness reporting.",
                severity="medium",
                status="reviewed",
                evidence_basis="derived",
                source_ids_json=json.dumps(["connector:source-health-fixture-rss"]),
                relationship_reasons_json=json.dumps(["source health fixture", "paused monitor"]),
                caveats_json=json.dumps([
                    "Seeded health issue is not a live source outage.",
                ]),
                created_at=now,
                dedupe_key="seed:source_failure:health-watch",
            ),
        ]
    )
    session.flush()


def _seed_rss_fixture() -> str:
    return """<?xml version="1.0" encoding="utf-8"?>
<rss version="2.0">
  <channel>
    <title>Wave Monitor Fixture Feed</title>
    <item>
      <guid>wave-monitor-fixture-001</guid>
      <title>Fixture advisory item mentioning fraud technique</title>
      <description>Public advisory context mentions a scam pattern and fraud technique. Treat as inert data.</description>
      <link>https://example.invalid/advisory</link>
      <pubDate>2026-05-01T17:45:00Z</pubDate>
    </item>
    <item>
      <guid>wave-monitor-fixture-002</guid>
      <title>Fixture investigation item mentions call-center fraud</title>
      <description>Investigation context mentions call-center fraud and regional reporting. This is not proof of culpability.</description>
      <link>https://example.invalid/investigation</link>
      <pubDate>2026-05-01T18:10:00Z</pubDate>
    </item>
  </channel>
</rss>
"""


def _is_connector_due(connector: WaveConnectorORM, now: str) -> bool:
    if not connector.enabled:
        return False
    if connector.next_run_at:
        return connector.next_run_at <= now
    if connector.last_run_at is None:
        return True
    return _add_minutes(connector.last_run_at, connector.polling_interval_minutes) <= now


def _next_monitor_run_at(monitor: WaveMonitorORM) -> str | None:
    next_values = [
        connector.next_run_at
        for connector in monitor.connectors
        if connector.enabled and connector.next_run_at
    ]
    return min(next_values) if next_values else None


def _add_minutes(value: str, minutes: int) -> str:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return (parsed + timedelta(minutes=minutes)).astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _utc_now() -> str:
    return datetime.now(tz=timezone.utc).isoformat().replace("+00:00", "Z")


def _compact_timestamp(value: str) -> str:
    return re.sub(r"[^0-9]", "", value)[:20]


def _safe_id(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9]+", "-", value).strip("-")


def _loads_list(raw: str | None) -> list[str]:
    if not raw:
        return []
    try:
        value = json.loads(raw)
    except json.JSONDecodeError:
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    return []
