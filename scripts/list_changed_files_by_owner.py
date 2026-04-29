#!/usr/bin/env python3
"""List changed files grouped by likely owning agent/task.

This script is heuristic. It is intended to help with local multi-agent
consolidation planning and does not replace manual diff review.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import OrderedDict
from pathlib import Path


GROUPS = [
    "connect-tooling",
    "gather-ui-integration",
    "geospatial-environmental",
    "aerospace",
    "marine",
    "features-webcam",
    "shared-high-collision",
    "unknown",
]

HIGH_COLLISION_GROUP = "shared-high-collision"
DOC_LINKS = [
    "app/docs/active-agent-worktree.md",
    "app/docs/commit-groups.current.md",
    "app/docs/validation-matrix.md",
    "app/docs/release-readiness.md",
]


def run_git_status(repo_root: Path) -> list[str]:
    result = subprocess.run(
        ["git", "status", "--short", "--branch"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.splitlines()


def parse_status(lines: list[str]) -> tuple[str | None, list[dict[str, str]]]:
    branch = None
    entries: list[dict[str, str]] = []
    for line in lines:
        if not line:
            continue
        if line.startswith("## "):
            branch = line[3:].strip()
            continue
        if len(line) < 4:
            continue
        status = line[:2]
        path = line[3:].strip()
        if " -> " in path:
            path = path.split(" -> ", 1)[1].strip()
        if path:
            entries.append({"status": status, "path": path.replace("\\", "/")})
    return branch, entries


def is_connect_tooling(path: str) -> bool:
    return path in {
        "app/docs/repo-workflow.md",
        "app/docs/active-agent-worktree.md",
        "app/docs/commit-groups.current.md",
        "app/docs/validation-matrix.md",
        "app/docs/release-readiness.md",
        "app/server/tests/run_playwright_smoke.py",
    } or path.startswith("scripts/")


def is_gather_ui_integration(path: str) -> bool:
    # Imagery presentation files may originate from geospatial work, but for the
    # current multi-agent consolidation pass we classify them under shared UI
    # integration because the edits are about presentation/primitive alignment.
    # Manual diff review still wins over this heuristic.
    return (
        path.startswith("app/client/src/components/ui/")
        or path.startswith("app/client/src/features/imagery/")
        or path == "app/client/src/styles/ui-primitives.css"
        or path == "app/docs/ui-integration.md"
        or path == "app/docs/data-source-backlog.md"
        or path == "app/docs/data-source-integration-rules.md"
        or path == "app/docs/data-source-registry.md"
        or path == "app/docs/data_sources.noauth.registry.json"
    )


def is_geospatial_environmental(path: str) -> bool:
    if path.startswith("app/client/src/features/environmental/"):
        return True
    if path.startswith("app/docs/environmental-events"):
        return True
    if path in {
        "app/server/src/services/eonet_service.py",
        "app/server/src/services/earthquake_service.py",
        "app/server/src/routes/events.py",
        "app/server/tests/test_eonet_events.py",
        "app/server/tests/test_earthquake_events.py",
        "app/client/src/layers/EonetLayer.tsx",
        "app/client/src/layers/EarthquakeLayer.tsx",
    }:
        return True
    if path.startswith("app/server/data/") and (
        "eonet" in path.lower() or "earthquake" in path.lower()
    ):
        return True
    return False


def is_aerospace(path: str) -> bool:
    return (
        path in {
            "app/client/src/layers/AircraftLayer.tsx",
            "app/client/src/layers/SatelliteLayer.tsx",
            "app/docs/aircraft-satellite-smoke.md",
        }
        or path.startswith("app/client/src/features/inspector/aerospace")
    )


def is_marine(path: str) -> bool:
    return (
        path.startswith("app/client/src/features/marine/")
        or path == "app/docs/marine-module.md"
        or path == "app/server/tests/test_marine_contracts.py"
    )


def is_features_webcam(path: str) -> bool:
    return (
        path.startswith("app/client/src/features/webcams/")
        or path == "app/client/src/features/layers/WebcamOperationsPanel.tsx"
        or path == "app/client/src/layers/CameraLayer.tsx"
        or path == "app/docs/webcams.md"
        or path == "app/server/tests/test_webcam_module.py"
    )


def is_shared_high_collision(path: str) -> bool:
    return path in {
        "app/client/src/features/app-shell/AppShell.tsx",
        "app/client/src/features/layers/LayerPanel.tsx",
        "app/client/src/features/inspector/InspectorPanel.tsx",
        "app/client/src/lib/store.ts",
        "app/client/src/lib/queries.ts",
        "app/client/src/styles/global.css",
        "app/client/src/types/api.ts",
        "app/client/src/types/entities.ts",
        "app/client/scripts/playwright_smoke.mjs",
        "app/server/tests/smoke_fixture_app.py",
        "app/server/src/types/api.py",
        "app/server/src/config/settings.py",
    }


def classify(path: str) -> str:
    if is_connect_tooling(path):
        return "connect-tooling"
    if is_gather_ui_integration(path):
        return "gather-ui-integration"
    if is_geospatial_environmental(path):
        return "geospatial-environmental"
    if is_aerospace(path):
        return "aerospace"
    if is_marine(path):
        return "marine"
    if is_features_webcam(path):
        return "features-webcam"
    if is_shared_high_collision(path):
        return "shared-high-collision"
    return "unknown"


def build_groups(files: list[str]) -> OrderedDict[str, list[str]]:
    grouped: OrderedDict[str, list[str]] = OrderedDict((group, []) for group in GROUPS)
    for path in files:
        grouped[classify(path)].append(path)
    return grouped


def build_json(branch: str | None, grouped: OrderedDict[str, list[str]], only: str | None) -> dict:
    items = grouped.items() if only is None else [(only, grouped[only])]
    groups = {
        name: {"count": len(files), "files": files}
        for name, files in items
        if files or name == "unknown"
    }
    unknown_files = grouped["unknown"] if only is None else (grouped[only] if only == "unknown" else [])
    return {
        "branch": branch,
        "groups": groups,
        "unmatched_count": len(unknown_files),
    }


def print_text(branch: str | None, grouped: OrderedDict[str, list[str]], only: str | None) -> None:
    if branch:
        print(f"Branch: {branch}")
    total = sum(len(files) for files in grouped.values())
    print(f"Changed paths: {total}")
    print("Heuristic grouping only; manual diff review is still required.")
    print()

    items = grouped.items() if only is None else [(only, grouped[only])]
    for name, files in items:
        if not files and name != "unknown":
            continue
        print(f"{name} ({len(files)})")
        if not files:
            print("  (none)")
        else:
            for path in files:
                print(f"  - {path}")
        print()


def summarize_status(entries: list[dict[str, str]]) -> dict[str, int]:
    modified = 0
    untracked = 0
    staged = 0
    other = 0
    for entry in entries:
        status = entry["status"]
        index_status = status[0]
        worktree_status = status[1]
        if status == "??":
            untracked += 1
        elif index_status != " ":
            staged += 1
        elif worktree_status != " ":
            modified += 1
        else:
            other += 1
    return {
        "modified": modified,
        "untracked": untracked,
        "staged": staged,
        "other": other,
        "total": len(entries),
    }


def build_summary_json(branch: str | None, entries: list[dict[str, str]], grouped: OrderedDict[str, list[str]]) -> dict:
    counts = summarize_status(entries)
    return {
        "branch": branch,
        "tracking": branch,
        "status_counts": counts,
        "ownership_counts": {name: len(files) for name, files in grouped.items()},
        "high_collision_files": grouped[HIGH_COLLISION_GROUP],
        "unknown_count": len(grouped["unknown"]),
        "advisory_docs": DOC_LINKS,
        "tooling_note": "Playwright may fail on this Windows machine with windows-playwright-launch-permission.",
        "reminders": [
            "Do not use git add .",
            "Use selective staging and git add -p for shared files.",
            "Scanner output is heuristic and does not replace manual diff review.",
        ],
    }


def print_summary(branch: str | None, entries: list[dict[str, str]], grouped: OrderedDict[str, list[str]]) -> None:
    counts = summarize_status(entries)
    print(f"Branch: {branch or 'unknown'}")
    print(f"Tracking: {branch or 'unknown'}")
    print(
        "Status counts: "
        f"modified={counts['modified']} "
        f"untracked={counts['untracked']} "
        f"staged={counts['staged']} "
        f"other={counts['other']} "
        f"total={counts['total']}"
    )
    print()
    print("Ownership groups:")
    for name, files in grouped.items():
        if not files and name != "unknown":
            continue
        print(f"  - {name}: {len(files)}")
    print()
    print(f"High-collision files changed: {len(grouped[HIGH_COLLISION_GROUP])}")
    for path in grouped[HIGH_COLLISION_GROUP]:
        print(f"  - {path}")
    print()
    print(f"Unknown files: {len(grouped['unknown'])}")
    if grouped["unknown"]:
        for path in grouped["unknown"]:
            print(f"  - {path}")
    else:
        print("  - none")
    print()
    print("Reference docs:")
    for path in DOC_LINKS:
        print(f"  - {path}")
    print()
    print("Known tooling note:")
    print("  - Playwright may fail on this Windows machine with windows-playwright-launch-permission.")
    print()
    print("Reminders:")
    print("  - Do not use git add .")
    print("  - Use selective staging and git add -p for shared files.")
    print("  - This report is advisory and does not replace manual diff review.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Group changed files by likely owning agent/task.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")
    parser.add_argument("--only", choices=GROUPS, help="Show only one ownership group.")
    parser.add_argument("--summary", action="store_true", help="Print a concise worktree snapshot summary.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parent.parent
    try:
        branch, entries = parse_status(run_git_status(repo_root))
    except subprocess.CalledProcessError as exc:
        print(exc.stderr.strip() or "git status failed", file=sys.stderr)
        return exc.returncode or 1

    files = [entry["path"] for entry in entries]
    grouped = build_groups(files)
    if args.summary and args.only:
        print("--summary cannot be combined with --only", file=sys.stderr)
        return 2
    if args.json and args.summary:
        print(json.dumps(build_summary_json(branch, entries, grouped), indent=2))
    elif args.summary:
        print_summary(branch, entries, grouped)
    elif args.json:
        print(json.dumps(build_json(branch, grouped, args.only), indent=2))
    else:
        print_text(branch, grouped, args.only)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
