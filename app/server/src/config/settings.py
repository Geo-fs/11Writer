from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_env: str = Field(default="development", alias="APP_ENV")
    app_cors_origins: str = Field(default="http://localhost:5173", alias="APP_CORS_ORIGINS")
    google_maps_api_key: str | None = Field(default=None, alias="GOOGLE_MAPS_API_KEY")
    cache_ttl_seconds: int = Field(default=60, alias="CACHE_TTL_SECONDS")
    opensky_base_url: str = Field(
        default="https://opensky-network.org/api",
        alias="OPENSKY_BASE_URL",
    )
    opensky_access_token: str | None = Field(default=None, alias="OPENSKY_ACCESS_TOKEN")
    celestrak_base_url: str = Field(
        default="https://celestrak.org/NORAD/elements",
        alias="CELESTRAK_BASE_URL",
    )
    webcam_cache_ttl_seconds: int = Field(default=60, alias="WEBCAM_CACHE_TTL_SECONDS")
    webcam_default_limit: int = Field(default=500, alias="WEBCAM_DEFAULT_LIMIT")
    wsdot_access_code: str | None = Field(default=None, alias="WSDOT_ACCESS_CODE")
    wsdot_base_url: str = Field(
        default="https://www.wsdot.wa.gov/Traffic/api/HighwayCameras/HighwayCamerasREST.svc",
        alias="WSDOT_BASE_URL",
    )
    ohgo_api_key: str | None = Field(default=None, alias="OHGO_API_KEY")
    ohgo_base_url: str = Field(default="https://publicapi.ohgo.com/api/v1", alias="OHGO_BASE_URL")
    wisconsin_511_api_key: str | None = Field(default=None, alias="WISCONSIN_511_API_KEY")
    wisconsin_511_base_url: str = Field(default="https://511wi.gov/api", alias="WISCONSIN_511_BASE_URL")
    georgia_511_api_key: str | None = Field(default=None, alias="GEORGIA_511_API_KEY")
    georgia_511_base_url: str = Field(default="https://511ga.org/api/v2", alias="GEORGIA_511_BASE_URL")
    newyork_511_api_key: str | None = Field(default=None, alias="NEWYORK_511_API_KEY")
    newyork_511_base_url: str = Field(default="https://511ny.org/api/v2", alias="NEWYORK_511_BASE_URL")
    idaho_511_api_key: str | None = Field(default=None, alias="IDAHO_511_API_KEY")
    idaho_511_base_url: str = Field(default="https://511.idaho.gov/api/v2", alias="IDAHO_511_BASE_URL")
    alaska_511_api_key: str | None = Field(default=None, alias="ALASKA_511_API_KEY")
    alaska_511_base_url: str = Field(default="https://511.alaska.gov/api/v2", alias="ALASKA_511_BASE_URL")
    usgs_ashcam_base_url: str = Field(
        default="https://volcview.wr.usgs.gov/ashcam-api/webcamApi",
        alias="USGS_ASHCAM_BASE_URL",
    )
    windy_webcams_api_key: str | None = Field(default=None, alias="WINDY_WEBCAMS_API_KEY")
    windy_webcams_base_url: str = Field(default="https://api.windy.com/api/webcams/v2", alias="WINDY_WEBCAMS_BASE_URL")
    reference_database_url: str = Field(default="sqlite:///./data/reference.db", alias="REFERENCE_DATABASE_URL")
    marine_database_url_override: str | None = Field(default=None, alias="MARINE_DATABASE_URL")
    marine_snapshot_interval_minutes: int = Field(default=5, alias="MARINE_SNAPSHOT_INTERVAL_MINUTES")
    marine_source_mode: str = Field(default="fixture", alias="MARINE_SOURCE_MODE")
    marine_ais_csv_path: str | None = Field(default=None, alias="MARINE_AIS_CSV_PATH")
    marine_http_source_url: str | None = Field(default=None, alias="MARINE_HTTP_SOURCE_URL")
    marine_http_source_token: str | None = Field(default=None, alias="MARINE_HTTP_SOURCE_TOKEN")
    marine_http_timeout_seconds: int = Field(default=20, alias="MARINE_HTTP_TIMEOUT_SECONDS")
    marine_fixture_scenario: str = Field(default="investigative-mix", alias="MARINE_FIXTURE_SCENARIO")
    marine_provider_fail_on_invalid: bool = Field(default=False, alias="MARINE_PROVIDER_FAIL_ON_INVALID")
    earthquake_source_mode: str = Field(default="fixture", alias="EARTHQUAKE_SOURCE_MODE")
    earthquake_fixture_path: str = Field(
        default="./data/usgs_earthquakes_fixture.geojson",
        alias="EARTHQUAKE_FIXTURE_PATH",
    )
    earthquake_usgs_feed_url: str = Field(
        default="https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson",
        alias="EARTHQUAKE_USGS_FEED_URL",
    )
    earthquake_http_timeout_seconds: int = Field(default=20, alias="EARTHQUAKE_HTTP_TIMEOUT_SECONDS")
    eonet_source_mode: str = Field(default="fixture", alias="EONET_SOURCE_MODE")
    eonet_fixture_path: str = Field(
        default="./data/nasa_eonet_events_fixture.json",
        alias="EONET_FIXTURE_PATH",
    )
    eonet_api_url: str = Field(
        default="https://eonet.gsfc.nasa.gov/api/v3/events",
        alias="EONET_API_URL",
    )
    eonet_http_timeout_seconds: int = Field(default=20, alias="EONET_HTTP_TIMEOUT_SECONDS")
    webcam_database_url: str | None = Field(default=None, alias="WEBCAM_DATABASE_URL")
    webcam_worker_enabled: bool = Field(default=False, alias="WEBCAM_WORKER_ENABLED")
    webcam_worker_poll_seconds: int = Field(default=15, alias="WEBCAM_WORKER_POLL_SECONDS")
    webcam_worker_run_on_startup: bool = Field(default=False, alias="WEBCAM_WORKER_RUN_ON_STARTUP")

    @property
    def cors_origins(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.app_cors_origins.split(",")
            if origin.strip()
        ]

    @property
    def camera_database_url(self) -> str:
        return self.webcam_database_url or self.reference_database_url

    @property
    def marine_database_url(self) -> str:
        return self.marine_database_url_override or self.reference_database_url


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
