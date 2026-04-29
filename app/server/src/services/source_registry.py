from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Literal


SourceState = Literal[
    "never-fetched",
    "healthy",
    "stale",
    "rate-limited",
    "degraded",
    "disabled",
    "blocked",
    "credentials-missing",
    "needs-review",
]


@dataclass
class SourceRuntimeStatus:
    name: str
    state: SourceState = "never-fetched"
    last_success_at: str | None = None
    last_attempt_at: str | None = None
    last_failure_at: str | None = None
    degraded_reason: str | None = None
    freshness_seconds: int | None = None
    stale_after_seconds: int | None = None
    rate_limited: bool = False
    hidden_reason: str | None = None
    blocked_reason: str | None = None
    credentials_configured: bool = True
    review_required: bool = False
    success_count: int = 0
    failure_count: int = 0
    warning_count: int = 0


_REGISTRY: dict[str, SourceRuntimeStatus] = {}


def get_source_runtime_status(name: str) -> SourceRuntimeStatus | None:
    return _REGISTRY.get(name)


def reset_source_registry() -> None:
    _REGISTRY.clear()


def record_source_success(
    name: str,
    *,
    freshness_seconds: int | None,
    stale_after_seconds: int | None,
    review_required: bool = False,
    warning_count: int = 0,
) -> None:
    previous = _REGISTRY.get(name)
    now = datetime.now(tz=timezone.utc).isoformat()
    _REGISTRY[name] = SourceRuntimeStatus(
        name=name,
        state="needs-review" if review_required else "healthy",
        last_success_at=now,
        last_attempt_at=now,
        last_failure_at=previous.last_failure_at if previous else None,
        freshness_seconds=freshness_seconds,
        stale_after_seconds=stale_after_seconds,
        degraded_reason=None,
        rate_limited=False,
        hidden_reason=None,
        blocked_reason=None,
        credentials_configured=True,
        review_required=review_required,
        success_count=(previous.success_count if previous else 0) + 1,
        failure_count=previous.failure_count if previous else 0,
        warning_count=warning_count,
    )


def record_source_failure(
    name: str,
    *,
    degraded_reason: str,
    state: SourceState | None = None,
    freshness_seconds: int | None = None,
    stale_after_seconds: int | None = None,
    rate_limited: bool = False,
    hidden_reason: str | None = None,
    blocked_reason: str | None = None,
    credentials_configured: bool = True,
    review_required: bool = False,
    warning_count: int | None = None,
) -> None:
    previous = _REGISTRY.get(name)
    now = datetime.now(tz=timezone.utc).isoformat()
    next_state = state or ("rate-limited" if rate_limited else "degraded")
    _REGISTRY[name] = SourceRuntimeStatus(
        name=name,
        state=next_state,
        last_success_at=previous.last_success_at if previous else None,
        last_attempt_at=now,
        last_failure_at=now,
        degraded_reason=degraded_reason,
        freshness_seconds=freshness_seconds if freshness_seconds is not None else (previous.freshness_seconds if previous else None),
        stale_after_seconds=stale_after_seconds if stale_after_seconds is not None else (previous.stale_after_seconds if previous else None),
        rate_limited=rate_limited,
        hidden_reason=hidden_reason if hidden_reason is not None else (previous.hidden_reason if previous else None),
        blocked_reason=blocked_reason if blocked_reason is not None else (previous.blocked_reason if previous else None),
        credentials_configured=credentials_configured,
        review_required=review_required,
        success_count=previous.success_count if previous else 0,
        failure_count=(previous.failure_count if previous else 0) + 1,
        warning_count=warning_count if warning_count is not None else (previous.warning_count if previous else 0),
    )
