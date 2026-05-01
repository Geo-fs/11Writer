from datetime import datetime, timezone

from sqlmodel import Session, select

from app.connectors.base import ConnectorConfigError
from app.connectors.registry import registry
from app.models.connector import Connector
from app.schemas.connector import ConnectorCreate, ConnectorUpdate


def list_connectors_for_wave(session: Session, wave_id: int) -> list[Connector]:
    statement = (
        select(Connector)
        .where(Connector.wave_id == wave_id)
        .order_by(Connector.created_at.desc())
    )
    return list(session.exec(statement))


def create_connector(session: Session, wave_id: int, payload: ConnectorCreate) -> Connector:
    runner = registry.get(payload.type)
    if runner is None:
        raise ConnectorConfigError(f"Unknown connector type '{payload.type}'")

    normalized_config = runner.validate_config(payload.config_json)
    connector = Connector(
        wave_id=wave_id,
        type=payload.type,
        name=payload.name,
        enabled=payload.enabled,
        config_json=normalized_config,
        polling_interval_minutes=payload.polling_interval_minutes,
    )
    session.add(connector)
    session.commit()
    session.refresh(connector)
    return connector


def get_connector_or_none(session: Session, connector_id: int) -> Connector | None:
    return session.get(Connector, connector_id)


def update_connector(session: Session, connector: Connector, payload: ConnectorUpdate) -> Connector:
    target_type = payload.type or connector.type
    target_config = (
        payload.config_json if payload.config_json is not None else connector.config_json
    )

    runner = registry.get(target_type)
    if runner is None:
        raise ConnectorConfigError(f"Unknown connector type '{target_type}'")
    normalized_config = runner.validate_config(target_config)

    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(connector, key, value)
    connector.type = target_type
    connector.config_json = normalized_config
    connector.updated_at = datetime.now(timezone.utc)
    session.add(connector)
    session.commit()
    session.refresh(connector)
    return connector


def delete_connector(session: Session, connector: Connector) -> None:
    session.delete(connector)
    session.commit()
