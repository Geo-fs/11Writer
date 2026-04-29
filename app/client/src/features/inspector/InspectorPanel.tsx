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
import {
  buildAerospaceFocusComputation,
  buildAerospaceFocusHistorySummary,
  buildAerospaceFocusSnapshot
} from "./aerospaceFocusMode";
import { formatRelativeAge, getReplaySnapshot, summarizeTrack } from "../../lib/history";
import {
  useAircraftReferenceLinkQuery,
  useCameraSourceInventoryQuery,
  useNearestAirportReferenceQuery,
  useNearestRunwayThresholdReferenceQuery,
  useSourceStatusQuery
} from "../../lib/queries";
import { useAppStore } from "../../lib/store";
import { CaveatBlock, DataBasisBadge, StatusBadge } from "../../components/ui";
import type {
  CameraSourceInventoryEntry,
  ReferenceNearbyItem,
  ReferenceObjectSummary
} from "../../types/api";
import type { AircraftEntity, CameraEntity, EarthquakeEntity, EonetEntity, SceneEntity } from "../../types/entities";
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
  const aerospaceFocus = useAppStore((state) => state.aerospaceFocus);
  const aerospaceFocusHistory = useAppStore((state) => state.aerospaceFocusHistory);
  const hud = useAppStore((state) => state.hud);
  const setFollowedEntityId = useAppStore((state) => state.setFollowedEntityId);
  const setSelectedEntityId = useAppStore((state) => state.setSelectedEntityId);
  const setSelectedReplayIndex = useAppStore((state) => state.setSelectedReplayIndex);
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

function EnvironmentalEventInspectorPanel({ event }: { event: EarthquakeEntity | EonetEntity }) {
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
