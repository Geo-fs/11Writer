export type WorkbenchModeId =
  | "now"
  | "map"
  | "timeline"
  | "queue"
  | "sources"
  | "reports"
  | "exports"
  | "tasks";

export interface WorkbenchModeDefinition {
  id: WorkbenchModeId;
  label: string;
  shortLabel: string;
  description: string;
}

export const WORKBENCH_MODES: WorkbenchModeDefinition[] = [
  { id: "now", label: "Now", shortLabel: "NW", description: "Cross-domain attention and degraded states." },
  { id: "map", label: "Map", shortLabel: "MP", description: "Geography-first orientation and layer work." },
  { id: "timeline", label: "Timeline", shortLabel: "TL", description: "Temporal sequence and freshness review." },
  { id: "queue", label: "Queue", shortLabel: "QU", description: "Review items, anomalies, and operator follow-up." },
  { id: "sources", label: "Sources", shortLabel: "SO", description: "Source health, freshness, and validation posture." },
  { id: "reports", label: "Reports", shortLabel: "RP", description: "Question-driven evidence packaging and briefing." },
  { id: "exports", label: "Exports", shortLabel: "EX", description: "Saved evidence packets and export outputs." },
  { id: "tasks", label: "Tasks", shortLabel: "TK", description: "Monitors, jobs, and runtime-visible tasks." }
];
