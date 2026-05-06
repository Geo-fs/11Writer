import type { MarineNavtexContextResponse } from "../../types/api";

export interface MarineNavtexContextSummary {
  sourceLine: string;
  broadcastLines: Array<{
    messageId: string;
    label: string;
    warningLine: string;
    detailLine: string;
    caveat?: string | null;
  }>;
  exportLines: string[];
  metadata: {
    sourceId: string;
    sourceMode: "fixture" | "live" | "unknown";
    health:
      | "loaded"
      | "empty"
      | "stale"
      | "degraded"
      | "unavailable"
      | "error"
      | "disabled"
      | "unknown";
    messageTypeFilter:
      | "all"
      | "navigational-warning"
      | "meteorological-warning"
      | "search-and-rescue"
      | "forecast"
      | "other";
    nearbyBroadcastCount: number;
    topIssuedAt?: string | null;
    topBroadcast:
      | {
          messageId: string;
          stationId: string;
          stationName: string;
          subjectIndicator: string;
          subjectLabel?: string | null;
          distanceKm: number;
        }
      | null;
    topSummary: string | null;
    caveats: string[];
  };
}

export function buildMarineNavtexContextSummary(
  response: MarineNavtexContextResponse | null
): MarineNavtexContextSummary | null {
  if (!response) {
    return null;
  }

  const topBroadcast = response.broadcasts[0] ?? null;
  const modeLabel =
    response.sourceHealth.sourceMode === "fixture"
      ? "fixture/local"
      : response.sourceHealth.sourceMode === "live"
        ? "live"
        : "unknown";
  const sourceLine =
    `USCG NAVTEX Broadcast Notices: ${response.sourceHealth.health} | ${modeLabel} | ` +
    `${response.count} nearby broadcast${response.count === 1 ? "" : "s"} | ${formatMessageType(response.messageTypeFilter)}`;
  const broadcastLines = response.broadcasts.slice(0, 2).map((broadcast) => ({
    messageId: broadcast.messageId,
    label: `${broadcast.stationName} | ${broadcast.distanceKm.toFixed(1)} km | ${broadcast.transmitterCharacter}`,
    warningLine: `${broadcast.subjectIndicator}${broadcast.subjectLabel ? ` | ${broadcast.subjectLabel}` : ""}`,
    detailLine: buildBroadcastDetail(broadcast),
    caveat: broadcast.caveats[0] ?? null
  }));

  const topSummary = topBroadcast ? buildBroadcastDetail(topBroadcast) : null;
  const exportLines = [sourceLine];
  if (topBroadcast && topSummary) {
    exportLines.push(`Top NAVTEX broadcast: ${topBroadcast.stationName} | ${topSummary}`);
  }

  return {
    sourceLine,
    broadcastLines,
    exportLines,
    metadata: {
      sourceId: response.sourceHealth.sourceId,
      sourceMode: response.sourceHealth.sourceMode,
      health: response.sourceHealth.health,
      messageTypeFilter: response.messageTypeFilter,
      nearbyBroadcastCount: response.count,
      topIssuedAt: topBroadcast?.issuedAt ?? null,
      topBroadcast: topBroadcast
        ? {
            messageId: topBroadcast.messageId,
            stationId: topBroadcast.stationId,
            stationName: topBroadcast.stationName,
            subjectIndicator: topBroadcast.subjectIndicator,
            subjectLabel: topBroadcast.subjectLabel ?? null,
            distanceKm: topBroadcast.distanceKm
          }
        : null,
      topSummary,
      caveats: [
        ...(response.sourceHealth.caveat ? [response.sourceHealth.caveat] : []),
        ...response.caveats.slice(0, 2),
        ...(topBroadcast?.caveats.slice(0, 1) ?? [])
      ]
    }
  };
}

function buildBroadcastDetail(broadcast: MarineNavtexContextResponse["broadcasts"][number]) {
  const subjectLine = broadcast.subjectLabel ?? `subject ${broadcast.subjectIndicator}`;
  const coverageLine =
    broadcast.coverageRadiusKm != null ? `coverage approx ${broadcast.coverageRadiusKm.toFixed(0)} km` : "coverage radius unavailable";
  return `${subjectLine} | issued ${broadcast.issuedAt} | ${coverageLine}`;
}

function formatMessageType(
  value: MarineNavtexContextResponse["messageTypeFilter"]
) {
  if (value === "navigational-warning") return "navigational warnings";
  if (value === "meteorological-warning") return "meteorological warnings";
  if (value === "search-and-rescue") return "search and rescue";
  if (value === "forecast") return "forecast";
  if (value === "other") return "other subjects";
  return "all warning subjects";
}
