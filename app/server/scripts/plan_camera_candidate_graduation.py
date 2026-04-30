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
    CameraCandidateEndpointReportItem,
    build_candidate_endpoint_report,
    select_candidate_sources,
)
from src.services.camera_candidate_graduation_plan import (
    build_camera_candidate_graduation_plan,
    render_camera_candidate_graduation_plan,
)
from src.services.camera_endpoint_evaluator import evaluate_camera_candidate_endpoint


async def _main() -> int:
    parser = argparse.ArgumentParser(
        description="Read-only webcam candidate graduation plan generator."
    )
    parser.add_argument("--source-id", help="Webcam source id to plan.")
    parser.add_argument("--url", help="Optional ad hoc or override candidate URL.")
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    args = parser.parse_args()

    if not args.source_id and not args.url:
        parser.error("at least one of --source-id or --url is required")

    report_item = await _resolve_report_item(
        Settings(),
        source_id=args.source_id,
        url=args.url,
    )
    plan = build_camera_candidate_graduation_plan(report_item)

    if args.json:
        print(json.dumps(plan.to_dict(), indent=2, sort_keys=True))
    else:
        print(render_camera_candidate_graduation_plan(plan))
    return 0


async def _resolve_report_item(
    settings: Settings,
    *,
    source_id: str | None,
    url: str | None,
) -> CameraCandidateEndpointReportItem:
    if source_id and not url:
        report = await build_candidate_endpoint_report(settings, source_id=source_id, limit=1)
        if not report:
            raise SystemExit(f"No webcam source with a candidate endpoint URL matched '{source_id}'.")
        return report[0]

    if source_id and url:
        sources = select_candidate_sources(settings, source_id=source_id, limit=1)
        source = sources[0] if sources else None
        evaluation = await evaluate_camera_candidate_endpoint(url)
        notes = list(evaluation.notes)
        if source and source.blocked_reason:
            notes.append(f"Blocked reason: {source.blocked_reason}")
        if source and source.verification_caveat:
            notes.append(f"Caveat: {source.verification_caveat}")
        return CameraCandidateEndpointReportItem(
            source_id=source.key if source else source_id,
            source_name=source.source_name if source else source_id,
            onboarding_state=source.onboarding_state if source else "candidate",
            import_readiness=source.import_readiness if source else None,
            candidate_url=url,
            http_status=evaluation.http_status,
            content_type=evaluation.content_type,
            detected_machine_readable_type=evaluation.detected_machine_readable_type,
            blocker_hints=list(evaluation.blocker_hints),
            endpoint_verification_status=evaluation.endpoint_verification_status,
            notes=notes,
            next_action="needs manual endpoint research",
        )

    assert url is not None
    evaluation = await evaluate_camera_candidate_endpoint(url)
    return CameraCandidateEndpointReportItem(
        source_id="ad-hoc-candidate",
        source_name="Ad hoc camera candidate",
        onboarding_state="candidate",
        import_readiness=None,
        candidate_url=url,
        http_status=evaluation.http_status,
        content_type=evaluation.content_type,
        detected_machine_readable_type=evaluation.detected_machine_readable_type,
        blocker_hints=list(evaluation.blocker_hints),
        endpoint_verification_status=evaluation.endpoint_verification_status,
        notes=list(evaluation.notes),
        next_action="needs manual endpoint research",
    )


if __name__ == "__main__":
    raise SystemExit(asyncio.run(_main()))
