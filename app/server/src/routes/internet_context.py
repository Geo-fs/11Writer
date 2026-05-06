from __future__ import annotations

import ipaddress
import re

from fastapi import APIRouter, Depends, HTTPException, Query

from src.config.settings import Settings, get_settings
from src.services.crtsh_service import CrtShLookupQuery, CrtShService
from src.services.rdap_context_service import RdapContextService, RdapLookupQuery
from src.types.api import CrtShLookupResponse, RdapLookupResponse

router = APIRouter(prefix="/api/context/internet", tags=["internet-context"])

_DOMAIN_PATTERN = re.compile(r"^(?=.{1,253}$)(?!-)[A-Za-z0-9.-]+\.[A-Za-z]{2,63}$")


@router.get("/rdap", response_model=RdapLookupResponse)
async def rdap_lookup(
    kind: str = Query(..., pattern=r"^(domain|ip|autnum)$"),
    query: str = Query(..., min_length=1, max_length=255),
    settings: Settings = Depends(get_settings),
) -> RdapLookupResponse:
    normalized_kind = kind.strip().lower()
    normalized_query = _normalize_rdap_query(normalized_kind, query)
    return await RdapContextService(settings).lookup(
        RdapLookupQuery(query_kind=normalized_kind, query_value=normalized_query)
    )


@router.get("/crtsh", response_model=CrtShLookupResponse)
async def crtsh_lookup(
    query: str = Query(..., min_length=1, max_length=253, description="Domain query for certificate-transparency search."),
    include_subdomains: bool = Query(default=True),
    limit: int = Query(default=25, ge=1, le=100),
    settings: Settings = Depends(get_settings),
) -> CrtShLookupResponse:
    normalized_domain = _normalize_domain(query)
    return await CrtShService(settings).lookup(
        CrtShLookupQuery(
            query_value=normalized_domain,
            include_subdomains=include_subdomains,
            limit=limit,
        )
    )


def _normalize_rdap_query(kind: str, value: str) -> str:
    if kind == "domain":
        return _normalize_domain(value)
    if kind == "ip":
        try:
            return str(ipaddress.ip_address(value.strip()))
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=f"Invalid IP address: {value.strip()}") from exc
    normalized = value.strip().upper()
    if normalized.startswith("AS"):
        normalized = normalized[2:]
    if not normalized.isdigit():
        raise HTTPException(status_code=400, detail=f"Invalid autnum identifier: {value.strip()}")
    return f"AS{int(normalized)}"


def _normalize_domain(value: str) -> str:
    trimmed = value.strip().rstrip(".")
    if not _DOMAIN_PATTERN.fullmatch(trimmed):
        raise HTTPException(status_code=400, detail=f"Invalid domain query: {trimmed}")
    try:
        return trimmed.encode("idna").decode("ascii").lower()
    except UnicodeError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid domain query: {trimmed}") from exc
