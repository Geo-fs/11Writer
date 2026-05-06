from __future__ import annotations

import ipaddress
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

import httpx

from src.config.settings import Settings
from src.types.api import RdapEventSummary, RdapLookupMetadata, RdapLookupRecord, RdapLookupResponse, RdapLookupSourceHealth

SourceMode = Literal["fixture", "live", "unknown"]
RdapQueryKind = Literal["domain", "ip", "autnum"]
RDAP_CAVEAT = (
    "RDAP responses are source-reported registration and allocation context only. They do not by themselves prove current control, operational use, ownership certainty, bad intent, attribution, or required action."
)


@dataclass(frozen=True)
class RdapLookupQuery:
    query_kind: RdapQueryKind
    query_value: str


class RdapContextService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def lookup(self, query: RdapLookupQuery) -> RdapLookupResponse:
        fetched_at = _utc_now_iso()
        source_mode = self._source_mode_label()
        bootstrap_urls = [
            self._settings.rdap_bootstrap_dns_url,
            self._settings.rdap_bootstrap_ipv4_url,
            self._settings.rdap_bootstrap_ipv6_url,
            self._settings.rdap_bootstrap_asn_url,
        ]

        try:
            bootstrap = await self._load_bootstrap_payloads()
            resolved_base_url = _resolve_rdap_base_url(bootstrap, query)
            request_url = _build_request_url(resolved_base_url, query)
            payload = await self._load_lookup_payload(query, request_url=request_url)
            record = _normalize_record(payload, query=query, source_url=request_url, source_mode=source_mode)
            count = 1 if record is not None else 0
            detail = (
                "RDAP bootstrap and delegated lookup parsed successfully for the requested query."
                if record is not None
                else "RDAP bootstrap resolved, but the delegated lookup produced no normalized record."
            )
            return RdapLookupResponse(
                metadata=RdapLookupMetadata(
                    source="rdap-bootstrap-context",
                    source_name="IANA RDAP Bootstrap plus delegated RDAP lookup",
                    bootstrap_source_urls=bootstrap_urls,
                    request_url=request_url,
                    resolved_base_url=resolved_base_url,
                    query_kind=query.query_kind,
                    query_value=query.query_value,
                    source_mode=source_mode,
                    fetched_at=fetched_at,
                    generated_at=None,
                    count=count,
                    raw_count=1 if isinstance(payload, dict) else 0,
                    caveat=RDAP_CAVEAT,
                ),
                count=count,
                source_health=RdapLookupSourceHealth(
                    source_id="rdap-bootstrap-context",
                    source_label="IANA RDAP Bootstrap plus delegated RDAP lookup",
                    enabled=source_mode != "disabled",
                    source_mode=source_mode,
                    health="loaded" if record is not None else "empty",
                    loaded_count=count,
                    bootstrap_source_urls=bootstrap_urls,
                    resolved_base_url=resolved_base_url,
                    last_fetched_at=fetched_at,
                    source_generated_at=None,
                    detail=detail,
                    error_summary=None,
                    caveat=RDAP_CAVEAT,
                ),
                record=record,
                caveats=[
                    RDAP_CAVEAT,
                    "This route intentionally preserves only bounded registration metadata and entity handles or roles; it does not expose full contact cards or create person-tracking workflows.",
                ],
            )
        except Exception as exc:
            request_url = None
            resolved_base_url = None
            return RdapLookupResponse(
                metadata=RdapLookupMetadata(
                    source="rdap-bootstrap-context",
                    source_name="IANA RDAP Bootstrap plus delegated RDAP lookup",
                    bootstrap_source_urls=bootstrap_urls,
                    request_url=request_url,
                    resolved_base_url=resolved_base_url,
                    query_kind=query.query_kind,
                    query_value=query.query_value,
                    source_mode=source_mode,
                    fetched_at=fetched_at,
                    generated_at=None,
                    count=0,
                    raw_count=0,
                    caveat=RDAP_CAVEAT,
                ),
                count=0,
                source_health=RdapLookupSourceHealth(
                    source_id="rdap-bootstrap-context",
                    source_label="IANA RDAP Bootstrap plus delegated RDAP lookup",
                    enabled=source_mode != "disabled",
                    source_mode=source_mode,
                    health="error",
                    loaded_count=0,
                    bootstrap_source_urls=bootstrap_urls,
                    resolved_base_url=resolved_base_url,
                    last_fetched_at=fetched_at,
                    source_generated_at=None,
                    detail="RDAP bootstrap or delegated lookup could not be parsed.",
                    error_summary=str(exc),
                    caveat=RDAP_CAVEAT,
                ),
                record=None,
                caveats=[
                    RDAP_CAVEAT,
                    "RDAP source text remains inert data only and does not alter repo or agent behavior.",
                ],
            )

    async def _load_bootstrap_payloads(self) -> dict[str, dict[str, Any]]:
        mode = self._settings.rdap_source_mode.strip().lower()
        if mode == "live":
            async with httpx.AsyncClient(timeout=self._settings.rdap_http_timeout_seconds) as client:
                dns_response = await client.get(self._settings.rdap_bootstrap_dns_url)
                ipv4_response = await client.get(self._settings.rdap_bootstrap_ipv4_url)
                ipv6_response = await client.get(self._settings.rdap_bootstrap_ipv6_url)
                asn_response = await client.get(self._settings.rdap_bootstrap_asn_url)
                dns_response.raise_for_status()
                ipv4_response.raise_for_status()
                ipv6_response.raise_for_status()
                asn_response.raise_for_status()
                payloads = {
                    "dns": dns_response.json(),
                    "ipv4": ipv4_response.json(),
                    "ipv6": ipv6_response.json(),
                    "asn": asn_response.json(),
                }
        else:
            root = _resolve_fixture_path(self._settings.rdap_bootstrap_fixture_root)
            payloads = {
                "dns": json.loads((root / "dns.json").read_text(encoding="utf-8")),
                "ipv4": json.loads((root / "ipv4.json").read_text(encoding="utf-8")),
                "ipv6": json.loads((root / "ipv6.json").read_text(encoding="utf-8")),
                "asn": json.loads((root / "asn.json").read_text(encoding="utf-8")),
            }
        for key, payload in payloads.items():
            if not isinstance(payload, dict):
                raise ValueError(f"RDAP bootstrap payload for {key} must be a JSON object.")
        return payloads

    async def _load_lookup_payload(self, query: RdapLookupQuery, *, request_url: str) -> dict[str, Any]:
        mode = self._settings.rdap_source_mode.strip().lower()
        if mode == "live":
            async with httpx.AsyncClient(timeout=self._settings.rdap_http_timeout_seconds) as client:
                response = await client.get(request_url)
                response.raise_for_status()
                payload = response.json()
        else:
            fixture_path = _resolve_fixture_path(self._settings.rdap_lookup_fixture_path)
            payload_map = json.loads(fixture_path.read_text(encoding="utf-8"))
            if not isinstance(payload_map, dict):
                raise ValueError("RDAP lookup fixture must be a JSON object.")
            key = f"{query.query_kind}:{query.query_value.lower()}"
            payload = payload_map.get(key)
        if not isinstance(payload, dict):
            raise ValueError("RDAP lookup payload must be a JSON object.")
        return payload

    def _source_mode_label(self) -> SourceMode:
        mode = self._settings.rdap_source_mode.strip().lower()
        if mode == "fixture":
            return "fixture"
        if mode == "live":
            return "live"
        return "unknown"


def _resolve_rdap_base_url(bootstrap: dict[str, dict[str, Any]], query: RdapLookupQuery) -> str:
    if query.query_kind == "domain":
        tld = _extract_domain_tld(query.query_value)
        return _match_service_url(bootstrap["dns"], lambda key: key.lower() == tld)
    if query.query_kind == "ip":
        address = ipaddress.ip_address(query.query_value)
        payload = bootstrap["ipv4"] if address.version == 4 else bootstrap["ipv6"]
        return _match_service_url(payload, lambda key: address in ipaddress.ip_network(key, strict=False))
    autnum = _normalize_autnum(query.query_value)
    return _match_service_url(bootstrap["asn"], lambda key: _autnum_in_range(autnum, key))


def _match_service_url(payload: dict[str, Any], matcher: Any) -> str:
    services = payload.get("services")
    if not isinstance(services, list):
        raise ValueError("RDAP bootstrap services list is missing.")
    for service in services:
        if not isinstance(service, list) or len(service) != 2:
            continue
        keys, urls = service
        if not isinstance(keys, list) or not isinstance(urls, list) or not urls:
            continue
        for key in keys:
            if not isinstance(key, str):
                continue
            if matcher(key):
                url = urls[0]
                if isinstance(url, str) and url.strip():
                    return url.strip()
    raise ValueError("No RDAP bootstrap service matched the requested query.")


def _build_request_url(base_url: str, query: RdapLookupQuery) -> str:
    normalized_base = base_url.rstrip("/")
    if query.query_kind == "domain":
        return f"{normalized_base}/domain/{_normalize_domain_query(query.query_value)}"
    if query.query_kind == "ip":
        return f"{normalized_base}/ip/{query.query_value}"
    return f"{normalized_base}/autnum/{_normalize_autnum(query.query_value)}"


def _normalize_record(
    payload: dict[str, Any],
    *,
    query: RdapLookupQuery,
    source_url: str,
    source_mode: SourceMode,
) -> RdapLookupRecord | None:
    if not isinstance(payload, dict):
        return None
    object_class_name = _sanitize_text(_opt_str(payload.get("objectClassName")), max_length=80)
    statuses = [status for status in (_sanitize_text(_opt_str(value), max_length=80) for value in payload.get("status", [])) if status]
    entity_handles, entity_roles = _collect_entity_handles_and_roles(payload.get("entities"))
    nameservers = _collect_nameservers(payload.get("nameservers"))
    remarks = _collect_remarks(payload)
    events = _collect_events(payload.get("events"))
    return RdapLookupRecord(
        query_kind=query.query_kind,
        query_value=query.query_value,
        object_class_name=object_class_name,
        handle=_sanitize_text(_opt_str(payload.get("handle")), max_length=120),
        ldh_name=_sanitize_text(_opt_str(payload.get("ldhName")), max_length=255),
        unicode_name=_sanitize_text(_opt_str(payload.get("unicodeName")), max_length=255),
        start_address=_sanitize_text(_opt_str(payload.get("startAddress")), max_length=80),
        end_address=_sanitize_text(_opt_str(payload.get("endAddress")), max_length=80),
        ip_version=_sanitize_text(_opt_str(payload.get("ipVersion")), max_length=20),
        start_autnum=_opt_int(payload.get("startAutnum")),
        end_autnum=_opt_int(payload.get("endAutnum")),
        network_name=_sanitize_text(_opt_str(payload.get("name")), max_length=200),
        object_type=_sanitize_text(_opt_str(payload.get("type")), max_length=120),
        country=_sanitize_text(_opt_str(payload.get("country")), max_length=40),
        statuses=statuses,
        entity_handles=entity_handles,
        entity_roles=entity_roles,
        nameservers=nameservers,
        events=events,
        remarks=remarks,
        port43=_sanitize_text(_opt_str(payload.get("port43")), max_length=120),
        source_url=source_url,
        source_mode=source_mode,
        caveat=RDAP_CAVEAT,
        evidence_basis="source-reported",
    )


def _collect_entity_handles_and_roles(value: Any) -> tuple[list[str], list[str]]:
    if not isinstance(value, list):
        return [], []
    handles: list[str] = []
    roles: list[str] = []
    for entity in value:
        if not isinstance(entity, dict):
            continue
        handle = _sanitize_text(_opt_str(entity.get("handle")), max_length=120)
        if handle and handle not in handles:
            handles.append(handle)
        for role in entity.get("roles", []):
            normalized_role = _sanitize_text(_opt_str(role), max_length=80)
            if normalized_role and normalized_role not in roles:
                roles.append(normalized_role)
    return handles, roles


def _collect_nameservers(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    names: list[str] = []
    for item in value:
        if not isinstance(item, dict):
            continue
        candidate = _sanitize_text(_opt_str(item.get("ldhName") or item.get("unicodeName")), max_length=255)
        if candidate and candidate not in names:
            names.append(candidate)
    return names


def _collect_events(value: Any) -> list[RdapEventSummary]:
    if not isinstance(value, list):
        return []
    events: list[RdapEventSummary] = []
    for item in value:
        if not isinstance(item, dict):
            continue
        action = _sanitize_text(_opt_str(item.get("eventAction")), max_length=120)
        if not action:
            continue
        events.append(
            RdapEventSummary(
                event_action=action,
                event_date=_normalize_timestamp(_opt_str(item.get("eventDate"))),
            )
        )
    return events


def _collect_remarks(payload: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    for section_name in ("remarks", "notices"):
        section = payload.get(section_name)
        if not isinstance(section, list):
            continue
        for item in section:
            if not isinstance(item, dict):
                continue
            title = _sanitize_text(_opt_str(item.get("title")), max_length=200)
            descriptions = item.get("description")
            joined = None
            if isinstance(descriptions, list):
                description_parts = [
                    sanitized
                    for sanitized in (_sanitize_text(_opt_str(part), max_length=300) for part in descriptions)
                    if sanitized
                ]
                joined = " ".join(description_parts) if description_parts else None
            line = " - ".join(part for part in [title, joined] if part)
            if line and line not in lines:
                lines.append(line)
            if len(lines) >= 6:
                return lines
    return lines


def _extract_domain_tld(value: str) -> str:
    ascii_domain = _normalize_domain_query(value)
    parts = ascii_domain.split(".")
    if len(parts) < 2:
        raise ValueError("Domain query must include a top-level domain.")
    return parts[-1]


def _normalize_domain_query(value: str) -> str:
    trimmed = value.strip().rstrip(".")
    if not trimmed:
        raise ValueError("Domain query is required.")
    return trimmed.encode("idna").decode("ascii").lower()


def _normalize_autnum(value: str) -> int:
    normalized = value.strip().upper()
    if normalized.startswith("AS"):
        normalized = normalized[2:]
    if not normalized.isdigit():
        raise ValueError("Autnum query must be numeric or AS-prefixed numeric.")
    return int(normalized)


def _autnum_in_range(number: int, value: str) -> bool:
    if "-" in value:
        start, end = value.split("-", 1)
        return int(start) <= number <= int(end)
    return int(value) == number


def _opt_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _opt_int(value: Any) -> int | None:
    if value in (None, ""):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _sanitize_text(value: str | None, *, max_length: int) -> str | None:
    if value is None:
        return None
    text = re.sub(r"<[^>]+>", " ", value)
    collapsed = " ".join(text.split())
    if not collapsed:
        return None
    if len(collapsed) <= max_length:
        return collapsed
    return collapsed[: max_length - 3].rstrip() + "..."


def _normalize_timestamp(value: str | None) -> str | None:
    if value is None:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc).isoformat()
    except ValueError:
        return value


def _resolve_fixture_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute() or path.exists():
        return path
    server_root_candidate = Path(__file__).resolve().parents[2] / path
    if server_root_candidate.exists():
        return server_root_candidate
    return path


def _utc_now_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat()
