import type { EnvironmentalEventFilterState, HudState, PinnedEnvironmentalEvent } from "../../lib/store";
import type {
  EarthquakeEventsMetadata,
  EonetEventsMetadata
} from "../../types/api";
import type { EarthquakeEntity, EonetEntity, SceneEntity } from "../../types/entities";

type EnvironmentalSourceKey = "earthquakes" | "eonet";
type SourceState = "disabled" | "loading" | "error" | "empty" | "ready";
type SourceHealthState = "loaded" | "loading" | "empty" | "stale" | "error" | "disabled" | "unknown";
type SourceMode = "fixture" | "live" | "unknown";
type RelevanceBand = "very-near" | "near" | "regional" | "distant";
type RelevanceAnchor = "view-center" | "selected-environmental-event";
type TimeAdjacencyBand = "same-hour" | "same-day" | "same-week" | "later";

const VERY_NEAR_KM = 50;
const NEAR_KM = 250;
const REGIONAL_KM = 1000;
const MIN_VIEW_RADIUS_KM = 75;
const MAX_VIEW_RADIUS_KM = 3000;
const FRESH_MS = 5 * 60 * 1000;
const RECENT_MS = 30 * 60 * 1000;
const POSSIBLY_STALE_MS = 2 * 60 * 60 * 1000;
const SAME_HOUR_MS = 60 * 60 * 1000;
const SAME_DAY_MS = 24 * 60 * 60 * 1000;
const SAME_WEEK_MS = 7 * 24 * 60 * 60 * 1000;

export interface EnvironmentalOverviewInput {
  earthquakeEnabled: boolean;
  earthquakeLoading: boolean;
  earthquakeError: boolean;
  earthquakeErrorSummary?: string | null;
  earthquakeDataUpdatedAt?: number;
  earthquakeMetadata?: EarthquakeEventsMetadata | null;
  earthquakeEntities: EarthquakeEntity[];
  eonetEnabled: boolean;
  eonetLoading: boolean;
  eonetError: boolean;
  eonetErrorSummary?: string | null;
  eonetDataUpdatedAt?: number;
  eonetMetadata?: EonetEventsMetadata | null;
  eonetEntities: EonetEntity[];
  pinnedEnvironmentalEvents: PinnedEnvironmentalEvent[];
  filters: EnvironmentalEventFilterState;
  selectedEntity: SceneEntity | null;
  hud: Pick<HudState, "latitude" | "longitude" | "altitudeMeters">;
}

export interface EnvironmentalOverviewSourceSummary {
  source: EnvironmentalSourceKey;
  label: string;
  state: SourceState;
  enabled: boolean;
  count: number;
}

export interface EnvironmentalOverviewSelectedEvent {
  source: EnvironmentalSourceKey;
  title: string;
  when: string;
  detail: string;
  caveat: string;
}

export interface EnvironmentalOverviewSourceHealth {
  sourceId: EnvironmentalSourceKey;
  sourceLabel: string;
  enabled: boolean;
  loadedCount: number;
  sourceMode: SourceMode;
  lastFetchedAt: string | null;
  sourceGeneratedAt: string | null;
  freshnessLabel: "fresh" | "recent" | "possibly stale" | "unknown";
  health: SourceHealthState;
  errorSummary: string | null;
  caveat: string;
  statusLine: string;
}

export interface EnvironmentalOverviewRelevanceEvent {
  source: EnvironmentalSourceKey;
  title: string;
  when: string;
  distanceKm: number;
  band: RelevanceBand;
}

export interface EnvironmentalOverviewRelevance {
  viewportContextAvailable: boolean;
  anchor: RelevanceAnchor | null;
  anchorLabel: string | null;
  referenceRadiusKm: number | null;
  visibleOrNearbyCount: number;
  nearestEvent: EnvironmentalOverviewRelevanceEvent | null;
  nearestEarthquake: EnvironmentalOverviewRelevanceEvent | null;
  nearestEonetEvent: EnvironmentalOverviewRelevanceEvent | null;
  newestNearbyEvent: EnvironmentalOverviewRelevanceEvent | null;
  strongestNearbyEarthquake: { title: string; magnitude: number; distanceKm: number } | null;
  nearbyCategories: string[];
  selectedEventNearestOther: EnvironmentalOverviewRelevanceEvent | null;
  distanceSummary: string[];
  caveats: string[];
  exportLines: string[];
  metadata: {
    anchor: RelevanceAnchor | null;
    referenceRadiusKm: number | null;
    visibleOrNearbyCount: number;
    nearestEventSource: EnvironmentalSourceKey | null;
    nearestEventDistanceKm: number | null;
    nearbyCategories: string[];
    selectedEventNearestOtherDistanceKm: number | null;
  };
}

export interface EnvironmentalOverviewCooccurrenceEvent {
  source: EnvironmentalSourceKey;
  title: string;
  when: string;
  distanceKm: number;
  distanceBand: RelevanceBand;
  timeDeltaMs: number;
  timeBand: TimeAdjacencyBand;
}

export interface EnvironmentalOverviewCooccurrencePair {
  left: EnvironmentalOverviewCooccurrenceEvent;
  right: EnvironmentalOverviewCooccurrenceEvent;
}

export interface EnvironmentalOverviewCooccurrence {
  selectedEventContext: {
    source: EnvironmentalSourceKey;
    title: string;
    sourceMode: SourceMode;
    nearestOther: EnvironmentalOverviewCooccurrenceEvent | null;
    nearestDifferentSource: EnvironmentalOverviewCooccurrenceEvent | null;
    nearbyCount: number;
    nearbyDifferentSourceCount: number;
    sameSourceNearbyCount: number;
    timeAdjacentCount: number;
    sameDayCount: number;
    sameWeekCount: number;
  } | null;
  nearbySameTimeEvents: number;
  nearbyDifferentSourceEvents: number;
  sameSourceNearbyEvents: number;
  timeWindowSummary: string[];
  distanceWindowSummary: string[];
  nearestCrossSourcePair: EnvironmentalOverviewCooccurrencePair | null;
  newestCrossSourceNearbyPair: EnvironmentalOverviewCooccurrencePair | null;
  caveats: string[];
  exportLines: string[];
  metadata: {
    nearbySameTimeEvents: number;
    nearbyDifferentSourceEvents: number;
    sameSourceNearbyEvents: number;
    selectedEventSource: EnvironmentalSourceKey | null;
    selectedNearestOtherDistanceKm: number | null;
    selectedNearestDifferentSourceDistanceKm: number | null;
    nearestCrossSourcePairDistanceKm: number | null;
    nearestCrossSourcePairTimeDeltaHours: number | null;
  };
}

export interface EnvironmentalOverview {
  enabledSources: EnvironmentalSourceKey[];
  loadedEventCount: number;
  earthquakeCount: number;
  eonetCount: number;
  newestEvent: { source: EnvironmentalSourceKey; title: string; when: string } | null;
  strongestEarthquake: { title: string; magnitude: number } | null;
  eonetCategories: string[];
  selectedEnvironmentalEvent: EnvironmentalOverviewSelectedEvent | null;
  sourceSummaries: EnvironmentalOverviewSourceSummary[];
  sourceHealth: EnvironmentalOverviewSourceHealth[];
  pinnedEvents: PinnedEnvironmentalEvent[];
  pinnedComparison: {
    pinnedCount: number;
    sourceMix: string[];
    nearestPair: {
      leftTitle: string;
      rightTitle: string;
      distanceKm: number;
    } | null;
    timeSpanHours: number | null;
    summaryLines: string[];
    caveats: string[];
    exportLines: string[];
    metadata: {
      pinnedCount: number;
      sourceMix: string[];
      nearestPairDistanceKm: number | null;
      timeSpanHours: number | null;
    };
  };
  caveats: string[];
  filtersSummary: string[];
  relevance: EnvironmentalOverviewRelevance;
  cooccurrence: EnvironmentalOverviewCooccurrence;
  exportLines: string[];
  metadata: {
    enabledSources: EnvironmentalSourceKey[];
    loadedEventCount: number;
    strongestEarthquakeMagnitude: number | null;
    eonetCategories: string[];
    selectedEnvironmentalEventSource: EnvironmentalSourceKey | null;
    sourceHealth: Array<{
      sourceId: EnvironmentalSourceKey;
      health: SourceHealthState;
      sourceMode: SourceMode;
      loadedCount: number;
      freshnessLabel: string;
    }>;
    pinnedComparison: {
      pinnedCount: number;
      sourceMix: string[];
      nearestPairDistanceKm: number | null;
      timeSpanHours: number | null;
    };
    relevance: EnvironmentalOverviewRelevance["metadata"];
    cooccurrence: EnvironmentalOverviewCooccurrence["metadata"];
  };
}

type EventWithDistance = {
  entity: EarthquakeEntity | EonetEntity;
  source: EnvironmentalSourceKey;
  title: string;
  when: string;
  distanceKm: number;
  band: RelevanceBand;
};

export function buildEnvironmentalEventsOverview(
  input: EnvironmentalOverviewInput
): EnvironmentalOverview {
  const enabledSources: EnvironmentalSourceKey[] = [
    ...(input.earthquakeEnabled ? ["earthquakes" as const] : []),
    ...(input.eonetEnabled ? ["eonet" as const] : [])
  ];
  const earthquakeCount = input.earthquakeEntities.length;
  const eonetCount = input.eonetEntities.length;
  const loadedEventCount = earthquakeCount + eonetCount;
  const strongestEarthquakeEntity = input.earthquakeEntities.reduce<EarthquakeEntity | null>((strongest, item) => {
    if (item.magnitude == null) {
      return strongest;
    }
    if (!strongest || strongest.magnitude == null || item.magnitude > strongest.magnitude) {
      return item;
    }
    return strongest;
  }, null);
  const strongestEarthquake =
    strongestEarthquakeEntity?.magnitude != null
      ? { title: strongestEarthquakeEntity.label, magnitude: strongestEarthquakeEntity.magnitude }
      : null;
  const newestEvent = newestCombinedEvent(input.earthquakeEntities, input.eonetEntities);
  const eonetCategories = Array.from(
    new Set(input.eonetEntities.flatMap((item) => item.categories).filter((value) => value.trim().length > 0))
  ).slice(0, 6);
  const selectedEnvironmentalEvent = toSelectedEnvironmentalEvent(input.selectedEntity);
  const sourceSummaries: EnvironmentalOverviewSourceSummary[] = [
    {
      source: "earthquakes",
      label: "Earthquakes",
      state: sourceState(input.earthquakeEnabled, input.earthquakeLoading, input.earthquakeError, earthquakeCount),
      enabled: input.earthquakeEnabled,
      count: earthquakeCount
    },
    {
      source: "eonet",
      label: "EONET",
      state: sourceState(input.eonetEnabled, input.eonetLoading, input.eonetError, eonetCount),
      enabled: input.eonetEnabled,
      count: eonetCount
    }
  ];
  const sourceHealth = [
    buildSourceHealth({
      sourceId: "earthquakes",
      sourceLabel: "Earthquakes",
      enabled: input.earthquakeEnabled,
      loading: input.earthquakeLoading,
      error: input.earthquakeError,
      errorSummary: input.earthquakeErrorSummary ?? null,
      loadedCount: earthquakeCount,
      metadata: input.earthquakeMetadata ?? null,
      dataUpdatedAt: input.earthquakeDataUpdatedAt
    }),
    buildSourceHealth({
      sourceId: "eonet",
      sourceLabel: "NASA EONET",
      enabled: input.eonetEnabled,
      loading: input.eonetLoading,
      error: input.eonetError,
      errorSummary: input.eonetErrorSummary ?? null,
      loadedCount: eonetCount,
      metadata: input.eonetMetadata ?? null,
      dataUpdatedAt: input.eonetDataUpdatedAt
    })
  ];
  const pinnedEvents = input.pinnedEnvironmentalEvents.slice(0, 5);
  const caveats = Array.from(
    new Set(
      [
        loadedEventCount > 0
          ? "Environmental event markers are source-reported context, not impact or damage estimates."
          : null,
        input.eonetEntities.length > 0
          ? "EONET markers may use representative latest geometry rather than full event footprint."
          : null,
        input.earthquakeEntities.length > 0
          ? "Earthquake magnitude indicates event size, not direct damage or casualty inference."
          : null,
        sourceHealth.some((item) => item.sourceMode === "fixture")
          ? "Fixture mode is local test data and should not be interpreted as a live source feed."
          : null
      ].filter((value): value is string => value != null)
    )
  );
  const filtersSummary = [
    `Earthquakes: window ${input.filters.window}, min magnitude ${input.filters.minMagnitude ?? "none"}, sort ${input.filters.sort}, limit ${input.filters.limit}`,
    `EONET: category ${input.filters.eonetCategory || "all"}, status ${input.filters.eonetStatus}, sort ${input.filters.eonetSort}, limit ${input.filters.eonetLimit}`
  ];
  const relevance = buildEnvironmentalRelevance(input);
  const cooccurrence = buildEnvironmentalCooccurrence(input, sourceHealth);
  const pinnedComparison = buildPinnedEnvironmentalComparison(pinnedEvents);
  const exportLines = buildExportLines({
    enabledSources,
    earthquakeCount,
    eonetCount,
    strongestEarthquake,
    eonetCategories,
    selectedEnvironmentalEvent,
    caveats,
    relevance,
    cooccurrence,
    pinnedComparison,
    sourceHealth
  });

  return {
    enabledSources,
    loadedEventCount,
    earthquakeCount,
    eonetCount,
    newestEvent,
    strongestEarthquake,
    eonetCategories,
    selectedEnvironmentalEvent,
    sourceSummaries,
    sourceHealth,
    pinnedEvents,
    pinnedComparison,
    caveats,
    filtersSummary,
    relevance,
    cooccurrence,
    exportLines,
    metadata: {
      enabledSources,
      loadedEventCount,
      strongestEarthquakeMagnitude: strongestEarthquake?.magnitude ?? null,
      eonetCategories,
      selectedEnvironmentalEventSource: selectedEnvironmentalEvent?.source ?? null,
      sourceHealth: sourceHealth.map((item) => ({
        sourceId: item.sourceId,
        health: item.health,
        sourceMode: item.sourceMode,
        loadedCount: item.loadedCount,
        freshnessLabel: item.freshnessLabel
      })),
      pinnedComparison: pinnedComparison.metadata,
      relevance: relevance.metadata,
      cooccurrence: cooccurrence.metadata
    }
  };
}

export function toPinnedEnvironmentalEvent(input: {
  entity: EarthquakeEntity | EonetEntity;
  sourceMode: SourceMode;
}): PinnedEnvironmentalEvent {
  const { entity, sourceMode } = input;
  if (entity.eventSource === "nasa-eonet") {
    return {
      source: "eonet",
      entityId: entity.id,
      eventId: entity.eventId,
      title: entity.label,
      eventTime: entity.eventDate,
      latitude: entity.latitude,
      longitude: entity.longitude,
      summaryLabel: `${entity.categories[0] ?? "event"} | ${entity.statusDetail}`,
      categoryOrMagnitude: entity.categories.join(", ") || "Unknown category",
      sourceMode,
      caveat: entity.caveat
    };
  }
  return {
    source: "earthquakes",
    entityId: entity.id,
    eventId: entity.eventId,
    title: entity.place ?? entity.label,
    eventTime: entity.timestamp,
    latitude: entity.latitude,
    longitude: entity.longitude,
    summaryLabel: entity.depthKm != null ? `${entity.depthKm.toFixed(1)} km depth` : "Depth unknown",
    categoryOrMagnitude:
      entity.magnitude != null
        ? `M${entity.magnitude.toFixed(1)}${entity.magnitudeType ? ` ${entity.magnitudeType}` : ""}`
        : "Magnitude not reported",
    sourceMode,
    caveat: entity.caveat
  };
}

function buildEnvironmentalRelevance(
  input: EnvironmentalOverviewInput
): EnvironmentalOverviewRelevance {
  const selectedEnvironmentalEntity =
    input.selectedEntity?.type === "environmental-event" ? input.selectedEntity : null;
  const viewportContextAvailable = Number.isFinite(input.hud.latitude) && Number.isFinite(input.hud.longitude);
  const anchorLat =
    selectedEnvironmentalEntity?.latitude ?? (viewportContextAvailable ? input.hud.latitude : null);
  const anchorLon =
    selectedEnvironmentalEntity?.longitude ?? (viewportContextAvailable ? input.hud.longitude : null);
  const anchor: RelevanceAnchor | null =
    anchorLat == null || anchorLon == null
      ? null
      : selectedEnvironmentalEntity
        ? "selected-environmental-event"
        : "view-center";
  const anchorLabel =
    anchor === "selected-environmental-event"
      ? `Selected ${selectedEnvironmentalEntity?.eventSource === "nasa-eonet" ? "EONET event" : "earthquake"}`
      : anchor === "view-center"
        ? "Current view center"
        : null;
  const referenceRadiusKm =
    anchor == null ? null : clamp(input.hud.altitudeMeters / 1500, MIN_VIEW_RADIUS_KM, MAX_VIEW_RADIUS_KM);
  const eventsWithDistance =
    anchorLat == null || anchorLon == null
      ? []
      : buildEventDistances(input.earthquakeEntities, input.eonetEntities, anchorLat, anchorLon);
  const nearbyEvents =
    referenceRadiusKm == null
      ? []
      : eventsWithDistance.filter((item) => item.distanceKm <= referenceRadiusKm);
  const nearbyEarthquakes = nearbyEvents.filter((item): item is EventWithDistance & { entity: EarthquakeEntity } => item.source === "earthquakes");
  const nearbyEonetEvents = nearbyEvents.filter((item): item is EventWithDistance & { entity: EonetEntity } => item.source === "eonet");
  const nearestEvent = toRelevanceEvent(eventsWithDistance[0] ?? null);
  const nearestEarthquake = toRelevanceEvent(nearbyEarthquakes[0] ?? null);
  const nearestEonetEvent = toRelevanceEvent(nearbyEonetEvents[0] ?? null);
  const newestNearbyEvent = toRelevanceEvent(
    nearbyEvents
      .slice()
      .sort((left, right) => new Date(right.when).getTime() - new Date(left.when).getTime())[0] ?? null
  );
  const strongestNearbyEarthquake = nearbyEarthquakes.reduce<{ title: string; magnitude: number; distanceKm: number } | null>(
    (strongest, item) => {
      if (item.entity.magnitude == null) {
        return strongest;
      }
      if (!strongest || item.entity.magnitude > strongest.magnitude) {
        return {
          title: item.title,
          magnitude: item.entity.magnitude,
          distanceKm: item.distanceKm
        };
      }
      return strongest;
    },
    null
  );
  const nearbyCategories = Array.from(
    new Set(
      nearbyEonetEvents.flatMap((item) => item.entity.categories).filter((value) => value.trim().length > 0)
    )
  ).slice(0, 6);
  const selectedEventNearestOther =
    selectedEnvironmentalEntity == null
      ? null
      : toRelevanceEvent(
          eventsWithDistance.find((item) => item.entity.id !== selectedEnvironmentalEntity.id) ?? null
        );
  const distanceSummary = buildDistanceSummary({
    anchorLabel,
    referenceRadiusKm,
    visibleOrNearbyCount: nearbyEvents.length,
    nearestEvent,
    selectedEventNearestOther
  });
  const caveats = Array.from(
    new Set(
      [
        anchor === "view-center"
          ? "View relevance uses current HUD camera center plus altitude-derived radius, not exact frustum bounds."
          : null,
        selectedEventNearestOther
          ? "Nearest other loaded environmental event is proximity-only. No relationship or causation is implied."
          : null,
        nearbyEonetEvents.length > 0
          ? "EONET distance is approximate for representative points and may not match full event extent."
          : null
      ].filter((value): value is string => value != null)
    )
  );
  const exportLines = buildRelevanceExportLines({
    anchorLabel,
    visibleOrNearbyCount: nearbyEvents.length,
    nearestEvent,
    strongestNearbyEarthquake,
    nearbyCategories,
    selectedEventNearestOther,
    caveats
  });

  return {
    viewportContextAvailable,
    anchor,
    anchorLabel,
    referenceRadiusKm,
    visibleOrNearbyCount: nearbyEvents.length,
    nearestEvent,
    nearestEarthquake,
    nearestEonetEvent,
    newestNearbyEvent,
    strongestNearbyEarthquake,
    nearbyCategories,
    selectedEventNearestOther,
    distanceSummary,
    caveats,
    exportLines,
    metadata: {
      anchor,
      referenceRadiusKm,
      visibleOrNearbyCount: nearbyEvents.length,
      nearestEventSource: nearestEvent?.source ?? null,
      nearestEventDistanceKm: nearestEvent?.distanceKm ?? null,
      nearbyCategories,
      selectedEventNearestOtherDistanceKm: selectedEventNearestOther?.distanceKm ?? null
    }
  };
}

function buildEnvironmentalCooccurrence(
  input: EnvironmentalOverviewInput,
  sourceHealth: EnvironmentalOverviewSourceHealth[]
): EnvironmentalOverviewCooccurrence {
  const allEvents = buildEnvironmentalEventRecords(input.earthquakeEntities, input.eonetEntities);
  const selected =
    input.selectedEntity?.type === "environmental-event"
      ? allEvents.find((item) => item.id === input.selectedEntity?.id) ?? null
      : null;
  const eventPairs = buildEnvironmentalEventPairs(allEvents);
  const crossSourcePairs = eventPairs.filter((item) => item.left.source !== item.right.source);
  const nearbyPairs = eventPairs.filter((item) => item.distanceKm <= REGIONAL_KM);
  const nearbySameTimeEvents = nearbyPairs.filter((item) => item.timeDeltaMs <= SAME_DAY_MS).length;
  const nearbyDifferentSourceEvents = nearbyPairs.filter((item) => item.left.source !== item.right.source).length;
  const sameSourceNearbyEvents = nearbyPairs.filter((item) => item.left.source === item.right.source).length;
  const nearestCrossSourcePair = toCooccurrencePair(crossSourcePairs[0] ?? null);
  const newestCrossSourceNearbyPair = toCooccurrencePair(
    crossSourcePairs
      .filter((item) => item.distanceKm <= REGIONAL_KM)
      .sort((left, right) => Math.max(right.left.whenMs, right.right.whenMs) - Math.max(left.left.whenMs, left.right.whenMs))[0] ?? null
  );
  const selectedEventContext = buildSelectedEventContext(selected, allEvents, sourceHealth);
  const timeWindowSummary = buildCooccurrenceTimeSummary({
    selectedEventContext,
    nearbySameTimeEvents,
    nearestCrossSourcePair
  });
  const distanceWindowSummary = buildCooccurrenceDistanceSummary({
    selectedEventContext,
    nearbyDifferentSourceEvents,
    sameSourceNearbyEvents,
    nearestCrossSourcePair
  });
  const caveats = Array.from(
    new Set(
      [
        selectedEventContext
          ? "Selected-event context uses loaded event proximity and time adjacency only. No relationship is implied."
          : null,
        nearbyDifferentSourceEvents > 0
          ? "Cross-source environmental context is descriptive only and does not imply shared cause, trigger, or impact chain."
          : null,
        allEvents.some((item) => item.source === "eonet")
          ? "EONET representative-point distance remains approximate for multi-geometry or non-point events."
          : null,
        sourceHealth.some((item) => item.enabled && item.sourceMode === "fixture")
          ? "Fixture/local source mode can be useful for workflow validation but should not be read as live event timing."
          : null
      ].filter((value): value is string => value != null)
    )
  );
  const exportLines = buildCooccurrenceExportLines({
    selectedEventContext,
    nearestCrossSourcePair,
    newestCrossSourceNearbyPair,
    nearbySameTimeEvents,
    nearbyDifferentSourceEvents,
    caveats
  });

  return {
    selectedEventContext,
    nearbySameTimeEvents,
    nearbyDifferentSourceEvents,
    sameSourceNearbyEvents,
    timeWindowSummary,
    distanceWindowSummary,
    nearestCrossSourcePair,
    newestCrossSourceNearbyPair,
    caveats,
    exportLines,
    metadata: {
      nearbySameTimeEvents,
      nearbyDifferentSourceEvents,
      sameSourceNearbyEvents,
      selectedEventSource: selectedEventContext?.source ?? null,
      selectedNearestOtherDistanceKm: selectedEventContext?.nearestOther?.distanceKm ?? null,
      selectedNearestDifferentSourceDistanceKm: selectedEventContext?.nearestDifferentSource?.distanceKm ?? null,
      nearestCrossSourcePairDistanceKm: nearestCrossSourcePair?.right.distanceKm ?? null,
      nearestCrossSourcePairTimeDeltaHours:
        nearestCrossSourcePair == null ? null : Number((nearestCrossSourcePair.right.timeDeltaMs / SAME_HOUR_MS).toFixed(2))
    }
  };
}

function buildSourceHealth(input: {
  sourceId: EnvironmentalSourceKey;
  sourceLabel: string;
  enabled: boolean;
  loading: boolean;
  error: boolean;
  errorSummary: string | null;
  loadedCount: number;
  metadata: { sourceMode: SourceMode; fetchedAt: string; generatedAt?: string | null; caveat: string } | null;
  dataUpdatedAt?: number;
}): EnvironmentalOverviewSourceHealth {
  const sourceMode = input.metadata?.sourceMode ?? "unknown";
  const lastFetchedAt = input.metadata?.fetchedAt ?? null;
  const sourceGeneratedAt = input.metadata?.generatedAt ?? null;
  const freshnessLabel = freshnessLabelFor(input.dataUpdatedAt);
  const health: SourceHealthState = !input.enabled
    ? "disabled"
    : input.loading
      ? "loading"
      : input.error
        ? "error"
        : input.loadedCount === 0
          ? "empty"
          : freshnessLabel === "possibly stale"
            ? "stale"
            : input.loadedCount > 0
              ? "loaded"
              : "unknown";
  const caveat =
    sourceMode === "fixture"
      ? "Fixture/local mode. Loaded data is deterministic test content, not a live feed."
      : input.metadata?.caveat ?? "Source caveat unavailable.";
  return {
    sourceId: input.sourceId,
    sourceLabel: input.sourceLabel,
    enabled: input.enabled,
    loadedCount: input.loadedCount,
    sourceMode,
    lastFetchedAt,
    sourceGeneratedAt,
    freshnessLabel,
    health,
    errorSummary: input.error ? input.errorSummary ?? "Query failed." : null,
    caveat,
    statusLine: buildSourceStatusLine({
      health,
      loadedCount: input.loadedCount,
      freshnessLabel,
      sourceMode,
      lastFetchedAt,
      sourceGeneratedAt
    })
  };
}

type EnvironmentalEventRecord = {
  id: string;
  source: EnvironmentalSourceKey;
  title: string;
  when: string;
  whenMs: number;
  latitude: number;
  longitude: number;
};

type EnvironmentalEventPair = {
  left: EnvironmentalEventRecord;
  right: EnvironmentalEventRecord;
  distanceKm: number;
  distanceBand: RelevanceBand;
  timeDeltaMs: number;
  timeBand: TimeAdjacencyBand;
};

function newestCombinedEvent(
  earthquakes: EarthquakeEntity[],
  eonetEvents: EonetEntity[]
): EnvironmentalOverview["newestEvent"] {
  const candidates = [
    ...earthquakes.map((item) => ({ source: "earthquakes" as const, title: item.place ?? item.label, when: item.timestamp })),
    ...eonetEvents.map((item) => ({ source: "eonet" as const, title: item.label, when: item.eventDate }))
  ];
  if (candidates.length === 0) {
    return null;
  }
  return candidates.sort((left, right) => new Date(right.when).getTime() - new Date(left.when).getTime())[0];
}

function sourceState(enabled: boolean, loading: boolean, error: boolean, count: number): SourceState {
  if (!enabled) return "disabled";
  if (loading) return "loading";
  if (error) return "error";
  if (count === 0) return "empty";
  return "ready";
}

function toSelectedEnvironmentalEvent(
  entity: SceneEntity | null
): EnvironmentalOverviewSelectedEvent | null {
  if (!entity || entity.type !== "environmental-event") {
    return null;
  }
  if (entity.eventSource === "nasa-eonet") {
    return {
      source: "eonet",
      title: entity.label,
      when: entity.eventDate,
      detail: `Categories ${entity.categories.join(", ") || "unknown"} | status ${entity.statusDetail}`,
      caveat: entity.caveat
    };
  }
  return {
    source: "earthquakes",
    title: entity.place ?? entity.label,
    when: entity.timestamp,
    detail:
      entity.magnitude != null
        ? `Magnitude M${entity.magnitude.toFixed(1)}${entity.magnitudeType ? ` ${entity.magnitudeType}` : ""}`
        : "Magnitude not reported",
    caveat: entity.caveat
  };
}

function buildEventDistances(
  earthquakes: EarthquakeEntity[],
  eonetEvents: EonetEntity[],
  anchorLat: number,
  anchorLon: number
): EventWithDistance[] {
  const toDistance = (latitude: number, longitude: number) =>
    haversineDistanceKm(anchorLat, anchorLon, latitude, longitude);
  const events: EventWithDistance[] = [
    ...earthquakes.map((entity) => {
      const distanceKm = toDistance(entity.latitude, entity.longitude);
      return {
        entity,
        source: "earthquakes" as const,
        title: entity.place ?? entity.label,
        when: entity.timestamp,
        distanceKm,
        band: relevanceBand(distanceKm)
      };
    }),
    ...eonetEvents.map((entity) => {
      const distanceKm = toDistance(entity.latitude, entity.longitude);
      return {
        entity,
        source: "eonet" as const,
        title: entity.label,
        when: entity.eventDate,
        distanceKm,
        band: relevanceBand(distanceKm)
      };
    })
  ];
  return events.sort((left, right) => left.distanceKm - right.distanceKm);
}

function buildEnvironmentalEventRecords(
  earthquakes: EarthquakeEntity[],
  eonetEvents: EonetEntity[]
): EnvironmentalEventRecord[] {
  return [
    ...earthquakes.map((entity) => ({
      id: entity.id,
      source: "earthquakes" as const,
      title: entity.place ?? entity.label,
      when: entity.timestamp,
      whenMs: new Date(entity.timestamp).getTime(),
      latitude: entity.latitude,
      longitude: entity.longitude
    })),
    ...eonetEvents.map((entity) => ({
      id: entity.id,
      source: "eonet" as const,
      title: entity.label,
      when: entity.eventDate,
      whenMs: new Date(entity.eventDate).getTime(),
      latitude: entity.latitude,
      longitude: entity.longitude
    }))
  ];
}

function buildEnvironmentalEventPairs(events: EnvironmentalEventRecord[]): EnvironmentalEventPair[] {
  const pairs: EnvironmentalEventPair[] = [];
  for (let index = 0; index < events.length; index += 1) {
    for (let otherIndex = index + 1; otherIndex < events.length; otherIndex += 1) {
      const left = events[index];
      const right = events[otherIndex];
      const distanceKm = haversineDistanceKm(left.latitude, left.longitude, right.latitude, right.longitude);
      const timeDeltaMs = Math.abs(left.whenMs - right.whenMs);
      pairs.push({
        left,
        right,
        distanceKm,
        distanceBand: relevanceBand(distanceKm),
        timeDeltaMs,
        timeBand: timeAdjacencyBand(timeDeltaMs)
      });
    }
  }
  return pairs.sort((left, right) => left.distanceKm - right.distanceKm || left.timeDeltaMs - right.timeDeltaMs);
}

function toRelevanceEvent(item: EventWithDistance | null): EnvironmentalOverviewRelevanceEvent | null {
  if (!item) return null;
  return {
    source: item.source,
    title: item.title,
    when: item.when,
    distanceKm: item.distanceKm,
    band: item.band
  };
}

function buildDistanceSummary(input: {
  anchorLabel: string | null;
  referenceRadiusKm: number | null;
  visibleOrNearbyCount: number;
  nearestEvent: EnvironmentalOverviewRelevanceEvent | null;
  selectedEventNearestOther: EnvironmentalOverviewRelevanceEvent | null;
}): string[] {
  if (!input.anchorLabel || input.referenceRadiusKm == null) {
    return [];
  }
  const lines = [
    `${input.visibleOrNearbyCount} loaded environmental events within ~${Math.round(input.referenceRadiusKm)} km of ${input.anchorLabel.toLowerCase()}.`
  ];
  if (input.nearestEvent) {
    lines.push(
      `Nearest loaded event ${input.nearestEvent.title} at ${formatDistanceKm(input.nearestEvent.distanceKm)} (${input.nearestEvent.band}).`
    );
  }
  if (input.selectedEventNearestOther) {
    lines.push(
      `Nearest other loaded environmental event ${input.selectedEventNearestOther.title} at ${formatDistanceKm(input.selectedEventNearestOther.distanceKm)}.`
    );
  }
  return lines;
}

function buildSelectedEventContext(
  selected: EnvironmentalEventRecord | null,
  allEvents: EnvironmentalEventRecord[],
  sourceHealth: EnvironmentalOverviewSourceHealth[]
): EnvironmentalOverviewCooccurrence["selectedEventContext"] {
  if (selected == null) {
    return null;
  }
  const otherEvents = allEvents
    .filter((item) => item.id !== selected.id)
    .map((item) => {
      const distanceKm = haversineDistanceKm(selected.latitude, selected.longitude, item.latitude, item.longitude);
      const timeDeltaMs = Math.abs(selected.whenMs - item.whenMs);
      return {
        source: item.source,
        title: item.title,
        when: item.when,
        distanceKm,
        distanceBand: relevanceBand(distanceKm),
        timeDeltaMs,
        timeBand: timeAdjacencyBand(timeDeltaMs)
      };
    })
    .sort((left, right) => left.distanceKm - right.distanceKm || left.timeDeltaMs - right.timeDeltaMs);
  const nearestOther = otherEvents[0] ?? null;
  const nearestDifferentSource = otherEvents.find((item) => item.source !== selected.source) ?? null;
  const nearbyCount = otherEvents.filter((item) => item.distanceKm <= REGIONAL_KM).length;
  const nearbyDifferentSourceCount = otherEvents.filter(
    (item) => item.source !== selected.source && item.distanceKm <= REGIONAL_KM
  ).length;
  const sameSourceNearbyCount = otherEvents.filter(
    (item) => item.source === selected.source && item.distanceKm <= REGIONAL_KM
  ).length;
  const sameDayCount = otherEvents.filter((item) => item.timeDeltaMs <= SAME_DAY_MS).length;
  const sameWeekCount = otherEvents.filter((item) => item.timeDeltaMs <= SAME_WEEK_MS).length;
  const timeAdjacentCount = sameDayCount;
  const sourceMode = sourceHealth.find((item) => item.sourceId === selected.source)?.sourceMode ?? "unknown";
  return {
    source: selected.source,
    title: selected.title,
    sourceMode,
    nearestOther,
    nearestDifferentSource,
    nearbyCount,
    nearbyDifferentSourceCount,
    sameSourceNearbyCount,
    timeAdjacentCount,
    sameDayCount,
    sameWeekCount
  };
}

function buildCooccurrenceTimeSummary(input: {
  selectedEventContext: EnvironmentalOverviewCooccurrence["selectedEventContext"];
  nearbySameTimeEvents: number;
  nearestCrossSourcePair: EnvironmentalOverviewCooccurrencePair | null;
}): string[] {
  const lines: string[] = [];
  if (input.selectedEventContext) {
    lines.push(
      `${input.selectedEventContext.sameDayCount} loaded events fall within the same-day window of the selected event.`
    );
    if (input.selectedEventContext.sameWeekCount > input.selectedEventContext.sameDayCount) {
      lines.push(
        `${input.selectedEventContext.sameWeekCount} loaded events fall within the same-week window of the selected event.`
      );
    }
  } else if (input.nearbySameTimeEvents > 0) {
    lines.push(`${input.nearbySameTimeEvents} loaded event pairs are both nearby and within the same-day window.`);
  }
  if (input.nearestCrossSourcePair) {
    lines.push(
      `Nearest Earthquake-EONET pair is ${formatDistanceKm(input.nearestCrossSourcePair.right.distanceKm)} apart with ${formatTimeDelta(input.nearestCrossSourcePair.right.timeDeltaMs)} separation.`
    );
  }
  return lines.slice(0, 2);
}

function buildCooccurrenceDistanceSummary(input: {
  selectedEventContext: EnvironmentalOverviewCooccurrence["selectedEventContext"];
  nearbyDifferentSourceEvents: number;
  sameSourceNearbyEvents: number;
  nearestCrossSourcePair: EnvironmentalOverviewCooccurrencePair | null;
}): string[] {
  const lines: string[] = [];
  if (input.selectedEventContext) {
    lines.push(
      `${input.selectedEventContext.nearbyCount} loaded events are within the regional distance band of the selected event.`
    );
    if (input.selectedEventContext.nearbyDifferentSourceCount > 0) {
      lines.push(
        `${input.selectedEventContext.nearbyDifferentSourceCount} of those nearby events come from the other environmental source.`
      );
    }
  } else if (input.nearbyDifferentSourceEvents > 0 || input.sameSourceNearbyEvents > 0) {
    lines.push(
      `${input.nearbyDifferentSourceEvents} cross-source nearby pairs and ${input.sameSourceNearbyEvents} same-source nearby pairs are loaded.`
    );
  }
  if (lines.length === 0 && input.nearestCrossSourcePair) {
    lines.push(
      `Cross-source context is available from a nearest Earthquake-EONET pair at ${formatDistanceKm(input.nearestCrossSourcePair.right.distanceKm)}.`
    );
  }
  return lines.slice(0, 2);
}

function buildExportLines(input: {
  enabledSources: EnvironmentalSourceKey[];
  earthquakeCount: number;
  eonetCount: number;
  strongestEarthquake: EnvironmentalOverview["strongestEarthquake"];
  eonetCategories: string[];
  selectedEnvironmentalEvent: EnvironmentalOverviewSelectedEvent | null;
  caveats: string[];
  relevance: EnvironmentalOverviewRelevance;
  cooccurrence: EnvironmentalOverviewCooccurrence;
  pinnedComparison: EnvironmentalOverview["pinnedComparison"];
  sourceHealth: EnvironmentalOverviewSourceHealth[];
}): string[] {
  if (input.enabledSources.length === 0) {
    return [];
  }
  const lines = [`Environmental events: Earthquakes ${input.earthquakeCount} | EONET ${input.eonetCount}`];
  const summaryParts = [
    input.strongestEarthquake ? `Strongest earthquake M${input.strongestEarthquake.magnitude.toFixed(1)}` : null,
    input.eonetCategories.length > 0 ? `EONET categories ${input.eonetCategories.slice(0, 3).join(", ")}` : null
  ].filter((value): value is string => value != null);
  if (summaryParts.length > 0) {
    lines.push(summaryParts.join(" | "));
  }
  const healthSummary = input.sourceHealth
    .filter((item) => item.enabled)
    .map((item) => `${item.sourceLabel} ${item.health}`)
    .join(" | ");
  if (healthSummary) {
    lines.push(`Environmental source health: ${healthSummary}`);
  }
  const fixtureSummary = input.sourceHealth
    .filter((item) => item.enabled && item.sourceMode !== "unknown")
    .map((item) => `${item.sourceLabel} ${item.sourceMode}`)
    .join(" | ");
  if (fixtureSummary) {
    lines.push(`Source mode: ${fixtureSummary}`);
  }
  if (input.relevance.exportLines.length > 0) {
    lines.push(...input.relevance.exportLines.slice(0, 2));
  }
  if (input.cooccurrence.exportLines.length > 0) {
    lines.push(...input.cooccurrence.exportLines.slice(0, 2));
  }
  if (input.pinnedComparison.exportLines.length > 0) {
    lines.push(...input.pinnedComparison.exportLines.slice(0, 2));
  }
  if (input.selectedEnvironmentalEvent) {
    lines.push(
      `Selected environmental event: ${input.selectedEnvironmentalEvent.source} | ${input.selectedEnvironmentalEvent.title} | ${input.selectedEnvironmentalEvent.detail}`
    );
  }
  if (input.caveats.length > 0) {
    lines.push(`Caveat: ${input.caveats[0]}`);
  }
  return lines.slice(0, 7);
}

function buildCooccurrenceExportLines(input: {
  selectedEventContext: EnvironmentalOverviewCooccurrence["selectedEventContext"];
  nearestCrossSourcePair: EnvironmentalOverviewCooccurrence["nearestCrossSourcePair"];
  newestCrossSourceNearbyPair: EnvironmentalOverviewCooccurrence["newestCrossSourceNearbyPair"];
  nearbySameTimeEvents: number;
  nearbyDifferentSourceEvents: number;
  caveats: string[];
}): string[] {
  const lines: string[] = [];
  if (input.selectedEventContext?.nearestOther) {
    lines.push(
      `Environmental context: nearest loaded event ${input.selectedEventContext.nearestOther.title} at ${formatDistanceKm(input.selectedEventContext.nearestOther.distanceKm)} | no relationship implied`
    );
  } else if (input.nearestCrossSourcePair) {
    lines.push(
      `Environmental context: nearest Earthquake-EONET pair ${formatDistanceKm(input.nearestCrossSourcePair.right.distanceKm)} apart | no relationship implied`
    );
  }
  const summaryParts = [
    input.nearbyDifferentSourceEvents > 0 ? `${input.nearbyDifferentSourceEvents} cross-source nearby pairs` : null,
    input.nearbySameTimeEvents > 0 ? `${input.nearbySameTimeEvents} same-day nearby pairs` : null,
    input.newestCrossSourceNearbyPair
      ? `Newest nearby cross-source pair ${input.newestCrossSourceNearbyPair.left.title} / ${input.newestCrossSourceNearbyPair.right.title}`
      : null
  ].filter((value): value is string => value != null);
  if (summaryParts.length > 0) {
    lines.push(summaryParts.join(" | "));
  }
  if (input.caveats.length > 0) {
    lines.push(`Context caveat: ${input.caveats[0]}`);
  }
  return lines.slice(0, 2);
}

function buildPinnedEnvironmentalComparison(pinnedEvents: PinnedEnvironmentalEvent[]): EnvironmentalOverview["pinnedComparison"] {
  const sourceMix = Array.from(
    new Set(
      pinnedEvents.map((item) => (item.source === "earthquakes" ? "Earthquakes" : "NASA EONET"))
    )
  );
  const sortedByTime = pinnedEvents
    .slice()
    .sort((left, right) => new Date(left.eventTime).getTime() - new Date(right.eventTime).getTime());
  const earliest = sortedByTime[0] ?? null;
  const latest = sortedByTime[sortedByTime.length - 1] ?? null;
  const timeSpanHours =
    earliest == null || latest == null
      ? null
      : Number(((new Date(latest.eventTime).getTime() - new Date(earliest.eventTime).getTime()) / SAME_HOUR_MS).toFixed(1));
  let nearestPair: EnvironmentalOverview["pinnedComparison"]["nearestPair"] = null;
  for (let index = 0; index < pinnedEvents.length; index += 1) {
    for (let otherIndex = index + 1; otherIndex < pinnedEvents.length; otherIndex += 1) {
      const left = pinnedEvents[index];
      const right = pinnedEvents[otherIndex];
      const distanceKm = haversineDistanceKm(left.latitude, left.longitude, right.latitude, right.longitude);
      if (nearestPair == null || distanceKm < nearestPair.distanceKm) {
        nearestPair = {
          leftTitle: left.title,
          rightTitle: right.title,
          distanceKm
        };
      }
    }
  }
  const summaryLines: string[] = [];
  if (pinnedEvents.length > 0) {
    summaryLines.push(`Pinned environmental events ${pinnedEvents.length} | sources ${sourceMix.join(", ") || "none"}`);
  }
  if (nearestPair) {
    summaryLines.push(
      `Nearest pinned pair ${nearestPair.leftTitle} / ${nearestPair.rightTitle} at ${formatDistanceKm(nearestPair.distanceKm)}`
    );
  }
  if (timeSpanHours != null) {
    summaryLines.push(`Pinned time span ${timeSpanHours.toFixed(timeSpanHours >= 24 ? 0 : 1)} hr`);
  }
  const caveats =
    pinnedEvents.length > 0
      ? [
          "Pinned environmental events are for comparison and reference only.",
          "Comparison only; no relationship implied.",
          pinnedEvents.some((item) => item.source === "eonet")
            ? "Pinned EONET event distance remains approximate for representative points."
            : null
        ].filter((value): value is string => value != null)
      : [];
  const exportLines = pinnedEvents.length === 0
    ? []
    : [
        `Pinned environmental events: ${pinnedEvents.length}`,
        sourceMix.length > 0 ? `Pinned sources: ${sourceMix.join(", ")}` : null,
        "Comparison only; no relationship implied"
      ].filter((value): value is string => value != null);
  return {
    pinnedCount: pinnedEvents.length,
    sourceMix,
    nearestPair,
    timeSpanHours,
    summaryLines: summaryLines.slice(0, 3),
    caveats,
    exportLines: exportLines.slice(0, 3),
    metadata: {
      pinnedCount: pinnedEvents.length,
      sourceMix,
      nearestPairDistanceKm: nearestPair?.distanceKm ?? null,
      timeSpanHours
    }
  };
}

function buildRelevanceExportLines(input: {
  anchorLabel: string | null;
  visibleOrNearbyCount: number;
  nearestEvent: EnvironmentalOverviewRelevanceEvent | null;
  strongestNearbyEarthquake: EnvironmentalOverviewRelevance["strongestNearbyEarthquake"];
  nearbyCategories: string[];
  selectedEventNearestOther: EnvironmentalOverviewRelevanceEvent | null;
  caveats: string[];
}): string[] {
  if (!input.anchorLabel) {
    return [];
  }
  const lines = [
    `View relevance: ${input.visibleOrNearbyCount} nearby loaded events from ${input.anchorLabel.toLowerCase()}`
  ];
  const summaryParts = [
    input.nearestEvent ? `Nearest ${input.nearestEvent.title} at ${formatDistanceKm(input.nearestEvent.distanceKm)}` : null,
    input.strongestNearbyEarthquake ? `Nearby strongest quake M${input.strongestNearbyEarthquake.magnitude.toFixed(1)}` : null,
    input.nearbyCategories.length > 0 ? `Nearby EONET ${input.nearbyCategories.slice(0, 2).join(", ")}` : null
  ].filter((value): value is string => value != null);
  if (summaryParts.length > 0) {
    lines.push(summaryParts.join(" | "));
  }
  if (input.selectedEventNearestOther) {
    lines.push(
      `Nearest other loaded environmental event: ${input.selectedEventNearestOther.title} at ${formatDistanceKm(input.selectedEventNearestOther.distanceKm)} | no relationship implied`
    );
  }
  if (input.caveats.length > 0) {
    lines.push(`Relevance caveat: ${input.caveats[0]}`);
  }
  return lines.slice(0, 3);
}

function buildSourceStatusLine(input: {
  health: SourceHealthState;
  loadedCount: number;
  freshnessLabel: string;
  sourceMode: SourceMode;
  lastFetchedAt: string | null;
  sourceGeneratedAt: string | null;
}) {
  const parts = [
    input.health,
    `${input.loadedCount} loaded`,
    input.freshnessLabel,
    input.sourceMode !== "unknown" ? `${input.sourceMode} mode` : "mode unknown",
    input.lastFetchedAt ? `Loaded at ${new Date(input.lastFetchedAt).toLocaleString()}` : null,
    input.sourceGeneratedAt ? `Source updated ${new Date(input.sourceGeneratedAt).toLocaleString()}` : null
  ].filter((value): value is string => value != null);
  return parts.join(" | ");
}

function toCooccurrencePair(item: EnvironmentalEventPair | null): EnvironmentalOverviewCooccurrencePair | null {
  if (item == null) {
    return null;
  }
  return {
    left: {
      source: item.left.source,
      title: item.left.title,
      when: item.left.when,
      distanceKm: 0,
      distanceBand: "very-near",
      timeDeltaMs: item.timeDeltaMs,
      timeBand: item.timeBand
    },
    right: {
      source: item.right.source,
      title: item.right.title,
      when: item.right.when,
      distanceKm: item.distanceKm,
      distanceBand: item.distanceBand,
      timeDeltaMs: item.timeDeltaMs,
      timeBand: item.timeBand
    }
  };
}

function freshnessLabelFor(dataUpdatedAt?: number) {
  if (!dataUpdatedAt) {
    return "unknown" as const;
  }
  const ageMs = Date.now() - dataUpdatedAt;
  if (ageMs <= FRESH_MS) return "fresh" as const;
  if (ageMs <= RECENT_MS) return "recent" as const;
  if (ageMs <= POSSIBLY_STALE_MS) return "possibly stale" as const;
  return "possibly stale" as const;
}

function timeAdjacencyBand(timeDeltaMs: number): TimeAdjacencyBand {
  if (timeDeltaMs <= SAME_HOUR_MS) return "same-hour";
  if (timeDeltaMs <= SAME_DAY_MS) return "same-day";
  if (timeDeltaMs <= SAME_WEEK_MS) return "same-week";
  return "later";
}

function haversineDistanceKm(lat1: number, lon1: number, lat2: number, lon2: number) {
  const toRadians = (value: number) => (value * Math.PI) / 180;
  const earthRadiusKm = 6371;
  const deltaLat = toRadians(lat2 - lat1);
  const deltaLon = toRadians(lon2 - lon1);
  const lat1Rad = toRadians(lat1);
  const lat2Rad = toRadians(lat2);
  const sinLat = Math.sin(deltaLat / 2);
  const sinLon = Math.sin(deltaLon / 2);
  const haversine =
    sinLat * sinLat + Math.cos(lat1Rad) * Math.cos(lat2Rad) * sinLon * sinLon;
  return earthRadiusKm * 2 * Math.atan2(Math.sqrt(haversine), Math.sqrt(1 - haversine));
}

function relevanceBand(distanceKm: number): RelevanceBand {
  if (distanceKm <= VERY_NEAR_KM) return "very-near";
  if (distanceKm <= NEAR_KM) return "near";
  if (distanceKm <= REGIONAL_KM) return "regional";
  return "distant";
}

function formatDistanceKm(distanceKm: number) {
  return `${distanceKm.toFixed(distanceKm >= 100 ? 0 : 1)} km`;
}

function formatTimeDelta(timeDeltaMs: number) {
  if (timeDeltaMs <= SAME_HOUR_MS) {
    return `${Math.max(1, Math.round(timeDeltaMs / (60 * 1000)))} min`;
  }
  if (timeDeltaMs <= SAME_DAY_MS) {
    return `${(timeDeltaMs / SAME_HOUR_MS).toFixed(1)} hr`;
  }
  return `${(timeDeltaMs / SAME_DAY_MS).toFixed(1)} day`;
}

function clamp(value: number, min: number, max: number) {
  return Math.min(max, Math.max(min, value));
}
