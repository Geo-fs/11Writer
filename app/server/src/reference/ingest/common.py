from __future__ import annotations

from typing import Iterable


def classify_airport_alias(alias: str, *, icao: str | None, iata: str | None, local: str | None, gps: str | None) -> str:
    normalized = alias.strip().upper()
    if icao and normalized == icao.upper():
        return "icao"
    if iata and normalized == iata.upper():
        return "iata"
    if local and normalized == local.upper():
        return "faa"
    if gps and normalized == gps.upper():
        return "gps"
    return "alternate"


def dedupe_aliases(values: Iterable[tuple[str, str]]) -> list[tuple[str, str]]:
    seen: set[tuple[str, str]] = set()
    output: list[tuple[str, str]] = []
    for value, kind in values:
        normalized = value.strip()
        if not normalized:
            continue
        key = (normalized.lower(), kind)
        if key in seen:
            continue
        seen.add(key)
        output.append((normalized, kind))
    return output


def build_search_text(values: Iterable[str | None]) -> str | None:
    tokens = [value.strip().lower() for value in values if value and value.strip()]
    if not tokens:
        return None
    unique: list[str] = []
    seen: set[str] = set()
    for token in tokens:
        if token not in seen:
            seen.add(token)
            unique.append(token)
    return " ".join(unique)


def code_priority(*, icao: str | None, iata: str | None, local: str | None, gps: str | None) -> str | None:
    for candidate in [icao, iata, local, gps]:
        if candidate:
            return candidate
    return None
