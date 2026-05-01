from datetime import datetime, timezone
from typing import Literal

from sqlalchemy import or_
from sqlmodel import Session, select

from app.models.record import Record


def _normalize_datetime(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    if value.tzinfo is None:
        return value
    return value.astimezone(timezone.utc).replace(tzinfo=None)


def list_records_for_wave(
    session: Session,
    wave_id: int,
    *,
    text_search: str | None = None,
    connector_id: int | None = None,
    source_type: str | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    has_coordinates: bool | None = None,
    sort: Literal["newest", "oldest"] = "newest",
) -> list[Record]:
    statement = select(Record).where(Record.wave_id == wave_id)
    if text_search:
        pattern = f"%{text_search.strip()}%"
        statement = statement.where(
            or_(
                Record.title.ilike(pattern),
                Record.content.ilike(pattern),
                Record.source_name.ilike(pattern),
            )
        )
    if connector_id is not None:
        statement = statement.where(Record.connector_id == connector_id)
    if source_type:
        statement = statement.where(Record.source_type == source_type)
    normalized_start = _normalize_datetime(start_date)
    if normalized_start is not None:
        statement = statement.where(Record.collected_at >= normalized_start)
    normalized_end = _normalize_datetime(end_date)
    if normalized_end is not None:
        statement = statement.where(Record.collected_at <= normalized_end)
    if has_coordinates is True:
        statement = statement.where(Record.latitude.is_not(None), Record.longitude.is_not(None))
    elif has_coordinates is False:
        statement = statement.where(or_(Record.latitude.is_(None), Record.longitude.is_(None)))

    if sort == "oldest":
        statement = statement.order_by(Record.collected_at.asc())
    else:
        statement = statement.order_by(Record.collected_at.desc())
    return list(session.exec(statement))
