import { describe, expect, it } from "vitest";

import { createConnectorPayload, getConnectorFormSpec } from "../features/connectors/connectorFormRegistry";

describe("connector form registry", () => {
  it("builds weather connector payload from form draft", () => {
    const spec = getConnectorFormSpec("weather");
    expect(spec).not.toBeNull();

    const payload = createConnectorPayload({
      type: "weather",
      name: "Austin Weather",
      enabled: true,
      polling_interval_minutes: 30,
      draft: {
        latitude: 30.2672,
        longitude: -97.7431,
        location_label: "Austin",
        units: "metric",
        min_temperature: "5",
        max_temperature: "35",
        max_wind_speed: "25",
        precipitation_trigger: true,
        severe_condition_keywords_csv: "thunderstorm, hail",
      },
    });

    expect(payload.type).toBe("weather");
    expect(payload.config_json).toEqual({
      latitude: 30.2672,
      longitude: -97.7431,
      location_label: "Austin",
      units: "metric",
      thresholds: {
        min_temperature: 5,
        max_temperature: 35,
        max_wind_speed: 25,
        precipitation_trigger: true,
        severe_condition_keywords: ["thunderstorm", "hail"],
      },
    });
  });
});
