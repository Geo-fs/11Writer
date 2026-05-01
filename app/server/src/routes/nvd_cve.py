from __future__ import annotations

import re

from fastapi import APIRouter, Depends, HTTPException, Query

from src.config.settings import Settings, get_settings
from src.services.cve_context_service import CveContextService
from src.services.nvd_cve_service import NvdCveQuery, NvdCveService
from src.types.api import CyberContextCompositionResponse, NvdCveResponse

router = APIRouter(prefix="/api/context/cyber", tags=["cyber-context"])

_CVE_PATTERN = re.compile(r"^CVE-\d{4}-\d{4,}$")


@router.get("/nvd-cve", response_model=NvdCveResponse)
async def nvd_cve_lookup(
    cve: str = Query(..., min_length=1, description="Single CVE identifier."),
    settings: Settings = Depends(get_settings),
) -> NvdCveResponse:
    normalized_cve = _normalize_cve(cve)
    return await NvdCveService(settings).lookup(NvdCveQuery(cve_id=normalized_cve))


@router.get("/cve-context", response_model=CyberContextCompositionResponse)
async def cve_context_summary(
    cve: str = Query(..., min_length=1, description="Single CVE identifier."),
    settings: Settings = Depends(get_settings),
) -> CyberContextCompositionResponse:
    normalized_cve = _normalize_cve(cve)
    return await CveContextService(settings).summarize(normalized_cve)


def _normalize_cve(value: str) -> str:
    normalized = value.strip().upper()
    if not _CVE_PATTERN.fullmatch(normalized):
        raise HTTPException(status_code=400, detail=f"Invalid CVE identifier: {normalized}")
    return normalized
