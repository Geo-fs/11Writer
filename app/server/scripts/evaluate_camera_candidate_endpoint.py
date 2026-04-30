from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.services.camera_endpoint_evaluator import evaluate_camera_candidate_endpoint


async def _main() -> int:
    parser = argparse.ArgumentParser(
        description="Lightweight webcam candidate endpoint evaluator. Read-only by default."
    )
    parser.add_argument("--url", required=True, help="Candidate endpoint URL to evaluate.")
    parser.add_argument("--source-id", help="Optional webcam source id for operator context.")
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    args = parser.parse_args()

    result = await evaluate_camera_candidate_endpoint(args.url)
    payload = result.to_dict()
    if args.source_id:
        payload["source_id"] = args.source_id

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        if args.source_id:
            print(f"Source: {args.source_id}")
        print(f"URL: {payload['url']}")
        print(f"Checked At: {payload['checked_at']}")
        print(f"HTTP Status: {payload['http_status']}")
        print(f"Content Type: {payload['content_type']}")
        print(f"Response Size (capped): {payload['response_size_capped']}")
        print(f"Detected Type: {payload['detected_machine_readable_type']}")
        print(f"Blocker Hints: {', '.join(payload['blocker_hints']) if payload['blocker_hints'] else 'none'}")
        print(f"Recommended Status: {payload['endpoint_verification_status']}")
        print(f"Result: {payload['result']}")
        if payload["notes"]:
            print("Notes:")
            for note in payload["notes"]:
                print(f"- {note}")
        print("Database write: disabled in this tool. Copy results into source inventory metadata manually.")

    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(_main()))
