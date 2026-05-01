import type { ConnectorConfigFormProps } from "./types";

export function SampleNewsConfigForm({ draft, onChange }: ConnectorConfigFormProps) {
  return (
    <label>
      Keywords (comma-separated)
      <input
        placeholder="airport, storm"
        value={String(draft.keywords_csv ?? "")}
        onChange={(event) =>
          onChange({
            ...draft,
            keywords_csv: event.target.value,
          })
        }
      />
    </label>
  );
}
