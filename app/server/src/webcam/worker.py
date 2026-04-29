from __future__ import annotations

import argparse
import asyncio

from src.config.settings import get_settings
from src.webcam.refresh import WebcamRefreshService, WebcamWorker


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the webcam refresh worker.")
    parser.add_argument("--once", action="store_true", help="Run one refresh cycle and exit.")
    parser.add_argument("--loop", action="store_true", help="Run the worker loop continuously.")
    parser.add_argument(
        "--validate-live",
        action="store_true",
        help="Run one bounded live-validation cycle against configured webcam sources.",
    )
    parser.add_argument(
        "--source",
        action="append",
        default=[],
        help="Restrict live validation to one or more webcam source keys.",
    )
    parser.add_argument(
        "--include-blocked",
        action="store_true",
        help="Allow live validation to attempt sources currently marked blocked.",
    )
    return parser


async def _run(once: bool, loop: bool, validate_live: bool, source: list[str], include_blocked: bool) -> None:
    settings = get_settings()
    refresh_service = WebcamRefreshService(settings)
    worker = WebcamWorker(refresh_service, poll_seconds=settings.webcam_worker_poll_seconds)
    if validate_live:
        await worker.run_live_validation(
            source_keys=source or None,
            include_blocked=include_blocked,
        )
        return
    if once or not loop:
        await worker.run_once()
        return
    await worker.run_loop()


def main() -> None:
    args = build_parser().parse_args()
    asyncio.run(_run(args.once, args.loop, args.validate_live, args.source, args.include_blocked))


if __name__ == "__main__":
    main()
