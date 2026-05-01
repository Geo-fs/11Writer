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
