import type { ActiveImageryContext } from "../../lib/imageryContext";
import { getImageryContextDisplay, getReplayImageryWarning } from "../../lib/imageryContext";

interface ImageryContextBadgeProps {
  context: ActiveImageryContext | null;
  isReplayContext?: boolean;
}

export function ImageryContextBadge({ context, isReplayContext = false }: ImageryContextBadgeProps) {
  const display = getImageryContextDisplay(context);
  const replayWarning = getReplayImageryWarning(context);
  const shouldShowWarning = isReplayContext && replayWarning.shouldShowInReplay && replayWarning.severity !== "none";

  return (
    <div className="imagery-context-badge" role="status" aria-live="polite">
      <div className="imagery-context-badge__row">
        <strong>{display.title}</strong>
        <span>{display.modeRoleLabel}</span>
        <span>{display.sensorFamilyLabel}</span>
      </div>
      <div className="imagery-context-badge__row imagery-context-badge__row--meta">
        <span>{display.source}</span>
        <span>{display.historicalFidelityLabel}</span>
      </div>
      {shouldShowWarning ? (
        <div className={`imagery-context-warning imagery-context-warning--${replayWarning.severity}`}>
          <span>{replayWarning.title}: </span>
          <span>{replayWarning.message}</span>
        </div>
      ) : null}
    </div>
  );
}
