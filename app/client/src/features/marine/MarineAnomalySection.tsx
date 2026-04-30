import { useEffect, useMemo, useRef, useState } from "react";
import clsx from "clsx";
import {
  useMarineChokepointSummaryQuery,
  useMarineIrelandOpwWaterLevelContextQuery,
  useMarineNdbcContextQuery,
  useMarineNoaaCoopsContextQuery,
  useMarineScottishWaterOverflowsQuery,
  useMarineVigicruesHydrometryContextQuery,
  useMarineVesselSummaryQuery,
  useMarineVesselsQuery,
  useMarineViewportSummaryQuery
} from "../../lib/queries";
import { useAppStore } from "../../lib/store";
import type { MarineChokepointSliceSummary } from "../../types/api";
import { buildActiveImageryContextFromHud } from "../../lib/imageryContext";
import { ImageryContextBadge } from "../imagery/ImageryContextBadge";
import { MarineAnomalyPanel } from "./MarineAnomalyComponents";
import {
  buildMarineEnvironmentalContextSummary,
  findMarineEnvironmentalContextPreset,
  getMarineEnvironmentalContextPreset,
  radiusKmForPreset,
  type MarineEnvironmentalContextAnchor,
  type MarineEnvironmentalContextPresetSelection,
  type MarineEnvironmentalContextRadiusPreset
} from "./marineEnvironmentalContext";
import { buildMarineEvidenceSummary } from "./marineEvidenceSummary";
import { buildMarineContextIssueQueue } from "./marineContextIssueQueue";
import { buildMarineContextFusionSummary } from "./marineContextFusionSummary";
import { buildMarineContextReviewReport } from "./marineContextReviewReport";
import { buildMarineContextSourceRegistrySummary } from "./marineContextSourceSummary";
import { buildMarineHydrologyContextSummary } from "./marineHydrologyContext";
import {
  buildMarineContextSnapshot,
  buildMarineContextTimelineSummary,
  clearMarineContextSnapshots,
  reduceMarineContextSnapshots,
  type MarineContextSnapshot
} from "./marineContextTimeline";
import { buildMarineNdbcContextSummary } from "./marineNdbcContext";
import { buildMarineNoaaContextSummary } from "./marineNoaaContext";
import { buildMarineIrelandOpwContextSummary } from "./marineIrelandOpwContext";
import { buildMarineScottishWaterContextSummary } from "./marineScottishWaterContext";
import { buildMarineVigicruesContextSummary } from "./marineVigicruesContext";
import { buildFocusedMarineReplayEvidence } from "./marineReplayEvidence";
import {
  buildMarineEvidenceInterpretation,
  getMarineEvidenceInterpretationCards,
  type MarineEvidenceInterpretationMode
} from "./marineEvidenceInterpretation";
import {
  chokepointSliceNavigationTarget,
  fromGapEvent,
  type MarineReplayNavigationTarget,
  vesselNavigationTarget,
  viewportNavigationTarget
} from "./marineReplayNavigation";

type SliceFilter = "all" | "medium+" | "high";
type SliceSort = "priority" | "score";

export function MarineAnomalySection() {
  const selectedEntity = useAppStore((state) => state.selectedEntity);
  const hud = useAppStore((state) => state.hud);
  const selectedReplayIndex = useAppStore((state) => state.selectedReplayIndex);
  const setMarineEvidenceSummary = useAppStore((state) => state.setMarineEvidenceSummary);
  const focusedTarget = useAppStore((state) => state.activeMarineReplayTarget);
  const setFocusedTarget = useAppStore((state) => state.setActiveMarineReplayTarget);
  const [sliceFilter, setSliceFilter] = useState<SliceFilter>("all");
  const [sliceSort, setSliceSort] = useState<SliceSort>("priority");
  const [interpretationMode, setInterpretationMode] =
    useState<MarineEvidenceInterpretationMode>("compact");
  const [contextAnchor, setContextAnchor] =
    useState<MarineEnvironmentalContextAnchor>("chokepoint");
  const [contextRadiusPreset, setContextRadiusPreset] =
    useState<MarineEnvironmentalContextRadiusPreset>("medium");
  const [selectedEnvironmentalContextPreset, setSelectedEnvironmentalContextPreset] =
    useState<MarineEnvironmentalContextPresetSelection>("chokepoint-review");
  const [enabledContextSources, setEnabledContextSources] = useState<{
    coops: boolean;
    ndbc: boolean;
  }>({ coops: true, ndbc: true });
  const [marineContextSnapshots, setMarineContextSnapshots] = useState<MarineContextSnapshot[]>([]);
  const lastMarineEvidenceSummaryKeyRef = useRef<string | null>(null);
  const vesselsQuery = useMarineVesselsQuery();
  const selectedMarineVesselId =
    selectedEntity?.type === "marine-vessel"
      ? selectedEntity.id
      : vesselsQuery.data?.vessels?.[0]?.id ?? null;
  const vesselSummaryQuery = useMarineVesselSummaryQuery(selectedMarineVesselId);
  const viewportLatitude = Number.isFinite(hud.latitude) ? hud.latitude : null;
  const viewportLongitude = Number.isFinite(hud.longitude) ? hud.longitude : null;
  const viewportCenter = useMemo(
    () =>
      viewportLatitude != null && viewportLongitude != null
        ? { lat: viewportLatitude, lon: viewportLongitude }
        : null,
    [viewportLatitude, viewportLongitude]
  );
  const viewportSummaryQuery = useMarineViewportSummaryQuery(viewportCenter);
  const chokepointSummaryQuery = useMarineChokepointSummaryQuery(viewportCenter);
  const selectedVesselCoordinates = useMemo(() => {
    if (
      selectedEntity?.type === "marine-vessel" &&
      Number.isFinite(selectedEntity.latitude) &&
      Number.isFinite(selectedEntity.longitude)
    ) {
      return {
        latitude: selectedEntity.latitude,
        longitude: selectedEntity.longitude
      };
    }
    const latestObserved = vesselSummaryQuery.data?.latestObserved;
    if (
      latestObserved &&
      Number.isFinite(latestObserved.latitude) &&
      Number.isFinite(latestObserved.longitude)
    ) {
      return {
        latitude: latestObserved.latitude,
        longitude: latestObserved.longitude
      };
    }
    return null;
  }, [
    selectedEntity?.type,
    selectedEntity?.latitude,
    selectedEntity?.longitude,
    vesselSummaryQuery.data?.latestObserved
  ]);
  const effectiveContextState = useMemo(() => {
    const selectedVesselCenter =
      selectedVesselCoordinates != null
        ? {
            lat: selectedVesselCoordinates.latitude,
            lon: selectedVesselCoordinates.longitude
          }
        : null;
    const currentViewportCenter =
      viewportLatitude != null && viewportLongitude != null
        ? { lat: viewportLatitude, lon: viewportLongitude }
        : null;
    if (contextAnchor === "selected-vessel") {
      if (selectedVesselCenter) {
        return {
          center: selectedVesselCenter,
          contextKind: "viewport" as const,
          effectiveAnchor: "selected-vessel" as const,
          centerAvailable: true,
          fallbackReason: null
        };
      }
      if (currentViewportCenter) {
        return {
          center: currentViewportCenter,
          contextKind: "viewport" as const,
          effectiveAnchor: "fallback-viewport" as const,
          centerAvailable: true,
          fallbackReason:
            "Selected vessel anchor unavailable; environmental context fell back to viewport center."
        };
      }
      return {
        center: null,
        contextKind: "viewport" as const,
        effectiveAnchor: "unavailable" as const,
        centerAvailable: false,
        fallbackReason: "Selected vessel anchor unavailable and no viewport center is available."
      };
    }
    if (contextAnchor === "viewport") {
      return {
        center: currentViewportCenter,
        contextKind: "viewport" as const,
        effectiveAnchor: currentViewportCenter ? ("viewport" as const) : ("unavailable" as const),
        centerAvailable: currentViewportCenter != null,
        fallbackReason: currentViewportCenter
          ? null
          : "Viewport anchor unavailable for environmental context."
      };
    }
    return {
      center: currentViewportCenter,
      contextKind: "chokepoint" as const,
      effectiveAnchor: currentViewportCenter ? ("chokepoint" as const) : ("unavailable" as const),
      centerAvailable: currentViewportCenter != null,
      fallbackReason: currentViewportCenter
        ? null
        : "Chokepoint anchor unavailable for environmental context."
    };
  }, [
    contextAnchor,
    selectedVesselCoordinates,
    viewportLatitude,
    viewportLongitude
  ]);
  const contextRadiusKm = radiusKmForPreset(contextRadiusPreset);
  const activeEnvironmentalPreset = useMemo(
    () =>
      selectedEnvironmentalContextPreset === "custom"
        ? null
        : getMarineEnvironmentalContextPreset(selectedEnvironmentalContextPreset),
    [selectedEnvironmentalContextPreset]
  );
  const syncEnvironmentalPreset = (
    anchor: MarineEnvironmentalContextAnchor,
    radiusPreset: MarineEnvironmentalContextRadiusPreset,
    sources: { coops: boolean; ndbc: boolean }
  ) => {
    const matchedPreset = findMarineEnvironmentalContextPreset({
      anchor,
      radiusPreset,
      enabledSources: [
        ...(sources.coops ? (["coops"] as const) : []),
        ...(sources.ndbc ? (["ndbc"] as const) : [])
      ]
    });
    setSelectedEnvironmentalContextPreset(matchedPreset?.id ?? "custom");
  };
  const noaaCoopsContextQuery = useMarineNoaaCoopsContextQuery({
    center: effectiveContextState.center,
    contextKind: effectiveContextState.contextKind,
    radiusKm: contextRadiusKm,
    enabled: enabledContextSources.coops
  });
  const ndbcContextQuery = useMarineNdbcContextQuery({
    center: effectiveContextState.center,
    contextKind: effectiveContextState.contextKind,
    radiusKm: contextRadiusKm,
    enabled: enabledContextSources.ndbc
  });
  const scottishWaterContextQuery = useMarineScottishWaterOverflowsQuery({
    center: effectiveContextState.center,
    radiusKm: contextRadiusKm,
    status: "all",
    enabled: true
  });
  const vigicruesContextQuery = useMarineVigicruesHydrometryContextQuery({
    center: effectiveContextState.center,
    radiusKm: contextRadiusKm,
    parameter: "all",
    enabled: effectiveContextState.centerAvailable
  });
  const irelandOpwContextQuery = useMarineIrelandOpwWaterLevelContextQuery({
    center: effectiveContextState.center,
    radiusKm: contextRadiusKm,
    enabled: effectiveContextState.centerAvailable
  });

  const sortedSlices = useMemo(() => {
    const slices = [...(chokepointSummaryQuery.data?.slices ?? [])];
    const filtered = slices.filter((slice) => {
      if (sliceFilter === "high") return slice.anomaly.level === "high";
      if (sliceFilter === "medium+") return slice.anomaly.level !== "low";
      return true;
    });
    filtered.sort((a, b) => {
      if (sliceSort === "priority") {
        const aRank = a.anomaly.priorityRank ?? Number.MAX_SAFE_INTEGER;
        const bRank = b.anomaly.priorityRank ?? Number.MAX_SAFE_INTEGER;
        if (aRank !== bRank) return aRank - bRank;
      }
      return b.anomaly.score - a.anomaly.score;
    });
    return filtered;
  }, [chokepointSummaryQuery.data?.slices, sliceFilter, sliceSort]);

  const attentionItems = useMemo(() => {
    const items: Array<{
      type: string;
      label: string;
      level: string;
      score: number;
      reason: string;
      caveat: string;
      target: MarineReplayNavigationTarget | null;
    }> = [];
    if (vesselSummaryQuery.data) {
      const target = vesselNavigationTarget(vesselSummaryQuery.data);
      items.push({
        type: "vessel",
        label: vesselSummaryQuery.data.anomaly.displayLabel,
        level: vesselSummaryQuery.data.anomaly.level,
        score: vesselSummaryQuery.data.anomaly.score,
        reason: vesselSummaryQuery.data.anomaly.reasons[0] ?? "No reason stated.",
        caveat: vesselSummaryQuery.data.anomaly.caveats[0] ?? "",
        target
      });
    }
    if (viewportSummaryQuery.data) {
      const target = viewportNavigationTarget(viewportSummaryQuery.data);
      items.push({
        type: "viewport",
        label: viewportSummaryQuery.data.anomaly.displayLabel,
        level: viewportSummaryQuery.data.anomaly.level,
        score: viewportSummaryQuery.data.anomaly.score,
        reason: viewportSummaryQuery.data.anomaly.reasons[0] ?? "No reason stated.",
        caveat: viewportSummaryQuery.data.anomaly.caveats[0] ?? "",
        target
      });
    }
    const topSlice = sortedSlices[0];
    if (topSlice) {
      const target = chokepointSliceNavigationTarget(topSlice);
      items.push({
        type: "chokepoint",
        label: topSlice.anomaly.displayLabel,
        level: topSlice.anomaly.level,
        score: topSlice.anomaly.score,
        reason: topSlice.anomaly.reasons[0] ?? "No reason stated.",
        caveat: topSlice.anomaly.caveats[0] ?? "",
        target
      });
    }
    return items.sort((a, b) => b.score - a.score);
  }, [sortedSlices, vesselSummaryQuery.data, viewportSummaryQuery.data]);

  const focusedEvidenceRows = useMemo(
    () =>
      buildFocusedMarineReplayEvidence({
        target: focusedTarget,
        vesselSummary: vesselSummaryQuery.data ?? null,
        viewportSummary: viewportSummaryQuery.data ?? null,
        chokepointSummary: chokepointSummaryQuery.data ?? null
      }),
    [focusedTarget, vesselSummaryQuery.data, viewportSummaryQuery.data, chokepointSummaryQuery.data]
  );

  const noaaContextSummary = useMemo(
    () => buildMarineNoaaContextSummary(noaaCoopsContextQuery.data ?? null),
    [noaaCoopsContextQuery.data]
  );
  const ndbcContextSummary = useMemo(
    () => buildMarineNdbcContextSummary(ndbcContextQuery.data ?? null),
    [ndbcContextQuery.data]
  );
  const scottishWaterContextSummary = useMemo(
    () => buildMarineScottishWaterContextSummary(scottishWaterContextQuery.data ?? null),
    [scottishWaterContextQuery.data]
  );
  const vigicruesContextSummary = useMemo(
    () => buildMarineVigicruesContextSummary(vigicruesContextQuery.data ?? null),
    [vigicruesContextQuery.data]
  );
  const irelandOpwContextSummary = useMemo(
    () => buildMarineIrelandOpwContextSummary(irelandOpwContextQuery.data ?? null),
    [irelandOpwContextQuery.data]
  );
  const hydrologyContextSummary = useMemo(
    () =>
      buildMarineHydrologyContextSummary({
        vigicrues: vigicruesContextSummary,
        irelandOpw: irelandOpwContextSummary
      }),
    [vigicruesContextSummary, irelandOpwContextSummary]
  );
  const contextSourceRegistrySummary = useMemo(
    () =>
      buildMarineContextSourceRegistrySummary({
        irelandOpw: irelandOpwContextSummary,
        noaaCoops: noaaContextSummary,
        ndbc: ndbcContextSummary,
        scottishWater: scottishWaterContextSummary,
        vigicrues: vigicruesContextSummary
      }),
    [irelandOpwContextSummary, noaaContextSummary, ndbcContextSummary, scottishWaterContextSummary, vigicruesContextSummary]
  );
  const environmentalContextSummary = useMemo(
    () =>
      buildMarineEnvironmentalContextSummary({
        noaaCoops: noaaCoopsContextQuery.data ?? null,
        ndbc: ndbcContextQuery.data ?? null,
        controls: {
          presetId: selectedEnvironmentalContextPreset,
          presetLabel: activeEnvironmentalPreset?.label ?? "Custom context settings",
          isCustomPreset: selectedEnvironmentalContextPreset === "custom",
          presetCaveat:
            activeEnvironmentalPreset?.caveat ??
            "Manual environmental context settings may differ from the predefined marine review presets.",
          anchor: contextAnchor,
          effectiveAnchor: effectiveContextState.effectiveAnchor,
          radiusPreset: contextRadiusPreset,
          radiusKm: contextRadiusKm,
          enabledSources: [
            ...(enabledContextSources.coops ? (["coops"] as const) : []),
            ...(enabledContextSources.ndbc ? (["ndbc"] as const) : [])
          ],
          centerAvailable: effectiveContextState.centerAvailable,
          fallbackReason: effectiveContextState.fallbackReason
        }
      }),
    [
      noaaCoopsContextQuery.data,
      ndbcContextQuery.data,
      selectedEnvironmentalContextPreset,
      activeEnvironmentalPreset,
      contextAnchor,
      contextRadiusPreset,
      contextRadiusKm,
      enabledContextSources,
      effectiveContextState
    ]
  );
  const contextIssueQueueSummary = useMemo(
    () => buildMarineContextIssueQueue(contextSourceRegistrySummary),
    [contextSourceRegistrySummary]
  );
  const contextFusionSummary = useMemo(
    () =>
      buildMarineContextFusionSummary({
        environmentalContextSummary,
        hydrologyContextSummary,
        scottishWaterContextSummary,
        contextSourceRegistrySummary,
        contextIssueQueueSummary
      }),
    [
      environmentalContextSummary,
      hydrologyContextSummary,
      scottishWaterContextSummary,
      contextSourceRegistrySummary,
      contextIssueQueueSummary
    ]
  );
  const contextReviewReportSummary = useMemo(
    () =>
      buildMarineContextReviewReport({
        fusionSummary: contextFusionSummary,
        issueQueueSummary: contextIssueQueueSummary
      }),
    [contextFusionSummary, contextIssueQueueSummary]
  );
  const currentContextSnapshot = useMemo(
    () =>
      buildMarineContextSnapshot({
        environmentalContextSummary,
        contextSourceRegistrySummary,
        focusedTarget
      }),
    [environmentalContextSummary, contextSourceRegistrySummary, focusedTarget]
  );
  const contextTimelineSummary = useMemo(
    () => buildMarineContextTimelineSummary(marineContextSnapshots),
    [marineContextSnapshots]
  );

  const focusedEvidenceInterpretation = useMemo(
    () =>
      buildMarineEvidenceInterpretation({
        focusedEvidenceRows,
        activeNavigationTarget: focusedTarget,
        vesselSummary: vesselSummaryQuery.data ?? null,
        viewportSummary: viewportSummaryQuery.data ?? null,
        chokepointSummary: chokepointSummaryQuery.data ?? null,
        environmentalContextSummary
      }),
    [
      focusedEvidenceRows,
      focusedTarget,
      vesselSummaryQuery.data,
      viewportSummaryQuery.data,
      chokepointSummaryQuery.data,
      environmentalContextSummary
    ]
  );

  const visibleInterpretationCards = useMemo(
    () => getMarineEvidenceInterpretationCards(focusedEvidenceInterpretation, interpretationMode),
    [focusedEvidenceInterpretation, interpretationMode]
  );

  const exportSummary = useMemo(
    () =>
      buildMarineEvidenceSummary({
        selectedVesselSummary: vesselSummaryQuery.data ?? null,
        viewportSummary: viewportSummaryQuery.data ?? null,
        chokepointSummary: chokepointSummaryQuery.data ?? null,
        visibleSlices: sortedSlices,
        controls: { chokepointFilter: sliceFilter, chokepointSort: sliceSort },
        activeNavigationTarget: focusedTarget,
        focusedEvidenceRows,
        focusedEvidenceInterpretation,
        focusedEvidenceInterpretationMode: interpretationMode,
        visibleInterpretationCards,
        noaaContextSummary,
        ndbcContextSummary,
        scottishWaterContextSummary,
        vigicruesContextSummary,
        irelandOpwContextSummary,
        hydrologyContextSummary,
        contextFusionSummary,
        contextReviewReportSummary,
        contextSourceRegistrySummary,
        contextTimelineSummary,
        contextIssueQueueSummary,
        environmentalContextSummary
      }),
    [
      vesselSummaryQuery.data,
      viewportSummaryQuery.data,
      chokepointSummaryQuery.data,
      sortedSlices,
      sliceFilter,
      sliceSort,
      focusedTarget,
      focusedEvidenceRows,
      focusedEvidenceInterpretation,
      interpretationMode,
      visibleInterpretationCards,
      noaaContextSummary,
      ndbcContextSummary,
      scottishWaterContextSummary,
      vigicruesContextSummary,
      irelandOpwContextSummary,
      hydrologyContextSummary,
      contextFusionSummary,
      contextReviewReportSummary,
      contextSourceRegistrySummary,
      contextTimelineSummary,
      contextIssueQueueSummary,
      environmentalContextSummary
    ]
  );

  const exportSummaryKey = useMemo(
    () => JSON.stringify({ lines: exportSummary.displayLines, metadata: exportSummary.metadata }),
    [exportSummary.displayLines, exportSummary.metadata]
  );

  useEffect(() => {
    if (lastMarineEvidenceSummaryKeyRef.current === exportSummaryKey) {
      return;
    }
    lastMarineEvidenceSummaryKeyRef.current = exportSummaryKey;
    setMarineEvidenceSummary({
      lines: exportSummary.displayLines,
      metadata: exportSummary.metadata
    });
  }, [exportSummary.displayLines, exportSummary.metadata, exportSummaryKey, setMarineEvidenceSummary]);

  useEffect(() => {
    setMarineContextSnapshots((current) => reduceMarineContextSnapshots(current, currentContextSnapshot));
  }, [currentContextSnapshot]);

  const focusedSliceVisible = useMemo(() => {
    if (!focusedTarget || focusedTarget.kind !== "chokepoint-slice") {
      return true;
    }
    return sortedSlices.some(
      (slice) =>
        slice.sliceStartAt === focusedTarget.timeWindowStart &&
        slice.sliceEndAt === focusedTarget.timeWindowEnd
    );
  }, [focusedTarget, sortedSlices]);

  const focusedStaleMessage = useMemo(() => {
    if (!focusedTarget) return null;
    if (focusedTarget.kind === "chokepoint-slice" && !focusedSliceVisible) {
      return "Focused target not visible under current filters";
    }
    if (!focusedTarget.directReplayTarget) {
      return focusedTarget.unavailableReason ?? "Summary-level signal only";
    }
    return null;
  }, [focusedTarget, focusedSliceVisible]);

  const anyLoading =
    vesselsQuery.isLoading ||
    vesselSummaryQuery.isLoading ||
    viewportSummaryQuery.isLoading ||
    chokepointSummaryQuery.isLoading;
  const imageryContext = buildActiveImageryContextFromHud(hud);

  return (
    <div className="panel__section" data-testid="marine-anomaly-section">
      <p className="panel__eyebrow">Marine Attention Priority</p>
      <div className="empty-state compact">
        <p>Attention priority is a review signal, not proof of intent.</p>
      </div>
      <ImageryContextBadge context={imageryContext} isReplayContext={selectedReplayIndex != null} />
      {anyLoading ? <span className="marine-anomaly-muted">Loading marine anomaly summaries.</span> : null}
      {environmentalContextSummary ? (
        <div className="data-card data-card--compact marine-anomaly-panel" data-testid="marine-environmental-context">
          <strong>Marine Environmental Context</strong>
          <div className="marine-anomaly-controls">
            <label data-testid="marine-environmental-preset">
              <span>Preset</span>
              <select
                value={selectedEnvironmentalContextPreset}
                onChange={(event) => {
                  const nextPresetId =
                    event.currentTarget.value as MarineEnvironmentalContextPresetSelection;
                  setSelectedEnvironmentalContextPreset(nextPresetId);
                  if (nextPresetId === "custom") {
                    return;
                  }
                  const nextPreset = getMarineEnvironmentalContextPreset(nextPresetId);
                  setContextAnchor(nextPreset.anchor);
                  setContextRadiusPreset(nextPreset.radiusPreset);
                  setEnabledContextSources({
                    coops: nextPreset.enabledSources.includes("coops"),
                    ndbc: nextPreset.enabledSources.includes("ndbc")
                  });
                }}
              >
                <option value="chokepoint-review">chokepoint review</option>
                <option value="selected-vessel-review">selected vessel review</option>
                <option value="regional-marine-context">regional marine context</option>
                <option value="water-level-current-focus">water level/current focus</option>
                <option value="buoy-weather-focus">buoy/weather focus</option>
                <option value="custom">custom</option>
              </select>
            </label>
            <label data-testid="marine-environmental-anchor">
              <span>Context anchor</span>
              <select
                value={contextAnchor}
                onChange={(event) => {
                  const nextAnchor = event.currentTarget.value as MarineEnvironmentalContextAnchor;
                  setContextAnchor(nextAnchor);
                  syncEnvironmentalPreset(nextAnchor, contextRadiusPreset, enabledContextSources);
                }}
              >
                <option value="selected-vessel">selected vessel</option>
                <option value="viewport">viewport</option>
                <option value="chokepoint">chokepoint</option>
              </select>
            </label>
            <label data-testid="marine-environmental-radius">
              <span>Radius</span>
              <select
                value={contextRadiusPreset}
                onChange={(event) => {
                  const nextRadiusPreset =
                    event.currentTarget.value as MarineEnvironmentalContextRadiusPreset;
                  setContextRadiusPreset(nextRadiusPreset);
                  syncEnvironmentalPreset(contextAnchor, nextRadiusPreset, enabledContextSources);
                }}
              >
                <option value="small">small</option>
                <option value="medium">medium</option>
                <option value="large">large</option>
              </select>
            </label>
            <label data-testid="marine-environmental-source-coops">
              <input
                type="checkbox"
                checked={enabledContextSources.coops}
                onChange={(event) => {
                  const nextSources = {
                    ...enabledContextSources,
                    coops: event.currentTarget.checked
                  };
                  setEnabledContextSources(nextSources);
                  syncEnvironmentalPreset(contextAnchor, contextRadiusPreset, nextSources);
                }}
              />
              <span>CO-OPS</span>
            </label>
            <label data-testid="marine-environmental-source-ndbc">
              <input
                type="checkbox"
                checked={enabledContextSources.ndbc}
                onChange={(event) => {
                  const nextSources = {
                    ...enabledContextSources,
                    ndbc: event.currentTarget.checked
                  };
                  setEnabledContextSources(nextSources);
                  syncEnvironmentalPreset(contextAnchor, contextRadiusPreset, nextSources);
                }}
              />
              <span>NDBC</span>
            </label>
          </div>
          <span>{environmentalContextSummary.exportLines[0]}</span>
          <span className="marine-anomaly-muted" data-testid="marine-environmental-preset-summary">
            Preset {environmentalContextSummary.metadata.presetLabel}
            {environmentalContextSummary.metadata.isCustomPreset ? " | Custom context settings" : ""}
          </span>
          <span className="marine-anomaly-muted">
            {environmentalContextSummary.metadata.presetCaveat ??
              "Environmental context presets support review context only."}
          </span>
          <span className="marine-anomaly-muted" data-testid="marine-environmental-context-caveat">
            {environmentalContextSummary.environmentalCaveatSummary.caveats[0]}
          </span>
          <span className="marine-anomaly-muted">
            Anchor {environmentalContextSummary.metadata.effectiveAnchor} | Radius{" "}
            {environmentalContextSummary.metadata.radiusKm} km | Sources{" "}
            {environmentalContextSummary.metadata.enabledSources.length > 0
              ? environmentalContextSummary.metadata.enabledSources.join(", ")
              : "none"}
          </span>
          {environmentalContextSummary.topWaterLevelStation ? (
            <span className="marine-anomaly-muted">
              Water level: {environmentalContextSummary.topWaterLevelStation.stationName} |{" "}
              {environmentalContextSummary.topWaterLevelStation.valueM.toFixed(2)} m (
              {environmentalContextSummary.topWaterLevelStation.datum})
            </span>
          ) : null}
          {environmentalContextSummary.topCurrentStation ? (
            <span className="marine-anomaly-muted">
              Current: {environmentalContextSummary.topCurrentStation.stationName} |{" "}
              {environmentalContextSummary.topCurrentStation.speedKts.toFixed(1)} kts
              {environmentalContextSummary.topCurrentStation.directionCardinal
                ? ` ${environmentalContextSummary.topCurrentStation.directionCardinal}`
                : ""}
            </span>
          ) : null}
          {environmentalContextSummary.topBuoyStation ? (
            <span className="marine-anomaly-muted">
              Buoy: {environmentalContextSummary.topBuoyStation.stationName} |{" "}
              {environmentalContextSummary.topBuoyStation.observationSummary}
            </span>
          ) : null}
          {environmentalContextSummary.windSummary ? (
            <span className="marine-anomaly-muted">
              Wind/wave: {environmentalContextSummary.windSummary}
              {environmentalContextSummary.waveSummary ? ` | ${environmentalContextSummary.waveSummary}` : ""}
            </span>
          ) : null}
          {environmentalContextSummary.pressureSummary || environmentalContextSummary.temperatureSummary ? (
            <span className="marine-anomaly-muted">
              {environmentalContextSummary.pressureSummary ?? ""}
              {environmentalContextSummary.pressureSummary && environmentalContextSummary.temperatureSummary
                ? " | "
                : ""}
              {environmentalContextSummary.temperatureSummary ?? ""}
            </span>
          ) : null}
          <span className="marine-anomaly-muted">
            Caveat: {environmentalContextSummary.caveats[0] ?? "Environmental context is not vessel-intent evidence."}
          </span>
        </div>
      ) : null}
      {contextSourceRegistrySummary ? (
        <div className="data-card data-card--compact marine-anomaly-panel" data-testid="marine-context-sources">
          <strong>Marine Context Sources</strong>
          <span>{contextSourceRegistrySummary.exportLines[0]}</span>
          {contextSourceRegistrySummary.rows.map((row) => (
            <div key={row.sourceId} className="stack stack--tight" data-testid="marine-context-source-row">
              <span>
                {row.label} | {row.availability} | {row.sourceMode}
              </span>
              <span className="marine-anomaly-muted">
                {row.nearbyCount} nearby
                {row.activeCount != null ? ` | ${row.activeCount} active` : ""}
                {row.topSummary ? ` | ${row.topSummary}` : ""}
              </span>
              {row.caveats[0] ? (
                <span className="marine-anomaly-muted">Caveat: {row.caveats[0]}</span>
              ) : null}
            </div>
          ))}
        </div>
      ) : null}
      {contextTimelineSummary ? (
        <div className="data-card data-card--compact marine-anomaly-panel" data-testid="marine-context-timeline">
          <strong>Marine Context Timeline</strong>
          <span>
            {contextTimelineSummary.snapshotCount} snapshot
            {contextTimelineSummary.snapshotCount === 1 ? "" : "s"} in this session
          </span>
          {contextTimelineSummary.currentSnapshot ? (
            <>
              <div className="stack stack--tight" data-testid="marine-context-timeline-item">
                <span>
                  {contextTimelineSummary.currentSnapshot.presetLabel}
                  {contextTimelineSummary.currentSnapshot.isCustomPreset ? " | Custom context settings" : ""}
                </span>
                <span className="marine-anomaly-muted">
                  {contextTimelineSummary.currentSnapshot.effectiveAnchor} | {contextTimelineSummary.currentSnapshot.radiusKm} km | {contextTimelineSummary.currentSnapshot.enabledSources.join(", ")}
                </span>
                <span className="marine-anomaly-muted">
                  {contextTimelineSummary.currentSnapshot.availableSourceCount}/{contextTimelineSummary.currentSnapshot.sourceCount} sources loaded
                </span>
                {contextTimelineSummary.currentSnapshot.caveats[0] ? (
                  <span className="marine-anomaly-muted">
                    Caveat: {contextTimelineSummary.currentSnapshot.caveats[0]}
                  </span>
                ) : null}
              </div>
              {contextTimelineSummary.previousSnapshot ? (
                <div className="stack stack--tight" data-testid="marine-context-timeline-item">
                  <span>{contextTimelineSummary.previousSnapshot.presetLabel}</span>
                  <span className="marine-anomaly-muted">
                    {contextTimelineSummary.previousSnapshot.effectiveAnchor} | {contextTimelineSummary.previousSnapshot.radiusKm} km | {contextTimelineSummary.previousSnapshot.enabledSources.join(", ")}
                  </span>
                </div>
              ) : null}
            </>
          ) : (
            <span className="marine-anomaly-muted">No marine context snapshots recorded yet.</span>
          )}
          <div className="stack stack--actions">
            <button
              type="button"
              className="ghost-button ghost-button--small"
              data-testid="marine-context-timeline-clear"
              onClick={() => setMarineContextSnapshots(clearMarineContextSnapshots())}
            >
              Clear context history
            </button>
          </div>
        </div>
      ) : null}
      {contextIssueQueueSummary ? (
        <div className="data-card data-card--compact marine-anomaly-panel" data-testid="marine-context-issues">
          <strong>Marine Context Issues</strong>
          <span>
            {contextIssueQueueSummary.issueCount} issue
            {contextIssueQueueSummary.issueCount === 1 ? "" : "s"} | {contextIssueQueueSummary.warningCount} warning |{" "}
            {contextIssueQueueSummary.noticeCount} notice | {contextIssueQueueSummary.infoCount} info
          </span>
          {contextIssueQueueSummary.topIssues.length > 0 ? (
            contextIssueQueueSummary.topIssues.map((issue) => (
              <div
                key={issue.id}
                className="stack stack--tight"
                data-testid="marine-context-issue-row"
              >
                <span>
                  {issue.sourceLabel} | {issue.severity} | {issue.title}
                </span>
                <span className="marine-anomaly-muted">{issue.detail}</span>
                <span className="marine-anomaly-muted">
                  Recommended action: {issue.recommendedAction}
                </span>
                <span className="marine-anomaly-muted">Caveat: {issue.caveat}</span>
              </div>
            ))
          ) : (
            <span className="marine-anomaly-muted">
              No source-health issues surfaced from current marine context sources.
            </span>
          )}
        </div>
      ) : null}
      {contextFusionSummary ? (
        <div className="data-card data-card--compact marine-anomaly-panel" data-testid="marine-context-fusion">
          <strong>Marine Context Fusion</strong>
          <span>{contextFusionSummary.overallAvailabilityLine}</span>
          <span className="marine-anomaly-muted">{contextFusionSummary.exportReadinessLine}</span>
          {contextFusionSummary.familyLines.map((line) => (
            <div key={line.family} className="stack stack--tight">
              <span>
                {line.label} | {line.availability}
              </span>
              <span className="marine-anomaly-muted">{line.detail}</span>
              {line.topSummary ? (
                <span className="marine-anomaly-muted">{line.topSummary}</span>
              ) : null}
              {line.caveat ? (
                <span className="marine-anomaly-muted">Caveat: {line.caveat}</span>
              ) : null}
            </div>
          ))}
          {contextFusionSummary.highestPriorityCaveats.map((caveat) => (
            <span key={caveat} className="marine-anomaly-muted">
              Caveat: {caveat}
            </span>
          ))}
        </div>
      ) : null}
      {contextReviewReportSummary ? (
        <div className="data-card data-card--compact marine-anomaly-panel" data-testid="marine-context-review-report">
          <strong>{contextReviewReportSummary.title}</strong>
          <span>{contextReviewReportSummary.summaryLine}</span>
          <span className="marine-anomaly-muted">{contextReviewReportSummary.sourceHealthSummary}</span>
          <span className="marine-anomaly-muted">
            Context families: {contextReviewReportSummary.contextFamiliesIncluded.join(" | ")}
          </span>
          {contextReviewReportSummary.reviewNeededItems.map((item) => (
            <span key={item} className="marine-anomaly-muted">
              Review next: {item}
            </span>
          ))}
          {contextReviewReportSummary.exportCaveatLines.slice(0, 2).map((line) => (
            <span key={line} className="marine-anomaly-muted">
              Caveat: {line}
            </span>
          ))}
          {contextReviewReportSummary.doesNotProveLines.slice(0, 2).map((line) => (
            <span key={line} className="marine-anomaly-muted">
              Does not prove: {line}
            </span>
          ))}
        </div>
      ) : null}
      {hydrologyContextSummary ? (
        <div className="data-card data-card--compact marine-anomaly-panel" data-testid="marine-hydrology-context">
          <strong>Marine Hydrology Context</strong>
          <span>{hydrologyContextSummary.sourceLine}</span>
          {hydrologyContextSummary.reviewLines.map((line) => (
            <div key={line.sourceId} className="stack stack--tight">
              <span>{line.label}</span>
              <span className="marine-anomaly-muted">{line.detail}</span>
              {line.caveat ? <span className="marine-anomaly-muted">Caveat: {line.caveat}</span> : null}
            </div>
          ))}
          <span className="marine-anomaly-muted">
            Caveat: {hydrologyContextSummary.metadata.caveats[0]}
          </span>
        </div>
      ) : null}
      {enabledContextSources.coops && noaaCoopsContextQuery.data ? (
        <div className="data-card data-card--compact marine-anomaly-panel" data-testid="marine-noaa-context">
          <strong>NOAA CO-OPS Tides &amp; Currents</strong>
          <span>{noaaContextSummary?.sourceLine ?? "NOAA CO-OPS context loaded."}</span>
          {noaaContextSummary?.stationLines.map((station) => (
            <div key={station.stationId} className="stack stack--tight">
              <span>{station.label}</span>
              <span className="marine-anomaly-muted">{station.observationLine}</span>
              <span className="marine-anomaly-muted">{station.detailLine}</span>
              {station.caveat ? <span className="marine-anomaly-muted">Caveat: {station.caveat}</span> : null}
            </div>
          ))}
          {noaaCoopsContextQuery.data.count === 0 ? (
            <span className="marine-anomaly-muted">No nearby NOAA CO-OPS station context in this window.</span>
          ) : null}
          {noaaCoopsContextQuery.data.sourceHealth.caveat ? (
            <span className="marine-anomaly-muted">{noaaCoopsContextQuery.data.sourceHealth.caveat}</span>
          ) : null}
        </div>
      ) : enabledContextSources.coops && noaaCoopsContextQuery.isLoading ? (
        <div className="empty-state compact" data-testid="marine-noaa-context-loading">
          <p>Loading NOAA CO-OPS context.</p>
        </div>
      ) : enabledContextSources.coops && noaaCoopsContextQuery.isError ? (
        <div className="empty-state compact" data-testid="marine-noaa-context-error">
          <p>NOAA CO-OPS context unavailable.</p>
          <span>Marine environmental context is limited until the source loads.</span>
        </div>
      ) : null}
      {enabledContextSources.ndbc && ndbcContextQuery.data ? (
        <div className="data-card data-card--compact marine-anomaly-panel" data-testid="marine-ndbc-context">
          <strong>NOAA NDBC Realtime Buoys</strong>
          <span>{ndbcContextSummary?.sourceLine ?? "NOAA NDBC context loaded."}</span>
          {ndbcContextSummary?.stationLines.map((station) => (
            <div key={station.stationId} className="stack stack--tight">
              <span>{station.label}</span>
              <span className="marine-anomaly-muted">{station.observationLine}</span>
              <span className="marine-anomaly-muted">{station.detailLine}</span>
              {station.caveat ? <span className="marine-anomaly-muted">Caveat: {station.caveat}</span> : null}
            </div>
          ))}
          {ndbcContextQuery.data.count === 0 ? (
            <span className="marine-anomaly-muted">No nearby NOAA NDBC buoy context in this window.</span>
          ) : null}
          {ndbcContextQuery.data.sourceHealth.caveat ? (
            <span className="marine-anomaly-muted">{ndbcContextQuery.data.sourceHealth.caveat}</span>
          ) : null}
        </div>
      ) : enabledContextSources.ndbc && ndbcContextQuery.isLoading ? (
        <div className="empty-state compact" data-testid="marine-ndbc-context-loading">
          <p>Loading NOAA NDBC context.</p>
        </div>
      ) : enabledContextSources.ndbc && ndbcContextQuery.isError ? (
        <div className="empty-state compact" data-testid="marine-ndbc-context-error">
          <p>NOAA NDBC context unavailable.</p>
          <span>Marine weather and wave context is limited until the source loads.</span>
        </div>
      ) : null}
      {scottishWaterContextQuery.data ? (
        <div className="data-card data-card--compact marine-anomaly-panel" data-testid="marine-scottish-water-context">
          <strong>Scottish Water Overflows</strong>
          <span>{scottishWaterContextSummary?.sourceLine ?? "Scottish Water overflow context loaded."}</span>
          {scottishWaterContextSummary?.eventLines.map((event) => (
            <div key={event.eventId} className="stack stack--tight">
              <span>{event.label}</span>
              <span className="marine-anomaly-muted">{event.statusLine}</span>
              <span className="marine-anomaly-muted">{event.detailLine}</span>
              {event.caveat ? <span className="marine-anomaly-muted">Caveat: {event.caveat}</span> : null}
            </div>
          ))}
          {scottishWaterContextQuery.data.count === 0 ? (
            <span className="marine-anomaly-muted">
              No nearby Scottish Water overflow monitor context in this window.
            </span>
          ) : null}
          {scottishWaterContextQuery.data.sourceHealth.caveat ? (
            <span className="marine-anomaly-muted">{scottishWaterContextQuery.data.sourceHealth.caveat}</span>
          ) : null}
        </div>
      ) : scottishWaterContextQuery.isLoading ? (
        <div className="empty-state compact" data-testid="marine-scottish-water-context-loading">
          <p>Loading Scottish Water overflow context.</p>
        </div>
      ) : scottishWaterContextQuery.isError ? (
        <div className="empty-state compact" data-testid="marine-scottish-water-context-error">
          <p>Scottish Water overflow context unavailable.</p>
          <span>Marine coastal infrastructure context is limited until the source loads.</span>
        </div>
      ) : null}
      {vigicruesContextQuery.data ? (
        <div className="data-card data-card--compact marine-anomaly-panel" data-testid="marine-vigicrues-context">
          <strong>France Vigicrues Hydrometry</strong>
          <span>{vigicruesContextSummary?.sourceLine ?? "Vigicrues hydrometry context loaded."}</span>
          {vigicruesContextSummary?.stationLines.map((station) => (
            <div key={station.stationId} className="stack stack--tight">
              <span>{station.label}</span>
              <span className="marine-anomaly-muted">{station.observationLine}</span>
              <span className="marine-anomaly-muted">{station.detailLine}</span>
              {station.caveat ? <span className="marine-anomaly-muted">Caveat: {station.caveat}</span> : null}
            </div>
          ))}
          {vigicruesContextQuery.data.count === 0 ? (
            <span className="marine-anomaly-muted">
              No nearby Vigicrues hydrometry station context in this window.
            </span>
          ) : null}
          {vigicruesContextQuery.data.sourceHealth.caveat ? (
            <span className="marine-anomaly-muted">{vigicruesContextQuery.data.sourceHealth.caveat}</span>
          ) : null}
        </div>
      ) : vigicruesContextQuery.isLoading ? (
        <div className="empty-state compact" data-testid="marine-vigicrues-context-loading">
          <p>Loading Vigicrues hydrometry context.</p>
        </div>
      ) : vigicruesContextQuery.isError ? (
        <div className="empty-state compact" data-testid="marine-vigicrues-context-error">
          <p>Vigicrues hydrometry context unavailable.</p>
          <span>Marine river-condition context is limited until the source loads.</span>
        </div>
      ) : null}
      {irelandOpwContextQuery.data ? (
        <div className="data-card data-card--compact marine-anomaly-panel" data-testid="marine-ireland-opw-context">
          <strong>Ireland OPW Water Level</strong>
          <span>{irelandOpwContextSummary?.sourceLine ?? "Ireland OPW water-level context loaded."}</span>
          {irelandOpwContextSummary?.stationLines.map((station) => (
            <div key={station.stationId} className="stack stack--tight">
              <span>{station.label}</span>
              <span className="marine-anomaly-muted">{station.observationLine}</span>
              <span className="marine-anomaly-muted">{station.detailLine}</span>
              {station.caveat ? <span className="marine-anomaly-muted">Caveat: {station.caveat}</span> : null}
            </div>
          ))}
          {irelandOpwContextQuery.data.count === 0 ? (
            <span className="marine-anomaly-muted">
              No nearby Ireland OPW water-level station context in this window.
            </span>
          ) : null}
          {irelandOpwContextQuery.data.sourceHealth.caveat ? (
            <span className="marine-anomaly-muted">{irelandOpwContextQuery.data.sourceHealth.caveat}</span>
          ) : null}
        </div>
      ) : irelandOpwContextQuery.isLoading ? (
        <div className="empty-state compact" data-testid="marine-ireland-opw-context-loading">
          <p>Loading Ireland OPW water-level context.</p>
        </div>
      ) : irelandOpwContextQuery.isError ? (
        <div className="empty-state compact" data-testid="marine-ireland-opw-context-error">
          <p>Ireland OPW water-level context unavailable.</p>
          <span>Marine hydrology context is limited until the source loads.</span>
        </div>
      ) : null}
      {vesselsQuery.isError ? (
        <div className="empty-state compact" data-testid="marine-vessels-error">
          <p>Marine vessel list unavailable.</p>
          <span>Attention ranking is limited until marine vessel data is available.</span>
        </div>
      ) : null}

      {selectedMarineVesselId == null && !vesselsQuery.isLoading ? (
        <div className="empty-state compact" data-testid="marine-no-selected-vessel">
          <p>No selected vessel.</p>
          <span>Select a marine vessel to inspect attention priority.</span>
        </div>
      ) : null}

      {vesselSummaryQuery.isLoading ? (
        <div className="empty-state compact" data-testid="marine-vessel-loading">
          <p>Loading selected vessel summary.</p>
        </div>
      ) : null}

      {vesselSummaryQuery.isError ? (
        <div className="empty-state compact" data-testid="marine-vessel-error">
          <p>Selected vessel summary unavailable.</p>
          <span>No notable anomaly in this window can be evaluated right now.</span>
        </div>
      ) : null}

      {vesselSummaryQuery.data ? (
        <>
          <MarineAnomalyPanel
            title={`Selected Vessel: ${vesselSummaryQuery.data.latestObserved?.label ?? vesselSummaryQuery.data.vesselId}`}
            anomaly={vesselSummaryQuery.data.anomaly}
            note="Notable activity from vessel summary window."
          />
          <div className="stack stack--actions">
            {vesselSummaryQuery.data.mostRecentResumedObservation ? (
              <button
                type="button"
                className="ghost-button ghost-button--small"
                data-testid="marine-focus-vessel-event"
                onClick={() => {
                  const resumed = vesselSummaryQuery.data?.mostRecentResumedObservation;
                  if (!resumed) {
                    return;
                  }
                  setFocusedTarget(
                    fromGapEvent(vesselSummaryQuery.data.vesselId, resumed, "Focus replay event")
                  );
                }}
              >
                Focus replay event
              </button>
            ) : (
              <button type="button" className="ghost-button ghost-button--small" disabled>
                Replay target unavailable for this reason
              </button>
            )}
          </div>
        </>
      ) : (
        <div className="empty-state compact" data-testid="marine-vessel-low-state">
          <p>No selected vessel anomaly summary.</p>
          <span>Low or unavailable marine vessel priority for this context.</span>
        </div>
      )}

      {viewportSummaryQuery.data ? (
        <>
          <MarineAnomalyPanel
            title="Viewport Notable Activity"
            anomaly={viewportSummaryQuery.data.anomaly}
            note="Does this time/area window deserve attention?"
          />
          <div className="stack stack--actions">
            <button
              type="button"
              className="ghost-button ghost-button--small"
              data-testid="marine-focus-viewport-window"
              onClick={() => setFocusedTarget(viewportNavigationTarget(viewportSummaryQuery.data))}
            >
              Focus viewport window
            </button>
          </div>
        </>
      ) : viewportSummaryQuery.isLoading ? (
        <div className="empty-state compact" data-testid="marine-viewport-loading">
          <p>Loading viewport summary.</p>
        </div>
      ) : (
        <div className="empty-state compact" data-testid="marine-viewport-error">
          <p>Viewport summary unavailable.</p>
          <span>No notable anomaly in this window can be evaluated from current data.</span>
        </div>
      )}

      {chokepointSummaryQuery.data ? (
        <div className="data-card marine-anomaly-panel" data-testid="marine-chokepoint-priority">
          <strong>Chokepoint Slice Prioritization</strong>
          <div className="marine-anomaly-controls">
            <label data-testid="marine-chokepoint-filter">
              <span>Filter</span>
              <select value={sliceFilter} onChange={(e) => setSliceFilter(e.currentTarget.value as SliceFilter)}>
                <option value="all">all</option>
                <option value="medium+">medium+</option>
                <option value="high">high only</option>
              </select>
            </label>
            <label data-testid="marine-chokepoint-sort">
              <span>Sort</span>
              <select value={sliceSort} onChange={(e) => setSliceSort(e.currentTarget.value as SliceSort)}>
                <option value="priority">priority rank</option>
                <option value="score">score</option>
              </select>
            </label>
          </div>
          <div className="stack" data-testid="marine-chokepoint-slice-list">
            {sortedSlices.map((slice) => (
              <SliceCard
                key={`${slice.sliceStartAt}-${slice.sliceEndAt}`}
                slice={slice}
                onFocus={() => setFocusedTarget(chokepointSliceNavigationTarget(slice))}
                focused={
                  focusedTarget?.kind === "chokepoint-slice" &&
                  focusedTarget.timeWindowStart === slice.sliceStartAt &&
                  focusedTarget.timeWindowEnd === slice.sliceEndAt
                }
              />
            ))}
            {sortedSlices.length === 0 ? (
              <div className="empty-state compact" data-testid="marine-chokepoint-empty">
                <p>No chokepoint slices match this filter.</p>
              </div>
            ) : null}
          </div>
        </div>
      ) : chokepointSummaryQuery.isLoading ? (
        <div className="empty-state compact" data-testid="marine-chokepoint-loading">
          <p>Loading chokepoint summary.</p>
        </div>
      ) : (
        <div className="empty-state compact" data-testid="marine-chokepoint-error">
          <p>Chokepoint summary unavailable.</p>
        </div>
      )}

      {attentionItems.length > 0 ? (
        <div className="data-card marine-anomaly-panel" data-testid="marine-attention-queue">
          <strong>Marine Attention Queue</strong>
          <div className="stack">
            {attentionItems.map((item, index) => (
              <button
                key={`${item.type}-${index}`}
                type="button"
                className={clsx(
                  "data-card data-card--compact marine-queue-item-button",
                  focusedTarget?.label === item.target?.label && "marine-target-focus"
                )}
                data-testid="marine-attention-queue-item"
                onClick={() => {
                  if (item.target) setFocusedTarget(item.target);
                }}
              >
                <span>{item.type}</span>
                <strong>{item.label}</strong>
                <span>{item.level.toUpperCase()} | {item.score.toFixed(1)}</span>
                <span>{item.reason}</span>
                <span className="marine-anomaly-muted">
                  {item.caveat ? `Caveat: ${item.caveat}` : "Caveats: 0"}
                </span>
                {!item.target?.directReplayTarget ? (
                  <span className="marine-anomaly-muted">
                    {item.target?.unavailableReason ?? "Summary-level signal only"}
                  </span>
                ) : null}
              </button>
            ))}
          </div>
        </div>
      ) : (
        <div className="empty-state compact" data-testid="marine-attention-queue-empty">
          <p>Attention queue unavailable for current data.</p>
        </div>
      )}

      <div className="data-card data-card--compact marine-anomaly-panel" data-testid="marine-export-preview">
        <strong>Snapshot Marine Evidence</strong>
        {exportSummary.displayLines.slice(0, 4).map((line) => (
          <span key={line}>{line}</span>
        ))}
      </div>
      {focusedTarget ? (
        <div
          className={clsx(
            "data-card data-card--compact marine-anomaly-panel",
            focusedStaleMessage && "marine-target-stale"
          )}
          data-testid="marine-focused-target"
        >
          <strong>Focused replay target</strong>
          <span>{focusedTarget.label}</span>
          <span>{focusedTarget.kind}</span>
          <span>
            {focusedTarget.timeWindowStart && focusedTarget.timeWindowEnd
              ? `${focusedTarget.timeWindowStart} to ${focusedTarget.timeWindowEnd}`
              : focusedTarget.timestamp ?? "Summary-level signal only"}
          </span>
          {focusedStaleMessage ? (
            <span className="marine-anomaly-muted" data-testid="marine-focused-target-stale">
              {focusedStaleMessage}
            </span>
          ) : null}
          {focusedTarget.caveat ? (
            <span className="marine-anomaly-muted">{focusedTarget.caveat}</span>
          ) : null}
        </div>
      ) : null}
      <div className="data-card marine-anomaly-panel" data-testid="marine-focused-evidence">
        <strong>Focused Replay Evidence</strong>
        {focusedTarget == null ? (
          <span className="marine-anomaly-muted">Focus an anomaly item to inspect replay evidence.</span>
        ) : (
          <>
            <span className="marine-anomaly-muted">
              {focusedTarget.label} ({focusedTarget.kind})
            </span>
            <div className="stack">
              {focusedEvidenceRows.map((row) => (
                <div
                  key={row.id}
                  className={clsx(
                    "data-card data-card--compact marine-evidence-row",
                    row.isFocused && "marine-target-focus",
                    row.observedOrInferred === "summary" && "marine-evidence-row--summary"
                  )}
                  data-testid="marine-evidence-row"
                >
                  <strong>{row.label}</strong>
                  <span className="marine-anomaly-muted">
                    {row.timeWindowStart && row.timeWindowEnd
                      ? `${row.timeWindowStart} to ${row.timeWindowEnd}`
                      : row.timestamp ?? "Summary-level signal only"}
                  </span>
                  <span>{row.detail}</span>
                  <span className="marine-anomaly-muted">
                    {row.observedOrInferred} · {row.kind}
                  </span>
                  {row.caveat ? (
                    <span className="marine-anomaly-muted">Caveat: {row.caveat}</span>
                  ) : null}
                </div>
              ))}
              {focusedEvidenceRows.length === 0 ? (
                <span className="marine-anomaly-muted">Replay target unavailable for this reason.</span>
              ) : null}
            </div>
            <div className="data-card data-card--compact" data-testid="marine-evidence-interpretation">
              <strong>Evidence Interpretation</strong>
              <label className="field-row" data-testid="marine-evidence-interpretation-mode">
                <span>Display mode</span>
                <select
                  className="panel__select"
                  value={interpretationMode}
                  onChange={(event) =>
                    setInterpretationMode(
                      event.currentTarget.value as MarineEvidenceInterpretationMode
                    )
                  }
                >
                  <option value="compact">Compact</option>
                  <option value="detailed">Detailed</option>
                  <option value="evidence-only">Evidence only</option>
                  <option value="caveats-first">Caveats first</option>
                </select>
              </label>
              <span>Why this was prioritized: {focusedEvidenceInterpretation.priorityExplanation}</span>
              <span className="marine-anomaly-muted">
                Trust/caveat: {focusedEvidenceInterpretation.trustLevel}
              </span>
              <span className="marine-anomaly-muted" data-testid="marine-focused-environmental-caveat">
                {environmentalContextSummary?.environmentalCaveatSummary.caveats[0] ??
                  "Environmental context unavailable for this review window."}
              </span>
              <div className="stack">
                {visibleInterpretationCards.map((card, index) => (
                  <div
                    key={`${card.kind}-${index}`}
                    className="data-card data-card--compact marine-evidence-row"
                    data-testid="marine-interpretation-card"
                  >
                    <strong>{card.label}</strong>
                    <span>{card.value}</span>
                    <span className="marine-anomaly-muted">{card.detail}</span>
                    <span className="marine-anomaly-muted">
                      {card.basis} · {card.severity}
                    </span>
                    {card.caveat ? (
                      <span className="marine-anomaly-muted">Caveat: {card.caveat}</span>
                    ) : null}
                  </div>
                ))}
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

function SliceCard({
  slice,
  onFocus,
  focused
}: {
  slice: MarineChokepointSliceSummary;
  onFocus: () => void;
  focused?: boolean;
}) {
  return (
    <div
      className={clsx("data-card data-card--compact marine-slice-card", focused && "marine-target-focus")}
      data-testid="marine-chokepoint-slice-item"
    >
      <strong>Rank #{slice.anomaly.priorityRank ?? "-"}</strong>
      <span>{slice.anomaly.displayLabel}</span>
      <span>{slice.anomaly.level.toUpperCase()} | {slice.anomaly.score.toFixed(1)}</span>
      <span>{slice.anomaly.reasons[0] ?? "No reason stated."}</span>
      {slice.anomaly.caveats[0] ? (
        <span className="marine-anomaly-muted">{slice.anomaly.caveats[0]}</span>
      ) : null}
      <button
        type="button"
        className="ghost-button ghost-button--small"
        data-testid="marine-focus-slice"
        onClick={onFocus}
      >
        Focus slice window
      </button>
    </div>
  );
}
