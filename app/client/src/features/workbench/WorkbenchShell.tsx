import type { ReactNode } from "react";
import type { WorkbenchModeId } from "./workbenchModes";

interface WorkbenchShellProps {
  activeModeId: WorkbenchModeId;
  activityRail: ReactNode;
  topBar: ReactNode;
  sidebar: ReactNode;
  center: ReactNode;
  inspector: ReactNode;
  statusStrip: ReactNode;
}

export function WorkbenchShell({
  activeModeId,
  activityRail,
  topBar,
  sidebar,
  center,
  inspector,
  statusStrip
}: WorkbenchShellProps) {
  return (
    <div className="workbench-shell" data-workbench-mode={activeModeId}>
      <aside className="workbench-shell__rail">{activityRail}</aside>
      <div className="workbench-shell__frame">
        <div className="workbench-shell__topbar">{topBar}</div>
        <div className="workbench-shell__body">
          <div className="workbench-shell__sidebar">{sidebar}</div>
          <main className="workbench-shell__center">{center}</main>
          <div className="workbench-shell__inspector">{inspector}</div>
        </div>
        <div className="workbench-shell__status">{statusStrip}</div>
      </div>
    </div>
  );
}
