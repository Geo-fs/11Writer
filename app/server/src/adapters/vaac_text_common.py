from __future__ import annotations

import html
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone


_FIELD_RE = re.compile(r"^(?P<label>[A-Z0-9 +/()\-]{2,}):\s*(?P<value>.*)$")
_FLIGHT_LEVEL_RE = re.compile(r"\bFL(?P<level>\d{2,3})\b", re.IGNORECASE)
_VOLCANO_RE = re.compile(r"^(?P<name>.+?)\s+(?P<number>\d{6,8})$")


@dataclass(frozen=True)
class ParsedVaacTextAdvisory:
    advisory_number: str | None
    issue_time: str | None
    observed_at: str | None
    volcano_name: str
    volcano_number: str | None
    area: str | None
    source_elevation_text: str | None
    source_elevation_ft: int | None
    information_source: str | None
    aviation_color_code: str | None
    eruption_details: str | None
    observed_ash_text: str | None
    remarks: str | None
    next_advisory: str | None
    max_flight_level: str | None
    caveats: list[str]


def advisory_page_html_to_text(payload: str) -> str:
    without_script = re.sub(r"(?is)<(script|style).*?>.*?</\1>", "\n", payload)
    without_tags = re.sub(r"(?s)<[^>]+>", "\n", without_script)
    return html.unescape(without_tags)


def parse_vaac_text_advisory(raw_text: str) -> ParsedVaacTextAdvisory | None:
    lines = [line.strip() for line in raw_text.splitlines()]
    lines = [line for line in lines if line and line != "* * *"]
    if "VA ADVISORY" not in lines:
        return None
    if any("NONE ISSUED BY THIS OFFICE RECENTLY" in line.upper() for line in lines):
        return None

    fields = _extract_fields(lines)
    issue_time = _parse_issue_time(fields.get("DTG"))
    volcano_name, volcano_number = _parse_volcano(fields.get("VOLCANO"))
    source_elevation_text = fields.get("SOURCE ELEV") or fields.get("SUMMIT ELEV")
    source_elevation_ft = _parse_source_elevation_ft(source_elevation_text)
    max_flight_level = _extract_max_flight_level(
        " ".join(
            part
            for part in [
                fields.get("ERUPTION DETAILS"),
                fields.get("OBS VA CLD"),
                fields.get("FCST VA CLD +6 HR"),
                fields.get("FCST VA CLD +12 HR"),
                fields.get("FCST VA CLD +18 HR"),
            ]
            if part
        )
    )
    caveats: list[str] = []
    if source_elevation_ft is None:
        caveats.append("Source elevation was not exposed as a usable height in this advisory record.")
    if max_flight_level is None:
        caveats.append("Maximum reported flight level was not exposed in this advisory record.")

    return ParsedVaacTextAdvisory(
        advisory_number=fields.get("ADVISORY NR"),
        issue_time=issue_time,
        observed_at=_parse_observed_time(fields.get("OBS VA DTG"), issue_time),
        volcano_name=volcano_name or "Unknown volcano",
        volcano_number=volcano_number,
        area=fields.get("AREA"),
        source_elevation_text=source_elevation_text,
        source_elevation_ft=source_elevation_ft,
        information_source=fields.get("INFO SOURCE"),
        aviation_color_code=fields.get("AVIATION COLOR CODE"),
        eruption_details=fields.get("ERUPTION DETAILS"),
        observed_ash_text=fields.get("OBS VA CLD"),
        remarks=fields.get("RMK"),
        next_advisory=fields.get("NXT ADVISORY"),
        max_flight_level=max_flight_level,
        caveats=caveats,
    )


def build_vaac_summary(
    center_label: str,
    volcano_name: str,
    advisory_number: str | None,
    issue_time: str | None,
    max_flight_level: str | None,
) -> str:
    parts = [f"{center_label} advisory for {volcano_name}"]
    if advisory_number:
        parts.append(f"advisory {advisory_number}")
    if max_flight_level:
        parts.append(f"reported to {max_flight_level}")
    if issue_time:
        parts.append(f"issued {issue_time}")
    return ", ".join(parts)


def _extract_fields(lines: list[str]) -> dict[str, str]:
    fields: dict[str, str] = {}
    current_label: str | None = None
    for line in lines:
        match = _FIELD_RE.match(line)
        if match:
            current_label = match.group("label").strip()
            fields[current_label] = match.group("value").strip()
            continue
        if current_label is not None:
            fields[current_label] = f"{fields[current_label]} {line}".strip()
    return fields


def _parse_issue_time(value: str | None) -> str | None:
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y%m%d/%H%MZ").replace(tzinfo=timezone.utc).isoformat()
    except ValueError:
        return value


def _parse_observed_time(value: str | None, issue_time: str | None) -> str | None:
    if not value or not issue_time:
        return None
    try:
        issue_dt = datetime.fromisoformat(issue_time.replace("Z", "+00:00")).astimezone(timezone.utc)
        day = int(value[0:2])
        hour = int(value[3:5])
        minute = int(value[5:7])
        candidate = issue_dt.replace(day=1, hour=hour, minute=minute, second=0, microsecond=0) + timedelta(days=day - 1)
        if candidate - issue_dt > timedelta(days=15):
            previous_month = (issue_dt.replace(day=1) - timedelta(days=1)).replace(hour=hour, minute=minute, second=0, microsecond=0)
            candidate = previous_month.replace(day=day)
        elif issue_dt - candidate > timedelta(days=15):
            next_month_anchor = (issue_dt.replace(day=28) + timedelta(days=4)).replace(day=1, hour=hour, minute=minute, second=0, microsecond=0)
            candidate = next_month_anchor + timedelta(days=day - 1)
        return candidate.isoformat()
    except (ValueError, IndexError):
        return value


def _parse_volcano(value: str | None) -> tuple[str | None, str | None]:
    if not value:
        return None, None
    match = _VOLCANO_RE.match(value.strip())
    if match is None:
        return value.strip(), None
    return match.group("name").strip(), match.group("number")


def _parse_source_elevation_ft(value: str | None) -> int | None:
    if not value:
        return None
    match_ft = re.search(r"(\d+)\s*FT", value, flags=re.IGNORECASE)
    if match_ft is not None:
        return int(match_ft.group(1))
    match_m = re.search(r"(\d+)\s*M", value, flags=re.IGNORECASE)
    if match_m is not None:
        meters = int(match_m.group(1))
        return round(meters * 3.28084)
    return None


def _extract_max_flight_level(text: str) -> str | None:
    levels = [int(match.group("level")) for match in _FLIGHT_LEVEL_RE.finditer(text)]
    if not levels:
        return None
    return f"FL{max(levels)}"
