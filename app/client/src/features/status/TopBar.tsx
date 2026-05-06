import type { PublicConfigResponse, SourceStatusResponse } from "../../types/api";
import { useAppStore } from "../../lib/store";
import { WorkbenchButton, WorkbenchInput } from "../../components/ui";
import type { WorkbenchModeId } from "../workbench/workbenchModes";

interface TopBarProps {
  config?: PublicConfigResponse;
  status?: SourceStatusResponse;
  activeModeId: WorkbenchModeId;
  onCommandSubmit: (value: string) => void;
  onCopyPermalink: () => void;
  onSaveBookmark: () => void;
  onExportSnapshot: () => void;
}

export function TopBar({
  config,
  status,
  activeModeId,
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
        <p className="topbar__eyebrow">11Writer Workbench</p>
        <h1>Situation Workspace</h1>
        <span className="topbar__subtitle">{activeModeId === "map" ? "Map mode" : `${activeModeId} mode`}</span>
      </div>
      <form
        className="topbar__command"
        onSubmit={(event) => {
          event.preventDefault();
          const form = new FormData(event.currentTarget);
          onCommandSubmit(String(form.get("command") ?? ""));
        }}
      >
        <WorkbenchInput
          className="topbar__command-input"
          type="text"
          name="command"
          placeholder="Try callsign:dal123, icao24:a1b2c3, norad:25544, source:opensky-network, or austin"
          autoComplete="off"
        />
        <WorkbenchButton type="submit" tone="primary">
          Run
        </WorkbenchButton>
      </form>
      <div className="topbar__meta">
        <WorkbenchButton type="button" onClick={onCopyPermalink}>
          Copy Permalink
        </WorkbenchButton>
        <WorkbenchButton type="button" onClick={onSaveBookmark}>
          Save View
        </WorkbenchButton>
        <WorkbenchButton type="button" onClick={onExportSnapshot}>
          Export Snapshot
        </WorkbenchButton>
        <span>Mode {activeModeId}</span>
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
