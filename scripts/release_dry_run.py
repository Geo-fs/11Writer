#!/usr/bin/env python3
"""Non-mutating release readiness scan for the current multi-agent worktree."""

from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
OWNER_SCANNER_PATH = REPO_ROOT / "scripts" / "list_changed_files_by_owner.py"
MAX_TEXT_SCAN_BYTES = 262_144

DOC_LINKS = [
    "app/docs/active-agent-worktree.md",
    "app/docs/commit-groups.current.md",
    "app/docs/validation-matrix.md",
    "app/docs/release-readiness.md",
]

SECRET_PATH_PATTERNS = [
    ".env",
    ".env.",
    ".pem",
    ".key",
    ".p12",
    ".pfx",
    "secrets.",
]

JUNK_PATH_PATTERNS = [
    "node_modules/",
    "dist/",
    "build/",
    "coverage/",
    "playwright-report/",
    "test-results/",
    "__pycache__/",
    ".pytest_cache/",
    ".venv/",
    ".mypy_cache/",
    ".ruff_cache/",
    ".vite/",
    ".tsbuildinfo",
    ".sqlite",
    ".sqlite3",
    ".db",
    ".log",
    ".tmp",
    ".bak",
    ".zip",
    ".7z",
    ".tar",
    ".gz",
]

CONTENT_RED_FLAGS = [
    ("API_KEY", "API_KEY"),
    ("SECRET", "SECRET"),
    ("TOKEN", "TOKEN"),
    ("PASSWORD", "PASSWORD"),
    ("PRIVATE_KEY", "PRIVATE_KEY"),
    ("OPENAI", "OPENAI"),
    ("OPENROUTER", "OPENROUTER"),
    ("GITHUB_TOKEN", "GITHUB_TOKEN"),
    ("BEGIN PRIVATE KEY", "BEGIN PRIVATE KEY"),
    ("Authorization: Bearer", "Authorization: Bearer"),
]

GENERATED_PATH_PATTERNS = [
    "app/client/dist/",
    "app/client/node_modules/",
    ".tsbuildinfo",
    "coverage/",
    "playwright-report/",
    "test-results/",
    "__pycache__/",
    ".pytest_cache/",
    ".mypy_cache/",
    ".ruff_cache/",
    ".vite/",
    ".venv/",
    ".sqlite",
    ".sqlite3",
    ".db",
    ".zip",
    ".7z",
    ".tar",
    ".gz",
]

VALIDATION_RECOMMENDATIONS = {
    "connect-tooling": [
        "python -m py_compile app/server/tests/run_playwright_smoke.py",
        "git diff -- app/docs/repo-workflow.md app/docs/active-agent-worktree.md app/docs/commit-groups.current.md app/docs/validation-matrix.md app/docs/release-readiness.md",
    ],
    "gather-ui-integration": [
        "python -m json.tool app/docs/data_sources.noauth.registry.json",
        "cd app/client",
        "cmd /c npm.cmd run lint",
        "cmd /c npm.cmd run build",
    ],
    "geospatial-environmental": [
        "cd app/server",
        "python -m pytest tests/test_eonet_events.py -q",
        "python -m pytest tests/test_earthquake_events.py -q",
        "python -m pytest tests/test_planet_config.py -q",
        "python -m compileall src",
        "cd ../client",
        "cmd /c npm.cmd run lint",
        "cmd /c npm.cmd run build",
    ],
    "aerospace": [
        "cd app/client",
        "cmd /c npm.cmd run lint",
        "cmd /c npm.cmd run build",
        "Optional: cd ../server && python tests/run_playwright_smoke.py aerospace",
    ],
    "marine": [
        "python -m pytest app/server/tests/test_marine_contracts.py -q",
        "cd app/client",
        "cmd /c npm.cmd run lint",
        "cmd /c npm.cmd run build",
        "Optional: cd .. && python app/server/tests/run_playwright_smoke.py marine",
    ],
    "features-webcam": [
        "python -m pytest app/server/tests/test_reference_module.py app/server/tests/test_webcam_module.py -q",
        "python -m compileall app/server/src app/server/tests/smoke_fixture_app.py",
        "cd app/client",
        "cmd /c npm.cmd run lint",
        "cmd /c npm.cmd run build",
        "Optional: cd .. && python app/server/tests/run_playwright_smoke.py webcam",
    ],
    "shared-high-collision": [
        "Review shared files manually before staging",
        "Use git add -p on AppShell.tsx, LayerPanel.tsx, InspectorPanel.tsx, store.ts, queries.ts, shared types, and smoke harness files",
        "cd app/client",
        "cmd /c npm.cmd run lint",
        "cmd /c npm.cmd run build",
        "Run targeted domain validations for every affected ownership group",
    ],
    "unknown": [
        "Review unknown files manually and assign them to a commit group before staging",
    ],
}


def load_owner_module():
    spec = importlib.util.spec_from_file_location("owner_scanner", OWNER_SCANNER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load ownership scanner at {OWNER_SCANNER_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_git_status_lines() -> list[str]:
    result = subprocess.run(
        ["git", "status", "--short", "--branch"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.splitlines()


def status_counts(entries: list[dict[str, str]]) -> dict[str, int]:
    modified = 0
    staged = 0
    untracked = 0
    other = 0
    for entry in entries:
        status = entry["status"]
        if status == "??":
            untracked += 1
            continue
        if status[0] != " ":
            staged += 1
        elif status[1] != " ":
            modified += 1
        else:
            other += 1
    return {
        "modified": modified,
        "staged": staged,
        "untracked": untracked,
        "other": other,
        "total": len(entries),
    }


def path_matches(path: str, pattern: str) -> bool:
    lower = path.lower()
    p = pattern.lower()
    if p.endswith("/"):
        return p in lower
    return lower == p or lower.endswith(p) or p in lower


def path_secret_hits(path: str) -> list[str]:
    hits: list[str] = []
    for pattern in SECRET_PATH_PATTERNS:
        if path_matches(path, pattern):
            hits.append(pattern)
    return hits


def path_junk_hits(path: str) -> list[str]:
    hits: list[str] = []
    for pattern in JUNK_PATH_PATTERNS:
        if path_matches(path, pattern):
            hits.append(pattern)
    return hits


def path_generated_hits(path: str) -> list[str]:
    hits: list[str] = []
    for pattern in GENERATED_PATH_PATTERNS:
        if path_matches(path, pattern):
            hits.append(pattern)
    return hits


def is_small_text_file(path: Path) -> bool:
    if not path.is_file():
        return False
    try:
        size = path.stat().st_size
    except OSError:
        return False
    if size > MAX_TEXT_SCAN_BYTES:
        return False
    try:
        raw = path.read_bytes()
    except OSError:
        return False
    if b"\x00" in raw:
        return False
    return True


def content_red_flags(path_str: str) -> list[str]:
    path = REPO_ROOT / path_str
    if not is_small_text_file(path):
        return []
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return []
    hits: list[str] = []
    for needle, label in CONTENT_RED_FLAGS:
        if needle in text:
            hits.append(label)
    return hits


def collect_red_flags(entries: list[dict[str, str]]) -> dict[str, list[dict[str, list[str]]]]:
    secrets: list[dict[str, list[str]]] = []
    junk: list[dict[str, list[str]]] = []
    generated: list[dict[str, list[str]]] = []
    for entry in entries:
        path = entry["path"]
        secret_hits = path_secret_hits(path)
        content_hits = content_red_flags(path)
        junk_hits = path_junk_hits(path)
        generated_hits = path_generated_hits(path)
        if secret_hits or content_hits:
            labels = secret_hits + [f"content:{label}" for label in content_hits]
            secrets.append({"path": path, "matches": labels})
        if junk_hits:
            junk.append({"path": path, "matches": junk_hits})
        if generated_hits:
            generated.append({"path": path, "matches": generated_hits})
    return {
        "secret_red_flags": secrets,
        "junk_red_flags": junk,
        "generated_red_flags": generated,
    }


def changed_groups(grouped: dict[str, list[str]]) -> list[str]:
    return [name for name, files in grouped.items() if files and name != "unknown"]


def validation_recommendations(grouped: dict[str, list[str]]) -> dict[str, list[str]]:
    recommendations: dict[str, list[str]] = {}
    for group in changed_groups(grouped):
        recommendations[group] = VALIDATION_RECOMMENDATIONS.get(group, [])
    if grouped.get("unknown"):
        recommendations["unknown"] = VALIDATION_RECOMMENDATIONS["unknown"]
    return recommendations


def build_report_json(
    branch: str | None,
    entries: list[dict[str, str]],
    grouped: dict[str, list[str]],
    red_flags: dict[str, list[dict[str, list[str]]]],
) -> dict:
    return {
        "branch": branch,
        "tracking": branch,
        "status_counts": status_counts(entries),
        "ownership_counts": {name: len(files) for name, files in grouped.items()},
        "high_collision_files": grouped["shared-high-collision"],
        "unknown_count": len(grouped["unknown"]),
        "docs": DOC_LINKS,
        "tooling_caveats": [
            "Playwright may fail on this Windows machine with windows-playwright-launch-permission.",
        ],
        "reminders": [
            "Do not use git add .",
            "Use selective staging and git add -p for shared files.",
            "This report is advisory and does not replace manual diff review.",
        ],
        "red_flags": red_flags,
        "validation_recommendations": validation_recommendations(grouped),
    }


def print_matches(title: str, items: list[dict[str, list[str]]]) -> None:
    print(f"{title}: {len(items)}")
    if not items:
        print("  - none")
        print()
        return
    for item in items:
        labels = ", ".join(item["matches"])
        print(f"  - {item['path']} [{labels}]")
    print()


def print_report(
    branch: str | None,
    entries: list[dict[str, str]],
    grouped: dict[str, list[str]],
    red_flags: dict[str, list[dict[str, list[str]]]],
) -> None:
    counts = status_counts(entries)
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
    for group, files in grouped.items():
        if not files and group != "unknown":
            continue
        print(f"  - {group}: {len(files)}")
    print()
    print(f"High-collision files changed: {len(grouped['shared-high-collision'])}")
    for path in grouped["shared-high-collision"]:
        print(f"  - {path}")
    print("Suggested handling:")
    print("  - review diff manually")
    print("  - use git add -p")
    print("  - split shared-file hunks into separate commits if needed")
    print()
    print(f"Unknown files: {len(grouped['unknown'])}")
    if grouped["unknown"]:
        for path in grouped["unknown"]:
            print(f"  - {path}")
    else:
        print("  - none")
    print()
    print_matches("Secret red flags", red_flags["secret_red_flags"])
    print_matches("Junk red flags", red_flags["junk_red_flags"])
    print_matches("Generated-file red flags", red_flags["generated_red_flags"])
    print("Reference docs:")
    for path in DOC_LINKS:
        print(f"  - {path}")
    print()
    print("Known tooling caveat:")
    print("  - Playwright may fail on this Windows machine with windows-playwright-launch-permission.")
    print()
    print("Validation recommendations:")
    for group, commands in validation_recommendations(grouped).items():
        print(f"  {group}:")
        for command in commands:
            print(f"    - {command}")
    print()
    print("Reminders:")
    print("  - Do not use git add .")
    print("  - Use selective staging / git add -p for shared files")
    print("  - This report is advisory and does not replace manual diff review")


def determine_exit_code(
    grouped: dict[str, list[str]],
    red_flags: dict[str, list[dict[str, list[str]]]],
    entries: list[dict[str, str]],
    strict: bool,
) -> int:
    has_red_flags = any(red_flags[key] for key in red_flags)
    if strict:
        counts = status_counts(entries)
        if counts["staged"] > 0:
            return 1
        if grouped["shared-high-collision"]:
            return 1
        if grouped["unknown"]:
            return 1
        if has_red_flags:
            return 1
    if has_red_flags:
        return 1
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a non-mutating release readiness scan.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit nonzero for shared/high-collision files, unknown files, staged files, or red flags.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    owner_module = load_owner_module()
    try:
        lines = run_git_status_lines()
        branch, entries = owner_module.parse_status(lines)
    except subprocess.CalledProcessError as exc:
        print(exc.stderr.strip() or "git status failed", file=sys.stderr)
        return 2

    files = [entry["path"] for entry in entries]
    grouped = owner_module.build_groups(files)
    red_flags = collect_red_flags(entries)

    if args.json:
        print(json.dumps(build_report_json(branch, entries, grouped, red_flags), indent=2))
    else:
        print_report(branch, entries, grouped, red_flags)
    return determine_exit_code(grouped, red_flags, entries, args.strict)


if __name__ == "__main__":
    raise SystemExit(main())
