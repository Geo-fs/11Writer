import type { ConnectorConfigFormProps } from "./types";

export function WeatherConfigForm({ draft, onChange }: ConnectorConfigFormProps) {
  return (
    <>
      <label>
        Latitude
        <input
          max={90}
          min={-90}
          required
          step="0.0001"
          type="number"
          value={Number(draft.latitude ?? 0)}
          onChange={(event) =>
            onChange({
              ...draft,
              latitude: Number(event.target.value),
            })
          }
        />
      </label>
      <label>
        Longitude
        <input
          max={180}
          min={-180}
          required
          step="0.0001"
          type="number"
          value={Number(draft.longitude ?? 0)}
          onChange={(event) =>
            onChange({
              ...draft,
              longitude: Number(event.target.value),
            })
          }
        />
      </label>
      <label>
        Location Label (optional)
        <input
          placeholder="Austin, TX"
          value={String(draft.location_label ?? "")}
          onChange={(event) =>
            onChange({
              ...draft,
              location_label: event.target.value,
            })
          }
        />
      </label>
      <label>
        Units
        <select
          value={String(draft.units ?? "metric")}
          onChange={(event) =>
            onChange({
              ...draft,
              units: event.target.value,
            })
          }
        >
          <option value="metric">metric</option>
          <option value="imperial">imperial</option>
        </select>
      </label>
      <label>
        Min Temperature (optional)
        <input
          step="0.1"
          type="number"
          value={String(draft.min_temperature ?? "")}
          onChange={(event) =>
            onChange({
              ...draft,
              min_temperature: event.target.value,
            })
          }
        />
      </label>
      <label>
        Max Temperature (optional)
        <input
          step="0.1"
          type="number"
          value={String(draft.max_temperature ?? "")}
          onChange={(event) =>
            onChange({
              ...draft,
              max_temperature: event.target.value,
            })
          }
        />
      </label>
      <label>
        Max Wind Speed (optional)
        <input
          min={0}
          step="0.1"
          type="number"
          value={String(draft.max_wind_speed ?? "")}
          onChange={(event) =>
            onChange({
              ...draft,
              max_wind_speed: event.target.value,
            })
          }
        />
      </label>
      <label className="inline">
        <input
          checked={Boolean(draft.precipitation_trigger)}
          type="checkbox"
          onChange={(event) =>
            onChange({
              ...draft,
              precipitation_trigger: event.target.checked,
            })
          }
        />
        Precipitation Trigger
      </label>
      <label>
        Severe Condition Keywords (comma-separated)
        <input
          placeholder="thunderstorm, hail"
          value={String(draft.severe_condition_keywords_csv ?? "")}
          onChange={(event) =>
            onChange({
              ...draft,
              severe_condition_keywords_csv: event.target.value,
            })
          }
        />
      </label>
    </>
  );
}
