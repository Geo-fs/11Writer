#!/usr/bin/env python3
"""Validate and summarize the shared alerts ledger."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_ALERTS_PATH = REPO_ROOT / "app" / "docs" / "alerts.md"
DEFAULT_MAX_LINES = 500
VALID_PRIORITIES = {"low", "medium", "high", "critical"}
VALID_STATES = {"open", "acknowledged", "in_progress", "completed"}


@dataclass
class AlertRecord:
    line_index: int
    raw_line: str
    time: str
    creating_agent: str
    title: str
    priority: str
    response_owner: str
    state: str
    description: str


def split_alert_line(line: str) -> list[str]:
    return [part.strip() for part in line.split(" | ")]


def parse_alert_line(line: str, line_index: int) -> tuple[AlertRecord | None, str | None]:
    parts = split_alert_line(line)
    if len(parts) != 7:
        return None, f"line {line_index}: expected 7 fields, found {len(parts)}"
    time, creating_agent, title, priority, response_owner, state, description = parts
    if priority not in VALID_PRIORITIES:
        return None, f"line {line_index}: invalid priority `{priority}`"
    if state not in VALID_STATES:
        return None, f"line {line_index}: invalid state `{state}`"
    if not all((time, creating_agent, title, response_owner, description)):
        return None, f"line {line_index}: one or more required fields are empty"
    return (
        AlertRecord(
            line_index=line_index,
            raw_line=line,
            time=time,
            creating_agent=creating_agent,
            title=title,
            priority=priority,
            response_owner=response_owner,
            state=state,
            description=description,
        ),
        None,
    )


def load_alerts(path: Path) -> tuple[list[str], list[AlertRecord], list[str], int | None]:
    lines = path.read_text(encoding="utf-8").splitlines()
    start_index: int | None = None
    for idx, line in enumerate(lines):
        if line.strip() == "Active alerts:":
            start_index = idx + 1
            break
    if start_index is None:
        return lines, [], ["Missing `Active alerts:` section"], None

    alerts: list[AlertRecord] = []
    malformed: list[str] = []
    for idx in range(start_index, len(lines)):
        raw = lines[idx]
        stripped = raw.strip()
        if not stripped:
            continue
        if stripped.startswith("#"):
            continue
        parsed, error = parse_alert_line(stripped, idx + 1)
        if error:
            malformed.append(error)
            continue
        if parsed is not None:
            alerts.append(parsed)
    return lines, alerts, malformed, start_index


def build_summary(alerts: list[AlertRecord]) -> dict[str, Any]:
    by_owner: dict[str, int] = {}
    by_priority: dict[str, int] = {}
    by_state: dict[str, int] = {}
    open_alerts = [alert for alert in alerts if alert.state != "completed"]
    for alert in open_alerts:
        by_owner[alert.response_owner] = by_owner.get(alert.response_owner, 0) + 1
        by_priority[alert.priority] = by_priority.get(alert.priority, 0) + 1
        by_state[alert.state] = by_state.get(alert.state, 0) + 1
    return {
        "total_alert_lines": len(alerts),
        "open_alert_lines": len(open_alerts),
        "completed_alert_lines": len([alert for alert in alerts if alert.state == "completed"]),
        "open_by_response_owner": dict(sorted(by_owner.items())),
        "open_by_priority": {key: by_priority.get(key, 0) for key in ("critical", "high", "medium", "low")},
        "open_by_state": dict(sorted(by_state.items())),
    }


def prune_completed(lines: list[str], alerts: list[AlertRecord], max_lines: int) -> tuple[list[str], list[str]]:
    if len(alerts) <= max_lines:
        return lines, []
    completed = [alert for alert in alerts if alert.state == "completed"]
    overage = len(alerts) - max_lines
    removable = completed[:overage]
    if not removable:
        return lines, ["No completed alerts available to prune while preserving open lines."]

    remove_indexes = {alert.line_index - 1 for alert in removable}
    new_lines = [line for idx, line in enumerate(lines) if idx not in remove_indexes]
    notes = [
        f"Pruned {len(removable)} completed alert(s) to reduce ledger from {len(alerts)} to {len(alerts) - len(removable)} line(s)."
    ]
    return new_lines, notes


def print_text(path: Path, summary: dict[str, Any], malformed: list[str], max_lines: int, prune_notes: list[str]) -> None:
    print("Alerts ledger summary")
    print(f"Path: {path}")
    print(f"Total alert lines: {summary['total_alert_lines']}")
    print(f"Open alert lines: {summary['open_alert_lines']}")
    print(f"Completed alert lines: {summary['completed_alert_lines']}")
    print(f"500-line target status: {'within target' if summary['total_alert_lines'] <= max_lines else 'over target'}")
    print()
    print("Open alerts by response owner:")
    if summary["open_by_response_owner"]:
        for owner, count in summary["open_by_response_owner"].items():
            print(f"- {owner}: {count}")
    else:
        print("- none")
    print()
    print("Open alerts by priority:")
    for priority, count in summary["open_by_priority"].items():
        print(f"- {priority}: {count}")
    print()
    if malformed:
        print("Malformed lines:")
        for issue in malformed:
            print(f"- {issue}")
        print()
    if prune_notes:
        print("Prune notes:")
        for note in prune_notes:
            print(f"- {note}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--path", default=str(DEFAULT_ALERTS_PATH), help="Path to alerts.md")
    parser.add_argument("--json", action="store_true", help="Emit JSON output")
    parser.add_argument(
        "--prune-completed",
        action="store_true",
        help="Prune oldest completed alerts first if the ledger exceeds the max line target",
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="Write prune changes back to the file. Only valid with --prune-completed",
    )
    parser.add_argument("--max-lines", type=int, default=DEFAULT_MAX_LINES, help="Target max alert lines")
    args = parser.parse_args()

    if args.write and not args.prune_completed:
        parser.error("--write requires --prune-completed")

    path = Path(args.path)
    lines, alerts, malformed, _ = load_alerts(path)
    prune_notes: list[str] = []
    if args.prune_completed:
        new_lines, prune_notes = prune_completed(lines, alerts, args.max_lines)
        if args.write and prune_notes and not prune_notes[0].startswith("No completed alerts available"):
            path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
            lines = new_lines
            _, alerts, malformed, _ = load_alerts(path)

    summary = build_summary(alerts)
    payload = {
        "path": str(path),
        "summary": summary,
        "max_lines": args.max_lines,
        "within_target": summary["total_alert_lines"] <= args.max_lines,
        "malformed": malformed,
        "prune_notes": prune_notes,
        "write_applied": bool(args.write and args.prune_completed and prune_notes and not prune_notes[0].startswith("No completed alerts available")),
    }

    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print_text(path, summary, malformed, args.max_lines, prune_notes)

    if malformed:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
