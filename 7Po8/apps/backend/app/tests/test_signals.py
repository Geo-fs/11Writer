from datetime import datetime, timedelta, timezone
from typing import Any

from sqlmodel import Session, select

from app.api.deps import db
from app.connectors.base import CollectedRecord, ConnectorRunner
from app.models.common import FocusType, SignalStatus
from app.models.connector import Connector
from app.models.signal import Signal
from app.models.wave import Wave
from app.scheduler.service import run_scheduler_tick


class AlwaysFailRunner:
    type_name = "always_fail"

    def validate_config(self, config: dict[str, Any]) -> dict[str, Any]:
        return config

    def collect(
        self,
        wave_name: str,  # noqa: ARG002
        focus_type: str,  # noqa: ARG002
        config: dict[str, Any],  # noqa: ARG002
    ) -> list[CollectedRecord]:
        raise RuntimeError("simulated failure")


class VariableCountRunner:
    type_name = "variable_count"

    def __init__(self, counts: list[int]) -> None:
        self._counts = counts
        self._run_index = 0

    def validate_config(self, config: dict[str, Any]) -> dict[str, Any]:
        return config

    def collect(
        self,
        wave_name: str,
        focus_type: str,  # noqa: ARG002
        config: dict[str, Any],  # noqa: ARG002
    ) -> list[CollectedRecord]:
        count = self._counts[min(self._run_index, len(self._counts) - 1)]
        self._run_index += 1
        now = datetime.now(timezone.utc)
        return [
            CollectedRecord(
                external_id=f"var:{self._run_index}:{index}",
                title=f"{wave_name} generated {index}",
                content="activity sample",
                source_type="variable_count",
                source_name="Variable Runner",
                source_url=None,
                collected_at=now,
                event_time=now,
                latitude=None,
                longitude=None,
                tags_json=["variable"],
                raw_payload_json={"index": index},
            )
            for index in range(count)
        ]


def test_matching_signal_created_and_not_spammed(client) -> None:
    wave_response = client.post(
        "/api/waves",
        json={
            "name": "Airport Focus",
            "description": "airport developments",
            "focus_type": "keyword",
        },
    )
    wave_id = wave_response.json()["id"]
    connector_response = client.post(
        f"/api/waves/{wave_id}/connectors",
        json={
            "type": "sample_news",
            "name": "Sample",
            "enabled": True,
            "polling_interval_minutes": 15,
            "config_json": {"keywords": ["airport", "permit"]},
        },
    )
    assert connector_response.status_code == 201

    first_ingest = client.post(f"/api/waves/{wave_id}/ingest/sample")
    assert first_ingest.status_code == 201

    wave_signals_one = client.get(f"/api/waves/{wave_id}/signals")
    assert wave_signals_one.status_code == 200
    matching = [signal for signal in wave_signals_one.json() if signal["type"] == "matching_record"]
    assert len(matching) == 1

    second_ingest = client.post(f"/api/waves/{wave_id}/ingest/sample")
    assert second_ingest.status_code == 201

    wave_signals_two = client.get(f"/api/waves/{wave_id}/signals")
    matching_two = [
        signal for signal in wave_signals_two.json() if signal["type"] == "matching_record"
    ]
    assert len(matching_two) == 1

    patch_response = client.patch(
        f"/api/signals/{matching_two[0]['id']}",
        json={"status": "acknowledged"},
    )
    assert patch_response.status_code == 200
    assert patch_response.json()["status"] == "acknowledged"


def test_failure_streak_signal(client) -> None:
    with Session(db.engine) as session:
        wave = Wave(name="Failure Signals", description="streak", focus_type=FocusType.KEYWORD)
        session.add(wave)
        session.commit()
        session.refresh(wave)
        connector = Connector(
            wave_id=wave.id,
            type="always_fail",
            name="Fail Connector",
            enabled=True,
            config_json={},
            polling_interval_minutes=1,
        )
        session.add(connector)
        session.commit()
        session.refresh(connector)

        runner: ConnectorRunner = AlwaysFailRunner()
        for _ in range(3):
            run_scheduler_tick(
                session,
                connector_lookup=(
                    lambda connector_type: runner if connector_type == "always_fail" else None
                ),
            )
            connector.next_run_at = datetime.now(timezone.utc) - timedelta(minutes=1)
            session.add(connector)
            session.commit()

        signals = list(
            session.exec(
                select(Signal).where(
                    Signal.connector_id == connector.id,
                    Signal.type == "failure_streak",
                )
            )
        )
        assert len(signals) == 1


def test_activity_spike_signal(client) -> None:
    with Session(db.engine) as session:
        wave = Wave(name="Spike Signals", description="spike", focus_type=FocusType.KEYWORD)
        session.add(wave)
        session.commit()
        session.refresh(wave)
        connector = Connector(
            wave_id=wave.id,
            type="variable_count",
            name="Variable Connector",
            enabled=True,
            config_json={},
            polling_interval_minutes=1,
        )
        session.add(connector)
        session.commit()
        session.refresh(connector)

        runner: ConnectorRunner = VariableCountRunner([1, 1, 1, 6])
        for _ in range(4):
            run_scheduler_tick(
                session,
                connector_lookup=(
                    lambda connector_type: runner if connector_type == "variable_count" else None
                ),
            )
            connector.next_run_at = datetime.now(timezone.utc) - timedelta(minutes=1)
            session.add(connector)
            session.commit()

        spike_signals = list(
            session.exec(
                select(Signal).where(
                    Signal.connector_id == connector.id,
                    Signal.type == "activity_spike",
                )
            )
        )
        assert len(spike_signals) == 1


def test_signal_api_list_and_resolve(client) -> None:
    wave_response = client.post(
        "/api/waves",
        json={"name": "Signal API", "description": "api test", "focus_type": "keyword"},
    )
    wave_id = wave_response.json()["id"]
    connector_response = client.post(
        f"/api/waves/{wave_id}/connectors",
        json={
            "type": "sample_news",
            "name": "Signal Source",
            "enabled": True,
            "polling_interval_minutes": 10,
            "config_json": {"keywords": ["airport"]},
        },
    )
    connector_id = connector_response.json()["id"]
    client.post(f"/api/waves/{wave_id}/ingest/sample")

    wave_list = client.get(f"/api/waves/{wave_id}/signals")
    connector_list = client.get(f"/api/connectors/{connector_id}/signals")
    assert wave_list.status_code == 200
    assert connector_list.status_code == 200
    assert len(wave_list.json()) >= 1

    signal_id = wave_list.json()[0]["id"]
    patch_response = client.patch(f"/api/signals/{signal_id}", json={"status": "resolved"})
    assert patch_response.status_code == 200
    assert patch_response.json()["status"] == SignalStatus.RESOLVED
