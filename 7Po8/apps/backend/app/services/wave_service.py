from datetime import datetime, timezone

from sqlalchemy import func
from sqlmodel import Session, select

from app.models.connector import Connector
from app.models.record import Record
from app.models.wave import Wave
from app.schemas.wave import WaveCreate, WaveUpdate


def list_waves_with_counts(session: Session) -> list[tuple[Wave, int, int]]:
    connector_count = func.count(func.distinct(Connector.id)).label("connector_count")
    record_count = func.count(func.distinct(Record.id)).label("record_count")

    statement = (
        select(Wave, connector_count, record_count)
        .outerjoin(Connector, Connector.wave_id == Wave.id)
        .outerjoin(Record, Record.wave_id == Wave.id)
        .group_by(Wave.id)
        .order_by(Wave.created_at.desc())
    )
    rows = session.exec(statement).all()
    return [(wave, int(c_count), int(r_count)) for wave, c_count, r_count in rows]


def create_wave(session: Session, payload: WaveCreate) -> Wave:
    wave = Wave(**payload.model_dump())
    session.add(wave)
    session.commit()
    session.refresh(wave)
    return wave


def get_wave_or_none(session: Session, wave_id: int) -> Wave | None:
    return session.get(Wave, wave_id)


def get_wave_with_counts_or_none(session: Session, wave_id: int) -> tuple[Wave, int, int] | None:
    connector_count = func.count(func.distinct(Connector.id)).label("connector_count")
    record_count = func.count(func.distinct(Record.id)).label("record_count")

    statement = (
        select(Wave, connector_count, record_count)
        .outerjoin(Connector, Connector.wave_id == Wave.id)
        .outerjoin(Record, Record.wave_id == Wave.id)
        .where(Wave.id == wave_id)
        .group_by(Wave.id)
    )
    row = session.exec(statement).first()
    if row is None:
        return None
    wave, c_count, r_count = row
    return wave, int(c_count), int(r_count)


def update_wave(session: Session, wave: Wave, payload: WaveUpdate) -> Wave:
    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(wave, key, value)
    wave.updated_at = datetime.now(timezone.utc)
    session.add(wave)
    session.commit()
    session.refresh(wave)
    return wave


def delete_wave(session: Session, wave: Wave) -> None:
    session.delete(wave)
    session.commit()
