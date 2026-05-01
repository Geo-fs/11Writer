import logging
from collections.abc import Callable

from sqlmodel import Session, select

from app.connectors.base import ConnectorRunner
from app.connectors.registry import registry
from app.models.connector import Connector
from app.models.record import Record
from app.models.wave import Wave

logger = logging.getLogger(__name__)


def run_wave_once(
    session: Session,
    wave: Wave,
    connector_lookup: Callable[[str], ConnectorRunner | None] = registry.get,
) -> list[Record]:
    persisted: list[Record] = []
    for connector in wave.connectors:
        if not connector.enabled:
            continue
        records = run_connector_once(
            session=session,
            wave=wave,
            connector=connector,
            connector_lookup=connector_lookup,
        )
        persisted.extend(records)
    return persisted


def run_connector_once(
    session: Session,
    wave: Wave,
    connector: Connector,
    connector_lookup: Callable[[str], ConnectorRunner | None] = registry.get,
) -> list[Record]:
    runner = connector_lookup(connector.type)
    if runner is None:
        logger.warning(
            "Unknown connector type '%s' for connector_id=%s",
            connector.type,
            connector.id,
        )
        return []

    collected = runner.collect(
        wave_name=wave.name,
        focus_type=wave.focus_type.value,
        config=connector.config_json,
    )
    persisted: list[Record] = []
    for item in collected:
        if item.external_id is not None:
            existing = session.exec(
                select(Record.id).where(
                    Record.connector_id == connector.id,
                    Record.external_id == item.external_id,
                )
            ).first()
            if existing is not None:
                continue

        record = Record(
            wave_id=wave.id,
            connector_id=connector.id,
            external_id=item.external_id,
            title=item.title,
            content=item.content,
            source_type=item.source_type,
            source_name=item.source_name,
            source_url=item.source_url,
            collected_at=item.collected_at,
            event_time=item.event_time,
            latitude=item.latitude,
            longitude=item.longitude,
            tags_json=item.tags_json,
            raw_payload_json=item.raw_payload_json,
        )
        session.add(record)
        persisted.append(record)
    session.commit()
    for record in persisted:
        session.refresh(record)
    logger.info(
        "Ingested %s records for wave_id=%s connector_id=%s",
        len(persisted),
        wave.id,
        connector.id,
    )
    return persisted
