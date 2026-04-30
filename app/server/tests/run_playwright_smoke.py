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

PLAYWRIGHT_EXECUTABLE_PATH_CHECK = """\
const { chromium } = require('playwright');
console.log(chromium.executablePath());
"""

RAW_NODE_SPAWN_CHECK_TEMPLATE = """\
const cp = require('child_process');
const target = %s;
const child = cp.spawn(target, ['--version']);
child.on('error', (error) => {
  console.error(`spawn-error:${error.code ?? 'unknown'}:${error.message}`);
  process.exit(1);
});
child.stdout.on('data', (chunk) => process.stdout.write(chunk));
child.stderr.on('data', (chunk) => process.stderr.write(chunk));
child.on('exit', (code) => process.exit(code ?? 0));
"""


def detect_windows_spawn_eperm(stderr: str) -> bool:
    lowered = stderr.lower()
    return "spawn eperm" in lowered or "access is denied. (0x5)" in lowered


def run_node_script(script: str, timeout: int = 60) -> dict[str, Any]:
    result = subprocess.run(
        ["node", "-e", script],
        cwd=str(CLIENT_DIR),
        capture_output=True,
        text=True,
        timeout=timeout,
        env=os.environ.copy(),
    )
    return {
        "returncode": result.returncode,
        "stdout": result.stdout[-12000:],
        "stderr": result.stderr[-12000:],
    }


def run_playwright_launch_check() -> dict[str, Any]:
    return run_node_script(PLAYWRIGHT_LAUNCH_CHECK, timeout=60)


def get_playwright_executable_path() -> str | None:
    result = run_node_script(PLAYWRIGHT_EXECUTABLE_PATH_CHECK, timeout=30)
    if result["returncode"] != 0:
        return None
    path = result["stdout"].strip()
    return path or None


def run_raw_node_spawn_check(executable_path: str) -> dict[str, Any]:
    script = RAW_NODE_SPAWN_CHECK_TEMPLATE % json.dumps(executable_path)
    return run_node_script(script, timeout=30)


def run_direct_executable_check(executable_path: str) -> dict[str, Any]:
    result = subprocess.run(
        [executable_path, "--version"],
        cwd=str(CLIENT_DIR),
        capture_output=True,
        text=True,
        timeout=30,
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
    executable_path = get_playwright_executable_path()
    if executable_path:
        payload["probes"] = {
            "playwrightExecutablePath": executable_path,
            "directExecutableCheck": run_direct_executable_check(executable_path),
            "rawNodeSpawnCheck": run_raw_node_spawn_check(executable_path),
        }
    if os.name == "nt" and detect_windows_spawn_eperm(str(launch_check["stderr"])):
        direct_ok = False
        direct_access_denied = False
        raw_spawn_eperm = False
        if isinstance(payload.get("probes"), dict):
            direct_check = payload["probes"].get("directExecutableCheck")
            raw_node_check = payload["probes"].get("rawNodeSpawnCheck")
            direct_ok = bool(isinstance(direct_check, dict) and direct_check.get("returncode") == 0)
            direct_access_denied = bool(
                isinstance(direct_check, dict)
                and detect_windows_spawn_eperm(str(direct_check.get("stderr", "")))
            )
            raw_spawn_eperm = bool(
                isinstance(raw_node_check, dict)
                and detect_windows_spawn_eperm(str(raw_node_check.get("stderr", "")))
            )
        if direct_ok and raw_spawn_eperm:
            summary = (
                "Playwright browser launch failed before smoke assertions. "
                "The browser install is present and direct executable launch works, "
                "but Node/Playwright launch fails with spawn EPERM."
            )
            narrowed_cause = "node-spawn-permission-boundary"
        elif raw_spawn_eperm and direct_access_denied:
            summary = (
                "Playwright browser launch failed before smoke assertions. "
                "This Windows host has a reproducible browser launch permission boundary: "
                "Node spawn fails with EPERM and direct executable probing also reports access denied."
            )
            narrowed_cause = "windows-browser-launch-permission"
        else:
            summary = (
                "Playwright browser launch failed before smoke assertions. "
                "This Windows host has a reproducible browser launch permission issue involving "
                "Node/Playwright spawn and related executable launch checks."
            )
            narrowed_cause = "windows-browser-launch-permission"
        payload["diagnosis"] = {
            "kind": "windows-playwright-launch-permission",
            "summary": summary,
            "likely_scope": "machine-environment-specific",
            "narrowed_cause": narrowed_cause,
            "troubleshooting": [
                "Confirm the runner is using Windows paths consistently; avoid mixed WSL and Windows launch paths.",
                "Verify the Playwright browser binary exists under %LOCALAPPDATA%\\ms-playwright and runs with --version.",
                "Test a minimal launch with: node -e \"const { chromium } = require('playwright'); chromium.launch({ headless: true })\".",
                "If a raw Node child_process spawn of the browser also fails with EPERM while direct executable launch works, treat that as a host-level Node/browser spawn permission problem rather than a missing browser install.",
                "If both raw Node spawn and direct executable probes report access denied, suspect Windows security policy or local browser execution controls beyond Playwright-specific settings.",
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
