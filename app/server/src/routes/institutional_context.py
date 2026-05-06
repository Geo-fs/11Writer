from __future__ import annotations

import re

from fastapi import APIRouter, Depends, HTTPException, Query

from src.config.settings import Settings, get_settings
from src.services.sec_edgar_service import SecEdgarQuery, SecEdgarService
from src.services.usaspending_service import UsaSpendingQuery, UsaSpendingService
from src.types.api import SecEdgarResponse, UsaSpendingResponse

router = APIRouter(prefix="/api/context/institutional", tags=["institutional-context"])

_CIK_PATTERN = re.compile(r"^\d{1,10}$")
_RECIPIENT_HASH_PATTERN = re.compile(r"^[A-Za-z0-9_-]{6,128}$")


@router.get("/sec-edgar/company", response_model=SecEdgarResponse)
async def sec_edgar_company(
    cik: str = Query(..., min_length=1, max_length=32, description="Issuer CIK, with or without leading zeros."),
    filing_limit: int = Query(default=10, ge=1, le=50),
    settings: Settings = Depends(get_settings),
) -> SecEdgarResponse:
    normalized_cik = _normalize_cik(cik)
    return await SecEdgarService(settings).lookup(SecEdgarQuery(cik=normalized_cik, filing_limit=filing_limit))


@router.get("/usaspending/recipient", response_model=UsaSpendingResponse)
async def usaspending_recipient(
    recipient_hash: str = Query(..., min_length=6, max_length=128, description="USAspending recipient hash identifier."),
    settings: Settings = Depends(get_settings),
) -> UsaSpendingResponse:
    normalized_hash = _normalize_recipient_hash(recipient_hash)
    return await UsaSpendingService(settings).lookup(UsaSpendingQuery(recipient_hash=normalized_hash))


def _normalize_cik(value: str) -> str:
    trimmed = value.strip()
    if not _CIK_PATTERN.fullmatch(trimmed):
        raise HTTPException(status_code=400, detail=f"Invalid CIK: {trimmed}")
    return trimmed.zfill(10)


def _normalize_recipient_hash(value: str) -> str:
    trimmed = value.strip()
    if not _RECIPIENT_HASH_PATTERN.fullmatch(trimmed):
        raise HTTPException(status_code=400, detail=f"Invalid recipient hash: {trimmed}")
    return trimmed
