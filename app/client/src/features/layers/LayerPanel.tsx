import clsx from "clsx";
import { useEarthquakeEventsQuery } from "../../lib/queries";
import { groupPlanetImageryModes } from "../../lib/planetImagery";
import { useAppStore } from "../../lib/store";
import type { SourceStatusResponse } from "../../types/api";
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
  const setLayerEnabled = useAppStore((state) => state.setLayerEnabled);
  const setImageryModeId = useAppStore((state) => state.setImageryModeId);
  const setFilters = useAppStore((state) => state.setFilters);
  const environmentalFilters = useAppStore((state) => state.environmentalFilters);
  const setEnvironmentalFilters = useAppStore((state) => state.setEnvironmentalFilters);
  const earthquakeEntities = useAppStore((state) => state.earthquakeEntities);
  const setSelectedEntity = useAppStore((state) => state.setSelectedEntity);
  const removeBookmark = useAppStore((state) => state.removeBookmark);
  const earthquakesEnabled = layers.find((layer) => layer.key === "earthquakes")?.enabled ?? false;
  const earthquakeQuery = useEarthquakeEventsQuery(environmentalFilters, earthquakesEnabled);
  const strongestMagnitude = earthquakeQuery.data?.events.reduce<number | null>(
    (max, event) => {
      if (event.magnitude == null) return max;
      if (max == null) return event.magnitude;
      return event.magnitude > max ? event.magnitude : max;
    },
    null
  );
  const newestTime = earthquakeQuery.data?.events[0]?.time ?? null;
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
