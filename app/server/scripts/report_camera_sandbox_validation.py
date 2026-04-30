from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.config.settings import Settings
from src.services.camera_sandbox_validation_report import (
    build_camera_sandbox_validation_report,
    render_camera_sandbox_validation_report,
)


async def _main() -> int:
    parser = argparse.ArgumentParser(
        description="Read-only webcam sandbox validation report."
    )
    parser.add_argument(
        "--source-id",
        default="finland-digitraffic-road-cameras",
        help="Sandbox-importable webcam source id to report.",
    )
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    args = parser.parse_args()

    try:
        report = await build_camera_sandbox_validation_report(
            Settings(),
            source_id=args.source_id,
        )
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(report.to_dict(), indent=2, sort_keys=True))
    else:
        print(render_camera_sandbox_validation_report(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(_main()))
