import type { MarineScottishWaterOverflowResponse } from "../../types/api";

export interface MarineScottishWaterContextSummary {
  sourceLine: string;
  eventLines: Array<{
    eventId: string;
    label: string;
    statusLine: string;
    detailLine: string;
    caveat?: string | null;
  }>;
  exportLines: string[];
  metadata: {
    sourceId: string;
    sourceMode: "fixture" | "live" | "unknown";
    health: "loaded" | "empty" | "stale" | "error" | "disabled" | "unknown";
    nearbyMonitorCount: number;
    activeMonitorCount: number;
    topMonitor:
      | {
          eventId: string;
          siteName: string;
          status: "active" | "inactive" | "unknown";
          distanceKm?: number | null;
        }
      | null;
    caveats: string[];
  };
}

export function buildMarineScottishWaterContextSummary(
  response: MarineScottishWaterOverflowResponse | null
): MarineScottishWaterContextSummary | null {
  if (!response) {
    return null;
  }

  const topMonitor =
    response.events.find((event) => event.status === "active") ?? response.events[0] ?? null;
  const modeLabel =
    response.sourceHealth.sourceMode === "fixture"
      ? "fixture/local"
      : response.sourceHealth.sourceMode === "live"
        ? "live"
        : "unknown";
  const sourceLine = `Scottish Water Overflows: ${response.sourceHealth.health} | ${modeLabel} | ${response.count} nearby monitor${response.count === 1 ? "" : "s"} | ${response.activeCount} active`;
  const eventLines = response.events.slice(0, 2).map((event) => ({
    eventId: event.eventId,
    label: `${event.siteName}${event.distanceKm != null ? ` | ${event.distanceKm.toFixed(1)} km` : ""}`,
    statusLine: `${event.status}${event.startedAt ? ` | started ${event.startedAt}` : ""}`,
    detailLine: buildOverflowDetail(event),
    caveat: event.caveats[0] ?? null
  }));

  const exportLines = [sourceLine];
  if (topMonitor) {
    exportLines.push(
      `Top overflow monitor: ${topMonitor.siteName} | ${topMonitor.status}${topMonitor.distanceKm != null ? ` | ${topMonitor.distanceKm.toFixed(1)} km` : ""}`
    );
  }

  return {
    sourceLine,
    eventLines,
    exportLines,
    metadata: {
      sourceId: response.sourceHealth.sourceId,
      sourceMode: response.sourceHealth.sourceMode,
      health: response.sourceHealth.health,
      nearbyMonitorCount: response.count,
      activeMonitorCount: response.activeCount,
      topMonitor: topMonitor
        ? {
            eventId: topMonitor.eventId,
            siteName: topMonitor.siteName,
            status: topMonitor.status,
            distanceKm: topMonitor.distanceKm ?? null
          }
        : null,
      caveats: [
        ...(response.sourceHealth.caveat ? [response.sourceHealth.caveat] : []),
        ...response.caveats.slice(0, 2)
      ]
    }
  };
}

function buildOverflowDetail(event: MarineScottishWaterOverflowResponse["events"][number]) {
  const parts: string[] = [];
  if (event.waterBody) {
    parts.push(event.waterBody);
  }
  if (event.locationLabel) {
    parts.push(event.locationLabel);
  }
  if (event.durationMinutes != null) {
    parts.push(`duration ${event.durationMinutes} min`);
  }
  if (event.lastUpdatedAt) {
    parts.push(`updated ${event.lastUpdatedAt}`);
  }
  return parts.join(" | ") || "Source-reported overflow monitor context loaded";
}
