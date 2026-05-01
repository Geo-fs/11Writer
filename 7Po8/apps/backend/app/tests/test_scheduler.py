from datetime import datetime, timedelta, timezone
from typing import Any

from sqlmodel import Session, select

from app.api.deps import db
from app.connectors.base import CollectedRecord, ConnectorRunner
from app.models.common import FocusType, RunStatus
from app.models.connector import Connector
from app.models.run_history import RunHistory
from app.models.wave import Wave
from app.scheduler.service import is_connector_due, run_scheduler_tick


class FailingConnectorRunner:
    type_name = "failing_connector"

    def validate_config(self, config: dict[str, Any]) -> dict[str, Any]:
        return config

    def collect(
        self,
        wave_name: str,  # noqa: ARG002
        focus_type: str,  # noqa: ARG002
        config: dict[str, Any],  # noqa: ARG002
    ) -> list[CollectedRecord]:
        raise RuntimeError("simulated connector failure")


def test_scheduler_due_logic() -> None:
    now = datetime(2026, 1, 1, tzinfo=timezone.utc)
    connector = Connector(
        wave_id=1,
        type="sample_news",
        name="Due Logic",
        enabled=True,
        polling_interval_minutes=10,
        config_json={},
    )
    assert is_connector_due(connector, now) is True

    connector.last_run_at = now - timedelta(minutes=5)
    assert is_connector_due(connector, now) is False

    connector.last_run_at = now - timedelta(minutes=11)
    assert is_connector_due(connector, now) is True

    connector.next_run_at = now + timedelta(minutes=3)
    assert is_connector_due(connector, now) is False


def test_scheduler_tick_creates_run_history(client) -> None:
    wave_response = client.post(
        "/api/waves",
        json={"name": "Scheduler Wave", "description": "tick test", "focus_type": "keyword"},
    )
    wave_id = wave_response.json()["id"]

    connector_response = client.post(
        f"/api/waves/{wave_id}/connectors",
        json={
            "type": "sample_news",
            "name": "Scheduled Connector",
            "enabled": True,
            "polling_interval_minutes": 15,
            "config_json": {"keywords": ["airport"]},
        },
    )
    connector_id = connector_response.json()["id"]

    tick_response = client.post("/api/scheduler/tick")
    assert tick_response.status_code == 200
    tick_payload = tick_response.json()
    assert tick_payload["eligible_connectors"] == 1
    assert tick_payload["successful_runs"] == 1
    assert tick_payload["failed_runs"] == 0

    runs_response = client.get(f"/api/waves/{wave_id}/runs")
    assert runs_response.status_code == 200
    runs = runs_response.json()
    assert len(runs) == 1
    assert runs[0]["connector_id"] == connector_id
    assert runs[0]["status"] == "success"
    assert runs[0]["records_created"] == 1

    connectors_response = client.get(f"/api/waves/{wave_id}/connectors")
    connector_payload = connectors_response.json()[0]
    assert connector_payload["last_run_at"] is not None
    assert connector_payload["last_success_at"] is not None
    assert connector_payload["next_run_at"] is not None


def test_scheduler_failure_is_recorded(client) -> None:
    with Session(db.engine) as session:
        wave = Wave(name="Failure Wave", description="failure path", focus_type=FocusType.KEYWORD)
        session.add(wave)
        session.commit()
        session.refresh(wave)

        connector = Connector(
            wave_id=wave.id,
            type="failing_connector",
            name="Failing",
            enabled=True,
            config_json={},
            polling_interval_minutes=5,
        )
        session.add(connector)
        session.commit()
        session.refresh(connector)

        runner: ConnectorRunner = FailingConnectorRunner()
        result = run_scheduler_tick(
            session,
            connector_lookup=(
                lambda connector_type: runner if connector_type == "failing_connector" else None
            ),
        )

        assert result.eligible_connectors == 1
        assert result.successful_runs == 0
        assert result.failed_runs == 1

        run_list = list(
            session.exec(select(RunHistory).where(RunHistory.connector_id == connector.id))
        )
        assert len(run_list) == 1
        assert run_list[0].status == RunStatus.FAILED
        assert "simulated connector failure" in (run_list[0].error_message or "")
