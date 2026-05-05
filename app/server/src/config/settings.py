from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_env: str = Field(default="development", alias="APP_ENV")
    app_runtime_mode: str = Field(default="desktop-sidecar", alias="APP_RUNTIME_MODE")
    app_resource_dir: str | None = Field(default=None, alias="APP_RESOURCE_DIR")
    app_user_data_dir: str | None = Field(default=None, alias="APP_USER_DATA_DIR")
    app_log_dir: str | None = Field(default=None, alias="APP_LOG_DIR")
    app_cache_dir: str | None = Field(default=None, alias="APP_CACHE_DIR")
    app_runtime_service_dir: str | None = Field(default=None, alias="APP_RUNTIME_SERVICE_DIR")
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
    nsw_live_traffic_cameras_mode: str = Field(
        default="fixture",
        alias="NSW_LIVE_TRAFFIC_CAMERAS_MODE",
    )
    nsw_live_traffic_cameras_fixture_path: str = Field(
        default="./app/server/data/nsw_live_traffic_cameras_fixture.json",
        alias="NSW_LIVE_TRAFFIC_CAMERAS_FIXTURE_PATH",
    )
    quebec_mtmd_traffic_cameras_mode: str = Field(
        default="fixture",
        alias="QUEBEC_MTMD_TRAFFIC_CAMERAS_MODE",
    )
    quebec_mtmd_traffic_cameras_fixture_path: str = Field(
        default="./app/server/data/quebec_mtmd_traffic_cameras_fixture.json",
        alias="QUEBEC_MTMD_TRAFFIC_CAMERAS_FIXTURE_PATH",
    )
    maryland_chart_traffic_cameras_mode: str = Field(
        default="fixture",
        alias="MARYLAND_CHART_TRAFFIC_CAMERAS_MODE",
    )
    maryland_chart_traffic_cameras_fixture_path: str = Field(
        default="./app/server/data/maryland_chart_traffic_cameras_fixture.json",
        alias="MARYLAND_CHART_TRAFFIC_CAMERAS_FIXTURE_PATH",
    )
    fingal_traffic_cameras_mode: str = Field(
        default="fixture",
        alias="FINGAL_TRAFFIC_CAMERAS_MODE",
    )
    fingal_traffic_cameras_fixture_path: str = Field(
        default="./app/server/data/fingal_traffic_cameras_fixture.json",
        alias="FINGAL_TRAFFIC_CAMERAS_FIXTURE_PATH",
    )
    baton_rouge_traffic_cameras_mode: str = Field(
        default="fixture",
        alias="BATON_ROUGE_TRAFFIC_CAMERAS_MODE",
    )
    baton_rouge_traffic_cameras_fixture_path: str = Field(
        default="./app/server/data/baton_rouge_traffic_cameras_fixture.json",
        alias="BATON_ROUGE_TRAFFIC_CAMERAS_FIXTURE_PATH",
    )
    vancouver_web_cam_url_links_mode: str = Field(
        default="fixture",
        alias="VANCOUVER_WEB_CAM_URL_LINKS_MODE",
    )
    vancouver_web_cam_url_links_fixture_path: str = Field(
        default="./app/server/data/vancouver_web_cam_url_links_fixture.json",
        alias="VANCOUVER_WEB_CAM_URL_LINKS_FIXTURE_PATH",
    )
    caltrans_cctv_cameras_mode: str = Field(
        default="fixture",
        alias="CALTRANS_CCTV_CAMERAS_MODE",
    )
    caltrans_cctv_cameras_fixture_path: str = Field(
        default="./app/server/data/caltrans_cctv_cameras_fixture.json",
        alias="CALTRANS_CCTV_CAMERAS_FIXTURE_PATH",
    )
    finland_digitraffic_source_mode: str = Field(
        default="fixture",
        alias="FINLAND_DIGITRAFFIC_SOURCE_MODE",
    )
    finland_digitraffic_weather_stations_fixture_path: str = Field(
        default="./app/server/data/digitraffic_weather_stations_fixture.json",
        alias="FINLAND_DIGITRAFFIC_WEATHER_STATIONS_FIXTURE_PATH",
    )
    finland_digitraffic_weather_station_data_fixture_path: str = Field(
        default="./app/server/data/digitraffic_weather_station_data_fixture.json",
        alias="FINLAND_DIGITRAFFIC_WEATHER_STATION_DATA_FIXTURE_PATH",
    )
    finland_digitraffic_weather_stations_url: str = Field(
        default="https://tie.digitraffic.fi/api/weather/v1/stations",
        alias="FINLAND_DIGITRAFFIC_WEATHER_STATIONS_URL",
    )
    finland_digitraffic_weather_station_data_url: str = Field(
        default="https://tie.digitraffic.fi/api/weather/v1/stations/data",
        alias="FINLAND_DIGITRAFFIC_WEATHER_STATION_DATA_URL",
    )
    finland_digitraffic_http_timeout_seconds: int = Field(
        default=20,
        alias="FINLAND_DIGITRAFFIC_HTTP_TIMEOUT_SECONDS",
    )
    windy_webcams_api_key: str | None = Field(default=None, alias="WINDY_WEBCAMS_API_KEY")
    windy_webcams_base_url: str = Field(default="https://api.windy.com/api/webcams/v2", alias="WINDY_WEBCAMS_BASE_URL")
    reference_database_url: str = Field(default="sqlite:///./data/reference.db", alias="REFERENCE_DATABASE_URL")
    ourairports_reference_source_mode: str = Field(
        default="fixture",
        alias="OURAIRPORTS_REFERENCE_SOURCE_MODE",
    )
    ourairports_reference_fixture_path: str = Field(
        default="./data/ourairports_reference_fixture",
        alias="OURAIRPORTS_REFERENCE_FIXTURE_PATH",
    )
    ourairports_reference_airports_url: str = Field(
        default="https://davidmegginson.github.io/ourairports-data/airports.csv",
        alias="OURAIRPORTS_REFERENCE_AIRPORTS_URL",
    )
    ourairports_reference_runways_url: str = Field(
        default="https://davidmegginson.github.io/ourairports-data/runways.csv",
        alias="OURAIRPORTS_REFERENCE_RUNWAYS_URL",
    )
    ourairports_reference_http_timeout_seconds: int = Field(
        default=20,
        alias="OURAIRPORTS_REFERENCE_HTTP_TIMEOUT_SECONDS",
    )
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
    vigicrues_hydrometry_mode: str = Field(default="fixture", alias="VIGICRUES_HYDROMETRY_MODE")
    vigicrues_hydrometry_fixture_path: str = Field(
        default="./data/vigicrues_hydrometry_fixture.json",
        alias="VIGICRUES_HYDROMETRY_FIXTURE_PATH",
    )
    vigicrues_hydrometry_stations_url: str = Field(
        default="https://hubeau.eaufrance.fr/api/v2/hydrometrie/referentiel/stations",
        alias="VIGICRUES_HYDROMETRY_STATIONS_URL",
    )
    vigicrues_hydrometry_sites_url: str = Field(
        default="https://hubeau.eaufrance.fr/api/v2/hydrometrie/referentiel/sites",
        alias="VIGICRUES_HYDROMETRY_SITES_URL",
    )
    vigicrues_hydrometry_observations_tr_url: str = Field(
        default="https://hubeau.eaufrance.fr/api/v2/hydrometrie/observations_tr",
        alias="VIGICRUES_HYDROMETRY_OBSERVATIONS_TR_URL",
    )
    vigicrues_hydrometry_http_timeout_seconds: int = Field(
        default=20,
        alias="VIGICRUES_HYDROMETRY_HTTP_TIMEOUT_SECONDS",
    )
    ireland_opw_waterlevel_mode: str = Field(default="fixture", alias="IRELAND_OPW_WATERLEVEL_MODE")
    ireland_opw_waterlevel_fixture_path: str = Field(
        default="./data/ireland_opw_waterlevel_fixture.json",
        alias="IRELAND_OPW_WATERLEVEL_FIXTURE_PATH",
    )
    ireland_opw_waterlevel_latest_url: str = Field(
        default="https://waterlevel.ie/geojson/latest/",
        alias="IRELAND_OPW_WATERLEVEL_LATEST_URL",
    )
    ireland_opw_waterlevel_geojson_url: str = Field(
        default="https://waterlevel.ie/geojson/",
        alias="IRELAND_OPW_WATERLEVEL_GEOJSON_URL",
    )
    ireland_opw_waterlevel_http_timeout_seconds: int = Field(
        default=20,
        alias="IRELAND_OPW_WATERLEVEL_HTTP_TIMEOUT_SECONDS",
    )
    netherlands_rws_waterinfo_mode: str = Field(
        default="fixture",
        alias="NETHERLANDS_RWS_WATERINFO_MODE",
    )
    netherlands_rws_waterinfo_fixture_path: str = Field(
        default="./data/netherlands_rws_waterinfo_fixture.json",
        alias="NETHERLANDS_RWS_WATERINFO_FIXTURE_PATH",
    )
    netherlands_rws_waterinfo_catalog_url: str = Field(
        default=(
            "https://waterwebservices.apps.rijkswaterstaat.nl/ddapi20-waterwebservices/api/"
            "METADATASERVICES_DBO/OphalenCatalogus"
        ),
        alias="NETHERLANDS_RWS_WATERINFO_CATALOG_URL",
    )
    netherlands_rws_waterinfo_latest_observations_url: str = Field(
        default=(
            "https://waterwebservices.apps.rijkswaterstaat.nl/ddapi20-waterwebservices/api/"
            "ONLINEWAARNEMINGENSERVICES_DBO/OphalenLaatsteWaarnemingen"
        ),
        alias="NETHERLANDS_RWS_WATERINFO_LATEST_OBSERVATIONS_URL",
    )
    netherlands_rws_waterinfo_http_timeout_seconds: int = Field(
        default=20,
        alias="NETHERLANDS_RWS_WATERINFO_HTTP_TIMEOUT_SECONDS",
    )
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
    ncei_space_weather_portal_source_mode: str = Field(
        default="fixture",
        alias="NCEI_SPACE_WEATHER_PORTAL_SOURCE_MODE",
    )
    ncei_space_weather_portal_metadata_url: str = Field(
        default="https://www.ncei.noaa.gov/access/metadata/landing-page/bin/iso?id=gov.noaa.ngdc.stp.swx:space_weather_products;view=xml;responseType=text/xml",
        alias="NCEI_SPACE_WEATHER_PORTAL_METADATA_URL",
    )
    ncei_space_weather_portal_http_timeout_seconds: int = Field(
        default=20,
        alias="NCEI_SPACE_WEATHER_PORTAL_HTTP_TIMEOUT_SECONDS",
    )
    ncei_space_weather_portal_fixture_path: str = Field(
        default="./data/ncei_space_weather_portal_fixture.xml",
        alias="NCEI_SPACE_WEATHER_PORTAL_FIXTURE_PATH",
    )
    washington_vaac_source_mode: str = Field(
        default="fixture",
        alias="WASHINGTON_VAAC_SOURCE_MODE",
    )
    washington_vaac_advisories_url: str = Field(
        default="https://www.ospo.noaa.gov/products/atmosphere/vaac/messages.html",
        alias="WASHINGTON_VAAC_ADVISORIES_URL",
    )
    washington_vaac_http_timeout_seconds: int = Field(
        default=20,
        alias="WASHINGTON_VAAC_HTTP_TIMEOUT_SECONDS",
    )
    washington_vaac_fixture_path: str = Field(
        default="./data/washington_vaac_advisories_fixture.json",
        alias="WASHINGTON_VAAC_FIXTURE_PATH",
    )
    anchorage_vaac_source_mode: str = Field(
        default="fixture",
        alias="ANCHORAGE_VAAC_SOURCE_MODE",
    )
    anchorage_vaac_advisories_url: str = Field(
        default="https://www.weather.gov/vaac/",
        alias="ANCHORAGE_VAAC_ADVISORIES_URL",
    )
    anchorage_vaac_http_timeout_seconds: int = Field(
        default=20,
        alias="ANCHORAGE_VAAC_HTTP_TIMEOUT_SECONDS",
    )
    anchorage_vaac_fixture_path: str = Field(
        default="./data/anchorage_vaac_advisories_fixture.json",
        alias="ANCHORAGE_VAAC_FIXTURE_PATH",
    )
    tokyo_vaac_source_mode: str = Field(
        default="fixture",
        alias="TOKYO_VAAC_SOURCE_MODE",
    )
    tokyo_vaac_advisories_url: str = Field(
        default="https://www.data.jma.go.jp/vaac/data/vaac_list.html",
        alias="TOKYO_VAAC_ADVISORIES_URL",
    )
    tokyo_vaac_http_timeout_seconds: int = Field(
        default=20,
        alias="TOKYO_VAAC_HTTP_TIMEOUT_SECONDS",
    )
    tokyo_vaac_fixture_path: str = Field(
        default="./data/tokyo_vaac_advisories_fixture.json",
        alias="TOKYO_VAAC_FIXTURE_PATH",
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
    emsc_seismicportal_source_mode: str = Field(
        default="fixture",
        alias="EMSC_SEISMICPORTAL_SOURCE_MODE",
    )
    emsc_seismicportal_fixture_path: str = Field(
        default="./data/emsc_seismicportal_realtime_fixture.json",
        alias="EMSC_SEISMICPORTAL_FIXTURE_PATH",
    )
    emsc_seismicportal_stream_url: str = Field(
        default="wss://www.seismicportal.eu/standing_order/websocket",
        alias="EMSC_SEISMICPORTAL_STREAM_URL",
    )
    emsc_seismicportal_documentation_url: str = Field(
        default="https://www.seismicportal.eu/realtime.html",
        alias="EMSC_SEISMICPORTAL_DOCUMENTATION_URL",
    )
    emsc_seismicportal_fdsn_url: str = Field(
        default="https://www.seismicportal.eu/fdsnws/event/1/",
        alias="EMSC_SEISMICPORTAL_FDSN_URL",
    )
    emsc_seismicportal_http_timeout_seconds: int = Field(
        default=20,
        alias="EMSC_SEISMICPORTAL_HTTP_TIMEOUT_SECONDS",
    )
    orfeus_eida_source_mode: str = Field(
        default="fixture",
        alias="ORFEUS_EIDA_SOURCE_MODE",
    )
    orfeus_eida_fixture_path: str = Field(
        default="./data/orfeus_eida_station_fixture.txt",
        alias="ORFEUS_EIDA_FIXTURE_PATH",
    )
    orfeus_eida_documentation_url: str = Field(
        default="https://www.orfeus-eu.org/data/eida/nodes/FEDERATOR/",
        alias="ORFEUS_EIDA_DOCUMENTATION_URL",
    )
    orfeus_eida_station_url: str = Field(
        default="https://federator.orfeus-eu.org/fdsnws/station/1/",
        alias="ORFEUS_EIDA_STATION_URL",
    )
    orfeus_eida_http_timeout_seconds: int = Field(
        default=20,
        alias="ORFEUS_EIDA_HTTP_TIMEOUT_SECONDS",
    )
    bc_wildfire_datamart_source_mode: str = Field(
        default="fixture",
        alias="BC_WILDFIRE_DATAMART_SOURCE_MODE",
    )
    bc_wildfire_datamart_fixture_path: str = Field(
        default="./data/bc_wildfire_datamart_fixture.json",
        alias="BC_WILDFIRE_DATAMART_FIXTURE_PATH",
    )
    bc_wildfire_datamart_stations_url: str = Field(
        default="https://bcwsapi.nrs.gov.bc.ca/wfwx-datamart-api/v1/stations",
        alias="BC_WILDFIRE_DATAMART_STATIONS_URL",
    )
    bc_wildfire_datamart_danger_summaries_url: str = Field(
        default="https://bcwsapi.nrs.gov.bc.ca/wfwx-datamart-api/v1/danger-summaries",
        alias="BC_WILDFIRE_DATAMART_DANGER_SUMMARIES_URL",
    )
    bc_wildfire_datamart_documentation_url: str = Field(
        default="https://www2.gov.bc.ca/assets/gov/public-safety-and-emergency-services/wildfire-status/prepare/bcws_datamart_and_api_v2_1.pdf",
        alias="BC_WILDFIRE_DATAMART_DOCUMENTATION_URL",
    )
    bc_wildfire_datamart_http_timeout_seconds: int = Field(
        default=20,
        alias="BC_WILDFIRE_DATAMART_HTTP_TIMEOUT_SECONDS",
    )
    meteoswiss_open_data_source_mode: str = Field(
        default="fixture",
        alias="METEOSWISS_OPEN_DATA_SOURCE_MODE",
    )
    meteoswiss_open_data_fixture_path: str = Field(
        default="./data/meteoswiss_open_data_fixture.json",
        alias="METEOSWISS_OPEN_DATA_FIXTURE_PATH",
    )
    meteoswiss_open_data_documentation_url: str = Field(
        default="https://opendatadocs.meteoswiss.ch/a-data-groundbased/a1-automatic-weather-stations",
        alias="METEOSWISS_OPEN_DATA_DOCUMENTATION_URL",
    )
    meteoswiss_open_data_collection_url: str = Field(
        default="https://data.geo.admin.ch/api/stac/v1/collections/ch.meteoschweiz.ogd-smn",
        alias="METEOSWISS_OPEN_DATA_COLLECTION_URL",
    )
    meteoswiss_open_data_items_url: str = Field(
        default="https://data.geo.admin.ch/api/stac/v1/collections/ch.meteoschweiz.ogd-smn/items",
        alias="METEOSWISS_OPEN_DATA_ITEMS_URL",
    )
    meteoswiss_open_data_http_timeout_seconds: int = Field(
        default=20,
        alias="METEOSWISS_OPEN_DATA_HTTP_TIMEOUT_SECONDS",
    )
    canada_geomet_ogc_source_mode: str = Field(
        default="fixture",
        alias="CANADA_GEOMET_OGC_SOURCE_MODE",
    )
    canada_geomet_ogc_fixture_path: str = Field(
        default="./data/canada_geomet_climate_stations_fixture.json",
        alias="CANADA_GEOMET_OGC_FIXTURE_PATH",
    )
    canada_geomet_ogc_documentation_url: str = Field(
        default="https://eccc-msc.github.io/open-data/msc-geomet/readme_en/",
        alias="CANADA_GEOMET_OGC_DOCUMENTATION_URL",
    )
    canada_geomet_ogc_collection_url: str = Field(
        default="https://api.weather.gc.ca/collections/climate-stations",
        alias="CANADA_GEOMET_OGC_COLLECTION_URL",
    )
    canada_geomet_ogc_items_url: str = Field(
        default="https://api.weather.gc.ca/collections/climate-stations/items",
        alias="CANADA_GEOMET_OGC_ITEMS_URL",
    )
    canada_geomet_ogc_http_timeout_seconds: int = Field(
        default=20,
        alias="CANADA_GEOMET_OGC_HTTP_TIMEOUT_SECONDS",
    )
    natural_earth_physical_source_mode: str = Field(
        default="fixture",
        alias="NATURAL_EARTH_PHYSICAL_SOURCE_MODE",
    )
    natural_earth_physical_fixture_path: str = Field(
        default="./data/natural_earth_physical_land_fixture.json",
        alias="NATURAL_EARTH_PHYSICAL_FIXTURE_PATH",
    )
    natural_earth_physical_source_url: str = Field(
        default="https://naturalearth.s3.amazonaws.com/110m_physical/ne_110m_land.zip",
        alias="NATURAL_EARTH_PHYSICAL_SOURCE_URL",
    )
    natural_earth_physical_http_timeout_seconds: int = Field(
        default=20,
        alias="NATURAL_EARTH_PHYSICAL_HTTP_TIMEOUT_SECONDS",
    )
    gshhg_shorelines_source_mode: str = Field(
        default="fixture",
        alias="GSHHG_SHORELINES_SOURCE_MODE",
    )
    gshhg_shorelines_fixture_path: str = Field(
        default="./data/gshhg_shorelines_fixture.json",
        alias="GSHHG_SHORELINES_FIXTURE_PATH",
    )
    gshhg_shorelines_source_url: str = Field(
        default="https://www.ngdc.noaa.gov/mgg/shorelines/shorelines.html",
        alias="GSHHG_SHORELINES_SOURCE_URL",
    )
    gshhg_shorelines_http_timeout_seconds: int = Field(
        default=20,
        alias="GSHHG_SHORELINES_HTTP_TIMEOUT_SECONDS",
    )
    pb2002_plate_boundaries_source_mode: str = Field(
        default="fixture",
        alias="PB2002_PLATE_BOUNDARIES_SOURCE_MODE",
    )
    pb2002_plate_boundaries_fixture_path: str = Field(
        default="./data/pb2002_plate_boundaries_fixture.json",
        alias="PB2002_PLATE_BOUNDARIES_FIXTURE_PATH",
    )
    pb2002_plate_boundaries_source_url: str = Field(
        default="https://peterbird.name/publications/2003_pb2002/2003_pb2002.htm",
        alias="PB2002_PLATE_BOUNDARIES_SOURCE_URL",
    )
    pb2002_plate_boundaries_http_timeout_seconds: int = Field(
        default=20,
        alias="PB2002_PLATE_BOUNDARIES_HTTP_TIMEOUT_SECONDS",
    )
    noaa_global_volcano_source_mode: str = Field(
        default="fixture",
        alias="NOAA_GLOBAL_VOLCANO_SOURCE_MODE",
    )
    noaa_global_volcano_fixture_path: str = Field(
        default="./data/noaa_global_volcano_locations_fixture.json",
        alias="NOAA_GLOBAL_VOLCANO_FIXTURE_PATH",
    )
    noaa_global_volcano_api_url: str = Field(
        default="https://www.ngdc.noaa.gov/hazel/hazard-service/api/v1/volcanolocs",
        alias="NOAA_GLOBAL_VOLCANO_API_URL",
    )
    noaa_global_volcano_http_timeout_seconds: int = Field(
        default=20,
        alias="NOAA_GLOBAL_VOLCANO_HTTP_TIMEOUT_SECONDS",
    )
    rgi_glacier_inventory_source_mode: str = Field(
        default="fixture",
        alias="RGI_GLACIER_INVENTORY_SOURCE_MODE",
    )
    rgi_glacier_inventory_fixture_path: str = Field(
        default="./data/rgi_glacier_inventory_fixture.json",
        alias="RGI_GLACIER_INVENTORY_FIXTURE_PATH",
    )
    rgi_glacier_inventory_source_url: str = Field(
        default="https://nsidc.org/data/nsidc-0770/versions/7",
        alias="RGI_GLACIER_INVENTORY_SOURCE_URL",
    )
    rgi_glacier_inventory_documentation_url: str = Field(
        default="https://www.glims.org/rgi_user_guide/welcome.html",
        alias="RGI_GLACIER_INVENTORY_DOCUMENTATION_URL",
    )
    rgi_glacier_inventory_http_timeout_seconds: int = Field(
        default=20,
        alias="RGI_GLACIER_INVENTORY_HTTP_TIMEOUT_SECONDS",
    )
    taiwan_cwa_source_mode: str = Field(default="fixture", alias="TAIWAN_CWA_SOURCE_MODE")
    taiwan_cwa_fixture_path: str = Field(
        default="./data/taiwan_cwa_current_weather_fixture.json",
        alias="TAIWAN_CWA_FIXTURE_PATH",
    )
    taiwan_cwa_current_weather_url: str = Field(
        default="https://cwaopendata.s3.ap-northeast-1.amazonaws.com/Observation/O-A0003-001.json",
        alias="TAIWAN_CWA_CURRENT_WEATHER_URL",
    )
    taiwan_cwa_http_timeout_seconds: int = Field(default=20, alias="TAIWAN_CWA_HTTP_TIMEOUT_SECONDS")
    nrc_event_notifications_source_mode: str = Field(
        default="fixture",
        alias="NRC_EVENT_NOTIFICATIONS_SOURCE_MODE",
    )
    nrc_event_notifications_fixture_path: str = Field(
        default="./data/nrc_event_notifications_fixture.xml",
        alias="NRC_EVENT_NOTIFICATIONS_FIXTURE_PATH",
    )
    nrc_event_notifications_feed_url: str = Field(
        default="https://www.nrc.gov/public-involve/rss?feed=event",
        alias="NRC_EVENT_NOTIFICATIONS_FEED_URL",
    )
    nrc_event_notifications_http_timeout_seconds: int = Field(
        default=20,
        alias="NRC_EVENT_NOTIFICATIONS_HTTP_TIMEOUT_SECONDS",
    )
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
    dwd_cap_source_mode: str = Field(default="fixture", alias="DWD_CAP_SOURCE_MODE")
    dwd_cap_fixture_path: str = Field(
        default="./data/dwd_cap_directory_fixture.html",
        alias="DWD_CAP_FIXTURE_PATH",
    )
    dwd_cap_directory_url: str = Field(
        default="https://opendata.dwd.de/weather/alerts/cap/",
        alias="DWD_CAP_DIRECTORY_URL",
    )
    dwd_cap_snapshot_family: str = Field(
        default="DISTRICT_DWD_STAT",
        alias="DWD_CAP_SNAPSHOT_FAMILY",
    )
    dwd_cap_snapshot_family_url: str = Field(
        default="https://opendata.dwd.de/weather/alerts/cap/DISTRICT_DWD_STAT/",
        alias="DWD_CAP_SNAPSHOT_FAMILY_URL",
    )
    dwd_cap_http_timeout_seconds: int = Field(default=20, alias="DWD_CAP_HTTP_TIMEOUT_SECONDS")
    bmkg_earthquakes_source_mode: str = Field(default="fixture", alias="BMKG_EARTHQUAKES_SOURCE_MODE")
    bmkg_earthquakes_fixture_path: str = Field(
        default="./data/bmkg_earthquakes_fixture.json",
        alias="BMKG_EARTHQUAKES_FIXTURE_PATH",
    )
    bmkg_earthquakes_latest_url: str = Field(
        default="https://data.bmkg.go.id/DataMKG/TEWS/autogempa.json",
        alias="BMKG_EARTHQUAKES_LATEST_URL",
    )
    bmkg_earthquakes_recent_url: str = Field(
        default="https://data.bmkg.go.id/DataMKG/TEWS/gempaterkini.json",
        alias="BMKG_EARTHQUAKES_RECENT_URL",
    )
    bmkg_earthquakes_http_timeout_seconds: int = Field(
        default=20,
        alias="BMKG_EARTHQUAKES_HTTP_TIMEOUT_SECONDS",
    )
    ga_recent_earthquakes_source_mode: str = Field(default="fixture", alias="GA_RECENT_EARTHQUAKES_SOURCE_MODE")
    ga_recent_earthquakes_fixture_path: str = Field(
        default="./data/ga_recent_earthquakes_fixture.kml",
        alias="GA_RECENT_EARTHQUAKES_FIXTURE_PATH",
    )
    ga_recent_earthquakes_feed_url: str = Field(
        default="https://earthquakes.ga.gov.au/geoserver/earthquakes/wms?service=wms&request=GetMap&version=1.1.1&format=application/vnd.google-earth.kml+xml&layers=earthquakes_seven_days&styles=earthquakes:earthquakes_seven_days&cql_filter=display_flag=%27Y%27&height=2048&width=2048&transparent=false&srs=EPSG:4326&bbox=-180,-90,180,90&format_options=AUTOFIT:true;KMATTR:true;KMPLACEMARK:false;KMSCORE:40;MODE:refresh;SUPEROVERLAY:false",
        alias="GA_RECENT_EARTHQUAKES_FEED_URL",
    )
    ga_recent_earthquakes_http_timeout_seconds: int = Field(
        default=20,
        alias="GA_RECENT_EARTHQUAKES_HTTP_TIMEOUT_SECONDS",
    )
    ipma_source_mode: str = Field(default="fixture", alias="IPMA_SOURCE_MODE")
    ipma_fixture_path: str = Field(
        default="./data/ipma_warnings_fixture.json",
        alias="IPMA_FIXTURE_PATH",
    )
    ipma_warnings_url: str = Field(
        default="https://api.ipma.pt/open-data/forecast/warnings/warnings_www.json",
        alias="IPMA_WARNINGS_URL",
    )
    ipma_areas_url: str = Field(
        default="https://api.ipma.pt/open-data/distrits-islands.json",
        alias="IPMA_AREAS_URL",
    )
    ipma_http_timeout_seconds: int = Field(default=20, alias="IPMA_HTTP_TIMEOUT_SECONDS")
    dmi_forecast_source_mode: str = Field(default="fixture", alias="DMI_FORECAST_SOURCE_MODE")
    dmi_forecast_fixture_path: str = Field(
        default="./data/dmi_forecast_fixture.json",
        alias="DMI_FORECAST_FIXTURE_PATH",
    )
    dmi_forecast_base_url: str = Field(
        default="https://opendataapi.dmi.dk/v1/forecastedr",
        alias="DMI_FORECAST_BASE_URL",
    )
    dmi_forecast_collection: str = Field(
        default="harmonie_dini_sf",
        alias="DMI_FORECAST_COLLECTION",
    )
    dmi_forecast_http_timeout_seconds: int = Field(default=20, alias="DMI_FORECAST_HTTP_TIMEOUT_SECONDS")
    ireland_wfd_source_mode: str = Field(default="fixture", alias="IRELAND_WFD_SOURCE_MODE")
    ireland_wfd_fixture_path: str = Field(
        default="./data/ireland_epa_wfd_catchments_fixture.json",
        alias="IRELAND_WFD_FIXTURE_PATH",
    )
    ireland_wfd_catchment_url: str = Field(
        default="https://wfdapi.edenireland.ie/api/catchment",
        alias="IRELAND_WFD_CATCHMENT_URL",
    )
    ireland_wfd_search_url: str = Field(
        default="https://wfdapi.edenireland.ie/api/search",
        alias="IRELAND_WFD_SEARCH_URL",
    )
    ireland_wfd_http_timeout_seconds: int = Field(default=20, alias="IRELAND_WFD_HTTP_TIMEOUT_SECONDS")
    met_eireann_warnings_source_mode: str = Field(default="fixture", alias="MET_EIREANN_WARNINGS_SOURCE_MODE")
    met_eireann_warnings_fixture_path: str = Field(
        default="./data/met_eireann_warning_rss_fixture.xml",
        alias="MET_EIREANN_WARNINGS_FIXTURE_PATH",
    )
    met_eireann_warnings_feed_url: str = Field(
        default="https://www.met.ie/warningsxml/rss.xml",
        alias="MET_EIREANN_WARNINGS_FEED_URL",
    )
    met_eireann_warnings_http_timeout_seconds: int = Field(
        default=20,
        alias="MET_EIREANN_WARNINGS_HTTP_TIMEOUT_SECONDS",
    )
    met_eireann_forecast_source_mode: str = Field(default="fixture", alias="MET_EIREANN_FORECAST_SOURCE_MODE")
    met_eireann_forecast_fixture_path: str = Field(
        default="./data/met_eireann_forecast_fixture.xml",
        alias="MET_EIREANN_FORECAST_FIXTURE_PATH",
    )
    met_eireann_forecast_url: str = Field(
        default="https://openaccess.pf.api.met.ie/metno-wdb2ts/locationforecast",
        alias="MET_EIREANN_FORECAST_URL",
    )
    met_eireann_forecast_http_timeout_seconds: int = Field(
        default=20,
        alias="MET_EIREANN_FORECAST_HTTP_TIMEOUT_SECONDS",
    )
    geosphere_austria_warnings_source_mode: str = Field(
        default="fixture",
        alias="GEOSPHERE_AUSTRIA_WARNINGS_SOURCE_MODE",
    )
    geosphere_austria_warnings_fixture_path: str = Field(
        default="./data/geosphere_austria_warnings_fixture.json",
        alias="GEOSPHERE_AUSTRIA_WARNINGS_FIXTURE_PATH",
    )
    geosphere_austria_warnings_url: str = Field(
        default="https://warnungen.zamg.at/wsapp/api/getWarnstatus?lang=en",
        alias="GEOSPHERE_AUSTRIA_WARNINGS_URL",
    )
    geosphere_austria_warnings_http_timeout_seconds: int = Field(
        default=20,
        alias="GEOSPHERE_AUSTRIA_WARNINGS_HTTP_TIMEOUT_SECONDS",
    )
    france_georisques_source_mode: str = Field(
        default="fixture",
        alias="FRANCE_GEORISQUES_SOURCE_MODE",
    )
    france_georisques_fixture_path: str = Field(
        default="./data/france_georisques_fixture.json",
        alias="FRANCE_GEORISQUES_FIXTURE_PATH",
    )
    france_georisques_seismic_zoning_url: str = Field(
        default="https://www.georisques.gouv.fr/api/v1/zonage_sismique",
        alias="FRANCE_GEORISQUES_SEISMIC_ZONING_URL",
    )
    france_georisques_http_timeout_seconds: int = Field(
        default=20,
        alias="FRANCE_GEORISQUES_HTTP_TIMEOUT_SECONDS",
    )
    uk_ea_water_quality_source_mode: str = Field(
        default="fixture",
        alias="UK_EA_WATER_QUALITY_SOURCE_MODE",
    )
    uk_ea_water_quality_fixture_path: str = Field(
        default="./data/uk_ea_water_quality_fixture.json",
        alias="UK_EA_WATER_QUALITY_FIXTURE_PATH",
    )
    uk_ea_water_quality_samples_url: str = Field(
        default="https://environment.data.gov.uk/data/bathing-water-quality/in-season/sample.json",
        alias="UK_EA_WATER_QUALITY_SAMPLES_URL",
    )
    uk_ea_water_quality_http_timeout_seconds: int = Field(
        default=20,
        alias="UK_EA_WATER_QUALITY_HTTP_TIMEOUT_SECONDS",
    )
    nasa_power_source_mode: str = Field(
        default="fixture",
        alias="NASA_POWER_SOURCE_MODE",
    )
    nasa_power_fixture_path: str = Field(
        default="./data/nasa_power_meteorology_solar_fixture.json",
        alias="NASA_POWER_FIXTURE_PATH",
    )
    nasa_power_daily_point_url: str = Field(
        default="https://power.larc.nasa.gov/api/temporal/daily/point",
        alias="NASA_POWER_DAILY_POINT_URL",
    )
    nasa_power_http_timeout_seconds: int = Field(
        default=20,
        alias="NASA_POWER_HTTP_TIMEOUT_SECONDS",
    )
    usgs_geomagnetism_source_mode: str = Field(
        default="fixture",
        alias="USGS_GEOMAGNETISM_SOURCE_MODE",
    )
    usgs_geomagnetism_fixture_path: str = Field(
        default="./data/usgs_geomagnetism_fixture.json",
        alias="USGS_GEOMAGNETISM_FIXTURE_PATH",
    )
    usgs_geomagnetism_data_url: str = Field(
        default="https://geomag.usgs.gov/ws/data/",
        alias="USGS_GEOMAGNETISM_DATA_URL",
    )
    usgs_geomagnetism_http_timeout_seconds: int = Field(
        default=20,
        alias="USGS_GEOMAGNETISM_HTTP_TIMEOUT_SECONDS",
    )
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
    cisa_cyber_advisories_source_mode: str = Field(
        default="fixture",
        alias="CISA_CYBER_ADVISORIES_SOURCE_MODE",
    )
    cisa_cyber_advisories_fixture_path: str = Field(
        default="./data/cisa_cybersecurity_advisories_fixture.xml",
        alias="CISA_CYBER_ADVISORIES_FIXTURE_PATH",
    )
    cisa_cyber_advisories_feed_url: str = Field(
        default="https://www.cisa.gov/cybersecurity-advisories/cybersecurity-advisories.xml",
        alias="CISA_CYBER_ADVISORIES_FEED_URL",
    )
    cisa_cyber_advisories_http_timeout_seconds: int = Field(
        default=20,
        alias="CISA_CYBER_ADVISORIES_HTTP_TIMEOUT_SECONDS",
    )
    first_epss_source_mode: str = Field(
        default="fixture",
        alias="FIRST_EPSS_SOURCE_MODE",
    )
    first_epss_fixture_path: str = Field(
        default="./data/first_epss_fixture.json",
        alias="FIRST_EPSS_FIXTURE_PATH",
    )
    first_epss_api_url: str = Field(
        default="https://api.first.org/data/v1/epss",
        alias="FIRST_EPSS_API_URL",
    )
    first_epss_http_timeout_seconds: int = Field(
        default=20,
        alias="FIRST_EPSS_HTTP_TIMEOUT_SECONDS",
    )
    data_ai_multi_feed_source_mode: str = Field(
        default="fixture",
        alias="DATA_AI_MULTI_FEED_SOURCE_MODE",
    )
    data_ai_multi_feed_fixture_root: str = Field(
        default="./data/data_ai_multi_feeds",
        alias="DATA_AI_MULTI_FEED_FIXTURE_ROOT",
    )
    data_ai_multi_feed_http_timeout_seconds: int = Field(
        default=20,
        alias="DATA_AI_MULTI_FEED_HTTP_TIMEOUT_SECONDS",
    )
    data_ai_multi_feed_stale_after_seconds: int = Field(
        default=172800,
        alias="DATA_AI_MULTI_FEED_STALE_AFTER_SECONDS",
    )
    nvd_cve_source_mode: str = Field(
        default="fixture",
        alias="NVD_CVE_SOURCE_MODE",
    )
    nvd_cve_fixture_path: str = Field(
        default="./data/nvd_cve_fixture.json",
        alias="NVD_CVE_FIXTURE_PATH",
    )
    nvd_cve_api_url: str = Field(
        default="https://services.nvd.nist.gov/rest/json/cves/2.0",
        alias="NVD_CVE_API_URL",
    )
    nvd_cve_http_timeout_seconds: int = Field(
        default=20,
        alias="NVD_CVE_HTTP_TIMEOUT_SECONDS",
    )
    wave_monitor_database_url: str = Field(
        default="sqlite:///./data/wave_monitor.db",
        alias="WAVE_MONITOR_DATABASE_URL",
    )
    wave_monitor_http_timeout_seconds: int = Field(
        default=20,
        alias="WAVE_MONITOR_HTTP_TIMEOUT_SECONDS",
    )
    source_discovery_database_url: str = Field(
        default="sqlite:///./data/source_discovery.db",
        alias="SOURCE_DISCOVERY_DATABASE_URL",
    )
    source_discovery_scheduler_enabled: bool = Field(default=False, alias="SOURCE_DISCOVERY_SCHEDULER_ENABLED")
    source_discovery_scheduler_run_on_startup: bool = Field(default=False, alias="SOURCE_DISCOVERY_SCHEDULER_RUN_ON_STARTUP")
    source_discovery_scheduler_poll_seconds: int = Field(default=300, alias="SOURCE_DISCOVERY_SCHEDULER_POLL_SECONDS")
    source_discovery_scheduler_health_check_limit: int = Field(default=2, alias="SOURCE_DISCOVERY_SCHEDULER_HEALTH_CHECK_LIMIT")
    source_discovery_scheduler_structure_scan_limit: int = Field(default=0, alias="SOURCE_DISCOVERY_SCHEDULER_STRUCTURE_SCAN_LIMIT")
    source_discovery_scheduler_public_discovery_job_limit: int = Field(default=0, alias="SOURCE_DISCOVERY_SCHEDULER_PUBLIC_DISCOVERY_JOB_LIMIT")
    source_discovery_scheduler_expansion_job_limit: int = Field(default=0, alias="SOURCE_DISCOVERY_SCHEDULER_EXPANSION_JOB_LIMIT")
    source_discovery_scheduler_knowledge_backfill_limit: int = Field(default=0, alias="SOURCE_DISCOVERY_SCHEDULER_KNOWLEDGE_BACKFILL_LIMIT")
    source_discovery_scheduler_record_extract_limit: int = Field(default=0, alias="SOURCE_DISCOVERY_SCHEDULER_RECORD_EXTRACT_LIMIT")
    source_discovery_scheduler_llm_task_limit: int = Field(default=0, alias="SOURCE_DISCOVERY_SCHEDULER_LLM_TASK_LIMIT")
    source_discovery_scheduler_request_budget: int = Field(default=0, alias="SOURCE_DISCOVERY_SCHEDULER_REQUEST_BUDGET")
    source_discovery_scheduler_allow_network: bool = Field(default=False, alias="SOURCE_DISCOVERY_SCHEDULER_ALLOW_NETWORK")
    source_discovery_media_max_bytes: int = Field(default=5_000_000, alias="SOURCE_DISCOVERY_MEDIA_MAX_BYTES")
    source_discovery_media_ocr_binary: str = Field(default="tesseract", alias="SOURCE_DISCOVERY_MEDIA_OCR_BINARY")
    source_discovery_media_ocr_default_engine: str = Field(default="tesseract", alias="SOURCE_DISCOVERY_MEDIA_OCR_DEFAULT_ENGINE")
    source_discovery_media_ocr_fallback_enabled: bool = Field(default=True, alias="SOURCE_DISCOVERY_MEDIA_OCR_FALLBACK_ENABLED")
    source_discovery_media_ocr_confidence_threshold: float = Field(default=0.65, alias="SOURCE_DISCOVERY_MEDIA_OCR_CONFIDENCE_THRESHOLD")
    source_discovery_media_ocr_min_text_length: int = Field(default=24, alias="SOURCE_DISCOVERY_MEDIA_OCR_MIN_TEXT_LENGTH")
    source_discovery_media_rapidocr_model_dir: str | None = Field(default=None, alias="SOURCE_DISCOVERY_MEDIA_RAPIDOCR_MODEL_DIR")
    source_discovery_media_ollama_enabled: bool = Field(default=False, alias="SOURCE_DISCOVERY_MEDIA_OLLAMA_ENABLED")
    source_discovery_media_ollama_model: str | None = Field(default=None, alias="SOURCE_DISCOVERY_MEDIA_OLLAMA_MODEL")
    source_discovery_media_openai_compat_enabled: bool = Field(default=False, alias="SOURCE_DISCOVERY_MEDIA_OPENAI_COMPAT_ENABLED")
    source_discovery_media_openai_compat_model: str | None = Field(default=None, alias="SOURCE_DISCOVERY_MEDIA_OPENAI_COMPAT_MODEL")
    source_discovery_media_openai_compat_base_url: str | None = Field(default="http://localhost:8000/v1", alias="SOURCE_DISCOVERY_MEDIA_OPENAI_COMPAT_BASE_URL")
    source_discovery_media_geolocation_default_engine: str = Field(default="fusion", alias="SOURCE_DISCOVERY_MEDIA_GEOLOCATION_DEFAULT_ENGINE")
    source_discovery_media_geolocation_max_candidates: int = Field(default=5, alias="SOURCE_DISCOVERY_MEDIA_GEOLOCATION_MAX_CANDIDATES")
    source_discovery_media_geolocation_eval_fixture_path: str = Field(
        default="./app/server/data/media_geolocation_eval_fixtures.json",
        alias="SOURCE_DISCOVERY_MEDIA_GEOLOCATION_EVAL_FIXTURE_PATH",
    )
    source_discovery_media_geoclip_enabled: bool = Field(default=False, alias="SOURCE_DISCOVERY_MEDIA_GEOCLIP_ENABLED")
    source_discovery_media_geoclip_allow_runtime_download: bool = Field(default=False, alias="SOURCE_DISCOVERY_MEDIA_GEOCLIP_ALLOW_RUNTIME_DOWNLOAD")
    source_discovery_media_geoclip_model_cache_dir: str | None = Field(default=None, alias="SOURCE_DISCOVERY_MEDIA_GEOCLIP_MODEL_CACHE_DIR")
    source_discovery_media_geoclip_weights_path: str | None = Field(default=None, alias="SOURCE_DISCOVERY_MEDIA_GEOCLIP_WEIGHTS_PATH")
    source_discovery_media_geoclip_expected_version: str | None = Field(default=None, alias="SOURCE_DISCOVERY_MEDIA_GEOCLIP_EXPECTED_VERSION")
    source_discovery_media_streetclip_enabled: bool = Field(default=False, alias="SOURCE_DISCOVERY_MEDIA_STREETCLIP_ENABLED")
    source_discovery_media_streetclip_model_id: str = Field(default="geolocal/StreetCLIP", alias="SOURCE_DISCOVERY_MEDIA_STREETCLIP_MODEL_ID")
    source_discovery_media_streetclip_allow_runtime_download: bool = Field(default=False, alias="SOURCE_DISCOVERY_MEDIA_STREETCLIP_ALLOW_RUNTIME_DOWNLOAD")
    source_discovery_media_streetclip_model_cache_dir: str | None = Field(default=None, alias="SOURCE_DISCOVERY_MEDIA_STREETCLIP_MODEL_CACHE_DIR")
    source_discovery_media_streetclip_expected_transformers_version: str | None = Field(default=None, alias="SOURCE_DISCOVERY_MEDIA_STREETCLIP_EXPECTED_TRANSFORMERS_VERSION")
    source_discovery_media_streetclip_label_bank_enabled: bool = Field(default=True, alias="SOURCE_DISCOVERY_MEDIA_STREETCLIP_LABEL_BANK_ENABLED")
    source_discovery_media_qwen_vl_local_model: str | None = Field(default=None, alias="SOURCE_DISCOVERY_MEDIA_QWEN_VL_LOCAL_MODEL")
    source_discovery_media_internvl_local_model: str | None = Field(default=None, alias="SOURCE_DISCOVERY_MEDIA_INTERNVL_LOCAL_MODEL")
    source_discovery_media_llava_local_model: str | None = Field(default=None, alias="SOURCE_DISCOVERY_MEDIA_LLAVA_LOCAL_MODEL")
    source_discovery_media_comparison_candidate_cap: int = Field(default=8, alias="SOURCE_DISCOVERY_MEDIA_COMPARISON_CANDIDATE_CAP")
    source_discovery_media_ssim_duplicate_threshold: float = Field(default=0.95, alias="SOURCE_DISCOVERY_MEDIA_SSIM_DUPLICATE_THRESHOLD")
    source_discovery_media_ssim_change_threshold: float = Field(default=0.72, alias="SOURCE_DISCOVERY_MEDIA_SSIM_CHANGE_THRESHOLD")
    source_discovery_media_phash_near_distance: int = Field(default=8, alias="SOURCE_DISCOVERY_MEDIA_PHASH_NEAR_DISTANCE")
    source_discovery_media_ffmpeg_binary: str = Field(default="ffmpeg", alias="SOURCE_DISCOVERY_MEDIA_FFMPEG_BINARY")
    source_discovery_media_frame_max_span_seconds: int = Field(default=60, alias="SOURCE_DISCOVERY_MEDIA_FRAME_MAX_SPAN_SECONDS")
    source_discovery_media_frame_max_frames: int = Field(default=12, alias="SOURCE_DISCOVERY_MEDIA_FRAME_MAX_FRAMES")
    source_discovery_media_frame_min_interval_seconds: int = Field(default=5, alias="SOURCE_DISCOVERY_MEDIA_FRAME_MIN_INTERVAL_SECONDS")
    wave_monitor_scheduler_enabled: bool = Field(default=False, alias="WAVE_MONITOR_SCHEDULER_ENABLED")
    wave_monitor_scheduler_run_on_startup: bool = Field(default=False, alias="WAVE_MONITOR_SCHEDULER_RUN_ON_STARTUP")
    wave_monitor_scheduler_poll_seconds: int = Field(default=300, alias="WAVE_MONITOR_SCHEDULER_POLL_SECONDS")
    wave_llm_enabled: bool = Field(default=False, alias="WAVE_LLM_ENABLED")
    wave_llm_default_provider: str = Field(default="fixture", alias="WAVE_LLM_DEFAULT_PROVIDER")
    wave_llm_default_model: str = Field(default="local-fixture", alias="WAVE_LLM_DEFAULT_MODEL")
    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    anthropic_api_key: str | None = Field(default=None, alias="ANTHROPIC_API_KEY")
    xai_api_key: str | None = Field(default=None, alias="XAI_API_KEY")
    google_ai_api_key: str | None = Field(default=None, alias="GOOGLE_AI_API_KEY")
    openrouter_api_key: str | None = Field(default=None, alias="OPENROUTER_API_KEY")
    ollama_base_url: str | None = Field(default="http://localhost:11434", alias="OLLAMA_BASE_URL")
    openclaw_base_url: str | None = Field(default=None, alias="OPENCLAW_BASE_URL")
    wave_llm_max_input_chars: int = Field(default=12000, alias="WAVE_LLM_MAX_INPUT_CHARS")
    wave_llm_max_output_chars: int = Field(default=8000, alias="WAVE_LLM_MAX_OUTPUT_CHARS")
    wave_llm_http_timeout_seconds: int = Field(default=30, alias="WAVE_LLM_HTTP_TIMEOUT_SECONDS")
    wave_llm_max_retries: int = Field(default=1, alias="WAVE_LLM_MAX_RETRIES")
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
