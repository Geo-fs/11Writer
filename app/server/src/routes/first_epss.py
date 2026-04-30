from __future__ import annotations

import re

from fastapi import APIRouter, Depends, HTTPException, Query

from src.config.settings import Settings, get_settings
from src.services.first_epss_service import FirstEpssQuery, FirstEpssService
from src.types.api import FirstEpssResponse

router = APIRouter(prefix="/api/context/cyber", tags=["cyber-context"])

_CVE_PATTERN = re.compile(r"^CVE-\d{4}-\d{4,}$")


@router.get("/first-epss", response_model=FirstEpssResponse)
async def first_epss_lookup(
    cve: str = Query(..., min_length=1, description="Comma-separated list of CVE IDs."),
    date: str | None = Query(default=None, pattern=r"^\d{4}-\d{2}-\d{2}$"),
    settings: Settings = Depends(get_settings),
) -> FirstEpssResponse:
    parsed_cves = _parse_cve_query(cve)
    service = FirstEpssService(settings)
    return await service.lookup(FirstEpssQuery(cve_ids=parsed_cves, date=date))


def _parse_cve_query(raw_value: str) -> list[str]:
    values: list[str] = []
    seen: set[str] = set()
    for item in raw_value.split(","):
        normalized = item.strip().upper()
        if not normalized:
            continue
        if not _CVE_PATTERN.fullmatch(normalized):
            raise HTTPException(status_code=400, detail=f"Invalid CVE identifier: {normalized}")
        if normalized in seen:
            continue
        seen.add(normalized)
        values.append(normalized)
    if not values:
        raise HTTPException(status_code=400, detail="At least one CVE identifier is required.")
    if len(values) > 50:
        raise HTTPException(status_code=400, detail="At most 50 CVE identifiers are supported in one request.")
    return values
