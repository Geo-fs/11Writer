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
    opensky_source_mode: str = Field(default="fixture", alias="OPENSKY_SOURCE_MODE")
    opensky_states_url: str = Field(
        default="https://opensky-network.org/api/states/all",
        alias="OPENSKY_STATES_URL",
    )
    opensky_http_timeout_seconds: int = Field(
        default=15,
        alias="OPENSKY_HTTP_TIMEOUT_SECONDS",
    )
    opensky_fixture_path: str = Field(
        default="./data/opensky_states_fixture.json",
        alias="OPENSKY_FIXTURE_PATH",
    )
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
    finland_digitraffic_weathercam_mode: str = Field(
        default="fixture",
        alias="FINLAND_DIGITRAFFIC_WEATHERCAM_MODE",
    )
    finland_digitraffic_weathercam_fixture_path: str = Field(
        default="./app/server/data/finland_digitraffic_weathercam_fixture.json",
        alias="FINLAND_DIGITRAFFIC_WEATHERCAM_FIXTURE_PATH",
    )
    finland_digitraffic_weathercam_base_url: str = Field(
        default="https://tie.digitraffic.fi/api/weathercam/v1",
        alias="FINLAND_DIGITRAFFIC_WEATHERCAM_BASE_URL",
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
    marine_noaa_coops_mode: str = Field(default="fixture", alias="MARINE_NOAA_COOPS_MODE")
    marine_ndbc_mode: str = Field(default="fixture", alias="MARINE_NDBC_MODE")
    marine_ndbc_latest_url: str | None = Field(default=None, alias="MARINE_NDBC_LATEST_URL")
    scottish_water_overflows_mode: str = Field(
        default="fixture",
        alias="SCOTTISH_WATER_OVERFLOWS_MODE",
    )
    scottish_water_overflows_fixture_path: str = Field(
        default="./data/scottish_water_overflows_fixture.json",
        alias="SCOTTISH_WATER_OVERFLOWS_FIXTURE_PATH",
    )
    scottish_water_overflows_api_url: str = Field(
        default="https://api.scottishwater.co.uk/overflow-event-monitoring/v1/near-real-time",
        alias="SCOTTISH_WATER_OVERFLOWS_API_URL",
    )
    scottish_water_overflows_http_timeout_seconds: int = Field(
        default=20,
        alias="SCOTTISH_WATER_OVERFLOWS_HTTP_TIMEOUT_SECONDS",
    )
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
    aviation_weather_base_url: str = Field(
        default="https://aviationweather.gov/api/data",
        alias="AVIATION_WEATHER_BASE_URL",
    )
    aviation_weather_http_timeout_seconds: int = Field(
        default=20,
        alias="AVIATION_WEATHER_HTTP_TIMEOUT_SECONDS",
    )
    faa_nas_status_mode: str = Field(default="fixture", alias="FAA_NAS_STATUS_MODE")
    faa_nas_status_url: str = Field(
        default="https://nasstatus.faa.gov/api/airport-status-information",
        alias="FAA_NAS_STATUS_URL",
    )
    faa_nas_http_timeout_seconds: int = Field(
        default=20,
        alias="FAA_NAS_HTTP_TIMEOUT_SECONDS",
    )
    faa_nas_fixture_path: str = Field(
        default="./data/faa_nas_airport_status_fixture.xml",
        alias="FAA_NAS_FIXTURE_PATH",
    )
    cneos_source_mode: str = Field(default="fixture", alias="CNEOS_SOURCE_MODE")
    cneos_close_approach_url: str = Field(
        default="https://ssd-api.jpl.nasa.gov/cad.api",
        alias="CNEOS_CLOSE_APPROACH_URL",
    )
    cneos_fireball_url: str = Field(
        default="https://ssd-api.jpl.nasa.gov/fireball.api",
        alias="CNEOS_FIREBALL_URL",
    )
    cneos_http_timeout_seconds: int = Field(
        default=20,
        alias="CNEOS_HTTP_TIMEOUT_SECONDS",
    )
    cneos_fixture_path: str = Field(
        default="./data/cneos_space_context_fixture.json",
        alias="CNEOS_FIXTURE_PATH",
    )
    swpc_source_mode: str = Field(default="fixture", alias="SWPC_SOURCE_MODE")
    swpc_summary_url: str = Field(
        default="https://services.swpc.noaa.gov/products/noaa-scales.json",
        alias="SWPC_SUMMARY_URL",
    )
    swpc_alerts_url: str = Field(
        default="https://services.swpc.noaa.gov/products/alerts.json",
        alias="SWPC_ALERTS_URL",
    )
    swpc_http_timeout_seconds: int = Field(
        default=20,
        alias="SWPC_HTTP_TIMEOUT_SECONDS",
    )
    swpc_fixture_path: str = Field(
        default="./data/swpc_space_weather_fixture.json",
        alias="SWPC_FIXTURE_PATH",
    )
    volcano_source_mode: str = Field(default="fixture", alias="VOLCANO_SOURCE_MODE")
    volcano_fixture_path: str = Field(
        default="./data/usgs_volcano_status_fixture.json",
        alias="VOLCANO_FIXTURE_PATH",
    )
    volcano_elevated_api_url: str = Field(
        default="https://volcanoes.usgs.gov/hans-public/api/volcano/getElevatedVolcanoes",
        alias="VOLCANO_ELEVATED_API_URL",
    )
    volcano_monitored_api_url: str = Field(
        default="https://volcanoes.usgs.gov/hans-public/api/volcano/getMonitoredVolcanoes",
        alias="VOLCANO_MONITORED_API_URL",
    )
    volcano_catalog_api_url: str = Field(
        default="https://volcanoes.usgs.gov/hans-public/api/volcano/getUSVolcanoes",
        alias="VOLCANO_CATALOG_API_URL",
    )
    volcano_http_timeout_seconds: int = Field(default=20, alias="VOLCANO_HTTP_TIMEOUT_SECONDS")
    tsunami_source_mode: str = Field(default="fixture", alias="TSUNAMI_SOURCE_MODE")
    tsunami_fixture_path: str = Field(
        default="./data/noaa_tsunami_alerts_fixture.json",
        alias="TSUNAMI_FIXTURE_PATH",
    )
    tsunami_ntwc_feed_url: str = Field(
        default="https://www.tsunami.gov/events/xml/PAAQAtom.xml",
        alias="TSUNAMI_NTWC_FEED_URL",
    )
    tsunami_ptwc_feed_url: str = Field(
        default="https://www.tsunami.gov/events/xml/PHEBAtom.xml",
        alias="TSUNAMI_PTWC_FEED_URL",
    )
    tsunami_http_timeout_seconds: int = Field(default=20, alias="TSUNAMI_HTTP_TIMEOUT_SECONDS")
    uk_ea_flood_source_mode: str = Field(default="fixture", alias="UK_EA_FLOOD_SOURCE_MODE")
    uk_ea_flood_fixture_path: str = Field(
        default="./data/uk_ea_flood_monitoring_fixture.json",
        alias="UK_EA_FLOOD_FIXTURE_PATH",
    )
    uk_ea_flood_warnings_url: str = Field(
        default="https://environment.data.gov.uk/flood-monitoring/id/floods",
        alias="UK_EA_FLOOD_WARNINGS_URL",
    )
    uk_ea_flood_stations_url: str = Field(
        default="https://environment.data.gov.uk/flood-monitoring/id/stations",
        alias="UK_EA_FLOOD_STATIONS_URL",
    )
    uk_ea_flood_readings_url: str = Field(
        default="https://environment.data.gov.uk/flood-monitoring/data/readings",
        alias="UK_EA_FLOOD_READINGS_URL",
    )
    uk_ea_flood_http_timeout_seconds: int = Field(default=20, alias="UK_EA_FLOOD_HTTP_TIMEOUT_SECONDS")
    geonet_source_mode: str = Field(default="fixture", alias="GEONET_SOURCE_MODE")
    geonet_fixture_path: str = Field(
        default="./data/geonet_hazards_fixture.json",
        alias="GEONET_FIXTURE_PATH",
    )
    geonet_quakes_url: str = Field(
        default="https://api.geonet.org.nz/quake?MMI=-1",
        alias="GEONET_QUAKES_URL",
    )
    geonet_volcano_alerts_url: str = Field(
        default="https://api.geonet.org.nz/volcano/val",
        alias="GEONET_VOLCANO_ALERTS_URL",
    )
    geonet_http_timeout_seconds: int = Field(default=20, alias="GEONET_HTTP_TIMEOUT_SECONDS")
    hko_source_mode: str = Field(default="fixture", alias="HKO_SOURCE_MODE")
    hko_fixture_path: str = Field(
        default="./data/hko_weather_fixture.json",
        alias="HKO_FIXTURE_PATH",
    )
    hko_warnings_url: str = Field(
        default="https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=warningInfo&lang=en",
        alias="HKO_WARNINGS_URL",
    )
    hko_tropical_cyclone_url: str = Field(
        default="https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=flw&lang=en",
        alias="HKO_TROPICAL_CYCLONE_URL",
    )
    hko_http_timeout_seconds: int = Field(default=20, alias="HKO_HTTP_TIMEOUT_SECONDS")
    metno_metalerts_source_mode: str = Field(default="fixture", alias="METNO_METALERTS_SOURCE_MODE")
    metno_metalerts_fixture_path: str = Field(
        default="./data/metno_metalerts_fixture.json",
        alias="METNO_METALERTS_FIXTURE_PATH",
    )
    metno_metalerts_cap_url: str = Field(
        default="https://api.met.no/weatherapi/metalerts/2.0/current.json",
        alias="METNO_METALERTS_CAP_URL",
    )
    metno_http_timeout_seconds: int = Field(default=20, alias="METNO_HTTP_TIMEOUT_SECONDS")
    metno_contact_user_agent: str = Field(
        default="11Writer/phase2 (contact: local-dev)",
        alias="METNO_CONTACT_USER_AGENT",
    )
    canada_cap_source_mode: str = Field(default="fixture", alias="CANADA_CAP_SOURCE_MODE")
    canada_cap_fixture_path: str = Field(
        default="./data/canada_cap_index_fixture.html",
        alias="CANADA_CAP_FIXTURE_PATH",
    )
    canada_cap_feed_url: str = Field(
        default="https://dd.weather.gc.ca/today/alerts/cap/",
        alias="CANADA_CAP_FEED_URL",
    )
    canada_cap_http_timeout_seconds: int = Field(default=20, alias="CANADA_CAP_HTTP_TIMEOUT_SECONDS")
    rss_feed_source_mode: str = Field(default="fixture", alias="RSS_FEED_SOURCE_MODE")
    rss_feed_fixture_path: str = Field(
        default="./data/rss_google_alerts_fixture.xml",
        alias="RSS_FEED_FIXTURE_PATH",
    )
    rss_feed_url: str = Field(
        default="https://example.invalid/private-rss-or-atom-feed-url",
        alias="RSS_FEED_URL",
    )
    rss_feed_name: str = Field(
        default="local-discovery-feed",
        alias="RSS_FEED_NAME",
    )
    rss_feed_http_timeout_seconds: int = Field(default=20, alias="RSS_FEED_HTTP_TIMEOUT_SECONDS")
    rss_feed_stale_after_seconds: int = Field(default=172800, alias="RSS_FEED_STALE_AFTER_SECONDS")
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
