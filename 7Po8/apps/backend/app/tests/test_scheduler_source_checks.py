from datetime import datetime, timedelta, timezone

from sqlmodel import Session, SQLModel, select

from app.api.deps import db
from app.models.common import (
    DiscoveredSourceStatus,
    FocusType,
    SignalSeverity,
    WaveStatus,
)
from app.models.discovered_source import DiscoveredSource
from app.models.signal import Signal
from app.models.wave import Wave
from app.scheduler.service import run_scheduler_tick
from app.services import source_check_service
from app.services.source_check_service import is_source_due


def _create_wave(session: Session) -> Wave:
    wave = Wave(
        name="Auto Source Checks",
        description="scheduler integration",
        focus_type=FocusType.MIXED,
        status=WaveStatus.ACTIVE,
    )
    session.add(wave)
    session.commit()
    session.refresh(wave)
    return wave


def _prepare_db() -> None:
    db.reconfigure("sqlite:///./data/test_scheduler_source_checks.db")
    SQLModel.metadata.drop_all(db.engine)
    SQLModel.metadata.create_all(db.engine)


def test_source_due_eligibility_logic() -> None:
    now = datetime(2026, 3, 15, 12, 0, 0, tzinfo=timezone.utc)
    source = DiscoveredSource(
        wave_id=1,
        url="https://example.com/feed.xml",
        title="feed",
        source_type="rss",
        status=DiscoveredSourceStatus.NEW,
        auto_check_enabled=True,
        check_interval_minutes=30,
    )
    assert is_source_due(source, now) is True

    source.next_check_at = now + timedelta(minutes=5)
    assert is_source_due(source, now) is False

    source.next_check_at = now - timedelta(minutes=1)
    assert is_source_due(source, now) is True

    source.status = DiscoveredSourceStatus.IGNORED
    assert is_source_due(source, now) is False


def test_scheduler_tick_runs_due_source_checks_and_updates_backoff(monkeypatch) -> None:
    _prepare_db()
    def failing_fetch(_url: str) -> tuple[int, str | None, bytes]:
        return 503, "text/plain", b"down"

    monkeypatch.setattr(source_check_service, "_default_fetch", failing_fetch)

    with Session(db.engine) as session:
        wave = _create_wave(session)
        source = DiscoveredSource(
            wave_id=wave.id,
            url="https://example.com/unreachable.xml",
            title="Unreachable",
            source_type="rss",
            status=DiscoveredSourceStatus.NEW,
            auto_check_enabled=True,
            check_interval_minutes=30,
            next_check_at=datetime(2026, 3, 15, 11, 0, 0),
        )
        session.add(source)
        session.commit()
        session.refresh(source)

        now = datetime(2026, 3, 15, 12, 0, 0, tzinfo=timezone.utc)
        result = run_scheduler_tick(session, now_fn=lambda: now)

        assert result.eligible_sources == 1
        assert result.failed_source_checks == 1
        session.refresh(source)
        assert source.consecutive_failures == 1
        assert source.next_check_at is not None
        assert source.next_check_at > now.replace(tzinfo=None)


def test_ignored_and_rejected_sources_not_auto_checked(monkeypatch) -> None:
    _prepare_db()
    def success_fetch(_url: str) -> tuple[int, str | None, bytes]:
        return 200, "application/rss+xml", b"<rss><channel></channel></rss>"

    monkeypatch.setattr(source_check_service, "_default_fetch", success_fetch)

    with Session(db.engine) as session:
        wave = _create_wave(session)
        ignored = DiscoveredSource(
            wave_id=wave.id,
            url="https://example.com/ignored.xml",
            title="Ignored",
            source_type="rss",
            status=DiscoveredSourceStatus.IGNORED,
            auto_check_enabled=True,
            next_check_at=datetime(2026, 3, 15, 10, 0, 0),
        )
        rejected = DiscoveredSource(
            wave_id=wave.id,
            url="https://example.com/rejected.xml",
            title="Rejected",
            source_type="rss",
            status=DiscoveredSourceStatus.REJECTED,
            auto_check_enabled=True,
            next_check_at=datetime(2026, 3, 15, 10, 0, 0),
        )
        session.add(ignored)
        session.add(rejected)
        session.commit()

        now = datetime(2026, 3, 15, 12, 0, 0, tzinfo=timezone.utc)
        result = run_scheduler_tick(session, now_fn=lambda: now)
        assert result.eligible_sources == 0
        assert result.successful_source_checks == 0


def test_source_health_signals_created_for_failures_and_recovery(monkeypatch) -> None:
    _prepare_db()
    responses = [
        (503, "text/plain", b"down"),
        (200, "application/json", b'{"ok": true}'),
    ]

    def changing_fetch(_url: str) -> tuple[int, str | None, bytes]:
        return responses.pop(0)

    monkeypatch.setattr(source_check_service, "_default_fetch", changing_fetch)

    with Session(db.engine) as session:
        wave = _create_wave(session)
        source = DiscoveredSource(
            wave_id=wave.id,
            url="https://example.com/source.json",
            title="Source JSON",
            source_type="api_json",
            status=DiscoveredSourceStatus.APPROVED,
            auto_check_enabled=True,
            check_interval_minutes=30,
            next_check_at=datetime(2026, 3, 15, 10, 0, 0),
            consecutive_failures=2,
            last_content_type="text/plain",
            stability_score=0.4,
        )
        session.add(source)
        session.commit()
        session.refresh(source)

        now = datetime(2026, 3, 15, 12, 0, 0, tzinfo=timezone.utc)
        run_scheduler_tick(session, now_fn=lambda: now)
        source.next_check_at = datetime(2026, 3, 15, 11, 0, 0)
        session.add(source)
        session.commit()
        run_scheduler_tick(session, now_fn=lambda: now + timedelta(minutes=1))

        severities = [
            SignalSeverity.MEDIUM,
            SignalSeverity.HIGH,
            SignalSeverity.LOW,
        ]
        signal_types = list(
            session.exec(
                select(Signal.type).where(
                    Signal.wave_id == wave.id,
                    Signal.severity.in_(severities),
                )
            )
        )
        assert "source_unreachable" in signal_types
        assert "source_degraded" in signal_types
        assert "source_recovered" in signal_types
        assert "source_content_type_changed" in signal_types
