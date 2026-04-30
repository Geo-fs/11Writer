#!/usr/bin/env python3
"""Build a compact repo-local validation snapshot from provided results."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parent.parent
KNOWN_PLAYWRIGHT_KIND = "windows-playwright-launch-permission"
KNOWN_PLAYWRIGHT_NARROWED_CAUSE = "windows-browser-launch-permission"
VALID_STATUSES = {"passed", "failed", "not-run"}


def parse_smoke_value(value: str) -> dict[str, Any]:
    if "=" not in value:
        raise argparse.ArgumentTypeError(
            "Smoke values must use phase=status or phase=known-local-caveat:narrowed-cause"
        )
    phase, raw_status = value.split("=", 1)
    phase = phase.strip().lower()
    raw_status = raw_status.strip()
    if not phase:
        raise argparse.ArgumentTypeError("Smoke phase cannot be empty")
    if raw_status == "passed":
        return {
            "phase": phase,
            "status": "passed",
            "classification": "clean",
            "details": None,
        }
    if raw_status == "failed":
        return {
            "phase": phase,
            "status": "failed",
            "classification": "runner-or-assertion-failure",
            "details": None,
        }
    if raw_status.startswith("known-local-caveat"):
        classification = KNOWN_PLAYWRIGHT_NARROWED_CAUSE
        if ":" in raw_status:
            _, classification = raw_status.split(":", 1)
            classification = classification.strip() or KNOWN_PLAYWRIGHT_NARROWED_CAUSE
        return {
            "phase": phase,
            "status": "known-local-caveat",
            "classification": classification,
            "details": {
                "kind": KNOWN_PLAYWRIGHT_KIND,
                "narrowed_cause": classification,
            },
        }
    raise argparse.ArgumentTypeError(
        "Smoke status must be passed, failed, or known-local-caveat[:narrowed-cause]"
    )


def normalize_core_status(name: str, value: str) -> dict[str, Any]:
    if value not in VALID_STATUSES:
        raise ValueError(f"{name} must be one of: {', '.join(sorted(VALID_STATUSES))}")
    return {"status": value}


def build_manager_summary(results: dict[str, Any], smokes: list[dict[str, Any]]) -> list[str]:
    core = ", ".join(
        f"{name}={results[name]['status']}" for name in ("compile", "lint", "build")
    )
    lines = [f"Core validation: {core}"]
    if smokes:
        smoke_bits = []
        for item in smokes:
            if item["status"] == "passed":
                smoke_bits.append(f"{item['phase']}=passed")
            elif item["status"] == "known-local-caveat":
                smoke_bits.append(
                    f"{item['phase']}=known-local-caveat({item['classification']})"
                )
            else:
                smoke_bits.append(f"{item['phase']}=failed")
        lines.append("Focused smoke: " + ", ".join(smoke_bits))
        known_local = [item for item in smokes if item["status"] == "known-local-caveat"]
        if known_local:
            lines.append(
                "Known local caveat: "
                + ", ".join(
                    f"{item['phase']} -> {item['classification']}" for item in known_local
                )
            )
    return lines


def print_text(payload: dict[str, Any]) -> None:
    print("Validation snapshot")
    print(f"Repo root: {REPO_ROOT}")
    print()
    for name in ("compile", "lint", "build"):
        print(f"{name}: {payload['results'][name]['status']}")
    if payload["smokes"]:
        print()
        print("Smoke phases:")
        for item in payload["smokes"]:
            print(f"- {item['phase']}: {item['status']} ({item['classification']})")
    print()
    print("Manager summary:")
    for line in payload["manager_summary"]:
        print(f"- {line}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--compile",
        required=True,
        choices=sorted(VALID_STATUSES),
        help="Compile status input",
    )
    parser.add_argument(
        "--lint",
        required=True,
        choices=sorted(VALID_STATUSES),
        help="Lint status input",
    )
    parser.add_argument(
        "--build",
        required=True,
        choices=sorted(VALID_STATUSES),
        help="Build status input",
    )
    parser.add_argument(
        "--smoke",
        action="append",
        default=[],
        type=parse_smoke_value,
        help="Smoke status input, e.g. --smoke marine=passed --smoke aerospace=known-local-caveat:windows-browser-launch-permission",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON output")
    args = parser.parse_args()

    payload = {
        "results": {
            "compile": normalize_core_status("compile", args.compile),
            "lint": normalize_core_status("lint", args.lint),
            "build": normalize_core_status("build", args.build),
        },
        "smokes": args.smoke,
        "known_local_caveat_kind": KNOWN_PLAYWRIGHT_KIND,
        "known_local_caveat_narrowed_cause": KNOWN_PLAYWRIGHT_NARROWED_CAUSE,
    }
    payload["manager_summary"] = build_manager_summary(payload["results"], payload["smokes"])

    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print_text(payload)

    if any(item["status"] == "failed" for item in payload["results"].values()):
        return 1
    if any(item["status"] == "failed" for item in payload["smokes"]):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
