import clsx from "clsx";
import { WORKBENCH_MODES, type WorkbenchModeId } from "./workbenchModes";

interface WorkbenchActivityRailProps {
  activeModeId: WorkbenchModeId;
  availableModeIds?: WorkbenchModeId[];
}

export function WorkbenchActivityRail({
  activeModeId,
  availableModeIds = [activeModeId]
}: WorkbenchActivityRailProps) {
  const available = new Set(availableModeIds);

  return (
    <nav className="workbench-activity-rail" aria-label="Workbench modes">
      <div className="workbench-activity-rail__brand">
        <span>11</span>
      </div>
      <div className="workbench-activity-rail__items">
        {WORKBENCH_MODES.map((mode) => {
          const isActive = mode.id === activeModeId;
          const isAvailable = available.has(mode.id);
          return (
            <button
              key={mode.id}
              type="button"
              className={clsx(
                "workbench-activity-rail__item",
                isActive && "workbench-activity-rail__item--active"
              )}
              aria-pressed={isActive}
              aria-label={mode.label}
              title={isAvailable ? `${mode.label}: ${mode.description}` : `${mode.label}: reserved shell slot`}
              disabled={!isAvailable}
            >
              <span>{mode.shortLabel}</span>
            </button>
          );
        })}
      </div>
    </nav>
  );
}
