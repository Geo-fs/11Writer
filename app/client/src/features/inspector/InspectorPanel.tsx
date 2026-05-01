import { useEffect, useMemo, useState } from "react";
import { buildActiveImageryContextFromHud } from "../../lib/imageryContext";
import {
  formatAgeLabel,
  summarizeAircraftActivity,
  summarizeSatelliteActivity
} from "./aerospaceActivity";
import {
  buildAircraftEvidenceSummary,
  buildSatelliteEvidenceSummary
} from "./aerospaceEvidenceSummary";
import {
  buildAircraftSourceHealthSummary,
  buildAerospaceSectionHealthDisplay,
  buildSatelliteSourceHealthSummary
} from "./aerospaceSourceHealth";
import {
  buildAircraftNearbyContextSummary,
  buildSatelliteNearbyContextSummary
} from "./aerospaceNearbyContext";
import { buildAerospaceContextAvailabilitySummary } from "./aerospaceContextAvailability";
import { buildAerospaceContextIssueSummary } from "./aerospaceContextIssues";
import { buildAerospaceExportReadinessSummary } from "./aerospaceExportReadiness";
import { buildAerospaceReviewQueueSummary } from "./aerospaceReviewQueue";
import { buildAerospaceContextReportSummary } from "./aerospaceContextReport";
import { buildAerospaceContextGapQueueSummary } from "./aerospaceContextGapQueue";
import { buildAerospaceCurrentArchiveContextSummary } from "./aerospaceCurrentArchiveContext";
import {
  AEROSPACE_SOURCE_READINESS_BUNDLES,
  buildAerospaceSourceReadinessBundleSummary,
  buildAerospaceSourceReadinessSummary
} from "./aerospaceSourceReadiness";
import { buildAerospaceAirportStatusSummary } from "./aerospaceAirportStatusContext";
import { buildAerospaceGeomagnetismContextSummary } from "./aerospaceGeomagnetismContext";
import {
  AEROSPACE_OPERATIONAL_PRESETS,
  buildAerospaceOperationalContextSummary
} from "./aerospaceOperationalContext";
import { buildAerospaceVaacContextSummary } from "./aerospaceVaacContext";
import { buildAerospaceSpaceContextSummary } from "./aerospaceSpaceContext";
import { buildAerospaceSpaceWeatherArchiveContextSummary } from "./aerospaceSpaceWeatherArchiveContext";
import { buildAerospaceSpaceWeatherContextSummary } from "./aerospaceSpaceWeatherContext";
import {
  buildAerospaceOpenSkyContextSummary
} from "./aerospaceOpenSkyContext";
import { buildAerospaceWeatherContextSummary } from "./aerospaceWeatherContext";
import { AEROSPACE_EXPORT_PROFILES } from "./aerospaceExportProfiles";
import {
  buildAerospaceFocusComputation,
  buildAerospaceFocusHistorySummary,
  buildAerospaceFocusSnapshot
} from "./aerospaceFocusMode";
import { formatRelativeAge, getReplaySnapshot, summarizeTrack } from "../../lib/history";
import {
  useAircraftReferenceLinkQuery,
  useAviationWeatherContextQuery,
  useCameraSourceInventoryQuery,
  useCneosEventsQuery,
  useFaaNasAirportStatusQuery,
  useNearestAirportReferenceQuery,
  useNearestRunwayThresholdReferenceQuery,
  useOpenSkyStatesQuery,
  useNceiSpaceWeatherArchiveQuery,
  useSourceStatusQuery,
  useAnchorageVaacAdvisoriesQuery,
  useUsgsGeomagnetismContextQuery,
  useSwpcSpaceWeatherContextQuery,
  useTokyoVaacAdvisoriesQuery,
  useWashingtonVaacAdvisoriesQuery
} from "../../lib/queries";
import { useAppStore } from "../../lib/store";
import { CaveatBlock, DataBasisBadge, StatusBadge } from "../../components/ui";
import type {
  CameraSourceInventoryEntry,
  ReferenceNearbyItem,
  ReferenceObjectSummary
} from "../../types/api";
import type {
  AircraftEntity,
  CanadaCapAlertEntity,
  CameraEntity,
  EarthquakeEntity,
  EonetEntity,
  GeoNetHazardEntity,
  HkoWeatherEntity,
  MetNoAlertEntity,
  SceneEntity,
  TsunamiAlertEntity,
  UkEaFloodEntity,
  VolcanoEntity
} from "../../types/entities";
import { ImageryContextPanel } from "../imagery";
import { MarineAnomalySection } from "../marine/MarineAnomalySection";
import { getCameraReferenceState } from "../webcams/webcamClustering";

export function InspectorPanel() {
  const entity = useAppStore((state) => state.selectedEntity);
  const aircraftEntities = useAppStore((state) => state.aircraftEntities);
  const satelliteEntities = useAppStore((state) => state.satelliteEntities);
  const cameraEntities = useAppStore((state) => state.cameraEntities);
  const entityHistoryTracks = useAppStore((state) => state.entityHistoryTracks);
  const satellitePassWindows = useAppStore((state) => state.satellitePassWindows);
  const followedEntityId = useAppStore((state) => state.followedEntityId);
  const selectedReplayIndex = useAppStore((state) => state.selectedReplayIndex);
  const selectedAerospaceOperationalPreset = useAppStore(
    (state) => state.selectedAerospaceOperationalPreset
  );
  const selectedAerospaceExportProfile = useAppStore(
    (state) => state.selectedAerospaceExportProfile
  );
  const selectedAerospaceSourceReadinessBundle = useAppStore(
    (state) => state.selectedAerospaceSourceReadinessBundle
  );
  const aerospaceFocus = useAppStore((state) => state.aerospaceFocus);
  const aerospaceFocusHistory = useAppStore((state) => state.aerospaceFocusHistory);
  const hud = useAppStore((state) => state.hud);
  const setFollowedEntityId = useAppStore((state) => state.setFollowedEntityId);
  const setSelectedEntityId = useAppStore((state) => state.setSelectedEntityId);
  const setSelectedReplayIndex = useAppStore((state) => state.setSelectedReplayIndex);
  const setSelectedAerospaceOperationalPreset = useAppStore(
    (state) => state.setSelectedAerospaceOperationalPreset
  );
  const setSelectedAerospaceExportProfile = useAppStore(
    (state) => state.setSelectedAerospaceExportProfile
  );
  const setSelectedAerospaceSourceReadinessBundle = useAppStore(
    (state) => state.setSelectedAerospaceSourceReadinessBundle
  );
  const stepSelectedReplayIndex = useAppStore((state) => state.stepSelectedReplayIndex);
  const setAerospaceFocus = useAppStore((state) => state.setAerospaceFocus);
  const setAerospaceFocusPreset = useAppStore((state) => state.setAerospaceFocusPreset);
  const clearAerospaceFocus = useAppStore((state) => state.clearAerospaceFocus);
  const setAerospaceFocusRelatedEntityIds = useAppStore((state) => state.setAerospaceFocusRelatedEntityIds);
  const recordAerospaceFocusSnapshot = useAppStore((state) => state.recordAerospaceFocusSnapshot);
  const clearAerospaceFocusHistory = useAppStore((state) => state.clearAerospaceFocusHistory);
  const sourceStatusQuery = useSourceStatusQuery();
  const cameraSourceInventoryQuery = useCameraSourceInventoryQuery();
  const [cameraFrameNonce, setCameraFrameNonce] = useState<number>(Date.now());

  const related = useMemo(() => {
    if (!entity) {
      return [];
    }

    return [...aircraftEntities, ...satelliteEntities, ...cameraEntities]
      .filter((item) => item.id !== entity.id)
      .map((item) => ({
        item,
        distanceKm: distanceKm(entity, item),
        relation: item.source === entity.source ? "same source" : relationLabel(entity, item)
      }))
      .sort((left, right) => left.distanceKm - right.distanceKm)
      .slice(0, 4);
  }, [aircraftEntities, cameraEntities, entity, satelliteEntities]);

  const sourceHealth = entity
    ? (sourceStatusQuery.data?.sources ?? []).find(
        (source) =>
          source.name === entity.source ||
          (entity.type === "aircraft" && source.name === "aircraft") ||
          (entity.type === "satellite" && source.name === "satellites")
      )
    : undefined;
  const passWindow = entity?.type === "satellite" ? satellitePassWindows[entity.id] : undefined;
  const isFollowing =
    entity != null && entity.type !== "camera" && followedEntityId === entity.id;
  const historyTrack =
    entity != null && (entity.type === "aircraft" || entity.type === "satellite")
      ? entityHistoryTracks[entity.id] ?? null
      : null;
  const replaySnapshot = getReplaySnapshot(historyTrack, selectedReplayIndex);
  const movementSummary = summarizeTrack(historyTrack);
  const recentTimeline =
    historyTrack?.points.map((point, index) => ({ point, index })).slice(-6).reverse() ?? [];
  const selectedAircraft = entity?.type === "aircraft" ? entity : null;
  const aircraftReferenceQuery = useAircraftReferenceLinkQuery(selectedAircraft);
  const nearestAirportQuery = useNearestAirportReferenceQuery(selectedAircraft);
  const runwayAirportRefId =
    nearestAirportQuery.data?.results[0]?.summary.refId ??
    (aircraftReferenceQuery.data?.primary?.summary.objectType === "airport"
      ? aircraftReferenceQuery.data.primary.summary.refId
      : aircraftReferenceQuery.data?.context?.nearestAirport?.refId ?? null);
  const nearestRunwayQuery = useNearestRunwayThresholdReferenceQuery(
    selectedAircraft,
    runwayAirportRefId
  );
  const nearestAirportCode =
    nearestAirportQuery.data?.results[0]?.summary.primaryCode ??
    (aircraftReferenceQuery.data?.primary?.summary.objectType === "airport"
      ? aircraftReferenceQuery.data.primary.summary.primaryCode ?? null
      : aircraftReferenceQuery.data?.context?.nearestAirport?.primaryCode ?? null);
  const nearestAirportName =
    nearestAirportQuery.data?.results[0]?.summary.canonicalName ??
    (aircraftReferenceQuery.data?.primary?.summary.objectType === "airport"
      ? aircraftReferenceQuery.data.primary.summary.canonicalName
      : aircraftReferenceQuery.data?.context?.nearestAirport?.canonicalName ?? null);
  const aviationWeatherQuery = useAviationWeatherContextQuery({
    airportCode: selectedAircraft ? nearestAirportCode ?? null : null,
    airportName: selectedAircraft ? nearestAirportName ?? null : null,
    airportRefId: selectedAircraft ? runwayAirportRefId : null,
    contextType: "nearest-airport"
  });
  const faaNasStatusQuery = useFaaNasAirportStatusQuery({
    airportCode: selectedAircraft ? nearestAirportCode ?? null : null,
    airportName: selectedAircraft ? nearestAirportName ?? null : null
  });
  const cneosEventsQuery = useCneosEventsQuery({
    enabled: entity?.type === "aircraft" || entity?.type === "satellite",
    eventType: "all",
    limit: 3
  });
  const openSkyStatesQuery = useOpenSkyStatesQuery({
    enabled: selectedAircraft != null,
    icao24: selectedAircraft?.canonicalIds.icao24 ?? null,
    callsign: selectedAircraft?.callsign ?? null,
    limit: 5
  });
  const swpcContextQuery = useSwpcSpaceWeatherContextQuery({
    enabled: entity?.type === "aircraft" || entity?.type === "satellite",
    productType: "all",
    limit: 3
  });
  const nceiSpaceWeatherArchiveQuery = useNceiSpaceWeatherArchiveQuery({
    enabled: entity?.type === "aircraft" || entity?.type === "satellite",
  });
  const washingtonVaacQuery = useWashingtonVaacAdvisoriesQuery({
    enabled: entity?.type === "aircraft" || entity?.type === "satellite",
    limit: 2
  });
  const anchorageVaacQuery = useAnchorageVaacAdvisoriesQuery({
    enabled: entity?.type === "aircraft" || entity?.type === "satellite",
    limit: 2
  });
  const tokyoVaacQuery = useTokyoVaacAdvisoriesQuery({
    enabled: entity?.type === "aircraft" || entity?.type === "satellite",
    limit: 2
  });
  const geomagnetismContextQuery = useUsgsGeomagnetismContextQuery({
    enabled: entity?.type === "aircraft" || entity?.type === "satellite",
    observatoryId: "BOU",
    elements: ["X", "Y", "Z", "F"]
  });
  const aviationWeatherSourceHealth = selectedAircraft
    ? (sourceStatusQuery.data?.sources ?? []).find((source) => source.name === "noaa-awc") ?? null
    : null;
  const faaNasSourceHealth = selectedAircraft
    ? (sourceStatusQuery.data?.sources ?? []).find((source) => source.name === "faa-nas-status") ?? null
    : null;
  const openSkySourceHealth = selectedAircraft
    ? (sourceStatusQuery.data?.sources ?? []).find((source) => source.name === "opensky-anonymous-states") ?? null
    : null;
  const cneosSourceHealth =
    entity?.type === "aircraft" || entity?.type === "satellite"
      ? (sourceStatusQuery.data?.sources ?? []).find((source) => source.name === "cneos-space-events") ?? null
      : null;
  const swpcSourceHealth =
    entity?.type === "aircraft" || entity?.type === "satellite"
      ? (sourceStatusQuery.data?.sources ?? []).find((source) => source.name === "noaa-swpc") ?? null
      : null;
  const nceiSpaceWeatherArchiveSourceHealth =
    entity?.type === "aircraft" || entity?.type === "satellite"
      ? (sourceStatusQuery.data?.sources ?? []).find((source) => source.name === "noaa-ncei-space-weather-portal") ?? null
      : null;
  const washingtonVaacSourceHealth =
    entity?.type === "aircraft" || entity?.type === "satellite"
      ? (sourceStatusQuery.data?.sources ?? []).find((source) => source.name === "washington-vaac") ?? null
      : null;
  const anchorageVaacSourceHealth =
    entity?.type === "aircraft" || entity?.type === "satellite"
      ? (sourceStatusQuery.data?.sources ?? []).find((source) => source.name === "anchorage-vaac") ?? null
      : null;
  const tokyoVaacSourceHealth =
    entity?.type === "aircraft" || entity?.type === "satellite"
      ? (sourceStatusQuery.data?.sources ?? []).find((source) => source.name === "tokyo-vaac") ?? null
      : null;
  const geomagnetismSourceHealth =
    entity?.type === "aircraft" || entity?.type === "satellite"
      ? (sourceStatusQuery.data?.sources ?? []).find((source) => source.name === "usgs-geomagnetism") ?? null
      : null;
  const aviationWeatherSummary = buildAerospaceWeatherContextSummary({
    weather: aviationWeatherQuery.data,
    sourceHealth: aviationWeatherSourceHealth
  });
  const airportStatusSummary = buildAerospaceAirportStatusSummary(faaNasStatusQuery.data);
  const cneosSpaceContextSummary = buildAerospaceSpaceContextSummary({
    context: cneosEventsQuery.data,
    sourceHealth: cneosSourceHealth
  });
  const openSkyContextSummary = buildAerospaceOpenSkyContextSummary({
    response: openSkyStatesQuery.data,
    sourceHealth: openSkySourceHealth,
    selectedAircraft
  });
  const swpcSpaceWeatherSummary = buildAerospaceSpaceWeatherContextSummary({
    context: swpcContextQuery.data,
    sourceHealth: swpcSourceHealth
  });
  const nceiSpaceWeatherArchiveSummary = buildAerospaceSpaceWeatherArchiveContextSummary({
    context: nceiSpaceWeatherArchiveQuery.data,
    sourceHealth: nceiSpaceWeatherArchiveSourceHealth
  });
  const aerospaceCurrentArchiveContextSummary = buildAerospaceCurrentArchiveContextSummary({
    currentSummary: swpcSpaceWeatherSummary,
    archiveSummary: nceiSpaceWeatherArchiveSummary
  });
  const vaacContextSummary = buildAerospaceVaacContextSummary({
    washingtonContext: washingtonVaacQuery.data,
    washingtonSourceHealth: washingtonVaacSourceHealth,
    anchorageContext: anchorageVaacQuery.data,
    anchorageSourceHealth: anchorageVaacSourceHealth,
    tokyoContext: tokyoVaacQuery.data,
    tokyoSourceHealth: tokyoVaacSourceHealth
  });
  const geomagnetismSummary = buildAerospaceGeomagnetismContextSummary({
    context: geomagnetismContextQuery.data,
    sourceHealth: geomagnetismSourceHealth
  });
  const aircraftActivitySummary = selectedAircraft
    ? summarizeAircraftActivity({
        track: historyTrack,
        nearestAirport: nearestAirportQuery.data?.results[0],
        nearestRunway: nearestRunwayQuery.data?.results[0]
      })
    : null;
  const satelliteActivitySummary =
    entity?.type === "satellite"
      ? summarizeSatelliteActivity({
          track: historyTrack,
          replaySnapshot,
          passWindow
        })
      : null;
  const aircraftEvidenceSummary = selectedAircraft
    ? buildAircraftEvidenceSummary({
        entity: selectedAircraft,
        track: historyTrack,
        nearestAirport: nearestAirportQuery.data?.results[0],
        nearestRunway: nearestRunwayQuery.data?.results[0],
        primaryReference: aircraftReferenceQuery.data?.primary ?? null
      })
    : null;
  const satelliteEvidenceSummary =
    entity?.type === "satellite"
      ? buildSatelliteEvidenceSummary({
          entity,
          track: historyTrack,
          replaySnapshot,
          passWindow
        })
      : null;
  const selectedEvidenceSummary = aircraftEvidenceSummary ?? satelliteEvidenceSummary;
  const selectedDataHealthSummary = selectedAircraft
    ? buildAircraftSourceHealthSummary({
        entity: selectedAircraft,
        track: historyTrack,
        sourceHealth: sourceHealth ?? null,
        nearestAirport: nearestAirportQuery.data?.results[0],
        nearestRunway: nearestRunwayQuery.data?.results[0]
      })
    : entity?.type === "satellite"
      ? buildSatelliteSourceHealthSummary({
          entity,
          track: historyTrack,
          sourceHealth: sourceHealth ?? null,
          passWindow
        })
      : null;
  const operationalContextSummary = buildAerospaceOperationalContextSummary({
    presetId: selectedAerospaceOperationalPreset,
    weatherSummary: aviationWeatherSummary,
    airportStatusSummary,
    geomagnetismSummary,
    spaceContextSummary: cneosSpaceContextSummary,
    spaceWeatherSummary: swpcSpaceWeatherSummary,
    spaceWeatherArchiveSummary: nceiSpaceWeatherArchiveSummary,
    vaacContextSummary,
    dataHealthSummary: selectedDataHealthSummary
  });
  const operationalContextAvailabilitySummary = buildAerospaceContextAvailabilitySummary({
    selectedTargetType:
      entity?.type === "aircraft" || entity?.type === "satellite" ? entity.type : null,
    weatherSummary: aviationWeatherSummary,
    weatherSourceHealth: aviationWeatherSourceHealth,
    airportStatusSummary,
    airportStatusSourceHealth: faaNasSourceHealth,
    geomagnetismSummary,
    geomagnetismSourceHealth,
    openSkySummary: openSkyContextSummary,
    openSkySourceHealth,
    spaceContextSummary: cneosSpaceContextSummary,
    spaceWeatherSummary: swpcSpaceWeatherSummary,
    spaceWeatherArchiveSummary: nceiSpaceWeatherArchiveSummary,
    vaacContextSummary,
    dataHealthSummary: selectedDataHealthSummary
  });
  const aerospaceContextIssueSummary = buildAerospaceContextIssueSummary({
    operationalContextSummary,
    availabilitySummary: operationalContextAvailabilitySummary,
    dataHealthSummary: selectedDataHealthSummary,
    openSkySummary: openSkyContextSummary
  });
  const aerospaceExportReadinessSummary = buildAerospaceExportReadinessSummary({
    operationalContextSummary,
    availabilitySummary: operationalContextAvailabilitySummary,
    issueSummary: aerospaceContextIssueSummary,
    dataHealthSummary: selectedDataHealthSummary
  });
  const aerospaceReviewQueueSummary = buildAerospaceReviewQueueSummary({
    issueSummary: aerospaceContextIssueSummary,
    readinessSummary: aerospaceExportReadinessSummary,
    availabilitySummary: operationalContextAvailabilitySummary,
    dataHealthSummary: selectedDataHealthSummary,
    openSkySummary: openSkyContextSummary
  });
  const aerospaceSourceReadinessSummary = buildAerospaceSourceReadinessSummary({
    availabilitySummary: operationalContextAvailabilitySummary,
    issueSummary: aerospaceContextIssueSummary,
    readinessSummary: aerospaceExportReadinessSummary,
    dataHealthSummary: selectedDataHealthSummary
  });
  const aerospaceSourceReadinessBundleSummary = buildAerospaceSourceReadinessBundleSummary({
    summary: aerospaceSourceReadinessSummary,
    bundleId: selectedAerospaceSourceReadinessBundle
  });
  const aerospaceContextGapQueueSummary = buildAerospaceContextGapQueueSummary({
    selectedTargetLabel: selectedEvidenceSummary?.label ?? null,
    exportProfileId: selectedAerospaceExportProfile,
    availabilitySummary: operationalContextAvailabilitySummary,
    sourceReadinessSummary: aerospaceSourceReadinessSummary
  });
  const aerospaceContextReportSummary = buildAerospaceContextReportSummary({
    selectedTargetSummary: selectedEvidenceSummary,
    availabilitySummary: operationalContextAvailabilitySummary,
    reviewQueueSummary: aerospaceReviewQueueSummary,
    readinessSummary: aerospaceExportReadinessSummary,
    dataHealthSummary: selectedDataHealthSummary
  });
  const selectedSectionHealthDisplay = buildAerospaceSectionHealthDisplay(selectedDataHealthSummary);
  const selectedNearbyContextSummary = selectedAircraft
    ? buildAircraftNearbyContextSummary({
        track: historyTrack,
        nearestAirport: nearestAirportQuery.data?.results[0],
        nearestRunway: nearestRunwayQuery.data?.results[0],
        primaryReference: aircraftReferenceQuery.data?.primary ?? null,
        sourceHealth: sourceHealth ?? null
      })
      : entity?.type === "satellite"
        ? buildSatelliteNearbyContextSummary({
            track: historyTrack,
            replaySnapshot,
            passWindow,
            sourceHealth: sourceHealth ?? null
          })
        : null;
  const aerospaceFocusComputation = buildAerospaceFocusComputation({
    focus: aerospaceFocus,
    selectedEntity: entity,
    aircraftEntities,
    satelliteEntities,
    nearbyContextSummary: selectedNearbyContextSummary,
    historyTracks: entityHistoryTracks,
    satellitePassWindows,
    selectedReplayIndex
  });
  const currentFocusSnapshot = useMemo(
    () =>
      aerospaceFocus.enabled
        ? buildAerospaceFocusSnapshot(aerospaceFocusComputation)
        : null,
    [aerospaceFocus.enabled, aerospaceFocusComputation]
  );
  const focusHistorySummary = useMemo(
    () =>
      buildAerospaceFocusHistorySummary({
        current: currentFocusSnapshot,
        history: aerospaceFocusHistory
      }),
    [aerospaceFocusHistory, currentFocusSnapshot]
  );
  const availableAerospaceTargets = useMemo(
    () =>
      new Set(
        [...aircraftEntities, ...satelliteEntities].map((item) => item.id)
      ),
    [aircraftEntities, satelliteEntities]
  );
  const displayedRelated = useMemo(() => {
    if (!entity) {
      return [];
    }
    if (!aerospaceFocus.enabled) {
      return related;
    }

    return [...aircraftEntities, ...satelliteEntities]
      .filter((item) => item.id !== entity.id)
      .filter((item) => aerospaceFocusComputation.relatedEntityIds.includes(item.id))
      .map((item) => ({
        item,
        distanceKm: distanceKm(entity, item),
        relation: item.source === entity.source ? "same source" : relationLabel(entity, item)
      }))
      .sort((left, right) => left.distanceKm - right.distanceKm)
      .slice(0, 6);
  }, [aerospaceFocus.enabled, aerospaceFocusComputation.relatedEntityIds, aircraftEntities, entity, related, satelliteEntities]);
  const imageryContext = buildActiveImageryContextFromHud(hud);
  const cameraSourceInventory =
    entity?.type === "camera"
      ? (cameraSourceInventoryQuery.data?.sources ?? []).find((source) => source.key === entity.source)
      : undefined;

  useEffect(() => {
    const nextIds =
      aerospaceFocus.enabled && aerospaceFocusComputation.relatedEntityIds.length > 0
        ? aerospaceFocusComputation.relatedEntityIds
        : [];
    const currentIds = aerospaceFocus.relatedEntityIds;
    if (currentIds.length === nextIds.length && currentIds.every((value, index) => value === nextIds[index])) {
      return;
    }
    setAerospaceFocusRelatedEntityIds(nextIds);
  }, [
    aerospaceFocus.enabled,
    aerospaceFocus.relatedEntityIds,
    aerospaceFocusComputation.relatedEntityIds,
    setAerospaceFocusRelatedEntityIds
  ]);

  useEffect(() => {
    if (!aerospaceFocus.enabled || !currentFocusSnapshot) {
      return;
    }
    recordAerospaceFocusSnapshot(currentFocusSnapshot);
  }, [aerospaceFocus.enabled, currentFocusSnapshot, recordAerospaceFocusSnapshot]);

  useEffect(() => {
    if (aerospaceFocus.enabled && aerospaceFocus.targetType == null) {
      clearAerospaceFocusHistory();
    }
  }, [aerospaceFocus.enabled, aerospaceFocus.targetType, clearAerospaceFocusHistory]);

  return (
    <aside className="panel panel--right">
      <div className="panel__section">
        <p className="panel__eyebrow">Evidence Inspector</p>
        {!entity ? (
          <div className="empty-state">
            <p>No target selected.</p>
            <span>
              Select an aircraft, satellite, or camera to inspect source attribution, timestamps,
              identifiers, derived values, and nearby context.
            </span>
          </div>
        ) : (
          <div className="data-card">
            <h3>{entity.label}</h3>
            <div className="stack">
              <strong>{entity.sourceDetail ?? entity.source}</strong>
              <span>Observed {formatTimestamp(entity.observedAt ?? entity.timestamp)}</span>
              <span>Fetched {formatTimestamp(entity.fetchedAt ?? entity.timestamp)}</span>
              {entity.quality?.label ? <span>Quality {entity.quality.label}</span> : null}
            </div>
            {entity.type === "aircraft" || entity.type === "satellite" ? (
              <div className="stack stack--actions">
                <button
                  type="button"
                  className="ghost-button"
                  onClick={() => setFollowedEntityId(isFollowing ? null : entity.id)}
                >
                  {isFollowing ? "Stop Following" : "Follow Target"}
                </button>
                {aerospaceFocusComputation.canEnable ? (
                  aerospaceFocus.enabled && aerospaceFocusComputation.targetId === entity.id ? (
                    <button
                      type="button"
                      className="ghost-button"
                      onClick={() => clearAerospaceFocus()}
                    >
                      Clear Aerospace Focus
                    </button>
                  ) : (
                    <button
                      type="button"
                      className="ghost-button"
                      onClick={() =>
                        setAerospaceFocus({
                          targetId: entity.id,
                          targetType: entity.type,
                          presetId: aerospaceFocusComputation.activePresetId,
                          radiusNm: aerospaceFocusComputation.radiusNm,
                          reason: aerospaceFocusComputation.reason
                        })
                      }
                    >
                      Focus Around This Target
                    </button>
                  )
                ) : null}
              </div>
            ) : null}
            {entity.type === "aircraft" || entity.type === "satellite" ? (
              <label className="field-row">
                <span>Focus Mode</span>
                <select
                  className="panel__input"
                  value={aerospaceFocusComputation.activePresetId}
                  onChange={(event) => setAerospaceFocusPreset(event.currentTarget.value as typeof aerospaceFocusComputation.activePresetId)}
                >
                  {aerospaceFocusComputation.presetOptions.map((preset) => (
                    <option key={preset.id} value={preset.id} disabled={!preset.available}>
                      {preset.available ? preset.label : `${preset.label} | Unavailable: ${preset.disabledReason}`}
                    </option>
                  ))}
                </select>
              </label>
            ) : null}
            {(entity.type === "aircraft" || entity.type === "satellite") &&
            (focusHistorySummary.current || aerospaceFocusHistory.length > 0) ? (
              <div className="panel__section">
                <p className="panel__eyebrow">Recent Focus States</p>
                {focusHistorySummary.comparisonLine ? (
                  <div className="data-card data-card--compact">
                    <span>{focusHistorySummary.comparisonLine}</span>
                  </div>
                ) : null}
                <div className="stack">
                  {aerospaceFocusHistory.slice(0, 4).map((snapshot) => {
                    const targetVisible = availableAerospaceTargets.has(snapshot.targetId);
                    const canRestore = targetVisible && snapshot.presetAvailable;
                    return (
                      <div key={`${snapshot.id}:${snapshot.createdAt}`} className="data-card data-card--compact">
                        <strong>
                          {snapshot.presetLabel} | {snapshot.targetLabel ?? snapshot.targetId}
                        </strong>
                        <span>
                          {snapshot.targetType} | {snapshot.relatedTargetCount} related targets
                        </span>
                        <span>
                          {snapshot.presetAvailable
                            ? "Preset available"
                            : `Unavailable: ${snapshot.disabledReason ?? "Preset unavailable"}`}
                        </span>
                        <span>{formatTimestamp(snapshot.createdAt)}</span>
                        <span>{snapshot.reason ?? "selected-target nearby context"}</span>
                        {canRestore ? (
                          <button
                            type="button"
                            className="ghost-button"
                            onClick={() => {
                              setSelectedEntityId(snapshot.targetId);
                              setAerospaceFocus({
                                targetId: snapshot.targetId,
                                targetType: snapshot.targetType,
                                presetId: snapshot.presetId,
                                radiusNm: snapshot.radiusNm,
                                reason: snapshot.reason
                              });
                            }}
                          >
                            Restore Focus State
                          </button>
                        ) : (
                          <span>
                            {targetVisible
                              ? "Restore unavailable until the preset context is available again."
                              : "Restore unavailable because the target is not currently visible."}
                          </span>
                        )}
                      </div>
                    );
                  })}
                </div>
                {aerospaceFocusHistory.length > 0 ? (
                  <div className="stack stack--actions">
                    <button
                      type="button"
                      className="ghost-button"
                      onClick={() => clearAerospaceFocusHistory()}
                    >
                      Clear Focus History
                    </button>
                  </div>
                ) : null}
              </div>
            ) : null}
            <div className="stack stack--actions">
              <button
                type="button"
                className="ghost-button"
                onClick={() =>
                  navigator.clipboard.writeText(
                    entity.type === "camera"
                      ? formatCameraCoordinates(entity)
                      : `${entity.latitude.toFixed(6)}, ${entity.longitude.toFixed(6)}`
                  )
                }
              >
                Copy Coordinates
              </button>
              <button
                type="button"
                className="ghost-button"
                onClick={() => navigator.clipboard.writeText(buildObservationSummary(entity))}
              >
                Copy Summary
              </button>
              {Object.keys(entity.canonicalIds).length > 0 ? (
                <button
                  type="button"
                  className="ghost-button"
                  onClick={() =>
                    navigator.clipboard.writeText(
                      Object.entries(entity.canonicalIds)
                        .map(([key, value]) => `${key}: ${value}`)
                        .join("\n")
                    )
                  }
                >
                  Copy IDs
                </button>
              ) : null}
              {entity.externalUrl ? (
                <a
                  className="ghost-button ghost-button--link"
                  href={entity.externalUrl}
                  target="_blank"
                  rel="noreferrer"
                >
                  Open Source Record
                </a>
              ) : null}
            </div>

            {sourceHealth ? (
              <div className="panel__section">
                <p className="panel__eyebrow">Source Health</p>
                <div className="data-card data-card--compact">
                  <strong>{sourceHealth.name}</strong>
                  <span>Status {sourceHealth.state}</span>
                  <span>
                    Credentials {sourceHealth.credentialsConfigured ? "configured" : "missing"}
                  </span>
                  <span>
                    {sourceHealth.lastSuccessAt
                      ? `Last success ${formatTimestamp(sourceHealth.lastSuccessAt)}`
                      : "No successful fetch yet"}
                  </span>
                  {sourceHealth.lastAttemptAt ? (
                    <span>Last attempt {formatTimestamp(sourceHealth.lastAttemptAt)}</span>
                  ) : null}
                  {sourceHealth.lastFailureAt ? (
                    <span>Last failure {formatTimestamp(sourceHealth.lastFailureAt)}</span>
                  ) : null}
                  {sourceHealth.lastStartedAt ? (
                    <span>Last started {formatTimestamp(sourceHealth.lastStartedAt)}</span>
                  ) : null}
                  {sourceHealth.lastCompletedAt ? (
                    <span>Last completed {formatTimestamp(sourceHealth.lastCompletedAt)}</span>
                  ) : null}
                  {sourceHealth.staleAfterSeconds != null ? (
                    <span>Stale after {sourceHealth.staleAfterSeconds}s</span>
                  ) : null}
                  {sourceHealth.nextRefreshAt ? (
                    <span>Next refresh {formatTimestamp(sourceHealth.nextRefreshAt)}</span>
                  ) : null}
                  {sourceHealth.backoffUntil ? (
                    <span>Backoff until {formatTimestamp(sourceHealth.backoffUntil)}</span>
                  ) : null}
                  {sourceHealth.cadenceSeconds != null ? (
                    <span>
                      Cadence {sourceHealth.cadenceSeconds}s
                      {sourceHealth.cadenceReason ? ` (${sourceHealth.cadenceReason})` : ""}
                    </span>
                  ) : null}
                  {sourceHealth.lastRunMode ? (
                    <span>Last run mode {sourceHealth.lastRunMode}</span>
                  ) : null}
                  {sourceHealth.lastValidationAt ? (
                    <span>Last live validation {formatTimestamp(sourceHealth.lastValidationAt)}</span>
                  ) : null}
                  {sourceHealth.lastFrameProbeCount != null ? (
                    <span>Last frame probes {sourceHealth.lastFrameProbeCount}</span>
                  ) : null}
                  {Object.keys(sourceHealth.lastFrameStatusSummary ?? {}).length > 0 ? (
                    <span>
                      Last frame results{" "}
                      {Object.entries(sourceHealth.lastFrameStatusSummary)
                        .map(([status, count]) => `${status}=${count}`)
                        .join(", ")}
                    </span>
                  ) : null}
                  {sourceHealth.lastMetadataUncertaintyCount != null ? (
                    <span>Metadata uncertainty {sourceHealth.lastMetadataUncertaintyCount}</span>
                  ) : null}
                  {sourceHealth.lastCadenceObservation ? (
                    <span>{sourceHealth.lastCadenceObservation}</span>
                  ) : null}
                  {sourceHealth.successCount != null || sourceHealth.failureCount != null ? (
                    <span>
                      Runs {sourceHealth.successCount ?? 0} ok / {sourceHealth.failureCount ?? 0} failed
                      {sourceHealth.warningCount ? ` / ${sourceHealth.warningCount} warnings` : ""}
                    </span>
                  ) : null}
                  {sourceHealth.lastHttpStatus != null ? (
                    <span>Last HTTP {sourceHealth.lastHttpStatus}</span>
                  ) : null}
                  {sourceHealth.retryCount != null ? (
                    <span>Retry count {sourceHealth.retryCount}</span>
                  ) : null}
                  <span>
                    {sourceHealth.blockedReason ??
                      sourceHealth.degradedReason ??
                      sourceHealth.hiddenReason ??
                      sourceHealth.detail}
                  </span>
                </div>
              </div>
            ) : null}

            {entity.type === "environmental-event" ? (
              <EnvironmentalEventInspectorPanel event={entity} />
            ) : entity.type === "camera" ? (
              <CameraPanel
                camera={entity}
                sourceInventory={cameraSourceInventory}
                frameNonce={cameraFrameNonce}
                onRefreshFrame={() => setCameraFrameNonce(Date.now())}
              />
            ) : (
              <>
                <dl>
                  <div>
                    <dt>ID</dt>
                    <dd>{entity.id}</dd>
                  </div>
                  <div>
                    <dt>Type</dt>
                    <dd>{entity.type}</dd>
                  </div>
                  <div>
                    <dt>Coordinates</dt>
                    <dd>{entity.latitude.toFixed(4)}, {entity.longitude.toFixed(4)}</dd>
                  </div>
                  <div>
                    <dt>Altitude</dt>
                    <dd>{entity.altitude.toFixed(0)} m</dd>
                  </div>
                  <div>
                    <dt>Speed</dt>
                    <dd>{entity.speed != null ? `${entity.speed.toFixed(0)} m/s` : "Unknown"}</dd>
                  </div>
                  <div>
                    <dt>Heading</dt>
                    <dd>{entity.heading != null ? `${entity.heading.toFixed(0)} deg` : "Unknown"}</dd>
                  </div>
                  <div>
                    <dt>Confidence</dt>
                    <dd>
                      {entity.confidence != null
                        ? `${Math.round(entity.confidence * 100)}% normalized`
                        : "Not stated"}
                    </dd>
                  </div>
                  <div>
                    <dt>History</dt>
                    <dd>{entity.historyAvailable ? "Available" : "Unavailable"}</dd>
                  </div>
                </dl>

                {entity.quality ? (
                  <div className="panel__section">
                    <p className="panel__eyebrow">Quality Metadata</p>
                    <div className="data-card data-card--compact">
                      <span>
                        Score {entity.quality.score != null ? entity.quality.score.toFixed(2) : "Unknown"}
                      </span>
                      <span>
                        Freshness {entity.quality.sourceFreshnessSeconds != null
                          ? `${entity.quality.sourceFreshnessSeconds}s`
                          : "Unknown"}
                      </span>
                      {entity.quality.notes.map((note) => (
                        <span key={note}>{note}</span>
                      ))}
                    </div>
                  </div>
                ) : null}

                <div className="panel__section">
                  <p className="panel__eyebrow">Identifiers</p>
                  <div className="stack">
                    {Object.entries(entity.canonicalIds).map(([key, value]) => (
                      <div key={key} className="data-card data-card--compact">
                        <strong>{key}</strong>
                        <span>{value}</span>
                      </div>
                    ))}
                    {Object.entries(entity.rawIdentifiers).map(([key, value]) => (
                      <div key={key} className="data-card data-card--compact">
                        <strong>{key} raw</strong>
                        <span>{value}</span>
                      </div>
                    ))}
                    {Object.entries(entity.canonicalIds).length === 0 &&
                    Object.entries(entity.rawIdentifiers).length === 0 ? (
                      <div className="empty-state compact">
                        <p>No identifiers available.</p>
                      </div>
                    ) : null}
                  </div>
                </div>

                <div className="panel__section">
                  <p className="panel__eyebrow">Derived Fields</p>
                  <div className="stack">
                    {entity.derivedFields.length === 0 ? (
                      <div className="empty-state compact">
                        <p>No derived values.</p>
                      </div>
                    ) : (
                      entity.derivedFields.map((field) => (
                        <div key={`${field.name}-${field.method}`} className="data-card data-card--compact">
                          <strong>{field.name} (Derived)</strong>
                          <span>{field.value}{field.unit ? ` ${field.unit}` : ""}</span>
                          <span>{field.derivedFrom}</span>
                          <span>{field.method}</span>
                        </div>
                      ))
                    )}
                  </div>
                </div>

                <div className="panel__section">
                  <p className="panel__eyebrow">History</p>
                  {entity.historySummary ? (
                    <div className="data-card data-card--compact">
                      <strong>{entity.historySummary.kind}</strong>
                      <span>{entity.historySummary.pointCount} points</span>
                      <span>{entity.historySummary.windowMinutes ?? "?"} minute window</span>
                      <span>
                        {entity.historySummary.lastPointAt
                          ? `Last point ${formatTimestamp(entity.historySummary.lastPointAt)}`
                          : "No last point"}
                      </span>
                      <span>{entity.historySummary.partial ? "Partial history" : "Complete for current window"}</span>
                      <span>{entity.historySummary.detail ?? ""}</span>
                    </div>
                  ) : (
                    <div className="empty-state compact">
                      <p>No history summary.</p>
                    </div>
                  )}
                </div>

                {entity.type === "aircraft" && aircraftActivitySummary ? (
                  <div className="panel__section">
                    <p className="panel__eyebrow">Recent Activity</p>
                    <div className="data-card data-card--compact">
                      <strong>Observed session history / live-polled</strong>
                      <span>Latest observed position age {formatAgeLabel(aircraftActivitySummary.latestObservationAgeSeconds)}</span>
                      <span>{aircraftActivitySummary.sessionPointCount} session points</span>
                      <span>
                        {aircraftActivitySummary.firstObservedAt
                          ? `First observed ${formatTimestamp(aircraftActivitySummary.firstObservedAt)}`
                          : "First observed time unavailable"}
                      </span>
                      <span>
                        {aircraftActivitySummary.latestObservedAt
                          ? `Latest observed ${formatTimestamp(aircraftActivitySummary.latestObservedAt)}`
                          : "Latest observed time unavailable"}
                      </span>
                      <span>
                        {aircraftActivitySummary.sessionDistanceKm != null
                          ? `${aircraftActivitySummary.sessionDistanceKm.toFixed(1)} km covered in session`
                          : "Insufficient session history for distance coverage"}
                      </span>
                      <span>Altitude trend {aircraftActivitySummary.altitudeTrend}</span>
                      <span>Speed trend {aircraftActivitySummary.speedTrend}</span>
                      <span>Heading behavior {aircraftActivitySummary.headingBehavior}</span>
                      <span>{aircraftActivitySummary.nearestAirportRelationship}</span>
                      <span>{aircraftActivitySummary.nearestRunwayRelationship}</span>
                      <span>{aircraftActivitySummary.nearbyAviationContext}</span>
                    </div>
                    {selectedSectionHealthDisplay?.recentActivityCaveat ? (
                      <CaveatBlock heading="Activity caveat" tone="evidence" compact>
                        {selectedSectionHealthDisplay.recentActivityCaveat}
                      </CaveatBlock>
                    ) : null}
                  </div>
                ) : null}

                {entity.type === "satellite" && satelliteActivitySummary ? (
                  <div className="panel__section">
                    <p className="panel__eyebrow">Recent Activity</p>
                    <div className="data-card data-card--compact">
                      <strong>Derived propagated track</strong>
                      <span>Latest derived position age {formatAgeLabel(satelliteActivitySummary.latestPointAgeSeconds)}</span>
                      <span>{satelliteActivitySummary.derivedPointCount} derived track points</span>
                      <span>
                        {satelliteActivitySummary.latestDerivedAt
                          ? `Latest derived point ${formatTimestamp(satelliteActivitySummary.latestDerivedAt)}`
                          : "Latest derived point unavailable"}
                      </span>
                      <span>Replay relation {satelliteActivitySummary.replayRelation}</span>
                      <span>{satelliteActivitySummary.passWindowStatus}</span>
                    </div>
                    {selectedSectionHealthDisplay?.recentActivityCaveat ? (
                      <CaveatBlock heading="Activity caveat" tone="evidence" compact>
                        {selectedSectionHealthDisplay.recentActivityCaveat}
                      </CaveatBlock>
                    ) : null}
                  </div>
                ) : null}

                {selectedEvidenceSummary ? (
                  <div className="panel__section">
                    <p className="panel__eyebrow">Snapshot Evidence</p>
                    <div className="data-card data-card--compact">
                      <strong>{selectedEvidenceSummary.label}</strong>
                      <div className="stack stack--actions">
                        <DataBasisBadge basis={selectedDataHealthSummary?.evidenceBasis ?? "unavailable"} prefix="Basis" />
                        <StatusBadge tone={selectedSectionHealthDisplay?.freshnessBadgeTone ?? freshnessTone(selectedDataHealthSummary?.freshness ?? "unknown")}>
                          Freshness: {selectedSectionHealthDisplay?.freshnessBadgeLabel ?? "unknown"}
                        </StatusBadge>
                      </div>
                      {selectedEvidenceSummary.displayLines.slice(0, 6).map((line) => (
                        <span key={line}>{line}</span>
                      ))}
                      <span>{selectedEvidenceSummary.caveat}</span>
                    </div>
                    {selectedSectionHealthDisplay?.snapshotEvidenceCaveat ? (
                      <CaveatBlock heading="Evidence caveat" tone="evidence" compact>
                        {selectedSectionHealthDisplay.snapshotEvidenceCaveat}
                      </CaveatBlock>
                    ) : null}
                    <ImageryContextPanel
                      context={imageryContext}
                      isReplayContext={selectedReplayIndex != null}
                    />
                  </div>
                ) : null}

                {selectedDataHealthSummary ? (
                  <div className="panel__section">
                    <p className="panel__eyebrow">Data Health</p>
                    <div className="data-card data-card--compact">
                      <div className="stack stack--actions">
                        <DataBasisBadge basis={selectedDataHealthSummary.evidenceBasis} prefix="Basis" />
                        <StatusBadge tone={selectedSectionHealthDisplay?.freshnessBadgeTone ?? freshnessTone(selectedDataHealthSummary.freshness)}>
                          Freshness: {selectedSectionHealthDisplay?.freshnessBadgeLabel ?? selectedDataHealthSummary.freshness}
                        </StatusBadge>
                        <StatusBadge tone={healthTone(selectedDataHealthSummary.health)}>
                          Health: {selectedDataHealthSummary.health}
                        </StatusBadge>
                      </div>
                      {selectedDataHealthSummary.displayLines.map((line) => (
                        <span key={line}>{line}</span>
                      ))}
                      {selectedDataHealthSummary.caveats.slice(0, 3).map((caveat) => (
                        <span key={caveat}>{caveat}</span>
                      ))}
                    </div>
                  </div>
                ) : null}

                {operationalContextSummary ? (
                  <div className="panel__section">
                    <p className="panel__eyebrow">Aerospace Operational Context</p>
                    <label className="field-row">
                      <span>Context preset</span>
                      <select
                        className="panel__input"
                        value={selectedAerospaceOperationalPreset}
                        onChange={(event) =>
                          setSelectedAerospaceOperationalPreset(
                            event.currentTarget.value as typeof selectedAerospaceOperationalPreset
                          )
                        }
                      >
                        {AEROSPACE_OPERATIONAL_PRESETS.map((preset) => (
                          <option key={preset.id} value={preset.id}>
                            {preset.label}
                          </option>
                        ))}
                      </select>
                    </label>
                    <div className="data-card data-card--compact">
                      <strong>
                        {operationalContextSummary.sourceCount} context sources | {operationalContextSummary.healthySourceCount} healthy
                      </strong>
                      <span>Active preset: {operationalContextSummary.presetLabel}</span>
                      <span>
                        Emphasized context: {operationalContextSummary.emphasizedContextTypes.join(", ")}
                      </span>
                      {operationalContextSummary.displayLines.map((line) => (
                        <span key={line}>{line}</span>
                      ))}
                    </div>
                    <CaveatBlock heading="Preset caveat" tone="evidence" compact>
                      {operationalContextSummary.presetCaveat}
                    </CaveatBlock>
                    {operationalContextSummary.caveats.slice(0, 2).map((caveat) => (
                      <CaveatBlock key={caveat} heading="Operational-context caveat" tone="evidence" compact>
                        {caveat}
                      </CaveatBlock>
                    ))}
                    <label className="field-row">
                      <span>Export profile</span>
                      <select
                        className="panel__input"
                        value={selectedAerospaceExportProfile}
                        onChange={(event) =>
                          setSelectedAerospaceExportProfile(
                            event.currentTarget.value as typeof selectedAerospaceExportProfile
                          )
                        }
                      >
                        {AEROSPACE_EXPORT_PROFILES.map((profile) => (
                          <option key={profile.id} value={profile.id}>
                            {profile.label}
                          </option>
                        ))}
                      </select>
                    </label>
                  </div>
                ) : null}

                {operationalContextAvailabilitySummary ? (
                  <div className="panel__section">
                    <p className="panel__eyebrow">Aerospace Context Availability</p>
                    <div className="data-card data-card--compact">
                      <strong>
                        {operationalContextAvailabilitySummary.availableCount} available | {operationalContextAvailabilitySummary.unavailableCount} unavailable/empty | {operationalContextAvailabilitySummary.degradedCount} degraded
                      </strong>
                      <span>Fixture sources: {operationalContextAvailabilitySummary.fixtureSourceCount}</span>
                      {operationalContextAvailabilitySummary.rows.map((row) => (
                        <div key={row.sourceId} className="data-card data-card--compact">
                          <strong>{row.label}</strong>
                          <div className="stack stack--actions">
                            <StatusBadge tone={availabilityTone(row.availability)}>
                              {row.availability}
                            </StatusBadge>
                            <StatusBadge tone={healthTone(normalizeAvailabilityHealth(row.health))}>
                              {row.sourceMode} | {row.health}
                            </StatusBadge>
                            <DataBasisBadge basis={row.evidenceBasis === "advisory" ? "contextual" : row.evidenceBasis} prefix="Basis" />
                          </div>
                          <span>{row.reason}</span>
                          {row.caveat ? <span>{row.caveat}</span> : null}
                        </div>
                      ))}
                    </div>
                  </div>
                ) : null}

                {aerospaceContextIssueSummary ? (
                  <div className="panel__section">
                    <p className="panel__eyebrow">Aerospace Context Review</p>
                    <div className="data-card data-card--compact">
                      <strong>
                        {aerospaceContextIssueSummary.attentionCount} attention | {aerospaceContextIssueSummary.infoCount} informational
                      </strong>
                      {aerospaceContextIssueSummary.displayLines.map((line) => (
                        <span key={line}>{line}</span>
                      ))}
                      {aerospaceContextIssueSummary.topIssues.map((issue) => (
                        <div key={issue.issueId} className="data-card data-card--compact">
                          <strong>{issue.label}</strong>
                          <div className="stack stack--actions">
                            <StatusBadge tone={issueSeverityTone(issue.severity)}>
                              {issue.severity}
                            </StatusBadge>
                            <StatusBadge tone={issueCategoryTone(issue.category)}>
                              {issue.category}
                            </StatusBadge>
                            <DataBasisBadge basis={issue.evidenceBasis === "advisory" ? "contextual" : issue.evidenceBasis} prefix="Basis" />
                          </div>
                          <span>{issue.summary}</span>
                          {issue.caveat ? <span>{issue.caveat}</span> : null}
                        </div>
                      ))}
                    </div>
                    {aerospaceContextIssueSummary.caveats.slice(0, 2).map((caveat) => (
                      <CaveatBlock key={caveat} heading="Review caveat" tone="evidence" compact>
                        {caveat}
                      </CaveatBlock>
                    ))}
                  </div>
                ) : null}

                {aerospaceExportReadinessSummary ? (
                  <div className="panel__section">
                    <p className="panel__eyebrow">Aerospace Export Readiness</p>
                    <div className="data-card data-card--compact">
                      <strong>{aerospaceExportReadinessSummary.label}</strong>
                      <div className="stack stack--actions">
                        <StatusBadge tone={readinessTone(aerospaceExportReadinessSummary.category)}>
                          {aerospaceExportReadinessSummary.category}
                        </StatusBadge>
                        <StatusBadge tone={aerospaceExportReadinessSummary.reviewRecommended ? "warning" : "info"}>
                          {aerospaceExportReadinessSummary.reviewRecommended ? "review recommended" : "export caveated"}
                        </StatusBadge>
                      </div>
                      {aerospaceExportReadinessSummary.displayLines.map((line) => (
                        <span key={line}>{line}</span>
                      ))}
                    </div>
                    {aerospaceExportReadinessSummary.caveats.slice(0, 2).map((caveat) => (
                      <CaveatBlock key={caveat} heading="Readiness caveat" tone="evidence" compact>
                        {caveat}
                      </CaveatBlock>
                    ))}
                  </div>
                ) : null}

                {aerospaceSourceReadinessSummary ? (
                  <div className="panel__section">
                    <p className="panel__eyebrow">Aerospace Source Readiness</p>
                    <label className="field-row">
                      <span>Readiness bundle</span>
                      <select
                        className="panel__input"
                        value={selectedAerospaceSourceReadinessBundle}
                        onChange={(event) =>
                          setSelectedAerospaceSourceReadinessBundle(
                            event.currentTarget.value as typeof selectedAerospaceSourceReadinessBundle
                          )
                        }
                      >
                        {AEROSPACE_SOURCE_READINESS_BUNDLES.map((bundle) => (
                          <option key={bundle.id} value={bundle.id}>
                            {bundle.label}
                          </option>
                        ))}
                      </select>
                    </label>
                    <div className="data-card data-card--compact">
                      <strong>
                        {aerospaceSourceReadinessSummary.familyCount} families | {aerospaceSourceReadinessSummary.reviewRecommendedCount} review recommended
                      </strong>
                      {aerospaceSourceReadinessSummary.displayLines.map((line) => (
                        <span key={line}>{line}</span>
                      ))}
                      {aerospaceSourceReadinessSummary.topFamilies.map((family) => (
                        <div key={family.familyId} className="data-card data-card--compact">
                          <strong>{family.label}</strong>
                          <div className="stack stack--actions">
                            <StatusBadge
                              tone={availabilityTone(
                                family.posture === "mixed"
                                  ? "degraded"
                                  : family.posture === "available"
                                    ? "available"
                                    : family.posture === "unavailable"
                                      ? "unavailable"
                                      : "degraded"
                              )}
                            >
                              {family.posture}
                            </StatusBadge>
                            <StatusBadge tone={family.reviewRecommended ? "warning" : "info"}>
                              {family.readinessLabel}
                            </StatusBadge>
                          </div>
                          <span>{family.summaryLine}</span>
                          {family.sources.map((source) => (
                            <div key={source.sourceId} className="data-card data-card--compact">
                              <strong>{source.label}</strong>
                              <div className="stack stack--actions">
                                <StatusBadge tone={availabilityTone(source.availability)}>
                                  {source.availability}
                                </StatusBadge>
                                <StatusBadge tone={healthTone(normalizeAvailabilityHealth(source.health))}>
                                  {source.sourceMode} | {source.health}
                                </StatusBadge>
                                <DataBasisBadge
                                  basis={source.evidenceBasis === "advisory" ? "contextual" : source.evidenceBasis}
                                  prefix="Basis"
                                />
                              </div>
                              <span>{source.reason}</span>
                              {source.freshnessLabel ? <span>Freshness: {source.freshnessLabel}</span> : null}
                              {source.caveat ? <span>{source.caveat}</span> : null}
                            </div>
                          ))}
                        </div>
                      ))}
                    </div>
                    {aerospaceSourceReadinessBundleSummary ? (
                      <div className="data-card data-card--compact">
                        <strong>{aerospaceSourceReadinessBundleSummary.bundleLabel}</strong>
                        {aerospaceSourceReadinessBundleSummary.displayLines.map((line) => (
                          <span key={line}>{line}</span>
                        ))}
                      </div>
                    ) : null}
                    {aerospaceSourceReadinessSummary.caveats.slice(0, 2).map((caveat) => (
                      <CaveatBlock key={caveat} heading="Source-readiness caveat" tone="evidence" compact>
                        {caveat}
                      </CaveatBlock>
                    ))}
                    {aerospaceSourceReadinessBundleSummary?.caveats.slice(0, 1).map((caveat) => (
                      <CaveatBlock key={caveat} heading="Bundle caveat" tone="evidence" compact>
                        {caveat}
                      </CaveatBlock>
                    ))}
                  </div>
                ) : null}

                {aerospaceContextGapQueueSummary ? (
                  <div className="panel__section">
                    <p className="panel__eyebrow">Aerospace Context Gap Queue</p>
                    <div className="data-card data-card--compact">
                      {aerospaceContextGapQueueSummary.displayLines.map((line) => (
                        <span key={line}>{line}</span>
                      ))}
                      {aerospaceContextGapQueueSummary.topItems.map((item) => (
                        <div key={item.itemId} className="data-card data-card--compact">
                          <strong>{item.familyLabel}</strong>
                          <div className="stack stack--actions">
                            <StatusBadge tone={issueCategoryTone("availability-gap")}>
                              {item.category}
                            </StatusBadge>
                            <StatusBadge tone="info">
                              {item.sourceModes.join(", ") || "unknown mode"}
                            </StatusBadge>
                          </div>
                          <span>{item.summary}</span>
                          <span>Sources: {item.sourceIds.join(", ") || "unavailable"}</span>
                          <span>Health: {item.sourceHealth.join(" | ") || "unknown"}</span>
                          {item.caveat ? <span>{item.caveat}</span> : null}
                        </div>
                      ))}
                    </div>
                    {aerospaceContextGapQueueSummary.caveats.slice(0, 2).map((caveat) => (
                      <CaveatBlock key={caveat} heading="Gap-queue caveat" tone="evidence" compact>
                        {caveat}
                      </CaveatBlock>
                    ))}
                  </div>
                ) : null}

                {aerospaceContextReportSummary ? (
                  <div className="panel__section">
                    <p className="panel__eyebrow">Aerospace Context Report</p>
                    <div className="data-card data-card--compact">
                      {aerospaceContextReportSummary.displayLines.map((line) => (
                        <span key={line}>{line}</span>
                      ))}
                    </div>
                    {aerospaceContextReportSummary.topCaveats.slice(0, 2).map((caveat) => (
                      <CaveatBlock key={caveat} heading="Report caveat" tone="evidence" compact>
                        {caveat}
                      </CaveatBlock>
                    ))}
                    {aerospaceContextReportSummary.limits.slice(0, 2).map((line) => (
                      <CaveatBlock key={line} heading="What this does not prove" tone="evidence" compact>
                        {line}
                      </CaveatBlock>
                    ))}
                  </div>
                ) : null}

                {aerospaceReviewQueueSummary ? (
                  <div className="panel__section">
                    <p className="panel__eyebrow">Aerospace Review Queue</p>
                    <div className="data-card data-card--compact">
                      <strong>
                        {aerospaceReviewQueueSummary.reviewFirstCount} review-first | {aerospaceReviewQueueSummary.reviewCount} review | {aerospaceReviewQueueSummary.noteCount} note
                      </strong>
                      {aerospaceReviewQueueSummary.displayLines.map((line) => (
                        <span key={line}>{line}</span>
                      ))}
                      {aerospaceReviewQueueSummary.topItems.map((item) => (
                        <div key={item.itemId} className="data-card data-card--compact">
                          <strong>{item.label}</strong>
                          <div className="stack stack--actions">
                            <StatusBadge tone={queueBandTone(item.band)}>
                              {item.band}
                            </StatusBadge>
                            <StatusBadge tone={queueCategoryTone(item.category)}>
                              {item.category}
                            </StatusBadge>
                            <DataBasisBadge basis={item.evidenceBasis === "advisory" ? "contextual" : item.evidenceBasis} prefix="Basis" />
                          </div>
                          <span>{item.summary}</span>
                          {item.caveat ? <span>{item.caveat}</span> : null}
                        </div>
                      ))}
                    </div>
                    {aerospaceReviewQueueSummary.caveats.slice(0, 2).map((caveat) => (
                      <CaveatBlock key={caveat} heading="Queue caveat" tone="evidence" compact>
                        {caveat}
                      </CaveatBlock>
                    ))}
                  </div>
                ) : null}

                {aerospaceFocus.enabled ? (
                  <div className="panel__section">
                    <p className="panel__eyebrow">Aerospace Focus</p>
                    <div className="data-card data-card--compact">
                      <strong>{aerospaceFocusComputation.statusLabel}</strong>
                      <span>
                        Preset {aerospaceFocusComputation.activePresetLabel}
                        {aerospaceFocusComputation.activePresetAvailable
                          ? ""
                          : ` | Unavailable: ${aerospaceFocusComputation.activePresetDisabledReason ?? "unavailable"}`}
                      </span>
                      <span>
                        Focus target {aerospaceFocus.targetType ?? "unknown"} {aerospaceFocus.targetId ?? "unknown"}
                      </span>
                      <span>
                        Radius {aerospaceFocus.radiusNm ?? aerospaceFocusComputation.radiusNm ?? "unknown"} nm
                      </span>
                      <span>{aerospaceFocus.reason ?? aerospaceFocusComputation.reason ?? "selected-target nearby context"}</span>
                      <span>{aerospaceFocusComputation.caveat}</span>
                      {!aerospaceFocusComputation.targetVisible ? (
                        <span>Focused target not currently visible.</span>
                      ) : null}
                      {isFollowing ? <span>Follow target is active alongside aerospace focus.</span> : null}
                      {selectedReplayIndex != null ? (
                        <span>Replay cursor remains active while focus mode is enabled.</span>
                      ) : null}
                    </div>
                    {selectedSectionHealthDisplay?.focusModeCaveat ? (
                      <CaveatBlock heading="Focus caveat" tone="evidence" compact>
                        {selectedSectionHealthDisplay.focusModeCaveat}
                      </CaveatBlock>
                    ) : null}
                  </div>
                ) : null}

                <div className="panel__section">
                  <p className="panel__eyebrow">Recent Movement</p>
                  {historyTrack && replaySnapshot && movementSummary ? (
                    <>
                      <div className="data-card data-card--compact">
                        <strong>
                          {historyTrack.semantics === "observed"
                            ? "Observed session trail"
                            : "Derived propagation trail"}
                        </strong>
                        <span>
                          {replaySnapshot.isLive
                            ? "Live point selected"
                            : `Replay point ${replaySnapshot.index + 1} of ${replaySnapshot.totalPoints}`}
                        </span>
                        <span>
                          {replaySnapshot.isLive
                            ? "Showing current live position."
                            : formatRelativeAge(replaySnapshot.ageSeconds)}
                        </span>
                        <span>{historyTrack.detail ?? ""}</span>
                      </div>
                      <div className="stack stack--actions">
                        <button
                          type="button"
                          className="ghost-button"
                          onClick={() => stepSelectedReplayIndex(-1)}
                          disabled={historyTrack.points.length < 2}
                        >
                          Step Back
                        </button>
                        <button
                          type="button"
                          className="ghost-button"
                          onClick={() => stepSelectedReplayIndex(1)}
                          disabled={replaySnapshot.isLive}
                        >
                          Step Forward
                        </button>
                        <button
                          type="button"
                          className="ghost-button"
                          onClick={() => setSelectedReplayIndex(null)}
                          disabled={replaySnapshot.isLive}
                        >
                          Return To Live
                        </button>
                      </div>
                      <label className="field-row">
                        <span>Replay Cursor</span>
                        <input
                          className="panel__input"
                          type="range"
                          min="0"
                          max={Math.max(historyTrack.points.length - 1, 0)}
                          value={replaySnapshot.index}
                          onChange={(event) =>
                            setSelectedReplayIndex(Number(event.currentTarget.value))
                          }
                          disabled={historyTrack.points.length < 2}
                        />
                      </label>
                      <div className="stack">
                        <div className="data-card data-card--compact">
                          <strong>
                            {historyTrack.semantics === "observed"
                              ? "Recent observed movement"
                              : "Recent derived movement"}
                          </strong>
                          <span>
                            {historyTrack.semantics === "observed"
                              ? "Observed session-built movement from live polling."
                              : "Derived movement from propagated orbital elements."}
                          </span>
                        </div>
                        <div className="data-card data-card--compact">
                          <strong>Track Summary</strong>
                          <span>{movementSummary.distanceKm.toFixed(1)} km in current window</span>
                          <span>{movementSummary.durationMinutes.toFixed(1)} minutes covered</span>
                          <span>{movementSummary.altitudeDeltaMeters.toFixed(0)} m altitude delta</span>
                          <span>
                            {movementSummary.averageSpeedMps != null
                              ? `${movementSummary.averageSpeedMps.toFixed(0)} m/s average movement`
                              : "Average movement unavailable"}
                          </span>
                          <span>
                            {movementSummary.headingDeltaDegrees != null
                              ? `${movementSummary.headingDeltaDegrees} deg heading delta`
                              : "Heading delta unavailable"}
                          </span>
                          <span>
                            {movementSummary.latestStatus != null
                              ? `Latest movement state ${movementSummary.latestStatus}`
                              : "No additional movement status in current track"}
                          </span>
                        </div>
                        {recentTimeline.map(({ point, index }) => (
                          <div key={`${point.timestamp}-${index}`} className="data-card data-card--compact">
                            <strong>
                              {index === replaySnapshot.index ? "Selected track point" : "Track point"}
                            </strong>
                            <span>{formatTimestamp(point.timestamp)}</span>
                            <span>
                              {point.latitude.toFixed(4)}, {point.longitude.toFixed(4)} at {point.altitude.toFixed(0)} m
                            </span>
                            <span>
                              {point.speed != null ? `${point.speed.toFixed(0)} m/s` : "Speed unknown"}
                              {" | "}
                              {point.heading != null ? `${point.heading.toFixed(0)} deg` : "Heading unknown"}
                            </span>
                            <span>
                              {historyTrack.semantics === "observed"
                                ? point.status ?? "Observed live poll"
                                : "Derived from propagated orbital elements"}
                            </span>
                          </div>
                        ))}
                      </div>
                    </>
                  ) : (
                    <div className="empty-state compact">
                      <p>No recent movement track.</p>
                      <span>History becomes replayable once the current session accumulates track points.</span>
                    </div>
                  )}
                </div>

                {passWindow ? (
                  <div className="panel__section">
                    <p className="panel__eyebrow">Pass Window (Derived)</p>
                    <div className="data-card data-card--compact">
                      <span>Rise {formatMaybeTimestamp(passWindow.riseAt)}</span>
                      <span>Peak {formatMaybeTimestamp(passWindow.peakAt)}</span>
                      <span>Set {formatMaybeTimestamp(passWindow.setAt)}</span>
                      <span>{passWindow.detail ?? ""}</span>
                    </div>
                  </div>
                ) : null}

                {entity.linkTargets.length > 0 ? (
                  <div className="panel__section">
                    <p className="panel__eyebrow">Link Targets</p>
                    <div className="stack">
                      {entity.linkTargets.map((target) => (
                        <div key={target} className="data-card data-card--compact">
                          <span>{target}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                ) : null}

                {selectedAircraft ? (
                  <AircraftReferenceContextPanel
                    aircraft={selectedAircraft}
                    isLoading={
                      aircraftReferenceQuery.isLoading ||
                      nearestAirportQuery.isLoading ||
                      nearestRunwayQuery.isLoading
                    }
                    primaryReference={aircraftReferenceQuery.data?.primary}
                    containingRegions={aircraftReferenceQuery.data?.context?.containingRegions ?? []}
                    nearestPlace={aircraftReferenceQuery.data?.context?.nearestPlace ?? null}
                    nearestAirport={nearestAirportQuery.data?.results[0]}
                    nearestRunway={nearestRunwayQuery.data?.results[0]}
                    contextCaveat={selectedSectionHealthDisplay?.aviationContextCaveat ?? null}
                  />
                ) : null}

                {selectedAircraft ? (
                  <div className="panel__section">
                    <p className="panel__eyebrow">Aviation Weather (NOAA AWC)</p>
                    {aviationWeatherQuery.isLoading ? (
                      <div className="data-card data-card--compact">
                        <span>Loading airport-context METAR/TAF.</span>
                      </div>
                    ) : aviationWeatherQuery.isError ? (
                      <div className="data-card data-card--compact">
                        <strong>Airport-area weather context unavailable</strong>
                        <span>
                          {aviationWeatherQuery.error instanceof Error
                            ? aviationWeatherQuery.error.message
                            : "NOAA AWC airport-context request failed."}
                        </span>
                        <span>Do not infer flight intent from missing weather context.</span>
                      </div>
                    ) : aviationWeatherSummary ? (
                      <>
                        <div className="data-card data-card--compact">
                          <strong>{aviationWeatherSummary.airportName ?? aviationWeatherSummary.airportCode}</strong>
                          <div className="stack stack--actions">
                            <StatusBadge
                              tone={healthTone(
                                aviationWeatherSourceHealth?.state === "healthy"
                                  ? "normal"
                                  : aviationWeatherSourceHealth?.state === "stale"
                                    ? "stale"
                                    : aviationWeatherSourceHealth?.state === "degraded" ||
                                        aviationWeatherSourceHealth?.state === "rate-limited"
                                      ? "degraded"
                                      : aviationWeatherSourceHealth?.state === "never-fetched"
                                        ? "unknown"
                                        : "partial"
                              )}
                            >
                              Source: {aviationWeatherSummary.sourceHealthState}
                            </StatusBadge>
                            <DataBasisBadge basis="contextual" prefix="Basis" />
                          </div>
                          {aviationWeatherSummary.displayLines.map((line) => (
                            <span key={line}>{line}</span>
                          ))}
                        </div>
                        {aviationWeatherSummary.caveats.slice(0, 3).map((caveat) => (
                          <CaveatBlock key={caveat} heading="Weather caveat" tone="evidence" compact>
                            {caveat}
                          </CaveatBlock>
                        ))}
                      </>
                    ) : (
                      <div className="data-card data-card--compact">
                        <strong>Airport-area weather context unavailable</strong>
                        <span>No nearest-airport weather context is currently loaded.</span>
                      </div>
                    )}
                  </div>
                ) : null}

                {selectedAircraft ? (
                  <div className="panel__section">
                    <p className="panel__eyebrow">Airport Status (FAA NAS)</p>
                    {faaNasStatusQuery.isLoading ? (
                      <div className="data-card data-card--compact">
                        <span>Loading airport operational status context.</span>
                      </div>
                    ) : faaNasStatusQuery.isError ? (
                      <div className="data-card data-card--compact">
                        <strong>Airport operational status unavailable</strong>
                        <span>
                          {faaNasStatusQuery.error instanceof Error
                            ? faaNasStatusQuery.error.message
                            : "FAA NAS airport-status request failed."}
                        </span>
                        <span>Do not infer aircraft intent from missing airport-status context.</span>
                      </div>
                    ) : airportStatusSummary ? (
                      <>
                        <div className="data-card data-card--compact">
                          <strong>{airportStatusSummary.airportName ?? airportStatusSummary.airportCode}</strong>
                          <div className="stack stack--actions">
                            <StatusBadge
                              tone={healthTone(
                                faaNasSourceHealth?.state === "healthy"
                                  ? "normal"
                                  : faaNasSourceHealth?.state === "stale"
                                    ? "stale"
                                    : faaNasSourceHealth?.state === "degraded" ||
                                        faaNasSourceHealth?.state === "rate-limited"
                                      ? "degraded"
                                      : faaNasSourceHealth?.state === "never-fetched"
                                        ? "unknown"
                                        : "partial"
                              )}
                            >
                              Source: {faaNasSourceHealth?.state ?? "unavailable"}
                            </StatusBadge>
                            <DataBasisBadge basis="contextual" prefix="Basis" />
                          </div>
                          {airportStatusSummary.displayLines.map((line) => (
                            <span key={line}>{line}</span>
                          ))}
                        </div>
                        {airportStatusSummary.caveats.slice(0, 3).map((caveat) => (
                          <CaveatBlock key={caveat} heading="Airport-status caveat" tone="evidence" compact>
                            {caveat}
                          </CaveatBlock>
                        ))}
                      </>
                    ) : (
                      <div className="data-card data-card--compact">
                        <strong>Airport operational status unavailable</strong>
                        <span>No nearest-airport FAA NAS context is currently loaded.</span>
                      </div>
                    )}
                  </div>
                ) : null}

                {selectedAircraft ? (
                  <div className="panel__section">
                    <p className="panel__eyebrow">OpenSky Anonymous States</p>
                    {openSkyStatesQuery.isLoading ? (
                      <div className="data-card data-card--compact">
                        <span>Loading optional anonymous OpenSky state-vector context.</span>
                      </div>
                    ) : openSkyStatesQuery.isError ? (
                      <div className="data-card data-card--compact">
                        <strong>Optional OpenSky state-vector context unavailable</strong>
                        <span>
                          {openSkyStatesQuery.error instanceof Error
                            ? openSkyStatesQuery.error.message
                            : "OpenSky anonymous state-vector request failed."}
                        </span>
                        <span>Anonymous OpenSky access is optional, rate-limited, and not guaranteed complete.</span>
                      </div>
                    ) : openSkyContextSummary ? (
                      <>
                        <div className="data-card data-card--compact">
                          <strong>Optional source-reported state vectors</strong>
                          <div className="stack stack--actions">
                            <StatusBadge
                              tone={healthTone(
                                openSkySourceHealth?.state === "healthy"
                                  ? "normal"
                                  : openSkySourceHealth?.state === "stale"
                                    ? "stale"
                                    : openSkySourceHealth?.state === "degraded" ||
                                        openSkySourceHealth?.state === "rate-limited"
                                      ? "degraded"
                                      : openSkySourceHealth?.state === "never-fetched"
                                        ? "unknown"
                                        : "partial"
                              )}
                            >
                              Source: {openSkyContextSummary.sourceState}
                            </StatusBadge>
                            <DataBasisBadge basis="observed" prefix="Basis" />
                          </div>
                          {openSkyContextSummary.displayLines.map((line) => (
                            <span key={line}>{line}</span>
                          ))}
                          <span>
                            Comparison status: {openSkyContextSummary.selectedTargetComparison.matchStatus}
                          </span>
                        </div>
                        {openSkyContextSummary.caveats.slice(0, 3).map((caveat) => (
                          <CaveatBlock key={caveat} heading="OpenSky caveat" tone="evidence" compact>
                            {caveat}
                          </CaveatBlock>
                        ))}
                      </>
                    ) : (
                      <div className="data-card data-card--compact">
                        <strong>Optional OpenSky state-vector context unavailable</strong>
                        <span>No matching anonymous OpenSky context is currently loaded.</span>
                      </div>
                    )}
                  </div>
                ) : null}

                {entity && (entity.type === "aircraft" || entity.type === "satellite") ? (
                  <div className="panel__section">
                    <p className="panel__eyebrow">Geomagnetism (USGS)</p>
                    {geomagnetismContextQuery.isLoading ? (
                      <div className="data-card data-card--compact">
                        <span>Loading contextual observatory geomagnetism values.</span>
                      </div>
                    ) : geomagnetismContextQuery.isError ? (
                      <div className="data-card data-card--compact">
                        <strong>Geomagnetism context unavailable</strong>
                        <span>
                          {geomagnetismContextQuery.error instanceof Error
                            ? geomagnetismContextQuery.error.message
                            : "USGS geomagnetism context request failed."}
                        </span>
                        <span>Do not infer GPS, radio, aircraft, or satellite failure from missing geomagnetism context.</span>
                      </div>
                    ) : geomagnetismSummary ? (
                      <>
                        <div className="data-card data-card--compact">
                          <strong>{geomagnetismSummary.observatoryName ?? geomagnetismSummary.observatoryId}</strong>
                          <div className="stack stack--actions">
                            <StatusBadge
                              tone={healthTone(
                                geomagnetismSourceHealth?.state === "healthy"
                                  ? "normal"
                                  : geomagnetismSourceHealth?.state === "stale"
                                    ? "stale"
                                    : geomagnetismSourceHealth?.state === "degraded" ||
                                        geomagnetismSourceHealth?.state === "rate-limited"
                                      ? "degraded"
                                      : geomagnetismSourceHealth?.state === "never-fetched"
                                        ? "unknown"
                                        : "partial"
                              )}
                            >
                              Source: {geomagnetismSummary.sourceState}
                            </StatusBadge>
                            <DataBasisBadge basis="contextual" prefix="Basis" />
                          </div>
                          {geomagnetismSummary.displayLines.map((line) => (
                            <span key={line}>{line}</span>
                          ))}
                        </div>
                        {geomagnetismSummary.caveats.slice(0, 3).map((caveat) => (
                          <CaveatBlock key={caveat} heading="Geomagnetism caveat" tone="evidence" compact>
                            {caveat}
                          </CaveatBlock>
                        ))}
                      </>
                    ) : (
                      <div className="data-card data-card--compact">
                        <strong>Geomagnetism context unavailable</strong>
                        <span>No observatory geomagnetism context is currently loaded.</span>
                      </div>
                    )}
                  </div>
                ) : null}

                {entity && (entity.type === "aircraft" || entity.type === "satellite") ? (
                  <div className="panel__section">
                    <p className="panel__eyebrow">Space Events (NASA/JPL CNEOS)</p>
                    {cneosEventsQuery.isLoading ? (
                      <div className="data-card data-card--compact">
                        <span>Loading contextual close-approach and fireball records.</span>
                      </div>
                    ) : cneosEventsQuery.isError ? (
                      <div className="data-card data-card--compact">
                        <strong>Space-event context unavailable</strong>
                        <span>
                          {cneosEventsQuery.error instanceof Error
                            ? cneosEventsQuery.error.message
                            : "NASA/JPL CNEOS context request failed."}
                        </span>
                        <span>Do not infer impact risk from missing CNEOS context.</span>
                      </div>
                    ) : cneosSpaceContextSummary ? (
                      <>
                        <div className="data-card data-card--compact">
                          <strong>Close approaches and fireballs</strong>
                          <div className="stack stack--actions">
                            <StatusBadge
                              tone={healthTone(
                                cneosSourceHealth?.state === "healthy"
                                  ? "normal"
                                  : cneosSourceHealth?.state === "stale"
                                    ? "stale"
                                    : cneosSourceHealth?.state === "degraded" ||
                                        cneosSourceHealth?.state === "rate-limited"
                                      ? "degraded"
                                      : cneosSourceHealth?.state === "never-fetched"
                                        ? "unknown"
                                        : "partial"
                              )}
                            >
                              Source: {cneosSpaceContextSummary.sourceState}
                            </StatusBadge>
                            <DataBasisBadge basis="contextual" prefix="Basis" />
                          </div>
                          {cneosSpaceContextSummary.displayLines.map((line) => (
                            <span key={line}>{line}</span>
                          ))}
                        </div>
                        {cneosSpaceContextSummary.caveats.slice(0, 3).map((caveat) => (
                          <CaveatBlock key={caveat} heading="Space-context caveat" tone="evidence" compact>
                            {caveat}
                          </CaveatBlock>
                        ))}
                      </>
                    ) : (
                      <div className="data-card data-card--compact">
                        <strong>Space-event context unavailable</strong>
                        <span>No NASA/JPL CNEOS close-approach or fireball context is currently loaded.</span>
                      </div>
                    )}
                  </div>
                ) : null}

                {entity && (entity.type === "aircraft" || entity.type === "satellite") ? (
                  <div className="panel__section">
                    <p className="panel__eyebrow">Space Weather (NOAA SWPC)</p>
                    {swpcContextQuery.isLoading ? (
                      <div className="data-card data-card--compact">
                        <span>Loading contextual space-weather summaries and advisories.</span>
                      </div>
                    ) : swpcContextQuery.isError ? (
                      <div className="data-card data-card--compact">
                        <strong>Space-weather context unavailable</strong>
                        <span>
                          {swpcContextQuery.error instanceof Error
                            ? swpcContextQuery.error.message
                            : "NOAA SWPC context request failed."}
                        </span>
                        <span>Do not infer satellite, GPS, or radio failure from missing SWPC context.</span>
                      </div>
                    ) : swpcSpaceWeatherSummary ? (
                      <>
                        <div className="data-card data-card--compact">
                          <strong>Space-weather advisories and scales</strong>
                          <div className="stack stack--actions">
                            <StatusBadge
                              tone={healthTone(
                                swpcSourceHealth?.state === "healthy"
                                  ? "normal"
                                  : swpcSourceHealth?.state === "stale"
                                    ? "stale"
                                    : swpcSourceHealth?.state === "degraded" ||
                                        swpcSourceHealth?.state === "rate-limited"
                                      ? "degraded"
                                      : swpcSourceHealth?.state === "never-fetched"
                                        ? "unknown"
                                        : "partial"
                              )}
                            >
                              Source: {swpcSpaceWeatherSummary.sourceState}
                            </StatusBadge>
                            <DataBasisBadge basis="contextual" prefix="Basis" />
                          </div>
                          {swpcSpaceWeatherSummary.displayLines.map((line) => (
                            <span key={line}>{line}</span>
                          ))}
                        </div>
                        {swpcSpaceWeatherSummary.caveats.slice(0, 3).map((caveat) => (
                          <CaveatBlock key={caveat} heading="Space-weather caveat" tone="evidence" compact>
                            {caveat}
                          </CaveatBlock>
                        ))}
                      </>
                    ) : (
                      <div className="data-card data-card--compact">
                        <strong>Space-weather context unavailable</strong>
                        <span>No NOAA SWPC summary or advisory context is currently loaded.</span>
                      </div>
                    )}
                  </div>
                ) : null}

                {entity && (entity.type === "aircraft" || entity.type === "satellite") ? (
                  <div className="panel__section">
                    <p className="panel__eyebrow">Space Weather Archive Context</p>
                    {nceiSpaceWeatherArchiveQuery.isLoading ? (
                      <div className="data-card data-card--compact">
                        <span>Loading archival space-weather collection metadata.</span>
                      </div>
                    ) : nceiSpaceWeatherArchiveQuery.isError ? (
                      <div className="data-card data-card--compact">
                        <strong>Archive context unavailable</strong>
                        <span>
                          {nceiSpaceWeatherArchiveQuery.error instanceof Error
                            ? nceiSpaceWeatherArchiveQuery.error.message
                            : "NOAA NCEI archive context request failed."}
                        </span>
                        <span>Do not treat missing archive metadata as proof of current SWPC conditions.</span>
                      </div>
                    ) : nceiSpaceWeatherArchiveSummary ? (
                      <>
                        <div className="data-card data-card--compact">
                          <strong>Archived collection metadata</strong>
                          <div className="stack stack--actions">
                            <StatusBadge
                              tone={healthTone(
                                nceiSpaceWeatherArchiveSourceHealth?.state === "healthy"
                                  ? "normal"
                                  : nceiSpaceWeatherArchiveSourceHealth?.state === "stale"
                                    ? "stale"
                                    : nceiSpaceWeatherArchiveSourceHealth?.state === "degraded" ||
                                        nceiSpaceWeatherArchiveSourceHealth?.state === "rate-limited"
                                      ? "degraded"
                                      : nceiSpaceWeatherArchiveSourceHealth?.state === "never-fetched"
                                        ? "unknown"
                                        : "partial"
                              )}
                            >
                              Source: {nceiSpaceWeatherArchiveSummary.sourceState}
                            </StatusBadge>
                            <DataBasisBadge basis="contextual" prefix="Basis" />
                          </div>
                          {nceiSpaceWeatherArchiveSummary.displayLines.map((line) => (
                            <span key={line}>{line}</span>
                          ))}
                        </div>
                        {nceiSpaceWeatherArchiveSummary.caveats.slice(0, 3).map((caveat) => (
                          <CaveatBlock key={caveat} heading="Archive caveat" tone="evidence" compact>
                            {caveat}
                          </CaveatBlock>
                        ))}
                      </>
                    ) : (
                      <div className="data-card data-card--compact">
                        <strong>Archive context unavailable</strong>
                        <span>No NOAA NCEI space-weather archive metadata is currently loaded.</span>
                      </div>
                    )}
                  </div>
                ) : null}

                {entity && (entity.type === "aircraft" || entity.type === "satellite") && aerospaceCurrentArchiveContextSummary ? (
                  <div className="panel__section">
                    <p className="panel__eyebrow">Current vs Archive Space-Weather Context</p>
                    <div className="data-card data-card--compact">
                      <strong>{aerospaceCurrentArchiveContextSummary.displayLines[0]}</strong>
                      <div className="stack stack--actions">
                        <StatusBadge tone="info">
                          {aerospaceCurrentArchiveContextSummary.separationState}
                        </StatusBadge>
                        <DataBasisBadge basis="contextual" prefix="Current/archive basis" />
                      </div>
                      {aerospaceCurrentArchiveContextSummary.displayLines.slice(1).map((line) => (
                        <span key={line}>{line}</span>
                      ))}
                    </div>
                    {aerospaceCurrentArchiveContextSummary.caveats.slice(0, 2).map((caveat) => (
                      <CaveatBlock key={caveat} heading="Separation caveat" tone="evidence" compact>
                        {caveat}
                      </CaveatBlock>
                    ))}
                  </div>
                ) : null}

                {entity && (entity.type === "aircraft" || entity.type === "satellite") ? (
                  <div className="panel__section">
                    <p className="panel__eyebrow">Volcanic Ash Advisory Context</p>
                    {washingtonVaacQuery.isLoading || anchorageVaacQuery.isLoading || tokyoVaacQuery.isLoading ? (
                      <div className="data-card data-card--compact">
                        <span>Loading contextual VAAC advisory summaries.</span>
                      </div>
                    ) : washingtonVaacQuery.isError || anchorageVaacQuery.isError || tokyoVaacQuery.isError ? (
                      <div className="data-card data-card--compact">
                        <strong>Volcanic-ash advisory context unavailable</strong>
                        <span>
                          {[
                            washingtonVaacQuery.error,
                            anchorageVaacQuery.error,
                            tokyoVaacQuery.error
                          ]
                            .find((error): error is Error => error instanceof Error)
                            ?.message ?? "One or more VAAC advisory requests failed."}
                        </span>
                        <span>
                          Do not infer route impact, aircraft exposure, or engine risk from missing VAAC context.
                        </span>
                      </div>
                    ) : vaacContextSummary ? (
                      <>
                        <div className="data-card data-card--compact">
                          <strong>Contextual volcanic-ash advisories</strong>
                          <div className="stack stack--actions">
                            <StatusBadge
                              tone={
                                vaacContextSummary.healthySourceCount === vaacContextSummary.sourceCount
                                  ? "success"
                                  : vaacContextSummary.availableSourceCount > 0
                                    ? "warning"
                                    : "neutral"
                              }
                            >
                              Sources: {vaacContextSummary.availableSourceCount}/{vaacContextSummary.sourceCount} with records
                            </StatusBadge>
                            <DataBasisBadge basis="advisory" prefix="Basis" />
                          </div>
                          {vaacContextSummary.displayLines.map((line) => (
                            <span key={line}>{line}</span>
                          ))}
                        </div>
                        {vaacContextSummary.sources.slice(0, 3).map((source) => (
                          <div key={source.sourceId} className="data-card data-card--compact">
                            <strong>{source.label}</strong>
                            <div className="stack stack--actions">
                              <StatusBadge
                                tone={healthTone(
                                  source.sourceState === "healthy"
                                    ? "normal"
                                    : source.sourceState === "stale"
                                      ? "stale"
                                      : source.sourceState === "degraded" ||
                                          source.sourceState === "rate-limited"
                                        ? "degraded"
                                        : "partial"
                                )}
                              >
                                {source.sourceMode} | {source.sourceState}
                              </StatusBadge>
                              <DataBasisBadge
                                basis={source.topAdvisory?.evidenceBasis === "source-reported" ? "contextual" : "advisory"}
                                prefix="Basis"
                              />
                            </div>
                            <span>Listing: {source.listingSourceUrl}</span>
                            <span>Advisories: {source.advisoryCount}</span>
                            <span>
                              {source.topAdvisory
                                ? `${source.topAdvisory.volcanoName} | ${source.topAdvisory.issueTime ?? "issue time unavailable"}`
                                : "No advisory records in the current source window."}
                            </span>
                            {source.topAdvisory?.summaryText ? (
                              <span>{source.topAdvisory.summaryText}</span>
                            ) : null}
                          </div>
                        ))}
                        {vaacContextSummary.caveats.slice(0, 3).map((caveat) => (
                          <CaveatBlock key={caveat} heading="VAAC caveat" tone="evidence" compact>
                            {caveat}
                          </CaveatBlock>
                        ))}
                        {vaacContextSummary.doesNotProve.slice(0, 2).map((line) => (
                          <CaveatBlock key={line} heading="Does not prove" tone="evidence" compact>
                            {line}
                          </CaveatBlock>
                        ))}
                      </>
                    ) : (
                      <div className="data-card data-card--compact">
                        <strong>Volcanic-ash advisory context unavailable</strong>
                        <span>No aerospace-local VAAC advisory context is currently loaded.</span>
                      </div>
                    )}
                  </div>
                ) : null}

                {selectedNearbyContextSummary ? (
                  <div className="panel__section">
                    <p className="panel__eyebrow">Nearby Aerospace Context</p>
                    <div className="stack">
                      {selectedNearbyContextSummary.cards.map((card) => (
                        <div key={`${card.kind}-${card.label}`} className="data-card data-card--compact">
                          <strong>{card.label}</strong>
                          <span>{card.value}</span>
                          <span>{card.detail}</span>
                          <span>Confidence {card.confidence}</span>
                          <span>{card.caveat}</span>
                        </div>
                      ))}
                      {selectedNearbyContextSummary.futureProviderSlots.map((slot) => (
                        <div key={slot.kind} className="data-card data-card--compact">
                          <strong>{slot.label}</strong>
                          <span>{slot.value}</span>
                          <span>{slot.detail}</span>
                          <span>Confidence {slot.confidence}</span>
                          <span>{slot.caveat}</span>
                        </div>
                      ))}
                      {selectedNearbyContextSummary.caveats.map((caveat) => (
                        <div key={caveat} className="data-card data-card--compact">
                          <strong>Context note</strong>
                          <span>{caveat}</span>
                        </div>
                      ))}
                      {selectedNearbyContextSummary.missingProviders.length > 0 ? (
                        <div className="data-card data-card--compact">
                          <strong>Missing provider families</strong>
                          <span>{selectedNearbyContextSummary.missingProviders.join(", ")}</span>
                        </div>
                      ) : null}
                    </div>
                  </div>
                ) : null}
              </>
            )}

            {displayedRelated.length > 0 ? (
              <div className="panel__section">
                <p className="panel__eyebrow">Nearby Targets</p>
                <div className="stack">
                  {displayedRelated.map(({ item, distanceKm, relation }) => (
                    <div key={item.id} className="data-card data-card--compact">
                      <strong>{item.label}</strong>
                      {aerospaceFocus.enabled ? <span>Aerospace focus related</span> : null}
                      <span>{relation}</span>
                      <span>{distanceKm.toFixed(1)} km away</span>
                        </div>
                      ))}
                    </div>
                    {selectedSectionHealthDisplay?.nearbyContextCaveat ? (
                      <CaveatBlock heading="Nearby context caveat" tone="evidence" compact>
                        {selectedSectionHealthDisplay.nearbyContextCaveat}
                      </CaveatBlock>
                    ) : null}
                  </div>
                ) : null}
          </div>
        )}
        <MarineAnomalySection />
      </div>
    </aside>
  );
}

function AircraftReferenceContextPanel({
  aircraft,
  isLoading,
  primaryReference,
  containingRegions,
  nearestPlace,
  nearestAirport,
  nearestRunway,
  contextCaveat
}: {
  aircraft: AircraftEntity;
  isLoading: boolean;
  primaryReference?: {
    summary: ReferenceObjectSummary;
    confidence: number;
    method: string;
    reason: string;
  } | null;
  containingRegions: ReferenceObjectSummary[];
  nearestPlace: ReferenceObjectSummary | null;
  nearestAirport?: ReferenceNearbyItem;
  nearestRunway?: ReferenceNearbyItem;
  contextCaveat?: string | null;
}) {
  const hasContext =
    primaryReference != null ||
    nearestAirport != null ||
    nearestRunway != null ||
    nearestPlace != null ||
    containingRegions.length > 0;

  return (
    <div className="panel__section">
      <p className="panel__eyebrow">Aviation Context (Derived)</p>
      {isLoading && !hasContext ? (
        <div className="empty-state compact">
          <p>Resolving canonical references.</p>
          <span>Using observed aircraft position and heading against the reference module.</span>
        </div>
      ) : hasContext ? (
        <div className="stack">
          {primaryReference ? (
            <div className="data-card data-card--compact">
              <strong>Primary match</strong>
              <span>{displayReference(primaryReference.summary)}</span>
              <span>
                {Math.round(primaryReference.confidence * 100)}% confidence via{" "}
                {primaryReference.method}
              </span>
              <span>{primaryReference.reason}</span>
            </div>
          ) : null}

          {nearestAirport ? (
            <div className="data-card data-card--compact">
              <strong>Nearest airport</strong>
              <span>{displayReference(nearestAirport.summary)}</span>
              <span>{formatDistanceMeters(nearestAirport.distanceM)}</span>
              <span>{formatBearing(nearestAirport.bearingDeg)}</span>
              <span>Geometry {nearestAirport.geometryMethod ?? "centroid"}</span>
            </div>
          ) : null}

          {nearestRunway ? (
            <div className="data-card data-card--compact">
              <strong>Nearest runway threshold</strong>
              <span>{displayReference(nearestRunway.summary)}</span>
              <span>{formatDistanceMeters(nearestRunway.distanceM)}</span>
              <span>{formatBearing(nearestRunway.bearingDeg)}</span>
              <span>Geometry {nearestRunway.geometryMethod ?? "segment"}</span>
            </div>
          ) : null}

          {nearestPlace ? (
            <div className="data-card data-card--compact">
              <strong>Nearest place context</strong>
              <span>{displayReference(nearestPlace)}</span>
              <span>{nearestPlace.objectType}</span>
            </div>
          ) : null}

          {containingRegions.length > 0 ? (
            <div className="data-card data-card--compact">
              <strong>Containing regions</strong>
              <span>
                {containingRegions
                  .slice(0, 3)
                  .map((region) => displayReference(region))
                  .join(" | ")}
              </span>
            </div>
          ) : null}

          <div className="data-card data-card--compact">
            <strong>Observed reference inputs</strong>
            <span>
              {aircraft.latitude.toFixed(4)}, {aircraft.longitude.toFixed(4)}
            </span>
            <span>
              Heading {aircraft.heading != null ? `${aircraft.heading.toFixed(0)} deg` : "unknown"}
            </span>
          </div>
        </div>
      ) : (
        <div className="empty-state compact">
          <p>No canonical aviation context resolved.</p>
          <span>The reference module did not return a nearby airport, runway, or region.</span>
        </div>
      )}
      {contextCaveat ? (
        <CaveatBlock heading="Reference context caveat" tone="evidence" compact>
          {contextCaveat}
        </CaveatBlock>
      ) : null}
    </div>
  );
}

function CameraPanel({
  camera,
  sourceInventory,
  frameNonce,
  onRefreshFrame
}: {
  camera: CameraEntity;
  sourceInventory?: CameraSourceInventoryEntry;
  frameNonce: number;
  onRefreshFrame: () => void;
}) {
  const frameUrl = camera.frame.imageUrl
    ? `${camera.frame.imageUrl}${camera.frame.imageUrl.includes("?") ? "&" : "?"}t=${frameNonce}`
    : null;
  const positionLabel = describePosition(camera);
  const orientationLabel = describeOrientation(camera);
  const confidenceLabel =
    camera.confidence != null ? `${Math.round(camera.confidence * 100)}% normalized` : "Not stated";
  const capabilityLabel = frameUrl
    ? "Direct-image"
    : camera.frame.viewerUrl
      ? "Viewer-only"
      : "No usable frame path";
  const usableLabel = isUsableCamera(camera) ? "Usable" : camera.review.status === "blocked" ? "Blocked" : "Limited";
  const referenceState = getCameraReferenceState(camera);

  return (
    <div className="panel__section" data-testid="webcam-camera-panel">
      <p className="panel__eyebrow">Camera Feed</p>
      {frameUrl ? (
        <img
          src={frameUrl}
          alt={camera.label}
          data-testid="webcam-camera-image"
          style={{ width: "100%", borderRadius: "12px", marginBottom: "12px" }}
        />
      ) : camera.frame.viewerUrl ? (
        <div className="empty-state compact" data-testid="webcam-viewer-only-notice">
          <p>Viewer fallback only.</p>
          <span>
            This source does not currently expose a trusted direct image URL. Open the viewer page
            for the current feed.
          </span>
        </div>
      ) : (
        <div className="empty-state compact">
          <p>No frame available.</p>
          <span>
            The source did not expose a usable direct image URL or viewer fallback for this camera.
          </span>
        </div>
      )}
      <div className="stack stack--actions">
        <button type="button" className="ghost-button" onClick={onRefreshFrame}>
          Refresh Frame
        </button>
        {camera.frame.viewerUrl ? (
          <a
            className="ghost-button ghost-button--link"
            href={camera.frame.viewerUrl}
            target="_blank"
            rel="noreferrer"
          >
            Open Viewer
          </a>
        ) : null}
      </div>
      <dl>
        <div>
          <dt>Source ID</dt>
          <dd>{camera.source}</dd>
        </div>
        <div>
          <dt>Capability</dt>
          <dd>{capabilityLabel}</dd>
        </div>
        <div>
          <dt>Usable Status</dt>
          <dd>{usableLabel}</dd>
        </div>
        <div>
          <dt>Roadway</dt>
          <dd>{camera.roadway ?? "Unknown"}</dd>
        </div>
        <div>
          <dt>Location</dt>
          <dd>{camera.locationDescription ?? "Unknown"}</dd>
        </div>
        <div>
          <dt>Position</dt>
          <dd>{positionLabel}</dd>
        </div>
        <div>
          <dt>Orientation</dt>
          <dd>{orientationLabel}</dd>
        </div>
        {camera.degradedReason ? (
          <div>
            <dt>Degraded Reason</dt>
            <dd>{camera.degradedReason}</dd>
          </div>
        ) : null}
        <div>
          <dt>Frame Status</dt>
          <dd>{camera.frame.status}</dd>
        </div>
        <div>
          <dt>Frame Time</dt>
          <dd>{formatMaybeTimestamp(camera.frame.lastFrameAt)}</dd>
        </div>
        <div>
          <dt>Frame Age</dt>
          <dd>{camera.frame.ageSeconds != null ? `${camera.frame.ageSeconds}s` : "Unknown"}</dd>
        </div>
        <div>
          <dt>Frame Size</dt>
          <dd>
            {camera.frame.width != null && camera.frame.height != null
              ? `${camera.frame.width} x ${camera.frame.height}`
              : "Unknown"}
          </dd>
        </div>
        <div>
          <dt>Metadata Refresh</dt>
          <dd>{formatMaybeTimestamp(camera.lastMetadataRefreshAt)}</dd>
        </div>
        <div>
          <dt>Next Frame Refresh</dt>
          <dd>{formatMaybeTimestamp(camera.nextFrameRefreshAt)}</dd>
        </div>
        <div>
          <dt>Backoff</dt>
          <dd>{formatMaybeTimestamp(camera.backoffUntil)}</dd>
        </div>
        <div>
          <dt>Health</dt>
          <dd>{camera.healthState ?? "Unknown"}</dd>
        </div>
        <div>
          <dt>Retry Count</dt>
          <dd>{camera.retryCount ?? 0}</dd>
        </div>
        <div>
          <dt>Last HTTP</dt>
          <dd>{camera.lastHttpStatus ?? "Unknown"}</dd>
        </div>
        <div>
          <dt>Review</dt>
          <dd>{camera.review.status}{camera.review.reason ? `: ${camera.review.reason}` : ""}</dd>
        </div>
        <div>
          <dt>Confidence</dt>
          <dd>{confidenceLabel}</dd>
        </div>
        <div>
          <dt>Coordinates</dt>
          <dd>{formatCameraCoordinates(camera)}</dd>
        </div>
        <div>
          <dt>Coordinate Certainty</dt>
          <dd>{positionLabel}</dd>
        </div>
        <div>
          <dt>Orientation Certainty</dt>
          <dd>{orientationLabel}</dd>
        </div>
        <div>
          <dt>Attribution</dt>
          <dd>
            {camera.compliance.attributionUrl ? (
              <a href={camera.compliance.attributionUrl} target="_blank" rel="noreferrer">
                {camera.compliance.attributionText}
              </a>
            ) : (
              camera.compliance.attributionText
            )}
          </dd>
        </div>
        {camera.compliance.termsUrl ? (
          <div>
            <dt>Terms</dt>
            <dd>
              <a href={camera.compliance.termsUrl} target="_blank" rel="noreferrer">
                Review source terms
              </a>
            </dd>
          </div>
        ) : null}
        {sourceInventory ? (
          <div>
            <dt>Source Readiness</dt>
            <dd>
              {describeSourceReadiness(sourceInventory)}
            </dd>
          </div>
        ) : null}
        {sourceInventory?.lastImportOutcome ? (
          <div>
            <dt>Source Import Outcome</dt>
            <dd>{sourceInventory.lastImportOutcome}</dd>
          </div>
        ) : null}
        {sourceInventory ? (
          <div>
            <dt>Source Yield</dt>
            <dd>
              {formatCount(sourceInventory.usableCameraCount)} usable / {formatCount(sourceInventory.directImageCameraCount)} direct-image / {formatCount(sourceInventory.viewerOnlyCameraCount)} viewer-only
            </dd>
          </div>
        ) : null}
      </dl>
      <div className="panel__section" data-testid="webcam-camera-reference-context">
        <p className="panel__eyebrow">Reference Context</p>
        <div className="data-card data-card--compact">
          <div className="stack">
            <StatusBadge tone={referenceStateTone(referenceState.kind)}>
              {referenceState.label}
            </StatusBadge>
            {camera.referenceHintText ? <span>Connector hint: {camera.referenceHintText}</span> : null}
            {camera.facilityCodeHint ? <span>Facility hint: {camera.facilityCodeHint}</span> : null}
            {camera.nearestReferenceRefId ? (
              <span>Reviewed link: {camera.nearestReferenceRefId}</span>
            ) : null}
            {camera.referenceLinkStatus && camera.referenceLinkStatus !== "hinted" ? (
              <span>
                Machine suggestion: {camera.referenceLinkStatus}
                {camera.linkCandidateCount != null ? ` (${camera.linkCandidateCount} candidates)` : ""}
              </span>
            ) : null}
            {!camera.nearestReferenceRefId && !camera.referenceHintText && !camera.facilityCodeHint && !camera.referenceLinkStatus ? (
              <span>No reference hint, machine suggestion, or reviewed link is available for this camera.</span>
            ) : null}
          </div>
          <CaveatBlock heading="Reference caveat" tone="evidence" compact>
            Connector hints are not canonical matches. Machine suggestions remain unreviewed until the reference subsystem confirms them. Reviewed links, when present, take precedence.
          </CaveatBlock>
        </div>
      </div>
      {camera.review.requiredActions.length > 0 ? (
        <div className="panel__section">
          <p className="panel__eyebrow">Review Actions</p>
          <div className="stack">
            {camera.review.requiredActions.map((action) => (
              <div key={action} className="data-card data-card--compact">
                <span>{action}</span>
              </div>
            ))}
          </div>
        </div>
      ) : null}
      {(camera.compliance.provenanceNotes.length > 0 || camera.compliance.notes.length > 0) ? (
        <div className="panel__section">
          <p className="panel__eyebrow">Compliance Notes</p>
          <div className="stack">
            {camera.compliance.provenanceNotes.map((note) => (
              <div key={`provenance-${note}`} className="data-card data-card--compact">
                <strong>Provenance</strong>
                <span>{note}</span>
              </div>
            ))}
            {camera.compliance.notes.map((note) => (
              <div key={`note-${note}`} className="data-card data-card--compact">
                <strong>Usage</strong>
                <span>{note}</span>
              </div>
            ))}
          </div>
        </div>
      ) : null}
    </div>
  );
}

function EnvironmentalEventInspectorPanel({
  event
}: {
  event:
    | EarthquakeEntity
    | EonetEntity
    | VolcanoEntity
    | TsunamiAlertEntity
    | UkEaFloodEntity
    | GeoNetHazardEntity
    | HkoWeatherEntity
    | MetNoAlertEntity
    | CanadaCapAlertEntity;
}) {
  if (event.eventSource === "environment-canada-cap") {
    return (
      <div className="panel__section" data-testid="canada-cap-inspector">
        <p className="panel__eyebrow">Environmental Event (Canada CAP)</p>
        <dl>
          <div><dt>Title</dt><dd>{event.label}</dd></div>
          <div><dt>Alert Type</dt><dd>{event.alertType}</dd></div>
          <div><dt>Severity</dt><dd>{event.severity}</dd></div>
          <div><dt>Urgency / Certainty</dt><dd>{[event.urgency, event.certainty].filter(Boolean).join(" / ") || "Unknown"}</dd></div>
          <div><dt>Area</dt><dd>{event.areaDescription ?? event.provinceOrRegion ?? "Unknown"}</dd></div>
          <div><dt>Sent / Effective</dt><dd>{formatTimestamp(event.effectiveAt ?? event.timestamp)}</dd></div>
          <div><dt>Expires</dt><dd>{event.expiresAt ? formatTimestamp(event.expiresAt) : "Unknown"}</dd></div>
          <div><dt>Evidence Basis</dt><dd>{event.evidenceBasis}</dd></div>
          <div><dt>Source Mode</dt><dd>{event.sourceMode}</dd></div>
          <div><dt>Source</dt><dd>Environment Canada CAP</dd></div>
          <div><dt>Caveat</dt><dd>{event.caveat}</dd></div>
        </dl>
        {event.externalUrl ? (
          <a className="ghost-button ghost-button--link" data-testid="canada-cap-inspector-source-link" href={event.externalUrl} target="_blank" rel="noreferrer">
            Open Canada CAP Record
          </a>
        ) : null}
      </div>
    );
  }
  if (event.eventSource === "hong-kong-observatory") {
    return (
      <div className="panel__section" data-testid="hko-weather-inspector">
        <p className="panel__eyebrow">Environmental Event (Hong Kong Observatory)</p>
        <dl>
          <div><dt>Title</dt><dd>{event.label}</dd></div>
          <div><dt>Kind</dt><dd>{event.entityKind}</dd></div>
          <div><dt>Warning Type</dt><dd>{event.warningType ?? "Unknown"}</dd></div>
          <div><dt>Level / Signal</dt><dd>{event.warningLevel ?? event.signal ?? "Unknown"}</dd></div>
          <div><dt>Issued / Updated</dt><dd>{formatTimestamp(event.updatedAt ?? event.issuedAt ?? event.timestamp)}</dd></div>
          <div><dt>Summary</dt><dd>{event.summary ?? event.affectedArea ?? "Summary unavailable"}</dd></div>
          <div><dt>Evidence Basis</dt><dd>{event.evidenceBasis}</dd></div>
          <div><dt>Source Mode</dt><dd>{event.sourceMode}</dd></div>
          <div><dt>Source</dt><dd>Hong Kong Observatory</dd></div>
          <div><dt>Caveat</dt><dd>{event.caveat}</dd></div>
        </dl>
        {event.externalUrl ? (
          <a className="ghost-button ghost-button--link" data-testid="hko-weather-inspector-source-link" href={event.externalUrl} target="_blank" rel="noreferrer">
            Open HKO Record
          </a>
        ) : null}
      </div>
    );
  }
  if (event.eventSource === "met-norway-metalerts") {
    return (
      <div className="panel__section" data-testid="metno-alert-inspector">
        <p className="panel__eyebrow">Environmental Event (MET Norway Alerts)</p>
        <dl>
          <div><dt>Title</dt><dd>{event.label}</dd></div>
          <div><dt>Alert Type</dt><dd>{event.alertType}</dd></div>
          <div><dt>Severity</dt><dd>{event.severity}</dd></div>
          <div><dt>Urgency / Certainty</dt><dd>{[event.urgency, event.certainty].filter(Boolean).join(" / ") || "Unknown"}</dd></div>
          <div><dt>Area</dt><dd>{event.areaDescription ?? "Unknown"}</dd></div>
          <div><dt>Effective</dt><dd>{event.effectiveAt ? formatTimestamp(event.effectiveAt) : "Unknown"}</dd></div>
          <div><dt>Onset</dt><dd>{event.onsetAt ? formatTimestamp(event.onsetAt) : "Unknown"}</dd></div>
          <div><dt>Expires</dt><dd>{event.expiresAt ? formatTimestamp(event.expiresAt) : "Unknown"}</dd></div>
          <div><dt>Sent / Updated</dt><dd>{formatTimestamp(event.updatedAt ?? event.sentAt ?? event.timestamp)}</dd></div>
          <div><dt>Geometry Summary</dt><dd>{event.geometrySummary ?? event.bboxSummary ?? "Summary unavailable"}</dd></div>
          <div><dt>Coordinate Basis</dt><dd>{event.coordinateProvenance}</dd></div>
          <div><dt>Evidence Basis</dt><dd>{event.evidenceBasis}</dd></div>
          <div><dt>Source Mode</dt><dd>{event.sourceMode}</dd></div>
          <div><dt>Source</dt><dd>MET Norway MetAlerts</dd></div>
          <div><dt>Caveat</dt><dd>{event.caveat}</dd></div>
        </dl>
        {event.externalUrl ? (
          <a className="ghost-button ghost-button--link" data-testid="metno-alert-inspector-source-link" href={event.externalUrl} target="_blank" rel="noreferrer">
            Open MET Norway Alert
          </a>
        ) : null}
      </div>
    );
  }
  if (event.eventSource === "geonet-nz") {
    return (
      <div className="panel__section" data-testid="geonet-inspector">
        <p className="panel__eyebrow">Environmental Event (GeoNet NZ)</p>
        <dl>
          <div><dt>Title</dt><dd>{event.label}</dd></div>
          <div><dt>Kind</dt><dd>{event.entityKind}</dd></div>
          <div><dt>Quality</dt><dd>{event.geonetQuality ?? "Unknown"}</dd></div>
          <div><dt>Region</dt><dd>{event.region ?? event.locality ?? event.volcanoName ?? "Unknown"}</dd></div>
          <div><dt>Magnitude / Alert</dt><dd>{event.entityKind === "quake" ? (event.magnitude != null ? `M${event.magnitude.toFixed(1)}` : "Unknown") : (event.alertLevel != null ? `VAL ${event.alertLevel}` : "Unknown")}</dd></div>
          <div><dt>Status</dt><dd>{event.statusDetail ?? event.activity ?? "Unknown"}</dd></div>
          <div><dt>Source Mode</dt><dd>{event.sourceMode}</dd></div>
          <div><dt>Source</dt><dd>GeoNet New Zealand</dd></div>
          <div><dt>Caveat</dt><dd>{event.caveat}</dd></div>
        </dl>
        {event.externalUrl ? (
          <a className="ghost-button ghost-button--link" data-testid="geonet-inspector-source-link" href={event.externalUrl} target="_blank" rel="noreferrer">
            Open GeoNet Record
          </a>
        ) : null}
      </div>
    );
  }
  if (event.eventSource === "uk-ea-flood-monitoring") {
    return (
      <div className="panel__section" data-testid="uk-flood-inspector">
        <p className="panel__eyebrow">Environmental Event (UK EA Flood Monitoring)</p>
        <dl>
          <div><dt>Title</dt><dd>{event.label}</dd></div>
          <div><dt>Kind</dt><dd>{event.entityKind}</dd></div>
          <div><dt>Severity</dt><dd>{event.severity ?? "Unknown"}</dd></div>
          <div><dt>Area</dt><dd>{event.areaName ?? event.stationLabel ?? "Unknown"}</dd></div>
          <div><dt>River/Sea</dt><dd>{event.riverOrSea ?? event.riverName ?? "Unknown"}</dd></div>
          <div><dt>Region</dt><dd>{event.region ?? event.county ?? "Unknown"}</dd></div>
          <div><dt>Observed Value</dt><dd>{event.value != null ? `${event.value}${event.unit ? ` ${event.unit}` : ""}` : "Not reported"}</dd></div>
          <div><dt>Observed / Issued</dt><dd>{formatTimestamp(event.timestamp)}</dd></div>
          <div><dt>Evidence Basis</dt><dd>{event.evidenceBasis}</dd></div>
          <div><dt>Source Mode</dt><dd>{event.sourceMode}</dd></div>
          <div><dt>Source</dt><dd>UK Environment Agency Flood Monitoring</dd></div>
          <div><dt>Caveat</dt><dd>{event.caveat}</dd></div>
        </dl>
        {event.externalUrl ? (
          <a className="ghost-button ghost-button--link" data-testid="uk-flood-inspector-source-link" href={event.externalUrl} target="_blank" rel="noreferrer">
            Open UK EA Flood Record
          </a>
        ) : null}
      </div>
    );
  }
  if (event.eventSource === "noaa-tsunami-alerts") {
    return (
      <div className="panel__section" data-testid="tsunami-inspector">
        <p className="panel__eyebrow">Environmental Event (NOAA Tsunami Alerts)</p>
        <dl>
          <div><dt>Title</dt><dd>{event.label}</dd></div>
          <div><dt>Alert Type</dt><dd>{event.alertType}</dd></div>
          <div><dt>Source Center</dt><dd>{event.sourceCenter}</dd></div>
          <div><dt>Issued</dt><dd>{formatTimestamp(event.issuedAt)}</dd></div>
          <div><dt>Updated</dt><dd>{event.updatedAt ? formatTimestamp(event.updatedAt) : "Unknown"}</dd></div>
          <div><dt>Affected Regions</dt><dd>{event.affectedRegions.join(", ") || "Summary unavailable"}</dd></div>
          <div><dt>Basin</dt><dd>{event.basin ?? "Unknown"}</dd></div>
          <div><dt>Source</dt><dd>NOAA Tsunami Warning Centers</dd></div>
          <div><dt>Evidence Basis</dt><dd>{event.evidenceBasis}</dd></div>
          <div><dt>Caveat</dt><dd>{event.caveat}</dd></div>
        </dl>
        {event.externalUrl ? (
          <a className="ghost-button ghost-button--link" data-testid="tsunami-inspector-source-link" href={event.externalUrl} target="_blank" rel="noreferrer">
            Open Tsunami Bulletin
          </a>
        ) : null}
      </div>
    );
  }
  if (event.eventSource === "usgs-volcano-hazards") {
    return (
      <div className="panel__section" data-testid="volcano-inspector">
        <p className="panel__eyebrow">Environmental Event (USGS Volcano Hazards)</p>
        <dl>
          <div><dt>Volcano</dt><dd>{event.volcanoName}</dd></div>
          <div><dt>Alert Level</dt><dd>{event.alertLevel}</dd></div>
          <div><dt>Aviation Color</dt><dd>{event.aviationColorCode}</dd></div>
          <div><dt>Observatory</dt><dd>{event.observatoryName}</dd></div>
          <div><dt>Region</dt><dd>{event.region ?? "Unknown"}</dd></div>
          <div><dt>Issued</dt><dd>{formatTimestamp(event.timestamp)}</dd></div>
          <div><dt>Notice Type</dt><dd>{event.noticeTypeLabel ?? event.noticeTypeCode ?? "Unknown"}</dd></div>
          <div><dt>Scope</dt><dd>{event.statusScope}</dd></div>
          <div><dt>Source</dt><dd>USGS Volcano Hazards Program</dd></div>
          <div><dt>Caveat</dt><dd>{event.caveat}</dd></div>
        </dl>
        {event.externalUrl ? (
          <a className="ghost-button ghost-button--link" data-testid="volcano-inspector-source-link" href={event.externalUrl} target="_blank" rel="noreferrer">
            Open USGS Volcano Notice
          </a>
        ) : null}
      </div>
    );
  }
  if (event.eventSource === "nasa-eonet") {
    return (
      <div className="panel__section" data-testid="eonet-inspector">
        <p className="panel__eyebrow">Environmental Event (NASA EONET)</p>
        <dl>
          <div><dt>Event ID</dt><dd>{event.eventId}</dd></div>
          <div><dt>Title</dt><dd>{event.label}</dd></div>
          <div><dt>Categories</dt><dd>{event.categories.join(", ") || "Unknown"}</dd></div>
          <div><dt>Event Date</dt><dd>{formatTimestamp(event.eventDate)}</dd></div>
          <div><dt>Status</dt><dd>{event.statusDetail}</dd></div>
          <div><dt>Geometry Type</dt><dd>{event.geometryType}</dd></div>
          <div><dt>Geometry Count</dt><dd>{event.geometryCount}</dd></div>
          <div><dt>Location Semantics</dt><dd>{event.coordinatesSummary}</dd></div>
          <div><dt>Source</dt><dd>NASA EONET</dd></div>
          <div><dt>Caveat</dt><dd>{event.caveat}</dd></div>
        </dl>
        {event.externalUrl ? (
          <a className="ghost-button ghost-button--link" data-testid="eonet-inspector-source-link" href={event.externalUrl} target="_blank" rel="noreferrer">
            Open NASA EONET Event
          </a>
        ) : null}
      </div>
    );
  }
  return (
    <div className="panel__section" data-testid="earthquake-inspector">
      <p className="panel__eyebrow">Environmental Event (USGS)</p>
      <dl>
        <div>
          <dt>Event ID</dt>
          <dd>{event.eventId}</dd>
        </div>
        <div>
          <dt>Place</dt>
          <dd>{event.place ?? "Unknown"}</dd>
        </div>
        <div>
          <dt>Magnitude</dt>
          <dd data-testid="earthquake-inspector-magnitude">
            {event.magnitude != null
              ? `${event.magnitude.toFixed(1)}${event.magnitudeType ? ` ${event.magnitudeType}` : ""}`
              : "Not reported"}
          </dd>
        </div>
        <div>
          <dt>Depth</dt>
          <dd data-testid="earthquake-inspector-depth">{event.depthKm != null ? `${event.depthKm.toFixed(1)} km` : "Unknown"}</dd>
        </div>
        <div>
          <dt>Event Time</dt>
          <dd data-testid="earthquake-inspector-time">{formatTimestamp(event.timestamp)}</dd>
        </div>
        <div>
          <dt>Updated Time</dt>
          <dd>{event.updated ? formatTimestamp(event.updated) : "Unknown"}</dd>
        </div>
        <div>
          <dt>Status</dt>
          <dd>{event.status ?? "Unknown"}</dd>
        </div>
        <div>
          <dt>Tsunami Flag</dt>
          <dd>{event.tsunami ?? 0}</dd>
        </div>
        <div>
          <dt>Significance</dt>
          <dd>{event.significance ?? "Unknown"}</dd>
        </div>
        <div>
          <dt>Felt Reports</dt>
          <dd>{event.felt ?? "Unknown"}</dd>
        </div>
        <div>
          <dt>Source</dt>
          <dd data-testid="earthquake-inspector-source">USGS Earthquake Hazards Program</dd>
        </div>
        <div>
          <dt>Caveat</dt>
          <dd data-testid="earthquake-inspector-caveat">{event.caveat}</dd>
        </div>
      </dl>
      {event.externalUrl ? (
        <a className="ghost-button ghost-button--link" data-testid="earthquake-inspector-source-link" href={event.externalUrl} target="_blank" rel="noreferrer">
          Open USGS Event Page
        </a>
      ) : null}
    </div>
  );
}

function formatCameraCoordinates(camera: CameraEntity) {
  const decimals = camera.position.kind === "exact" ? 6 : 4;
  return `${camera.latitude.toFixed(decimals)}, ${camera.longitude.toFixed(decimals)} (${camera.position.kind})`;
}

function describePosition(camera: CameraEntity) {
  const confidence = camera.position.confidence != null ? `, ${Math.round(camera.position.confidence * 100)}% confidence` : "";
  return `${camera.position.kind}${confidence}`;
}

function describeOrientation(camera: CameraEntity) {
  if (camera.orientation.kind === "exact" && camera.orientation.degrees != null) {
    return `${camera.orientation.kind} (${camera.orientation.degrees.toFixed(0)} deg)`;
  }
  if (camera.orientation.cardinalDirection) {
    return `${camera.orientation.kind} (${camera.orientation.cardinalDirection})`;
  }
  if (camera.orientation.kind === "ptz") {
    return "ptz / dynamic";
  }
  return camera.orientation.kind;
}

function isUsableCamera(camera: CameraEntity) {
  if (camera.review.status === "blocked" || camera.healthState === "blocked") {
    return false;
  }
  return camera.frame.status === "live" || camera.frame.status === "viewer-page-only";
}

function describeSourceReadiness(source: CameraSourceInventoryEntry) {
  if (source.onboardingState === "candidate") {
    return "Candidate only";
  }
  if (source.authentication !== "none" && !source.credentialsConfigured) {
    return "Credential blocked";
  }
  switch (source.importReadiness) {
    case "validated":
      return "Validated";
    case "low-yield":
      return "Low yield";
    case "poor-quality":
      return "Poor quality";
    case "actively-importing":
      return "Actively importing";
    case "approved-unvalidated":
      return "Approved but unvalidated";
    default:
      return source.importReadiness ?? "Unknown";
  }
}

function formatCount(value?: number | null) {
  return value == null ? "Unknown" : value.toLocaleString();
}

function referenceStateTone(kind: ReturnType<typeof getCameraReferenceState>["kind"]) {
  switch (kind) {
    case "reviewed":
      return "success" as const;
    case "machine":
      return "info" as const;
    case "hint":
      return "warning" as const;
    default:
      return "neutral" as const;
  }
}

function freshnessTone(value: "fresh" | "recent" | "possibly-stale" | "stale" | "unknown") {
  switch (value) {
    case "fresh":
      return "available" as const;
    case "recent":
      return "info" as const;
    case "possibly-stale":
      return "advisory" as const;
    case "stale":
      return "danger" as const;
    case "unknown":
    default:
      return "neutral" as const;
  }
}

function healthTone(value: "normal" | "degraded" | "stale" | "unavailable" | "partial" | "unknown") {
  switch (value) {
    case "normal":
      return "available" as const;
    case "degraded":
      return "warning" as const;
    case "stale":
      return "danger" as const;
    case "unavailable":
      return "unavailable" as const;
    case "partial":
      return "advisory" as const;
    case "unknown":
    default:
      return "neutral" as const;
  }
}

function availabilityTone(value: "available" | "unavailable" | "disabled" | "empty" | "degraded" | "unknown") {
  switch (value) {
    case "available":
      return "available" as const;
    case "degraded":
      return "warning" as const;
    case "empty":
      return "neutral" as const;
    case "disabled":
      return "unavailable" as const;
    case "unavailable":
      return "danger" as const;
    case "unknown":
    default:
      return "neutral" as const;
  }
}

function issueSeverityTone(value: "attention" | "info") {
  switch (value) {
    case "attention":
      return "warning" as const;
    case "info":
    default:
      return "info" as const;
  }
}

function readinessTone(
  value:
    | "ready-with-caveats"
    | "missing-optional-context"
    | "fixture-local-context-present"
    | "degraded-or-unavailable-context"
    | "selected-target-freshness-limited"
) {
  switch (value) {
    case "ready-with-caveats":
      return "info" as const;
    case "missing-optional-context":
      return "advisory" as const;
    case "fixture-local-context-present":
      return "neutral" as const;
    case "degraded-or-unavailable-context":
      return "warning" as const;
    case "selected-target-freshness-limited":
      return "danger" as const;
    default:
      return "neutral" as const;
  }
}

function queueBandTone(value: "review-first" | "review" | "note") {
  switch (value) {
    case "review-first":
      return "warning" as const;
    case "review":
      return "advisory" as const;
    case "note":
    default:
      return "info" as const;
  }
}

function queueCategoryTone(
  value: "source-context" | "freshness" | "comparison" | "export-readiness"
) {
  switch (value) {
    case "freshness":
      return "warning" as const;
    case "comparison":
      return "advisory" as const;
    case "export-readiness":
      return "info" as const;
    case "source-context":
    default:
      return "neutral" as const;
  }
}

function issueCategoryTone(
  value: "source-health" | "availability-gap" | "coverage-limit" | "evidence-basis"
) {
  switch (value) {
    case "source-health":
      return "warning" as const;
    case "availability-gap":
      return "danger" as const;
    case "coverage-limit":
      return "advisory" as const;
    case "evidence-basis":
    default:
      return "info" as const;
  }
}

function normalizeAvailabilityHealth(value: string) {
  if (value.includes("degraded")) {
    return "degraded" as const;
  }
  if (value.includes("stale")) {
    return "stale" as const;
  }
  if (value.includes("partial")) {
    return "partial" as const;
  }
  if (value.includes("unavailable") || value.includes("blocked") || value.includes("disabled")) {
    return "unavailable" as const;
  }
  if (value.includes("normal") || value.includes("healthy")) {
    return "normal" as const;
  }
  return "unknown" as const;
}

function relationLabel(subject: SceneEntity, other: SceneEntity) {
  if (subject.type === "aircraft" && other.type === "satellite") {
    return "overhead satellite";
  }
  if (subject.type === "satellite" && other.type === "aircraft") {
    return "nearby aircraft";
  }
  return "nearby target";
}

function distanceKm(a: SceneEntity, b: SceneEntity) {
  const toRadians = (value: number) => (value * Math.PI) / 180;
  const lat1 = toRadians(a.latitude);
  const lat2 = toRadians(b.latitude);
  const deltaLat = toRadians(b.latitude - a.latitude);
  const deltaLon = toRadians(b.longitude - a.longitude);
  const sinLat = Math.sin(deltaLat / 2);
  const sinLon = Math.sin(deltaLon / 2);
  const h = sinLat * sinLat + Math.cos(lat1) * Math.cos(lat2) * sinLon * sinLon;
  return 6371 * 2 * Math.atan2(Math.sqrt(h), Math.sqrt(1 - h));
}

function formatTimestamp(value: string) {
  return new Date(value).toLocaleString();
}

function formatMaybeTimestamp(value?: string | null) {
  return value ? formatTimestamp(value) : "Unknown";
}

function formatDistanceMeters(value: number) {
  if (value >= 1000) {
    return `${(value / 1000).toFixed(1)} km`;
  }
  return `${Math.round(value)} m`;
}

function formatBearing(value?: number | null) {
  return value != null ? `Bearing ${value.toFixed(0)} deg` : "Bearing unknown";
}

function displayReference(reference: ReferenceObjectSummary) {
  return reference.objectDisplayLabel ?? reference.codeContext ?? reference.canonicalName;
}

function buildObservationSummary(entity: SceneEntity) {
  const lines = [
    `Label: ${entity.label}`,
    `ID: ${entity.id}`,
    `Type: ${entity.type}`,
    `Source: ${entity.sourceDetail ?? entity.source}`,
    `Observed: ${entity.observedAt ?? entity.timestamp}`,
    `Fetched: ${entity.fetchedAt ?? entity.timestamp}`,
    `Coordinates: ${entity.latitude.toFixed(6)}, ${entity.longitude.toFixed(6)}`
  ];

  if (entity.type === "camera") {
    lines.push(`Coordinates: ${formatCameraCoordinates(entity)}`);
    lines.push(`Position Kind: ${describePosition(entity)}`);
    lines.push(`Orientation Kind: ${describeOrientation(entity)}`);
    lines.push(`Attribution: ${entity.compliance.attributionText}`);
  } else {
    lines.push(`Altitude: ${entity.altitude.toFixed(0)} m`);
    lines.push(`Heading: ${entity.heading != null ? `${entity.heading.toFixed(0)} deg` : "Unknown"}`);
    lines.push(`Speed: ${entity.speed != null ? `${entity.speed.toFixed(0)} m/s` : "Unknown"}`);
    if (entity.historySummary) {
      lines.push(`History Kind: ${entity.historySummary.kind}`);
      lines.push(`History Points: ${entity.historySummary.pointCount}`);
      lines.push(`History Detail: ${entity.historySummary.detail ?? "None"}`);
    }
  }

  return lines.join("\n");
}
