from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from sqlalchemy import select

from src.config.settings import Settings
from src.services.source_discovery_service import SourceDiscoveryService
from src.services.wave_monitor_service import WaveMonitorService
from src.source_discovery.db import session_scope
from src.source_discovery.models import RuntimeSchedulerRunORM, RuntimeSchedulerWorkerORM
from src.types.source_discovery import (
    SourceDiscoveryRuntimeControlRequest,
    SourceDiscoveryRuntimeControlResponse,
    SourceDiscoveryRuntimeRunSummary,
    SourceDiscoveryRuntimeServiceBundleResponse,
    SourceDiscoveryRuntimeServiceSpec,
    SourceDiscoveryRuntimeStatusResponse,
    SourceDiscoveryRuntimeWorkerSummary,
    SourceDiscoverySchedulerTickRequest,
)


WORKER_SOURCE_DISCOVERY = "source_discovery"
WORKER_WAVE_MONITOR = "wave_monitor"
PROCESS_OWNER = f"pid-{os.getpid()}-{uuid4().hex[:8]}"
SERVICE_ENTRYPOINT_MODULE = "src.runtime_worker"
SERVER_WORKDIR = Path(__file__).resolve().parents[2]


@dataclass
class _WorkerState:
    enabled: bool = False
    running: bool = False
    poll_seconds: int = 0


@dataclass
class _RuntimeSchedulerState:
    runtime_mode: str = "desktop-sidecar"
    source_discovery: _WorkerState = field(default_factory=_WorkerState)
    wave_monitor: _WorkerState = field(default_factory=_WorkerState)


_STATE = _RuntimeSchedulerState()


def configure_runtime_scheduler_state(settings: Settings) -> None:
    _STATE.runtime_mode = settings.app_runtime_mode
    _STATE.source_discovery.enabled = settings.source_discovery_scheduler_enabled
    _STATE.source_discovery.poll_seconds = max(1, settings.source_discovery_scheduler_poll_seconds)
    _STATE.wave_monitor.enabled = settings.wave_monitor_scheduler_enabled
    _STATE.wave_monitor.poll_seconds = max(1, settings.wave_monitor_scheduler_poll_seconds)


def build_runtime_status(settings: Settings) -> SourceDiscoveryRuntimeStatusResponse:
    configure_runtime_scheduler_state(settings)
    _ensure_worker_rows(settings)
    workers = _load_worker_summaries(settings)
    source_worker = next(worker for worker in workers if worker.worker_name == WORKER_SOURCE_DISCOVERY)
    wave_worker = next(worker for worker in workers if worker.worker_name == WORKER_WAVE_MONITOR)
    service_managers = _supported_service_managers()
    return SourceDiscoveryRuntimeStatusResponse(
        runtime_mode=_STATE.runtime_mode,
        recommended_runtime_deployment="os-managed-service" if service_managers else "embedded-preview",
        service_worker_entrypoint=f"{sys.executable} -m {SERVICE_ENTRYPOINT_MODULE}",
        supported_service_managers=service_managers,
        source_discovery_scheduler_enabled=source_worker.enabled_by_config,
        source_discovery_scheduler_running=source_worker.loop_active_in_process,
        source_discovery_scheduler_poll_seconds=source_worker.poll_seconds,
        source_discovery_scheduler_last_tick_at=source_worker.last_tick_finished_at,
        source_discovery_scheduler_last_error=source_worker.last_error,
        source_discovery_scheduler_last_summary=source_worker.last_summary,
        wave_monitor_scheduler_enabled=wave_worker.enabled_by_config,
        wave_monitor_scheduler_running=wave_worker.loop_active_in_process,
        wave_monitor_scheduler_poll_seconds=wave_worker.poll_seconds,
        wave_monitor_scheduler_last_tick_at=wave_worker.last_tick_finished_at,
        wave_monitor_scheduler_last_error=wave_worker.last_error,
        wave_monitor_scheduler_last_summary=wave_worker.last_summary,
        workers=workers,
        caveats=[
            "Runtime scheduler state and leases are persisted in the Source Discovery database.",
            "Embedded FastAPI startup loops remain available for preview, but long-running backend deployment should use the dedicated runtime worker entrypoint and OS service manager.",
            "Duplicate-worker protection prefers skipping over double-running.",
        ],
    )


def build_runtime_service_bundle(
    settings: Settings,
    *,
    platform_name: str | None = None,
) -> SourceDiscoveryRuntimeServiceBundleResponse:
    current_platform = _current_service_platform(platform_name)
    return SourceDiscoveryRuntimeServiceBundleResponse(
        runtime_mode=settings.app_runtime_mode,
        current_platform=current_platform,  # type: ignore[arg-type]
        entrypoint_module=SERVICE_ENTRYPOINT_MODULE,
        services=_service_specs(current_platform),
        caveats=[
            "Generated artifacts are user-level service-manager templates; install them from the app/server working directory.",
            "Each worker should run as its own long-lived process so lease coordination can skip duplicates safely.",
            "Embedded startup loops are still useful for development preview, but backend-only deployment should prefer these service artifacts.",
        ],
    )


def should_start_source_discovery_scheduler(settings: Settings) -> bool:
    return settings.source_discovery_scheduler_enabled and settings.source_discovery_scheduler_run_on_startup


def should_start_wave_monitor_scheduler(settings: Settings) -> bool:
    return settings.wave_monitor_scheduler_enabled and settings.wave_monitor_scheduler_run_on_startup


def control_runtime_worker(
    settings: Settings,
    worker_name: str,
    request: SourceDiscoveryRuntimeControlRequest,
) -> SourceDiscoveryRuntimeControlResponse:
    if worker_name not in {WORKER_SOURCE_DISCOVERY, WORKER_WAVE_MONITOR}:
        raise ValueError(f"Unsupported runtime worker: {worker_name}")
    _ensure_worker_rows(settings)
    if request.action == "run_now":
        run = RuntimeSchedulerCoordinator(settings).run_worker_now(worker_name, requested_by=request.requested_by)
        worker = next(worker for worker in _load_worker_summaries(settings) if worker.worker_name == worker_name)
        return SourceDiscoveryRuntimeControlResponse(
            worker=worker,
            run=run,
            caveats=[
                "Manual run-now is bounded and still respects lease safety and review-only automation rules.",
            ],
        )

    with session_scope(settings.source_discovery_database_url) as session:
        row = _get_or_create_worker_row(session, settings, worker_name)
        if request.action == "pause":
            row.desired_state = "paused"
        elif request.action == "resume":
            row.desired_state = "running"
        elif request.action == "stop":
            row.desired_state = "stopped"
        else:
            raise ValueError(f"Unsupported runtime control action: {request.action}")
        row.updated_at = _utc_now()
        session.flush()

    worker = next(worker for worker in _load_worker_summaries(settings) if worker.worker_name == worker_name)
    return SourceDiscoveryRuntimeControlResponse(
        worker=worker,
        run=None,
        caveats=[
            "Control changes persist immediately, but existing background loops observe them on their next poll boundary.",
        ],
    )


class RuntimeSchedulerCoordinator:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        configure_runtime_scheduler_state(settings)
        _ensure_worker_rows(settings)

    async def source_discovery_loop(self, *, stop_event: asyncio.Event) -> None:
        _STATE.source_discovery.running = True
        try:
            while not stop_event.is_set():
                self._run_source_discovery_cycle_sync(trigger_kind="scheduled", requested_by="runtime-loop")
                try:
                    await asyncio.wait_for(stop_event.wait(), timeout=_STATE.source_discovery.poll_seconds)
                except asyncio.TimeoutError:
                    continue
        finally:
            _STATE.source_discovery.running = False

    async def wave_monitor_loop(self, *, stop_event: asyncio.Event) -> None:
        _STATE.wave_monitor.running = True
        try:
            while not stop_event.is_set():
                await self._run_wave_monitor_cycle_async(trigger_kind="scheduled", requested_by="runtime-loop")
                try:
                    await asyncio.wait_for(stop_event.wait(), timeout=_STATE.wave_monitor.poll_seconds)
                except asyncio.TimeoutError:
                    continue
        finally:
            _STATE.wave_monitor.running = False

    async def run_source_discovery_cycle(self) -> None:
        self._run_source_discovery_cycle_sync(trigger_kind="scheduled", requested_by="runtime-loop")

    async def run_wave_monitor_cycle(self) -> None:
        await self._run_wave_monitor_cycle_async(trigger_kind="scheduled", requested_by="runtime-loop")

    def run_worker_now(self, worker_name: str, *, requested_by: str) -> SourceDiscoveryRuntimeRunSummary:
        if worker_name == WORKER_SOURCE_DISCOVERY:
            return self._run_source_discovery_cycle_sync(
                trigger_kind="manual",
                requested_by=requested_by,
                ignore_state=True,
            )
        if worker_name == WORKER_WAVE_MONITOR:
            return asyncio.run(
                self._run_wave_monitor_cycle_async(
                    trigger_kind="manual",
                    requested_by=requested_by,
                    ignore_state=True,
                )
            )
        raise ValueError(f"Unsupported runtime worker: {worker_name}")

    def _run_source_discovery_cycle_sync(
        self,
        *,
        trigger_kind: str,
        requested_by: str,
        ignore_state: bool = False,
    ) -> SourceDiscoveryRuntimeRunSummary:
        worker_name = WORKER_SOURCE_DISCOVERY
        now = _utc_now()
        run = self._prepare_worker_run(
            worker_name,
            trigger_kind=trigger_kind,
            requested_by=requested_by,
            ignore_state=ignore_state,
            now=now,
        )
        if run.status != "running":
            return run
        try:
            summary = self._execute_source_discovery_cycle()
            return self._complete_worker_run(worker_name, run.run_id, summary=summary)
        except Exception as exc:  # noqa: BLE001
            return self._fail_worker_run(worker_name, run.run_id, error_summary=str(exc)[:400])

    async def _run_wave_monitor_cycle_async(
        self,
        *,
        trigger_kind: str,
        requested_by: str,
        ignore_state: bool = False,
    ) -> SourceDiscoveryRuntimeRunSummary:
        worker_name = WORKER_WAVE_MONITOR
        now = _utc_now()
        run = self._prepare_worker_run(
            worker_name,
            trigger_kind=trigger_kind,
            requested_by=requested_by,
            ignore_state=ignore_state,
            now=now,
        )
        if run.status != "running":
            return run
        try:
            summary = await self._execute_wave_monitor_cycle()
            return self._complete_worker_run(worker_name, run.run_id, summary=summary)
        except Exception as exc:  # noqa: BLE001
            return self._fail_worker_run(worker_name, run.run_id, error_summary=str(exc)[:400])

    def _prepare_worker_run(
        self,
        worker_name: str,
        *,
        trigger_kind: str,
        requested_by: str,
        ignore_state: bool,
        now: str,
    ) -> SourceDiscoveryRuntimeRunSummary:
        _ensure_worker_rows(self._settings)
        with session_scope(self._settings.source_discovery_database_url) as session:
            worker = _get_or_create_worker_row(session, self._settings, worker_name)
            worker.last_tick_requested_at = now
            worker.updated_at = now
            if not ignore_state and worker.desired_state != "running":
                worker.last_status = f"skipped_{worker.desired_state}"
                worker.last_summary = f"Skipped because desired state is {worker.desired_state}."
                row = _create_runtime_run(
                    session,
                    worker_name=worker_name,
                    trigger_kind=trigger_kind,
                    requested_by=requested_by,
                    status=worker.last_status,
                    started_at=now,
                    finished_at=now,
                    lease_owner=None,
                    summary=worker.last_summary,
                    error_summary=None,
                )
                session.flush()
                return _serialize_runtime_run(row)
            if not _acquire_lease(worker, now, ttl_seconds=max(30, worker.poll_seconds * 2)):
                summary = "Skipped because another backend instance currently owns the worker lease."
                worker.last_status = "skipped_lease"
                worker.last_summary = summary
                row = _create_runtime_run(
                    session,
                    worker_name=worker_name,
                    trigger_kind=trigger_kind,
                    requested_by=requested_by,
                    status="skipped_lease",
                    started_at=now,
                    finished_at=now,
                    lease_owner=worker.lease_owner,
                    summary=summary,
                    error_summary=None,
                )
                session.flush()
                return _serialize_runtime_run(row)
            row = _create_runtime_run(
                session,
                worker_name=worker_name,
                trigger_kind=trigger_kind,
                requested_by=requested_by,
                status="running",
                started_at=now,
                finished_at=None,
                lease_owner=PROCESS_OWNER,
                summary=None,
                error_summary=None,
            )
            worker.last_tick_started_at = now
            worker.last_status = "running"
            worker.last_error = None
            session.flush()
            return _serialize_runtime_run(row)

    def _complete_worker_run(self, worker_name: str, run_id: str, *, summary: str) -> SourceDiscoveryRuntimeRunSummary:
        finished_at = _utc_now()
        with session_scope(self._settings.source_discovery_database_url) as session:
            worker = _get_or_create_worker_row(session, self._settings, worker_name)
            row = session.get(RuntimeSchedulerRunORM, run_id)
            worker.last_tick_finished_at = finished_at
            worker.last_status = "completed"
            worker.last_summary = summary
            worker.last_error = None
            _release_lease(worker)
            if row is not None:
                row.status = "completed"
                row.finished_at = finished_at
                row.summary = summary
                row.error_summary = None
            session.flush()
            return _serialize_runtime_run(row) if row is not None else SourceDiscoveryRuntimeRunSummary(
                run_id=run_id,
                worker_name=worker_name,  # type: ignore[arg-type]
                trigger_kind="unknown",
                status="completed",
                requested_by=None,
                lease_owner=None,
                started_at=finished_at,
                finished_at=finished_at,
                summary=summary,
                error_summary=None,
            )

    def _fail_worker_run(self, worker_name: str, run_id: str, *, error_summary: str) -> SourceDiscoveryRuntimeRunSummary:
        finished_at = _utc_now()
        with session_scope(self._settings.source_discovery_database_url) as session:
            worker = _get_or_create_worker_row(session, self._settings, worker_name)
            row = session.get(RuntimeSchedulerRunORM, run_id)
            worker.last_tick_finished_at = finished_at
            worker.last_status = "failed"
            worker.last_summary = None
            worker.last_error = error_summary
            _release_lease(worker)
            if row is not None:
                row.status = "failed"
                row.finished_at = finished_at
                row.summary = None
                row.error_summary = error_summary
            session.flush()
            return _serialize_runtime_run(row) if row is not None else SourceDiscoveryRuntimeRunSummary(
                run_id=run_id,
                worker_name=worker_name,  # type: ignore[arg-type]
                trigger_kind="unknown",
                status="failed",
                requested_by=None,
                lease_owner=None,
                started_at=finished_at,
                finished_at=finished_at,
                summary=None,
                error_summary=error_summary,
            )

    def _execute_source_discovery_cycle(self) -> str:
        response = SourceDiscoveryService(self._settings).run_scheduler_tick(
            SourceDiscoverySchedulerTickRequest(
                health_check_limit=max(0, self._settings.source_discovery_scheduler_health_check_limit),
                record_source_extract_limit=max(0, self._settings.source_discovery_scheduler_record_extract_limit),
                llm_task_limit=max(0, self._settings.source_discovery_scheduler_llm_task_limit),
                llm_provider=self._settings.wave_llm_default_provider,
                llm_allow_network=self._settings.source_discovery_scheduler_allow_network,
                request_budget=max(0, self._settings.source_discovery_scheduler_request_budget),
                caveats=[f"Runtime worker execution in {self._settings.app_runtime_mode}."],
            )
        )
        return (
            f"health={response.health_checks_completed}, "
            f"recordExtract={response.record_extract_jobs_completed}, "
            f"llm={response.llm_tasks_completed}, "
            f"usedRequests={response.used_requests}"
        )

    async def _execute_wave_monitor_cycle(self) -> str:
        response = await WaveMonitorService(self._settings).scheduler_tick()
        return (
            f"eligible={response.eligible_connectors}, "
            f"success={response.successful_runs}, "
            f"records={response.records_created}, "
            f"signals={response.signals_created}"
        )


def _ensure_worker_rows(settings: Settings) -> None:
    specs = _worker_specs(settings)
    now = _utc_now()
    with session_scope(settings.source_discovery_database_url) as session:
        for worker_name, spec in specs.items():
            row = session.get(RuntimeSchedulerWorkerORM, worker_name)
            if row is None:
                row = RuntimeSchedulerWorkerORM(
                    worker_name=worker_name,
                    desired_state="running" if spec["enabled"] else "stopped",
                    enabled_by_config=bool(spec["enabled"]),
                    poll_seconds=int(spec["poll_seconds"]),
                    lease_owner=None,
                    lease_expires_at=None,
                    last_tick_requested_at=None,
                    last_tick_started_at=None,
                    last_tick_finished_at=None,
                    last_status=None,
                    last_error=None,
                    last_summary=None,
                    updated_at=now,
                )
                session.add(row)
            else:
                row.enabled_by_config = bool(spec["enabled"])
                row.poll_seconds = int(spec["poll_seconds"])
                row.updated_at = now
        session.flush()


def _worker_specs(settings: Settings) -> dict[str, dict[str, object]]:
    return {
        WORKER_SOURCE_DISCOVERY: {
            "enabled": settings.source_discovery_scheduler_enabled,
            "poll_seconds": max(1, settings.source_discovery_scheduler_poll_seconds),
        },
        WORKER_WAVE_MONITOR: {
            "enabled": settings.wave_monitor_scheduler_enabled,
            "poll_seconds": max(1, settings.wave_monitor_scheduler_poll_seconds),
        },
    }


def _supported_service_managers() -> list[str]:
    return ["task-scheduler", "launchd", "systemd-user"]


def _current_service_platform(platform_name: str | None = None) -> str:
    if platform_name:
        normalized = platform_name.strip().casefold()
    else:
        normalized = sys.platform.casefold()
    if normalized.startswith("win"):
        return "windows"
    if normalized.startswith("darwin") or normalized == "macos":
        return "macos"
    if normalized.startswith("linux"):
        return "linux"
    raise ValueError(f"Unsupported runtime service platform: {platform_name or sys.platform}")


def _service_specs(platform_name: str) -> list[SourceDiscoveryRuntimeServiceSpec]:
    if platform_name == "windows":
        return [_windows_task_spec(WORKER_SOURCE_DISCOVERY), _windows_task_spec(WORKER_WAVE_MONITOR)]
    if platform_name == "macos":
        return [_launchd_spec(WORKER_SOURCE_DISCOVERY), _launchd_spec(WORKER_WAVE_MONITOR)]
    if platform_name == "linux":
        return [_systemd_user_spec(WORKER_SOURCE_DISCOVERY), _systemd_user_spec(WORKER_WAVE_MONITOR)]
    raise ValueError(f"Unsupported runtime service platform: {platform_name}")


def _entry_command(worker_name: str) -> list[str]:
    return [sys.executable, "-m", SERVICE_ENTRYPOINT_MODULE, "--worker", worker_name, "--loop"]


def _service_name(worker_name: str) -> str:
    suffix = "source-discovery" if worker_name == WORKER_SOURCE_DISCOVERY else "wave-monitor"
    return f"11writer-{suffix}"


def _windows_task_spec(worker_name: str) -> SourceDiscoveryRuntimeServiceSpec:
    service_name = _service_name(worker_name)
    entry = _entry_command(worker_name)
    quoted_entry = " ".join(f'"{part}"' if " " in part or part.endswith(".exe") else part for part in entry)
    artifact_text = (
        f'$taskName = "{service_name}"\n'
        f'$workdir = "{SERVER_WORKDIR}"\n'
        f'$command = "{quoted_entry}"\n'
        'schtasks /Create /TN $taskName /SC ONLOGON /RL LIMITED /F '
        '/TR ("cmd.exe /c cd /d `"" + $workdir + "`" && " + $command)\n'
    )
    return SourceDiscoveryRuntimeServiceSpec(
        worker_name=worker_name,  # type: ignore[arg-type]
        platform="windows",
        service_manager="task-scheduler",
        service_name=service_name,
        working_directory=str(SERVER_WORKDIR),
        artifact_file_name=f"{service_name}.ps1",
        artifact_text=artifact_text,
        entry_command=entry,
        install_command=["schtasks", "/Create", "/TN", service_name, "/SC", "ONLOGON", "/RL", "LIMITED", "/F"],
        uninstall_command=["schtasks", "/Delete", "/TN", service_name, "/F"],
        caveats=[
            "Windows uses Task Scheduler here so the worker can run without claiming an admin-only Windows Service install.",
            "The task action should start one long-lived worker process per backend worker.",
        ],
    )


def _launchd_spec(worker_name: str) -> SourceDiscoveryRuntimeServiceSpec:
    service_name = f"invalid.local.{_service_name(worker_name)}"
    entry = _entry_command(worker_name)
    arguments = "\n".join(f"      <string>{part}</string>" for part in entry)
    artifact_text = (
        "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
        "<!DOCTYPE plist PUBLIC \"-//Apple//DTD PLIST 1.0//EN\" "
        "\"http://www.apple.com/DTDs/PropertyList-1.0.dtd\">\n"
        "<plist version=\"1.0\">\n"
        "  <dict>\n"
        f"    <key>Label</key><string>{service_name}</string>\n"
        "    <key>ProgramArguments</key>\n"
        "    <array>\n"
        f"{arguments}\n"
        "    </array>\n"
        f"    <key>WorkingDirectory</key><string>{SERVER_WORKDIR}</string>\n"
        "    <key>RunAtLoad</key><true/>\n"
        "    <key>KeepAlive</key><true/>\n"
        "  </dict>\n"
        "</plist>\n"
    )
    artifact_file_name = f"{service_name}.plist"
    return SourceDiscoveryRuntimeServiceSpec(
        worker_name=worker_name,  # type: ignore[arg-type]
        platform="macos",
        service_manager="launchd",
        service_name=service_name,
        working_directory=str(SERVER_WORKDIR),
        artifact_file_name=artifact_file_name,
        artifact_text=artifact_text,
        entry_command=entry,
        install_command=["launchctl", "bootstrap", "gui/$(id -u)", f"~/Library/LaunchAgents/{artifact_file_name}"],
        uninstall_command=["launchctl", "bootout", "gui/$(id -u)", service_name],
        caveats=[
            "Install the plist into ~/Library/LaunchAgents for per-user backend-only operation.",
            "launchd should own the long-running worker lifecycle instead of embedding the loop in the API process.",
        ],
    )


def _systemd_user_spec(worker_name: str) -> SourceDiscoveryRuntimeServiceSpec:
    service_name = f"{_service_name(worker_name)}.service"
    entry = _entry_command(worker_name)
    exec_start = " ".join(f'"{part}"' if " " in part or part.endswith(".exe") else part for part in entry)
    artifact_text = (
        "[Unit]\n"
        f"Description=11Writer runtime worker ({worker_name})\n\n"
        "[Service]\n"
        "Type=simple\n"
        f"WorkingDirectory={SERVER_WORKDIR}\n"
        f"ExecStart={exec_start}\n"
        "Restart=always\n"
        "RestartSec=5\n\n"
        "[Install]\n"
        "WantedBy=default.target\n"
    )
    return SourceDiscoveryRuntimeServiceSpec(
        worker_name=worker_name,  # type: ignore[arg-type]
        platform="linux",
        service_manager="systemd-user",
        service_name=service_name,
        working_directory=str(SERVER_WORKDIR),
        artifact_file_name=service_name,
        artifact_text=artifact_text,
        entry_command=entry,
        install_command=["systemctl", "--user", "enable", "--now", service_name],
        uninstall_command=["systemctl", "--user", "disable", "--now", service_name],
        caveats=[
            "This slice generates a user-level systemd unit, not a privileged system service.",
            "Copy the unit into ~/.config/systemd/user before enabling it.",
        ],
    )


def _load_worker_summaries(settings: Settings) -> list[SourceDiscoveryRuntimeWorkerSummary]:
    with session_scope(settings.source_discovery_database_url) as session:
        rows = list(session.scalars(select(RuntimeSchedulerWorkerORM).order_by(RuntimeSchedulerWorkerORM.worker_name)))
        runs = list(session.scalars(select(RuntimeSchedulerRunORM).order_by(RuntimeSchedulerRunORM.started_at.desc()).limit(40)))
        grouped_runs: dict[str, list[RuntimeSchedulerRunORM]] = {WORKER_SOURCE_DISCOVERY: [], WORKER_WAVE_MONITOR: []}
        for run in runs:
            grouped_runs.setdefault(run.worker_name, []).append(run)
        summaries: list[SourceDiscoveryRuntimeWorkerSummary] = []
        for row in rows:
            loop_active = _STATE.source_discovery.running if row.worker_name == WORKER_SOURCE_DISCOVERY else _STATE.wave_monitor.running
            summaries.append(
                SourceDiscoveryRuntimeWorkerSummary(
                    worker_name=row.worker_name,  # type: ignore[arg-type]
                    desired_state=row.desired_state,  # type: ignore[arg-type]
                    enabled_by_config=row.enabled_by_config,
                    poll_seconds=row.poll_seconds,
                    loop_active_in_process=loop_active,
                    lease_owner=row.lease_owner,
                    lease_expires_at=row.lease_expires_at,
                    last_tick_requested_at=row.last_tick_requested_at,
                    last_tick_started_at=row.last_tick_started_at,
                    last_tick_finished_at=row.last_tick_finished_at,
                    last_status=row.last_status,
                    last_error=row.last_error,
                    last_summary=row.last_summary,
                    recent_runs=[_serialize_runtime_run(run) for run in grouped_runs.get(row.worker_name, [])[:10]],
                )
            )
        return summaries


def _get_or_create_worker_row(session, settings: Settings, worker_name: str) -> RuntimeSchedulerWorkerORM:
    row = session.get(RuntimeSchedulerWorkerORM, worker_name)
    if row is not None:
        return row
    spec = _worker_specs(settings)[worker_name]
    now = _utc_now()
    row = RuntimeSchedulerWorkerORM(
        worker_name=worker_name,
        desired_state="running" if spec["enabled"] else "stopped",
        enabled_by_config=bool(spec["enabled"]),
        poll_seconds=int(spec["poll_seconds"]),
        updated_at=now,
    )
    session.add(row)
    session.flush()
    return row


def _create_runtime_run(
    session,
    *,
    worker_name: str,
    trigger_kind: str,
    requested_by: str | None,
    status: str,
    started_at: str,
    finished_at: str | None,
    lease_owner: str | None,
    summary: str | None,
    error_summary: str | None,
) -> RuntimeSchedulerRunORM:
    row = RuntimeSchedulerRunORM(
        run_id=f"runtime-run:{worker_name}:{_compact_timestamp(started_at)}:{uuid4().hex[:8]}",
        worker_name=worker_name,
        trigger_kind=trigger_kind,
        status=status,
        requested_by=requested_by,
        lease_owner=lease_owner,
        started_at=started_at,
        finished_at=finished_at,
        summary=summary,
        error_summary=error_summary,
    )
    session.add(row)
    session.flush()
    return row


def _acquire_lease(worker: RuntimeSchedulerWorkerORM, now: str, *, ttl_seconds: int) -> bool:
    current = _parse_utc_like(now) or datetime.now(tz=timezone.utc)
    lease_expires_at = _parse_utc_like(worker.lease_expires_at)
    if worker.lease_owner and worker.lease_owner != PROCESS_OWNER and lease_expires_at and lease_expires_at > current:
        return False
    worker.lease_owner = PROCESS_OWNER
    worker.lease_expires_at = (current + timedelta(seconds=max(30, ttl_seconds))).isoformat().replace("+00:00", "Z")
    return True


def _release_lease(worker: RuntimeSchedulerWorkerORM) -> None:
    worker.lease_owner = None
    worker.lease_expires_at = None
    worker.updated_at = _utc_now()


def _serialize_runtime_run(row: RuntimeSchedulerRunORM) -> SourceDiscoveryRuntimeRunSummary:
    return SourceDiscoveryRuntimeRunSummary(
        run_id=row.run_id,
        worker_name=row.worker_name,  # type: ignore[arg-type]
        trigger_kind=row.trigger_kind,
        status=row.status,
        requested_by=row.requested_by,
        lease_owner=row.lease_owner,
        started_at=row.started_at,
        finished_at=row.finished_at,
        summary=row.summary,
        error_summary=row.error_summary,
    )


def _parse_utc_like(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
    except ValueError:
        return None


def _utc_now() -> str:
    return datetime.now(tz=timezone.utc).isoformat().replace("+00:00", "Z")


def _compact_timestamp(value: str) -> str:
    return re.sub(r"[^0-9]", "", value)[:20]
