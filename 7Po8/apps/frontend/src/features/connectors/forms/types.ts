export type ConnectorConfigDraft = Record<string, string | number | boolean>;

export type ConnectorConfigFormProps = {
  draft: ConnectorConfigDraft;
  onChange: (nextDraft: ConnectorConfigDraft) => void;
};
