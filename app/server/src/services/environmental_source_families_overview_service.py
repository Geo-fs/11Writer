from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Literal

from src.config.settings import Settings
from src.services.bmkg_earthquakes_service import BmkgEarthquakesQuery, BmkgEarthquakesService
from src.services.bc_wildfire_datamart_service import BcWildfireDatamartQuery, BcWildfireDatamartService
from src.services.dmi_forecast_service import DmiForecastQuery, DmiForecastService
from src.services.emsc_seismicportal_realtime_service import (
    EmscSeismicPortalQuery,
    EmscSeismicPortalRealtimeService,
)
from src.services.earthquake_service import EarthquakeQuery, EarthquakeService
from src.services.eonet_service import EonetQuery, EonetService
from src.services.france_georisques_service import FranceGeorisquesQuery, FranceGeorisquesService
from src.services.ga_recent_earthquakes_service import GaRecentEarthquakesQuery, GaRecentEarthquakesService
from src.services.gshhg_shorelines_service import GshhgShorelinesQuery, GshhgShorelinesService
from src.services.geosphere_austria_warnings_service import (
    GeosphereWarningLevel,
    GeosphereWarningSort,
    GeosphereAustriaWarningsQuery,
    GeosphereAustriaWarningsService,
)
from src.services.geonet_service import GeoNetQuery, GeoNetService
from src.services.hko_weather_service import HkoWeatherQuery, HkoWeatherService
from src.services.ireland_wfd_service import IrelandWfdQuery, IrelandWfdService
from src.services.ipma_warnings_service import IpmaWarningsQuery, IpmaWarningsService
from src.services.met_eireann_forecast_service import MetEireannForecastQuery, MetEireannForecastService
from src.services.met_eireann_warnings_service import (
    MetEireannWarningsQuery,
    MetEireannWarningsService,
)
from src.services.meteoswiss_open_data_service import MeteoSwissOpenDataQuery, MeteoSwissOpenDataService
from src.services.metno_metalerts_service import MetNoMetAlertsQuery, MetNoMetAlertsService
from src.services.nasa_power_meteorology_solar_service import (
    NasaPowerMeteorologySolarQuery,
    NasaPowerMeteorologySolarService,
)
from src.services.natural_earth_physical_service import NaturalEarthPhysicalQuery, NaturalEarthPhysicalService
from src.services.noaa_global_volcano_service import NoaaGlobalVolcanoQuery, NoaaGlobalVolcanoService
from src.services.nrc_event_notifications_service import NrcEventNotificationsQuery, NrcEventNotificationsService, NrcSort
from src.services.orfeus_eida_service import OrfeusEidaQuery, OrfeusEidaService
from src.services.pb2002_plate_boundaries_service import (
    Pb2002PlateBoundariesQuery,
    Pb2002PlateBoundariesService,
)
from src.services.source_registry import SourceRuntimeStatus, get_source_runtime_status
from src.services.taiwan_cwa_weather_service import TaiwanCwaWeatherQuery, TaiwanCwaWeatherService
from src.services.tsunami_service import TsunamiQuery, TsunamiService
from src.services.canada_cap_service import CanadaCapQuery, CanadaCapService
from src.services.uk_ea_flood_service import UkEaFloodQuery, UkEaFloodService
from src.services.uk_ea_water_quality_service import UkEaWaterQualityQuery, UkEaWaterQualityService
from src.services.usgs_geomagnetism_service import UsgsGeomagnetismQuery, UsgsGeomagnetismService
from src.services.volcano_service import VolcanoQuery, VolcanoService
from src.types.api import (
    EnvironmentalContextExportPackage,
    EnvironmentalContextExportPackageMetadata,
    EnvironmentalContextExportSnapshotMetadata,
    EnvironmentalSourceHealthIssue,
    EnvironmentalSourceHealthIssueQueueMetadata,
    EnvironmentalSourceHealthIssueQueuePackage,
    EnvironmentalSituationSnapshotPackage,
    EnvironmentalSituationSnapshotPackageMetadata,
    EnvironmentalSourceFamiliesExportMetadata,
    EnvironmentalSourceFamiliesExportResponse,
    EnvironmentalSourceFamiliesOverviewMetadata,
    EnvironmentalSourceFamiliesOverviewResponse,
    EnvironmentalSourceFamilyExportBundle,
    EnvironmentalSourceFamilyMember,
    EnvironmentalSourceFamilySummary,
    EnvironmentalWeatherObservationExportBundle,
    EnvironmentalWeatherObservationExportMetadata,
    EnvironmentalWeatherObservationReviewItem,
    EnvironmentalWeatherObservationReviewQueueMetadata,
    EnvironmentalWeatherObservationReviewQueuePackage,
    EnvironmentalWeatherObservationSourceSummary,
)

_OVERVIEW_CAVEAT = (
    "This environmental source-family overview is a backend fusion helper over existing source-specific contracts. "
    "It preserves source health, evidence basis, source mode, and caveats without creating a common hazard, damage, or impact score."
)
_EXPORT_CAVEAT = (
    "This compact environmental source-family export bundle is review context only. "
    "It preserves source health, evidence basis, source mode, caveats, and export-safe review lines without creating global hazard, damage, or health-risk scoring."
)
_CONTEXT_EXPORT_CAVEAT = (
    "This environmental context export package is a compact backend snapshot/report input, not a common situation UI and not a hazard, impact, damage, or health-risk truth model."
)
_ISSUE_QUEUE_CAVEAT = (
    "This environmental source-health issue queue is a compact review queue for source-health and evidence-limitation follow-up, not a threat, target, hazard, impact, damage, or health-risk model."
)
_SITUATION_SNAPSHOT_CAVEAT = (
    "This environmental situation snapshot package is a compact backend report input that preserves environmental source context, evidence basis, and source-health posture without becoming a common situation UI or a hazard, threat, impact, damage, or health-risk truth model."
)
_WEATHER_OBSERVATION_EXPORT_CAVEAT = (
    "This environmental weather-observation export bundle is compact review/export context only. "
    "It preserves source mode, source health, evidence basis, timestamps, coordinate gaps, and scope caveats without creating hazard, impact, or action claims."
)
_WEATHER_OBSERVATION_REVIEW_CAVEAT = (
    "This environmental weather-observation review queue is a bounded backend review surface for observation/context source limits, not a hazard, impact, damage, risk, or action model."
)

_FAMILY_ORDER: tuple[str, ...] = (
    "seismic",
    "environmental-event-context",
    "volcano-reference",
    "tsunami-advisory",
    "weather-alert-advisory",
    "weather-flood-hydrology",
    "infrastructure-event-context",
    "geomagnetic-context",
    "base-earth-reference",
    "risk-reference",
    "water-quality-context",
)

_FREE_TEXT_INERT_SOURCE_IDS: frozenset[str] = frozenset(
    {
        "bmkg-earthquakes",
        "ga-recent-earthquakes",
        "nasa-eonet",
        "hong-kong-observatory-open-weather",
        "environment-canada-cap-alerts",
        "met-norway-metalerts",
        "met-eireann-warnings",
        "meteoswiss-open-data",
        "bc-wildfire-datamart",
        "nrc-event-notifications",
        "uk-ea-water-quality",
    }
)
_COUNT_ONLY_SOURCE_IDS: frozenset[str] = frozenset(
    {
        "nasa-eonet",
        "hong-kong-observatory-open-weather",
        "environment-canada-cap-alerts",
        "met-norway-metalerts",
        "france-georisques",
        "ireland-epa-wfd-catchments",
        "noaa-tsunami-alerts",
        "noaa-global-volcano-locations",
        "gshhg-shorelines",
        "pb2002-plate-boundaries",
    }
)
_WEATHER_OBSERVATION_SOURCE_ORDER: tuple[str, ...] = (
    "meteoswiss-open-data",
    "bc-wildfire-datamart",
    "taiwan-cwa-aws-opendata",
    "dmi-forecast-aws",
    "met-eireann-forecast",
    "nasa-power-meteorology-solar",
)


@dataclass(frozen=True)
class _SourceOverviewRow:
    family_id: str
    family_label: str
    source_id: str
    source_label: str
    source_mode: Literal["fixture", "live", "unknown"]
    health: Literal["loaded", "empty", "stale", "error", "disabled", "unknown"]
    runtime_state: str | None
    loaded_count: int
    evidence_basis: str
    last_fetched_at: str | None
    source_generated_at: str | None
    caveat: str
    summary_line: str
    review_lines: list[str]
    export_lines: list[str]


@dataclass(frozen=True)
class _WeatherObservationRow:
    source_id: str
    source_label: str
    source_mode: Literal["fixture", "live", "unknown"]
    source_health: Literal["loaded", "empty", "stale", "error", "disabled", "unknown"]
    evidence_basis: str
    loaded_count: int
    last_fetched_at: str | None
    source_generated_at: str | None
    coordinate_count: int
    missing_coordinate_count: int
    limited_scope: bool
    export_ready: bool
    caveats: list[str]
    review_lines: list[str]
    export_lines: list[str]
    summary_line: str


class EnvironmentalSourceFamiliesOverviewService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def get_overview(self) -> EnvironmentalSourceFamiliesOverviewResponse:
        fetched_at = _utc_now_iso()
        rows = await self._load_rows()
        families = _build_family_summaries(rows)
        return EnvironmentalSourceFamiliesOverviewResponse(
            metadata=EnvironmentalSourceFamiliesOverviewMetadata(
                source="environmental-source-family-overview",
                source_name="Environmental Source Family Overview",
                source_mode=_combined_source_mode([row.source_mode for row in rows]),
                fetched_at=fetched_at,
                family_count=len(families),
                source_count=len(rows),
                caveat=_OVERVIEW_CAVEAT,
            ),
            family_count=len(families),
            source_count=len(rows),
            families=families,
            caveats=[
                _OVERVIEW_CAVEAT,
                "Family rows summarize existing source contracts; they do not replace source-specific meaning or prove impact, health risk, causation, or enforcement relevance.",
            ],
        )

    async def get_export_bundle(
        self,
        *,
        family_ids: list[str] | None = None,
    ) -> EnvironmentalSourceFamiliesExportResponse:
        fetched_at = _utc_now_iso()
        rows = await self._load_rows()
        families = _build_family_summaries(rows)
        requested_family_ids = _normalize_family_ids(family_ids)
        selected_families = _filter_family_summaries(families, requested_family_ids)
        included_family_ids = [family.family_id for family in selected_families]
        missing_family_ids = [family_id for family_id in requested_family_ids if family_id not in included_family_ids]
        source_count = sum(family.source_count for family in selected_families)
        source_mode = _combined_source_mode([row.source_mode for row in rows])
        return EnvironmentalSourceFamiliesExportResponse(
            metadata=EnvironmentalSourceFamiliesExportMetadata(
                source="environmental-source-family-overview",
                source_name="Environmental Source Family Export Bundle",
                profile="compact",
                source_mode=source_mode,
                fetched_at=fetched_at,
                requested_family_ids=requested_family_ids,
                included_family_ids=included_family_ids,
                missing_family_ids=missing_family_ids,
                family_count=len(selected_families),
                source_count=source_count,
                caveat=_EXPORT_CAVEAT,
            ),
            family_count=len(selected_families),
            source_count=source_count,
            families=[
                EnvironmentalSourceFamilyExportBundle(
                    family_id=family.family_id,
                    family_label=family.family_label,
                    family_health=family.family_health,
                    family_mode=family.family_mode,
                    source_ids=family.source_ids,
                    evidence_bases=family.evidence_bases,
                    source_count=family.source_count,
                    loaded_source_count=family.loaded_source_count,
                    fixture_source_count=family.fixture_source_count,
                    last_fetched_at=family.last_fetched_at,
                    source_generated_at=family.source_generated_at,
                    caveats=family.caveats,
                    review_lines=family.review_lines,
                    export_lines=family.export_lines,
                )
                for family in selected_families
            ],
            caveats=[
                _EXPORT_CAVEAT,
                "Export bundles are compact review summaries only and do not replace source-specific meaning or prove impact, damage, health risk, causation, or enforcement relevance.",
            ],
        )

    async def get_context_export_package(
        self,
        *,
        family_ids: list[str] | None = None,
    ) -> EnvironmentalContextExportPackage:
        export_bundle = await self.get_export_bundle(family_ids=family_ids)
        all_family_ids = [family.family_id for family in export_bundle.families]
        all_source_ids = sorted({source_id for family in export_bundle.families for source_id in family.source_ids})
        evidence_bases = sorted({basis for family in export_bundle.families for basis in family.evidence_bases})
        review_lines = [
            *[
                f"{family.family_label}: family health {family.family_health} · mode {family.family_mode} · {family.loaded_source_count}/{family.source_count} sources loaded"
                for family in export_bundle.families
            ],
            *[line for family in export_bundle.families for line in family.review_lines[:2]],
        ]
        export_lines = [
            f"Environmental context export: {export_bundle.family_count} families · {export_bundle.source_count} sources · mode {export_bundle.metadata.source_mode}",
            *[line for family in export_bundle.families for line in family.export_lines[:2]],
        ]
        return EnvironmentalContextExportPackage(
            metadata=EnvironmentalContextExportPackageMetadata(
                source="environmental-context-export-package",
                source_name="Environmental Context Export Package",
                profile="compact",
                source_mode=export_bundle.metadata.source_mode,
                fetched_at=export_bundle.metadata.fetched_at,
                family_count=export_bundle.family_count,
                source_count=export_bundle.source_count,
                evidence_bases=evidence_bases,
                caveat=_CONTEXT_EXPORT_CAVEAT,
            ),
            snapshot_metadata=EnvironmentalContextExportSnapshotMetadata(
                snapshot_type="environmental-context-export",
                captured_at=export_bundle.metadata.fetched_at,
                requested_family_ids=export_bundle.metadata.requested_family_ids,
                included_family_ids=export_bundle.metadata.included_family_ids,
                missing_family_ids=export_bundle.metadata.missing_family_ids,
                source_mode=export_bundle.metadata.source_mode,
                family_count=export_bundle.family_count,
                source_count=export_bundle.source_count,
            ),
            family_ids=all_family_ids,
            source_ids=all_source_ids,
            family_count=export_bundle.family_count,
            source_count=export_bundle.source_count,
            families=export_bundle.families,
            review_lines=review_lines,
            export_lines=export_lines,
            caveats=[
                _CONTEXT_EXPORT_CAVEAT,
                *export_bundle.caveats,
            ],
        )

    async def get_source_health_issue_queue(
        self,
        *,
        family_ids: list[str] | None = None,
    ) -> EnvironmentalSourceHealthIssueQueuePackage:
        overview = await self.get_overview()
        context_package = await self.get_context_export_package(family_ids=family_ids)
        selected = {family_id for family_id in context_package.snapshot_metadata.included_family_ids}
        overview_families = [
            family for family in overview.families if not selected or family.family_id in selected
        ]
        issues = _build_source_health_issues(
            families=overview_families,
            missing_family_ids=context_package.snapshot_metadata.missing_family_ids,
        )
        review_lines = [
            f"Environmental source-health queue: {len(issues)} issues across {context_package.family_count} families and {context_package.source_count} sources.",
            *[issue.summary_line for issue in issues[:8]],
        ]
        export_lines = [
            f"Environmental source-health issues: {len(issues)}",
            *[line for issue in issues[:6] for line in issue.export_lines[:1]],
        ]
        return EnvironmentalSourceHealthIssueQueuePackage(
            metadata=EnvironmentalSourceHealthIssueQueueMetadata(
                source="environmental-source-health-issue-queue",
                source_name="Environmental Source Health Issue Queue",
                profile="compact",
                source_mode=context_package.metadata.source_mode,
                fetched_at=context_package.metadata.fetched_at,
                issue_count=len(issues),
                family_count=context_package.family_count,
                source_count=context_package.source_count,
                caveat=_ISSUE_QUEUE_CAVEAT,
            ),
            snapshot_metadata=context_package.snapshot_metadata,
            family_ids=context_package.family_ids,
            source_ids=context_package.source_ids,
            family_count=context_package.family_count,
            source_count=context_package.source_count,
            issue_count=len(issues),
            issues=issues,
            review_lines=review_lines,
            export_lines=export_lines,
            caveats=[
                _ISSUE_QUEUE_CAVEAT,
                "Issues are review posture only. They do not imply threat, target status, hazard scoring, impact, damage, or health risk.",
                *context_package.caveats[:2],
            ],
        )

    async def get_situation_snapshot_package(
        self,
        *,
        family_ids: list[str] | None = None,
        profile: Literal["default", "chokepoint-context", "source-health-review"] = "default",
    ) -> EnvironmentalSituationSnapshotPackage:
        overview = await self.get_overview()
        context_package = await self.get_context_export_package(family_ids=family_ids)
        issue_queue = await self.get_source_health_issue_queue(family_ids=family_ids)
        selected = {family_id for family_id in context_package.snapshot_metadata.included_family_ids}
        overview_families = [
            family for family in overview.families if not selected or family.family_id in selected
        ]
        health_mode_summary = [
            f"{family.family_label}: health {family.family_health} · mode {family.family_mode} · bases {', '.join(family.evidence_bases)}"
            for family in overview_families
        ]
        review_lines = [
            f"Environmental situation snapshot: {context_package.family_count} families · {context_package.source_count} sources · {issue_queue.issue_count} issues.",
            *health_mode_summary[:6],
            *issue_queue.review_lines[:6],
        ]
        export_lines = [
            f"Environmental snapshot package: {context_package.family_count} families · {context_package.source_count} sources · {issue_queue.issue_count} issues · profile {profile}",
            *context_package.export_lines[:4],
            *issue_queue.export_lines[:4],
        ]
        caveats = [
            _SITUATION_SNAPSHOT_CAVEAT,
            *context_package.caveats[:2],
            *issue_queue.caveats[:2],
        ]
        profile_review_lines, profile_export_lines, profile_caveats = _profile_lines(
            profile=profile,
            family_count=context_package.family_count,
            issue_count=issue_queue.issue_count,
        )
        return EnvironmentalSituationSnapshotPackage(
            metadata=EnvironmentalSituationSnapshotPackageMetadata(
                source="environmental-situation-snapshot-package",
                source_name="Environmental Situation Snapshot Package",
                profile=profile,
                source_mode=context_package.metadata.source_mode,
                fetched_at=context_package.metadata.fetched_at,
                family_count=context_package.family_count,
                source_count=context_package.source_count,
                issue_count=issue_queue.issue_count,
                evidence_bases=context_package.metadata.evidence_bases,
                caveat=_SITUATION_SNAPSHOT_CAVEAT,
            ),
            snapshot_metadata=context_package.snapshot_metadata,
            family_ids=context_package.family_ids,
            source_ids=context_package.source_ids,
            family_count=context_package.family_count,
            source_count=context_package.source_count,
            issue_count=issue_queue.issue_count,
            families=context_package.families,
            issues=issue_queue.issues,
            health_mode_summary=health_mode_summary,
            review_lines=[*review_lines, *profile_review_lines],
            export_lines=[*export_lines, *profile_export_lines],
            caveats=[*caveats, *profile_caveats],
        )

    async def get_weather_observation_export_bundle(
        self,
        *,
        source_ids: list[str] | None = None,
    ) -> EnvironmentalWeatherObservationExportBundle:
        fetched_at = _utc_now_iso()
        rows = await self._load_weather_observation_rows()
        requested_source_ids = _normalize_family_ids(source_ids)
        selected_rows = _filter_weather_rows(rows, requested_source_ids)
        included_source_ids = [row.source_id for row in selected_rows]
        missing_source_ids = [source_id for source_id in requested_source_ids if source_id not in included_source_ids]
        source_mode = _combined_source_mode([row.source_mode for row in selected_rows or rows])
        review_lines = [
            f"{row.source_label}: health {row.source_health} · mode {row.source_mode} · basis {row.evidence_basis} · {row.loaded_count} records"
            for row in selected_rows
        ]
        export_lines = [
            f"Environmental weather observation export: {len(selected_rows)} sources · mode {source_mode}",
            *[line for row in selected_rows for line in row.export_lines[:2]],
        ]
        return EnvironmentalWeatherObservationExportBundle(
            metadata=EnvironmentalWeatherObservationExportMetadata(
                source="environmental-weather-observation-export-bundle",
                source_name="Environmental Weather Observation Export Bundle",
                source_mode=source_mode,
                fetched_at=fetched_at,
                requested_source_ids=requested_source_ids,
                included_source_ids=included_source_ids,
                missing_source_ids=missing_source_ids,
                source_count=len(selected_rows),
                caveat=_WEATHER_OBSERVATION_EXPORT_CAVEAT,
            ),
            source_count=len(selected_rows),
            sources=[_weather_source_summary(row) for row in selected_rows],
            review_lines=review_lines,
            export_lines=export_lines,
            caveats=[
                _WEATHER_OBSERVATION_EXPORT_CAVEAT,
                "Observation/context weather export lines do not establish hazard, impact, local damage, responsibility, or action recommendations.",
            ],
        )

    async def get_weather_observation_review_queue(
        self,
        *,
        source_ids: list[str] | None = None,
    ) -> EnvironmentalWeatherObservationReviewQueuePackage:
        export_bundle = await self.get_weather_observation_export_bundle(source_ids=source_ids)
        issues = _build_weather_observation_issues(
            rows=[_weather_row_from_summary(item) for item in export_bundle.sources],
            missing_source_ids=export_bundle.metadata.missing_source_ids,
        )
        review_lines = [
            f"Environmental weather observation review queue: {export_bundle.source_count} sources · {len(issues)} issues.",
            *[issue.summary_line for issue in issues[:8]],
        ]
        export_lines = [
            f"Environmental weather observation issues: {len(issues)}",
            *[line for issue in issues[:6] for line in issue.export_lines[:1]],
        ]
        return EnvironmentalWeatherObservationReviewQueuePackage(
            metadata=EnvironmentalWeatherObservationReviewQueueMetadata(
                source="environmental-weather-observation-review-queue",
                source_name="Environmental Weather Observation Review Queue",
                source_mode=export_bundle.metadata.source_mode,
                fetched_at=export_bundle.metadata.fetched_at,
                requested_source_ids=export_bundle.metadata.requested_source_ids,
                included_source_ids=export_bundle.metadata.included_source_ids,
                missing_source_ids=export_bundle.metadata.missing_source_ids,
                source_count=export_bundle.source_count,
                issue_count=len(issues),
                caveat=_WEATHER_OBSERVATION_REVIEW_CAVEAT,
            ),
            source_count=export_bundle.source_count,
            issue_count=len(issues),
            sources=export_bundle.sources,
            issues=issues,
            review_lines=review_lines,
            export_lines=export_lines,
            caveats=[
                _WEATHER_OBSERVATION_REVIEW_CAVEAT,
                *export_bundle.caveats[:1],
            ],
        )

    async def _load_rows(self) -> list[_SourceOverviewRow]:
        return [
            await self._usgs_earthquakes(),
            await self._emsc_seismicportal(),
            await self._orfeus_eida(),
            await self._bmkg_earthquakes(),
            await self._ga_earthquakes(),
            await self._geonet_quakes(),
            await self._eonet(),
            await self._usgs_volcanoes(),
            await self._geonet_volcano_alerts(),
            await self._noaa_global_volcanoes(),
            await self._tsunami(),
            await self._hko_weather(),
            await self._canada_cap(),
            await self._metno_alerts(),
            await self._ipma_warnings(),
            await self._met_eireann_warnings(),
            await self._geosphere_austria_warnings(),
            await self._uk_ea_flood(),
            await self._bc_wildfire_datamart(),
            await self._meteoswiss_open_data(),
            await self._taiwan_cwa(),
            await self._dmi_forecast(),
            await self._met_eireann_forecast(),
            await self._nasa_power(),
            await self._nrc_event_notifications(),
            await self._usgs_geomagnetism(),
            await self._natural_earth(),
            await self._gshhg_shorelines(),
            await self._pb2002_plate_boundaries(),
            await self._france_georisques(),
            await self._ireland_wfd(),
            await self._uk_ea_water_quality(),
        ]

    async def _usgs_earthquakes(self) -> _SourceOverviewRow:
        response = await EarthquakeService(self._settings).list_recent(
            EarthquakeQuery(min_magnitude=None, since=None, limit=25, bbox=None, window="week", sort="newest")
        )
        return _row_from_response(
            family_id="seismic",
            family_label="Seismic",
            source_label="USGS Earthquakes",
            response=response,
            evidence_basis="observed",
            summary_subject="events",
        )

    async def _bmkg_earthquakes(self) -> _SourceOverviewRow:
        response = await BmkgEarthquakesService(self._settings).list_recent(
            BmkgEarthquakesQuery(min_magnitude=5.0, limit=15, sort="newest")
        )
        return _row_from_response(
            family_id="seismic",
            family_label="Seismic",
            source_label="BMKG Earthquakes",
            response=response,
            evidence_basis="source-reported",
            summary_subject="events",
        )

    async def _emsc_seismicportal(self) -> _SourceOverviewRow:
        response = await EmscSeismicPortalRealtimeService(self._settings).list_recent(
            EmscSeismicPortalQuery(min_magnitude=None, limit=15, bbox=None, action="all", sort="newest")
        )
        return _row_from_response(
            family_id="seismic",
            family_label="Seismic",
            source_label="EMSC Seismic Portal Realtime",
            response=response,
            evidence_basis="source-reported",
            summary_subject="events",
        )

    async def _orfeus_eida(self) -> _SourceOverviewRow:
        response = await OrfeusEidaService(self._settings).get_context(
            OrfeusEidaQuery(network=None, station=None, bbox=None, limit=15)
        )
        return _row_from_response(
            family_id="seismic",
            family_label="Seismic",
            source_label="ORFEUS EIDA Federator",
            response=response,
            evidence_basis="reference",
            summary_subject="stations",
        )

    async def _ga_earthquakes(self) -> _SourceOverviewRow:
        response = await GaRecentEarthquakesService(self._settings).list_recent(
            GaRecentEarthquakesQuery(min_magnitude=None, limit=20, bbox=None, sort="newest")
        )
        return _row_from_response(
            family_id="seismic",
            family_label="Seismic",
            source_label="Geoscience Australia Earthquakes",
            response=response,
            evidence_basis="source-reported",
            summary_subject="events",
        )

    async def _geonet_quakes(self) -> _SourceOverviewRow:
        response = await GeoNetService(self._settings).list_recent(
            GeoNetQuery(event_type="quake", min_magnitude=None, alert_level="all", limit=10, bbox=None, sort="newest")
        )
        return _row_from_response(
            family_id="seismic",
            family_label="Seismic",
            source_label="GeoNet Quakes",
            response=response,
            evidence_basis="source-reported",
            summary_subject="quakes",
        )

    async def _eonet(self) -> _SourceOverviewRow:
        response = await EonetService(self._settings).list_recent(
            EonetQuery(category=None, status="all", limit=25, bbox=None, since=None, sort="newest")
        )
        return _row_from_response(
            family_id="environmental-event-context",
            family_label="Environmental Event Context",
            source_label="NASA EONET",
            response=response,
            evidence_basis="contextual",
            summary_subject="events",
        )

    async def _usgs_volcanoes(self) -> _SourceOverviewRow:
        response = await VolcanoService(self._settings).list_recent(
            VolcanoQuery(scope="elevated", alert_level="all", observatory=None, limit=10, bbox=None, sort="alert")
        )
        return _row_from_response(
            family_id="volcano-reference",
            family_label="Volcano and Reference",
            source_label="USGS Volcano Hazards",
            response=response,
            evidence_basis="advisory",
            summary_subject="status records",
        )

    async def _geonet_volcano_alerts(self) -> _SourceOverviewRow:
        response = await GeoNetService(self._settings).list_recent(
            GeoNetQuery(event_type="volcano", min_magnitude=None, alert_level="all", limit=10, bbox=None, sort="alert_level")
        )
        return _row_from_response(
            family_id="volcano-reference",
            family_label="Volcano and Reference",
            source_label="GeoNet Volcano Alerts",
            response=response,
            evidence_basis="advisory",
            summary_subject="alert records",
        )

    async def _noaa_global_volcanoes(self) -> _SourceOverviewRow:
        response = await NoaaGlobalVolcanoService(self._settings).get_context(
            NoaaGlobalVolcanoQuery(q=None, country=None, limit=10, sort="name")
        )
        return _row_from_response(
            family_id="volcano-reference",
            family_label="Volcano and Reference",
            source_label="NOAA Global Volcano Locations",
            response=response,
            evidence_basis="reference",
            summary_subject="reference records",
        )

    async def _tsunami(self) -> _SourceOverviewRow:
        response = await TsunamiService(self._settings).list_recent(
            TsunamiQuery(alert_type="all", source_center="all", limit=10, bbox=None, sort="newest")
        )
        return _row_from_response(
            family_id="tsunami-advisory",
            family_label="Tsunami Advisory",
            source_label="NOAA Tsunami Alerts",
            response=response,
            evidence_basis="advisory",
            summary_subject="alerts",
        )

    async def _hko_weather(self) -> _SourceOverviewRow:
        response = await HkoWeatherService(self._settings).list_recent(
            HkoWeatherQuery(
                warning_type="all",
                limit=10,
                sort="newest",
            )
        )
        return _row_from_response(
            family_id="weather-alert-advisory",
            family_label="Weather Alert Advisory",
            source_label="HKO Open Weather",
            response=response,
            evidence_basis="mixed",
            summary_subject="warning/context records",
        )

    async def _canada_cap(self) -> _SourceOverviewRow:
        response = await CanadaCapService(self._settings).list_recent(
            CanadaCapQuery(
                alert_type="all",
                severity="all",
                province=None,
                limit=10,
                sort="newest",
            )
        )
        return _row_from_response(
            family_id="weather-alert-advisory",
            family_label="Weather Alert Advisory",
            source_label="Canada CAP Alerts",
            response=response,
            evidence_basis="advisory",
            summary_subject="alerts",
        )

    async def _metno_alerts(self) -> _SourceOverviewRow:
        response = await MetNoMetAlertsService(self._settings).list_recent(
            MetNoMetAlertsQuery(
                severity="all",
                alert_type=None,
                limit=10,
                sort="newest",
                bbox=None,
            )
        )
        return _row_from_response(
            family_id="weather-alert-advisory",
            family_label="Weather Alert Advisory",
            source_label="MET Norway MetAlerts",
            response=response,
            evidence_basis="advisory",
            summary_subject="alerts",
        )

    async def _ipma_warnings(self) -> _SourceOverviewRow:
        response = await IpmaWarningsService(self._settings).list_recent(
            IpmaWarningsQuery(
                level="all",
                area_id=None,
                warning_type=None,
                active_only=True,
                limit=10,
                sort="newest",
            )
        )
        return _row_from_response(
            family_id="weather-alert-advisory",
            family_label="Weather Alert Advisory",
            source_label="IPMA Warnings",
            response=response,
            evidence_basis="advisory",
            summary_subject="warnings",
        )

    async def _met_eireann_warnings(self) -> _SourceOverviewRow:
        response = await MetEireannWarningsService(self._settings).list_recent(
            MetEireannWarningsQuery(
                level="all",
                limit=10,
                sort="newest",
            )
        )
        return _row_from_response(
            family_id="weather-alert-advisory",
            family_label="Weather Alert Advisory",
            source_label="Met Eireann Warnings",
            response=response,
            evidence_basis="advisory",
            summary_subject="warnings",
        )

    async def _geosphere_austria_warnings(self) -> _SourceOverviewRow:
        response = await GeosphereAustriaWarningsService(self._settings).list_recent(
            GeosphereAustriaWarningsQuery(
                level="all",
                limit=10,
                sort="newest",
            )
        )
        return _row_from_response(
            family_id="weather-alert-advisory",
            family_label="Weather Alert Advisory",
            source_label="GeoSphere Austria Warnings",
            response=response,
            evidence_basis="advisory",
            summary_subject="warnings",
        )

    async def _uk_ea_flood(self) -> _SourceOverviewRow:
        response = await UkEaFloodService(self._settings).list_recent(
            UkEaFloodQuery(severity="all", area=None, limit=10, bbox=None, include_stations=True, sort="newest")
        )
        return _row_from_response(
            family_id="weather-flood-hydrology",
            family_label="Weather, Flood, and Hydrology",
            source_label="UK EA Flood Monitoring",
            response=response,
            evidence_basis="mixed",
            summary_subject="records",
        )

    async def _bc_wildfire_datamart(self) -> _SourceOverviewRow:
        response = await BcWildfireDatamartService(self._settings).get_context(
            BcWildfireDatamartQuery(station_code=None, fire_centre=None, resource="all", limit=5)
        )
        return _row_from_response(
            family_id="weather-flood-hydrology",
            family_label="Weather, Flood, and Hydrology",
            source_label="BC Wildfire Datamart",
            response=response,
            evidence_basis="contextual",
            summary_subject="fire-weather context records",
        )

    async def _taiwan_cwa(self) -> _SourceOverviewRow:
        response = await TaiwanCwaWeatherService(self._settings).get_context(
            TaiwanCwaWeatherQuery(county=None, station_id=None, limit=10, sort="newest")
        )
        return _row_from_response(
            family_id="weather-flood-hydrology",
            family_label="Weather, Flood, and Hydrology",
            source_label="Taiwan CWA Weather",
            response=response,
            evidence_basis="observed",
            summary_subject="stations",
        )

    async def _meteoswiss_open_data(self) -> _SourceOverviewRow:
        response = await MeteoSwissOpenDataService(self._settings).get_context(
            MeteoSwissOpenDataQuery(station_abbr=None, canton=None, limit=10)
        )
        return _row_from_response(
            family_id="weather-flood-hydrology",
            family_label="Weather, Flood, and Hydrology",
            source_label="MeteoSwiss Open Data",
            response=response,
            evidence_basis="observed",
            summary_subject="station observations",
        )

    async def _dmi_forecast(self) -> _SourceOverviewRow:
        response = await DmiForecastService(self._settings).get_context(
            DmiForecastQuery(latitude=55.715, longitude=12.561, limit=12)
        )
        return _row_from_response(
            family_id="weather-flood-hydrology",
            family_label="Weather, Flood, and Hydrology",
            source_label="DMI Forecast",
            response=response,
            evidence_basis="contextual",
            summary_subject="forecast samples",
        )

    async def _met_eireann_forecast(self) -> _SourceOverviewRow:
        response = await MetEireannForecastService(self._settings).get_context(
            MetEireannForecastQuery(latitude=53.3498, longitude=-6.2603, limit=12)
        )
        return _row_from_response(
            family_id="weather-flood-hydrology",
            family_label="Weather, Flood, and Hydrology",
            source_label="Met Eireann Forecast",
            response=response,
            evidence_basis="forecast",
            summary_subject="forecast samples",
        )

    async def _nasa_power(self) -> _SourceOverviewRow:
        response = await NasaPowerMeteorologySolarService(self._settings).get_context(
            NasaPowerMeteorologySolarQuery(latitude=53.3498, longitude=-6.2603, start="20250101", end="20250103", limit=3)
        )
        return _row_from_response(
            family_id="weather-flood-hydrology",
            family_label="Weather, Flood, and Hydrology",
            source_label="NASA POWER Meteorology Solar",
            response=response,
            evidence_basis="modeled",
            summary_subject="modeled samples",
        )

    async def _nrc_event_notifications(self) -> _SourceOverviewRow:
        response = await NrcEventNotificationsService(self._settings).list_recent(
            NrcEventNotificationsQuery(q=None, limit=10, sort="event_id")
        )
        return _row_from_response(
            family_id="infrastructure-event-context",
            family_label="Infrastructure Event Context",
            source_label="NRC Event Notifications",
            response=response,
            evidence_basis="source-reported",
            summary_subject="notifications",
        )

    async def _usgs_geomagnetism(self) -> _SourceOverviewRow:
        response = await UsgsGeomagnetismService(self._settings).get_context(
            UsgsGeomagnetismQuery(observatory_id="BOU", elements=None)
        )
        return _row_from_response(
            family_id="geomagnetic-context",
            family_label="Geomagnetic Context",
            source_label="USGS Geomagnetism",
            response=response,
            evidence_basis="observed",
            summary_subject="samples",
        )

    async def _natural_earth(self) -> _SourceOverviewRow:
        response = await NaturalEarthPhysicalService(self._settings).get_context(
            NaturalEarthPhysicalQuery(bbox=None, limit=5)
        )
        return _row_from_response(
            family_id="base-earth-reference",
            family_label="Base Earth Reference",
            source_label="Natural Earth Physical Land",
            response=response,
            evidence_basis="reference",
            summary_subject="features",
        )

    async def _gshhg_shorelines(self) -> _SourceOverviewRow:
        response = await GshhgShorelinesService(self._settings).get_context(
            GshhgShorelinesQuery(bbox=None, limit=5)
        )
        return _row_from_response(
            family_id="base-earth-reference",
            family_label="Base Earth Reference",
            source_label="GSHHG Shorelines",
            response=response,
            evidence_basis="reference",
            summary_subject="features",
        )

    async def _pb2002_plate_boundaries(self) -> _SourceOverviewRow:
        response = await Pb2002PlateBoundariesService(self._settings).get_context(
            Pb2002PlateBoundariesQuery(boundary_type=None, bbox=None, limit=5)
        )
        return _row_from_response(
            family_id="base-earth-reference",
            family_label="Base Earth Reference",
            source_label="PB2002 Plate Boundaries",
            response=response,
            evidence_basis="reference",
            summary_subject="boundary records",
        )

    async def _france_georisques(self) -> _SourceOverviewRow:
        response = await FranceGeorisquesService(self._settings).get_context(
            FranceGeorisquesQuery(code_insee="06088", latitude=None, longitude=None, limit=5)
        )
        return _row_from_response(
            family_id="risk-reference",
            family_label="Risk Reference",
            source_label="France Géorisques",
            response=response,
            evidence_basis="reference",
            summary_subject="reference records",
        )

    async def _ireland_wfd(self) -> _SourceOverviewRow:
        response = await IrelandWfdService(self._settings).get_context(IrelandWfdQuery(q=None, limit=10))
        return _row_from_response(
            family_id="risk-reference",
            family_label="Risk Reference",
            source_label="Ireland EPA WFD Catchments",
            response=response,
            evidence_basis="reference",
            summary_subject="reference records",
        )

    async def _uk_ea_water_quality(self) -> _SourceOverviewRow:
        response = await UkEaWaterQualityService(self._settings).get_context(
            UkEaWaterQualityQuery(point_id=None, sample_year=None, district=None, limit=10, sort="newest")
        )
        return _row_from_response(
            family_id="water-quality-context",
            family_label="Water Quality Context",
            source_label="UK EA Water Quality",
            response=response,
            evidence_basis="observed",
            summary_subject="sample assessments",
        )

    async def _load_weather_observation_rows(self) -> list[_WeatherObservationRow]:
        rows = [
            await self._weather_row_meteoswiss(),
            await self._weather_row_bcws(),
            await self._weather_row_taiwan_cwa(),
            await self._weather_row_dmi(),
            await self._weather_row_met_eireann_forecast(),
            await self._weather_row_nasa_power(),
        ]
        ordered: list[_WeatherObservationRow] = []
        row_map = {row.source_id: row for row in rows}
        for source_id in _WEATHER_OBSERVATION_SOURCE_ORDER:
            row = row_map.get(source_id)
            if row is not None:
                ordered.append(row)
        return ordered

    async def _weather_row_meteoswiss(self) -> _WeatherObservationRow:
        response = await MeteoSwissOpenDataService(self._settings).get_context(
            MeteoSwissOpenDataQuery(station_abbr=None, canton=None, limit=10)
        )
        coordinate_count = sum(1 for station in response.stations if station.latitude is not None and station.longitude is not None)
        missing_coordinate_count = max(len(response.stations) - coordinate_count, 0)
        return _build_weather_row(
            source_id=response.metadata.source,
            source_label="MeteoSwiss Open Data",
            source_mode=response.source_health.source_mode,
            source_health=response.source_health.health,
            evidence_basis="observed",
            loaded_count=response.count,
            last_fetched_at=response.source_health.last_fetched_at,
            source_generated_at=response.source_health.source_generated_at,
            coordinate_count=coordinate_count,
            missing_coordinate_count=missing_coordinate_count,
            limited_scope=True,
            export_ready=coordinate_count > 0,
            caveats=response.caveats,
            extra_review_lines=["MeteoSwiss is intentionally bounded to one `t_now` observation asset family plus station metadata."],
        )

    async def _weather_row_bcws(self) -> _WeatherObservationRow:
        response = await BcWildfireDatamartService(self._settings).get_context(
            BcWildfireDatamartQuery(station_code=None, fire_centre=None, resource="all", limit=10)
        )
        coordinate_count = sum(1 for station in response.stations if station.latitude is not None and station.longitude is not None)
        missing_coordinate_count = sum(
            1 for station in response.stations if station.latitude is None or station.longitude is None
        ) + len(response.danger_summaries)
        return _build_weather_row(
            source_id=response.metadata.source,
            source_label="BC Wildfire Datamart",
            source_mode=response.source_health.source_mode,
            source_health=response.source_health.health,
            evidence_basis="contextual",
            loaded_count=response.count,
            last_fetched_at=response.source_health.last_fetched_at,
            source_generated_at=response.source_health.source_generated_at,
            coordinate_count=coordinate_count,
            missing_coordinate_count=missing_coordinate_count,
            limited_scope=True,
            export_ready=coordinate_count > 0,
            caveats=response.caveats,
            extra_review_lines=["BCWS mixes station reference rows with fire-centre danger summaries; danger summaries do not provide point coordinates."],
        )

    async def _weather_row_taiwan_cwa(self) -> _WeatherObservationRow:
        response = await TaiwanCwaWeatherService(self._settings).get_context(
            TaiwanCwaWeatherQuery(county=None, station_id=None, limit=10, sort="newest")
        )
        coordinate_count = sum(1 for station in response.stations if station.latitude is not None and station.longitude is not None)
        missing_coordinate_count = max(len(response.stations) - coordinate_count, 0)
        return _build_weather_row(
            source_id=response.metadata.source,
            source_label="Taiwan CWA Weather",
            source_mode=response.source_health.source_mode,
            source_health=response.source_health.health,
            evidence_basis="observed",
            loaded_count=response.count,
            last_fetched_at=response.source_health.last_fetched_at,
            source_generated_at=response.source_health.source_generated_at,
            coordinate_count=coordinate_count,
            missing_coordinate_count=missing_coordinate_count,
            limited_scope=False,
            export_ready=True,
            caveats=response.caveats,
            extra_review_lines=[],
        )

    async def _weather_row_dmi(self) -> _WeatherObservationRow:
        response = await DmiForecastService(self._settings).get_context(
            DmiForecastQuery(latitude=55.715, longitude=12.561, limit=12)
        )
        return _build_weather_row(
            source_id=response.metadata.source,
            source_label="DMI Forecast",
            source_mode=response.source_health.source_mode,
            source_health=response.source_health.health,
            evidence_basis="contextual",
            loaded_count=response.count,
            last_fetched_at=response.source_health.last_fetched_at,
            source_generated_at=response.source_health.source_generated_at,
            coordinate_count=1,
            missing_coordinate_count=0,
            limited_scope=False,
            export_ready=response.metadata.generated_at is not None or response.metadata.first_forecast_time is not None,
            caveats=response.caveats,
            extra_review_lines=["DMI is point forecast context, not direct observed station weather."],
        )

    async def _weather_row_met_eireann_forecast(self) -> _WeatherObservationRow:
        response = await MetEireannForecastService(self._settings).get_context(
            MetEireannForecastQuery(latitude=53.3498, longitude=-6.2603, limit=12)
        )
        return _build_weather_row(
            source_id=response.metadata.source,
            source_label="Met Eireann Forecast",
            source_mode=response.source_health.source_mode,
            source_health=response.source_health.health,
            evidence_basis="forecast",
            loaded_count=response.count,
            last_fetched_at=response.source_health.last_fetched_at,
            source_generated_at=response.source_health.source_generated_at,
            coordinate_count=1,
            missing_coordinate_count=0,
            limited_scope=False,
            export_ready=response.metadata.first_forecast_time is not None,
            caveats=response.caveats,
            extra_review_lines=["Met Eireann remains forecast/context only and should not be read as observed weather."],
        )

    async def _weather_row_nasa_power(self) -> _WeatherObservationRow:
        response = await NasaPowerMeteorologySolarService(self._settings).get_context(
            NasaPowerMeteorologySolarQuery(latitude=53.3498, longitude=-6.2603, start="20250101", end="20250103", limit=3)
        )
        return _build_weather_row(
            source_id=response.metadata.source,
            source_label="NASA POWER Meteorology Solar",
            source_mode=response.source_health.source_mode,
            source_health=response.source_health.health,
            evidence_basis="modeled",
            loaded_count=response.count,
            last_fetched_at=response.source_health.last_fetched_at,
            source_generated_at=response.source_health.source_generated_at,
            coordinate_count=1,
            missing_coordinate_count=0,
            limited_scope=False,
            export_ready=response.metadata.start_date is not None and response.metadata.end_date is not None,
            caveats=response.caveats,
            extra_review_lines=["NASA POWER values remain modeled/contextual only and should not be treated as direct observed local weather."],
        )


def _row_from_response(
    *,
    family_id: str,
    family_label: str,
    source_label: str,
    response: object,
    evidence_basis: str,
    summary_subject: str,
) -> _SourceOverviewRow:
    metadata = getattr(response, "metadata")
    source_health = getattr(response, "source_health", None)
    source_id = str(getattr(metadata, "source"))
    source_mode = getattr(source_health, "source_mode", None) or getattr(metadata, "source_mode", "unknown")
    loaded_count = int(getattr(source_health, "loaded_count", getattr(response, "count", 0)))
    health = getattr(source_health, "health", "loaded" if loaded_count > 0 else "empty")
    last_fetched_at = getattr(source_health, "last_fetched_at", None) or getattr(metadata, "fetched_at", None)
    source_generated_at = getattr(source_health, "source_generated_at", None) or getattr(metadata, "generated_at", None)
    caveat = getattr(source_health, "caveat", None) or getattr(metadata, "caveat", "No caveat recorded.")
    runtime_status = get_source_runtime_status(source_id)
    runtime_state = runtime_status.state if runtime_status is not None else None
    summary_line = f"{source_label}: {health} · {loaded_count} {summary_subject} · mode {source_mode} · basis {evidence_basis}"
    review_lines = _build_review_lines(
        source_id=source_id,
        source_label=source_label,
        source_mode=source_mode,
        health=health,
        runtime_status=runtime_status,
    )
    export_lines = [summary_line, *review_lines[:2]]
    return _SourceOverviewRow(
        family_id=family_id,
        family_label=family_label,
        source_id=source_id,
        source_label=source_label,
        source_mode=source_mode,
        health=health,
        runtime_state=runtime_state,
        loaded_count=loaded_count,
        evidence_basis=evidence_basis,
        last_fetched_at=last_fetched_at,
        source_generated_at=source_generated_at,
        caveat=caveat,
        summary_line=summary_line,
        review_lines=review_lines,
        export_lines=export_lines,
    )


def _build_review_lines(
    *,
    source_id: str,
    source_label: str,
    source_mode: Literal["fixture", "live", "unknown"],
    health: str,
    runtime_status: SourceRuntimeStatus | None,
) -> list[str]:
    lines: list[str] = []
    if source_mode == "fixture":
        lines.append(f"{source_label}: fixture/local mode; live freshness and live availability are not asserted.")
    elif source_mode == "unknown":
        lines.append(f"{source_label}: source mode is unknown.")

    if health in {"empty", "stale", "error", "disabled", "unknown"}:
        lines.append(f"{source_label}: source health is {health}.")

    if runtime_status is not None and runtime_status.state in {"stale", "degraded", "blocked", "rate-limited", "needs-review", "disabled"}:
        lines.append(f"{source_label}: runtime state is {runtime_status.state}.")
    if source_id in _FREE_TEXT_INERT_SOURCE_IDS:
        lines.append(f"{source_label}: source-provided free text remains inert data only and never changes validation state or workflow behavior.")
    return lines


def _build_family_summaries(rows: list[_SourceOverviewRow]) -> list[EnvironmentalSourceFamilySummary]:
    grouped: dict[str, list[_SourceOverviewRow]] = {}
    for row in rows:
        grouped.setdefault(row.family_id, []).append(row)

    families: list[EnvironmentalSourceFamilySummary] = []
    for family_id in _FAMILY_ORDER:
        items = grouped.get(family_id, [])
        if not items:
            continue
        family_label = items[0].family_label
        family_health = _family_health(items)
        family_mode = _combined_source_mode([item.source_mode for item in items])
        source_ids = [item.source_id for item in items]
        evidence_bases = sorted({item.evidence_basis for item in items})
        loaded_source_count = sum(1 for item in items if item.health == "loaded")
        fixture_source_count = sum(1 for item in items if item.source_mode == "fixture")
        review_lines = [line for item in items for line in item.review_lines]
        export_lines = [
            f"{family_label}: {loaded_source_count}/{len(items)} sources loaded · family health {family_health} · mode {family_mode}",
            *[item.summary_line for item in items],
            *review_lines[:4],
        ]
        caveats = sorted({item.caveat for item in items})
        families.append(
            EnvironmentalSourceFamilySummary(
                family_id=family_id,
                family_label=family_label,
                family_health=family_health,
                family_mode=family_mode,
                source_ids=source_ids,
                evidence_bases=evidence_bases,
                source_count=len(items),
                loaded_source_count=loaded_source_count,
                fixture_source_count=fixture_source_count,
                last_fetched_at=_latest_timestamp([item.last_fetched_at for item in items]),
                source_generated_at=_latest_timestamp([item.source_generated_at for item in items]),
                review_lines=review_lines,
                export_lines=export_lines,
                caveats=caveats,
                sources=[
                    EnvironmentalSourceFamilyMember(
                        family_id=item.family_id,
                        family_label=item.family_label,
                        source_id=item.source_id,
                        source_label=item.source_label,
                        source_mode=item.source_mode,
                        health=item.health,
                        runtime_state=item.runtime_state,
                        loaded_count=item.loaded_count,
                        evidence_basis=item.evidence_basis,
                        last_fetched_at=item.last_fetched_at,
                        source_generated_at=item.source_generated_at,
                        caveat=item.caveat,
                        summary_line=item.summary_line,
                        review_lines=item.review_lines,
                        export_lines=item.export_lines,
                    )
                    for item in items
                ],
            )
        )
    return families


def _normalize_family_ids(values: list[str] | None) -> list[str]:
    if not values:
        return []
    normalized: list[str] = []
    for value in values:
        family_id = value.strip().lower()
        if not family_id or family_id in normalized:
            continue
        normalized.append(family_id)
    return normalized


def _filter_family_summaries(
    families: list[EnvironmentalSourceFamilySummary],
    family_ids: list[str],
) -> list[EnvironmentalSourceFamilySummary]:
    if not family_ids:
        return families
    selected = {family_id for family_id in family_ids}
    return [family for family in families if family.family_id in selected]


def _filter_weather_rows(
    rows: list[_WeatherObservationRow],
    source_ids: list[str],
) -> list[_WeatherObservationRow]:
    if not source_ids:
        return rows
    selected = {source_id for source_id in source_ids}
    return [row for row in rows if row.source_id in selected]


def _build_weather_row(
    *,
    source_id: str,
    source_label: str,
    source_mode: Literal["fixture", "live", "unknown"],
    source_health: Literal["loaded", "empty", "stale", "error", "disabled", "unknown"],
    evidence_basis: str,
    loaded_count: int,
    last_fetched_at: str | None,
    source_generated_at: str | None,
    coordinate_count: int,
    missing_coordinate_count: int,
    limited_scope: bool,
    export_ready: bool,
    caveats: list[str],
    extra_review_lines: list[str],
) -> _WeatherObservationRow:
    summary_line = (
        f"{source_label}: {source_health} · {loaded_count} records · mode {source_mode} · basis {evidence_basis}"
    )
    review_lines = [
        *extra_review_lines,
        *_build_review_lines(
            source_id=source_id,
            source_label=source_label,
            source_mode=source_mode,
            health=source_health,
            runtime_status=get_source_runtime_status(source_id),
        ),
    ]
    if missing_coordinate_count > 0:
        review_lines.append(
            f"{source_label}: {missing_coordinate_count} records or context rows do not carry point coordinates."
        )
    if limited_scope:
        review_lines.append(f"{source_label}: bounded first-slice scope is intentionally limited.")
    if evidence_basis != "observed":
        review_lines.append(f"{source_label}: evidence basis is {evidence_basis}, not direct observed station truth.")
    if not export_ready:
        review_lines.append(f"{source_label}: export readiness is limited by coordinate or timestamp gaps.")
    export_lines = [summary_line, *review_lines[:3]]
    return _WeatherObservationRow(
        source_id=source_id,
        source_label=source_label,
        source_mode=source_mode,
        source_health=source_health,
        evidence_basis=evidence_basis,
        loaded_count=loaded_count,
        last_fetched_at=last_fetched_at,
        source_generated_at=source_generated_at,
        coordinate_count=coordinate_count,
        missing_coordinate_count=missing_coordinate_count,
        limited_scope=limited_scope,
        export_ready=export_ready,
        caveats=caveats,
        review_lines=review_lines,
        export_lines=export_lines,
        summary_line=summary_line,
    )


def _weather_source_summary(row: _WeatherObservationRow) -> EnvironmentalWeatherObservationSourceSummary:
    return EnvironmentalWeatherObservationSourceSummary(
        source_id=row.source_id,
        source_label=row.source_label,
        source_mode=row.source_mode,
        source_health=row.source_health,
        evidence_basis=row.evidence_basis,
        loaded_count=row.loaded_count,
        last_fetched_at=row.last_fetched_at,
        source_generated_at=row.source_generated_at,
        coordinate_count=row.coordinate_count,
        missing_coordinate_count=row.missing_coordinate_count,
        limited_scope=row.limited_scope,
        export_ready=row.export_ready,
        summary_line=row.summary_line,
        review_lines=row.review_lines,
        export_lines=row.export_lines,
        caveats=row.caveats,
    )


def _weather_row_from_summary(summary: EnvironmentalWeatherObservationSourceSummary) -> _WeatherObservationRow:
    return _WeatherObservationRow(
        source_id=summary.source_id,
        source_label=summary.source_label,
        source_mode=summary.source_mode,
        source_health=summary.source_health,
        evidence_basis=summary.evidence_basis,
        loaded_count=summary.loaded_count,
        last_fetched_at=summary.last_fetched_at,
        source_generated_at=summary.source_generated_at,
        coordinate_count=summary.coordinate_count,
        missing_coordinate_count=summary.missing_coordinate_count,
        limited_scope=summary.limited_scope,
        export_ready=summary.export_ready,
        caveats=summary.caveats,
        review_lines=summary.review_lines,
        export_lines=summary.export_lines,
        summary_line=summary.summary_line,
    )


def _build_source_health_issues(
    *,
    families: list[EnvironmentalSourceFamilySummary],
    missing_family_ids: list[str],
) -> list[EnvironmentalSourceHealthIssue]:
    issues: list[EnvironmentalSourceHealthIssue] = []
    for family_id in missing_family_ids:
        issues.append(
            EnvironmentalSourceHealthIssue(
                issue_id=f"missing-family:{family_id}",
                issue_type="missing-family",
                allowed_review_posture="source-health-review-only",
                family_id=family_id,
                family_label=None,
                source_id=None,
                source_label=None,
                source_ids=[],
                source_mode="unknown",
                source_health="unknown",
                evidence_basis="unknown",
                summary_line=f"Requested family `{family_id}` is not included in the current environmental source-family coverage.",
                caveats=[
                    "Missing family ids indicate unavailable overview/export coverage for the requested family filter, not hazard, impact, or threat.",
                ],
                review_lines=[
                    f"Missing family `{family_id}` should be reviewed as a coverage/filter issue only.",
                ],
                export_lines=[
                    f"Missing family: {family_id}",
                ],
            )
        )

    for family in families:
        for source in family.sources:
            source_mode = source.source_mode
            source_health = source.health
            evidence_basis = source.evidence_basis
            common = dict(
                family_id=family.family_id,
                family_label=family.family_label,
                source_id=source.source_id,
                source_label=source.source_label,
                source_ids=[source.source_id],
                source_mode=source_mode,
                source_health=source_health,
                evidence_basis=evidence_basis,
                caveats=[source.caveat, *source.review_lines[:1]],
                review_lines=source.review_lines,
                export_lines=source.export_lines,
            )

            if source_mode == "fixture":
                issues.append(
                    EnvironmentalSourceHealthIssue(
                        issue_id=f"{family.family_id}:{source.source_id}:fixture-only",
                        issue_type="fixture-only",
                        allowed_review_posture="document-and-monitor",
                        summary_line=f"{source.source_label} is running in fixture/local mode only.",
                        **common,
                    )
                )

            if source.source_id in _COUNT_ONLY_SOURCE_IDS:
                issues.append(
                    EnvironmentalSourceHealthIssue(
                        issue_id=f"{family.family_id}:{source.source_id}:count-only-health",
                        issue_type="count-only-health",
                        allowed_review_posture="source-health-review-only",
                        summary_line=f"{source.source_label} currently exposes count-only health in this fusion contract; richer source-health state is not asserted.",
                        **common,
                    )
                )

            health_issue_type = {
                "empty": "source-health-empty",
                "stale": "source-health-stale",
                "error": "source-health-error",
                "disabled": "source-health-disabled",
                "unknown": "source-health-unknown",
            }.get(source_health)
            if health_issue_type is not None:
                issues.append(
                    EnvironmentalSourceHealthIssue(
                        issue_id=f"{family.family_id}:{source.source_id}:{health_issue_type}",
                        issue_type=health_issue_type,
                        allowed_review_posture="source-health-review-only",
                        summary_line=f"{source.source_label} source health is {source_health}.",
                        **common,
                    )
                )

            evidence_issue_type = {
                "advisory": "advisory-only",
                "forecast": "forecast-only",
                "modeled": "modeled-only",
                "reference": "reference-only",
                "contextual": "contextual-only",
            }.get(evidence_basis)
            if evidence_issue_type is not None:
                issues.append(
                    EnvironmentalSourceHealthIssue(
                        issue_id=f"{family.family_id}:{source.source_id}:{evidence_issue_type}",
                        issue_type=evidence_issue_type,
                        allowed_review_posture="document-and-monitor",
                        summary_line=f"{source.source_label} should be reviewed with {evidence_basis} evidence limits visible.",
                        **common,
                    )
                )

    return issues


def _build_weather_observation_issues(
    *,
    rows: list[_WeatherObservationRow],
    missing_source_ids: list[str],
) -> list[EnvironmentalWeatherObservationReviewItem]:
    issues: list[EnvironmentalWeatherObservationReviewItem] = []
    for source_id in missing_source_ids:
        issues.append(
            EnvironmentalWeatherObservationReviewItem(
                issue_id=f"missing-source:{source_id}",
                issue_type="missing-source",
                source_id=source_id,
                source_label=None,
                source_mode="unknown",
                source_health="unknown",
                evidence_basis="unknown",
                summary_line=f"Requested weather/observation source `{source_id}` is not included in the current bounded review bundle.",
                review_lines=[f"Missing weather/observation source `{source_id}` should be reviewed as a coverage/filter issue only."],
                export_lines=[f"Missing weather/observation source: {source_id}"],
                caveats=["Missing source ids are coverage/filter issues only and do not imply hazard, impact, or action relevance."],
            )
        )

    for row in rows:
        common = dict(
            source_id=row.source_id,
            source_label=row.source_label,
            source_mode=row.source_mode,
            source_health=row.source_health,
            evidence_basis=row.evidence_basis,
            review_lines=row.review_lines,
            export_lines=row.export_lines,
            caveats=row.caveats,
        )
        if row.source_mode == "fixture":
            issues.append(
                EnvironmentalWeatherObservationReviewItem(
                    issue_id=f"{row.source_id}:fixture-only",
                    issue_type="fixture-only",
                    summary_line=f"{row.source_label} is running in fixture/local mode only.",
                    **common,
                )
            )

        health_issue_type = {
            "empty": "source-health-empty",
            "stale": "source-health-stale",
            "error": "source-health-error",
            "disabled": "source-health-disabled",
            "unknown": "source-health-unknown",
        }.get(row.source_health)
        if health_issue_type is not None:
            issues.append(
                EnvironmentalWeatherObservationReviewItem(
                    issue_id=f"{row.source_id}:{health_issue_type}",
                    issue_type=health_issue_type,
                    summary_line=f"{row.source_label} source health is {row.source_health}.",
                    **common,
                )
            )

        if row.missing_coordinate_count > 0:
            issues.append(
                EnvironmentalWeatherObservationReviewItem(
                    issue_id=f"{row.source_id}:missing-coordinates",
                    issue_type="missing-coordinates",
                    summary_line=f"{row.source_label} has {row.missing_coordinate_count} records or context rows without point coordinates.",
                    **common,
                )
            )

        if row.limited_scope:
            issues.append(
                EnvironmentalWeatherObservationReviewItem(
                    issue_id=f"{row.source_id}:limited-asset-scope",
                    issue_type="limited-asset-scope",
                    summary_line=f"{row.source_label} is intentionally bounded to a limited asset or product scope in this first slice.",
                    **common,
                )
            )

        if row.evidence_basis != "observed":
            issues.append(
                EnvironmentalWeatherObservationReviewItem(
                    issue_id=f"{row.source_id}:advisory-vs-observation-caveat",
                    issue_type="advisory-vs-observation-caveat",
                    summary_line=f"{row.source_label} should be reviewed with its {row.evidence_basis} evidence limits visible rather than treated as direct observed weather truth.",
                    **common,
                )
            )

        if not row.export_ready:
            issues.append(
                EnvironmentalWeatherObservationReviewItem(
                    issue_id=f"{row.source_id}:export-readiness-gap",
                    issue_type="export-readiness-gap",
                    summary_line=f"{row.source_label} has export-readiness gaps due to coordinate or timestamp limitations in the current bounded slice.",
                    **common,
                )
            )

    return issues


def _profile_lines(
    *,
    profile: Literal["default", "chokepoint-context", "source-health-review"],
    family_count: int,
    issue_count: int,
) -> tuple[list[str], list[str], list[str]]:
    if profile == "chokepoint-context":
        return (
            [
                "Chokepoint-context profile: preserve route-adjacent environmental and reference context only.",
            ],
            [
                f"Chokepoint-context snapshot: {family_count} families reviewed with {issue_count} source-health issues.",
            ],
            [
                "Chokepoint-context profile is review context only and does not prove impact, threat, target status, blockade, evasion, or wrongdoing.",
            ],
        )
    if profile == "source-health-review":
        return (
            [
                "Source-health-review profile: emphasize availability, freshness limits, evidence posture, and coverage gaps only.",
            ],
            [
                f"Source-health-review snapshot: {issue_count} issues across {family_count} families.",
            ],
            [
                "Source-health-review profile is not event significance scoring and does not imply hazard, impact, damage, or health risk.",
            ],
        )
    return (
        [
            "Default profile: compact environmental review context with source-health visibility preserved.",
        ],
        [
            f"Default environmental snapshot: {family_count} families reviewed.",
        ],
        [
            "Default profile is review context only and does not replace source-specific meaning or prove impact, damage, or health risk.",
        ],
    )


def _family_health(rows: list[_SourceOverviewRow]) -> Literal["loaded", "mixed", "empty", "degraded", "unknown"]:
    if any((row.runtime_state in {"degraded", "blocked", "rate-limited"}) or row.health == "error" for row in rows):
        return "degraded"
    if all(row.health == "empty" for row in rows):
        return "empty"
    if all(row.health == "loaded" for row in rows):
        return "loaded"
    if any(row.health in {"stale", "disabled", "unknown", "empty"} for row in rows):
        return "mixed"
    return "unknown"


def _combined_source_mode(
    source_modes: list[Literal["fixture", "live", "unknown"]],
) -> Literal["fixture", "live", "mixed", "unknown"]:
    modes = {mode for mode in source_modes if mode != "unknown"}
    if not modes:
        return "unknown"
    if len(modes) == 1:
        return modes.pop()
    return "mixed"


def _latest_timestamp(values: list[str | None]) -> str | None:
    present = [value for value in values if value]
    if not present:
        return None
    try:
        return max(present, key=lambda value: datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp())
    except ValueError:
        return present[-1]


def _utc_now_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat()
