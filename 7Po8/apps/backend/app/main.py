from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.connectors import root_router as connector_root_router
from app.api.connectors import router as connector_router
from app.api.deps import db
from app.api.discovery import root_router as discovery_root_router
from app.api.discovery import wave_router as discovery_wave_router
from app.api.domain_trust import router as domain_trust_router
from app.api.health import router as health_router
from app.api.policy_actions import source_router as source_policy_action_router
from app.api.policy_actions import wave_router as wave_policy_action_router
from app.api.records import router as record_router
from app.api.runs import connector_router as connector_run_router
from app.api.runs import wave_router as wave_run_router
from app.api.scheduler import router as scheduler_router
from app.api.signals import connector_router as connector_signal_router
from app.api.signals import root_router as signal_root_router
from app.api.signals import wave_router as wave_signal_router
from app.api.wave_trust_overrides import root_router as wave_trust_override_root_router
from app.api.wave_trust_overrides import wave_router as wave_trust_override_wave_router
from app.api.waves import router as wave_router
from app.core.settings import settings
from app.db.init_db import init_db


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    init_db(db)
    yield


def create_app() -> FastAPI:
    settings.ensure_data_dir()
    app = FastAPI(title=settings.app_name, version=settings.app_version, lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health_router)
    app.include_router(wave_router, prefix=settings.api_prefix)
    app.include_router(connector_router, prefix=settings.api_prefix)
    app.include_router(connector_root_router, prefix=settings.api_prefix)
    app.include_router(record_router, prefix=settings.api_prefix)
    app.include_router(wave_run_router, prefix=settings.api_prefix)
    app.include_router(connector_run_router, prefix=settings.api_prefix)
    app.include_router(scheduler_router, prefix=settings.api_prefix)
    app.include_router(wave_signal_router, prefix=settings.api_prefix)
    app.include_router(connector_signal_router, prefix=settings.api_prefix)
    app.include_router(signal_root_router, prefix=settings.api_prefix)
    app.include_router(discovery_wave_router, prefix=settings.api_prefix)
    app.include_router(discovery_root_router, prefix=settings.api_prefix)
    app.include_router(domain_trust_router, prefix=settings.api_prefix)
    app.include_router(wave_trust_override_wave_router, prefix=settings.api_prefix)
    app.include_router(wave_trust_override_root_router, prefix=settings.api_prefix)
    app.include_router(wave_policy_action_router, prefix=settings.api_prefix)
    app.include_router(source_policy_action_router, prefix=settings.api_prefix)

    return app


app = create_app()
