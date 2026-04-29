import type { ActiveImageryContext } from "../../lib/imageryContext";
import { getImageryContextDisplay, getReplayImageryWarning } from "../../lib/imageryContext";
import { CaveatBlock, SourceBadge, StatusBadge } from "../../components/ui";

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
      </div>
      <div className="imagery-context-badge__row">
        <StatusBadge tone="info">{display.modeRoleLabel}</StatusBadge>
        <StatusBadge>{display.sensorFamilyLabel}</StatusBadge>
        <StatusBadge tone="advisory">{display.historicalFidelityLabel}</StatusBadge>
        <SourceBadge source={display.source} />
      </div>
      {shouldShowWarning ? (
        <CaveatBlock
          compact
          heading={replayWarning.title}
          tone={replayWarning.severity === "warning" ? "warning" : "info"}
        >
          {replayWarning.message}
        </CaveatBlock>
      ) : null}
    </div>
  );
}
