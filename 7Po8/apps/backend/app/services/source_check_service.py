from __future__ import annotations

import json
import time
from collections import Counter
from collections.abc import Callable
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Literal

import httpx
from sqlmodel import Session, select

from app.models.common import SourceCheckStatus
from app.models.discovered_source import DiscoveredSource
from app.models.source_check import SourceCheck
from app.services.source_policy_service import apply_policy_to_source


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _normalize_datetime(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    if value.tzinfo is None:
        return value
    return value.astimezone(timezone.utc).replace(tzinfo=None)


def _status_text(value: object) -> str:
    if isinstance(value, Enum):
        return str(value.value).casefold()
    return str(value).casefold()


def _default_fetch(url: str) -> tuple[int, str | None, bytes]:
    response = httpx.get(url, timeout=12.0, follow_redirects=True)
    return response.status_code, response.headers.get("Content-Type"), response.content


def _normalize_content_type(content_type: str | None) -> str | None:
    if content_type is None:
        return None
    return content_type.split(";")[0].strip().lower()


def _is_parseable(
    source_type: str,
    content_type: str | None,
    body: bytes,
) -> bool:
    normalized = _normalize_content_type(content_type)
    body_head = body[:300].decode("utf-8", errors="ignore").casefold()
    source_type_lower = source_type.casefold()
    if source_type_lower == "rss":
        return bool(
            normalized
            in {
                "application/rss+xml",
                "application/atom+xml",
                "text/xml",
                "application/xml",
            }
            or "<rss" in body_head
            or "<feed" in body_head
        )
    if source_type_lower == "api_json":
        if normalized == "application/json":
            return True
        try:
            json.loads(body.decode("utf-8", errors="strict"))
            return True
        except (UnicodeDecodeError, json.JSONDecodeError):
            return False
    if source_type_lower == "document_pdf":
        return bool(normalized == "application/pdf" or body.startswith(b"%PDF"))
    if source_type_lower in {"web_page", "open_data_page"}:
        return bool(
            normalized in {"text/html", "application/xhtml+xml"}
            or "<html" in body_head
            or "<!doctype html" in body_head
        )
    return len(body) > 0


def _compute_stability_score(recent_checks: list[SourceCheck], failure_count: int) -> float | None:
    if not recent_checks:
        return None
    total = len(recent_checks)
    success_checks = [row for row in recent_checks if row.status == SourceCheckStatus.SUCCESS]
    success_rate = len(success_checks) / total
    parseable_rate = sum(1 for row in recent_checks if row.parseable) / total

    content_types = [row.content_type for row in success_checks if row.content_type]
    if content_types:
        mode_count = Counter(content_types).most_common(1)[0][1]
        consistency_score = mode_count / len(content_types)
    else:
        consistency_score = 0.5

    latencies = [row.latency_ms for row in success_checks if row.latency_ms is not None]
    if not latencies:
        latency_score = 0.5
    else:
        avg_latency = sum(latencies) / len(latencies)
        if avg_latency <= 800:
            latency_score = 1.0
        elif avg_latency <= 2000:
            latency_score = 0.8
        elif avg_latency <= 5000:
            latency_score = 0.6
        else:
            latency_score = 0.4

    base = (
        (0.45 * success_rate)
        + (0.25 * parseable_rate)
        + (0.20 * consistency_score)
        + (0.10 * latency_score)
    )
    penalty = min(0.30, failure_count * 0.05)
    return max(0.0, min(1.0, base - penalty))


def _base_check_interval_minutes(source: DiscoveredSource) -> int:
    status = _status_text(source.status)
    if status in {"candidate", "sandboxed"}:
        return 30
    if status == "approved":
        if (source.stability_score or 0.0) >= 0.85 and source.consecutive_failures == 0:
            return 240
        return 120
    if status == "degraded":
        return 45
    return 60


def _next_interval_minutes(source: DiscoveredSource, check_status: SourceCheckStatus) -> int:
    configured = source.check_interval_minutes
    base = max(configured, _base_check_interval_minutes(source))
    if check_status == SourceCheckStatus.FAILED:
        multiplier = 2 ** min(source.consecutive_failures, 4)
        return min(1440, base * multiplier)
    return base


def is_source_due(source: DiscoveredSource, now: datetime) -> bool:
    if not source.auto_check_enabled:
        return False
    status = _status_text(source.status)
    if status in {"ignored", "rejected", "archived"}:
        return False
    normalized_now = _normalize_datetime(now)
    if source.next_check_at is not None:
        return _normalize_datetime(source.next_check_at) <= normalized_now
    if source.last_checked_at is None:
        return True
    due_at = _normalize_datetime(source.last_checked_at) + timedelta(
        minutes=max(5, source.check_interval_minutes)
    )
    return due_at <= normalized_now


def list_checks_for_source(
    session: Session,
    source_id: int,
    *,
    limit: int = 50,
    status: SourceCheckStatus | None = None,
    reachable: bool | None = None,
    parseable: bool | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    content_type: str | None = None,
    sort: Literal["newest", "oldest"] = "newest",
) -> list[SourceCheck]:
    bounded = max(1, min(limit, 200))
    statement = select(SourceCheck).where(SourceCheck.discovered_source_id == source_id)
    if status is not None:
        statement = statement.where(SourceCheck.status == status)
    if reachable is not None:
        statement = statement.where(SourceCheck.reachable == reachable)
    if parseable is not None:
        statement = statement.where(SourceCheck.parseable == parseable)
    normalized_start = _normalize_datetime(start_date)
    if normalized_start is not None:
        statement = statement.where(SourceCheck.checked_at >= normalized_start)
    normalized_end = _normalize_datetime(end_date)
    if normalized_end is not None:
        statement = statement.where(SourceCheck.checked_at <= normalized_end)
    if content_type:
        cleaned_content_type = content_type.strip().lower()
        statement = statement.where(SourceCheck.content_type.ilike(f"%{cleaned_content_type}%"))
    if sort == "oldest":
        statement = statement.order_by(SourceCheck.checked_at.asc())
    else:
        statement = statement.order_by(SourceCheck.checked_at.desc())
    statement = statement.limit(bounded)
    return list(session.exec(statement))


def check_discovered_source(
    session: Session,
    source: DiscoveredSource,
    *,
    fetcher: Callable[[str], tuple[int, str | None, bytes]] | None = None,
    automated: bool = False,
    checked_at: datetime | None = None,
) -> SourceCheck:
    effective_fetcher = fetcher or _default_fetch
    check_time = _normalize_datetime(checked_at) or utc_now()
    start = time.perf_counter()

    if _status_text(source.status) in {"rejected", "ignored", "archived"} and automated:
        source.next_check_at = None
        session.add(source)
        session.commit()
        row = SourceCheck(
            discovered_source_id=source.id,
            checked_at=check_time,
            status=SourceCheckStatus.SKIPPED,
            reachable=False,
            parseable=False,
            metadata_json={"reason": f"status:{_status_text(source.status)}"},
        )
        session.add(row)
        session.commit()
        session.refresh(row)
        return row

    if _status_text(source.status) in {"rejected", "ignored", "archived"} and not automated:
        row = SourceCheck(
            discovered_source_id=source.id,
            checked_at=check_time,
            status=SourceCheckStatus.SKIPPED,
            reachable=False,
            parseable=False,
            metadata_json={"reason": f"status:{_status_text(source.status)}"},
        )
        session.add(row)
        source.last_checked_at = check_time
        session.add(source)
        session.commit()
        session.refresh(row)
        apply_policy_to_source(session, source, trigger="manual_source_check", now=check_time)
        return row

    status = SourceCheckStatus.FAILED
    http_status: int | None = None
    content_type: str | None = None
    latency_ms: int | None = None
    reachable = False
    parseable = False
    metadata_json: dict[str, str] | None = None

    try:
        http_status, content_type_header, body = effective_fetcher(source.url)
        elapsed_ms = int((time.perf_counter() - start) * 1000)
        latency_ms = max(0, elapsed_ms)
        content_type = _normalize_content_type(content_type_header)
        reachable = http_status < 400
        parseable = reachable and _is_parseable(source.source_type, content_type, body)
        status = SourceCheckStatus.SUCCESS if reachable and parseable else SourceCheckStatus.FAILED
    except Exception as exc:  # noqa: BLE001
        elapsed_ms = int((time.perf_counter() - start) * 1000)
        latency_ms = max(0, elapsed_ms)
        metadata_json = {"error": str(exc)}

    row = SourceCheck(
        discovered_source_id=source.id,
        checked_at=check_time,
        status=status,
        http_status=http_status,
        content_type=content_type,
        latency_ms=latency_ms,
        reachable=reachable,
        parseable=parseable,
        metadata_json=metadata_json,
    )
    session.add(row)

    source.last_checked_at = check_time
    source.last_http_status = http_status
    source.last_content_type = content_type
    if status == SourceCheckStatus.SUCCESS:
        source.last_success_at = check_time
        source.consecutive_failures = 0
    elif status == SourceCheckStatus.FAILED:
        source.failure_count += 1
        source.consecutive_failures += 1

    recent_checks = list_checks_for_source(session, source.id, limit=10)
    # include the current row before it is committed/refreshed
    recent_checks = [row, *recent_checks][:10]
    source.stability_score = _compute_stability_score(recent_checks, source.failure_count)
    source.check_interval_minutes = max(5, source.check_interval_minutes)
    next_interval = _next_interval_minutes(source, status)
    source.next_check_at = check_time + timedelta(minutes=next_interval)

    session.add(source)
    session.commit()
    session.refresh(row)
    apply_policy_to_source(
        session,
        source,
        trigger="automated_source_check" if automated else "manual_source_check",
        now=check_time,
    )
    return row


def check_sources_for_wave(
    session: Session,
    wave_id: int,
    *,
    fetcher: Callable[[str], tuple[int, str | None, bytes]] | None = None,
    limit: int = 100,
) -> list[SourceCheck]:
    sources = list(
        session.exec(
            select(DiscoveredSource)
            .where(DiscoveredSource.wave_id == wave_id)
            .order_by(
                DiscoveredSource.relevance_score.desc(),
                DiscoveredSource.discovered_at.desc(),
            )
            .limit(max(1, min(limit, 300)))
        )
    )
    return [check_discovered_source(session, source, fetcher=fetcher) for source in sources]
