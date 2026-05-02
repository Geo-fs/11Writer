from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from html import unescape
from html.parser import HTMLParser
from typing import Any
from urllib.parse import parse_qsl, urlencode, urljoin, urlsplit, urlunsplit

from src.types.source_discovery import SourceDiscoverySocialMetadataSummary


POSITIVE_HINTS = (
    "article",
    "content",
    "story",
    "post",
    "entry",
    "main",
    "body",
    "text",
    "caption",
)
NEGATIVE_HINTS = (
    "nav",
    "menu",
    "footer",
    "header",
    "sidebar",
    "social",
    "share",
    "promo",
    "ad-",
    "advert",
    "comment",
    "related",
    "newsletter",
    "cookie",
    "banner",
)
ARTICLE_JSONLD_TYPES = {
    "article",
    "newsarticle",
    "blogposting",
    "report",
    "analysisnewsarticle",
}
SOCIAL_JSONLD_TYPES = {
    "socialmediaposting",
    "photograph",
    "imageobject",
    "article",
    "newsarticle",
}
BLOCK_TAGS = {"article", "main", "section", "div", "body", "figure", "blockquote", "li"}
VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}


@dataclass
class ArticleExtractionResult:
    text: str
    title: str | None
    author: str | None
    published_at: str | None
    canonical_url: str | None
    method: str


@dataclass
class SocialExtractionResult:
    metadata: SourceDiscoverySocialMetadataSummary
    text: str
    method: str


@dataclass
class _BlockCandidate:
    text: str
    tag: str
    attrs_blob: str
    paragraph_count: int
    heading_count: int
    link_chars: int
    captions: list[str] = field(default_factory=list)
    alt_texts: list[str] = field(default_factory=list)


@dataclass
class _NodeContext:
    tag: str
    attrs: dict[str, str]
    text_parts: list[str] = field(default_factory=list)
    captions: list[str] = field(default_factory=list)
    alt_texts: list[str] = field(default_factory=list)
    media_urls: list[str] = field(default_factory=list)
    paragraph_count: int = 0
    heading_count: int = 0
    link_chars: int = 0

    @property
    def attrs_blob(self) -> str:
        return " ".join(value for value in (self.attrs.get("class", ""), self.attrs.get("id", "")) if value).strip()


class _SemanticHtmlParser(HTMLParser):
    def __init__(self, *, base_url: str | None = None) -> None:
        super().__init__(convert_charrefs=True)
        self._base_url = base_url
        self._stack: list[_NodeContext] = [_NodeContext("document", {})]
        self._title_parts: list[str] = []
        self._json_ld_parts: list[str] = []
        self._json_ld_depth = 0
        self._current_script_type: str | None = None
        self._in_title = False
        self.meta: dict[str, str] = {}
        self.link_rel: dict[str, str] = {}
        self.time_values: list[str] = []
        self.blocks: list[_BlockCandidate] = []
        self.all_text_parts: list[str] = []
        self.media_urls: list[str] = []
        self.alt_texts: list[str] = []
        self.captions: list[str] = []
        self.json_ld_objects: list[dict[str, Any]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        normalized = {key.lower(): (value or "").strip() for key, value in attrs if key}
        tag = tag.lower()
        if tag == "title":
            self._in_title = True
        if tag == "meta":
            self._handle_meta(normalized)
        elif tag == "link":
            self._handle_link(normalized)
        elif tag == "time":
            datetime_value = normalized.get("datetime")
            if datetime_value:
                self.time_values.append(datetime_value.strip())
        elif tag == "img":
            self._handle_media(normalized)
        elif tag in {"video", "source"}:
            src = normalized.get("src")
            if src:
                self.media_urls.append(_absolute_url(src, self._base_url))
        elif tag == "script":
            self._current_script_type = normalized.get("type", "").lower()
            if "application/ld+json" in self._current_script_type:
                self._json_ld_depth += 1
        node = _NodeContext(tag=tag, attrs=normalized)
        self._stack.append(node)
        if tag == "p":
            node.paragraph_count += 1
        elif tag in {"h1", "h2", "h3"}:
            node.heading_count += 1

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag == "title":
            self._in_title = False
        if tag == "script" and self._current_script_type and "application/ld+json" in self._current_script_type:
            self._json_ld_depth = max(0, self._json_ld_depth - 1)
            if self._json_ld_depth == 0:
                self._flush_json_ld()
                self._current_script_type = None
        if len(self._stack) <= 1:
            return
        node = self._stack.pop()
        text = _normalize_text(" ".join(node.text_parts))
        if tag == "figcaption" and text:
            self.captions.append(text)
            self._stack[-1].captions.append(text)
        if text:
            self._stack[-1].text_parts.append(text)
            self._stack[-1].paragraph_count += node.paragraph_count
            self._stack[-1].heading_count += node.heading_count
            if tag == "a":
                self._stack[-1].link_chars += len(text)
            else:
                self._stack[-1].link_chars += node.link_chars
        self._stack[-1].captions.extend(node.captions)
        self._stack[-1].alt_texts.extend(node.alt_texts)
        self._stack[-1].media_urls.extend(node.media_urls)
        if tag in BLOCK_TAGS and text:
            self.blocks.append(
                _BlockCandidate(
                    text=text,
                    tag=tag,
                    attrs_blob=node.attrs_blob,
                    paragraph_count=max(0, node.paragraph_count),
                    heading_count=max(0, node.heading_count),
                    link_chars=max(0, node.link_chars),
                    captions=_dedupe_preserve(node.captions),
                    alt_texts=_dedupe_preserve(node.alt_texts),
                )
            )

    def handle_data(self, data: str) -> None:
        if self._json_ld_depth > 0:
            self._json_ld_parts.append(data)
            return
        text = _normalize_text(data)
        if not text:
            return
        if self._in_title:
            self._title_parts.append(text)
        self._stack[-1].text_parts.append(text)
        self.all_text_parts.append(text)

    @property
    def title(self) -> str | None:
        return _normalize_optional(" ".join(self._title_parts))

    @property
    def body_text(self) -> str:
        return _normalize_text(" ".join(self.all_text_parts))

    def _handle_meta(self, attrs: dict[str, str]) -> None:
        key = (attrs.get("property") or attrs.get("name") or attrs.get("itemprop") or "").strip().casefold()
        content = _normalize_optional(attrs.get("content"))
        if key and content:
            self.meta[key] = content

    def _handle_link(self, attrs: dict[str, str]) -> None:
        rel = attrs.get("rel", "").strip().casefold()
        href = attrs.get("href", "").strip()
        if rel and href:
            self.link_rel[rel] = _absolute_url(href, self._base_url)

    def _handle_media(self, attrs: dict[str, str]) -> None:
        src = attrs.get("src") or attrs.get("data-src") or attrs.get("srcset", "").split(",", 1)[0].strip().split(" ", 1)[0]
        alt = _normalize_optional(attrs.get("alt"))
        if src:
            absolute = _absolute_url(src, self._base_url)
            self.media_urls.append(absolute)
            self._stack[-1].media_urls.append(absolute)
        if alt:
            self.alt_texts.append(alt)
            self._stack[-1].alt_texts.append(alt)

    def _flush_json_ld(self) -> None:
        raw = _normalize_text(" ".join(self._json_ld_parts))
        self._json_ld_parts.clear()
        if not raw:
            return
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            return
        for obj in _flatten_json_ld(payload):
            if isinstance(obj, dict):
                self.json_ld_objects.append(obj)


def extract_article_snapshot_from_html(html: str, *, base_url: str | None = None) -> ArticleExtractionResult:
    parser = _build_parser(html, base_url=base_url)
    json_ld = _best_jsonld_object(parser.json_ld_objects, ARTICLE_JSONLD_TYPES)
    jsonld_text = _jsonld_text(json_ld, "articleBody") or ""
    best_block = _best_block(parser.blocks)
    block_text = best_block.text if best_block is not None else ""
    if len(jsonld_text) >= 160:
        text = jsonld_text
        method = "html_article_json_ld"
    elif len(block_text) >= 120:
        text = block_text
        method = "html_article_readability"
    else:
        text = parser.body_text
        method = "html_article_fallback"
    title = (
        _jsonld_text(json_ld, "headline")
        or _meta_value(parser, "og:title", "twitter:title", "title")
        or parser.title
    )
    author = (
        _jsonld_person_name(json_ld, "author")
        or _meta_value(parser, "author", "article:author", "byline")
    )
    published_at = (
        _jsonld_text(json_ld, "datePublished")
        or _meta_value(parser, "article:published_time", "datepublished", "pubdate", "date")
        or (parser.time_values[0] if parser.time_values else None)
    )
    canonical_url = (
        _jsonld_text(json_ld, "url")
        or parser.link_rel.get("canonical")
        or _meta_value(parser, "og:url")
    )
    return ArticleExtractionResult(
        text=_normalize_text(text),
        title=_normalize_optional(title),
        author=_normalize_optional(author),
        published_at=_normalize_optional(published_at),
        canonical_url=_canonical_url(canonical_url, base_url=base_url),
        method=method,
    )


def extract_social_metadata_from_html(
    html: str,
    *,
    url: str,
) -> SocialExtractionResult:
    parser = _build_parser(html, base_url=url)
    json_ld = _best_jsonld_object(parser.json_ld_objects, SOCIAL_JSONLD_TYPES)
    best_block = _best_block(parser.blocks)
    block_excerpt = ""
    if best_block is not None:
        block_excerpt = best_block.text[:1200]
    plain_excerpt = parser.body_text[:1200]
    description = (
        _jsonld_text(json_ld, "description")
        or _meta_value(parser, "og:description", "description", "twitter:description")
    )
    captions = _dedupe_preserve(
        [*_jsonld_list(json_ld, "caption"), *parser.captions, *(best_block.captions if best_block else [])]
    )
    alt_texts = _dedupe_preserve(
        [*parser.alt_texts, *(best_block.alt_texts if best_block else [])]
    )
    media_urls = _dedupe_preserve(
        [
            *_jsonld_url_list(json_ld, "image", base_url=url),
            *_meta_media_urls(parser, base_url=url),
            *parser.media_urls,
        ]
    )
    evidence_parts = [
        _jsonld_text(json_ld, "articleBody"),
        description,
        block_excerpt,
        plain_excerpt,
        " ".join(captions),
        " ".join(alt_texts),
    ]
    evidence_text = _normalize_optional(" ".join(part for part in evidence_parts if part))
    metadata = SourceDiscoverySocialMetadataSummary(
        display_title=(
            _jsonld_text(json_ld, "headline")
            or _jsonld_text(json_ld, "name")
            or _meta_value(parser, "og:title", "twitter:title", "title")
            or parser.title
        ),
        description=_normalize_optional(description),
        author=(
            _jsonld_person_name(json_ld, "author")
            or _meta_value(parser, "author", "article:author", "twitter:creator")
        ),
        published_at=(
            _jsonld_text(json_ld, "datePublished")
            or _meta_value(parser, "article:published_time", "datepublished")
            or (parser.time_values[0] if parser.time_values else None)
        ),
        image_url=media_urls[0] if media_urls else None,
        media_hints=_media_hints(url=url, media_urls=media_urls, captions=captions, alt_texts=alt_texts),
        media_urls=media_urls,
        alt_texts=alt_texts,
        captions=captions,
        evidence_text=evidence_text,
        canonical_url=(
            _canonical_url(_jsonld_text(json_ld, "url"), base_url=url)
            or _canonical_url(parser.link_rel.get("canonical"), base_url=url)
            or _canonical_url(_meta_value(parser, "og:url"), base_url=url)
        ),
        extraction_method="social_page_evidence",
    )
    text = _normalize_text(
        " ".join(
            part for part in [
                metadata.display_title,
                metadata.description,
                metadata.author,
                metadata.published_at,
                metadata.evidence_text,
                " ".join(metadata.captions),
                " ".join(metadata.alt_texts),
            ] if part
        )
    )
    return SocialExtractionResult(metadata=metadata, text=text, method="social_page_evidence")


def _build_parser(html: str, *, base_url: str | None) -> _SemanticHtmlParser:
    parser = _SemanticHtmlParser(base_url=base_url)
    parser.feed(_strip_noise(html))
    parser.close()
    return parser


def _strip_noise(html: str) -> str:
    cleaned = re.sub(r"(?is)<!--.*?-->", " ", html)
    cleaned = re.sub(r"(?is)<(noscript|svg|canvas|iframe).*?>.*?</\1>", " ", cleaned)
    return cleaned


def _best_block(blocks: list[_BlockCandidate]) -> _BlockCandidate | None:
    scored: list[tuple[float, _BlockCandidate]] = []
    for block in blocks:
        text = block.text
        if len(text) < 60:
            continue
        attrs_blob = block.attrs_blob.casefold()
        positive_hits = sum(1 for hint in POSITIVE_HINTS if hint in attrs_blob or hint == block.tag)
        negative_hits = sum(1 for hint in NEGATIVE_HINTS if hint in attrs_blob)
        sentence_count = len(re.findall(r"[.!?]", text))
        link_density = block.link_chars / max(len(text), 1)
        score = (
            len(text)
            + (block.paragraph_count * 180)
            + (block.heading_count * 70)
            + (sentence_count * 18)
            + (positive_hits * 140)
            + (len(block.captions) * 30)
            - (negative_hits * 180)
            - int(link_density * 500)
        )
        scored.append((score, block))
    if not scored:
        return None
    scored.sort(key=lambda item: item[0], reverse=True)
    return scored[0][1]


def _meta_value(parser: _SemanticHtmlParser, *keys: str) -> str | None:
    for key in keys:
        value = parser.meta.get(key.casefold())
        if value:
            return value
    return None


def _jsonld_text(payload: dict[str, Any] | None, key: str) -> str | None:
    if not payload:
        return None
    value = payload.get(key)
    if isinstance(value, str):
        return _normalize_optional(value)
    if isinstance(value, dict):
        for candidate_key in ("name", "text", "@value", "url"):
            candidate = value.get(candidate_key)
            if isinstance(candidate, str):
                return _normalize_optional(candidate)
    if isinstance(value, list):
        parts = [_normalize_optional(item if isinstance(item, str) else item.get("name") if isinstance(item, dict) else None) for item in value]
        return _normalize_optional(" ".join(part for part in parts if part))
    return None


def _jsonld_list(payload: dict[str, Any] | None, key: str) -> list[str]:
    if not payload:
        return []
    value = payload.get(key)
    if isinstance(value, str):
        return [_normalize_text(value)] if value.strip() else []
    if isinstance(value, list):
        values: list[str] = []
        for item in value:
            if isinstance(item, str) and item.strip():
                values.append(_normalize_text(item))
            elif isinstance(item, dict):
                for candidate_key in ("name", "text", "caption"):
                    candidate = item.get(candidate_key)
                    if isinstance(candidate, str) and candidate.strip():
                        values.append(_normalize_text(candidate))
                        break
        return values
    return []


def _jsonld_url_list(payload: dict[str, Any] | None, key: str, *, base_url: str) -> list[str]:
    if not payload:
        return []
    value = payload.get(key)
    values: list[str] = []
    items = value if isinstance(value, list) else [value]
    for item in items:
        if isinstance(item, str) and item.strip():
            values.append(_absolute_url(item, base_url))
        elif isinstance(item, dict):
            url = item.get("url") or item.get("contentUrl")
            if isinstance(url, str) and url.strip():
                values.append(_absolute_url(url, base_url))
    return values


def _jsonld_person_name(payload: dict[str, Any] | None, key: str) -> str | None:
    if not payload:
        return None
    value = payload.get(key)
    if isinstance(value, str):
        return _normalize_optional(value)
    if isinstance(value, dict):
        candidate = value.get("name") or value.get("@id")
        if isinstance(candidate, str):
            return _normalize_optional(candidate)
    if isinstance(value, list):
        names = []
        for item in value:
            if isinstance(item, str) and item.strip():
                names.append(_normalize_text(item))
            elif isinstance(item, dict):
                candidate = item.get("name")
                if isinstance(candidate, str) and candidate.strip():
                    names.append(_normalize_text(candidate))
        return _normalize_optional(", ".join(names))
    return None


def _best_jsonld_object(objects: list[dict[str, Any]], allowed_types: set[str]) -> dict[str, Any] | None:
    best: dict[str, Any] | None = None
    best_score = -1
    for payload in objects:
        types = _jsonld_types(payload)
        if not types or not (types & allowed_types):
            continue
        score = 0
        for key in ("articleBody", "headline", "description", "caption", "image", "datePublished", "author"):
            if payload.get(key):
                score += 1
        if score > best_score:
            best = payload
            best_score = score
    return best


def _jsonld_types(payload: dict[str, Any]) -> set[str]:
    raw = payload.get("@type")
    if isinstance(raw, str):
        return {raw.casefold()}
    if isinstance(raw, list):
        return {str(item).casefold() for item in raw}
    return set()


def _flatten_json_ld(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, dict):
        values = [payload]
        graph = payload.get("@graph")
        if isinstance(graph, list):
            values.extend(item for item in graph if isinstance(item, dict))
        return values
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    return []


def _meta_media_urls(parser: _SemanticHtmlParser, *, base_url: str) -> list[str]:
    urls = []
    for key in ("og:image", "twitter:image", "og:video", "twitter:player"):
        value = parser.meta.get(key)
        if value:
            urls.append(_absolute_url(value, base_url))
    return urls


def _media_hints(*, url: str, media_urls: list[str], captions: list[str], alt_texts: list[str]) -> list[str]:
    hints: list[str] = []
    lowered_url = url.casefold()
    if any(token in lowered_url for token in ("x.com", "twitter.com", "instagram.com", "tiktok.com", "facebook.com")):
        hints.append("social-post")
    if any(token in lowered_url for token in ("youtube.com", "youtu.be", "vimeo.com")):
        hints.append("video")
    if any(media.casefold().endswith(ext) for media in media_urls for ext in (".jpg", ".jpeg", ".png", ".gif", ".webp")):
        hints.append("image")
    if any(media.casefold().endswith(ext) for media in media_urls for ext in (".mp4", ".mov", ".m3u8", ".webm")):
        hints.append("video")
    if captions or alt_texts:
        hints.append("captioned-media")
    return _dedupe_preserve(hints)


def _absolute_url(value: str, base_url: str | None) -> str:
    if base_url:
        return urljoin(base_url, value)
    return value


def _canonical_url(value: str | None, *, base_url: str | None) -> str | None:
    normalized = _normalize_optional(value)
    if not normalized:
        return None
    absolute = _absolute_url(normalized, base_url)
    split = urlsplit(absolute)
    filtered_pairs = []
    for key, item in parse_qsl(split.query, keep_blank_values=True):
        lowered = key.casefold()
        if lowered.startswith("utm_") or lowered in {"fbclid", "gclid", "igshid", "ref", "ref_src"}:
            continue
        filtered_pairs.append((key, item))
    query = urlencode(filtered_pairs, doseq=True)
    return urlunsplit((split.scheme, split.netloc, split.path, query, ""))


def _normalize_text(text: str) -> str:
    value = unescape(text or "")
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def _normalize_optional(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = _normalize_text(value)
    return normalized or None


def _dedupe_preserve(values: list[str]) -> list[str]:
    seen: set[str] = set()
    results: list[str] = []
    for value in values:
        normalized = _normalize_optional(value)
        if not normalized:
            continue
        if normalized in seen:
            continue
        seen.add(normalized)
        results.append(normalized)
    return results
