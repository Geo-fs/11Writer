from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from src.app import create_application
from src.config.settings import Settings, get_settings


def _settings(database_path: Path, source_memory_path: Path) -> Settings:
    return Settings(
        APP_ENV="test",
        WAVE_MONITOR_DATABASE_URL=f"sqlite:///{database_path.as_posix()}",
        SOURCE_DISCOVERY_DATABASE_URL=f"sqlite:///{source_memory_path.as_posix()}",
        WEBCAM_WORKER_ENABLED=False,
        WEBCAM_WORKER_RUN_ON_STARTUP=False,
    )


def _client(database_path: Path) -> TestClient:
    app = create_application()
    app.dependency_overrides[get_settings] = lambda: _settings(
        database_path,
        database_path.with_name("source_discovery.db"),
    )
    return TestClient(app)


def test_wave_monitor_overview_exposes_7po8_as_11writer_tool_not_runtime(tmp_path: Path) -> None:
    client = _client(tmp_path / "wave_monitor.db")

    response = client.get("/api/tools/waves/overview")
    payload = response.json()

    assert response.status_code == 200
    assert payload["metadata"]["source"] == "wave-monitor-overview"
    assert payload["metadata"]["importedProject"] == "7Po8"
    assert payload["metadata"]["toolStatus"] == "persistent-backend-preview"
    assert payload["runtime"]["toolName"] == "Wave Monitor"
    assert payload["runtime"]["standaloneRuntimeEnabled"] is False
    assert payload["runtime"]["routePrefix"] == "/api/tools/waves"
    assert payload["runtime"]["storageMode"] == "persistent-sqlite"
    assert payload["runtime"]["schedulerMode"] == "manual"
    assert "not mounted" in " ".join(payload["runtime"]["caveats"]).lower()
    assert payload["summary"]["totalMonitors"] == 2
    assert payload["summary"]["activeMonitors"] == 1
    assert payload["summary"]["totalSignals"] == 3
    assert payload["summary"]["sourceIssues"] == 1


def test_wave_monitor_signals_preserve_safe_hypothesis_caveats(tmp_path: Path) -> None:
    client = _client(tmp_path / "wave_monitor.db")

    payload = client.get("/api/tools/waves/overview").json()
    scam_monitor = next(
        monitor for monitor in payload["monitors"] if monitor["monitorId"] == "wave:scam-ecosystem-watch"
    )
    matching_signal = next(
        signal for signal in scam_monitor["signals"] if signal["signalType"] == "matching_record"
    )

    assert matching_signal["evidenceBasis"] == "scored"
    assert matching_signal["severity"] == "medium"
    assert "inspect-evidence" in matching_signal["availableActions"]
    assert "shared topic terms" in matching_signal["relationshipReasons"]
    caveat_text = " ".join(matching_signal["caveats"]).lower()
    assert "not proof" in caveat_text
    assert "culpable" in caveat_text
    assert "export-packet" in scam_monitor["availableActions"]


def test_wave_monitor_source_candidates_are_lifecycle_candidates_not_validated_sources(tmp_path: Path) -> None:
    client = _client(tmp_path / "wave_monitor.db")

    payload = client.get("/api/tools/waves/overview").json()
    scam_monitor = next(
        monitor for monitor in payload["monitors"] if monitor["monitorId"] == "wave:scam-ecosystem-watch"
    )
    source_candidates = scam_monitor["sourceCandidates"]

    assert {source["lifecycleState"] for source in source_candidates} == {"candidate"}
    assert any(source["sourceHealth"] == "stale" for source in source_candidates)
    assert all(source["policyState"] == "manual_review" for source in source_candidates)
    assert any(
        "manual review required" in " ".join(source["caveats"]).lower()
        for source in source_candidates
    )


def test_wave_monitor_run_now_persists_records_and_run_summary(tmp_path: Path) -> None:
    client = _client(tmp_path / "wave_monitor.db")

    response = client.post("/api/tools/waves/wave:scam-ecosystem-watch/run-now")
    payload = response.json()

    assert response.status_code == 200
    assert payload["monitorId"] == "wave:scam-ecosystem-watch"
    assert payload["status"] == "success"
    assert payload["recordsCreated"] == 2
    assert payload["runs"][0]["status"] == "success"

    overview = client.get("/api/tools/waves/overview").json()
    scam_monitor = next(
        monitor for monitor in overview["monitors"] if monitor["monitorId"] == "wave:scam-ecosystem-watch"
    )
    assert scam_monitor["recordCount"] == 3
    assert len(scam_monitor["recentRecords"]) >= 2
    assert any(run["recordsCreated"] == 2 for run in scam_monitor["recentRuns"])


def test_wave_monitor_scheduler_tick_runs_due_active_connectors_once(tmp_path: Path) -> None:
    client = _client(tmp_path / "wave_monitor.db")

    first = client.post("/api/tools/waves/scheduler/tick").json()
    second = client.post("/api/tools/waves/scheduler/tick").json()

    assert first["scannedConnectors"] == 1
    assert first["eligibleConnectors"] == 1
    assert first["successfulRuns"] == 1
    assert first["recordsCreated"] == 2
    assert second["eligibleConnectors"] == 0
    assert second["recordsCreated"] == 0


def test_wave_monitor_run_now_returns_404_for_unknown_monitor(tmp_path: Path) -> None:
    client = _client(tmp_path / "wave_monitor.db")

    response = client.post("/api/tools/waves/wave:missing/run-now")

    assert response.status_code == 404
