import clsx from "clsx";
import { buildEnvironmentalEventsOverview, toPinnedEnvironmentalEvent } from "../environmental/environmentalEventsOverview";
import {
  useCanadaCapAlertsQuery,
  useEonetEventsQuery,
  useEarthquakeEventsQuery,
  useGeoNetHazardsQuery,
  useHkoWeatherQuery,
  useMetNoMetAlertsQuery,
  useTsunamiAlertsQuery,
  useUkEaFloodMonitoringQuery,
  useVolcanoStatusQuery
} from "../../lib/queries";
import { groupPlanetImageryModes } from "../../lib/planetImagery";
import { useAppStore } from "../../lib/store";
import type { SourceStatusResponse } from "../../types/api";
import { OperatorControlPanel } from "../operator/OperatorControlPanel";
import { WebcamOperationsPanel } from "./WebcamOperationsPanel";

interface LayerPanelProps {
  status?: SourceStatusResponse;
  onJumpToCity: (preset: "global" | "austin" | "nyc" | "london") => void;
  onCopyPermalink: () => void;
}

export function LayerPanel({ status, onJumpToCity, onCopyPermalink }: LayerPanelProps) {
  const layers = useAppStore((state) => state.layers);
  const filters = useAppStore((state) => state.filters);
  const bookmarks = useAppStore((state) => state.bookmarks);
  const imageryModeId = useAppStore((state) => state.imageryModeId);
  const imageryCategories = useAppStore((state) => state.imageryCategories);
  const availableImageryModes = useAppStore((state) => state.availableImageryModes);
  const hud = useAppStore((state) => state.hud);
  const setLayerEnabled = useAppStore((state) => state.setLayerEnabled);
  const setImageryModeId = useAppStore((state) => state.setImageryModeId);
  const setFilters = useAppStore((state) => state.setFilters);
  const environmentalFilters = useAppStore((state) => state.environmentalFilters);
  const setEnvironmentalFilters = useAppStore((state) => state.setEnvironmentalFilters);
  const earthquakeEntities = useAppStore((state) => state.earthquakeEntities);
  const eonetEntities = useAppStore((state) => state.eonetEntities);
  const volcanoEntities = useAppStore((state) => state.volcanoEntities);
  const tsunamiEntities = useAppStore((state) => state.tsunamiEntities);
  const ukFloodEntities = useAppStore((state) => state.ukFloodEntities);
  const geonetEntities = useAppStore((state) => state.geonetEntities);
  const hkoWeatherEntities = useAppStore((state) => state.hkoWeatherEntities);
  const metnoAlertEntities = useAppStore((state) => state.metnoAlertEntities);
  const canadaCapEntities = useAppStore((state) => state.canadaCapEntities);
  const pinnedEnvironmentalEvents = useAppStore((state) => state.pinnedEnvironmentalEvents);
  const selectedEntity = useAppStore((state) => state.selectedEntity);
  const setSelectedEntity = useAppStore((state) => state.setSelectedEntity);
  const pinEnvironmentalEvent = useAppStore((state) => state.pinEnvironmentalEvent);
  const unpinEnvironmentalEvent = useAppStore((state) => state.unpinEnvironmentalEvent);
  const clearPinnedEnvironmentalEvents = useAppStore((state) => state.clearPinnedEnvironmentalEvents);
  const removeBookmark = useAppStore((state) => state.removeBookmark);
  const earthquakesEnabled = layers.find((layer) => layer.key === "earthquakes")?.enabled ?? false;
  const eonetEnabled = layers.find((layer) => layer.key === "eonet")?.enabled ?? false;
  const volcanoEnabled = layers.find((layer) => layer.key === "volcanoes")?.enabled ?? false;
  const tsunamiEnabled = layers.find((layer) => layer.key === "tsunami")?.enabled ?? false;
  const ukFloodEnabled = layers.find((layer) => layer.key === "ukFloods")?.enabled ?? false;
  const geonetEnabled = layers.find((layer) => layer.key === "geonet")?.enabled ?? false;
  const hkoWeatherEnabled = layers.find((layer) => layer.key === "hkoWeather")?.enabled ?? false;
  const metnoAlertsEnabled = layers.find((layer) => layer.key === "metnoAlerts")?.enabled ?? false;
  const canadaCapEnabled = layers.find((layer) => layer.key === "canadaCap")?.enabled ?? false;
  const earthquakeQuery = useEarthquakeEventsQuery(environmentalFilters, earthquakesEnabled);
  const eonetQuery = useEonetEventsQuery(environmentalFilters, eonetEnabled);
  const volcanoQuery = useVolcanoStatusQuery(environmentalFilters, volcanoEnabled);
  const tsunamiQuery = useTsunamiAlertsQuery(environmentalFilters, tsunamiEnabled);
  const ukFloodQuery = useUkEaFloodMonitoringQuery(environmentalFilters, ukFloodEnabled);
  const geonetQuery = useGeoNetHazardsQuery(environmentalFilters, geonetEnabled);
  const hkoWeatherQuery = useHkoWeatherQuery(environmentalFilters, hkoWeatherEnabled);
  const metnoAlertsQuery = useMetNoMetAlertsQuery(environmentalFilters, metnoAlertsEnabled);
  const canadaCapQuery = useCanadaCapAlertsQuery(environmentalFilters, canadaCapEnabled);
  const strongestMagnitude = earthquakeQuery.data?.events.reduce<number | null>(
    (max, event) => {
      if (event.magnitude == null) return max;
      if (max == null) return event.magnitude;
      return event.magnitude > max ? event.magnitude : max;
    },
    null
  );
  const newestTime = earthquakeQuery.data?.events[0]?.time ?? null;
  const eonetNewest = eonetQuery.data?.events[0]?.eventDate ?? null;
  const environmentalOverview = buildEnvironmentalEventsOverview({
    earthquakeEnabled: earthquakesEnabled,
    earthquakeLoading: earthquakeQuery.isLoading,
    earthquakeError: earthquakeQuery.isError,
    earthquakeErrorSummary: earthquakeQuery.error instanceof Error ? earthquakeQuery.error.message : null,
    earthquakeDataUpdatedAt: earthquakeQuery.dataUpdatedAt,
    earthquakeMetadata: earthquakeQuery.data?.metadata ?? null,
    earthquakeEntities,
    eonetEnabled,
    eonetLoading: eonetQuery.isLoading,
    eonetError: eonetQuery.isError,
    eonetErrorSummary: eonetQuery.error instanceof Error ? eonetQuery.error.message : null,
    eonetDataUpdatedAt: eonetQuery.dataUpdatedAt,
    eonetMetadata: eonetQuery.data?.metadata ?? null,
    eonetEntities,
    tsunamiEnabled,
    tsunamiLoading: tsunamiQuery.isLoading,
    tsunamiError: tsunamiQuery.isError,
    tsunamiErrorSummary: tsunamiQuery.error instanceof Error ? tsunamiQuery.error.message : null,
    tsunamiDataUpdatedAt: tsunamiQuery.dataUpdatedAt,
    tsunamiMetadata: tsunamiQuery.data?.metadata ?? null,
    tsunamiCount: tsunamiEntities.length,
    ukFloodEnabled,
    ukFloodLoading: ukFloodQuery.isLoading,
    ukFloodError: ukFloodQuery.isError,
    ukFloodErrorSummary: ukFloodQuery.error instanceof Error ? ukFloodQuery.error.message : null,
    ukFloodDataUpdatedAt: ukFloodQuery.dataUpdatedAt,
    ukFloodMetadata: ukFloodQuery.data?.metadata ?? null,
    ukFloodEntities,
    geonetEnabled,
    geonetLoading: geonetQuery.isLoading,
    geonetError: geonetQuery.isError,
    geonetErrorSummary: geonetQuery.error instanceof Error ? geonetQuery.error.message : null,
    geonetDataUpdatedAt: geonetQuery.dataUpdatedAt,
    geonetMetadata: geonetQuery.data?.metadata ?? null,
    geonetEntities,
    hkoWeatherEnabled,
    hkoWeatherLoading: hkoWeatherQuery.isLoading,
    hkoWeatherError: hkoWeatherQuery.isError,
    hkoWeatherErrorSummary: hkoWeatherQuery.error instanceof Error ? hkoWeatherQuery.error.message : null,
    hkoWeatherDataUpdatedAt: hkoWeatherQuery.dataUpdatedAt,
    hkoWeatherMetadata: hkoWeatherQuery.data?.metadata ?? null,
    hkoWeatherEntities,
    metnoAlertsEnabled,
    metnoAlertsLoading: metnoAlertsQuery.isLoading,
    metnoAlertsError: metnoAlertsQuery.isError,
    metnoAlertsErrorSummary: metnoAlertsQuery.error instanceof Error ? metnoAlertsQuery.error.message : null,
    metnoAlertsDataUpdatedAt: metnoAlertsQuery.dataUpdatedAt,
    metnoAlertsMetadata: metnoAlertsQuery.data?.metadata ?? null,
    metnoAlertEntities,
    canadaCapEnabled,
    canadaCapLoading: canadaCapQuery.isLoading,
    canadaCapError: canadaCapQuery.isError,
    canadaCapErrorSummary: canadaCapQuery.error instanceof Error ? canadaCapQuery.error.message : null,
    canadaCapDataUpdatedAt: canadaCapQuery.dataUpdatedAt,
    canadaCapMetadata: canadaCapQuery.data?.metadata ?? null,
    canadaCapEntities,
    pinnedEnvironmentalEvents,
    filters: environmentalFilters,
    selectedEntity,
    hud
  });
  const selectedEnvironmentalEntity =
    selectedEntity?.type === "environmental-event" &&
    (selectedEntity.eventSource === "usgs-earthquake" || selectedEntity.eventSource === "nasa-eonet")
      ? selectedEntity
      : null;
  const selectedEnvironmentalSourceMode =
    selectedEnvironmentalEntity?.eventSource === "nasa-eonet"
      ? environmentalOverview.sourceHealth.find((item) => item.sourceId === "eonet")?.sourceMode ?? "unknown"
      : selectedEnvironmentalEntity?.eventSource === "usgs-earthquake"
        ? environmentalOverview.sourceHealth.find((item) => item.sourceId === "earthquakes")?.sourceMode ?? "unknown"
        : "unknown";
  const selectedEnvironmentalPinned =
    selectedEnvironmentalEntity != null &&
    pinnedEnvironmentalEvents.some((item) => item.entityId === selectedEnvironmentalEntity.id);
  const groupedImageryModes = groupPlanetImageryModes(imageryCategories, availableImageryModes);
  const activeImageryMode =
    availableImageryModes.find((mode) => mode.id === imageryModeId) ?? availableImageryModes[0];

  return (
    <aside className="panel panel--left">
      <div className="panel__section">
        <p className="panel__eyebrow">Investigation Filters</p>
        <input
          className="panel__input"
          value={filters.query}
          onChange={(event) => setFilters({ query: event.currentTarget.value })}
          placeholder="General search"
        />
        <div className="field-grid">
          <label className="field-row">
            <span>Callsign</span>
            <input
              className="panel__input"
              value={filters.callsign}
              onChange={(event) => setFilters({ callsign: event.currentTarget.value })}
            />
          </label>
          <label className="field-row">
            <span>ICAO24</span>
            <input
              className="panel__input"
              value={filters.icao24}
              onChange={(event) => setFilters({ icao24: event.currentTarget.value })}
            />
          </label>
          <label className="field-row">
            <span>NORAD ID</span>
            <input
              className="panel__input"
              value={filters.noradId}
              onChange={(event) => setFilters({ noradId: event.currentTarget.value })}
            />
          </label>
          <label className="field-row">
            <span>Source</span>
            <input
              className="panel__input"
              value={filters.source}
              onChange={(event) => setFilters({ source: event.currentTarget.value })}
            />
          </label>
          <label className="field-row">
            <span>Aircraft Status</span>
            <select
              className="panel__select"
              value={filters.status}
              onChange={(event) =>
                setFilters({ status: event.currentTarget.value as typeof filters.status })
              }
            >
              <option value="all">All</option>
              <option value="airborne">Airborne</option>
              <option value="on-ground">On Ground</option>
            </select>
          </label>
          <label className="field-row">
            <span>Orbit Class</span>
            <select
              className="panel__select"
              value={filters.orbitClass}
              onChange={(event) =>
                setFilters({ orbitClass: event.currentTarget.value as typeof filters.orbitClass })
              }
            >
              <option value="all">All</option>
              <option value="leo">LEO</option>
              <option value="meo">MEO</option>
              <option value="geo">GEO</option>
            </select>
          </label>
          <label className="field-row">
            <span>Observed After (local)</span>
            <input
              className="panel__input"
              type="datetime-local"
              value={filters.observedAfter}
              onChange={(event) => setFilters({ observedAfter: event.currentTarget.value })}
            />
          </label>
          <label className="field-row">
            <span>Observed Before (local)</span>
            <input
              className="panel__input"
              type="datetime-local"
              value={filters.observedBefore}
              onChange={(event) => setFilters({ observedBefore: event.currentTarget.value })}
            />
          </label>
          <label className="field-row">
            <span>Recency (s)</span>
            <input
              className="panel__input"
              type="number"
              min="0"
              value={filters.recencySeconds ?? ""}
              onChange={(event) =>
                setFilters({
                  recencySeconds:
                    event.currentTarget.value === "" ? null : Number(event.currentTarget.value)
                })
              }
            />
          </label>
          <label className="field-row">
            <span>Min Altitude (m)</span>
            <input
              className="panel__input"
              type="number"
              min="0"
              value={filters.minAltitude ?? ""}
              onChange={(event) =>
                setFilters({
                  minAltitude:
                    event.currentTarget.value === "" ? null : Number(event.currentTarget.value)
                })
              }
            />
          </label>
          <label className="field-row">
            <span>Max Altitude (m)</span>
            <input
              className="panel__input"
              type="number"
              min="0"
              value={filters.maxAltitude ?? ""}
              onChange={(event) =>
                setFilters({
                  maxAltitude:
                    event.currentTarget.value === "" ? null : Number(event.currentTarget.value)
                })
              }
            />
          </label>
          <label className="field-row">
            <span>History Window (session only)</span>
            <input
              className="panel__input"
              type="number"
              min="5"
              max="180"
              value={filters.historyWindowMinutes}
              onChange={(event) =>
                setFilters({ historyWindowMinutes: Number(event.currentTarget.value) || 30 })
              }
            />
          </label>
        </div>
      </div>

      <div className="panel__section">
        <p className="panel__eyebrow">Planet Imagery</p>
        <label className="field-row">
          <span>Imagery Mode</span>
          <select
            className="panel__select"
            value={activeImageryMode?.id ?? ""}
            onChange={(event) => setImageryModeId(event.currentTarget.value)}
            disabled={availableImageryModes.length === 0}
          >
            {groupedImageryModes.map((group) => (
              <optgroup key={group.category.id} label={group.category.title}>
                {group.modes.map((mode) => (
                  <option key={mode.id} value={mode.id}>
                    {mode.modeRole === "analysis-layer" ? `[Analysis] ${mode.title}` : mode.title}
                  </option>
                ))}
              </optgroup>
            ))}
          </select>
        </label>
        {activeImageryMode ? (
          <div className="data-card data-card--compact">
            <strong>{activeImageryMode.title}</strong>
            <span>
              {activeImageryMode.temporalNature} | {activeImageryMode.cloudBehavior}
            </span>
            <span>
              {activeImageryMode.modeRole} | {activeImageryMode.sensorFamily}
            </span>
            <span>{activeImageryMode.source}</span>
            <span>{activeImageryMode.shortDescription}</span>
            <span>{activeImageryMode.shortCaveat}</span>
            <span>{activeImageryMode.displayTags.join(" | ")}</span>
          </div>
        ) : (
          <div className="empty-state compact">
            <p>Imagery registry loading.</p>
            <span>The globe will use the configured default once public config arrives.</span>
          </div>
        )}
      </div>

      <div className="panel__section">
        <p className="panel__eyebrow">Environmental Events</p>
        <div className="stack" data-testid="environmental-events-overview">
          {environmentalOverview.enabledSources.length === 0 ? (
            <div className="empty-state compact" data-testid="environmental-overview-disabled">
              <p>No environmental event layers enabled.</p>
              <span>Enable Earthquakes or Natural Events (EONET) to load source-reported event context.</span>
            </div>
          ) : environmentalOverview.loadedEventCount === 0 &&
            !earthquakeQuery.isLoading &&
            !eonetQuery.isLoading &&
            !earthquakeQuery.isError &&
            !eonetQuery.isError ? (
            <div className="empty-state compact" data-testid="environmental-overview-empty">
              <p>No environmental events match current filters.</p>
              <span>Adjust earthquake or EONET filters to broaden results.</span>
            </div>
          ) : (
            <div className="data-card data-card--compact" data-testid="environmental-overview-card">
              <strong>
                Environmental Events Overview | {environmentalOverview.loadedEventCount} loaded
              </strong>
              <span>
                Sources{" "}
                {environmentalOverview.sourceSummaries
                  .filter((item) => item.enabled)
                  .map((item) => `${item.label} ${item.count}`)
                  .join(" | ") || "none"}
              </span>
              <span>
                Newest{" "}
                {environmentalOverview.newestEvent
                  ? `${environmentalOverview.newestEvent.title} | ${new Date(environmentalOverview.newestEvent.when).toLocaleString()}`
                  : "none loaded"}
              </span>
              <span>
                Strongest earthquake{" "}
                {environmentalOverview.strongestEarthquake
                  ? `M${environmentalOverview.strongestEarthquake.magnitude.toFixed(1)}`
                  : "none loaded"}{" "}
                | EONET categories {environmentalOverview.eonetCategories.slice(0, 3).join(", ") || "none loaded"}
              </span>
              <span>{environmentalOverview.filtersSummary.join(" | ")}</span>
              <span>{environmentalOverview.caveats[0] ?? "Environmental event context depends on source-specific caveats."}</span>
              <span>
                Source health |{" "}
                {environmentalOverview.sourceHealth
                  .filter((item) => item.enabled)
                  .map((item) => `${item.sourceLabel} ${item.health} ${item.loadedCount} loaded ${item.freshnessLabel} ${item.sourceMode}`)
                  .join(" | ") || "No enabled environmental sources"}
              </span>
              {environmentalOverview.sourceHealth
                .filter((item) => item.enabled)
                .map((item) => (
                  <span key={`source-health-${item.sourceId}`}>
                    {item.sourceLabel} | {item.statusLine}
                    {item.errorSummary ? ` | ${item.errorSummary}` : ""}
                  </span>
                ))}
              {environmentalOverview.relevance.viewportContextAvailable ? (
                <>
                  <span>
                    View relevance | {environmentalOverview.relevance.visibleOrNearbyCount} nearby loaded events |{" "}
                    {environmentalOverview.relevance.anchorLabel ?? "view context unavailable"}
                  </span>
                  {environmentalOverview.relevance.nearestEvent ? (
                    <span>
                      Nearest loaded event {environmentalOverview.relevance.nearestEvent.title} |{" "}
                      {environmentalOverview.relevance.nearestEvent.distanceKm.toFixed(
                        environmentalOverview.relevance.nearestEvent.distanceKm >= 100 ? 0 : 1
                      )}{" "}
                      km | {environmentalOverview.relevance.nearestEvent.band}
                    </span>
                  ) : null}
                  {environmentalOverview.relevance.strongestNearbyEarthquake ? (
                    <span>
                      Strongest nearby earthquake M
                      {environmentalOverview.relevance.strongestNearbyEarthquake.magnitude.toFixed(1)} |{" "}
                      {environmentalOverview.relevance.nearbyCategories.length > 0
                        ? `Nearby EONET ${environmentalOverview.relevance.nearbyCategories.slice(0, 3).join(", ")}`
                        : "No nearby EONET categories"}
                    </span>
                  ) : environmentalOverview.relevance.nearbyCategories.length > 0 ? (
                    <span>
                      Nearby EONET categories {environmentalOverview.relevance.nearbyCategories.slice(0, 3).join(", ")}
                    </span>
                  ) : null}
                  <span>
                    {environmentalOverview.relevance.caveats[0] ??
                      "Representative-point distance is approximate for non-point EONET events."}
                  </span>
                </>
              ) : null}
              {environmentalOverview.selectedEnvironmentalEvent ? (
                <span data-testid="environmental-overview-selected">
                  Selected {environmentalOverview.selectedEnvironmentalEvent.source} |{" "}
                  {environmentalOverview.selectedEnvironmentalEvent.title} |{" "}
                  {environmentalOverview.selectedEnvironmentalEvent.detail}
                </span>
              ) : null}
              {selectedEnvironmentalEntity ? (
                <div className="stack stack--actions">
                  <button
                    type="button"
                    className="ghost-button"
                    onClick={() =>
                      selectedEnvironmentalPinned
                        ? unpinEnvironmentalEvent(selectedEnvironmentalEntity.id)
                        : pinEnvironmentalEvent(
                            toPinnedEnvironmentalEvent({
                              entity: selectedEnvironmentalEntity,
                              sourceMode: selectedEnvironmentalSourceMode
                            })
                          )
                    }
                  >
                    {selectedEnvironmentalPinned ? "Unpin Event" : "Pin Event"}
                  </button>
                </div>
              ) : null}
              {environmentalOverview.relevance.selectedEventNearestOther ? (
                <span data-testid="environmental-overview-nearest-other">
                  Nearest other loaded environmental event | {environmentalOverview.relevance.selectedEventNearestOther.title} |{" "}
                  {environmentalOverview.relevance.selectedEventNearestOther.distanceKm.toFixed(
                    environmentalOverview.relevance.selectedEventNearestOther.distanceKm >= 100 ? 0 : 1
                  )}{" "}
                  km | No relationship implied
                </span>
              ) : null}
              {environmentalOverview.cooccurrence.selectedEventContext ||
              environmentalOverview.cooccurrence.nearestCrossSourcePair ||
              environmentalOverview.cooccurrence.nearbyDifferentSourceEvents > 0 ? (
                <>
                  <span>
                    Event context |{" "}
                    {environmentalOverview.cooccurrence.selectedEventContext
                      ? `Selected ${environmentalOverview.cooccurrence.selectedEventContext.source} | ${environmentalOverview.cooccurrence.selectedEventContext.sourceMode} mode`
                      : "Loaded cross-source context"}
                  </span>
                  {environmentalOverview.cooccurrence.selectedEventContext?.nearestDifferentSource ? (
                    <span data-testid="environmental-overview-cross-source">
                      Nearest different-source event |{" "}
                      {environmentalOverview.cooccurrence.selectedEventContext.nearestDifferentSource.title} |{" "}
                      {environmentalOverview.cooccurrence.selectedEventContext.nearestDifferentSource.distanceKm.toFixed(
                        environmentalOverview.cooccurrence.selectedEventContext.nearestDifferentSource.distanceKm >= 100
                          ? 0
                          : 1
                      )}{" "}
                      km | {environmentalOverview.cooccurrence.selectedEventContext.nearestDifferentSource.timeBand} | No relationship implied
                    </span>
                  ) : environmentalOverview.cooccurrence.nearestCrossSourcePair ? (
                    <span data-testid="environmental-overview-cross-source">
                      Nearest Earthquake-EONET pair | {environmentalOverview.cooccurrence.nearestCrossSourcePair.left.title} /{" "}
                      {environmentalOverview.cooccurrence.nearestCrossSourcePair.right.title} |{" "}
                      {environmentalOverview.cooccurrence.nearestCrossSourcePair.right.distanceKm.toFixed(
                        environmentalOverview.cooccurrence.nearestCrossSourcePair.right.distanceKm >= 100 ? 0 : 1
                      )}{" "}
                      km | {environmentalOverview.cooccurrence.nearestCrossSourcePair.right.timeBand} | No relationship implied
                    </span>
                  ) : null}
                  {environmentalOverview.cooccurrence.timeWindowSummary[0] ? (
                    <span>{environmentalOverview.cooccurrence.timeWindowSummary[0]}</span>
                  ) : null}
                  <span>
                    {environmentalOverview.cooccurrence.caveats[0] ??
                      "Nearby or time-adjacent loaded events are contextual only. No relationship implied."}
                  </span>
                </>
              ) : null}
              {environmentalOverview.pinnedEvents.length > 0 ? (
                <>
                  <span>
                    Pinned environmental events | {environmentalOverview.pinnedComparison.pinnedCount} |{" "}
                    {environmentalOverview.pinnedComparison.sourceMix.join(", ")}
                  </span>
                  {environmentalOverview.pinnedComparison.summaryLines.map((line) => (
                    <span key={line}>{line}</span>
                  ))}
                  {environmentalOverview.pinnedEvents.map((event) => (
                    <span key={`pinned-${event.entityId}`}>
                      {event.source} | {event.title} | {event.categoryOrMagnitude} |{" "}
                      {new Date(event.eventTime).toLocaleString()} | {event.sourceMode}
                    </span>
                  ))}
                  <span>
                    {environmentalOverview.pinnedComparison.caveats[0] ??
                      "Pinned environmental events are for comparison only; no relationship implied."}
                  </span>
                  <div className="stack stack--actions">
                    <button
                      type="button"
                      className="ghost-button"
                      onClick={() => clearPinnedEnvironmentalEvents()}
                    >
                      Clear Pinned Events
                    </button>
                  </div>
                </>
              ) : null}
            </div>
          )}
        </div>
        <div className="field-grid">
          <label className="field-row">
            <span>Earthquake Window</span>
            <select
              className="panel__select"
              value={environmentalFilters.window}
              onChange={(event) =>
                setEnvironmentalFilters({
                  window: event.currentTarget.value as typeof environmentalFilters.window
                })
              }
            >
              <option value="hour">Past Hour</option>
              <option value="day">Past Day</option>
              <option value="week">Past 7 Days</option>
              <option value="month">Past 30 Days</option>
            </select>
          </label>
          <label className="field-row">
            <span>Min Magnitude</span>
            <input
              className="panel__input"
              type="number"
              min="0"
              max="10"
              step="0.1"
              value={environmentalFilters.minMagnitude ?? ""}
              onChange={(event) =>
                setEnvironmentalFilters({
                  minMagnitude:
                    event.currentTarget.value === "" ? null : Number(event.currentTarget.value)
                })
              }
            />
          </label>
          <label className="field-row">
            <span>Sort</span>
            <select
              className="panel__select"
              value={environmentalFilters.sort}
              onChange={(event) =>
                setEnvironmentalFilters({
                  sort: event.currentTarget.value as typeof environmentalFilters.sort
                })
              }
            >
              <option value="newest">Newest first</option>
              <option value="magnitude">Strongest first</option>
            </select>
          </label>
          <label className="field-row">
            <span>Event Limit</span>
            <input
              className="panel__input"
              type="number"
              min="1"
              max="2000"
              value={environmentalFilters.limit}
              onChange={(event) =>
                setEnvironmentalFilters({ limit: Math.max(1, Math.min(2000, Number(event.currentTarget.value) || 300)) })
              }
            />
          </label>
          <label className="field-row">
            <span>EONET Category</span>
            <input
              className="panel__input"
              value={environmentalFilters.eonetCategory}
              onChange={(event) =>
                setEnvironmentalFilters({
                  eonetCategory: event.currentTarget.value
                })
              }
              placeholder="wildfires, volcanoes, severeStorms"
            />
          </label>
          <label className="field-row">
            <span>EONET Status</span>
            <select
              className="panel__select"
              value={environmentalFilters.eonetStatus}
              onChange={(event) =>
                setEnvironmentalFilters({
                  eonetStatus: event.currentTarget.value as typeof environmentalFilters.eonetStatus
                })
              }
            >
              <option value="open">Open</option>
              <option value="closed">Closed</option>
              <option value="all">All</option>
            </select>
          </label>
          <label className="field-row">
            <span>EONET Sort</span>
            <select
              className="panel__select"
              value={environmentalFilters.eonetSort}
              onChange={(event) =>
                setEnvironmentalFilters({
                  eonetSort: event.currentTarget.value as typeof environmentalFilters.eonetSort
                })
              }
            >
              <option value="newest">Newest first</option>
              <option value="category">Category</option>
            </select>
          </label>
          <label className="field-row">
            <span>EONET Limit</span>
            <input
              className="panel__input"
              type="number"
              min="1"
              max="2000"
              value={environmentalFilters.eonetLimit}
              onChange={(event) =>
                setEnvironmentalFilters({
                  eonetLimit: Math.max(1, Math.min(2000, Number(event.currentTarget.value) || 200))
                })
              }
            />
          </label>
          <label className="field-row">
            <span>Volcano Scope</span>
            <select
              className="panel__select"
              value={environmentalFilters.volcanoScope}
              onChange={(event) =>
                setEnvironmentalFilters({
                  volcanoScope: event.currentTarget.value as typeof environmentalFilters.volcanoScope
                })
              }
            >
              <option value="elevated">Elevated</option>
              <option value="monitored">Monitored</option>
            </select>
          </label>
          <label className="field-row">
            <span>Volcano Alert</span>
            <select
              className="panel__select"
              value={environmentalFilters.volcanoAlertLevel}
              onChange={(event) =>
                setEnvironmentalFilters({
                  volcanoAlertLevel: event.currentTarget.value as typeof environmentalFilters.volcanoAlertLevel
                })
              }
            >
              <option value="all">All</option>
              <option value="ADVISORY">Advisory</option>
              <option value="WATCH">Watch</option>
              <option value="WARNING">Warning</option>
              <option value="NORMAL">Normal</option>
            </select>
          </label>
          <label className="field-row">
            <span>Volcano Limit</span>
            <input
              className="panel__input"
              type="number"
              min="1"
              max="1000"
              value={environmentalFilters.volcanoLimit}
              onChange={(event) =>
                setEnvironmentalFilters({
                  volcanoLimit: Math.max(1, Math.min(1000, Number(event.currentTarget.value) || 100))
                })
              }
            />
          </label>
          <label className="field-row">
            <span>Tsunami Alert</span>
            <select
              className="panel__select"
              value={environmentalFilters.tsunamiAlertType}
              onChange={(event) =>
                setEnvironmentalFilters({
                  tsunamiAlertType: event.currentTarget.value as typeof environmentalFilters.tsunamiAlertType
                })
              }
            >
              <option value="all">All</option>
              <option value="warning">Warning</option>
              <option value="watch">Watch</option>
              <option value="advisory">Advisory</option>
              <option value="information">Information</option>
              <option value="cancellation">Cancellation</option>
            </select>
          </label>
          <label className="field-row">
            <span>Tsunami Center</span>
            <select
              className="panel__select"
              value={environmentalFilters.tsunamiSourceCenter}
              onChange={(event) =>
                setEnvironmentalFilters({
                  tsunamiSourceCenter: event.currentTarget.value as typeof environmentalFilters.tsunamiSourceCenter
                })
              }
            >
              <option value="all">All</option>
              <option value="NTWC">NTWC</option>
              <option value="PTWC">PTWC</option>
              <option value="unknown">Unknown</option>
            </select>
          </label>
          <label className="field-row">
            <span>Tsunami Limit</span>
            <input
              className="panel__input"
              type="number"
              min="1"
              max="1000"
              value={environmentalFilters.tsunamiLimit}
              onChange={(event) =>
                setEnvironmentalFilters({
                  tsunamiLimit: Math.max(1, Math.min(1000, Number(event.currentTarget.value) || 100))
                })
              }
            />
          </label>
          <label className="field-row">
            <span>UK Flood Severity</span>
            <select
              className="panel__select"
              value={environmentalFilters.ukFloodSeverity}
              onChange={(event) =>
                setEnvironmentalFilters({
                  ukFloodSeverity: event.currentTarget.value as typeof environmentalFilters.ukFloodSeverity
                })
              }
            >
              <option value="all">All</option>
              <option value="severe-warning">Severe warning</option>
              <option value="warning">Warning</option>
              <option value="alert">Alert</option>
              <option value="inactive">Inactive</option>
              <option value="unknown">Unknown</option>
            </select>
          </label>
          <label className="field-row">
            <span>UK Flood Limit</span>
            <input
              className="panel__input"
              type="number"
              min="1"
              max="1000"
              value={environmentalFilters.ukFloodLimit}
              onChange={(event) =>
                setEnvironmentalFilters({
                  ukFloodLimit: Math.max(1, Math.min(1000, Number(event.currentTarget.value) || 100))
                })
              }
            />
          </label>
          <label className="field-row">
            <span>Include Stations</span>
            <input
              type="checkbox"
              checked={environmentalFilters.ukFloodIncludeStations}
              onChange={(event) =>
                setEnvironmentalFilters({
                  ukFloodIncludeStations: event.currentTarget.checked
                })
              }
            />
          </label>
          <label className="field-row">
            <span>GeoNet Type</span>
            <select
              className="panel__select"
              value={environmentalFilters.geonetEventType}
              onChange={(event) =>
                setEnvironmentalFilters({
                  geonetEventType: event.currentTarget.value as typeof environmentalFilters.geonetEventType
                })
              }
            >
              <option value="all">All</option>
              <option value="quake">Quake</option>
              <option value="volcano">Volcano</option>
            </select>
          </label>
          <label className="field-row">
            <span>GeoNet Min Mag</span>
            <input
              className="panel__input"
              type="number"
              min="0"
              max="10"
              step="0.1"
              value={environmentalFilters.geonetMinMagnitude ?? ""}
              onChange={(event) =>
                setEnvironmentalFilters({
                  geonetMinMagnitude:
                    event.currentTarget.value.trim() === "" ? null : Math.max(0, Math.min(10, Number(event.currentTarget.value) || 0))
                })
              }
            />
          </label>
          <label className="field-row">
            <span>GeoNet Alert</span>
            <select
              className="panel__select"
              value={environmentalFilters.geonetAlertLevel}
              onChange={(event) =>
                setEnvironmentalFilters({
                  geonetAlertLevel: event.currentTarget.value as typeof environmentalFilters.geonetAlertLevel
                })
              }
            >
              <option value="all">All</option>
              <option value="0">0</option>
              <option value="1">1</option>
              <option value="2">2</option>
              <option value="3">3</option>
              <option value="4">4</option>
              <option value="5">5</option>
            </select>
          </label>
          <label className="field-row">
            <span>GeoNet Limit</span>
            <input
              className="panel__input"
              type="number"
              min="1"
              max="1000"
              value={environmentalFilters.geonetLimit}
              onChange={(event) =>
                setEnvironmentalFilters({
                  geonetLimit: Math.max(1, Math.min(1000, Number(event.currentTarget.value) || 100))
                })
              }
            />
          </label>
          <label className="field-row">
            <span>HKO Warning</span>
            <select
              className="panel__select"
              value={environmentalFilters.hkoWarningType}
              onChange={(event) =>
                setEnvironmentalFilters({
                  hkoWarningType: event.currentTarget.value as typeof environmentalFilters.hkoWarningType
                })
              }
            >
              <option value="all">All</option>
              <option value="WTS">Thunderstorm</option>
              <option value="WRAIN">Rainstorm</option>
              <option value="WTCSGNL">Tropical Cyclone Signal</option>
              <option value="WTMW">Tsunami Warning</option>
              <option value="WL">Landslip</option>
              <option value="WHOT">Very Hot</option>
              <option value="WCOLD">Cold</option>
              <option value="WFIRE">Fire Danger</option>
              <option value="WMSGNL">Strong Monsoon</option>
            </select>
          </label>
          <label className="field-row">
            <span>HKO Limit</span>
            <input
              className="panel__input"
              type="number"
              min="1"
              max="500"
              value={environmentalFilters.hkoLimit}
              onChange={(event) =>
                setEnvironmentalFilters({
                  hkoLimit: Math.max(1, Math.min(500, Number(event.currentTarget.value) || 50))
                })
              }
            />
          </label>
          <label className="field-row">
            <span>METNO Severity</span>
            <select
              className="panel__select"
              value={environmentalFilters.metnoAlertSeverity}
              onChange={(event) =>
                setEnvironmentalFilters({
                  metnoAlertSeverity: event.currentTarget.value as typeof environmentalFilters.metnoAlertSeverity
                })
              }
            >
              <option value="all">All</option>
              <option value="red">Red</option>
              <option value="orange">Orange</option>
              <option value="yellow">Yellow</option>
              <option value="green">Green</option>
              <option value="unknown">Unknown</option>
            </select>
          </label>
          <label className="field-row">
            <span>METNO Type</span>
            <input
              className="panel__input"
              value={environmentalFilters.metnoAlertType}
              onChange={(event) => setEnvironmentalFilters({ metnoAlertType: event.currentTarget.value })}
              placeholder="rain, wind, snow"
            />
          </label>
          <label className="field-row">
            <span>METNO Limit</span>
            <input
              className="panel__input"
              type="number"
              min="1"
              max="1000"
              value={environmentalFilters.metnoLimit}
              onChange={(event) =>
                setEnvironmentalFilters({
                  metnoLimit: Math.max(1, Math.min(1000, Number(event.currentTarget.value) || 50))
                })
              }
            />
          </label>
          <label className="field-row">
            <span>Canada CAP Type</span>
            <select
              className="panel__select"
              value={environmentalFilters.canadaCapAlertType}
              onChange={(event) =>
                setEnvironmentalFilters({
                  canadaCapAlertType: event.currentTarget.value as typeof environmentalFilters.canadaCapAlertType
                })
              }
            >
              <option value="all">All</option>
              <option value="warning">Warning</option>
              <option value="watch">Watch</option>
              <option value="advisory">Advisory</option>
              <option value="statement">Statement</option>
            </select>
          </label>
          <label className="field-row">
            <span>Canada CAP Severity</span>
            <select
              className="panel__select"
              value={environmentalFilters.canadaCapSeverity}
              onChange={(event) =>
                setEnvironmentalFilters({
                  canadaCapSeverity: event.currentTarget.value as typeof environmentalFilters.canadaCapSeverity
                })
              }
            >
              <option value="all">All</option>
              <option value="extreme">Extreme</option>
              <option value="severe">Severe</option>
              <option value="moderate">Moderate</option>
              <option value="minor">Minor</option>
            </select>
          </label>
          <label className="field-row">
            <span>Canada CAP Limit</span>
            <input
              className="panel__input"
              type="number"
              min="1"
              max="1000"
              value={environmentalFilters.canadaCapLimit}
              onChange={(event) =>
                setEnvironmentalFilters({
                  canadaCapLimit: Math.max(1, Math.min(1000, Number(event.currentTarget.value) || 100))
                })
              }
            />
          </label>
        </div>
        {!earthquakesEnabled ? (
          <div className="empty-state compact" data-testid="earthquake-layer-disabled">
            <p>Earthquake layer disabled.</p>
            <span>Enable the Earthquakes layer to load source-reported USGS environmental events.</span>
          </div>
        ) : earthquakeQuery.isLoading ? (
          <div className="empty-state compact" data-testid="earthquake-layer-loading">
            <p>Loading earthquake events.</p>
            <span>Fetching source-reported USGS earthquake events for the selected window.</span>
          </div>
        ) : earthquakeQuery.isError ? (
          <div className="empty-state compact" data-testid="earthquake-layer-error">
            <p>Earthquake events unavailable.</p>
            <span>Unable to load source-reported USGS earthquake events.</span>
          </div>
        ) : (earthquakeQuery.data?.events.length ?? 0) === 0 ? (
          <div className="empty-state compact" data-testid="earthquake-layer-empty">
            <p>No earthquake events match current filters.</p>
            <span>Adjust window, minimum magnitude, or limit to broaden results.</span>
          </div>
        ) : (
          <div className="stack" data-testid="earthquake-layer-summary">
            <div className="data-card data-card--compact">
              <strong>
                Earthquakes · {earthquakeQuery.data?.count ?? 0} loaded
              </strong>
              <span>
                Strongest {strongestMagnitude != null ? `M${strongestMagnitude.toFixed(1)}` : "N/A"} ·{" "}
                {environmentalFilters.window} window · sort {environmentalFilters.sort}
              </span>
              <span>
                Newest {newestTime ? new Date(newestTime).toLocaleString() : "Unknown"} · Source: USGS
              </span>
              <span>{earthquakeQuery.data?.metadata.caveat}</span>
            </div>
            <div className="stack" data-testid="earthquake-recent-list">
              {earthquakeQuery.data?.events.slice(0, 8).map((event) => (
                <button
                  key={event.eventId}
                  type="button"
                  className="ghost-button"
                  data-testid={`earthquake-item-${event.eventId}`}
                  onClick={() => {
                    const selected = earthquakeEntities.find((item) => item.eventId === event.eventId);
                    if (selected) {
                      setSelectedEntity(selected);
                    }
                  }}
                >
                  {event.magnitude != null ? `M${event.magnitude.toFixed(1)}` : "M?"} · {event.place ?? event.title} ·{" "}
                  {event.depthKm != null ? `${event.depthKm.toFixed(1)} km` : "Depth ?"} ·{" "}
                  {new Date(event.time).toLocaleString()}
                </button>
              ))}
            </div>
          </div>
        )}
        {!eonetEnabled ? (
          <div className="empty-state compact" data-testid="eonet-layer-disabled">
            <p>EONET layer disabled.</p>
            <span>Enable Natural Events (EONET) to load NASA source-reported natural events.</span>
          </div>
        ) : eonetQuery.isLoading ? (
          <div className="empty-state compact" data-testid="eonet-layer-loading">
            <p>Loading NASA EONET events.</p>
            <span>Fetching source-reported natural events.</span>
          </div>
        ) : eonetQuery.isError ? (
          <div className="empty-state compact" data-testid="eonet-layer-error">
            <p>NASA EONET events unavailable.</p>
            <span>Unable to load source-reported natural events.</span>
          </div>
        ) : (eonetQuery.data?.events.length ?? 0) === 0 ? (
          <div className="empty-state compact" data-testid="eonet-layer-empty">
            <p>No EONET events match current filters.</p>
            <span>Adjust category, status, or limit to broaden results.</span>
          </div>
        ) : (
          <div className="stack" data-testid="eonet-layer-summary">
            <div className="data-card data-card--compact">
              <strong>EONET Natural Events | {eonetQuery.data?.count ?? 0} loaded</strong>
              <span>
                category {environmentalFilters.eonetCategory || "all"} | status {environmentalFilters.eonetStatus} | sort{" "}
                {environmentalFilters.eonetSort}
              </span>
              <span>Newest {eonetNewest ? new Date(eonetNewest).toLocaleString() : "Unknown"} | Source: NASA EONET</span>
              <span>{eonetQuery.data?.metadata.caveat}</span>
            </div>
            <div className="stack" data-testid="eonet-recent-list">
              {eonetQuery.data?.events.slice(0, 8).map((event) => (
                <button
                  key={event.eventId}
                  type="button"
                  className="ghost-button"
                  data-testid={`eonet-item-${event.eventId}`}
                  onClick={() => {
                    const selected = eonetEntities.find((item) => item.eventId === event.eventId);
                    if (selected) {
                      setSelectedEntity(selected);
                    }
                  }}
                >
                  {(event.categoryTitles[0] ?? "event")} | {event.title} | {event.status} | {new Date(event.eventDate).toLocaleString()}
                </button>
              ))}
            </div>
          </div>
        )}
        {!volcanoEnabled ? (
          <div className="empty-state compact" data-testid="volcano-layer-disabled">
            <p>Volcano status layer disabled.</p>
            <span>Enable Volcano Status to load USGS monitored or elevated volcano advisories.</span>
          </div>
        ) : volcanoQuery.isLoading ? (
          <div className="empty-state compact" data-testid="volcano-layer-loading">
            <p>Loading volcano status records.</p>
            <span>Fetching source-reported USGS volcano advisory status.</span>
          </div>
        ) : volcanoQuery.isError ? (
          <div className="empty-state compact" data-testid="volcano-layer-error">
            <p>Volcano status unavailable.</p>
            <span>Unable to load source-reported USGS volcano status records.</span>
          </div>
        ) : (volcanoQuery.data?.events.length ?? 0) === 0 ? (
          <div className="empty-state compact" data-testid="volcano-layer-empty">
            <p>No volcano status records match current filters.</p>
            <span>Adjust scope, alert level, or limit to broaden results.</span>
          </div>
        ) : (
          <div className="stack" data-testid="volcano-layer-summary">
            <div className="data-card data-card--compact">
              <strong>Volcano Status | {volcanoQuery.data?.count ?? 0} loaded</strong>
              <span>
                scope {environmentalFilters.volcanoScope} | alert {environmentalFilters.volcanoAlertLevel} | limit{" "}
                {environmentalFilters.volcanoLimit}
              </span>
              <span>
                Source health | {volcanoQuery.data?.metadata.sourceMode ?? "unknown"} | loaded{" "}
                {new Date(volcanoQuery.data?.metadata.fetchedAt ?? Date.now()).toLocaleString()}
              </span>
              <span>{volcanoQuery.data?.metadata.caveat}</span>
            </div>
            <div className="stack" data-testid="volcano-recent-list">
              {volcanoQuery.data?.events.slice(0, 8).map((event) => (
                <button
                  key={event.eventId}
                  type="button"
                  className="ghost-button"
                  data-testid={`volcano-item-${event.eventId}`}
                  onClick={() => {
                    const selected = volcanoEntities.find((item) => item.eventId === event.eventId);
                    if (selected) {
                      setSelectedEntity(selected);
                    }
                  }}
                >
                  {event.alertLevel} | {event.volcanoName} | {event.observatoryAbbr ?? event.observatoryName} |{" "}
                  {new Date(event.issuedAt).toLocaleString()}
                </button>
              ))}
            </div>
          </div>
        )}
        {!tsunamiEnabled ? (
          <div className="empty-state compact" data-testid="tsunami-layer-disabled">
            <p>Tsunami alert layer disabled.</p>
            <span>Enable Tsunami Alerts to load official NOAA warning-center advisory context.</span>
          </div>
        ) : tsunamiQuery.isLoading ? (
          <div className="empty-state compact" data-testid="tsunami-layer-loading">
            <p>Loading tsunami alerts.</p>
            <span>Fetching official warning-center advisory context.</span>
          </div>
        ) : tsunamiQuery.isError ? (
          <div className="empty-state compact" data-testid="tsunami-layer-error">
            <p>Tsunami alerts unavailable.</p>
            <span>Unable to load official tsunami advisory records.</span>
          </div>
        ) : (tsunamiQuery.data?.events.length ?? 0) === 0 ? (
          <div className="empty-state compact" data-testid="tsunami-layer-empty">
            <p>No tsunami alerts match current filters.</p>
            <span>Adjust alert type, source center, or limit to broaden results.</span>
          </div>
        ) : (
          <div className="stack" data-testid="tsunami-layer-summary">
            <div className="data-card data-card--compact">
              <strong>Tsunami Alerts | {tsunamiQuery.data?.count ?? 0} loaded</strong>
              <span>
                type {environmentalFilters.tsunamiAlertType} | center {environmentalFilters.tsunamiSourceCenter} | limit{" "}
                {environmentalFilters.tsunamiLimit}
              </span>
              <span>
                Source health | {tsunamiQuery.data?.metadata.sourceMode ?? "unknown"} | loaded{" "}
                {new Date(tsunamiQuery.data?.metadata.fetchedAt ?? Date.now()).toLocaleString()}
              </span>
              <span>{tsunamiQuery.data?.metadata.caveat}</span>
            </div>
            <div className="stack" data-testid="tsunami-recent-list">
              {tsunamiQuery.data?.events.slice(0, 8).map((event) => (
                <button
                  key={event.eventId}
                  type="button"
                  className="ghost-button"
                  data-testid={`tsunami-item-${event.eventId}`}
                  onClick={() => {
                    const selected = tsunamiEntities.find((item) => item.eventId === event.eventId);
                    if (selected) {
                      setSelectedEntity(selected);
                    }
                  }}
                >
                  {event.alertType.toUpperCase()} | {event.sourceCenter} | {event.affectedRegions[0] ?? event.title} |{" "}
                  {new Date(event.issuedAt).toLocaleString()}
                </button>
              ))}
            </div>
          </div>
        )}
        {!ukFloodEnabled ? (
          <div className="empty-state compact" data-testid="uk-flood-layer-disabled">
            <p>UK flood layer disabled.</p>
            <span>Enable UK Flood Monitoring to load Environment Agency warnings and observed station readings.</span>
          </div>
        ) : ukFloodQuery.isLoading ? (
          <div className="empty-state compact" data-testid="uk-flood-layer-loading">
            <p>Loading UK flood monitoring records.</p>
            <span>Fetching Environment Agency advisory and observed monitoring context.</span>
          </div>
        ) : ukFloodQuery.isError ? (
          <div className="empty-state compact" data-testid="uk-flood-layer-error">
            <p>UK flood monitoring unavailable.</p>
            <span>Unable to load Environment Agency flood warnings or station readings.</span>
          </div>
        ) : (ukFloodQuery.data?.count ?? 0) === 0 ? (
          <div className="empty-state compact" data-testid="uk-flood-layer-empty">
            <p>No UK flood records match current filters.</p>
            <span>Adjust severity, station inclusion, or limit to broaden results.</span>
          </div>
        ) : (
          <div className="stack" data-testid="uk-flood-layer-summary">
            <div className="data-card data-card--compact">
              <strong>
                UK Flood Monitoring | {ukFloodQuery.data?.metadata.eventCount ?? 0} alerts | {ukFloodQuery.data?.metadata.stationCount ?? 0} stations
              </strong>
              <span>
                severity {environmentalFilters.ukFloodSeverity} | stations {environmentalFilters.ukFloodIncludeStations ? "on" : "off"} | limit{" "}
                {environmentalFilters.ukFloodLimit}
              </span>
              <span>
                Source health | {ukFloodQuery.data?.metadata.sourceMode ?? "unknown"} | loaded{" "}
                {new Date(ukFloodQuery.data?.metadata.fetchedAt ?? Date.now()).toLocaleString()}
              </span>
              <span>{ukFloodQuery.data?.metadata.caveat}</span>
            </div>
            <div className="stack" data-testid="uk-flood-recent-list">
              {ukFloodQuery.data?.events.slice(0, 4).map((event) => (
                <button
                  key={event.eventId}
                  type="button"
                  className="ghost-button"
                  data-testid={`uk-flood-alert-item-${event.eventId}`}
                  onClick={() => {
                    const selected = ukFloodEntities.find((item) => item.id === `ukflood:alert:${event.eventId}`);
                    if (selected) {
                      setSelectedEntity(selected);
                    }
                  }}
                >
                  {event.severity} | {event.areaName ?? event.riverOrSea ?? event.title} | {new Date(event.issuedAt ?? Date.now()).toLocaleString()}
                </button>
              ))}
              {ukFloodQuery.data?.stations.slice(0, 4).map((station) => (
                <button
                  key={station.stationId}
                  type="button"
                  className="ghost-button"
                  data-testid={`uk-flood-station-item-${station.stationId}`}
                  onClick={() => {
                    const selected = ukFloodEntities.find((item) => item.id === `ukflood:station:${station.stationId}`);
                    if (selected) {
                      setSelectedEntity(selected);
                    }
                  }}
                >
                  station | {station.stationLabel} | {station.parameter} {station.value ?? "n/a"}{station.unit ?? ""} |{" "}
                  {station.observedAt ? new Date(station.observedAt).toLocaleString() : "time unknown"}
                </button>
              ))}
            </div>
          </div>
        )}
        {!geonetEnabled ? (
          <div className="empty-state compact" data-testid="geonet-layer-disabled">
            <p>GeoNet layer disabled.</p>
            <span>Enable GeoNet Hazards to load New Zealand quake records and volcanic alert context.</span>
          </div>
        ) : geonetQuery.isLoading ? (
          <div className="empty-state compact" data-testid="geonet-layer-loading">
            <p>Loading GeoNet hazards.</p>
            <span>Fetching source-reported GeoNet quake and volcanic alert records.</span>
          </div>
        ) : geonetQuery.isError ? (
          <div className="empty-state compact" data-testid="geonet-layer-error">
            <p>GeoNet hazards unavailable.</p>
            <span>Unable to load GeoNet hazard records.</span>
          </div>
        ) : (geonetQuery.data?.count ?? 0) === 0 ? (
          <div className="empty-state compact" data-testid="geonet-layer-empty">
            <p>No GeoNet records match current filters.</p>
            <span>Adjust event type, magnitude, alert level, or limit to broaden results.</span>
          </div>
        ) : (
          <div className="stack" data-testid="geonet-layer-summary">
            <div className="data-card data-card--compact">
              <strong>GeoNet Hazards | {geonetQuery.data?.metadata.quakeCount ?? 0} quakes | {geonetQuery.data?.metadata.volcanoCount ?? 0} volcano alerts</strong>
              <span>
                type {environmentalFilters.geonetEventType} | min mag {environmentalFilters.geonetMinMagnitude ?? "none"} | alert {environmentalFilters.geonetAlertLevel} | limit {environmentalFilters.geonetLimit}
              </span>
              <span>
                Source health | {geonetQuery.data?.metadata.sourceMode ?? "unknown"} | loaded{" "}
                {new Date(geonetQuery.data?.metadata.fetchedAt ?? Date.now()).toLocaleString()}
              </span>
              <span>{geonetQuery.data?.metadata.caveat}</span>
            </div>
            <div className="stack" data-testid="geonet-recent-list">
              {geonetQuery.data?.quakes.slice(0, 4).map((event) => (
                <button
                  key={event.eventId}
                  type="button"
                  className="ghost-button"
                  data-testid={`geonet-quake-item-${event.eventId}`}
                  onClick={() => {
                    const selected = geonetEntities.find((item) => item.id === `geonet:quake:${event.eventId}`);
                    if (selected) setSelectedEntity(selected);
                  }}
                >
                  {event.magnitude != null ? `M${event.magnitude.toFixed(1)}` : "M?"} | {event.locality ?? event.title} | {new Date(event.eventTime).toLocaleString()}
                </button>
              ))}
              {geonetQuery.data?.volcanoAlerts.slice(0, 4).map((event) => (
                <button
                  key={event.volcanoId}
                  type="button"
                  className="ghost-button"
                  data-testid={`geonet-volcano-item-${event.volcanoId}`}
                  onClick={() => {
                    const selected = geonetEntities.find((item) => item.id === `geonet:volcano:${event.volcanoId}`);
                    if (selected) setSelectedEntity(selected);
                  }}
                >
                  VAL {event.alertLevel ?? "?"} | {event.volcanoName} | {event.activity ?? "activity unknown"}
                </button>
              ))}
            </div>
          </div>
        )}
        {!hkoWeatherEnabled ? (
          <div className="empty-state compact" data-testid="hko-weather-layer-disabled">
            <p>HKO weather layer disabled.</p>
            <span>Enable HKO Weather to load Hong Kong Observatory warning and cyclone context.</span>
          </div>
        ) : hkoWeatherQuery.isLoading ? (
          <div className="empty-state compact" data-testid="hko-weather-layer-loading">
            <p>Loading HKO weather records.</p>
            <span>Fetching advisory weather warnings and tropical cyclone context from HKO.</span>
          </div>
        ) : hkoWeatherQuery.isError ? (
          <div className="empty-state compact" data-testid="hko-weather-layer-error">
            <p>HKO weather unavailable.</p>
            <span>Unable to load Hong Kong Observatory weather warning records.</span>
          </div>
        ) : ((hkoWeatherQuery.data?.warnings.length ?? 0) + (hkoWeatherQuery.data?.tropicalCyclone ? 1 : 0)) === 0 ? (
          <div className="empty-state compact" data-testid="hko-weather-layer-empty">
            <p>No HKO weather records match current filters.</p>
            <span>Adjust warning type or limit to broaden results.</span>
          </div>
        ) : (
          <div className="stack" data-testid="hko-weather-layer-summary">
            <div className="data-card data-card--compact">
              <strong>
                HKO Weather | {hkoWeatherQuery.data?.metadata.warningCount ?? 0} warnings | cyclone {hkoWeatherQuery.data?.tropicalCyclone ? "yes" : "no"}
              </strong>
              <span>
                warning {environmentalFilters.hkoWarningType} | limit {environmentalFilters.hkoLimit}
              </span>
              <span>
                Source health | {hkoWeatherQuery.data?.metadata.sourceMode ?? "unknown"} | loaded{" "}
                {new Date(hkoWeatherQuery.data?.metadata.fetchedAt ?? Date.now()).toLocaleString()}
              </span>
              <span>{hkoWeatherQuery.data?.metadata.caveat}</span>
            </div>
            <div className="stack" data-testid="hko-weather-recent-list">
              {hkoWeatherQuery.data?.warnings.slice(0, 4).map((event) => (
                <button
                  key={event.eventId}
                  type="button"
                  className="ghost-button"
                  data-testid={`hko-warning-item-${event.eventId}`}
                  onClick={() => {
                    const selected = hkoWeatherEntities.find((item) => item.id === `hko:warning:${event.eventId}`);
                    if (selected) setSelectedEntity(selected);
                  }}
                >
                  {event.warningType}{event.warningLevel ? ` ${event.warningLevel}` : ""} | {event.title} |{" "}
                  {new Date(event.updatedAt ?? event.issuedAt ?? Date.now()).toLocaleString()}
                </button>
              ))}
              {hkoWeatherQuery.data?.tropicalCyclone ? (
                <button
                  type="button"
                  className="ghost-button"
                  data-testid={`hko-tc-item-${hkoWeatherQuery.data.tropicalCyclone.eventId}`}
                  onClick={() => {
                    const selected = hkoWeatherEntities.find((item) => item.id === `hko:tc:${hkoWeatherQuery.data?.tropicalCyclone?.eventId}`);
                    if (selected) setSelectedEntity(selected);
                  }}
                >
                  cyclone | {hkoWeatherQuery.data.tropicalCyclone.signal ?? "signal unknown"} |{" "}
                  {new Date(hkoWeatherQuery.data.tropicalCyclone.updatedAt ?? Date.now()).toLocaleString()}
                </button>
              ) : null}
            </div>
          </div>
        )}
        {!metnoAlertsEnabled ? (
          <div className="empty-state compact" data-testid="metno-alerts-layer-disabled">
            <p>MET Norway alert layer disabled.</p>
            <span>Enable MET Norway Alerts to load advisory CAP-style weather warning context.</span>
          </div>
        ) : metnoAlertsQuery.isLoading ? (
          <div className="empty-state compact" data-testid="metno-alerts-layer-loading">
            <p>Loading MET Norway alerts.</p>
            <span>Fetching backend-served CAP-style alert records with required User-Agent handling.</span>
          </div>
        ) : metnoAlertsQuery.isError ? (
          <div className="empty-state compact" data-testid="metno-alerts-layer-error">
            <p>MET Norway alerts unavailable.</p>
            <span>Unable to load MET Norway advisory warning records.</span>
          </div>
        ) : (metnoAlertsQuery.data?.alerts.length ?? 0) === 0 ? (
          <div className="empty-state compact" data-testid="metno-alerts-layer-empty">
            <p>No MET Norway alerts match current filters.</p>
            <span>Adjust severity, alert type, or limit to broaden results.</span>
          </div>
        ) : (
          <div className="stack" data-testid="metno-alerts-layer-summary">
            <div className="data-card data-card--compact">
              <strong>MET Norway Alerts | {metnoAlertsQuery.data?.count ?? 0} loaded</strong>
              <span>
                severity {environmentalFilters.metnoAlertSeverity} | type {environmentalFilters.metnoAlertType || "all"} | limit {environmentalFilters.metnoLimit}
              </span>
              <span>
                Source health | {metnoAlertsQuery.data?.metadata.sourceMode ?? "unknown"} | loaded{" "}
                {new Date(metnoAlertsQuery.data?.metadata.fetchedAt ?? Date.now()).toLocaleString()}
              </span>
              <span>{metnoAlertsQuery.data?.metadata.caveat}</span>
            </div>
            <div className="stack" data-testid="metno-alerts-recent-list">
              {metnoAlertsQuery.data?.alerts.slice(0, 6).map((event) => (
                <button
                  key={event.eventId}
                  type="button"
                  className="ghost-button"
                  data-testid={`metno-alert-item-${event.eventId}`}
                  onClick={() => {
                    const selected = metnoAlertEntities.find((item) => item.id === `metno:${event.eventId}`);
                    if (selected) setSelectedEntity(selected);
                  }}
                >
                  {event.severity.toUpperCase()} | {event.alertType} | {event.areaDescription ?? event.title} |{" "}
                  {new Date(event.updatedAt ?? event.sentAt ?? event.effectiveAt ?? event.onsetAt ?? Date.now()).toLocaleString()}
                </button>
              ))}
            </div>
          </div>
        )}
        {!canadaCapEnabled ? (
          <div className="empty-state compact" data-testid="canada-cap-layer-disabled">
            <p>Canada CAP layer disabled.</p>
            <span>Enable Canada CAP Alerts to load official Canadian CAP warning and advisory context.</span>
          </div>
        ) : canadaCapQuery.isLoading ? (
          <div className="empty-state compact" data-testid="canada-cap-layer-loading">
            <p>Loading Canada CAP alerts.</p>
            <span>Fetching active Canadian CAP weather alert records.</span>
          </div>
        ) : canadaCapQuery.isError ? (
          <div className="empty-state compact" data-testid="canada-cap-layer-error">
            <p>Canada CAP alerts unavailable.</p>
            <span>Unable to load Environment Canada CAP alert records.</span>
          </div>
        ) : (canadaCapQuery.data?.alerts.length ?? 0) === 0 ? (
          <div className="empty-state compact" data-testid="canada-cap-layer-empty">
            <p>No Canada CAP alerts match current filters.</p>
            <span>Adjust alert type, severity, or limit to broaden results.</span>
          </div>
        ) : (
          <div className="stack" data-testid="canada-cap-layer-summary">
            <div className="data-card data-card--compact">
              <strong>Canada CAP Alerts | {canadaCapQuery.data?.count ?? 0} loaded</strong>
              <span>
                type {environmentalFilters.canadaCapAlertType} | severity {environmentalFilters.canadaCapSeverity} | limit {environmentalFilters.canadaCapLimit}
              </span>
              <span>
                Source health | {canadaCapQuery.data?.metadata.sourceMode ?? "unknown"} | loaded{" "}
                {new Date(canadaCapQuery.data?.metadata.fetchedAt ?? Date.now()).toLocaleString()}
              </span>
              <span>{canadaCapQuery.data?.metadata.caveat}</span>
            </div>
            <div className="stack" data-testid="canada-cap-recent-list">
              {canadaCapQuery.data?.alerts.slice(0, 6).map((event) => (
                <button
                  key={event.eventId}
                  type="button"
                  className="ghost-button"
                  data-testid={`canada-cap-item-${event.eventId}`}
                  onClick={() => {
                    const selected = canadaCapEntities.find((item) => item.id === `canadacap:${event.eventId}`);
                    if (selected) setSelectedEntity(selected);
                  }}
                >
                  {event.alertType} | {event.severity} | {event.title} | {new Date(event.sentAt).toLocaleString()}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      <div className="panel__section">
        <p className="panel__eyebrow">Layer Controls</p>
        {layers.map((layer) => (
          <label
            key={layer.key}
            className={clsx("toggle-row", !layer.available && "toggle-row--disabled")}
          >
            <span>{layer.label}</span>
            <input
              type="checkbox"
              checked={layer.enabled}
              disabled={!layer.available}
              onChange={(event) => setLayerEnabled(layer.key, event.currentTarget.checked)}
            />
          </label>
        ))}
      </div>

      <div className="panel__section">
        <p className="panel__eyebrow">View Presets</p>
        <div className="stack">
          <button type="button" className="ghost-button" onClick={() => onJumpToCity("global")}>
            Global Reset
          </button>
          <button type="button" className="ghost-button" onClick={() => onJumpToCity("austin")}>
            Austin
          </button>
          <button type="button" className="ghost-button" onClick={() => onJumpToCity("nyc")}>
            NYC
          </button>
          <button type="button" className="ghost-button" onClick={() => onJumpToCity("london")}>
            London
          </button>
        </div>
      </div>

      <div className="panel__section">
        <p className="panel__eyebrow">Source Health</p>
        <div className="stack">
          {(status?.sources ?? []).map((source) => (
            <div key={source.name} className="data-card data-card--compact">
              <strong>{source.name}</strong>
              <span>{source.state}</span>
              <span>
                {source.lastSuccessAt
                  ? new Date(source.lastSuccessAt).toLocaleString()
                  : "No successful fetch yet"}
              </span>
              <span>
                {source.degradedReason ?? source.hiddenReason ?? source.detail}
              </span>
            </div>
          ))}
        </div>
      </div>

      <OperatorControlPanel />

      <WebcamOperationsPanel />

      <div className="panel__section">
        <p className="panel__eyebrow">ATC Audio</p>
        <div className="empty-state compact">
          <p>External-only for now.</p>
          <span>In-app playback is only allowed for providers with explicit embed permission.</span>
          <a href="https://www.atc.net/" target="_blank" rel="noreferrer">
            ATC.net
          </a>
          <a href="https://www.liveatc.net/" target="_blank" rel="noreferrer">
            LiveATC (external)
          </a>
        </div>
      </div>

      <div className="panel__section">
        <p className="panel__eyebrow">Saved Views</p>
        <div className="stack">
          <button type="button" className="ghost-button" onClick={onCopyPermalink}>
            Copy Current View
          </button>
          {bookmarks.length === 0 ? (
            <div className="empty-state compact">
              <p>No saved views yet.</p>
              <span>Use Save View in the header to preserve filters, layers, and map position.</span>
            </div>
          ) : (
            bookmarks.map((bookmark) => (
              <div key={bookmark.id} className="data-card data-card--compact">
                <strong>{bookmark.name}</strong>
                <span>{new Date(bookmark.createdAt).toLocaleString()}</span>
                <a href={bookmark.url} target="_blank" rel="noreferrer">
                  Open
                </a>
                <button
                  type="button"
                  className="ghost-button ghost-button--small"
                  onClick={() => removeBookmark(bookmark.id)}
                >
                  Remove
                </button>
              </div>
            ))
          )}
        </div>
      </div>
    </aside>
  );
}
