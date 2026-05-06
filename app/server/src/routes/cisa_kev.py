from __future__ import annotations

import re

from fastapi import APIRouter, Depends, HTTPException, Query

from src.config.settings import Settings, get_settings
from src.services.cisa_kev_service import CisaKevQuery, CisaKevService
from src.types.api import CisaKevResponse

router = APIRouter(prefix="/api/context/cyber", tags=["cyber-context"])

_CVE_PATTERN = re.compile(r"^CVE-\d{4}-\d{4,}$")


@router.get("/cisa-kev", response_model=CisaKevResponse)
async def cisa_kev_lookup(
    cve: str | None = Query(default=None, description="Optional single CVE identifier."),
    limit: int = Query(default=25, ge=1, le=100),
    settings: Settings = Depends(get_settings),
) -> CisaKevResponse:
    normalized_cve = _normalize_cve(cve) if cve is not None else None
    return await CisaKevService(settings).lookup(CisaKevQuery(cve_id=normalized_cve, limit=limit))


def _normalize_cve(value: str) -> str:
    normalized = value.strip().upper()
    if not _CVE_PATTERN.fullmatch(normalized):
        raise HTTPException(status_code=400, detail=f"Invalid CVE identifier: {normalized}")
    return normalized
