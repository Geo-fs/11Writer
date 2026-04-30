import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config.settings import get_settings
from src.routes.aircraft import router as aircraft_router
from src.routes.aviation_weather import router as aviation_weather_router
from src.routes.cameras import router as cameras_router
from src.routes.cneos import router as cneos_router
from src.routes.config import router as config_router
from src.routes.events import router as events_router
from src.routes.faa_nas_status import router as faa_nas_status_router
from src.routes.feeds import router as feeds_router
from src.routes.health import router as health_router
from src.routes.marine import router as marine_router
from src.routes.opensky_states import router as opensky_states_router
from src.routes.reference import router as reference_router
from src.routes.satellite import router as satellite_router
from src.routes.status import router as status_router
from src.routes.swpc import router as swpc_router
from src.webcam.refresh import WebcamRefreshService, WebcamWorker


@asynccontextmanager
async def _lifespan(_: FastAPI):
    settings = get_settings()
    stop_event: asyncio.Event | None = None
    worker_task: asyncio.Task[None] | None = None
    if settings.webcam_worker_enabled and settings.webcam_worker_run_on_startup:
        stop_event = asyncio.Event()
        worker = WebcamWorker(
            WebcamRefreshService(settings),
            poll_seconds=settings.webcam_worker_poll_seconds,
        )
        worker_task = asyncio.create_task(worker.run_loop(stop_event=stop_event))
    try:
        yield
    finally:
        if stop_event is not None:
            stop_event.set()
        if worker_task is not None:
            await worker_task


def create_application() -> FastAPI:
    settings = get_settings()
    application = FastAPI(
        title="WorldView Spatial Intelligence Simulator API",
        version="0.1.0",
        lifespan=_lifespan,
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.include_router(health_router)
    application.include_router(config_router)
    application.include_router(events_router)
    application.include_router(feeds_router)
    application.include_router(status_router)
    application.include_router(reference_router)
    application.include_router(aircraft_router)
    application.include_router(opensky_states_router)
    application.include_router(aviation_weather_router)
    application.include_router(faa_nas_status_router)
    application.include_router(cneos_router)
    application.include_router(swpc_router)
    application.include_router(satellite_router)
    application.include_router(marine_router)
    application.include_router(cameras_router)

    return application
