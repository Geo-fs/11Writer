import type { ActiveImageryContext } from "../../lib/imageryContext";
import { getImageryContextDisplay, getReplayImageryWarning } from "../../lib/imageryContext";
import {
  CaveatBlock,
  EvidenceCard,
  MetricRow,
  SourceBadge,
  StatusBadge
} from "../../components/ui";

interface ImageryContextPanelProps {
  context: ActiveImageryContext | null;
  isReplayContext?: boolean;
}

export function ImageryContextPanel({ context, isReplayContext = false }: ImageryContextPanelProps) {
  const display = getImageryContextDisplay(context);
  const replayWarning = getReplayImageryWarning(context);
  const shouldShowWarning = isReplayContext && replayWarning.shouldShowInReplay && replayWarning.severity !== "none";

  return (
    <EvidenceCard
      aria-label="Imagery context"
      className="imagery-context-panel"
      compact
      heading={<strong>{display.title}</strong>}
    >
      <div className="imagery-context-panel__meta">
        <StatusBadge tone="info">{display.modeRoleLabel}</StatusBadge>
        <StatusBadge>{display.sensorFamilyLabel}</StatusBadge>
        <StatusBadge tone="advisory">{display.historicalFidelityLabel}</StatusBadge>
      </div>
      <MetricRow label="Source" value={<SourceBadge source={display.source} />} />
      {display.tags.length > 0 ? (
        <div className="imagery-context-panel__tags">
          {display.tags.map((tag) => (
            <StatusBadge key={tag} tone="neutral">
              {tag}
            </StatusBadge>
          ))}
        </div>
      ) : null}
      <CaveatBlock heading="Imagery caveat" tone="source">
        {display.shortCaveat}
      </CaveatBlock>
      <CaveatBlock heading="Replay note" tone={isReplayContext ? "warning" : "evidence"}>
        {display.replayShortNote}
      </CaveatBlock>
      {shouldShowWarning ? (
        <CaveatBlock heading={replayWarning.title} tone={replayWarning.severity === "warning" ? "warning" : "info"}>
          {replayWarning.message}
        </CaveatBlock>
      ) : null}
    </EvidenceCard>
  );
}
