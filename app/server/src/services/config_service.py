from src.config.settings import Settings
from src.services.camera_registry import build_camera_source_registry
from src.services.planet_imagery_service import build_planet_config
from src.types.api import FeatureFlags, PublicConfigResponse, TilesConfig


def build_public_config(settings: Settings) -> PublicConfigResponse:
    google_enabled = bool(settings.google_maps_api_key)
    camera_sources_enabled = any(source.enabled for source in build_camera_source_registry(settings))
    return PublicConfigResponse(
        app_name="WorldView Spatial Intelligence Simulator",
        environment=settings.app_env,
        tiles=TilesConfig(
            provider="google-photorealistic-3d" if google_enabled else "cesium-world-terrain",
            google_tiles_enabled=google_enabled,
            fallback_enabled=True,
            google_maps_api_key=settings.google_maps_api_key if google_enabled else None,
        ),
        features=FeatureFlags(
            aircraft=True,
            satellites=True,
            cameras=camera_sources_enabled,
            marine=True,
            visual_modes=True,
        ),
        planet=build_planet_config(),
    )
