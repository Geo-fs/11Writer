import type { MarineAnomalyScore } from "../../types/api";
import {
  CaveatBlock,
  DataBasisBadge,
  EvidenceCard,
  PriorityBadge,
  SignalBreakdown
} from "../../components/ui";

export function MarineAnomalyBadge({ anomaly }: { anomaly: MarineAnomalyScore }) {
  return (
    <PriorityBadge
      className={`marine-anomaly-badge marine-anomaly-badge--${anomaly.level}`}
      data-testid="marine-anomaly-badge"
      priority={anomaly.level}
      score={anomaly.score}
      rank={anomaly.priorityRank}
      prefix="Attention priority"
    />
  );
}

export function MarineAnomalyReasonsList({
  title,
  items,
  testId
}: {
  title: string;
  items: string[];
  testId?: string;
}) {
  return (
    <div className="marine-anomaly-group" data-testid={testId}>
      <strong>{title}</strong>
      {items.length === 0 ? (
        <span className="marine-anomaly-muted">None.</span>
      ) : (
        <ul>
          {items.map((item, index) => (
            <li key={`${title}-${index}`}>{item}</li>
          ))}
        </ul>
      )}
    </div>
  );
}

export function MarineAnomalySignalBreakdown({ anomaly }: { anomaly: MarineAnomalyScore }) {
  return (
    <SignalBreakdown
      className="marine-anomaly-signals"
      data-testid="marine-anomaly-signals"
      sections={[
        { title: <DataBasisBadge basis="observed" prefix="Basis" />, items: anomaly.observedSignals },
        { title: <DataBasisBadge basis="inferred" prefix="Basis" />, items: anomaly.inferredSignals },
        { title: <DataBasisBadge basis="scored" prefix="Basis" />, items: anomaly.scoredSignals }
      ]}
    />
  );
}

export function MarineAnomalyPanel({
  title,
  anomaly,
  note
}: {
  title: string;
  anomaly: MarineAnomalyScore;
  note?: string;
}) {
  return (
    <EvidenceCard
      className="marine-anomaly-panel"
      data-testid="marine-anomaly-panel"
      heading={<strong>{title}</strong>}
    >
      <MarineAnomalyBadge anomaly={anomaly} />
      <span>{anomaly.displayLabel}</span>
      {note ? <span className="marine-anomaly-muted">{note}</span> : null}
      <MarineAnomalyReasonsList title="Reasons" items={anomaly.reasons} testId="marine-anomaly-reasons" />
      {anomaly.caveats.length > 0 ? (
        <CaveatBlock heading="Caveats" tone="evidence" data-testid="marine-anomaly-caveats">
          {anomaly.caveats.join(" | ")}
        </CaveatBlock>
      ) : null}
      <MarineAnomalySignalBreakdown anomaly={anomaly} />
    </EvidenceCard>
  );
}
