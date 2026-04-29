import type { HudState } from "./store";

export interface ActiveImageryContext {
  modeId: string;
  title: string;
  source: string;
  modeRole: string;
  sensorFamily: string;
  historicalFidelity: string;
  shortCaveat: string;
  replayShortNote: string;
  status: string;
  displayTags?: string[];
}

export interface ImageryContextDisplay {
  title: string;
  source: string;
  modeRoleLabel: string;
  sensorFamilyLabel: string;
  historicalFidelityLabel: string;
  shortCaveat: string;
  replayShortNote: string;
  tags: string[];
}

export interface ReplayImageryWarning {
  severity: "none" | "info" | "warning";
  title: string;
  message: string;
  shouldShowInReplay: boolean;
}

export function buildActiveImageryContextFromHud(hud: HudState): ActiveImageryContext {
  return {
    modeId: hud.imageryModeId,
    title: hud.imageryModeTitle,
    source: hud.imagerySource,
    modeRole: hud.imageryModeRole,
    sensorFamily: hud.imagerySensorFamily,
    historicalFidelity: hud.imageryHistoricalFidelity,
    shortCaveat: hud.imageryShortCaveat,
    replayShortNote: hud.imageryReplayShortNote,
    status: hud.imageryStatus
  };
}

export function getImageryContextDisplay(context: ActiveImageryContext | null | undefined): ImageryContextDisplay {
  if (!context) {
    return {
      title: "Imagery unavailable",
      source: "Imagery source unavailable",
      modeRoleLabel: "Mode role unknown",
      sensorFamilyLabel: "Sensor family unknown",
      historicalFidelityLabel: "Historical fidelity unknown",
      shortCaveat: "No active imagery context is available.",
      replayShortNote: "Replay interpretation note unavailable.",
      tags: []
    };
  }

  return {
    title: context.title,
    source: context.source,
    modeRoleLabel: toModeRoleLabel(context.modeRole),
    sensorFamilyLabel: toSensorFamilyLabel(context.sensorFamily),
    historicalFidelityLabel: toHistoricalFidelityLabel(context.historicalFidelity),
    shortCaveat: context.shortCaveat,
    replayShortNote: context.replayShortNote,
    tags: context.displayTags ?? []
  };
}

export function getReplayImageryWarning(
  context: ActiveImageryContext | null | undefined
): ReplayImageryWarning {
  if (!context || !context.historicalFidelity) {
    return {
      severity: "none",
      title: "",
      message: "",
      shouldShowInReplay: false
    };
  }

  const sensorFamily = context.sensorFamily.toLowerCase();
  const historicalFidelity = context.historicalFidelity.toLowerCase();
  const isAnalysisLayer = context.modeRole === "analysis-layer";
  const shortNote = context.replayShortNote || "Imagery timing context is limited for replay interpretation.";

  if (sensorFamily === "radar") {
    return {
      severity: "warning",
      title: "Replay over radar analysis imagery",
      message: `${shortNote} Radar backscatter is interpretation-sensitive and is not optical ground truth.`,
      shouldShowInReplay: true
    };
  }

  if (historicalFidelity === "multi-day-approximate" || isAnalysisLayer) {
    return {
      severity: "warning",
      title: "Replay over non-literal imagery context",
      message: shortNote,
      shouldShowInReplay: true
    };
  }

  if (historicalFidelity === "daily-approximate") {
    return {
      severity: "info",
      title: "Replay over daily approximate imagery",
      message: shortNote,
      shouldShowInReplay: true
    };
  }

  if (historicalFidelity === "composite-reference") {
    return {
      severity: "info",
      title: "Replay over reference composite imagery",
      message: shortNote,
      shouldShowInReplay: true
    };
  }

  return {
    severity: "none",
    title: "",
    message: "",
    shouldShowInReplay: false
  };
}

export function formatReplayImageryDisclosure(context: ActiveImageryContext): string {
  const warning = getReplayImageryWarning(context);
  if (warning.severity === "none") {
    return `${context.title}: ${context.replayShortNote}`;
  }
  return `${warning.title}: ${warning.message}`;
}

function toModeRoleLabel(modeRole: string) {
  switch (modeRole) {
    case "default-basemap":
      return "Default basemap";
    case "optional-basemap":
      return "Optional basemap";
    case "analysis-layer":
      return "Analysis layer";
    default:
      return "Mode role unknown";
  }
}

function toSensorFamilyLabel(sensorFamily: string) {
  switch (sensorFamily) {
    case "optical":
      return "Optical imagery";
    case "radar":
      return "Radar / SAR imagery";
    case "thematic":
      return "Thematic analysis imagery";
    default:
      return "Sensor family unknown";
  }
}

function toHistoricalFidelityLabel(historicalFidelity: string) {
  switch (historicalFidelity) {
    case "composite-reference":
      return "Composite reference context";
    case "daily-approximate":
      return "Daily approximate context";
    case "multi-day-approximate":
      return "Multi-day approximate context";
    default:
      return "Historical fidelity unknown";
  }
}
