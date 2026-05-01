from __future__ import annotations

from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Literal

from sqlalchemy import func
from sqlmodel import Session, select

from app.models.common import RunStatus, SignalSeverity, SignalStatus
from app.models.connector import Connector
from app.models.discovered_source import DiscoveredSource
from app.models.record import Record
from app.models.run_history import RunHistory
from app.models.signal import Signal
from app.models.source_check import SourceCheck
from app.models.wave import Wave


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _normalize_datetime(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    if value.tzinfo is None:
        return value
    return value.astimezone(timezone.utc).replace(tzinfo=None)


def _status_text(value: Any) -> str:
    if isinstance(value, Enum):
        return str(value.value).casefold()
    return str(value).casefold()


def list_signals_for_wave(
    session: Session,
    wave_id: int,
    *,
    limit: int = 100,
    severity: SignalSeverity | None = None,
    status: SignalStatus | None = None,
    signal_type: str | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    sort: Literal["newest", "oldest"] = "newest",
) -> list[Signal]:
    bounded = max(1, min(limit, 300))
    statement = select(Signal).where(Signal.wave_id == wave_id)
    if severity is not None:
        statement = statement.where(Signal.severity == severity)
    if status is not None:
        statement = statement.where(Signal.status == status)
    if signal_type:
        statement = statement.where(Signal.type == signal_type)
    normalized_start = _normalize_datetime(start_date)
    if normalized_start is not None:
        statement = statement.where(Signal.created_at >= normalized_start)
    normalized_end = _normalize_datetime(end_date)
    if normalized_end is not None:
        statement = statement.where(Signal.created_at <= normalized_end)
    if sort == "oldest":
        statement = statement.order_by(Signal.created_at.asc())
    else:
        statement = statement.order_by(Signal.created_at.desc())
    statement = statement.limit(bounded)
    return list(session.exec(statement))


def list_signals_for_connector(
    session: Session,
    connector_id: int,
    *,
    limit: int = 100,
    severity: SignalSeverity | None = None,
    status: SignalStatus | None = None,
    signal_type: str | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    sort: Literal["newest", "oldest"] = "newest",
) -> list[Signal]:
    bounded = max(1, min(limit, 300))
    statement = select(Signal).where(Signal.connector_id == connector_id)
    if severity is not None:
        statement = statement.where(Signal.severity == severity)
    if status is not None:
        statement = statement.where(Signal.status == status)
    if signal_type:
        statement = statement.where(Signal.type == signal_type)
    normalized_start = _normalize_datetime(start_date)
    if normalized_start is not None:
        statement = statement.where(Signal.created_at >= normalized_start)
    normalized_end = _normalize_datetime(end_date)
    if normalized_end is not None:
        statement = statement.where(Signal.created_at <= normalized_end)
    if sort == "oldest":
        statement = statement.order_by(Signal.created_at.asc())
    else:
        statement = statement.order_by(Signal.created_at.desc())
    statement = statement.limit(bounded)
    return list(session.exec(statement))


def get_signal_or_none(session: Session, signal_id: int) -> Signal | None:
    return session.get(Signal, signal_id)


def update_signal(
    session: Session,
    signal: Signal,
    *,
    status: SignalStatus | None,
    severity: SignalSeverity | None,
    title: str | None,
    summary: str | None,
) -> Signal:
    if status is not None:
        signal.status = status
    if severity is not None:
        signal.severity = severity
    if title is not None:
        signal.title = title
    if summary is not None:
        signal.summary = summary
    session.add(signal)
    session.commit()
    session.refresh(signal)
    return signal


def create_signal_with_cooldown(
    session: Session,
    *,
    wave_id: int,
    connector_id: int | None,
    signal_type: str,
    severity: SignalSeverity,
    title: str,
    summary: str,
    metadata_json: dict[str, Any] | None,
    dedupe_key: str,
    cooldown_minutes: int,
    now: datetime,
) -> Signal | None:
    cutoff = now - timedelta(minutes=max(1, cooldown_minutes))
    recent = session.exec(
        select(Signal.id).where(
            Signal.wave_id == wave_id,
            Signal.connector_id == connector_id,
            Signal.type == signal_type,
            Signal.dedupe_key == dedupe_key,
            Signal.created_at >= cutoff,
            Signal.status != SignalStatus.RESOLVED,
        )
    ).first()
    if recent is not None:
        return None

    signal = Signal(
        wave_id=wave_id,
        connector_id=connector_id,
        type=signal_type,
        severity=severity,
        title=title,
        summary=summary,
        status=SignalStatus.NEW,
        created_at=now,
        metadata_json=metadata_json,
        dedupe_key=dedupe_key,
    )
    session.add(signal)
    session.commit()
    session.refresh(signal)
    return signal


def _focus_terms(wave: Wave) -> list[str]:
    source_text = f"{wave.name} {wave.description}".casefold()
    terms = [token.strip(".,:;!?()[]{}\"'") for token in source_text.split()]
    return [term for term in terms if len(term) >= 4]


def _include_terms(connector: Connector) -> list[str]:
    config = connector.config_json or {}
    include = config.get("include_keywords")
    if isinstance(include, list):
        values = [str(value).casefold() for value in include if str(value).strip()]
        return values[:20]
    keywords = config.get("keywords")
    if isinstance(keywords, list):
        values = [str(value).casefold() for value in keywords if str(value).strip()]
        return values[:20]
    return []


def _check_matching_records_signal(
    session: Session,
    wave: Wave,
    connector: Connector,
    run_history: RunHistory,
    new_records: list[Record],
    now: datetime,
) -> None:
    if not new_records:
        return
    terms = set(_focus_terms(wave) + _include_terms(connector))
    if not terms:
        return

    matched = []
    for record in new_records:
        text = f"{record.title}\n{record.content}".casefold()
        if sum(1 for term in terms if term in text) >= 2 or any(term in text for term in terms):
            matched.append(record.id)
    if not matched:
        return

    create_signal_with_cooldown(
        session,
        wave_id=wave.id,
        connector_id=connector.id,
        signal_type="matching_record",
        severity=SignalSeverity.MEDIUM,
        title=f"Matching records detected for {connector.name}",
        summary=f"{len(matched)} newly ingested records matched configured focus terms.",
        metadata_json={"matched_record_ids": matched, "run_id": run_history.id},
        dedupe_key=f"matching:{connector.id}",
        cooldown_minutes=60,
        now=now,
    )


def _check_failure_streak_signal(
    session: Session,
    wave: Wave,
    connector: Connector,
    run_history: RunHistory,
    now: datetime,
) -> None:
    if run_history.status != RunStatus.FAILED:
        return
    recent = list(
        session.exec(
            select(RunHistory.status)
            .where(RunHistory.connector_id == connector.id)
            .order_by(RunHistory.started_at.desc())
            .limit(3)
        )
    )
    if len(recent) < 3 or any(status != RunStatus.FAILED for status in recent):
        return

    create_signal_with_cooldown(
        session,
        wave_id=wave.id,
        connector_id=connector.id,
        signal_type="failure_streak",
        severity=SignalSeverity.HIGH,
        title=f"Connector failure streak for {connector.name}",
        summary="Connector has failed in 3 consecutive runs.",
        metadata_json={"run_id": run_history.id, "streak_length": 3},
        dedupe_key=f"failure_streak:{connector.id}",
        cooldown_minutes=180,
        now=now,
    )


def _check_activity_spike_signal(
    session: Session,
    wave: Wave,
    connector: Connector,
    run_history: RunHistory,
    now: datetime,
) -> None:
    if run_history.status != RunStatus.SUCCESS or run_history.records_created <= 0:
        return

    recent_runs = list(
        session.exec(
            select(RunHistory.records_created)
            .where(
                RunHistory.connector_id == connector.id,
                RunHistory.status == RunStatus.SUCCESS,
            )
            .order_by(RunHistory.started_at.desc())
            .offset(1)
            .limit(5)
        )
    )
    if len(recent_runs) < 3:
        return

    baseline = sum(recent_runs) / len(recent_runs)
    if baseline < 1:
        return
    if run_history.records_created < max(3, int(baseline * 2)):
        return

    create_signal_with_cooldown(
        session,
        wave_id=wave.id,
        connector_id=connector.id,
        signal_type="activity_spike",
        severity=SignalSeverity.MEDIUM,
        title=f"Activity spike for {connector.name}",
        summary=(
            f"Connector produced {run_history.records_created} records, "
            f"above baseline {baseline:.1f}."
        ),
        metadata_json={"run_id": run_history.id, "baseline": baseline},
        dedupe_key=f"activity_spike:{connector.id}",
        cooldown_minutes=120,
        now=now,
    )


def _check_source_silence_signal(
    session: Session,
    wave: Wave,
    connector: Connector,
    run_history: RunHistory,
    now: datetime,
) -> None:
    if run_history.status != RunStatus.SUCCESS:
        return

    latest_record_time = session.exec(
        select(func.max(Record.collected_at)).where(Record.connector_id == connector.id)
    ).first()
    if latest_record_time is None:
        return

    latest = (
        latest_record_time.astimezone(timezone.utc).replace(tzinfo=None)
        if latest_record_time.tzinfo is not None
        else latest_record_time
    )
    silence_threshold = (
        now - timedelta(minutes=connector.polling_interval_minutes * 3)
    ).astimezone(timezone.utc).replace(tzinfo=None)
    if latest > silence_threshold:
        return

    create_signal_with_cooldown(
        session,
        wave_id=wave.id,
        connector_id=connector.id,
        signal_type="source_silence",
        severity=SignalSeverity.LOW,
        title=f"Source silence for {connector.name}",
        summary="No new records have appeared for at least 3 polling intervals.",
        metadata_json={"latest_record_at": latest.isoformat(), "run_id": run_history.id},
        dedupe_key=f"source_silence:{connector.id}",
        cooldown_minutes=180,
        now=now,
    )


def _to_float(value: Any) -> float | None:
    if isinstance(value, (int, float)):
        return float(value)
    return None


def _check_weather_threshold_signal(
    session: Session,
    wave: Wave,
    connector: Connector,
    run_history: RunHistory,
    new_records: list[Record],
    now: datetime,
) -> None:
    if connector.type != "weather" or run_history.status != RunStatus.SUCCESS:
        return
    if not new_records:
        return

    payload = new_records[-1].raw_payload_json or {}
    thresholds = payload.get("thresholds")
    if not isinstance(thresholds, dict):
        return

    temperature = _to_float(payload.get("temperature"))
    wind_speed = _to_float(payload.get("wind_speed"))
    precipitation = _to_float(payload.get("precipitation"))
    weather_description = str(payload.get("weather_description", "")).casefold()

    triggers: list[str] = []
    min_temperature = _to_float(thresholds.get("min_temperature"))
    max_temperature = _to_float(thresholds.get("max_temperature"))
    max_wind_speed = _to_float(thresholds.get("max_wind_speed"))
    precipitation_trigger = bool(thresholds.get("precipitation_trigger"))

    if min_temperature is not None and temperature is not None and temperature < min_temperature:
        triggers.append(f"temperature below {min_temperature}")
    if max_temperature is not None and temperature is not None and temperature > max_temperature:
        triggers.append(f"temperature above {max_temperature}")
    if max_wind_speed is not None and wind_speed is not None and wind_speed > max_wind_speed:
        triggers.append(f"wind speed above {max_wind_speed}")
    if precipitation_trigger and precipitation is not None and precipitation > 0:
        triggers.append("precipitation detected")

    severe_keywords = thresholds.get("severe_condition_keywords", [])
    if isinstance(severe_keywords, list):
        severe_match = [
            str(keyword).casefold()
            for keyword in severe_keywords
            if str(keyword).strip() and str(keyword).casefold() in weather_description
        ]
    else:
        severe_match = []
    if severe_match:
        triggers.append(f"severe condition keyword matched: {', '.join(severe_match)}")

    if not triggers:
        return

    create_signal_with_cooldown(
        session,
        wave_id=wave.id,
        connector_id=connector.id,
        signal_type="weather_threshold_crossed",
        severity=SignalSeverity.HIGH if severe_match else SignalSeverity.MEDIUM,
        title=f"Weather threshold crossed for {connector.name}",
        summary="; ".join(triggers),
        metadata_json={"run_id": run_history.id, "triggers": triggers},
        dedupe_key=f"weather_threshold:{connector.id}",
        cooldown_minutes=90,
        now=now,
    )


def _check_weather_major_change_signal(
    session: Session,
    wave: Wave,
    connector: Connector,
    run_history: RunHistory,
    new_records: list[Record],
    now: datetime,
) -> None:
    if connector.type != "weather" or run_history.status != RunStatus.SUCCESS:
        return
    if not new_records:
        return

    current_payload = new_records[-1].raw_payload_json or {}
    current_temperature = _to_float(current_payload.get("temperature"))
    units = str(current_payload.get("units", "metric"))
    if current_temperature is None:
        return

    recent_records = list(
        session.exec(
            select(Record.raw_payload_json)
            .where(
                Record.connector_id == connector.id,
                Record.source_type == "weather",
            )
            .order_by(Record.collected_at.desc())
            .offset(1)
            .limit(5)
        )
    )
    temperatures = [
        _to_float(payload.get("temperature"))
        for payload in recent_records
        if isinstance(payload, dict)
    ]
    baseline_values = [value for value in temperatures if value is not None]
    if len(baseline_values) < 3:
        return

    baseline = sum(baseline_values) / len(baseline_values)
    delta = abs(current_temperature - baseline)
    threshold = 8.0 if units == "metric" else 15.0
    if delta < threshold:
        return

    create_signal_with_cooldown(
        session,
        wave_id=wave.id,
        connector_id=connector.id,
        signal_type="weather_major_change",
        severity=SignalSeverity.MEDIUM,
        title=f"Major weather change for {connector.name}",
        summary=(
            f"Current temperature changed by {delta:.1f} from recent baseline {baseline:.1f}."
        ),
        metadata_json={
            "run_id": run_history.id,
            "current_temperature": current_temperature,
            "baseline_temperature": baseline,
        },
        dedupe_key=f"weather_major_change:{connector.id}",
        cooldown_minutes=90,
        now=now,
    )


def generate_signals_for_run(
    session: Session,
    wave: Wave,
    connector: Connector,
    run_history: RunHistory,
    new_records: list[Record],
    now: datetime | None = None,
) -> None:
    current_time = now or utc_now()
    _check_matching_records_signal(session, wave, connector, run_history, new_records, current_time)
    _check_failure_streak_signal(session, wave, connector, run_history, current_time)
    _check_activity_spike_signal(session, wave, connector, run_history, current_time)
    _check_source_silence_signal(session, wave, connector, run_history, current_time)
    _check_weather_threshold_signal(
        session,
        wave,
        connector,
        run_history,
        new_records,
        current_time,
    )
    _check_weather_major_change_signal(
        session,
        wave,
        connector,
        run_history,
        new_records,
        current_time,
    )


def generate_signals_for_source_check(
    session: Session,
    source: DiscoveredSource,
    check: SourceCheck,
    *,
    previous_consecutive_failures: int,
    previous_content_type: str | None,
    previous_stability_score: float | None,
    now: datetime | None = None,
) -> None:
    if source.wave_id is None:
        return
    current_time = now or utc_now()
    source_name = source.title or source.url

    if check.status.value == "failed":
        if not check.reachable:
            create_signal_with_cooldown(
                session,
                wave_id=source.wave_id,
                connector_id=None,
                signal_type="source_unreachable",
                severity=SignalSeverity.MEDIUM,
                title=f"Source unreachable: {source_name}",
                summary="Automated source check could not reach the source.",
                metadata_json={"source_id": source.id, "url": source.url},
                dedupe_key=f"source_unreachable:{source.id}",
                cooldown_minutes=180,
                now=current_time,
            )
        if _status_text(source.status) == "approved" and source.consecutive_failures >= 3:
            create_signal_with_cooldown(
                session,
                wave_id=source.wave_id,
                connector_id=None,
                signal_type="approved_source_failure_streak",
                severity=SignalSeverity.HIGH,
                title=f"Approved source failure streak: {source_name}",
                summary="Approved source has failed automated checks repeatedly.",
                metadata_json={
                    "source_id": source.id,
                    "consecutive_failures": source.consecutive_failures,
                },
                dedupe_key=f"approved_source_failure_streak:{source.id}",
                cooldown_minutes=240,
                now=current_time,
            )

    if (
        previous_content_type
        and check.content_type
        and previous_content_type != check.content_type
        and check.status.value == "success"
    ):
        create_signal_with_cooldown(
            session,
            wave_id=source.wave_id,
            connector_id=None,
            signal_type="source_content_type_changed",
            severity=SignalSeverity.MEDIUM,
            title=f"Source content type changed: {source_name}",
            summary=f"Content type changed from {previous_content_type} to {check.content_type}.",
            metadata_json={"source_id": source.id, "url": source.url},
            dedupe_key=f"source_content_type_changed:{source.id}",
            cooldown_minutes=360,
            now=current_time,
        )

    if check.status.value == "success" and previous_consecutive_failures >= 2:
        create_signal_with_cooldown(
            session,
            wave_id=source.wave_id,
            connector_id=None,
            signal_type="source_recovered",
            severity=SignalSeverity.LOW,
            title=f"Source recovered: {source_name}",
            summary="Source recovered after repeated failures.",
            metadata_json={
                "source_id": source.id,
                "previous_consecutive_failures": previous_consecutive_failures,
            },
            dedupe_key=f"source_recovered:{source.id}",
            cooldown_minutes=240,
            now=current_time,
        )

    if (
        _status_text(source.status) == "candidate"
        and (previous_stability_score or 0.0) < 0.8
        and (source.stability_score or 0.0) >= 0.8
        and check.status.value == "success"
    ):
        create_signal_with_cooldown(
            session,
            wave_id=source.wave_id,
            connector_id=None,
            signal_type="source_stability_improved",
            severity=SignalSeverity.LOW,
            title=f"Source stability improved: {source_name}",
            summary="Source stability crossed the review threshold.",
            metadata_json={
                "source_id": source.id,
                "stability_score": source.stability_score,
            },
            dedupe_key=f"source_stability_improved:{source.id}",
            cooldown_minutes=720,
            now=current_time,
        )
