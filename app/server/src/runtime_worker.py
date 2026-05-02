from __future__ import annotations

import argparse
import asyncio
import signal

from src.config.settings import get_settings
from src.services.runtime_scheduler_service import (
    RuntimeSchedulerCoordinator,
    WORKER_SOURCE_DISCOVERY,
    WORKER_WAVE_MONITOR,
)


WORKER_CHOICES = [WORKER_SOURCE_DISCOVERY, WORKER_WAVE_MONITOR, "all"]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run 11Writer runtime workers outside the API process.")
    parser.add_argument(
        "--worker",
        choices=WORKER_CHOICES,
        default="all",
        help="Choose one worker or run both together.",
    )
    parser.add_argument("--once", action="store_true", help="Run one bounded cycle and exit.")
    parser.add_argument("--loop", action="store_true", help="Run continuously until stopped.")
    return parser


async def _run(worker: str, *, once: bool, loop: bool) -> None:
    settings = get_settings()
    coordinator = RuntimeSchedulerCoordinator(settings)
    if once or not loop:
        await _run_once(coordinator, worker)
        return

    stop_event = asyncio.Event()
    _install_signal_handlers(stop_event)
    tasks = _loop_tasks(coordinator, worker, stop_event)
    try:
        await asyncio.gather(*tasks)
    finally:
        stop_event.set()


async def _run_once(coordinator: RuntimeSchedulerCoordinator, worker: str) -> None:
    if worker in {WORKER_SOURCE_DISCOVERY, "all"}:
        await coordinator.run_source_discovery_cycle()
    if worker in {WORKER_WAVE_MONITOR, "all"}:
        await coordinator.run_wave_monitor_cycle()


def _loop_tasks(
    coordinator: RuntimeSchedulerCoordinator,
    worker: str,
    stop_event: asyncio.Event,
) -> list[asyncio.Task[None]]:
    tasks: list[asyncio.Task[None]] = []
    if worker in {WORKER_SOURCE_DISCOVERY, "all"}:
        tasks.append(asyncio.create_task(coordinator.source_discovery_loop(stop_event=stop_event)))
    if worker in {WORKER_WAVE_MONITOR, "all"}:
        tasks.append(asyncio.create_task(coordinator.wave_monitor_loop(stop_event=stop_event)))
    return tasks


def _install_signal_handlers(stop_event: asyncio.Event) -> None:
    loop = asyncio.get_running_loop()

    def _stop() -> None:
        stop_event.set()

    for signame in ("SIGINT", "SIGTERM"):
        sig = getattr(signal, signame, None)
        if sig is None:
            continue
        try:
            loop.add_signal_handler(sig, _stop)
        except (NotImplementedError, RuntimeError):
            continue


def main() -> None:
    args = build_parser().parse_args()
    asyncio.run(_run(args.worker, once=args.once, loop=args.loop))


if __name__ == "__main__":
    main()
