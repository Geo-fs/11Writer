from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

import httpx

from src.config.settings import Settings
from src.services.source_registry import record_source_failure, record_source_success
from src.types.api import NwsAlertEvent, NwsAlertsMetadata, NwsAlertsResponse, NwsAlertsSourceHealth

NwsAlertType = Literal["all", "warning", "watch", "advisory", "statement", "unknown"]
NwsSeverity = Literal["all", "extreme", "severe", "moderate", "minor", "unknown"]
NwsSort = Literal["newest", "severity"]

_NWS_ALERTS_CAVEAT = (
    "NWS Alerts API rows in this slice are active advisory/contextual warning records only. "
    "They do not by themselves establish damage, local impact, certainty, responsibility, legal meaning, or required action."
)
_SEVERITY_ORDER: dict[str, int] = {
    "extreme": 4,
    "severe": 3,
    "moderate": 2,
    "minor": 1,
    "unknown": 0,
}


@dataclass(frozen=True)
class NwsAlertsQuery:
    alert_type: NwsAlertType
    severity: NwsSeverity
    area: str | None
    zone: str | None
    event: str | None
    limit: int
    sort: NwsSort


class NwsAlertsService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def list_recent(self, query: NwsAlertsQuery) -> NwsAlertsResponse:
        fetched_at = datetime.now(tz=timezone.utc).isoformat()
        source_mode = self._source_mode_label()
        if self._settings.nws_alerts_source_mode.strip().lower() == "disabled":
            return NwsAlertsResponse(
                metadata=self._metadata(fetched_at=fetched_at, generated_at=None, count=0, source_mode=source_mode),
                count=0,
                source_health=NwsAlertsSourceHealth(
                    source_id="nws-alerts",
                    source_label="NWS Alerts API",
                    enabled=False,
                    source_mode=source_mode,
                    health="disabled",
                    loaded_count=0,
                    last_fetched_at=fetched_at,
                    source_generated_at=None,
                    detail="NWS Alerts API source is disabled for this runtime.",
                    error_summary=None,
                    caveat=_NWS_ALERTS_CAVEAT,
                ),
                alerts=[],
                caveats=[
                    _NWS_ALERTS_CAVEAT,
                    "Disabled mode is an explicit runtime posture only and does not imply alert absence.",
                ],
            )

        try:
            alerts = await self._load_alerts()
        except Exception as exc:
            record_source_failure(
                "nws-alerts",
                degraded_reason=str(exc),
                freshness_seconds=1800,
                stale_after_seconds=10800,
            )
            raise

        filtered = [alert for alert in alerts if self._matches_filters(alert, query)]
        if query.sort == "severity":
            filtered.sort(
                key=lambda item: (_SEVERITY_ORDER.get(item.severity, 0), _iso_sort_key(item.sent_at or item.effective_at)),
                reverse=True,
            )
        else:
            filtered.sort(key=lambda item: _iso_sort_key(item.sent_at or item.effective_at), reverse=True)
        limited = filtered[: query.limit]
        generated_at = max((item.sent_at for item in alerts if item.sent_at), default=None)
        health = "loaded" if limited else "empty"
        detail = (
            "NWS active alerts loaded successfully."
            if limited
            else "NWS active alerts loaded but no alerts matched the current filters."
        )
        if health == "loaded":
            record_source_success(
                "nws-alerts",
                freshness_seconds=1800,
                stale_after_seconds=10800,
                warning_count=len(limited),
            )
        else:
            record_source_failure(
                "nws-alerts",
                degraded_reason="NWS active alerts returned no matching rows for the current filters.",
                state="stale",
                freshness_seconds=1800,
                stale_after_seconds=10800,
                warning_count=0,
            )
        return NwsAlertsResponse(
            metadata=self._metadata(
                fetched_at=fetched_at,
                generated_at=generated_at,
                count=len(limited),
                source_mode=source_mode,
            ),
            count=len(limited),
            source_health=NwsAlertsSourceHealth(
                source_id="nws-alerts",
                source_label="NWS Alerts API",
                enabled=True,
                source_mode=source_mode,
                health=health,
                loaded_count=len(limited),
                last_fetched_at=fetched_at,
                source_generated_at=generated_at,
                detail=detail,
                error_summary=None,
                caveat=_NWS_ALERTS_CAVEAT,
            ),
            alerts=limited,
            caveats=[
                _NWS_ALERTS_CAVEAT,
                "Live-mode requests should send a responsible custom User-Agent as documented by the NWS API.",
                "Polygon-derived centroids and state-code summaries are bounded geometry aids only and do not prove local footprint or impact.",
                "Free-form alert text remains inert source data only and never changes validation state, source health, or workflow behavior.",
            ],
        )

    async def _load_alerts(self) -> list[NwsAlertEvent]:
        mode = self._settings.nws_alerts_source_mode.strip().lower()
        if mode == "live":
            headers = {
                "Accept": "application/geo+json",
                "User-Agent": self._settings.nws_contact_user_agent,
            }
            async with httpx.AsyncClient(timeout=self._settings.nws_alerts_http_timeout_seconds, headers=headers) as client:
                response = await client.get(self._settings.nws_alerts_api_url)
                response.raise_for_status()
                payload = response.json()
            return self._parse_payload(payload, source_url=self._settings.nws_alerts_api_url)

        fixture_path = _resolve_fixture_path(self._settings.nws_alerts_fixture_path)
        payload = json.loads(fixture_path.read_text(encoding="utf-8"))
        return self._parse_payload(payload, source_url=f"fixture://{fixture_path.name}")

    def _parse_payload(self, payload: Any, *, source_url: str) -> list[NwsAlertEvent]:
        if not isinstance(payload, dict):
            raise ValueError("NWS alerts payload must be a JSON object.")
        features = payload.get("features")
        if not isinstance(features, list):
            return []
        alerts: list[NwsAlertEvent] = []
        for feature in features:
            if not isinstance(feature, dict):
                continue
            properties = feature.get("properties")
            geometry = feature.get("geometry")
            if not isinstance(properties, dict):
                continue
            if _opt_str(properties.get("status")) and (_opt_str(properties.get("status")) or "").lower() == "cancel":
                continue
            event = _opt_str(properties.get("event"))
            headline = _opt_str(properties.get("headline"))
            alert_type = _normalize_alert_type(event, headline)
            severity = _normalize_severity(properties.get("severity"))
            area_desc = _opt_str(properties.get("areaDesc"))
            sent_at = _opt_str(properties.get("sent"))
            effective_at = _opt_str(properties.get("effective"))
            expires_at = _opt_str(properties.get("expires"))
            onset_at = _opt_str(properties.get("onset"))
            latitude, longitude, geometry_summary = _geometry_centroid_summary(geometry)
            area_codes, zone_codes = _extract_area_and_zone_codes(properties.get("geocode"))
            alerts.append(
                NwsAlertEvent(
                    event_id=_opt_str(feature.get("id")) or _opt_str(properties.get("id")) or headline or event or "nws-alert",
                    title=headline or event or "NWS alert",
                    alert_type=alert_type,
                    event=event,
                    headline=headline,
                    severity=severity,
                    urgency=_opt_str(properties.get("urgency")),
                    certainty=_opt_str(properties.get("certainty")),
                    status=_opt_str(properties.get("status")),
                    message_type=_opt_str(properties.get("messageType")),
                    category=_first_str(properties.get("category")),
                    sender_name=_opt_str(properties.get("senderName")),
                    area_description=area_desc,
                    area_codes=area_codes,
                    zone_codes=zone_codes,
                    effective_at=effective_at,
                    onset_at=onset_at,
                    expires_at=expires_at,
                    sent_at=sent_at,
                    updated_at=effective_at or sent_at,
                    instruction=_opt_str(properties.get("instruction")),
                    description=_opt_str(properties.get("description")),
                    response=_first_str(properties.get("response")),
                    geometry_summary=geometry_summary,
                    longitude=longitude,
                    latitude=latitude,
                    source_url=_opt_str(properties.get("@id")) or source_url,
                    source_mode=self._source_mode_label(),
                    caveat=(
                        "NWS alert text is advisory/contextual only. Severity, urgency, certainty, and warning wording do not by themselves establish damage, local impact, legal meaning, or required action."
                    ),
                    evidence_basis="advisory",
                )
            )
        return alerts

    def _matches_filters(self, alert: NwsAlertEvent, query: NwsAlertsQuery) -> bool:
        if query.alert_type != "all" and alert.alert_type != query.alert_type:
            return False
        if query.severity != "all" and alert.severity != query.severity:
            return False
        if query.area and query.area.upper() not in {code.upper() for code in alert.area_codes}:
            return False
        if query.zone and query.zone.upper() not in {code.upper() for code in alert.zone_codes}:
            return False
        if query.event:
            needle = query.event.lower()
            haystacks = [alert.event, alert.title, alert.headline, alert.area_description]
            if not any(value and needle in value.lower() for value in haystacks):
                return False
        return True

    def _metadata(
        self,
        *,
        fetched_at: str,
        generated_at: str | None,
        count: int,
        source_mode: Literal["fixture", "live", "unknown"],
    ) -> NwsAlertsMetadata:
        return NwsAlertsMetadata(
            source="nws-alerts",
            feed_name="nws-active-alerts",
            api_url=self._settings.nws_alerts_api_url,
            source_mode=source_mode,
            fetched_at=fetched_at,
            generated_at=generated_at,
            count=count,
            caveat=_NWS_ALERTS_CAVEAT,
            user_agent_required=True,
            backend_live_mode_only=True,
        )

    def _source_mode_label(self) -> Literal["fixture", "live", "unknown"]:
        mode = self._settings.nws_alerts_source_mode.strip().lower()
        if mode == "fixture":
            return "fixture"
        if mode == "live":
            return "live"
        return "unknown"


def _normalize_alert_type(event: str | None, headline: str | None) -> Literal["warning", "watch", "advisory", "statement", "unknown"]:
    haystack = " ".join(part for part in [event, headline] if part).lower()
    if "warning" in haystack:
        return "warning"
    if "watch" in haystack:
        return "watch"
    if "advisory" in haystack:
        return "advisory"
    if "statement" in haystack:
        return "statement"
    return "unknown"


def _normalize_severity(value: Any) -> Literal["extreme", "severe", "moderate", "minor", "unknown"]:
    text = _opt_str(value)
    if text is None:
        return "unknown"
    lowered = text.lower()
    if lowered in {"extreme", "severe", "moderate", "minor"}:
        return lowered  # type: ignore[return-value]
    return "unknown"


def _extract_area_and_zone_codes(value: Any) -> tuple[list[str], list[str]]:
    if not isinstance(value, dict):
        return ([], [])
    ugc_values = value.get("UGC")
    if not isinstance(ugc_values, list):
        return ([], [])
    zones: list[str] = []
    areas: list[str] = []
    for item in ugc_values:
        code = _opt_str(item)
        if code is None:
            continue
        zones.append(code)
        prefix = code[:2]
        if len(prefix) == 2 and prefix.isalpha() and prefix not in areas:
            areas.append(prefix)
    return (areas, zones)


def _geometry_centroid_summary(geometry: Any) -> tuple[float | None, float | None, str | None]:
    if not isinstance(geometry, dict):
        return (None, None, None)
    coords = list(_iter_coordinates(geometry.get("coordinates")))
    if not coords:
        geometry_type = _opt_str(geometry.get("type"))
        return (None, None, f"{geometry_type.lower()}-present" if geometry_type else None)
    lons = [coord[0] for coord in coords]
    lats = [coord[1] for coord in coords]
    return (
        round(sum(lats) / len(lats), 6),
        round(sum(lons) / len(lons), 6),
        f"centroid:{_opt_str(geometry.get('type')) or 'geometry'}:{len(coords)}",
    )


def _iter_coordinates(value: Any):
    if isinstance(value, (list, tuple)):
        if len(value) >= 2 and all(isinstance(item, (int, float)) for item in value[:2]):
            yield (float(value[0]), float(value[1]))
            return
        for item in value:
            yield from _iter_coordinates(item)


def _first_str(value: Any) -> str | None:
    if isinstance(value, list):
        for item in value:
            text = _opt_str(item)
            if text is not None:
                return text
        return None
    return _opt_str(value)


def _opt_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    without_script = re.sub(r"(?is)<(script|style).*?>.*?</\1>", " ", text)
    without_tags = re.sub(r"(?s)<[^>]+>", " ", without_script)
    collapsed = " ".join(without_tags.split())
    return collapsed or None


def _iso_sort_key(value: str | None) -> float:
    if not value:
        return 0.0
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()
    except ValueError:
        return 0.0


def _resolve_fixture_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute() or path.exists():
        return path
    server_root_candidate = Path(__file__).resolve().parents[2] / path
    if server_root_candidate.exists():
        return server_root_candidate
    return path
