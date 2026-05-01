import type { ComponentType } from "react";

import type { Connector, ConnectorCreateInput } from "../../types/domain";
import { RSSNewsConfigForm } from "./forms/RSSNewsConfigForm";
import { SampleNewsConfigForm } from "./forms/SampleNewsConfigForm";
import { WeatherConfigForm } from "./forms/WeatherConfigForm";
import type { ConnectorConfigDraft, ConnectorConfigFormProps } from "./forms/types";

type ConnectorFormSpec = {
  type: string;
  label: string;
  defaultName: string;
  createDefaultDraft: () => ConnectorConfigDraft;
  buildConfig: (draft: ConnectorConfigDraft) => Record<string, unknown>;
  summarizeConfig: (config: Record<string, unknown>) => string;
  component: ComponentType<ConnectorConfigFormProps>;
};

function parseCsv(value: string): string[] {
  return value
    .split(",")
    .map((part) => part.trim())
    .filter(Boolean);
}

const specs: ConnectorFormSpec[] = [
  {
    type: "sample_news",
    label: "sample_news",
    defaultName: "Sample News Connector",
    createDefaultDraft: () => ({ keywords_csv: "airport, storm" }),
    buildConfig: (draft) => ({
      keywords: parseCsv(String(draft.keywords_csv ?? "")),
    }),
    summarizeConfig: (config) => {
      const keywords = Array.isArray(config.keywords) ? config.keywords.join(", ") : "";
      return keywords ? `keywords: ${keywords}` : "keywords: (none)";
    },
    component: SampleNewsConfigForm,
  },
  {
    type: "rss_news",
    label: "rss_news",
    defaultName: "RSS News Connector",
    createDefaultDraft: () => ({
      feed_url: "",
      include_keywords_csv: "",
      exclude_keywords_csv: "",
      max_items_per_run: 20,
      source_name: "",
    }),
    buildConfig: (draft) => ({
      feed_url: String(draft.feed_url ?? "").trim(),
      include_keywords: parseCsv(String(draft.include_keywords_csv ?? "")),
      exclude_keywords: parseCsv(String(draft.exclude_keywords_csv ?? "")),
      max_items_per_run: Number(draft.max_items_per_run ?? 20),
      ...(String(draft.source_name ?? "").trim()
        ? { source_name: String(draft.source_name).trim() }
        : {}),
    }),
    summarizeConfig: (config) => {
      const feedUrl = typeof config.feed_url === "string" ? config.feed_url : "(missing)";
      const maxItems =
        typeof config.max_items_per_run === "number" ? config.max_items_per_run : "(default)";
      return `feed: ${feedUrl} | max items: ${maxItems}`;
    },
    component: RSSNewsConfigForm,
  },
  {
    type: "weather",
    label: "weather",
    defaultName: "Weather Connector",
    createDefaultDraft: () => ({
      latitude: 30.2672,
      longitude: -97.7431,
      location_label: "",
      units: "metric",
      min_temperature: "",
      max_temperature: "",
      max_wind_speed: "",
      precipitation_trigger: false,
      severe_condition_keywords_csv: "",
    }),
    buildConfig: (draft) => {
      const minTemperature = String(draft.min_temperature ?? "").trim();
      const maxTemperature = String(draft.max_temperature ?? "").trim();
      const maxWindSpeed = String(draft.max_wind_speed ?? "").trim();
      const severeKeywords = parseCsv(String(draft.severe_condition_keywords_csv ?? ""));
      const thresholds = {
        ...(minTemperature ? { min_temperature: Number(minTemperature) } : {}),
        ...(maxTemperature ? { max_temperature: Number(maxTemperature) } : {}),
        ...(maxWindSpeed ? { max_wind_speed: Number(maxWindSpeed) } : {}),
        ...(draft.precipitation_trigger ? { precipitation_trigger: true } : {}),
        ...(severeKeywords.length ? { severe_condition_keywords: severeKeywords } : {}),
      };
      return {
        latitude: Number(draft.latitude),
        longitude: Number(draft.longitude),
        units: String(draft.units || "metric"),
        ...(String(draft.location_label ?? "").trim()
          ? { location_label: String(draft.location_label).trim() }
          : {}),
        ...(Object.keys(thresholds).length ? { thresholds } : {}),
      };
    },
    summarizeConfig: (config) => {
      const latitude = typeof config.latitude === "number" ? config.latitude.toFixed(3) : "?";
      const longitude = typeof config.longitude === "number" ? config.longitude.toFixed(3) : "?";
      const units = typeof config.units === "string" ? config.units : "metric";
      return `location: ${latitude}, ${longitude} | units: ${units}`;
    },
    component: WeatherConfigForm,
  },
];

const byType = new Map(specs.map((spec) => [spec.type, spec]));

export function listConnectorFormSpecs(): ConnectorFormSpec[] {
  return specs;
}

export function getConnectorFormSpec(type: string): ConnectorFormSpec | null {
  return byType.get(type) ?? null;
}

export function createConnectorPayload(input: {
  type: string;
  name: string;
  enabled: boolean;
  polling_interval_minutes: number;
  draft: ConnectorConfigDraft;
}): ConnectorCreateInput {
  const spec = getConnectorFormSpec(input.type);
  const config_json = spec ? spec.buildConfig(input.draft) : {};
  return {
    type: input.type,
    name: input.name,
    enabled: input.enabled,
    polling_interval_minutes: input.polling_interval_minutes,
    config_json,
  };
}

export function summarizeConnectorConfig(connector: Connector): string {
  const spec = getConnectorFormSpec(connector.type);
  if (!spec) {
    return JSON.stringify(connector.config_json);
  }
  return spec.summarizeConfig(connector.config_json);
}
