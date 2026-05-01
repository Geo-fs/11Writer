import type { ConnectorConfigFormProps } from "./types";

export function RSSNewsConfigForm({ draft, onChange }: ConnectorConfigFormProps) {
  return (
    <>
      <label>
        Feed URL
        <input
          placeholder="https://example.com/rss.xml"
          required
          type="url"
          value={String(draft.feed_url ?? "")}
          onChange={(event) =>
            onChange({
              ...draft,
              feed_url: event.target.value,
            })
          }
        />
      </label>
      <label>
        Include Keywords (comma-separated)
        <input
          placeholder="airport, weather"
          value={String(draft.include_keywords_csv ?? "")}
          onChange={(event) =>
            onChange({
              ...draft,
              include_keywords_csv: event.target.value,
            })
          }
        />
      </label>
      <label>
        Exclude Keywords (comma-separated)
        <input
          placeholder="opinion, sports"
          value={String(draft.exclude_keywords_csv ?? "")}
          onChange={(event) =>
            onChange({
              ...draft,
              exclude_keywords_csv: event.target.value,
            })
          }
        />
      </label>
      <label>
        Max Items Per Run
        <input
          max={100}
          min={1}
          type="number"
          value={Number(draft.max_items_per_run ?? 20)}
          onChange={(event) =>
            onChange({
              ...draft,
              max_items_per_run: Number(event.target.value),
            })
          }
        />
      </label>
      <label>
        Source Name Override (optional)
        <input
          placeholder="My RSS Source"
          value={String(draft.source_name ?? "")}
          onChange={(event) =>
            onChange({
              ...draft,
              source_name: event.target.value,
            })
          }
        />
      </label>
    </>
  );
}
