import type { ActiveImageryContext } from "../../lib/imageryContext";
import { getImageryContextDisplay, getReplayImageryWarning } from "../../lib/imageryContext";

interface ImageryContextPanelProps {
  context: ActiveImageryContext | null;
  isReplayContext?: boolean;
}

export function ImageryContextPanel({ context, isReplayContext = false }: ImageryContextPanelProps) {
  const display = getImageryContextDisplay(context);
  const replayWarning = getReplayImageryWarning(context);
  const shouldShowWarning = isReplayContext && replayWarning.shouldShowInReplay && replayWarning.severity !== "none";

  return (
    <section className="imagery-context-panel data-card data-card--compact" aria-label="Imagery context">
      <div className="imagery-context-panel__title">
        <strong>{display.title}</strong>
      </div>
      <div className="imagery-context-panel__meta">
        <span>{display.modeRoleLabel}</span>
        <span>{display.sensorFamilyLabel}</span>
        <span>{display.historicalFidelityLabel}</span>
      </div>
      <div className="imagery-context-panel__meta">
        <span>Source: {display.source}</span>
      </div>
      {display.tags.length > 0 ? (
        <div className="imagery-context-panel__tags">
          {display.tags.map((tag) => (
            <span key={tag}>{tag}</span>
          ))}
        </div>
      ) : null}
      <div className="imagery-context-panel__text">
        <span>Caveat: {display.shortCaveat}</span>
      </div>
      <div className="imagery-context-panel__text">
        <span>Replay note: {display.replayShortNote}</span>
      </div>
      {shouldShowWarning ? (
        <div className={`imagery-context-warning imagery-context-warning--${replayWarning.severity}`}>
          <span>{replayWarning.title}: </span>
          <span>{replayWarning.message}</span>
        </div>
      ) : null}
    </section>
  );
}
