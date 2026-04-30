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
from src.services.camera_candidate_endpoint_report import (
    build_candidate_endpoint_report,
    render_candidate_endpoint_report,
)


async def _main() -> int:
    parser = argparse.ArgumentParser(
        description="Read-only webcam candidate endpoint evaluation report."
    )
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    parser.add_argument("--limit", type=int, help="Optional limit on candidate sources to evaluate.")
    parser.add_argument("--source-id", help="Optional webcam source id to evaluate explicitly.")
    args = parser.parse_args()

    report = await build_candidate_endpoint_report(
        Settings(),
        source_id=args.source_id,
        limit=args.limit,
    )

    if args.json:
        print(json.dumps([item.to_dict() for item in report], indent=2, sort_keys=True))
    else:
        print(render_candidate_endpoint_report(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(_main()))
