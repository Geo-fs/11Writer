from datetime import datetime, timezone

from sqlmodel import Session

from app.api.deps import db
from app.models.common import (
    DiscoveredSourceStatus,
    FocusType,
    SignalSeverity,
    SignalStatus,
    SourceCheckStatus,
    WaveStatus,
)
from app.models.connector import Connector
from app.models.discovered_source import DiscoveredSource
from app.models.record import Record
from app.models.signal import Signal
from app.models.source_check import SourceCheck
from app.models.wave import Wave


def _dt(value: str) -> datetime:
    return datetime.fromisoformat(value).replace(tzinfo=timezone.utc).replace(tzinfo=None)


def _create_wave_with_data() -> tuple[int, int, int, int]:
    with Session(db.engine) as session:
        wave = Wave(
            name="Filter Wave",
            description="Wave for filter tests",
            status=WaveStatus.ACTIVE,
            focus_type=FocusType.MIXED,
        )
        session.add(wave)
        session.commit()
        session.refresh(wave)
        connector_a = Connector(
            wave_id=wave.id,
            type="sample_news",
            name="Connector A",
            enabled=True,
            config_json={},
            polling_interval_minutes=10,
        )
        connector_b = Connector(
            wave_id=wave.id,
            type="rss_news",
            name="Connector B",
            enabled=True,
            config_json={"feed_url": "https://example.com/feed.xml"},
            polling_interval_minutes=20,
        )
        session.add(connector_a)
        session.add(connector_b)
        session.commit()
        session.refresh(connector_a)
        session.refresh(connector_b)

        records = [
            Record(
                wave_id=wave.id,
                connector_id=connector_a.id,
                external_id="r1",
                title="Airport expansion update",
                content="Permit approved",
                source_type="rss_news",
                source_name="City News",
                source_url="https://example.com/airport",
                collected_at=_dt("2026-03-10T10:00:00"),
                latitude=30.1,
                longitude=-97.7,
            ),
            Record(
                wave_id=wave.id,
                connector_id=connector_b.id,
                external_id="r2",
                title="Weather watch",
                content="Strong wind expected",
                source_type="weather",
                source_name="Weather API",
                source_url="https://example.com/weather",
                collected_at=_dt("2026-03-11T10:00:00"),
                latitude=None,
                longitude=None,
            ),
            Record(
                wave_id=wave.id,
                connector_id=connector_b.id,
                external_id="r3",
                title="Airport closure rumor",
                content="Unverified social chatter",
                source_type="rss_news",
                source_name="Regional Feed",
                source_url="https://example.com/closure",
                collected_at=_dt("2026-03-12T10:00:00"),
                latitude=31.0,
                longitude=-98.0,
            ),
        ]
        session.add_all(records)

        signals = [
            Signal(
                wave_id=wave.id,
                connector_id=connector_a.id,
                type="matching_record",
                severity=SignalSeverity.MEDIUM,
                title="Match 1",
                summary="A",
                status=SignalStatus.NEW,
                created_at=_dt("2026-03-10T11:00:00"),
            ),
            Signal(
                wave_id=wave.id,
                connector_id=connector_a.id,
                type="activity_spike",
                severity=SignalSeverity.HIGH,
                title="Spike",
                summary="B",
                status=SignalStatus.ACKNOWLEDGED,
                created_at=_dt("2026-03-11T11:00:00"),
            ),
            Signal(
                wave_id=wave.id,
                connector_id=connector_b.id,
                type="source_silence",
                severity=SignalSeverity.LOW,
                title="Silence",
                summary="C",
                status=SignalStatus.RESOLVED,
                created_at=_dt("2026-03-12T11:00:00"),
            ),
        ]
        session.add_all(signals)

        sources = [
            DiscoveredSource(
                wave_id=wave.id,
                url="https://city.example.gov/feed.xml",
                title="City Feed",
                source_type="rss",
                parent_domain="city.example.gov",
                status=DiscoveredSourceStatus.NEW,
                discovery_method="seed",
                relevance_score=0.8,
                stability_score=0.7,
                free_access=True,
                suggested_connector_type="rss_news",
                discovered_at=_dt("2026-03-10T09:00:00"),
                last_checked_at=_dt("2026-03-12T09:00:00"),
                last_success_at=_dt("2026-03-12T09:00:00"),
                failure_count=1,
                last_http_status=200,
                last_content_type="application/rss+xml",
            ),
            DiscoveredSource(
                wave_id=wave.id,
                url="https://data.example.gov/incidents.json",
                title="Incidents API",
                source_type="api_json",
                parent_domain="data.example.gov",
                status=DiscoveredSourceStatus.APPROVED,
                discovery_method="seed",
                relevance_score=0.9,
                stability_score=0.95,
                free_access=True,
                suggested_connector_type=None,
                discovered_at=_dt("2026-03-11T09:00:00"),
                last_checked_at=_dt("2026-03-12T09:00:00"),
                last_success_at=_dt("2026-03-12T09:00:00"),
                failure_count=0,
                last_http_status=200,
                last_content_type="application/json",
            ),
            DiscoveredSource(
                wave_id=wave.id,
                url="https://docs.example.gov/report.pdf",
                title="Report",
                source_type="document_pdf",
                parent_domain="docs.example.gov",
                status=DiscoveredSourceStatus.REJECTED,
                discovery_method="seed",
                relevance_score=0.4,
                stability_score=0.2,
                free_access=True,
                suggested_connector_type=None,
                discovered_at=_dt("2026-03-12T09:00:00"),
                failure_count=3,
            ),
        ]
        session.add_all(sources)
        session.commit()
        session.refresh(sources[0])
        session.refresh(sources[1])
        session.refresh(sources[2])

        checks = [
            SourceCheck(
                discovered_source_id=sources[1].id,
                checked_at=_dt("2026-03-10T12:00:00"),
                status=SourceCheckStatus.SUCCESS,
                http_status=200,
                content_type="application/json",
                latency_ms=120,
                reachable=True,
                parseable=True,
            ),
            SourceCheck(
                discovered_source_id=sources[1].id,
                checked_at=_dt("2026-03-11T12:00:00"),
                status=SourceCheckStatus.FAILED,
                http_status=500,
                content_type="text/html",
                latency_ms=400,
                reachable=False,
                parseable=False,
            ),
            SourceCheck(
                discovered_source_id=sources[1].id,
                checked_at=_dt("2026-03-12T12:00:00"),
                status=SourceCheckStatus.SUCCESS,
                http_status=200,
                content_type="application/json",
                latency_ms=140,
                reachable=True,
                parseable=True,
            ),
        ]
        session.add_all(checks)
        session.commit()

        return wave.id, connector_a.id, connector_b.id, sources[1].id


def test_record_filters_and_sort(client) -> None:
    wave_id, connector_a_id, _, _ = _create_wave_with_data()

    filtered = client.get(
        f"/api/waves/{wave_id}/records?text_search=airport&connector_id={connector_a_id}"
        "&source_type=rss_news&has_coordinates=true&sort=oldest"
    )
    assert filtered.status_code == 200
    payload = filtered.json()
    assert len(payload) == 1
    assert payload[0]["title"] == "Airport expansion update"

    date_filtered = client.get(
        f"/api/waves/{wave_id}/records?start_date=2026-03-11T00:00:00&end_date=2026-03-12T00:00:00"
    )
    assert date_filtered.status_code == 200
    assert len(date_filtered.json()) == 1
    assert date_filtered.json()[0]["external_id"] == "r2"


def test_signal_filters_and_sort(client) -> None:
    wave_id, connector_a_id, _, _ = _create_wave_with_data()

    wave_filtered = client.get(
        f"/api/waves/{wave_id}/signals?severity=high&status=acknowledged&signal_type=activity_spike"
    )
    assert wave_filtered.status_code == 200
    payload = wave_filtered.json()
    assert len(payload) == 1
    assert payload[0]["title"] == "Spike"

    connector_sorted = client.get(
        f"/api/connectors/{connector_a_id}/signals?sort=oldest"
    )
    assert connector_sorted.status_code == 200
    sorted_payload = connector_sorted.json()
    assert len(sorted_payload) == 2
    assert sorted_payload[0]["title"] == "Match 1"


def test_discovered_source_filters_and_sort(client) -> None:
    wave_id, _, _, _ = _create_wave_with_data()

    approved = client.get(f"/api/waves/{wave_id}/discovered-sources?approved_only=true")
    assert approved.status_code == 200
    approved_payload = approved.json()
    assert len(approved_payload) == 1
    assert approved_payload[0]["status"] == "approved"

    scored = client.get(
        f"/api/waves/{wave_id}/discovered-sources?"
        "source_type=api_json&min_relevance_score=0.7&min_stability_score=0.8"
        "&parent_domain=data.example.gov&sort=stability_desc"
    )
    assert scored.status_code == 200
    scored_payload = scored.json()
    assert len(scored_payload) == 1
    assert scored_payload[0]["title"] == "Incidents API"


def test_source_check_filters_and_sort(client) -> None:
    _, _, _, source_id = _create_wave_with_data()

    filtered = client.get(
        f"/api/discovered-sources/{source_id}/checks?"
        "status=success&reachable=true&parseable=true&content_type=application/json"
        "&start_date=2026-03-10T00:00:00&end_date=2026-03-12T23:59:59&sort=oldest"
    )
    assert filtered.status_code == 200
    payload = filtered.json()
    assert len(payload) == 2
    assert payload[0]["checked_at"].startswith("2026-03-10")
