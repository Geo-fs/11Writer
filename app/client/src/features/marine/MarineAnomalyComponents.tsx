import type { MarineAnomalyScore } from "../../types/api";

export function MarineAnomalyBadge({ anomaly }: { anomaly: MarineAnomalyScore }) {
  return (
    <span
      className={`marine-anomaly-badge marine-anomaly-badge--${anomaly.level}`}
      data-testid="marine-anomaly-badge"
    >
      Attention priority: {anomaly.level.toUpperCase()} ({anomaly.score.toFixed(1)})
      {anomaly.priorityRank != null ? ` #${anomaly.priorityRank}` : ""}
    </span>
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
    <div className="marine-anomaly-signals" data-testid="marine-anomaly-signals">
      <MarineAnomalyReasonsList title="Observed signals" items={anomaly.observedSignals} />
      <MarineAnomalyReasonsList title="Inferred signals" items={anomaly.inferredSignals} />
      <MarineAnomalyReasonsList title="Scored signals" items={anomaly.scoredSignals} />
    </div>
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
    <div className="data-card marine-anomaly-panel" data-testid="marine-anomaly-panel">
      <strong>{title}</strong>
      <MarineAnomalyBadge anomaly={anomaly} />
      <span>{anomaly.displayLabel}</span>
      {note ? <span className="marine-anomaly-muted">{note}</span> : null}
      <MarineAnomalyReasonsList title="Reasons" items={anomaly.reasons} testId="marine-anomaly-reasons" />
      <MarineAnomalyReasonsList title="Caveats" items={anomaly.caveats} testId="marine-anomaly-caveats" />
      <MarineAnomalySignalBreakdown anomaly={anomaly} />
    </div>
  );
}
