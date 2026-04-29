from __future__ import annotations

import json
import os
import pathlib
import subprocess
import sys
import time
import urllib.request


ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = ROOT / "output" / "playwright"
OUT.mkdir(parents=True, exist_ok=True)
BACKEND_URL = "http://127.0.0.1:8000"


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

    required_failures = ("aircraft", "satellite", "restore", "webcam", "earthquake")
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
