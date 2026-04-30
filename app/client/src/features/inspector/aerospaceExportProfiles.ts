import type { AerospaceExportProfileId } from "../../lib/store";
import type { AerospaceContextAvailabilitySummary } from "./aerospaceContextAvailability";
import type { AerospaceFocusHistorySummary } from "./aerospaceFocusMode";
import type { AerospaceOperationalContextSummary } from "./aerospaceOperationalContext";
import type { AerospaceSourceHealthSummary } from "./aerospaceSourceHealth";

export interface AerospaceExportProfileDefinition {
  id: AerospaceExportProfileId;
  label: string;
  description: string;
  includedMetadataKeys: string[];
  preferredFooterSections: string[];
  caveat: string;
}

export interface AerospaceExportProfileSummary {
  profileId: AerospaceExportProfileId;
  profileLabel: string;
  includedSections: string[];
  caveat: string;
  footerLines: string[];
  metadata: {
    profileId: AerospaceExportProfileId;
    profileLabel: string;
    includedSections: string[];
    caveat: string;
  };
}

export const AEROSPACE_EXPORT_PROFILES: AerospaceExportProfileDefinition[] = [
  {
    id: "compact-evidence",
    label: "Compact Evidence",
    description: "Prioritizes selected-target evidence and the most important trust caveats.",
    includedMetadataKeys: ["selectedTargetSummary", "aerospaceDataHealth", "aerospaceOperationalContext"],
    preferredFooterSections: ["selected-target", "data-health", "operational-context", "availability"],
    caveat: "Compact evidence keeps footer output short but does not remove full machine metadata."
  },
  {
    id: "full-aerospace-context",
    label: "Full Aerospace Context",
    description: "Prioritizes the combined operational context with weather, airport, and space context together.",
    includedMetadataKeys: ["aerospaceOperationalContext", "aerospaceContextAvailability", "aerospaceDataHealth"],
    preferredFooterSections: ["operational-context", "availability", "selected-target", "data-health", "airport-weather", "space-context", "focus-history"],
    caveat: "Full context footer lines remain summary-only and do not imply causation between sources."
  },
  {
    id: "airport-weather",
    label: "Airport / Weather",
    description: "Prioritizes airport-context weather and airport operational status for aircraft workflows.",
    includedMetadataKeys: ["aviationWeatherContext", "faaNasAirportStatus", "aerospaceOperationalContext"],
    preferredFooterSections: ["airport-weather", "selected-target", "data-health", "operational-context", "availability"],
    caveat: "Airport and weather context remain advisory/contextual and do not explain aircraft behavior."
  },
  {
    id: "space-context",
    label: "Space Context",
    description: "Prioritizes CNEOS, SWPC, and derived satellite context for aerospace review.",
    includedMetadataKeys: ["cneosSpaceContext", "swpcSpaceWeatherContext", "aerospaceOperationalContext"],
    preferredFooterSections: ["space-context", "selected-target", "data-health", "operational-context", "availability"],
    caveat: "Space context remains contextual/advisory and does not imply target-specific failure or impact."
  },
  {
    id: "source-health",
    label: "Source Health",
    description: "Prioritizes selected-target data health and context availability coverage.",
    includedMetadataKeys: ["aerospaceDataHealth", "aerospaceContextAvailability", "aerospaceOperationalContext"],
    preferredFooterSections: ["data-health", "availability", "selected-target", "operational-context"],
    caveat: "Source-health emphasis summarizes trust and coverage, not behavior or causation."
  },
  {
    id: "focus-history",
    label: "Focus / History",
    description: "Prioritizes focus state, focus history, and selected-target evidence for analyst workflows.",
    includedMetadataKeys: ["aerospaceFocus", "aerospaceFocusHistory", "selectedTargetSummary", "aerospaceDataHealth"],
    preferredFooterSections: ["focus-history", "selected-target", "data-health", "operational-context", "availability"],
    caveat: "Focus/history emphasis is an analysis aid only and does not prove operational relationships."
  }
];

export function buildAerospaceExportProfileSummary(input: {
  profileId?: AerospaceExportProfileId;
  selectedTargetLines?: string[];
  dataHealthLine?: string | null;
  nearbyContextLines?: string[];
  aviationWeatherLines?: string[];
  faaNasAirportStatusLines?: string[];
  openSkyContextLines?: string[];
  cneosSpaceContextLines?: string[];
  swpcSpaceWeatherLines?: string[];
  operationalContextLines?: string[];
  operationalAvailabilityLine?: string | null;
  focusLines?: string[];
  selectedDataHealthSummary?: AerospaceSourceHealthSummary | null;
  operationalContextSummary?: AerospaceOperationalContextSummary | null;
  availabilitySummary?: AerospaceContextAvailabilitySummary | null;
  focusHistorySummary?: AerospaceFocusHistorySummary | null;
}): AerospaceExportProfileSummary {
  const profile =
    AEROSPACE_EXPORT_PROFILES.find((item) => item.id === (input.profileId ?? "compact-evidence")) ??
    AEROSPACE_EXPORT_PROFILES[0];

  const sections: Record<string, string[]> = {
    "selected-target": (input.selectedTargetLines ?? []).slice(0, 4),
    "data-health": input.dataHealthLine ? [input.dataHealthLine] : [],
    "nearby-context": (input.nearbyContextLines ?? []).slice(0, 2),
    "airport-weather": [
      ...(input.aviationWeatherLines ?? []).slice(0, 2),
      ...(input.faaNasAirportStatusLines ?? []).slice(0, 2),
      ...(input.openSkyContextLines ?? []).slice(0, 1)
    ],
    "space-context": [
      ...(input.cneosSpaceContextLines ?? []).slice(0, 2),
      ...(input.swpcSpaceWeatherLines ?? []).slice(0, 2)
    ],
    "operational-context": (input.operationalContextLines ?? []).slice(0, 3),
    "availability": input.operationalAvailabilityLine ? [input.operationalAvailabilityLine] : [],
    "focus-history": (input.focusLines ?? []).slice(0, 3),
  };

  const ordered = profile.preferredFooterSections.flatMap((section) => sections[section] ?? []);
  const fallback = Object.entries(sections)
    .filter(([section]) => !profile.preferredFooterSections.includes(section))
    .flatMap(([, lines]) => lines);
  const footerLines = Array.from(
    new Set([`Export profile: ${profile.label}`, ...ordered, ...fallback])
  )
    .filter(Boolean)
    .slice(0, 6);

  return {
    profileId: profile.id,
    profileLabel: profile.label,
    includedSections: profile.preferredFooterSections.filter((section) => (sections[section] ?? []).length > 0),
    caveat: profile.caveat,
    footerLines,
    metadata: {
      profileId: profile.id,
      profileLabel: profile.label,
      includedSections: profile.preferredFooterSections,
      caveat: profile.caveat,
    }
  };
}
