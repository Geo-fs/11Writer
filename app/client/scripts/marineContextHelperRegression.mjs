import { buildMarineEvidenceSummary } from "../src/features/marine/marineEvidenceSummary.ts";
import { buildMarineChokepointReviewPackage } from "../src/features/marine/marineChokepointReviewPackage.ts";
import { getMarineEvidenceInterpretationCards } from "../src/features/marine/marineEvidenceInterpretation.ts";
import { buildMarineContextFusionSummary } from "../src/features/marine/marineContextFusionSummary.ts";
import { buildMarineContextIssueExportBundle } from "../src/features/marine/marineContextIssueExportBundle.ts";
import { buildMarineContextIssueQueue } from "../src/features/marine/marineContextIssueQueue.ts";
import { buildMarineContextReviewReport } from "../src/features/marine/marineContextReviewReport.ts";
import {
  buildMarineContextSnapshot,
  buildMarineContextTimelineSummary,
  reduceMarineContextSnapshots
} from "../src/features/marine/marineContextTimeline.ts";

function assert(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}

function buildDominatedSourceRegistrySummary() {
  const rows = [
    {
      sourceId: "noaa-coops-tides-currents",
      label: "NOAA CO-OPS",
      category: "oceanographic",
      sourceMode: "fixture",
      health: "loaded",
      availability: "loaded",
      nearbyCount: 2,
      activeCount: null,
      topSummary: "Galveston | mixed",
      caveats: ["Fixture/local mode should not be treated as live operational coastal coverage."],
      evidenceBasis: "observed"
    },
    {
      sourceId: "noaa-ndbc-realtime",
      label: "NOAA NDBC",
      category: "meteorological",
      sourceMode: "fixture",
      health: "empty",
      availability: "empty",
      nearbyCount: 0,
      activeCount: null,
      topSummary: null,
      caveats: ["No nearby buoy observations matched the current marine review radius."],
      evidenceBasis: "observed"
    },
    {
      sourceId: "scottish-water-overflows",
      label: "Scottish Water Overflows",
      category: "coastal-infrastructure",
      sourceMode: "fixture",
      health: "degraded",
      availability: "degraded",
      nearbyCount: 3,
      activeCount: 1,
      topSummary: "Portobello East Overflow | active",
      caveats: ["Partial metadata degrades source-health confidence for this fixture review path."],
      evidenceBasis: "contextual"
    },
    {
      sourceId: "france-vigicrues-hydrometry",
      label: "France Vigicrues Hydrometry",
      category: "hydrology",
      sourceMode: "fixture",
      health: "unavailable",
      availability: "unavailable",
      nearbyCount: 0,
      activeCount: null,
      topSummary: null,
      caveats: [
        "Vigicrues retrieval failed, so current hydrology context is unavailable and should not be treated as negative vessel evidence."
      ],
      evidenceBasis: "observed"
    },
    {
      sourceId: "ireland-opw-waterlevel",
      label: "Ireland OPW Water Level",
      category: "hydrology",
      sourceMode: "fixture",
      health: "degraded",
      availability: "degraded",
      nearbyCount: 2,
      activeCount: null,
      topSummary: "Ballyduff | 1.42 m | River Feale",
      caveats: ["Partial metadata degrades source-health confidence for this fixture review path."],
      evidenceBasis: "observed"
    },
    {
      sourceId: "netherlands-rws-waterinfo",
      label: "Netherlands RWS Waterinfo",
      category: "hydrology",
      sourceMode: "fixture",
      health: "degraded",
      availability: "degraded",
      nearbyCount: 2,
      activeCount: null,
      topSummary: "Hoek van Holland | Waterhoogte 126.0 centimeter",
      caveats: ["Source-provided station labels remain inert metadata and partial metadata degrades source health."],
      evidenceBasis: "observed"
    }
  ];

  return {
    rows,
    sourceCount: rows.length,
    availableSourceCount: 1,
    degradedSourceCount: 3,
    unavailableSourceCount: 1,
    fixtureSourceCount: 6,
    disabledSourceCount: 0,
    caveats: [
      "Marine context source registry summarizes availability only; it does not imply vessel behavior."
    ],
    exportLines: ["Marine context sources: 1/6 loaded | 3 degraded | 1 unavailable | 6 fixture"],
    metadata: {
      sourceCount: rows.length,
      availableSourceCount: 1,
      degradedSourceCount: 3,
      unavailableSourceCount: 1,
      fixtureSourceCount: 6,
      disabledSourceCount: 0,
      rows,
      caveats: [
        "Marine context source registry summarizes availability only; it does not imply vessel behavior."
      ]
    }
  };
}

function buildEnvironmentalContextSummary() {
  return {
    sourceCount: 2,
    healthySourceCount: 1,
    sourceModes: ["fixture", "fixture"],
    nearbyStationCount: 2,
    coopsStationCount: 2,
    ndbcStationCount: 0,
    topWaterLevelStation: {
      stationId: "coops-1",
      stationName: "Galveston",
      distanceKm: 8.2,
      valueM: 0.52,
      datum: "MLLW"
    },
    topCurrentStation: null,
    topBuoyStation: null,
    windSummary: null,
    waveSummary: null,
    pressureSummary: null,
    temperatureSummary: null,
    healthSummary: "1/2 enabled sources loaded; partial context",
    caveats: [
      "Environmental context available from selected marine sources; not used as proof of vessel intent."
    ],
    exportLines: [],
    environmentalCaveatSummary: {
      availability: "available",
      sourceHealthSummary: "1/2 enabled sources loaded; partial context; mixed source health",
      sourceModes: ["fixture", "fixture"],
      caveats: [
        "Environmental context available from selected marine sources; not used as proof of vessel intent."
      ]
    },
    metadata: {
      sourceCount: 2,
      healthySourceCount: 1,
      sourceModes: ["fixture", "fixture"],
      nearbyStationCount: 2,
      coopsStationCount: 2,
      ndbcStationCount: 0,
      contextKind: "chokepoint",
      presetId: "chokepoint-review",
      presetLabel: "Chokepoint review",
      isCustomPreset: false,
      presetCaveat:
        "Use for chokepoint review context; environmental observations remain contextual only.",
      anchor: "chokepoint",
      effectiveAnchor: "chokepoint",
      radiusKm: 400,
      radiusPreset: "medium",
      enabledSources: ["coops", "ndbc"],
      centerAvailable: true,
      fallbackReason: null,
      healthSummary: "1/2 enabled sources loaded; partial context",
      topWaterLevelStation: {
        stationId: "coops-1",
        stationName: "Galveston",
        distanceKm: 8.2,
        valueM: 0.52,
        datum: "MLLW"
      },
      topCurrentStation: null,
      topBuoyStation: null,
      topObservations: ["Water level: Galveston 0.52 m (MLLW)"],
      environmentalCaveatSummary: {
        availability: "available",
        sourceHealthSummary: "1/2 enabled sources loaded; partial context; mixed source health",
        sourceModes: ["fixture", "fixture"],
        caveats: [
          "Environmental context available from selected marine sources; not used as proof of vessel intent."
        ]
      },
      caveats: [
        "Environmental context available from selected marine sources; not used as proof of vessel intent."
      ]
    }
  };
}

function buildNoaaContextSummary() {
  return {
    sourceLine: "NOAA CO-OPS: loaded | fixture/local | 2 nearby stations",
    stationLines: [],
    exportLines: ["NOAA CO-OPS: loaded | fixture/local | 2 nearby stations"],
    metadata: {
      sourceId: "noaa-coops-tides-currents",
      sourceMode: "fixture",
      health: "loaded",
      nearbyStationCount: 2,
      contextKind: "chokepoint",
      topStation: {
        stationId: "coops-1",
        stationName: "Galveston",
        distanceKm: 8.2,
        stationType: "mixed"
      },
      caveats: [
        "Fixture/local mode should not be treated as live operational coastal coverage."
      ]
    }
  };
}

function buildNdbcContextSummary() {
  return {
    sourceLine: "NOAA NDBC: empty | fixture/local | 0 nearby stations",
    stationLines: [],
    exportLines: ["NOAA NDBC: empty | fixture/local | 0 nearby stations"],
    metadata: {
      sourceId: "noaa-ndbc-realtime",
      sourceMode: "fixture",
      health: "empty",
      nearbyStationCount: 0,
      contextKind: "chokepoint",
      topStation: null,
      topObservationSummary: null,
      caveats: ["No nearby buoy observations matched the current marine review radius."]
    }
  };
}

function buildHydrologyContextSummary() {
  return {
    sourceLine: "Marine hydrology context: 0/3 loaded | partial context",
    reviewLines: [],
    exportLines: [],
    metadata: {
      sourceCount: 3,
      loadedSourceCount: 0,
      emptySourceCount: 0,
      degradedSourceCount: 2,
      disabledSourceCount: 0,
      fixtureSourceCount: 3,
      nearbyStationCount: 4,
      healthSummary: "0/3 hydrology sources loaded; partial context",
      vigicrues: {
        sourceMode: "fixture",
        health: "unavailable",
        nearbyStationCount: 0,
        parameterFilter: "all",
        topStationName: null,
        topObservationObservedAt: null,
        hasPartialMetadata: false
      },
      irelandOpw: {
        sourceMode: "fixture",
        health: "degraded",
        nearbyStationCount: 2,
        topStationName: "Ballyduff",
        topReadingAt: "2026-04-04T11:42:00Z",
        hasPartialMetadata: true
      },
      waterinfo: {
        sourceMode: "fixture",
        health: "degraded",
        nearbyStationCount: 2,
        topStationName: "Hoek van Holland",
        topObservationObservedAt: "2026-04-04T11:41:00Z",
        hasPartialMetadata: true
      },
      caveats: ["Hydrology context is partial and should not be treated as flood-impact confirmation."]
    }
  };
}

function buildWaterinfoContextSummary() {
  return {
    sourceLine: "Netherlands RWS Waterinfo: degraded | fixture/local | 2 nearby stations",
    stationLines: [],
    exportLines: ["Netherlands RWS Waterinfo: degraded | fixture/local | 2 nearby stations"],
    metadata: {
      sourceId: "netherlands-rws-waterinfo",
      sourceMode: "fixture",
      health: "degraded",
      nearbyStationCount: 2,
      topStation: {
        stationId: "HOEKVHLD",
        stationName: "Hoek van Holland",
        distanceKm: 0.9,
        waterBody: "Nieuwe Waterweg",
        parameterCode: "WATHTE",
        parameterLabel: "Waterhoogte"
      },
      topObservationSummary: "Waterhoogte 126.0 centimeter | 2026-04-04T11:41:00Z | Nieuwe Waterweg",
      topObservationObservedAt: "2026-04-04T11:41:00Z",
      hasPartialMetadata: true,
      caveats: [
        "Source-provided station labels remain inert metadata and partial metadata degrades source health."
      ]
    }
  };
}

function buildScottishWaterContextSummary() {
  return {
    sourceLine: "Scottish Water Overflows: degraded | fixture/local | 3 nearby monitors | 1 active",
    eventLines: [],
    exportLines: [],
    metadata: {
      sourceId: "scottish-water-overflows",
      sourceMode: "fixture",
      health: "degraded",
      nearbyMonitorCount: 3,
      activeMonitorCount: 1,
      topMonitor: {
        eventId: "sw-1",
        siteName: "Portobello East Overflow",
        status: "active",
        distanceKm: 0.6
      },
      caveats: [
        "Overflow monitor activation is source-reported infrastructure context only and does not confirm pollution impact or vessel behavior."
      ]
    }
  };
}

function buildBroadAllSourcesSourceRegistrySummary() {
  const rows = [
    {
      sourceId: "noaa-coops-tides-currents",
      label: "NOAA CO-OPS",
      category: "oceanographic",
      sourceMode: "fixture",
      health: "loaded",
      availability: "loaded",
      nearbyCount: 3,
      activeCount: null,
      topSummary: "Galveston | mixed",
      caveats: ["Fixture/local mode should not be treated as live operational coastal coverage."],
      evidenceBasis: "observed"
    },
    {
      sourceId: "noaa-ndbc-realtime",
      label: "NOAA NDBC",
      category: "meteorological",
      sourceMode: "fixture",
      health: "loaded",
      availability: "loaded",
      nearbyCount: 2,
      activeCount: null,
      topSummary: "42035 | 1.9 m seas",
      caveats: ["Fixture/local mode should not be treated as live operational buoy coverage."],
      evidenceBasis: "observed"
    },
    {
      sourceId: "scottish-water-overflows",
      label: "Scottish Water Overflows",
      category: "coastal-infrastructure",
      sourceMode: "fixture",
      health: "loaded",
      availability: "loaded",
      nearbyCount: 2,
      activeCount: 0,
      topSummary: "Leith Sands Overflow | inactive",
      caveats: ["Overflow monitor activation is contextual infrastructure status only."],
      evidenceBasis: "contextual"
    },
    {
      sourceId: "france-vigicrues-hydrometry",
      label: "France Vigicrues Hydrometry",
      category: "hydrology",
      sourceMode: "fixture",
      health: "loaded",
      availability: "loaded",
      nearbyCount: 2,
      activeCount: null,
      topSummary: "Arles | 3.10 m water height",
      caveats: ["Hydrology context is station-local and not flood-impact confirmation."],
      evidenceBasis: "observed"
    },
    {
      sourceId: "ireland-opw-waterlevel",
      label: "Ireland OPW Water Level",
      category: "hydrology",
      sourceMode: "fixture",
      health: "loaded",
      availability: "loaded",
      nearbyCount: 1,
      activeCount: null,
      topSummary: "Ballyduff | 1.12 m | River Feale",
      caveats: ["OPW readings are contextual hydrometric data only."],
      evidenceBasis: "observed"
    },
    {
      sourceId: "netherlands-rws-waterinfo",
      label: "Netherlands RWS Waterinfo",
      category: "hydrology",
      sourceMode: "fixture",
      health: "loaded",
      availability: "loaded",
      nearbyCount: 2,
      activeCount: null,
      topSummary: "Hoek van Holland | Waterhoogte 124.0 centimeter",
      caveats: ["Waterinfo water-level observations are contextual hydrology data only."],
      evidenceBasis: "observed"
    }
  ];

  return {
    rows,
    sourceCount: rows.length,
    availableSourceCount: 6,
    degradedSourceCount: 0,
    unavailableSourceCount: 0,
    fixtureSourceCount: 6,
    disabledSourceCount: 0,
    caveats: [
      "Marine context source registry summarizes availability only; it does not imply vessel behavior."
    ],
    exportLines: ["Marine context sources: 6/6 loaded | 0 degraded | 0 unavailable | 6 fixture"],
    metadata: {
      sourceCount: rows.length,
      availableSourceCount: 6,
      degradedSourceCount: 0,
      unavailableSourceCount: 0,
      fixtureSourceCount: 6,
      disabledSourceCount: 0,
      rows,
      caveats: [
        "Marine context source registry summarizes availability only; it does not imply vessel behavior."
      ]
    }
  };
}

function buildBroadAllSourcesEnvironmentalContextSummary() {
  return {
    sourceCount: 2,
    healthySourceCount: 2,
    sourceModes: ["fixture", "fixture"],
    nearbyStationCount: 5,
    coopsStationCount: 3,
    ndbcStationCount: 2,
    topWaterLevelStation: {
      stationId: "coops-2",
      stationName: "Galveston Pier 21",
      distanceKm: 5.2,
      valueM: 0.61,
      datum: "MLLW"
    },
    topCurrentStation: {
      stationId: "coops-current-1",
      stationName: "Bolivar Roads",
      distanceKm: 7.4,
      speedKts: 1.8,
      directionCardinal: "NE"
    },
    topBuoyStation: {
      stationId: "ndbc-42035",
      stationName: "NDBC 42035",
      distanceKm: 46.3,
      stationType: "buoy",
      observationSummary: "Wind 14 kts | seas 1.9 m"
    },
    windSummary: "Wind 14 kts from SSE at nearest buoy.",
    waveSummary: "Seas 1.9 m at nearest buoy.",
    pressureSummary: "1014 hPa at nearest buoy.",
    temperatureSummary: "Water 23 C at nearest buoy.",
    healthSummary: "2/2 enabled sources loaded; broad marine context available",
    caveats: [
      "Environmental context available from selected marine sources; not used as proof of vessel intent."
    ],
    exportLines: [],
    environmentalCaveatSummary: {
      availability: "available",
      sourceHealthSummary: "2/2 enabled sources loaded; broad marine context available",
      sourceModes: ["fixture", "fixture"],
      caveats: [
        "Environmental context available from selected marine sources; not used as proof of vessel intent."
      ]
    },
    metadata: {
      sourceCount: 2,
      healthySourceCount: 2,
      sourceModes: ["fixture", "fixture"],
      nearbyStationCount: 5,
      coopsStationCount: 3,
      ndbcStationCount: 2,
      contextKind: "viewport",
      presetId: "regional-marine-context",
      presetLabel: "Regional marine context",
      isCustomPreset: false,
      presetCaveat:
        "Use for broader environmental context review; observations remain contextual only.",
      anchor: "viewport",
      effectiveAnchor: "viewport",
      radiusKm: 900,
      radiusPreset: "large",
      enabledSources: ["coops", "ndbc"],
      centerAvailable: true,
      fallbackReason: null,
      healthSummary: "2/2 enabled sources loaded; broad marine context available",
      topWaterLevelStation: {
        stationId: "coops-2",
        stationName: "Galveston Pier 21",
        distanceKm: 5.2,
        valueM: 0.61,
        datum: "MLLW"
      },
      topCurrentStation: {
        stationId: "coops-current-1",
        stationName: "Bolivar Roads",
        distanceKm: 7.4,
        speedKts: 1.8,
        directionCardinal: "NE"
      },
      topBuoyStation: {
        stationId: "ndbc-42035",
        stationName: "NDBC 42035",
        distanceKm: 46.3,
        stationType: "buoy",
        observationSummary: "Wind 14 kts | seas 1.9 m"
      },
      topObservations: [
        "Water level: Galveston Pier 21 0.61 m (MLLW)",
        "Current: Bolivar Roads 1.8 kts NE",
        "Buoy: NDBC 42035 Wind 14 kts | seas 1.9 m"
      ],
      environmentalCaveatSummary: {
        availability: "available",
        sourceHealthSummary: "2/2 enabled sources loaded; broad marine context available",
        sourceModes: ["fixture", "fixture"],
        caveats: [
          "Environmental context available from selected marine sources; not used as proof of vessel intent."
        ]
      },
      caveats: [
        "Environmental context available from selected marine sources; not used as proof of vessel intent."
      ]
    }
  };
}

function buildToggleLimitedSourceRegistrySummary() {
  const rows = [
    {
      sourceId: "noaa-coops-tides-currents",
      label: "NOAA CO-OPS",
      category: "oceanographic",
      sourceMode: "fixture",
      health: "disabled",
      availability: "disabled",
      nearbyCount: 0,
      activeCount: null,
      topSummary: null,
      caveats: ["CO-OPS is disabled by the current marine preset/source-toggle state."],
      evidenceBasis: "observed"
    },
    {
      sourceId: "noaa-ndbc-realtime",
      label: "NOAA NDBC",
      category: "meteorological",
      sourceMode: "fixture",
      health: "loaded",
      availability: "loaded",
      nearbyCount: 1,
      activeCount: null,
      topSummary: "42019 | Wind 18 kts | seas 2.4 m",
      caveats: ["Fixture/local mode should not be treated as live operational buoy coverage."],
      evidenceBasis: "observed"
    },
    {
      sourceId: "scottish-water-overflows",
      label: "Scottish Water Overflows",
      category: "coastal-infrastructure",
      sourceMode: "fixture",
      health: "degraded",
      availability: "degraded",
      nearbyCount: 3,
      activeCount: 1,
      topSummary: "Portobello East Overflow | active",
      caveats: ["Partial metadata degrades source-health confidence for this fixture review path."],
      evidenceBasis: "contextual"
    },
    {
      sourceId: "france-vigicrues-hydrometry",
      label: "France Vigicrues Hydrometry",
      category: "hydrology",
      sourceMode: "fixture",
      health: "unavailable",
      availability: "unavailable",
      nearbyCount: 0,
      activeCount: null,
      topSummary: null,
      caveats: [
        "Vigicrues retrieval failed, so current hydrology context is unavailable and should not be treated as negative vessel evidence."
      ],
      evidenceBasis: "observed"
    },
    {
      sourceId: "ireland-opw-waterlevel",
      label: "Ireland OPW Water Level",
      category: "hydrology",
      sourceMode: "fixture",
      health: "loaded",
      availability: "loaded",
      nearbyCount: 1,
      activeCount: null,
      topSummary: "Ballyduff | 1.18 m | River Feale",
      caveats: ["OPW readings are contextual hydrometric data only."],
      evidenceBasis: "observed"
    },
    {
      sourceId: "netherlands-rws-waterinfo",
      label: "Netherlands RWS Waterinfo",
      category: "hydrology",
      sourceMode: "fixture",
      health: "degraded",
      availability: "degraded",
      nearbyCount: 1,
      activeCount: null,
      topSummary: "Hoek van Holland | Waterhoogte 122.0 centimeter",
      caveats: ["Waterinfo is partial context only in this limited source mix."],
      evidenceBasis: "observed"
    }
  ];

  return {
    rows,
    sourceCount: rows.length,
    availableSourceCount: 2,
    degradedSourceCount: 2,
    unavailableSourceCount: 1,
    fixtureSourceCount: 6,
    disabledSourceCount: 1,
    caveats: [
      "Marine context source registry summarizes availability only; it does not imply vessel behavior."
    ],
    exportLines: ["Marine context sources: 2/6 loaded | 2 degraded | 1 unavailable | 1 disabled | 6 fixture"],
    metadata: {
      sourceCount: rows.length,
      availableSourceCount: 2,
      degradedSourceCount: 2,
      unavailableSourceCount: 1,
      fixtureSourceCount: 6,
      disabledSourceCount: 1,
      rows,
      caveats: [
        "Marine context source registry summarizes availability only; it does not imply vessel behavior."
      ]
    }
  };
}

function buildToggleLimitedEnvironmentalContextSummary() {
  return {
    sourceCount: 1,
    healthySourceCount: 1,
    sourceModes: ["fixture"],
    nearbyStationCount: 1,
    coopsStationCount: 0,
    ndbcStationCount: 1,
    topWaterLevelStation: null,
    topCurrentStation: null,
    topBuoyStation: {
      stationId: "ndbc-42019",
      stationName: "NDBC 42019",
      distanceKm: 35.1,
      stationType: "buoy",
      observationSummary: "Wind 18 kts | seas 2.4 m"
    },
    windSummary: "Wind 18 kts from ESE at nearest buoy.",
    waveSummary: "Seas 2.4 m at nearest buoy.",
    pressureSummary: "1011 hPa at nearest buoy.",
    temperatureSummary: "Water 22 C at nearest buoy.",
    healthSummary: "1/1 enabled sources loaded; CO-OPS disabled by current preset",
    caveats: [
      "Environmental context available from selected marine sources; not used as proof of vessel intent.",
      "CO-OPS is disabled by the current marine preset/source-toggle state."
    ],
    exportLines: [],
    environmentalCaveatSummary: {
      availability: "available",
      sourceHealthSummary: "1/1 enabled sources loaded; CO-OPS disabled by current preset",
      sourceModes: ["fixture"],
      caveats: [
        "Environmental context available from selected marine sources; not used as proof of vessel intent.",
        "CO-OPS is disabled by the current marine preset/source-toggle state."
      ]
    },
    metadata: {
      sourceCount: 1,
      healthySourceCount: 1,
      sourceModes: ["fixture"],
      nearbyStationCount: 1,
      coopsStationCount: 0,
      ndbcStationCount: 1,
      contextKind: "viewport",
      presetId: "buoy-weather-focus",
      presetLabel: "Buoy weather focus",
      isCustomPreset: false,
      presetCaveat:
        "Use for buoy/weather-focused review; disabled sources remain source-setting choices, not missing evidence.",
      anchor: "viewport",
      effectiveAnchor: "viewport",
      radiusKm: 400,
      radiusPreset: "medium",
      enabledSources: ["ndbc"],
      centerAvailable: true,
      fallbackReason: null,
      healthSummary: "1/1 enabled sources loaded; CO-OPS disabled by current preset",
      topWaterLevelStation: null,
      topCurrentStation: null,
      topBuoyStation: {
        stationId: "ndbc-42019",
        stationName: "NDBC 42019",
        distanceKm: 35.1,
        stationType: "buoy",
        observationSummary: "Wind 18 kts | seas 2.4 m"
      },
      topObservations: ["Buoy: NDBC 42019 Wind 18 kts | seas 2.4 m"],
      environmentalCaveatSummary: {
        availability: "available",
        sourceHealthSummary: "1/1 enabled sources loaded; CO-OPS disabled by current preset",
        sourceModes: ["fixture"],
        caveats: [
          "Environmental context available from selected marine sources; not used as proof of vessel intent.",
          "CO-OPS is disabled by the current marine preset/source-toggle state."
        ]
      },
      caveats: [
        "Environmental context available from selected marine sources; not used as proof of vessel intent.",
        "CO-OPS is disabled by the current marine preset/source-toggle state."
      ]
    }
  };
}

function runRegression() {
  const noaaContextSummary = buildNoaaContextSummary();
  const ndbcContextSummary = buildNdbcContextSummary();
  const environmentalContextSummary = buildEnvironmentalContextSummary();
  const hydrologyContextSummary = buildHydrologyContextSummary();
  const waterinfoContextSummary = buildWaterinfoContextSummary();
  const scottishWaterContextSummary = buildScottishWaterContextSummary();
  const sourceRegistrySummary = buildDominatedSourceRegistrySummary();
  const issueQueueSummary = buildMarineContextIssueQueue(sourceRegistrySummary);
  const fusionSummary = buildMarineContextFusionSummary({
    environmentalContextSummary,
    hydrologyContextSummary,
    scottishWaterContextSummary,
    contextSourceRegistrySummary: sourceRegistrySummary,
    contextIssueQueueSummary: issueQueueSummary
  });

  assert(fusionSummary, "Fusion summary should be created for dominated source mix.");
  assert(
    fusionSummary.metadata.dominatedByLimitedSources === true,
    "Fusion summary should flag dominated limited sources."
  );
  assert(
    /partial context/i.test(fusionSummary.overallAvailabilityLine),
    "Fusion summary should use partial-context wording."
  );
  assert(
    /source-health limitations dominate current source mix/i.test(fusionSummary.exportReadinessLine),
    "Fusion export readiness should call out dominant source-health limitation wording."
  );
  assert(
    /not anomaly severity or impact proof/i.test(fusionSummary.dominantLimitationLine ?? ""),
    "Fusion dominant limitation should preserve no-severity/no-impact wording."
  );

  const reviewReport = buildMarineContextReviewReport({
    fusionSummary,
    issueQueueSummary
  });

  assert(reviewReport, "Review report should be created for dominated source mix.");
  assert(/partial context/i.test(reviewReport.summaryLine), "Review report should use partial-context wording.");
  assert(/review caveat/i.test(reviewReport.sourceHealthSummary), "Review report should surface review-caveat wording.");
  assert(
    reviewReport.reviewNeededItems.some((item) => /partial context only/i.test(item)),
    "Review report should include partial-context-only review guidance."
  );
  assert(
    reviewReport.doesNotProveLines.some((line) => /vessel intent/i.test(line)),
    "Review report should preserve vessel-intent guardrails."
  );
  assert(
    reviewReport.doesNotProveLines.some((line) => /wrongdoing/i.test(line)),
    "Review report should preserve wrongdoing guardrails."
  );

  const issueExportBundle = buildMarineContextIssueExportBundle({
    sourceRegistrySummary,
    issueQueueSummary
  });

  assert(issueExportBundle, "Issue export bundle should be created for marine source summaries.");
  assert(/partial context/i.test(issueExportBundle.summaryLine), "Issue export bundle should use partial-context summary wording.");
  assert(
    /not anomaly severity, impact, or vessel-intent evidence/i.test(issueExportBundle.dominantLimitationLine ?? ""),
    "Issue export bundle should preserve no-severity/no-impact/no-intent wording."
  );
  assert(issueExportBundle.rows.length === 6, "Issue export bundle should preserve all six source rows.");

  const scottishWaterRow = issueExportBundle.rows.find((row) => row.sourceId === "scottish-water-overflows");
  assert(scottishWaterRow, "Issue export bundle should include Scottish Water row.");
  assert(
    scottishWaterRow.category === "coastal-infrastructure" &&
      scottishWaterRow.evidenceBasis === "contextual",
    "Scottish Water row should preserve infrastructure/contextual semantics."
  );
  assert(
    /review source health and caveats/i.test(scottishWaterRow.allowedReviewAction),
    "Scottish Water row should preserve allowed review action wording."
  );
  assert(
    /pollution impact, health risk, vessel behavior, or wrongdoing/i.test(scottishWaterRow.doesNotProveLine),
    "Scottish Water row should preserve no-impact/no-wrongdoing guardrails."
  );

  const vigicruesRow = issueExportBundle.rows.find((row) => row.sourceId === "france-vigicrues-hydrometry");
  assert(vigicruesRow, "Issue export bundle should include Vigicrues row.");
  assert(vigicruesRow.health === "unavailable", "Vigicrues row should preserve unavailable health state.");
  assert(
    /verify source settings or query center/i.test(vigicruesRow.allowedReviewAction),
    "Vigicrues row should preserve missing-context review wording."
  );
  assert(
    /flooding, contamination, damage, vessel behavior, or anomaly cause/i.test(vigicruesRow.doesNotProveLine),
    "Vigicrues row should preserve hydrology guardrails."
  );

  const focusedEvidenceInterpretation = {
    priorityExplanation: "Summary-level source-health review context",
    trustLevel: "limited",
    gapContext: "long",
    movementContext: "notable",
    sourceHealthContext: "degraded/stale",
    sparseReportingContext: "plausible",
    confidenceContext: "medium",
    environmentalContextAvailability:
      environmentalContextSummary.environmentalCaveatSummary.availability,
    environmentalContextSourceHealthSummary:
      environmentalContextSummary.environmentalCaveatSummary.sourceHealthSummary,
    cards: [
      {
        kind: "confidence",
        label: "Why this was prioritized",
        value: "Chokepoint slice priority",
        detail: "Observed and inferred AIS/signal gap review signals justify analyst review.",
        basis: "scored",
        severity: "important"
      },
      {
        kind: "gap-duration",
        label: "Gap duration",
        value: "long",
        detail: "2h 30m between observed points.",
        basis: "observed",
        severity: "important"
      },
      {
        kind: "movement-across-gap",
        label: "Movement across gap",
        value: "notable",
        detail: "62.0 km moved between observations.",
        basis: "observed",
        severity: "important"
      },
      {
        kind: "source-health",
        label: "Source health",
        value: "degraded/stale",
        detail: "Source state: stale.",
        basis: "summary",
        severity: "important",
        caveat: "Source health can reduce confidence in interval interpretation."
      },
      {
        kind: "sparse-reporting",
        label: "Sparse reporting plausibility",
        value: "plausible",
        detail: "Model indicates sparse reporting may explain part of the gap.",
        basis: "inferred",
        severity: "notice"
      },
      {
        kind: "summary-only",
        label: "Evidence limits",
        value: "summary-level signal",
        detail: "No direct replay event attached.",
        basis: "summary",
        severity: "notice",
        caveat: "Interpretation is based on aggregate anomaly summary."
      },
      {
        kind: "evidence-limits",
        label: "Trust/caveat",
        value: "limited summary context",
        detail:
          "Prioritization supports analyst review. It is not proof of intent, wrongdoing, or intentional AIS disabling.",
        basis: "summary",
        severity: "notice",
        caveat:
          "AIS/signal gaps, reroutes, queue/backlog wording, and contextual source-health limits do not prove evasion, escort, toll activity, blockade, targeting, threat, intent, wrongdoing, or causation."
      },
      {
        kind: "evidence-limits",
        label: "Environmental context",
        value: "available",
        detail: environmentalContextSummary.environmentalCaveatSummary.sourceHealthSummary,
        basis: "summary",
        severity: "neutral",
        caveat:
          environmentalContextSummary.environmentalCaveatSummary.caveats[0]
      }
    ],
    caveats: [
      "Environmental context available from selected marine sources; not used as proof of vessel intent.",
      "Interpretation is based on aggregate anomaly summary.",
      "AIS/signal gaps, reroutes, queue/backlog wording, and contextual source-health limits do not prove evasion, escort, toll activity, blockade, targeting, threat, intent, wrongdoing, or causation."
    ]
  };
  function buildInterpretationForEnvironmentalContext(summary) {
    return {
      ...focusedEvidenceInterpretation,
      environmentalContextAvailability: summary.environmentalCaveatSummary.availability,
      environmentalContextSourceHealthSummary:
        summary.environmentalCaveatSummary.sourceHealthSummary,
      cards: focusedEvidenceInterpretation.cards.map((card) =>
        card.kind === "evidence-limits" && card.label === "Environmental context"
          ? {
              ...card,
              value: summary.environmentalCaveatSummary.availability,
              detail: summary.environmentalCaveatSummary.sourceHealthSummary,
              caveat: summary.environmentalCaveatSummary.caveats[0]
            }
          : card
      ),
      caveats: Array.from(
        new Set([
          ...focusedEvidenceInterpretation.caveats.filter(
            (line) => !/selected marine sources|CO-OPS is disabled/i.test(line)
          ),
          ...summary.environmentalCaveatSummary.caveats
        ])
      )
    };
  }
  const focusedEvidenceRows = [
    {
      id: "focused-summary-row",
      kind: "summary-only",
      label: "AIS/signal gap review",
      detail: "Summary-level AIS/signal gap wording remains review-only in the current chokepoint lens.",
      observedOrInferred: "summary",
      timestamp: null,
      timeWindowStart: "2026-04-04T11:30:00Z",
      timeWindowEnd: "2026-04-04T12:00:00Z",
      isFocused: true,
      caveat: "Interpretation is based on aggregate anomaly summary."
    },
    {
      id: "focused-reroute-row",
      kind: "summary-signal",
      label: "Reroute review wording",
      detail: "Reroute and queue/backlog wording is bounded review context only.",
      source: "summary-window",
      observedOrInferred: "summary",
      timeWindowStart: "2026-04-04T11:30:00Z",
      timeWindowEnd: "2026-04-04T12:00:00Z",
      caveat: "Route-change wording does not prove evasion or escort.",
      isFocused: false
    },
    {
      id: "focused-queue-row",
      kind: "summary-signal",
      label: "Queue/backlog review wording",
      detail: "Queue/backlog conditions remain operational review context, not targeting or threat evidence.",
      source: "summary-window",
      observedOrInferred: "summary",
      timeWindowStart: "2026-04-04T11:30:00Z",
      timeWindowEnd: "2026-04-04T12:00:00Z",
      caveat: "Queue/backlog wording does not prove toll, blockade, or wrongdoing.",
      isFocused: false
    }
  ];
  const activeNavigationTarget = {
    kind: "chokepoint-slice",
    label: "Galveston chokepoint review window",
    timeWindowStart: "2026-04-04T11:30:00Z",
    timeWindowEnd: "2026-04-04T12:00:00Z",
    timestamp: undefined,
    caveat: "Summary-level focus only; no direct replay event attached.",
    directReplayTarget: false,
    unavailableReason: "No direct replay event attached."
  };
  const selectedVesselSummary = {
    anomaly: {
      score: 81,
      level: "high",
      displayLabel: "Selected vessel attention priority",
      reasons: ["Observed and inferred signals justify review."],
      caveats: ["Ranking prioritizes review; it does not prove intent."],
      observedSignals: ["gap-start"],
      inferredSignals: ["possible-dark-interval"],
      scoredSignals: ["attention-priority"]
    }
  };
  const viewportSummary = {
    anomaly: {
      score: 67,
      level: "medium",
      displayLabel: "Viewport notable activity",
      reasons: ["Viewport source-health caveats warrant context review."],
      caveats: ["Viewport prioritization remains review-only."],
      observedSignals: ["observed-gap-density"],
      inferredSignals: ["viewport-summary"],
      scoredSignals: ["attention-priority"]
    }
  };
  const visibleSlices = [
    {
      sliceStartAt: "2026-04-04T11:30:00Z",
      sliceEndAt: "2026-04-04T12:00:00Z",
      anomaly: {
        score: 72,
        level: "high",
        displayLabel: "Chokepoint slice priority",
        priorityRank: 1,
        reasons: ["Chokepoint review window includes limited-context source mix."],
        caveats: ["Chokepoint slice ranking remains attention prioritization only."],
        observedSignals: ["slice-gap-observed"],
        inferredSignals: ["slice-summary"],
        scoredSignals: ["attention-priority"]
      }
    }
  ];
  const chokepointReviewContext = {
    corridorLabel: "Hormuz-style bounded corridor review",
    boundedAreaLabel: "Northern chokepoint review box",
    crossingCount: 14
  };
  const chokepointSummary = {
    fetchedAt: "2026-04-04T12:05:00Z",
    startAt: "2026-04-04T11:30:00Z",
    endAt: "2026-04-04T12:00:00Z",
    sliceMinutes: 30,
    sliceCount: 1,
    totalVesselObservations: 14,
    totalObservedGapEvents: 3,
    totalSuspiciousGapEvents: 2,
    anomaly: visibleSlices[0].anomaly,
    slices: visibleSlices,
    observedFields: ["totalVesselObservations", "totalObservedGapEvents"],
    inferredFields: ["totalSuspiciousGapEvents"]
  };

  const chokepointReviewPackage = buildMarineChokepointReviewPackage({
    chokepointReviewContext,
    chokepointSummary,
    activeNavigationTarget,
    focusedEvidenceRows,
    focusedEvidenceInterpretation,
    contextSourceRegistrySummary: sourceRegistrySummary,
    contextIssueQueueSummary: issueQueueSummary,
    contextIssueExportBundle: issueExportBundle,
    contextFusionSummary: fusionSummary,
    contextReviewReportSummary: reviewReport,
    hydrologyContextSummary,
    environmentalContextSummary
  });

  assert(chokepointReviewPackage, "Chokepoint review package should be created for deterministic review inputs.");
  assert(chokepointReviewPackage.reviewOnly === true, "Chokepoint review package should stay review-only.");
  assert(
    chokepointReviewPackage.metadata.corridorLabel === "Hormuz-style bounded corridor review",
    "Chokepoint review package should preserve the bounded corridor label."
  );
  assert(
    chokepointReviewPackage.metadata.crossingCount === 14,
    "Chokepoint review package should preserve deterministic crossing counts."
  );
  assert(
    chokepointReviewPackage.metadata.reviewSignals.some((line) => /AIS\/signal gap review/i.test(line)),
    "Chokepoint review package should preserve AIS/signal-gap review wording."
  );
  assert(
    chokepointReviewPackage.metadata.reviewSignals.some((line) => /reroute/i.test(line)),
    "Chokepoint review package should preserve reroute review wording."
  );
  assert(
    chokepointReviewPackage.metadata.reviewSignals.some((line) => /queue\/backlog/i.test(line)),
    "Chokepoint review package should preserve queue/backlog review wording."
  );
  assert(
    chokepointReviewPackage.metadata.doesNotProve.some((line) => /evasion, escort, toll activity, blockade, targeting, threat, intent, wrongdoing, or causation/i.test(line)),
    "Chokepoint review package should preserve no-evasion/no-threat/no-causation guardrails."
  );
  assert(
    chokepointReviewPackage.metadata.evidenceBasis.includes("summary") &&
      chokepointReviewPackage.metadata.evidenceBasis.includes("contextual"),
    "Chokepoint review package should preserve summary and contextual evidence-basis distinctions."
  );

  const currentContextSnapshot = buildMarineContextSnapshot({
    environmentalContextSummary,
    contextSourceRegistrySummary: sourceRegistrySummary,
    focusedTarget: activeNavigationTarget,
    chokepointReviewPackage,
    createdAt: "2026-04-04T12:05:00Z"
  });
  assert(currentContextSnapshot, "Context timeline snapshot should be created for deterministic review inputs.");
  assert(
    currentContextSnapshot.reviewOnly === true,
    "Context timeline snapshot should preserve review-only posture."
  );
  assert(
    currentContextSnapshot.corridorLabel === chokepointReviewPackage.metadata.corridorLabel,
    "Context timeline snapshot should preserve corridor label coherence."
  );
  assert(
    currentContextSnapshot.contextGapCount === chokepointReviewPackage.metadata.contextGapCount,
    "Context timeline snapshot should preserve context-gap coherence."
  );
  assert(
    JSON.stringify(currentContextSnapshot.focusedEvidenceKinds) ===
      JSON.stringify(chokepointReviewPackage.metadata.focusedEvidenceKinds),
    "Context timeline snapshot should preserve focused-evidence kinds."
  );
  assert(
    currentContextSnapshot.sourceHealthLine === chokepointReviewPackage.metadata.sourceHealthLine,
    "Context timeline snapshot should preserve source-health line coherence."
  );
  assert(
    currentContextSnapshot.dominantLimitationLine ===
      chokepointReviewPackage.metadata.dominantLimitationLine,
    "Context timeline snapshot should preserve dominant-limitation coherence."
  );
  assert(
    currentContextSnapshot.topSummaryLines.some((line) =>
      currentContextSnapshot.focusedTargetLabel
        ? line === currentContextSnapshot.focusedTargetLabel
        : chokepointReviewPackage.metadata.reviewSignals.includes(line)
    ),
    "Context timeline snapshot should retain chokepoint review-lens summary text."
  );

  const previousContextSnapshot = buildMarineContextSnapshot({
    environmentalContextSummary,
    contextSourceRegistrySummary: sourceRegistrySummary,
    focusedTarget: {
      ...activeNavigationTarget,
      label: "Previous chokepoint review window",
      timeWindowStart: "2026-04-04T10:30:00Z",
      timeWindowEnd: "2026-04-04T11:00:00Z"
    },
    chokepointReviewPackage: {
      ...chokepointReviewPackage,
      metadata: {
        ...chokepointReviewPackage.metadata,
        focusedTargetLabel: "Previous chokepoint review window",
        timeWindowStart: "2026-04-04T10:30:00Z",
        timeWindowEnd: "2026-04-04T11:00:00Z"
      }
    },
    createdAt: "2026-04-04T11:05:00Z"
  });
  assert(previousContextSnapshot, "Previous context timeline snapshot should be created for history regression.");
  const timelineSnapshots = reduceMarineContextSnapshots(
    reduceMarineContextSnapshots([], previousContextSnapshot),
    currentContextSnapshot
  );
  const contextTimelineSummary = buildMarineContextTimelineSummary(timelineSnapshots);
  assert(
    contextTimelineSummary.snapshotCount === 2,
    "Context timeline summary should preserve two deterministic snapshots."
  );
  assert(
    contextTimelineSummary.currentSnapshot?.corridorLabel ===
      chokepointReviewPackage.metadata.corridorLabel,
    "Context timeline current snapshot should align with chokepoint corridor label."
  );
  assert(
    contextTimelineSummary.currentSnapshot?.sourceHealthLine ===
      chokepointReviewPackage.metadata.sourceHealthLine,
    "Context timeline current snapshot should align with chokepoint source-health line."
  );
  assert(
    contextTimelineSummary.currentSnapshot?.focusedTargetLabel ===
      chokepointReviewPackage.metadata.focusedTargetLabel,
    "Context timeline current snapshot should align with chokepoint focused target label."
  );
  assert(
    contextTimelineSummary.previousSnapshot?.focusedTargetLabel ===
      "Previous chokepoint review window",
    "Context timeline previous snapshot should preserve prior review-lens label."
  );
  assert(
    contextTimelineSummary.caveats.some((line) => /do not imply vessel behavior or anomaly cause/i.test(line)),
    "Context timeline summary should preserve no-behavior/no-cause guardrails."
  );

  const expectedInterpretationCardsByMode = {
    compact: getMarineEvidenceInterpretationCards(focusedEvidenceInterpretation, "compact"),
    detailed: getMarineEvidenceInterpretationCards(focusedEvidenceInterpretation, "detailed"),
    "evidence-only": getMarineEvidenceInterpretationCards(
      focusedEvidenceInterpretation,
      "evidence-only"
    ),
    "caveats-first": getMarineEvidenceInterpretationCards(
      focusedEvidenceInterpretation,
      "caveats-first"
    )
  };

  assert(
    expectedInterpretationCardsByMode.compact.length === 3,
    "Compact interpretation mode should limit visible cards to three."
  );
  assert(
    expectedInterpretationCardsByMode.detailed.length === focusedEvidenceInterpretation.cards.length,
    "Detailed interpretation mode should preserve all interpretation cards."
  );
  assert(
    expectedInterpretationCardsByMode["evidence-only"].every(
      (card) =>
        card.kind !== "evidence-limits" &&
        card.kind !== "source-health" &&
        !(card.kind === "summary-only" && card.basis === "summary")
    ),
    "Evidence-only mode should exclude caveat-first and summary-limit cards."
  );
  assert(
    expectedInterpretationCardsByMode["caveats-first"][0]?.kind === "summary-only" &&
      expectedInterpretationCardsByMode["caveats-first"][1]?.kind === "evidence-limits",
    "Caveats-first mode should front-load evidence-limit cards."
  );

  for (const [mode, visibleInterpretationCards] of Object.entries(expectedInterpretationCardsByMode)) {
    const evidenceSummaryForMode = buildMarineEvidenceSummary({
      selectedVesselSummary,
      viewportSummary,
      chokepointSummary,
      visibleSlices,
      controls: { chokepointFilter: "all", chokepointSort: "priority" },
      activeNavigationTarget,
      focusedEvidenceRows,
      focusedEvidenceInterpretation,
      focusedEvidenceInterpretationMode: mode,
      visibleInterpretationCards,
      noaaContextSummary,
      ndbcContextSummary,
      scottishWaterContextSummary,
      vigicruesContextSummary: {
        sourceLine: "France Vigicrues Hydrometry: unavailable | fixture/local | 0 nearby stations",
        stationLines: [],
        exportLines: [
          "France Vigicrues Hydrometry: unavailable | fixture/local | 0 nearby stations"
        ],
        metadata: {
          sourceId: "france-vigicrues-hydrometry",
          sourceMode: "fixture",
          health: "unavailable",
          nearbyStationCount: 0,
          parameterFilter: "all",
          topStation: null,
          topObservationSummary: null,
          topObservationObservedAt: null,
          hasPartialMetadata: false,
          caveats: [
            "Vigicrues retrieval failed, so current hydrology context is unavailable and should not be treated as negative vessel evidence."
          ]
        }
      },
      irelandOpwContextSummary: {
        sourceLine: "Ireland OPW Water Level: degraded | fixture/local | 2 nearby stations",
        stationLines: [],
        exportLines: [
          "Ireland OPW Water Level: degraded | fixture/local | 2 nearby stations"
        ],
        metadata: {
          sourceId: "ireland-opw-waterlevel",
          sourceMode: "fixture",
          health: "degraded",
          nearbyStationCount: 2,
          topStation: {
            stationId: "opw-1",
            stationName: "Ballyduff",
            distanceKm: 0.7,
            waterbody: "River Feale",
            hydrometricArea: "Shannon Estuary South"
          },
          topObservationSummary: "Ballyduff | 1.42 m | River Feale",
          topReadingAt: "2026-04-04T11:42:00Z",
          hasPartialMetadata: true,
          caveats: [
            "Partial metadata degrades source-health confidence for this fixture review path."
          ]
        }
      },
      hydrologyContextSummary,
      contextFusionSummary: fusionSummary,
      contextReviewReportSummary: reviewReport,
      contextSourceRegistrySummary: sourceRegistrySummary,
      contextTimelineSummary,
      contextIssueQueueSummary: issueQueueSummary,
      contextIssueExportBundle: issueExportBundle,
      environmentalContextSummary,
      chokepointReviewContext
    });
    const interpretationMetadata =
      evidenceSummaryForMode.metadata.marineAnomalySummary.focusedEvidenceInterpretation;
    assert(
      interpretationMetadata.mode === mode,
      `Focused evidence interpretation metadata should preserve ${mode} mode.`
    );
    assert(
      interpretationMetadata.visibleCardCount === visibleInterpretationCards.length,
      `Focused evidence interpretation metadata should preserve ${mode} visible-card count.`
    );
    assert(
      JSON.stringify(interpretationMetadata.visibleCardKinds) ===
        JSON.stringify(visibleInterpretationCards.map((card) => card.kind)),
      `Focused evidence interpretation metadata should preserve ${mode} visible-card kinds.`
    );
    assert(
      JSON.stringify(interpretationMetadata.visibleCardLabels) ===
        JSON.stringify(visibleInterpretationCards.map((card) => card.label)),
      `Focused evidence interpretation metadata should preserve ${mode} visible-card labels.`
    );
    assert(
      JSON.stringify(interpretationMetadata.visibleCardBases) ===
        JSON.stringify(visibleInterpretationCards.map((card) => card.basis)),
      `Focused evidence interpretation metadata should preserve ${mode} visible-card bases.`
    );
    assert(
      interpretationMetadata.topCaveats.some((line) => /proof of vessel intent|aggregate anomaly summary|contextual source-health limits/i.test(line)),
      `Focused evidence interpretation metadata should preserve review/export caveats in ${mode} mode.`
    );
    assert(
      evidenceSummaryForMode.metadata.marineAnomalySummary.chokepointReviewPackage?.reviewOnly === true,
      `Chokepoint review package should remain review-only in ${mode} mode.`
    );
    assert(
      evidenceSummaryForMode.metadata.marineAnomalySummary.contextTimeline?.currentSnapshot
        ?.reviewOnly === true,
      `Context timeline should remain review-only in ${mode} mode.`
    );
    assert(
      evidenceSummaryForMode.metadata.marineAnomalySummary.contextIssueExportBundle?.doesNotProveLines.some(
        (line) => /vessel intent|wrongdoing/i.test(line)
      ),
      `Issue export bundle should preserve no-intent/no-wrongdoing wording in ${mode} mode.`
    );
    assert(
      evidenceSummaryForMode.metadata.marineAnomalySummary.caveats.some((line) =>
        /proof of intent or wrongdoing/i.test(line)
      ),
      `Top-level marine caveats should preserve no-intent/no-wrongdoing wording in ${mode} mode.`
    );
  }

  const broadEnvironmentalContextSummary = buildBroadAllSourcesEnvironmentalContextSummary();
  const broadSourceRegistrySummary = buildBroadAllSourcesSourceRegistrySummary();
  const broadIssueQueueSummary = buildMarineContextIssueQueue(broadSourceRegistrySummary);
  const broadHydrologyContextSummary = {
    ...hydrologyContextSummary,
    sourceLine: "Marine hydrology context: 3/3 loaded | broad context",
    metadata: {
      ...hydrologyContextSummary.metadata,
      loadedSourceCount: 3,
      degradedSourceCount: 0,
      nearbyStationCount: 5,
      healthSummary: "3/3 hydrology sources loaded; broad context available",
      vigicrues: {
        ...hydrologyContextSummary.metadata.vigicrues,
        health: "loaded",
        nearbyStationCount: 2,
        topStationName: "Arles",
        topObservationObservedAt: "2026-04-04T11:40:00Z"
      },
      irelandOpw: {
        ...hydrologyContextSummary.metadata.irelandOpw,
        health: "loaded",
        nearbyStationCount: 1,
        topStationName: "Ballyduff",
        topReadingAt: "2026-04-04T11:42:00Z",
        hasPartialMetadata: false
      },
      waterinfo: {
        ...hydrologyContextSummary.metadata.waterinfo,
        health: "loaded",
        nearbyStationCount: 2,
        topStationName: "Hoek van Holland",
        topObservationObservedAt: "2026-04-04T11:41:00Z",
        hasPartialMetadata: false
      },
      caveats: ["Hydrology context is available and remains contextual only."]
    }
  };
  const broadScottishWaterContextSummary = {
    ...scottishWaterContextSummary,
    sourceLine: "Scottish Water Overflows: loaded | fixture/local | 2 nearby monitors | 0 active",
    metadata: {
      ...scottishWaterContextSummary.metadata,
      health: "loaded",
      nearbyMonitorCount: 2,
      activeMonitorCount: 0,
      topMonitor: {
        eventId: "sw-broad-1",
        siteName: "Leith Sands Overflow",
        status: "inactive",
        distanceKm: 1.2
      },
      caveats: ["Overflow monitor activation is contextual infrastructure status only."]
    }
  };
  const broadFusionSummary = buildMarineContextFusionSummary({
    environmentalContextSummary: broadEnvironmentalContextSummary,
    hydrologyContextSummary: broadHydrologyContextSummary,
    scottishWaterContextSummary: broadScottishWaterContextSummary,
    contextSourceRegistrySummary: broadSourceRegistrySummary,
    contextIssueQueueSummary: broadIssueQueueSummary
  });
  const broadReviewReport = buildMarineContextReviewReport({
    fusionSummary: broadFusionSummary,
    issueQueueSummary: broadIssueQueueSummary
  });
  const broadIssueExportBundle = buildMarineContextIssueExportBundle({
    sourceRegistrySummary: broadSourceRegistrySummary,
    issueQueueSummary: broadIssueQueueSummary
  });

  assert(broadFusionSummary, "Broad preset fusion summary should be created.");
  assert(
    broadFusionSummary.metadata.exportReadiness === "ready-with-caveats",
    "Broad preset fusion summary should remain ready-with-caveats."
  );
  assert(
    broadFusionSummary.metadata.dominatedByLimitedSources === false,
    "Broad preset fusion summary should not be dominated by limited sources."
  );

  const limitedEnvironmentalContextSummary = buildToggleLimitedEnvironmentalContextSummary();
  const limitedSourceRegistrySummary = buildToggleLimitedSourceRegistrySummary();
  const limitedIssueQueueSummary = buildMarineContextIssueQueue(limitedSourceRegistrySummary);
  const limitedHydrologyContextSummary = {
    ...hydrologyContextSummary,
    metadata: {
      ...hydrologyContextSummary.metadata,
      loadedSourceCount: 1,
      degradedSourceCount: 1,
      nearbyStationCount: 2,
      healthSummary: "1/3 hydrology sources loaded; partial context",
      vigicrues: {
        ...hydrologyContextSummary.metadata.vigicrues,
        health: "unavailable",
        nearbyStationCount: 0,
        topStationName: null,
        topObservationObservedAt: null
      },
      irelandOpw: {
        ...hydrologyContextSummary.metadata.irelandOpw,
        health: "loaded",
        nearbyStationCount: 1,
        topStationName: "Ballyduff",
        topReadingAt: "2026-04-04T11:42:00Z",
        hasPartialMetadata: false
      },
      waterinfo: {
        ...hydrologyContextSummary.metadata.waterinfo,
        health: "degraded",
        nearbyStationCount: 1,
        topStationName: "Hoek van Holland",
        topObservationObservedAt: "2026-04-04T11:41:00Z",
        hasPartialMetadata: true
      },
      caveats: ["Hydrology context is partial and remains contextual only."]
    }
  };
  const limitedScottishWaterContextSummary = scottishWaterContextSummary;
  const limitedFusionSummary = buildMarineContextFusionSummary({
    environmentalContextSummary: limitedEnvironmentalContextSummary,
    hydrologyContextSummary: limitedHydrologyContextSummary,
    scottishWaterContextSummary: limitedScottishWaterContextSummary,
    contextSourceRegistrySummary: limitedSourceRegistrySummary,
    contextIssueQueueSummary: limitedIssueQueueSummary
  });
  const limitedReviewReport = buildMarineContextReviewReport({
    fusionSummary: limitedFusionSummary,
    issueQueueSummary: limitedIssueQueueSummary
  });
  const limitedIssueExportBundle = buildMarineContextIssueExportBundle({
    sourceRegistrySummary: limitedSourceRegistrySummary,
    issueQueueSummary: limitedIssueQueueSummary
  });

  assert(limitedFusionSummary, "Limited preset fusion summary should be created.");
  assert(
    limitedFusionSummary.metadata.dominatedByLimitedSources === true,
    "Limited preset fusion summary should be dominated by limited sources."
  );
  assert(
    /partial context/i.test(limitedFusionSummary.overallAvailabilityLine),
    "Limited preset fusion summary should use partial-context wording."
  );
  assert(
    limitedIssueQueueSummary.topIssues.some((issue) => issue.issueType === "disabled"),
    "Limited preset issue queue should surface at least one disabled-source issue."
  );
  assert(
    limitedIssueExportBundle.rows.some(
      (row) => row.sourceId === "noaa-coops-tides-currents" && row.availability === "disabled"
    ),
    "Limited preset issue export should preserve disabled CO-OPS row."
  );

  const broadChokepointReviewPackage = buildMarineChokepointReviewPackage({
    chokepointReviewContext,
    chokepointSummary,
    activeNavigationTarget,
    focusedEvidenceRows,
    focusedEvidenceInterpretation: buildInterpretationForEnvironmentalContext(
      broadEnvironmentalContextSummary
    ),
    contextSourceRegistrySummary: broadSourceRegistrySummary,
    contextIssueQueueSummary: broadIssueQueueSummary,
    contextIssueExportBundle: broadIssueExportBundle,
    contextFusionSummary: broadFusionSummary,
    contextReviewReportSummary: broadReviewReport,
    hydrologyContextSummary: broadHydrologyContextSummary,
    environmentalContextSummary: broadEnvironmentalContextSummary
  });
  const limitedChokepointReviewPackage = buildMarineChokepointReviewPackage({
    chokepointReviewContext,
    chokepointSummary,
    activeNavigationTarget,
    focusedEvidenceRows,
    focusedEvidenceInterpretation: buildInterpretationForEnvironmentalContext(
      limitedEnvironmentalContextSummary
    ),
    contextSourceRegistrySummary: limitedSourceRegistrySummary,
    contextIssueQueueSummary: limitedIssueQueueSummary,
    contextIssueExportBundle: limitedIssueExportBundle,
    contextFusionSummary: limitedFusionSummary,
    contextReviewReportSummary: limitedReviewReport,
    hydrologyContextSummary: limitedHydrologyContextSummary,
    environmentalContextSummary: limitedEnvironmentalContextSummary
  });

  const broadSnapshot = buildMarineContextSnapshot({
    environmentalContextSummary: broadEnvironmentalContextSummary,
    contextSourceRegistrySummary: broadSourceRegistrySummary,
    focusedTarget: activeNavigationTarget,
    chokepointReviewPackage: broadChokepointReviewPackage,
    createdAt: "2026-04-04T10:45:00Z"
  });
  const limitedSnapshot = buildMarineContextSnapshot({
    environmentalContextSummary: limitedEnvironmentalContextSummary,
    contextSourceRegistrySummary: limitedSourceRegistrySummary,
    focusedTarget: activeNavigationTarget,
    chokepointReviewPackage: limitedChokepointReviewPackage,
    createdAt: "2026-04-04T12:15:00Z"
  });
  const transitionTimeline = buildMarineContextTimelineSummary(
    reduceMarineContextSnapshots(
      reduceMarineContextSnapshots([], broadSnapshot),
      limitedSnapshot
    )
  );

  assert(
    transitionTimeline.snapshotCount === 2,
    "Toggle/preset transition timeline should preserve current and previous snapshots."
  );
  assert(
    transitionTimeline.currentSnapshot?.presetId === "buoy-weather-focus" &&
      transitionTimeline.previousSnapshot?.presetId === "regional-marine-context",
    "Transition timeline should preserve current limited preset and previous broad preset."
  );
  assert(
    JSON.stringify(transitionTimeline.currentSnapshot?.enabledSources ?? []) ===
      JSON.stringify(["ndbc"]),
    "Transition timeline current snapshot should preserve limited enabled-source set."
  );
  assert(
    JSON.stringify(transitionTimeline.previousSnapshot?.enabledSources ?? []) ===
      JSON.stringify(["coops", "ndbc"]),
    "Transition timeline previous snapshot should preserve broad enabled-source set."
  );

  const limitedTransitionInterpretation = buildInterpretationForEnvironmentalContext(
    limitedEnvironmentalContextSummary
  );
  const limitedTransitionVisibleCards = getMarineEvidenceInterpretationCards(
    limitedTransitionInterpretation,
    "compact"
  );
  const limitedTransitionEvidenceSummary = buildMarineEvidenceSummary({
    selectedVesselSummary,
    viewportSummary,
    chokepointSummary,
    visibleSlices,
    controls: { chokepointFilter: "all", chokepointSort: "priority" },
    activeNavigationTarget,
    focusedEvidenceRows,
    focusedEvidenceInterpretation: limitedTransitionInterpretation,
    focusedEvidenceInterpretationMode: "compact",
    visibleInterpretationCards: limitedTransitionVisibleCards,
    noaaContextSummary: {
      sourceLine: "NOAA CO-OPS: disabled | fixture/local | 0 nearby stations",
      stationLines: [],
      exportLines: ["NOAA CO-OPS: disabled | fixture/local | 0 nearby stations"],
      metadata: {
        sourceId: "noaa-coops-tides-currents",
        sourceMode: "fixture",
        health: "disabled",
        nearbyStationCount: 0,
        contextKind: "viewport",
        topStation: null,
        caveats: ["CO-OPS is disabled by the current marine preset/source-toggle state."]
      }
    },
    ndbcContextSummary: {
      sourceLine: "NOAA NDBC: loaded | fixture/local | 1 nearby station",
      stationLines: [],
      exportLines: ["NOAA NDBC: loaded | fixture/local | 1 nearby station"],
      metadata: {
        sourceId: "noaa-ndbc-realtime",
        sourceMode: "fixture",
        health: "loaded",
        nearbyStationCount: 1,
        contextKind: "viewport",
        topStation: {
          stationId: "ndbc-42019",
          stationName: "NDBC 42019",
          distanceKm: 35.1,
          stationType: "buoy"
        },
        topObservationSummary: "Wind 18 kts | seas 2.4 m",
        caveats: ["Fixture/local mode should not be treated as live operational buoy coverage."]
      }
    },
    scottishWaterContextSummary: limitedScottishWaterContextSummary,
    vigicruesContextSummary: {
      sourceLine: "France Vigicrues Hydrometry: unavailable | fixture/local | 0 nearby stations",
      stationLines: [],
      exportLines: [
        "France Vigicrues Hydrometry: unavailable | fixture/local | 0 nearby stations"
      ],
      metadata: {
        sourceId: "france-vigicrues-hydrometry",
        sourceMode: "fixture",
        health: "unavailable",
        nearbyStationCount: 0,
        parameterFilter: "all",
        topStation: null,
        topObservationSummary: null,
        topObservationObservedAt: null,
        hasPartialMetadata: false,
        caveats: [
          "Vigicrues retrieval failed, so current hydrology context is unavailable and should not be treated as negative vessel evidence."
        ]
      }
    },
    irelandOpwContextSummary: {
      sourceLine: "Ireland OPW Water Level: loaded | fixture/local | 1 nearby station",
      stationLines: [],
      exportLines: ["Ireland OPW Water Level: loaded | fixture/local | 1 nearby station"],
      metadata: {
        sourceId: "ireland-opw-waterlevel",
        sourceMode: "fixture",
        health: "loaded",
        nearbyStationCount: 1,
        topStation: {
          stationId: "opw-1",
          stationName: "Ballyduff",
          distanceKm: 0.7,
          waterbody: "River Feale",
          hydrometricArea: "Shannon Estuary South"
        },
        topObservationSummary: "Ballyduff | 1.18 m | River Feale",
        topReadingAt: "2026-04-04T11:42:00Z",
        hasPartialMetadata: false,
        caveats: ["OPW readings are contextual hydrometric data only."]
      }
    },
    hydrologyContextSummary: limitedHydrologyContextSummary,
    contextFusionSummary: limitedFusionSummary,
    contextReviewReportSummary: limitedReviewReport,
    contextSourceRegistrySummary: limitedSourceRegistrySummary,
    contextTimelineSummary: transitionTimeline,
    contextIssueQueueSummary: limitedIssueQueueSummary,
    contextIssueExportBundle: limitedIssueExportBundle,
    environmentalContextSummary: limitedEnvironmentalContextSummary,
    chokepointReviewContext
  });
  const limitedTransitionMetadata =
    limitedTransitionEvidenceSummary.metadata.marineAnomalySummary;
  assert(
    limitedTransitionMetadata.environmentalContext?.presetId === "buoy-weather-focus",
    "Limited transition export metadata should preserve the active preset id."
  );
  assert(
    JSON.stringify(limitedTransitionMetadata.environmentalContext?.enabledSources ?? []) ===
      JSON.stringify(["ndbc"]),
    "Limited transition export metadata should preserve enabled sources."
  );
  assert(
    limitedTransitionMetadata.contextSourceSummary?.disabledSourceCount === 1,
    "Limited transition export metadata should preserve disabled-source count."
  );
  assert(
    limitedTransitionMetadata.contextSourceSummary?.rows.some(
      (row) => row.sourceId === "noaa-coops-tides-currents" && row.availability === "disabled"
    ),
    "Limited transition export metadata should preserve disabled source row state."
  );
  assert(
    limitedTransitionMetadata.contextIssueQueue?.topIssues.some(
      (issue) => issue.issueType === "disabled"
    ),
    "Limited transition export metadata should preserve disabled-source issue visibility."
  );
  assert(
    limitedTransitionMetadata.contextIssueExportBundle?.rows.some(
      (row) => row.sourceId === "noaa-coops-tides-currents" && /re-enable/i.test(row.allowedReviewAction)
    ),
    "Limited transition issue-export metadata should preserve disabled-source review action."
  );
  assert(
    limitedTransitionMetadata.contextFusionSummary?.limitedSourceCount === 4 &&
      limitedTransitionMetadata.contextFusionSummary?.dominatedByLimitedSources === true,
    "Limited transition fusion metadata should align with degraded/unavailable/disabled source totals."
  );
  assert(
    limitedTransitionMetadata.contextTimeline?.currentSnapshot?.presetId ===
      limitedTransitionMetadata.environmentalContext?.presetId,
    "Limited transition timeline should align current preset id with environmental context metadata."
  );
  assert(
    JSON.stringify(
      limitedTransitionMetadata.contextTimeline?.currentSnapshot?.enabledSources ?? []
    ) === JSON.stringify(limitedTransitionMetadata.environmentalContext?.enabledSources ?? []),
    "Limited transition timeline should align current enabled sources with environmental context metadata."
  );
  assert(
    JSON.stringify(
      limitedTransitionMetadata.focusedEvidenceInterpretation.sourceModes
    ) === JSON.stringify(limitedEnvironmentalContextSummary.environmentalCaveatSummary.sourceModes),
    "Limited transition focused interpretation should align source-mode caveats with the active environmental context."
  );
  assert(
    limitedTransitionMetadata.focusedEvidenceInterpretation.environmentalCaveats.some((line) =>
      /not used as proof of vessel intent/i.test(line)
    ),
    "Limited transition focused interpretation should preserve no-intent environmental caveats."
  );
  assert(
    limitedTransitionMetadata.contextReviewReport?.doesNotProveLines.some((line) =>
      /wrongdoing/i.test(line)
    ) &&
      limitedTransitionMetadata.contextIssueExportBundle?.doesNotProveLines.some((line) =>
        /vessel intent/i.test(line)
      ) &&
      limitedTransitionMetadata.caveats.some((line) => /proof of intent or wrongdoing/i.test(line)),
    "Limited transition export package should preserve no-intent/no-wrongdoing guardrails across review layers."
  );

  function buildCompactScopeScenario(input) {
    const issueQueueSummary = buildMarineContextIssueQueue(input.contextSourceRegistrySummary);
    const contextFusionSummary = buildMarineContextFusionSummary({
      environmentalContextSummary: input.environmentalContextSummary,
      hydrologyContextSummary: input.hydrologyContextSummary,
      scottishWaterContextSummary: input.scottishWaterContextSummary,
      contextSourceRegistrySummary: input.contextSourceRegistrySummary,
      contextIssueQueueSummary: issueQueueSummary
    });
    const contextReviewReportSummary = buildMarineContextReviewReport({
      fusionSummary: contextFusionSummary,
      issueQueueSummary
    });
    const contextIssueExportBundle = buildMarineContextIssueExportBundle({
      sourceRegistrySummary: input.contextSourceRegistrySummary,
      issueQueueSummary
    });
    const scopeInterpretation = buildInterpretationForEnvironmentalContext(
      input.environmentalContextSummary
    );
    const chokepointReviewPackage = buildMarineChokepointReviewPackage({
      chokepointReviewContext,
      chokepointSummary,
      activeNavigationTarget,
      focusedEvidenceRows,
      focusedEvidenceInterpretation: scopeInterpretation,
      contextSourceRegistrySummary: input.contextSourceRegistrySummary,
      contextIssueQueueSummary: issueQueueSummary,
      contextIssueExportBundle,
      contextFusionSummary,
      contextReviewReportSummary,
      hydrologyContextSummary: input.hydrologyContextSummary,
      environmentalContextSummary: input.environmentalContextSummary
    });
    const currentSnapshot = buildMarineContextSnapshot({
      environmentalContextSummary: input.environmentalContextSummary,
      contextSourceRegistrySummary: input.contextSourceRegistrySummary,
      focusedTarget: activeNavigationTarget,
      chokepointReviewPackage,
      createdAt: input.createdAt
    });
    const contextTimelineSummary = buildMarineContextTimelineSummary(
      input.previousSnapshot
        ? reduceMarineContextSnapshots(
            reduceMarineContextSnapshots([], input.previousSnapshot),
            currentSnapshot
          )
        : reduceMarineContextSnapshots([], currentSnapshot)
    );
    const evidenceSummary = buildMarineEvidenceSummary({
      selectedVesselSummary,
      viewportSummary,
      chokepointSummary,
      visibleSlices,
      controls: { chokepointFilter: "all", chokepointSort: "priority" },
      activeNavigationTarget,
      focusedEvidenceRows,
      focusedEvidenceInterpretation: scopeInterpretation,
      focusedEvidenceInterpretationMode: "compact",
      visibleInterpretationCards: getMarineEvidenceInterpretationCards(
        scopeInterpretation,
        "compact"
      ),
      noaaContextSummary: input.noaaContextSummary,
      ndbcContextSummary: input.ndbcContextSummary,
      scottishWaterContextSummary: input.scottishWaterContextSummary,
      vigicruesContextSummary: input.vigicruesContextSummary,
      irelandOpwContextSummary: input.irelandOpwContextSummary,
      hydrologyContextSummary: input.hydrologyContextSummary,
      contextFusionSummary,
      contextReviewReportSummary,
      contextSourceRegistrySummary: input.contextSourceRegistrySummary,
      contextTimelineSummary,
      contextIssueQueueSummary: issueQueueSummary,
      contextIssueExportBundle,
      environmentalContextSummary: input.environmentalContextSummary,
      chokepointReviewContext
    });

    return {
      issueQueueSummary,
      contextFusionSummary,
      contextReviewReportSummary,
      contextIssueExportBundle,
      chokepointReviewPackage,
      currentSnapshot,
      contextTimelineSummary,
      evidenceSummary
    };
  }

  const broadNoaaContextSummary = {
    ...noaaContextSummary,
    sourceLine: "NOAA CO-OPS: loaded | fixture/local | 3 nearby stations",
    exportLines: ["NOAA CO-OPS: loaded | fixture/local | 3 nearby stations"],
    metadata: {
      ...noaaContextSummary.metadata,
      nearbyStationCount: 3,
      contextKind: "viewport",
      topStation: {
        stationId: "coops-2",
        stationName: "Galveston Pier 21",
        distanceKm: 5.2,
        stationType: "mixed"
      }
    }
  };
  const broadNdbcContextSummary = {
    sourceLine: "NOAA NDBC: loaded | fixture/local | 2 nearby stations",
    stationLines: [],
    exportLines: ["NOAA NDBC: loaded | fixture/local | 2 nearby stations"],
    metadata: {
      sourceId: "noaa-ndbc-realtime",
      sourceMode: "fixture",
      health: "loaded",
      nearbyStationCount: 2,
      contextKind: "viewport",
      topStation: {
        stationId: "ndbc-42035",
        stationName: "NDBC 42035",
        distanceKm: 46.3,
        stationType: "buoy"
      },
      topObservationSummary: "Wind 14 kts | seas 1.9 m",
      caveats: ["Fixture/local mode should not be treated as live operational buoy coverage."]
    }
  };
  const broadVigicruesContextSummary = {
    sourceLine: "France Vigicrues Hydrometry: loaded | fixture/local | 2 nearby stations",
    stationLines: [],
    exportLines: ["France Vigicrues Hydrometry: loaded | fixture/local | 2 nearby stations"],
    metadata: {
      sourceId: "france-vigicrues-hydrometry",
      sourceMode: "fixture",
      health: "loaded",
      nearbyStationCount: 2,
      parameterFilter: "all",
      topStation: {
        stationId: "vig-1",
        stationName: "Arles",
        distanceKm: 12.4,
        parameter: "water-height",
        riverBasin: "Rhone"
      },
      topObservationSummary: "Arles | 3.10 m water height",
      topObservationObservedAt: "2026-04-04T11:40:00Z",
      hasPartialMetadata: false,
      caveats: ["Hydrology context is station-local and not flood-impact confirmation."]
    }
  };
  const broadIrelandOpwContextSummary = {
    sourceLine: "Ireland OPW Water Level: loaded | fixture/local | 1 nearby station",
    stationLines: [],
    exportLines: ["Ireland OPW Water Level: loaded | fixture/local | 1 nearby station"],
    metadata: {
      sourceId: "ireland-opw-waterlevel",
      sourceMode: "fixture",
      health: "loaded",
      nearbyStationCount: 1,
      topStation: {
        stationId: "opw-1",
        stationName: "Ballyduff",
        distanceKm: 0.7,
        waterbody: "River Feale",
        hydrometricArea: "Shannon Estuary South"
      },
      topObservationSummary: "Ballyduff | 1.12 m | River Feale",
      topReadingAt: "2026-04-04T11:42:00Z",
      hasPartialMetadata: false,
      caveats: ["OPW readings are contextual hydrometric data only."]
    }
  };

  const selectedVesselEnvironmentalContextSummary = {
    ...broadEnvironmentalContextSummary,
    healthSummary: "2/2 enabled sources loaded; selected-vessel anchored context available",
    environmentalCaveatSummary: {
      ...broadEnvironmentalContextSummary.environmentalCaveatSummary,
      sourceHealthSummary: "2/2 enabled sources loaded; selected-vessel anchored context available"
    },
    metadata: {
      ...broadEnvironmentalContextSummary.metadata,
      presetId: "selected-vessel-review",
      presetLabel: "Selected vessel review",
      anchor: "selected-vessel",
      effectiveAnchor: "selected-vessel",
      radiusKm: 150,
      radiusPreset: "small",
      healthSummary: "2/2 enabled sources loaded; selected-vessel anchored context available",
      environmentalCaveatSummary: {
        ...broadEnvironmentalContextSummary.metadata.environmentalCaveatSummary,
        sourceHealthSummary:
          "2/2 enabled sources loaded; selected-vessel anchored context available"
      }
    }
  };
  const selectedVesselScenario = buildCompactScopeScenario({
    environmentalContextSummary: selectedVesselEnvironmentalContextSummary,
    contextSourceRegistrySummary: broadSourceRegistrySummary,
    hydrologyContextSummary: broadHydrologyContextSummary,
    scottishWaterContextSummary: broadScottishWaterContextSummary,
    noaaContextSummary: broadNoaaContextSummary,
    ndbcContextSummary: broadNdbcContextSummary,
    vigicruesContextSummary: broadVigicruesContextSummary,
    irelandOpwContextSummary: broadIrelandOpwContextSummary,
    createdAt: "2026-04-04T09:30:00Z"
  });
  const selectedVesselMetadata = selectedVesselScenario.evidenceSummary.metadata.marineAnomalySummary;
  assert(
    selectedVesselMetadata.environmentalContext?.anchor === "selected-vessel" &&
      selectedVesselMetadata.environmentalContext?.effectiveAnchor === "selected-vessel",
    "Selected-vessel scenario should preserve selected-vessel anchor metadata."
  );
  assert(
    selectedVesselMetadata.contextTimeline?.currentSnapshot?.anchor === "selected-vessel" &&
      selectedVesselMetadata.contextTimeline?.currentSnapshot?.effectiveAnchor === "selected-vessel",
    "Selected-vessel scenario timeline should preserve selected-vessel anchor metadata."
  );
  assert(
    selectedVesselMetadata.contextFusionSummary?.familyLines[0]?.detail.includes(
      "preset Selected vessel review"
    ),
    "Selected-vessel scenario fusion summary should preserve selected-vessel preset labeling."
  );

  const fallbackEnvironmentalContextSummary = {
    ...selectedVesselEnvironmentalContextSummary,
    healthSummary: "2/2 enabled sources loaded; viewport/manual fallback context available",
    caveats: [
      ...selectedVesselEnvironmentalContextSummary.caveats,
      "Selected vessel center unavailable; using viewport center for current marine context."
    ],
    environmentalCaveatSummary: {
      ...selectedVesselEnvironmentalContextSummary.environmentalCaveatSummary,
      sourceHealthSummary:
        "2/2 enabled sources loaded; viewport/manual fallback context available",
      caveats: [
        ...selectedVesselEnvironmentalContextSummary.environmentalCaveatSummary.caveats,
        "Selected vessel center unavailable; using viewport center for current marine context."
      ]
    },
    metadata: {
      ...selectedVesselEnvironmentalContextSummary.metadata,
      effectiveAnchor: "fallback-viewport",
      fallbackReason: "Selected vessel center unavailable; using viewport center.",
      healthSummary: "2/2 enabled sources loaded; viewport/manual fallback context available",
      caveats: [
        ...selectedVesselEnvironmentalContextSummary.metadata.caveats,
        "Selected vessel center unavailable; using viewport center for current marine context."
      ],
      environmentalCaveatSummary: {
        ...selectedVesselEnvironmentalContextSummary.metadata.environmentalCaveatSummary,
        sourceHealthSummary:
          "2/2 enabled sources loaded; viewport/manual fallback context available",
        caveats: [
          ...selectedVesselEnvironmentalContextSummary.metadata.environmentalCaveatSummary.caveats,
          "Selected vessel center unavailable; using viewport center for current marine context."
        ]
      }
    }
  };
  const fallbackScenario = buildCompactScopeScenario({
    environmentalContextSummary: fallbackEnvironmentalContextSummary,
    contextSourceRegistrySummary: broadSourceRegistrySummary,
    hydrologyContextSummary: broadHydrologyContextSummary,
    scottishWaterContextSummary: broadScottishWaterContextSummary,
    noaaContextSummary: broadNoaaContextSummary,
    ndbcContextSummary: broadNdbcContextSummary,
    vigicruesContextSummary: broadVigicruesContextSummary,
    irelandOpwContextSummary: broadIrelandOpwContextSummary,
    previousSnapshot: selectedVesselScenario.currentSnapshot,
    createdAt: "2026-04-04T09:45:00Z"
  });
  const fallbackMetadata = fallbackScenario.evidenceSummary.metadata.marineAnomalySummary;
  assert(
    fallbackMetadata.environmentalContext?.effectiveAnchor === "fallback-viewport" &&
      /using viewport center/i.test(fallbackMetadata.environmentalContext?.fallbackReason ?? ""),
    "Fallback scenario should preserve viewport/manual fallback anchor metadata."
  );
  assert(
    fallbackMetadata.contextTimeline?.currentSnapshot?.effectiveAnchor === "fallback-viewport" &&
      fallbackMetadata.contextTimeline?.previousSnapshot?.effectiveAnchor === "selected-vessel",
    "Fallback scenario timeline should preserve fallback current snapshot and selected-vessel previous snapshot."
  );
  assert(
    fallbackMetadata.focusedEvidenceInterpretation.environmentalCaveats.some((line) =>
      /using viewport center/i.test(line)
    ),
    "Fallback scenario focused interpretation should preserve fallback-center caveats."
  );

  const chokepointScopedScenario = buildCompactScopeScenario({
    environmentalContextSummary,
    contextSourceRegistrySummary: sourceRegistrySummary,
    hydrologyContextSummary,
    scottishWaterContextSummary,
    noaaContextSummary,
    ndbcContextSummary,
    vigicruesContextSummary: {
      sourceLine: "France Vigicrues Hydrometry: unavailable | fixture/local | 0 nearby stations",
      stationLines: [],
      exportLines: [
        "France Vigicrues Hydrometry: unavailable | fixture/local | 0 nearby stations"
      ],
      metadata: {
        sourceId: "france-vigicrues-hydrometry",
        sourceMode: "fixture",
        health: "unavailable",
        nearbyStationCount: 0,
        parameterFilter: "all",
        topStation: null,
        topObservationSummary: null,
        topObservationObservedAt: null,
        hasPartialMetadata: false,
        caveats: [
          "Vigicrues retrieval failed, so current hydrology context is unavailable and should not be treated as negative vessel evidence."
        ]
      }
    },
    irelandOpwContextSummary: {
      sourceLine: "Ireland OPW Water Level: degraded | fixture/local | 2 nearby stations",
      stationLines: [],
      exportLines: [
        "Ireland OPW Water Level: degraded | fixture/local | 2 nearby stations"
      ],
      metadata: {
        sourceId: "ireland-opw-waterlevel",
        sourceMode: "fixture",
        health: "degraded",
        nearbyStationCount: 2,
        topStation: {
          stationId: "opw-1",
          stationName: "Ballyduff",
          distanceKm: 0.7,
          waterbody: "River Feale",
          hydrometricArea: "Shannon Estuary South"
        },
        topObservationSummary: "Ballyduff | 1.42 m | River Feale",
        topReadingAt: "2026-04-04T11:42:00Z",
        hasPartialMetadata: true,
        caveats: [
          "Partial metadata degrades source-health confidence for this fixture review path."
        ]
      }
    },
    createdAt: "2026-04-04T11:30:00Z"
  });
  const chokepointScopedMetadata =
    chokepointScopedScenario.evidenceSummary.metadata.marineAnomalySummary;
  assert(
    chokepointScopedMetadata.environmentalContext?.anchor === "chokepoint" &&
      chokepointScopedMetadata.chokepointReviewPackage?.boundedAreaLabel ===
        "Northern chokepoint review box",
    "Chokepoint-scoped scenario should preserve chokepoint anchor and bounded-area label."
  );
  assert(
    chokepointScopedMetadata.contextTimeline?.currentSnapshot?.boundedAreaLabel ===
      chokepointScopedMetadata.chokepointReviewPackage?.boundedAreaLabel,
    "Chokepoint-scoped timeline should preserve bounded-area label coherence."
  );

  const smallRadiusSourceRegistrySummary = {
    ...broadSourceRegistrySummary,
    rows: broadSourceRegistrySummary.rows.map((row) => {
      if (row.sourceId === "noaa-coops-tides-currents") {
        return { ...row, nearbyCount: 1, topSummary: "Galveston Pier 21 | mixed" };
      }
      if (row.sourceId === "noaa-ndbc-realtime") {
        return { ...row, nearbyCount: 1, topSummary: "42035 | 1.9 m seas" };
      }
      return row;
    }),
    metadata: {
      ...broadSourceRegistrySummary.metadata,
      rows: broadSourceRegistrySummary.metadata.rows.map((row) => {
        if (row.sourceId === "noaa-coops-tides-currents") {
          return { ...row, nearbyCount: 1, topSummary: "Galveston Pier 21 | mixed" };
        }
        if (row.sourceId === "noaa-ndbc-realtime") {
          return { ...row, nearbyCount: 1, topSummary: "42035 | 1.9 m seas" };
        }
        return row;
      })
    }
  };
  const smallRadiusEnvironmentalContextSummary = {
    ...selectedVesselEnvironmentalContextSummary,
    nearbyStationCount: 2,
    coopsStationCount: 1,
    ndbcStationCount: 1,
    metadata: {
      ...selectedVesselEnvironmentalContextSummary.metadata,
      presetId: "custom",
      presetLabel: "Custom context settings",
      isCustomPreset: true,
      radiusKm: 150,
      radiusPreset: "small",
      nearbyStationCount: 2,
      coopsStationCount: 1,
      ndbcStationCount: 1,
      topObservations: [
        "Water level: Galveston Pier 21 0.61 m (MLLW)",
        "Buoy: NDBC 42035 Wind 14 kts | seas 1.9 m"
      ]
    }
  };
  const largeRadiusEnvironmentalContextSummary = {
    ...selectedVesselEnvironmentalContextSummary,
    nearbyStationCount: 5,
    coopsStationCount: 3,
    ndbcStationCount: 2,
    metadata: {
      ...selectedVesselEnvironmentalContextSummary.metadata,
      presetId: "custom",
      presetLabel: "Custom context settings",
      isCustomPreset: true,
      radiusKm: 900,
      radiusPreset: "large",
      nearbyStationCount: 5,
      coopsStationCount: 3,
      ndbcStationCount: 2,
      topObservations: [
        "Water level: Galveston Pier 21 0.61 m (MLLW)",
        "Current: Bolivar Roads 1.8 kts NE",
        "Buoy: NDBC 42035 Wind 14 kts | seas 1.9 m"
      ]
    }
  };
  const smallRadiusScenario = buildCompactScopeScenario({
    environmentalContextSummary: smallRadiusEnvironmentalContextSummary,
    contextSourceRegistrySummary: smallRadiusSourceRegistrySummary,
    hydrologyContextSummary: broadHydrologyContextSummary,
    scottishWaterContextSummary: broadScottishWaterContextSummary,
    noaaContextSummary: {
      ...broadNoaaContextSummary,
      sourceLine: "NOAA CO-OPS: loaded | fixture/local | 1 nearby station",
      exportLines: ["NOAA CO-OPS: loaded | fixture/local | 1 nearby station"],
      metadata: {
        ...broadNoaaContextSummary.metadata,
        nearbyStationCount: 1
      }
    },
    ndbcContextSummary: {
      ...broadNdbcContextSummary,
      sourceLine: "NOAA NDBC: loaded | fixture/local | 1 nearby station",
      exportLines: ["NOAA NDBC: loaded | fixture/local | 1 nearby station"],
      metadata: {
        ...broadNdbcContextSummary.metadata,
        nearbyStationCount: 1
      }
    },
    vigicruesContextSummary: broadVigicruesContextSummary,
    irelandOpwContextSummary: broadIrelandOpwContextSummary,
    createdAt: "2026-04-04T09:50:00Z"
  });
  const largeRadiusScenario = buildCompactScopeScenario({
    environmentalContextSummary: largeRadiusEnvironmentalContextSummary,
    contextSourceRegistrySummary: broadSourceRegistrySummary,
    hydrologyContextSummary: broadHydrologyContextSummary,
    scottishWaterContextSummary: broadScottishWaterContextSummary,
    noaaContextSummary: broadNoaaContextSummary,
    ndbcContextSummary: broadNdbcContextSummary,
    vigicruesContextSummary: broadVigicruesContextSummary,
    irelandOpwContextSummary: broadIrelandOpwContextSummary,
    previousSnapshot: smallRadiusScenario.currentSnapshot,
    createdAt: "2026-04-04T10:05:00Z"
  });
  const smallRadiusMetadata = smallRadiusScenario.evidenceSummary.metadata.marineAnomalySummary;
  const largeRadiusMetadata = largeRadiusScenario.evidenceSummary.metadata.marineAnomalySummary;
  assert(
    smallRadiusMetadata.environmentalContext?.radiusKm === 150 &&
      largeRadiusMetadata.environmentalContext?.radiusKm === 900,
    "Radius-change scenarios should preserve changed radius metadata."
  );
  assert(
    smallRadiusMetadata.contextTimeline?.currentSnapshot?.radiusKm === 150 &&
      largeRadiusMetadata.contextTimeline?.currentSnapshot?.radiusKm === 900 &&
      largeRadiusMetadata.contextTimeline?.previousSnapshot?.radiusKm === 150,
    "Radius-change timeline should preserve current and previous radius values."
  );
  assert(
    smallRadiusMetadata.selectedVessel?.score === largeRadiusMetadata.selectedVessel?.score &&
      smallRadiusMetadata.viewport?.score === largeRadiusMetadata.viewport?.score &&
      smallRadiusMetadata.topChokepointSlice?.score === largeRadiusMetadata.topChokepointSlice?.score,
    "Radius changes should not alter anomaly scoring metadata."
  );
  assert(
    smallRadiusMetadata.contextSourceSummary?.rows.every((row, index) => {
      const largeRow = largeRadiusMetadata.contextSourceSummary?.rows[index];
      return (
        row.sourceId === largeRow?.sourceId &&
        row.health === largeRow?.health &&
        row.evidenceBasis === largeRow?.evidenceBasis
      );
    }),
    "Radius changes should preserve source ids, health states, and evidence bases."
  );

  const evidenceSummary = buildMarineEvidenceSummary({
    selectedVesselSummary,
    viewportSummary,
    chokepointSummary,
    visibleSlices,
    controls: { chokepointFilter: "all", chokepointSort: "priority" },
    activeNavigationTarget,
    focusedEvidenceRows,
    focusedEvidenceInterpretation,
    focusedEvidenceInterpretationMode: "compact",
    visibleInterpretationCards: expectedInterpretationCardsByMode.compact,
    noaaContextSummary,
    ndbcContextSummary,
    scottishWaterContextSummary,
    vigicruesContextSummary: {
      sourceLine: "France Vigicrues Hydrometry: unavailable | fixture/local | 0 nearby stations",
      stationLines: [],
      exportLines: [
        "France Vigicrues Hydrometry: unavailable | fixture/local | 0 nearby stations"
      ],
      metadata: {
        sourceId: "france-vigicrues-hydrometry",
        sourceMode: "fixture",
        health: "unavailable",
        nearbyStationCount: 0,
        parameterFilter: "all",
        topStation: null,
        topObservationSummary: null,
        topObservationObservedAt: null,
        hasPartialMetadata: false,
        caveats: [
          "Vigicrues retrieval failed, so current hydrology context is unavailable and should not be treated as negative vessel evidence."
        ]
      }
    },
    irelandOpwContextSummary: {
      sourceLine: "Ireland OPW Water Level: degraded | fixture/local | 2 nearby stations",
      stationLines: [],
      exportLines: [
        "Ireland OPW Water Level: degraded | fixture/local | 2 nearby stations"
      ],
      metadata: {
        sourceId: "ireland-opw-waterlevel",
        sourceMode: "fixture",
        health: "degraded",
        nearbyStationCount: 2,
        topStation: {
          stationId: "opw-1",
          stationName: "Ballyduff",
          distanceKm: 0.7,
          waterbody: "River Feale",
          hydrometricArea: "Shannon Estuary South"
        },
        topObservationSummary: "Ballyduff | 1.42 m | River Feale",
        topReadingAt: "2026-04-04T11:42:00Z",
        hasPartialMetadata: true,
        caveats: [
          "Partial metadata degrades source-health confidence for this fixture review path."
        ]
      }
    },
    netherlandsRwsWaterinfoContextSummary: waterinfoContextSummary,
    hydrologyContextSummary,
    contextFusionSummary: fusionSummary,
    contextReviewReportSummary: reviewReport,
    contextSourceRegistrySummary: sourceRegistrySummary,
    contextTimelineSummary,
    contextIssueQueueSummary: issueQueueSummary,
    contextIssueExportBundle: issueExportBundle,
    environmentalContextSummary,
    chokepointReviewContext
  });

  const marineMetadata = evidenceSummary.metadata.marineAnomalySummary;
  assert(marineMetadata.contextFusionSummary, "Marine evidence summary should export context fusion metadata.");
  assert(marineMetadata.contextReviewReport, "Marine evidence summary should export context review metadata.");
  assert(marineMetadata.contextSourceSummary, "Marine evidence summary should export context source-summary metadata.");
  assert(marineMetadata.contextIssueQueue, "Marine evidence summary should export context issue queue metadata.");
  assert(marineMetadata.contextIssueExportBundle, "Marine evidence summary should export context issue-export metadata.");
  assert(marineMetadata.hydrologyContext, "Marine evidence summary should export hydrology metadata.");
  assert(
    marineMetadata.netherlandsRwsWaterinfoContext,
    "Marine evidence summary should export Netherlands RWS Waterinfo metadata."
  );
  assert(marineMetadata.contextTimeline, "Marine evidence summary should export context timeline metadata.");
  assert(
    JSON.stringify(marineMetadata.contextFusionSummary) === JSON.stringify(fusionSummary.metadata),
    "Marine evidence summary should preserve fusion metadata without drift."
  );
  assert(
    JSON.stringify(marineMetadata.contextReviewReport) === JSON.stringify(reviewReport.metadata),
    "Marine evidence summary should preserve review-report metadata without drift."
  );
  assert(
    JSON.stringify(marineMetadata.contextSourceSummary) === JSON.stringify(sourceRegistrySummary.metadata),
    "Marine evidence summary should preserve source-summary metadata without drift."
  );
  assert(
    JSON.stringify(marineMetadata.contextIssueQueue) === JSON.stringify(issueQueueSummary.metadata),
    "Marine evidence summary should preserve issue-queue metadata without drift."
  );
  assert(
    JSON.stringify(marineMetadata.contextIssueExportBundle) === JSON.stringify(issueExportBundle.metadata),
    "Marine evidence summary should preserve issue-export metadata without drift."
  );
  assert(
    JSON.stringify(marineMetadata.netherlandsRwsWaterinfoContext) ===
      JSON.stringify(waterinfoContextSummary.metadata),
    "Marine evidence summary should preserve Waterinfo metadata without drift."
  );
  assert(
    JSON.stringify(marineMetadata.hydrologyContext) === JSON.stringify(hydrologyContextSummary.metadata),
    "Marine evidence summary should preserve hydrology metadata without drift."
  );
  assert(
    JSON.stringify(marineMetadata.contextTimeline) === JSON.stringify(contextTimelineSummary.metadata),
    "Marine evidence summary should preserve context-timeline metadata without drift."
  );
  assert(
    marineMetadata.chokepointReviewPackage,
    "Marine evidence summary should export chokepoint review package metadata."
  );
  assert(
    JSON.stringify(marineMetadata.chokepointReviewPackage) === JSON.stringify(chokepointReviewPackage.metadata),
    "Marine evidence summary should preserve chokepoint review package metadata without drift."
  );
  assert(
    marineMetadata.chokepointReviewPackage.reviewOnly === true,
    "Exported chokepoint review package should remain review-only."
  );
  assert(
    marineMetadata.chokepointReviewPackage.doesNotProve.some((line) =>
      /evasion, escort, toll activity, blockade, targeting, threat, intent, wrongdoing, or causation/i.test(line)
    ),
    "Exported chokepoint review package should preserve chokepoint no-intent/no-evasion guardrails."
  );
  assert(
    marineMetadata.chokepointReviewPackage.reviewSignals.some((line) => /queue\/backlog/i.test(line)),
    "Exported chokepoint review package should preserve queue/backlog review wording."
  );
  assert(
    marineMetadata.chokepointReviewPackage.reviewSignals.some((line) => /reroute/i.test(line)),
    "Exported chokepoint review package should preserve reroute review wording."
  );
  assert(
    marineMetadata.chokepointReviewPackage.contextGapCount ===
      marineMetadata.contextSourceSummary.unavailableSourceCount +
        marineMetadata.contextSourceSummary.disabledSourceCount +
        marineMetadata.contextSourceSummary.rows.filter((row) => row.availability === "empty").length,
    "Exported chokepoint review package should align context-gap count with source-summary empty/unavailable/disabled totals."
  );
  assert(
    marineMetadata.contextTimeline.currentSnapshot?.contextGapCount ===
      marineMetadata.chokepointReviewPackage.contextGapCount,
    "Exported context timeline should align current snapshot context-gap count with chokepoint review metadata."
  );
  assert(
    marineMetadata.contextTimeline.currentSnapshot?.corridorLabel ===
      marineMetadata.chokepointReviewPackage.corridorLabel,
    "Exported context timeline should align current snapshot corridor label with chokepoint review metadata."
  );
  assert(
    marineMetadata.contextTimeline.currentSnapshot?.sourceHealthLine ===
      marineMetadata.chokepointReviewPackage.sourceHealthLine,
    "Exported context timeline should align current snapshot source-health line with chokepoint review metadata."
  );
  assert(
    JSON.stringify(marineMetadata.contextTimeline.currentSnapshot?.focusedEvidenceKinds ?? []) ===
      JSON.stringify(marineMetadata.chokepointReviewPackage.focusedEvidenceKinds),
    "Exported context timeline should align current snapshot focused-evidence kinds with chokepoint review metadata."
  );
  assert(
    marineMetadata.contextTimeline.currentSnapshot?.reviewOnly === true,
    "Exported context timeline should preserve review-only posture."
  );
  assert(
    marineMetadata.contextIssueExportBundle.sourceCount ===
      marineMetadata.contextSourceSummary.sourceCount,
    "Issue export bundle source count should match source-summary source count."
  );
  assert(
    marineMetadata.contextIssueExportBundle.warningCount ===
      marineMetadata.contextIssueQueue.warningCount,
    "Issue export bundle warning count should match issue-queue warning count."
  );
  assert(
    marineMetadata.contextReviewReport.warningCount ===
      marineMetadata.contextIssueQueue.warningCount,
    "Review report warning count should match issue-queue warning count."
  );
  assert(
    marineMetadata.contextFusionSummary.limitedSourceCount ===
      marineMetadata.contextSourceSummary.degradedSourceCount +
        marineMetadata.contextSourceSummary.unavailableSourceCount +
        marineMetadata.contextSourceSummary.disabledSourceCount,
    "Fusion limited-source count should align with source-summary degraded/unavailable/disabled totals."
  );
  assert(
    marineMetadata.contextIssueExportBundle.rows.filter((row) => row.category === "hydrology")
      .length === 2,
    "Issue export bundle should preserve two hydrology rows."
  );
  assert(
    new Set(marineMetadata.contextIssueExportBundle.rows.map((row) => row.category)).size === 4,
    "Issue export bundle should preserve all four source-family categories."
  );
  assert(
    marineMetadata.contextIssueExportBundle.rows.some(
      (row) => row.sourceId === "noaa-coops-tides-currents" && row.evidenceBasis === "observed"
    ),
    "Issue export bundle should preserve observed evidence basis for NOAA CO-OPS."
  );
  assert(
    marineMetadata.contextIssueExportBundle.rows.some(
      (row) => row.sourceId === "noaa-ndbc-realtime" && row.evidenceBasis === "observed"
    ),
    "Issue export bundle should preserve observed evidence basis for NOAA NDBC."
  );
  assert(
    marineMetadata.contextIssueExportBundle.rows.some(
      (row) => row.sourceId === "scottish-water-overflows" && row.evidenceBasis === "contextual"
    ),
    "Issue export bundle should preserve contextual evidence basis for Scottish Water."
  );
  assert(
    marineMetadata.contextReviewReport.doesNotProveLines.some((line) =>
      /wrongdoing/i.test(line)
    ),
    "Review-report metadata should preserve wrongdoing guardrails."
  );
  assert(
    marineMetadata.contextReviewReport.doesNotProveLines.some((line) =>
      /single severity score/i.test(line)
    ),
    "Review-report metadata should preserve the no-single-severity-score guardrail."
  );
  assert(
    marineMetadata.contextIssueExportBundle.doesNotProveLines.some((line) =>
      /vessel intent/i.test(line)
    ),
    "Issue-export metadata should preserve vessel-intent guardrails."
  );
  assert(
    marineMetadata.caveats.some((line) => /proof of intent or wrongdoing/i.test(line)),
    "Top-level marine evidence metadata should preserve intent/wrongdoing caveats."
  );
  assert(
    evidenceSummary.displayLines.some((line) => /Marine context fusion: partial context/i.test(line)),
    "Evidence summary display lines should preserve partial-context fusion wording."
  );
  assert(
    evidenceSummary.displayLines.some((line) => /Marine source-health export: partial context/i.test(line)),
    "Evidence summary display lines should preserve issue-export partial-context wording."
  );
  assert(
    evidenceSummary.displayLines.some((line) => /Marine chokepoint review: Hormuz-style bounded corridor review/i.test(line)),
    "Evidence summary display lines should preserve chokepoint review export wording."
  );
  assert(
    evidenceSummary.displayLines.some((line) => /Marine context timeline: 2 snapshots \| current Chokepoint review/i.test(line)),
    "Evidence summary display lines should preserve timeline summary wording for the active chokepoint review lens."
  );
  assert(
    evidenceSummary.displayLines.some((line) => /ranking prioritizes review; it does not prove intent or wrongdoing/i.test(line)),
    "Evidence summary display lines should preserve intent/wrongdoing guardrails."
  );

  console.log("marine context helper regression passed");
}

runRegression();
