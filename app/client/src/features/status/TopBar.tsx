import type { PublicConfigResponse, SourceStatusResponse } from "../../types/api";
import { useAppStore } from "../../lib/store";

interface TopBarProps {
  config?: PublicConfigResponse;
  status?: SourceStatusResponse;
  onCommandSubmit: (value: string) => void;
  onCopyPermalink: () => void;
  onSaveBookmark: () => void;
  onExportSnapshot: () => void;
}

export function TopBar({
  config,
  status,
  onCommandSubmit,
  onCopyPermalink,
  onSaveBookmark,
  onExportSnapshot
}: TopBarProps) {
  const healthySources =
    status?.sources.filter((source) => source.enabled && source.state === "healthy").length ?? 0;
  const degradedSources =
    status?.sources.filter((source) => ["stale", "rate-limited", "degraded"].includes(source.state))
      .length ?? 0;
  const hud = useAppStore((state) => state.hud);

  return (
    <header className="topbar">
      <div className="topbar__title">
        <p className="topbar__eyebrow">Public Data OSINT Workspace</p>
        <h1>WorldView Spatial Console</h1>
      </div>
      <form
        className="topbar__command"
        onSubmit={(event) => {
          event.preventDefault();
          const form = new FormData(event.currentTarget);
          onCommandSubmit(String(form.get("command") ?? ""));
        }}
      >
        <input
          className="topbar__command-input"
          type="text"
          name="command"
          placeholder="Try callsign:dal123, icao24:a1b2c3, norad:25544, source:opensky-network, or austin"
          autoComplete="off"
        />
        <button type="submit" className="ghost-button">
          Run
        </button>
      </form>
      <div className="topbar__meta">
        <button type="button" className="ghost-button" onClick={onCopyPermalink}>
          Copy Permalink
        </button>
        <button type="button" className="ghost-button" onClick={onSaveBookmark}>
          Save View
        </button>
        <button type="button" className="ghost-button" onClick={onExportSnapshot}>
          Export Snapshot
        </button>
        <span>{config?.environment ?? "local"} environment</span>
        <span>{hud.imageryModeTitle}</span>
        <span>{hud.imageryModeRole}</span>
        <span>{hud.imagerySensorFamily}</span>
        <span>{hud.imageryShortCaveat}</span>
        <span>{config?.tiles.provider ?? "loading tiles"}</span>
        <span>{healthySources} healthy sources</span>
        <span>{degradedSources} degraded sources</span>
      </div>
    </header>
  );
}
