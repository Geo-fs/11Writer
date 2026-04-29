import clsx from "clsx";
import type { ComponentPropsWithoutRef, ReactNode } from "react";
import "../../styles/ui-primitives.css";

type CoreStatusTone = "neutral" | "info" | "success" | "warning" | "danger";
type StatusTone =
  | CoreStatusTone
  | "available"
  | "unavailable"
  | "advisory";
type PriorityLevel = "low" | "medium" | "high";
type SourceBadgeTone = StatusTone | "source";
type EmptyStateVariant = "empty" | "loading" | "error" | "disabled" | "unavailable";
type CaveatTone = "info" | "warning" | "danger" | "source" | "evidence";
type FreshnessValue = "fresh" | "recent" | "possibly-stale" | "unknown";
type DataBasis =
  | "observed"
  | "inferred"
  | "derived"
  | "scored"
  | "summary"
  | "contextual"
  | "advisory"
  | "unavailable";

export function InspectorSection({
  eyebrow,
  className,
  children,
  ...props
}: ComponentPropsWithoutRef<"section"> & {
  eyebrow?: ReactNode;
}) {
  return (
    <section className={clsx("panel__section", className)} {...props}>
      {eyebrow ? <p className="panel__eyebrow">{eyebrow}</p> : null}
      {children}
    </section>
  );
}

export function EvidenceCard({
  heading,
  badge,
  compact = false,
  className,
  children,
  ...props
}: ComponentPropsWithoutRef<"article"> & {
  heading?: ReactNode;
  badge?: ReactNode;
  compact?: boolean;
}) {
  return (
    <article className={clsx("data-card", compact && "data-card--compact", className)} {...props}>
      {heading != null || badge != null ? (
        <div className="ui-evidence-card__header">
          {heading != null ? <div className="ui-evidence-card__title">{heading}</div> : null}
          {badge}
        </div>
      ) : null}
      {children}
    </article>
  );
}

export function StatusBadge({
  tone = "neutral",
  className,
  children,
  ...props
}: ComponentPropsWithoutRef<"span"> & {
  tone?: StatusTone;
}) {
  const resolvedTone = resolveStatusTone(tone);

  return (
    <span className={clsx("ui-badge", `ui-badge--${resolvedTone}`, className)} {...props}>
      {children}
    </span>
  );
}

export function PriorityBadge({
  priority,
  score,
  rank,
  prefix = "Priority",
  className,
  ...props
}: Omit<ComponentPropsWithoutRef<"span">, "children"> & {
  priority: PriorityLevel;
  score?: number | null;
  rank?: number | null;
  prefix?: string;
}) {
  const tone: Record<PriorityLevel, StatusTone> = {
    low: "info",
    medium: "warning",
    high: "danger"
  };

  return (
    <StatusBadge
      tone={tone[priority]}
      className={className}
      {...props}
    >
      {prefix}: {priority.toUpperCase()}
      {score != null ? ` (${score.toFixed(1)})` : ""}
      {rank != null ? ` #${rank}` : ""}
    </StatusBadge>
  );
}

export function FreshnessBadge({
  value,
  prefix = "Freshness",
  className,
  ...props
}: Omit<ComponentPropsWithoutRef<"span">, "children"> & {
  value: FreshnessValue;
  prefix?: ReactNode;
}) {
  return (
    <StatusBadge
      tone={freshnessTone(value)}
      className={clsx("ui-freshness-badge", className)}
      {...props}
    >
      {prefix}: {value}
    </StatusBadge>
  );
}

export function DataBasisBadge({
  basis,
  prefix,
  className,
  ...props
}: Omit<ComponentPropsWithoutRef<"span">, "children"> & {
  basis: DataBasis;
  prefix?: ReactNode;
}) {
  return (
    <StatusBadge
      tone={dataBasisTone(basis)}
      className={clsx("ui-data-basis-badge", className)}
      {...props}
    >
      {prefix ? `${prefix}: ` : ""}
      {basis}
    </StatusBadge>
  );
}

export function SourceBadge({
  source,
  label = "Source",
  tone = "source",
  className,
  ...props
}: Omit<ComponentPropsWithoutRef<"span">, "children"> & {
  source: ReactNode;
  label?: ReactNode;
  tone?: SourceBadgeTone;
}) {
  const resolvedTone = resolveSourceBadgeTone(tone);

  return (
    <span className={clsx("ui-source-badge", `ui-source-badge--${resolvedTone}`, className)} {...props}>
      <span className="ui-source-badge__label">{label}</span>
      <span>{source}</span>
    </span>
  );
}

export function SourceHealthRow({
  source,
  status,
  statusTone = "neutral",
  freshness,
  summary,
  caveat,
  className,
  ...props
}: ComponentPropsWithoutRef<"div"> & {
  source: ReactNode;
  status: ReactNode;
  statusTone?: StatusTone;
  freshness?: FreshnessValue | null;
  summary?: ReactNode;
  caveat?: ReactNode;
}) {
  return (
    <div className={clsx("ui-source-health-row", className)} {...props}>
      <div className="ui-source-health-row__top">
        <SourceBadge source={source} />
        <div className="ui-source-health-row__badges">
          <StatusBadge tone={statusTone}>{status}</StatusBadge>
          {freshness ? <FreshnessBadge value={freshness} prefix="Age" /> : null}
        </div>
      </div>
      {summary != null ? <div className="ui-source-health-row__summary">{summary}</div> : null}
      {caveat != null ? (
        <div className="ui-source-health-row__caveat">
          <CaveatBlock compact tone="source" heading="Source note">
            {caveat}
          </CaveatBlock>
        </div>
      ) : null}
    </div>
  );
}

export function EmptyState({
  heading,
  description,
  variant = "empty",
  compact = false,
  className,
  children,
  ...props
}: ComponentPropsWithoutRef<"div"> & {
  heading: ReactNode;
  description?: ReactNode;
  variant?: EmptyStateVariant;
  compact?: boolean;
}) {
  return (
    <div
      className={clsx("empty-state", `ui-empty-state--${variant}`, compact && "compact", className)}
      {...props}
    >
      <p className="ui-empty-state__title">{heading}</p>
      {description != null ? <span className="ui-empty-state__detail">{description}</span> : null}
      {children}
    </div>
  );
}

export function CaveatBlock({
  heading = "Caveat",
  tone = "warning",
  compact = false,
  className,
  children,
  ...props
}: ComponentPropsWithoutRef<"div"> & {
  heading?: ReactNode;
  tone?: CaveatTone;
  compact?: boolean;
}) {
  return (
    <div
      className={clsx(
        "ui-caveat-block",
        `ui-caveat-block--${tone}`,
        compact && "ui-caveat-block--compact",
        className
      )}
      {...props}
    >
      <strong className="ui-caveat-block__title">{heading}</strong>
      <div className="ui-caveat-block__body">{children}</div>
    </div>
  );
}

export function MetricRow({
  label,
  value,
  className,
  ...props
}: ComponentPropsWithoutRef<"div"> & {
  label: ReactNode;
  value: ReactNode;
}) {
  return (
    <div className={clsx("ui-metric-row", className)} {...props}>
      <span className="ui-metric-row__label">{label}</span>
      <span className="ui-metric-row__value">{value}</span>
    </div>
  );
}

export function CompactContextRow({
  label,
  value,
  detail,
  caveat,
  badge,
  className,
  ...props
}: ComponentPropsWithoutRef<"div"> & {
  label: ReactNode;
  value: ReactNode;
  detail?: ReactNode;
  caveat?: ReactNode;
  badge?: ReactNode;
}) {
  return (
    <div className={clsx("ui-compact-context-row", className)} {...props}>
      <div className="ui-compact-context-row__header">
        <span className="ui-compact-context-row__label">{label}</span>
        {badge}
      </div>
      <div className="ui-compact-context-row__value">{value}</div>
      {detail != null ? <div className="ui-compact-context-row__detail">{detail}</div> : null}
      {caveat != null ? <div className="ui-compact-context-row__caveat">{caveat}</div> : null}
    </div>
  );
}

export function SignalBreakdown({
  sections,
  emptyLabel = "None.",
  className,
  ...props
}: ComponentPropsWithoutRef<"div"> & {
  sections: Array<{ title: ReactNode; items: string[] }>;
  emptyLabel?: ReactNode;
}) {
  return (
    <div className={clsx("ui-signal-breakdown", className)} {...props}>
      {sections.map((section, index) => (
        <div key={index} className="ui-signal-breakdown__group">
          <strong>{section.title}</strong>
          {section.items.length === 0 ? (
            <span className="ui-signal-breakdown__empty">{emptyLabel}</span>
          ) : (
            <ul>
              {section.items.map((item, itemIndex) => (
                <li key={itemIndex}>{item}</li>
              ))}
            </ul>
          )}
        </div>
      ))}
    </div>
  );
}

function resolveStatusTone(tone: StatusTone): CoreStatusTone {
  switch (tone) {
    case "available":
      return "success";
    case "unavailable":
      return "danger";
    case "advisory":
      return "warning";
    default:
      return tone;
  }
}

function resolveSourceBadgeTone(tone: SourceBadgeTone) {
  if (tone === "source") {
    return "source";
  }
  return resolveStatusTone(tone);
}

function freshnessTone(value: FreshnessValue): StatusTone {
  switch (value) {
    case "fresh":
      return "available";
    case "recent":
      return "info";
    case "possibly-stale":
      return "advisory";
    case "unknown":
      return "neutral";
  }
}

function dataBasisTone(value: DataBasis): StatusTone {
  switch (value) {
    case "observed":
      return "available";
    case "derived":
      return "info";
    case "inferred":
      return "warning";
    case "scored":
      return "info";
    case "summary":
      return "neutral";
    case "contextual":
      return "advisory";
    case "advisory":
      return "warning";
    case "unavailable":
      return "unavailable";
  }
}
