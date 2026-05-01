from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timedelta, timezone
from html.parser import HTMLParser
from typing import Any, Literal
from urllib.parse import urljoin, urlparse

import httpx
from sqlmodel import Session, select

from app.models.common import SourceLifecycleState, SourceTrustTier
from app.models.connector import Connector
from app.models.discovered_source import DiscoveredSource
from app.models.record import Record
from app.models.wave import Wave
from app.services.source_policy_service import (
    apply_policy_to_source,
)
from app.services.source_policy_service import (
    approve_discovered_source as approve_source_with_policy,
)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class LinkExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []
        self.feed_links: list[str] = []
        self.title: str = ""
        self._in_title = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = {key.lower(): value for key, value in attrs if value is not None}
        if tag.lower() == "a" and attr_map.get("href"):
            self.links.append(attr_map["href"])
        if tag.lower() == "link":
            rel = (attr_map.get("rel") or "").lower()
            typ = (attr_map.get("type") or "").lower()
            href = attr_map.get("href")
            if href and ("alternate" in rel and ("rss" in typ or "atom" in typ)):
                self.feed_links.append(href)
        if tag.lower() == "title":
            self._in_title = True

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "title":
            self._in_title = False

    def handle_data(self, data: str) -> None:
        if self._in_title and data.strip():
            self.title = data.strip()


def _parse_csv_keywords(text: str) -> list[str]:
    return [token.strip().casefold() for token in text.split() if token.strip()]


def _extract_wave_keywords(wave: Wave) -> list[str]:
    text = f"{wave.name} {wave.description}".casefold()
    terms = _parse_csv_keywords(text)
    return [term for term in terms if len(term) >= 4][:20]


def _extract_urls_from_text(text: str) -> list[str]:
    tokens = text.split()
    urls = [token.strip("()[]{}<>,\"'") for token in tokens if token.lower().startswith("http")]
    return urls[:20]


def _classify_url(url: str) -> tuple[str, str | None]:
    lowered = url.casefold()
    if lowered.endswith(".rss") or lowered.endswith(".xml") or "feed" in lowered:
        return "rss", "rss_news"
    if lowered.endswith(".json") or "/api/" in lowered:
        return "api_json", None
    if lowered.endswith(".pdf"):
        return "document_pdf", None
    if any(token in lowered for token in ["/data", "open-data", "opendata", "dataset"]):
        return "open_data_page", None
    return "web_page", None


def _score_relevance(url: str, title: str, keywords: list[str]) -> float:
    haystack = f"{url} {title}".casefold()
    if not keywords:
        return 0.3
    hits = sum(1 for keyword in keywords if keyword in haystack)
    return min(1.0, 0.2 + 0.2 * hits)


def _parent_domain(url: str) -> str | None:
    parsed = urlparse(url)
    return parsed.netloc or None


def _normalize_url(url: str) -> str:
    parsed = urlparse(url)
    normalized_path = parsed.path or "/"
    if normalized_path != "/" and normalized_path.endswith("/"):
        normalized_path = normalized_path[:-1]
    query = f"?{parsed.query}" if parsed.query else ""
    return f"{parsed.scheme}://{parsed.netloc}{normalized_path}{query}"


def _default_fetch(url: str) -> tuple[int, str, bytes]:
    response = httpx.get(url, timeout=12.0, follow_redirects=True)
    return response.status_code, response.headers.get("Content-Type", ""), response.content


def _collect_seed_urls(session: Session, wave: Wave, request_seed_urls: list[str]) -> list[str]:
    seeds: list[str] = []
    seeds.extend(request_seed_urls)
    seeds.extend(_extract_urls_from_text(f"{wave.name} {wave.description}"))

    connectors = list(session.exec(select(Connector).where(Connector.wave_id == wave.id)))
    for connector in connectors:
        config = connector.config_json or {}
        if connector.type == "rss_news" and isinstance(config.get("feed_url"), str):
            seeds.append(config["feed_url"])
    recent_source_urls = list(
        session.exec(
            select(Record.source_url)
            .where(Record.wave_id == wave.id, Record.source_url.is_not(None))
            .order_by(Record.collected_at.desc())
            .limit(15)
        )
    )
    seeds.extend([url for url in recent_source_urls if isinstance(url, str)])
    return [seed for seed in seeds if seed.startswith("http")]


def run_discovery_for_wave(
    session: Session,
    wave: Wave,
    *,
    seed_urls: list[str] | None = None,
    fetcher: Callable[[str], tuple[int, str, bytes]] | None = None,
) -> tuple[int, int]:
    effective_fetcher = fetcher or _default_fetch
    keywords = _extract_wave_keywords(wave)
    deduped_count = 0
    discovered_count = 0

    all_seeds = _collect_seed_urls(session, wave, seed_urls or [])
    # simple deterministic heuristic targets if user/context has no direct URL
    if not all_seeds:
        all_seeds = [
            "https://www.nasa.gov/rss/dyn/breaking_news.rss",
            "https://www.weather.gov/",
            "https://www.noaa.gov/",
        ]

    candidate_urls: set[str] = set()
    for seed in all_seeds[:25]:
        candidate_urls.add(seed)
        source_type, _ = _classify_url(seed)
        if source_type in {"rss", "api_json", "document_pdf"}:
            continue
        try:
            status_code, content_type, body = effective_fetcher(seed)
        except Exception:  # noqa: BLE001
            continue
        if status_code >= 400:
            continue
        text_body = body.decode("utf-8", errors="ignore")
        parser = LinkExtractor()
        parser.feed(text_body)
        for link in parser.feed_links[:10]:
            candidate_urls.add(urljoin(seed, link))
        for link in parser.links[:50]:
            absolute = urljoin(seed, link)
            stype, _ = _classify_url(absolute)
            if stype in {"rss", "api_json", "document_pdf", "open_data_page"}:
                candidate_urls.add(absolute)
        if "rss" in content_type.lower() or "atom" in content_type.lower():
            candidate_urls.add(seed)

    pending: list[DiscoveredSource] = []
    for raw_url in sorted(candidate_urls):
        if not raw_url.startswith("http"):
            continue
        url = _normalize_url(raw_url)
        exists = session.exec(
            select(DiscoveredSource.id).where(
                DiscoveredSource.wave_id == wave.id,
                DiscoveredSource.url == url,
            )
        ).first()
        if exists is not None:
            deduped_count += 1
            continue

        source_type, suggested_connector = _classify_url(url)
        title = urlparse(url).path.split("/")[-1] or urlparse(url).netloc
        relevance = _score_relevance(url, title, keywords)
        free_access = True
        description_summary = None
        metadata_json = {"keywords": keywords}

        pending.append(
            DiscoveredSource(
                wave_id=wave.id,
                url=url,
                title=title,
                source_type=source_type,
                parent_domain=_parent_domain(url),
                status=SourceLifecycleState.CANDIDATE,
                trust_tier=SourceTrustTier.TIER_4,
                discovery_method="seed+page-inspection",
                relevance_score=relevance,
                stability_score=None,
                free_access=free_access,
                suggested_connector_type=suggested_connector,
                description_summary=description_summary,
                metadata_json=metadata_json,
                discovered_at=utc_now(),
                last_checked_at=None,
                auto_check_enabled=True,
                check_interval_minutes=60,
                next_check_at=utc_now() + timedelta(minutes=30),
            )
        )
        discovered_count += 1

    if pending:
        session.add_all(pending)
        session.commit()
        for source in pending:
            apply_policy_to_source(session, source, trigger="discovery")

    return discovered_count, deduped_count


def list_discovered_sources_for_wave(
    session: Session,
    wave_id: int,
    *,
    limit: int = 200,
    status: SourceLifecycleState | None = None,
    source_type: str | None = None,
    min_relevance_score: float | None = None,
    min_stability_score: float | None = None,
    parent_domain: str | None = None,
    approved_only: bool = False,
    new_only: bool = False,
    sort: Literal[
        "newest",
        "oldest",
        "relevance_desc",
        "relevance_asc",
        "stability_desc",
        "stability_asc",
    ] = "relevance_desc",
) -> list[DiscoveredSource]:
    bounded = max(1, min(limit, 300))
    statement = select(DiscoveredSource).where(DiscoveredSource.wave_id == wave_id)
    if approved_only:
        statement = statement.where(DiscoveredSource.status == SourceLifecycleState.APPROVED)
    elif new_only:
        statement = statement.where(DiscoveredSource.status == SourceLifecycleState.CANDIDATE)
    elif status is not None:
        statement = statement.where(DiscoveredSource.status == status)
    if source_type:
        statement = statement.where(DiscoveredSource.source_type == source_type)
    if min_relevance_score is not None:
        statement = statement.where(DiscoveredSource.relevance_score >= min_relevance_score)
    if min_stability_score is not None:
        statement = statement.where(DiscoveredSource.stability_score >= min_stability_score)
    if parent_domain:
        statement = statement.where(DiscoveredSource.parent_domain.ilike(f"%{parent_domain}%"))

    if sort == "oldest":
        statement = statement.order_by(DiscoveredSource.discovered_at.asc())
    elif sort == "relevance_desc":
        statement = statement.order_by(
            DiscoveredSource.relevance_score.desc(),
            DiscoveredSource.discovered_at.desc(),
        )
    elif sort == "relevance_asc":
        statement = statement.order_by(
            DiscoveredSource.relevance_score.asc(),
            DiscoveredSource.discovered_at.desc(),
        )
    elif sort == "stability_desc":
        statement = statement.order_by(
            DiscoveredSource.stability_score.desc(),
            DiscoveredSource.discovered_at.desc(),
        )
    elif sort == "stability_asc":
        statement = statement.order_by(
            DiscoveredSource.stability_score.asc(),
            DiscoveredSource.discovered_at.desc(),
        )
    else:
        statement = statement.order_by(DiscoveredSource.discovered_at.desc())
    statement = statement.limit(bounded)
    return list(session.exec(statement))


def get_discovered_source_or_none(session: Session, source_id: int) -> DiscoveredSource | None:
    return session.get(DiscoveredSource, source_id)


def update_discovered_source(
    session: Session,
    source: DiscoveredSource,
    **updates: Any,
) -> DiscoveredSource:
    for key, value in updates.items():
        if value is not None:
            setattr(source, key, value)
    session.add(source)
    session.commit()
    session.refresh(source)
    return source


def approve_discovered_source(
    session: Session,
    source: DiscoveredSource,
) -> int | None:
    return approve_source_with_policy(session, source, approval_origin="manual")
