from __future__ import annotations

import json
import os
import pathlib
import subprocess
import sys
import time
import urllib.request
from typing import Any


ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = ROOT / "output" / "playwright"
OUT.mkdir(parents=True, exist_ok=True)
BACKEND_URL = "http://127.0.0.1:8000"
CLIENT_DIR = ROOT / "app" / "client"


PLAYWRIGHT_LAUNCH_CHECK = """\
const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch({ headless: true });
  await browser.close();
})();
"""


def detect_windows_spawn_eperm(stderr: str) -> bool:
    lowered = stderr.lower()
    return "spawn eperm" in lowered or "access is denied. (0x5)" in lowered


def run_playwright_launch_check() -> dict[str, Any]:
    result = subprocess.run(
        ["node", "-e", PLAYWRIGHT_LAUNCH_CHECK],
        cwd=str(CLIENT_DIR),
        capture_output=True,
        text=True,
        timeout=60,
        env=os.environ.copy(),
    )
    return {
        "returncode": result.returncode,
        "stdout": result.stdout[-12000:],
        "stderr": result.stderr[-12000:],
    }


def build_launch_failure_payload(launch_check: dict[str, Any]) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "runner_error": {
            "code": launch_check["returncode"],
            "stdout": launch_check["stdout"],
            "stderr": launch_check["stderr"],
        }
    }
    if os.name == "nt" and detect_windows_spawn_eperm(str(launch_check["stderr"])):
        payload["diagnosis"] = {
            "kind": "windows-playwright-launch-permission",
            "summary": (
                "Playwright browser launch failed before smoke assertions. "
                "This Windows host can execute the browser binary directly, "
                "but Node/Playwright launch fails with spawn EPERM or access denied."
            ),
            "likely_scope": "machine-environment-specific",
            "troubleshooting": [
                "Confirm the runner is using Windows paths consistently; avoid mixed WSL and Windows launch paths.",
                "Verify the Playwright browser binary exists under %LOCALAPPDATA%\\ms-playwright and runs with --version.",
                "Test a minimal launch with: node -e \"const { chromium } = require('playwright'); chromium.launch({ headless: true })\".",
                "If direct executable launch works but Node launch fails, check Windows Defender / antivirus / Controlled Folder Access allowlists for node.exe and the Playwright Chromium binaries.",
                "If needed, reinstall browsers with: npx playwright install chromium.",
                "Treat this as a harness environment issue unless a browser can actually launch and reach app assertions.",
            ],
        }
    return payload


def wait_for_backend(process: subprocess.Popen[str]) -> None:
    deadline = time.time() + 120
    last_error: str | None = None
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(f"{BACKEND_URL}/health", timeout=5) as response:
                if response.status == 200:
                    return
        except Exception as exc:  # pragma: no cover - smoke only
            last_error = repr(exc)
            if process.poll() is not None:
                raise RuntimeError(f"backend exited early: {process.poll()}") from exc
            time.sleep(1)
    raise RuntimeError(f"backend not ready: {last_error}")


def phase_failed(result: dict[str, object], phase: str) -> bool:
    if phase == "marine":
        marine = result.get("marine")
        return bool(isinstance(marine, dict) and marine.get("errors"))

    required_failures = ("aircraft", "satellite", "restore", "webcam", "earthquake", "eonet")
    if any(
        isinstance(result.get(name), dict) and result[name].get("errors")
        for name in required_failures
    ):
        return True

    canvas_aircraft = result.get("canvasAircraft")
    if isinstance(canvas_aircraft, dict) and canvas_aircraft.get("errors"):
        print("Known headless limitation: aircraft direct canvas picking remains informational in smoke mode.", file=sys.stderr)

    canvas_satellite = result.get("canvasSatellite")
    if isinstance(canvas_satellite, dict) and canvas_satellite.get("errors"):
        print("Headless telemetry note: satellite direct canvas picking is currently informational in smoke mode.", file=sys.stderr)

    return False


def main() -> int:
    phase = "full"
    if len(sys.argv) > 1:
        phase = sys.argv[1].strip().lower()
    launch_check = run_playwright_launch_check()
    if launch_check["returncode"] != 0:
        data = build_launch_failure_payload(launch_check)
        session_path = OUT / "playwright-session.json"
        session_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        print(json.dumps(data, indent=2))
        return 1
    backend_stdout = open(OUT / "backend.stdout.log", "w", encoding="utf-8")
    backend_stderr = open(OUT / "backend.stderr.log", "w", encoding="utf-8")
    backend = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "tests.smoke_fixture_app:app", "--host", "127.0.0.1", "--port", "8000"],
        cwd=str(ROOT / "app" / "server"),
        stdout=backend_stdout,
        stderr=backend_stderr,
        env=os.environ.copy(),
    )

    try:
        wait_for_backend(backend)
        result = subprocess.run(
            ["node", "scripts/playwright_smoke.mjs", BACKEND_URL, phase],
            cwd=str(ROOT / "app" / "client"),
            capture_output=True,
            text=True,
            timeout=600,
            env=os.environ.copy(),
        )

        session_path = OUT / "playwright-session.json"
        if result.returncode == 0:
            data = json.loads(result.stdout)
        else:
            data = {
                "runner_error": {
                    "code": result.returncode,
                    "stdout": result.stdout[-12000:],
                    "stderr": result.stderr[-12000:],
                }
            }
        session_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        print(json.dumps(data, indent=2))
        return 1 if result.returncode != 0 or phase_failed(data, phase) else 0
    finally:
        if backend.poll() is None:
            backend.terminate()
            try:
                backend.wait(timeout=10)
            except subprocess.TimeoutExpired:  # pragma: no cover - cleanup only
                backend.kill()
                backend.wait(timeout=10)


if __name__ == "__main__":
    raise SystemExit(main())
