import { useEffect, useMemo, useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { postJson } from "../../lib/api";
import {
  useSourceDiscoveryMemoryDetailQuery,
  useSourceDiscoveryReviewQueueQuery,
  useSourceDiscoveryRuntimeServicesQuery,
  useSourceDiscoveryRuntimeStatusQuery,
  useWaveLlmConfigQuery,
  useWaveLlmExecutionHistoryQuery,
  useWaveMonitorOverviewQuery,
  useWaveLlmReviewQueueQuery
} from "../../lib/queries";
import {
  CaveatBlock,
  EmptyState,
  EvidenceCard,
  InspectorSection,
  PriorityBadge,
  StatusBadge
} from "../../components/ui";
import type {
  SourceDiscoveryReviewAction,
  SourceDiscoveryReviewActionResponse,
  SourceDiscoveryReviewClaimApplicationResponse,
  SourceDiscoveryRuntimeControlResponse,
  SourceDiscoveryRuntimeServiceAction,
  SourceDiscoveryRuntimeServiceActionResponse,
  SourceDiscoveryRuntimeStatusResponse,
  WaveLlmConfigResponse,
  WaveLlmExecutionHistoryItem,
  WaveLlmProvider,
  WaveLlmReviewQueueItem
} from "../../types/api";

const REVIEW_ACTIONS: SourceDiscoveryReviewAction[] = [
  "mark_reviewed",
  "approve_candidate",
  "sandbox_check",
  "reject",
  "archive",
  "assign_owner"
];

const SERVICE_ACTIONS: SourceDiscoveryRuntimeServiceAction[] = [
  "materialize",
  "install",
  "start",
  "restart",
  "stop",
  "status",
  "uninstall"
];

export function OperatorControlPanel() {
  const queryClient = useQueryClient();
  const [operatorName, setOperatorName] = useState("Atlas Operator");
  const [reviewReason, setReviewReason] = useState("Reviewed in the single-page operator console.");
  const [approvalReason, setApprovalReason] = useState(
    "Human review accepted the bounded review packet for source-memory application."
  );
  const [ownerLane, setOwnerLane] = useState("");
  const [selectedSourceId, setSelectedSourceId] = useState<string | null>(null);
  const [selectedReviewId, setSelectedReviewId] = useState<string | null>(null);
  const [selectedProvider, setSelectedProvider] = useState<WaveLlmProvider>("openai");
  const [selectedMonitorId, setSelectedMonitorId] = useState<string | null>(null);
  const [claimSelections, setClaimSelections] = useState<Record<string, Record<number, string>>>({});
  const [defaultModel, setDefaultModel] = useState("local-fixture");
  const [defaultProvider, setDefaultProvider] = useState<WaveLlmProvider>("fixture");
  const [defaultAllowNetwork, setDefaultAllowNetwork] = useState(false);
  const [defaultRequestBudget, setDefaultRequestBudget] = useState("0");
  const [defaultMaxRetries, setDefaultMaxRetries] = useState("1");
  const [defaultTimeoutSeconds, setDefaultTimeoutSeconds] = useState("30");
  const [providerApiKey, setProviderApiKey] = useState("");
  const [providerClearApiKey, setProviderClearApiKey] = useState(false);
  const [providerBaseUrl, setProviderBaseUrl] = useState("");
  const [providerDefaultModel, setProviderDefaultModel] = useState("");
  const [providerAllowNetwork, setProviderAllowNetwork] = useState("");
  const [providerRequestBudget, setProviderRequestBudget] = useState("");
  const [providerMaxRetries, setProviderMaxRetries] = useState("");
  const [providerTimeoutSeconds, setProviderTimeoutSeconds] = useState("");
  const [monitorProvider, setMonitorProvider] = useState("");
  const [monitorModel, setMonitorModel] = useState("");
  const [monitorAllowNetwork, setMonitorAllowNetwork] = useState("");
  const [monitorRequestBudget, setMonitorRequestBudget] = useState("");
  const [monitorMaxRetries, setMonitorMaxRetries] = useState("");
  const [monitorTimeoutSeconds, setMonitorTimeoutSeconds] = useState("");
  const [feedback, setFeedback] = useState<string | null>(null);

  const runtimeStatusQuery = useSourceDiscoveryRuntimeStatusQuery();
  const runtimeServicesQuery = useSourceDiscoveryRuntimeServicesQuery();
  const waveLlmConfigQuery = useWaveLlmConfigQuery();
  const waveLlmExecutionHistoryQuery = useWaveLlmExecutionHistoryQuery({ limit: 8 });
  const waveOverviewQuery = useWaveMonitorOverviewQuery();
  const reviewQueueQuery = useSourceDiscoveryReviewQueueQuery({
    limit: 10,
    ownerLane: ownerLane.trim() || null
  });
  const waveReviewQueueQuery = useWaveLlmReviewQueueQuery({ limit: 8 });

  useEffect(() => {
    if (!selectedSourceId && reviewQueueQuery.data?.items[0]?.sourceId) {
      setSelectedSourceId(reviewQueueQuery.data.items[0].sourceId);
    }
  }, [reviewQueueQuery.data?.items, selectedSourceId]);

  useEffect(() => {
    if (!selectedReviewId && waveReviewQueueQuery.data?.items[0]?.review.reviewId) {
      setSelectedReviewId(waveReviewQueueQuery.data.items[0].review.reviewId);
    }
  }, [selectedReviewId, waveReviewQueueQuery.data?.items]);

  useEffect(() => {
    if (!selectedMonitorId && waveOverviewQuery.data?.monitors[0]?.monitorId) {
      setSelectedMonitorId(waveOverviewQuery.data.monitors[0].monitorId);
    }
  }, [selectedMonitorId, waveOverviewQuery.data?.monitors]);

  useEffect(() => {
    if (!waveLlmConfigQuery.data) {
      return;
    }
    const { defaults } = waveLlmConfigQuery.data;
    setDefaultProvider(defaults.defaultProvider);
    setDefaultModel(defaults.defaultModel);
    setDefaultAllowNetwork(defaults.allowNetworkDefault);
    setDefaultRequestBudget(String(defaults.requestBudgetDefault));
    setDefaultMaxRetries(String(defaults.maxRetriesDefault));
    setDefaultTimeoutSeconds(String(defaults.timeoutSecondsDefault));
  }, [waveLlmConfigQuery.data]);

  const selectedProviderConfig = useMemo(
    () =>
      waveLlmConfigQuery.data?.providers.find((provider) => provider.provider === selectedProvider) ??
      null,
    [selectedProvider, waveLlmConfigQuery.data?.providers]
  );

  useEffect(() => {
    if (!selectedProviderConfig) {
      return;
    }
    setProviderApiKey("");
    setProviderClearApiKey(false);
    setProviderBaseUrl(selectedProviderConfig.baseUrl ?? "");
    setProviderDefaultModel(selectedProviderConfig.defaultModel ?? "");
    setProviderAllowNetwork(
      selectedProviderConfig.allowNetworkDefault == null
        ? ""
        : selectedProviderConfig.allowNetworkDefault
          ? "true"
          : "false"
    );
    setProviderRequestBudget(
      selectedProviderConfig.requestBudgetDefault == null
        ? ""
        : String(selectedProviderConfig.requestBudgetDefault)
    );
    setProviderMaxRetries(
      selectedProviderConfig.maxRetriesDefault == null
        ? ""
        : String(selectedProviderConfig.maxRetriesDefault)
    );
    setProviderTimeoutSeconds(
      selectedProviderConfig.timeoutSecondsDefault == null
        ? ""
        : String(selectedProviderConfig.timeoutSecondsDefault)
    );
  }, [selectedProviderConfig]);

  const selectedMonitorPreference = useMemo(
    () =>
      waveLlmConfigQuery.data?.monitorPreferences.find(
        (preference) => preference.monitorId === selectedMonitorId
      ) ?? null,
    [selectedMonitorId, waveLlmConfigQuery.data?.monitorPreferences]
  );

  useEffect(() => {
    if (!selectedMonitorId) {
      return;
    }
    setMonitorProvider(selectedMonitorPreference?.provider ?? "");
    setMonitorModel(selectedMonitorPreference?.model ?? "");
    setMonitorAllowNetwork(
      selectedMonitorPreference?.allowNetwork == null
        ? ""
        : selectedMonitorPreference.allowNetwork
          ? "true"
          : "false"
    );
    setMonitorRequestBudget(
      selectedMonitorPreference?.requestBudget == null
        ? ""
        : String(selectedMonitorPreference.requestBudget)
    );
    setMonitorMaxRetries(
      selectedMonitorPreference?.maxRetries == null
        ? ""
        : String(selectedMonitorPreference.maxRetries)
    );
    setMonitorTimeoutSeconds(
      selectedMonitorPreference?.timeoutSeconds == null
        ? ""
        : String(selectedMonitorPreference.timeoutSeconds)
    );
  }, [selectedMonitorId, selectedMonitorPreference]);

  const selectedReviewItem = useMemo(
    () =>
      waveReviewQueueQuery.data?.items.find((item) => item.review.reviewId === selectedReviewId) ??
      null,
    [selectedReviewId, waveReviewQueueQuery.data?.items]
  );
  const memoryDetailQuery = useSourceDiscoveryMemoryDetailQuery(selectedSourceId, 12);

  const invalidateOpsQueries = async () => {
    await Promise.all([
      queryClient.invalidateQueries({ queryKey: ["source-discovery-runtime-status"] }),
      queryClient.invalidateQueries({ queryKey: ["source-discovery-runtime-services"] }),
      queryClient.invalidateQueries({ queryKey: ["source-discovery-review-queue"] }),
      queryClient.invalidateQueries({ queryKey: ["source-discovery-memory-detail"] }),
      queryClient.invalidateQueries({ queryKey: ["wave-llm-review-queue"] }),
      queryClient.invalidateQueries({ queryKey: ["wave-llm-config"] }),
      queryClient.invalidateQueries({ queryKey: ["wave-llm-executions"] }),
      queryClient.invalidateQueries({ queryKey: ["wave-monitor-overview-operator"] })
    ]);
  };

  const runtimeControlMutation = useMutation({
    mutationFn: ({
      workerName,
      action
    }: {
      workerName: "source_discovery" | "wave_monitor";
      action: "pause" | "resume" | "stop" | "run_now";
    }) =>
      postJson<SourceDiscoveryRuntimeControlResponse>(
        `/api/source-discovery/runtime/workers/${workerName}/control`,
        {
          action,
          requestedBy: operatorName,
          caveats: ["Requested from the single-page operator control surface."]
        }
      ),
    onSuccess: async (payload) => {
      setFeedback(`Worker ${payload.worker.workerName} -> ${payload.worker.desiredState}`);
      await invalidateOpsQueries();
    }
  });

  const runtimeServiceMutation = useMutation({
    mutationFn: ({
      workerName,
      action
    }: {
      workerName: "source_discovery" | "wave_monitor";
      action: SourceDiscoveryRuntimeServiceAction;
    }) =>
      postJson<SourceDiscoveryRuntimeServiceActionResponse>(
        `/api/source-discovery/runtime/services/${workerName}/actions`,
        {
          action,
          requestedBy: operatorName,
          dryRun: false,
          overwriteArtifact: action === "materialize" || action === "install",
          timeoutSeconds: 20,
          caveats: ["Requested from the single-page operator control surface."]
        }
      ),
    onSuccess: async (payload) => {
      setFeedback(
        `${payload.installation.serviceName} ${payload.action.action} -> ${payload.action.status}`
      );
      await invalidateOpsQueries();
    }
  });

  const reviewActionMutation = useMutation({
    mutationFn: ({
      sourceId,
      action
    }: {
      sourceId: string;
      action: SourceDiscoveryReviewAction;
    }) =>
      postJson<SourceDiscoveryReviewActionResponse>("/api/source-discovery/review/actions", {
        sourceId,
        action,
        reviewedBy: operatorName,
        reason: reviewReason,
        ownerLane: ownerLane.trim() || null
      }),
    onSuccess: async (payload) => {
      setFeedback(`${payload.memory.title} -> ${payload.action.action}`);
      await invalidateOpsQueries();
    }
  });

  const applyClaimsMutation = useMutation({
    mutationFn: (item: WaveLlmReviewQueueItem) => {
      const acceptedClaims = item.review.claims
        .map((claim, index) => ({ claim, index }))
        .filter(({ claim }) => claim.status === "accepted_for_review");
      return postJson<SourceDiscoveryReviewClaimApplicationResponse>(
        "/api/source-discovery/reviews/apply-claims",
        {
          reviewId: item.review.reviewId,
          sourceId: item.primarySourceId,
          approvedBy: operatorName,
          approvalReason,
          applications: acceptedClaims.map(({ index }) => ({
            claimIndex: index,
            outcome: claimSelections[item.review.reviewId]?.[index] ?? "confirmed"
          }))
        }
      );
    },
    onSuccess: async (payload) => {
      setFeedback(
        `Applied ${payload.applications.length} reviewed claim(s) to ${payload.memory.sourceId}.`
      );
      await invalidateOpsQueries();
    }
  });

  const waveDefaultsMutation = useMutation({
    mutationFn: () =>
      postJson<WaveLlmConfigResponse>("/api/tools/waves/llm/config/defaults", {
        defaultProvider,
        defaultModel,
        allowNetworkDefault: defaultAllowNetwork,
        requestBudgetDefault: Number(defaultRequestBudget || 0),
        maxRetriesDefault: Number(defaultMaxRetries || 0),
        timeoutSecondsDefault: Number(defaultTimeoutSeconds || 30)
      }),
    onSuccess: async (payload) => {
      setFeedback(`Saved global Wave LLM defaults to ${payload.defaults.defaultProvider}.`);
      await invalidateOpsQueries();
    }
  });

  const waveProviderConfigMutation = useMutation({
    mutationFn: () =>
      postJson<WaveLlmConfigResponse>(`/api/tools/waves/llm/config/providers/${selectedProvider}`, {
        apiKey: providerApiKey.trim() || null,
        clearApiKey: providerClearApiKey,
        baseUrl: providerBaseUrl.trim() || null,
        defaultModel: providerDefaultModel.trim() || null,
        allowNetworkDefault: parseOptionalBoolean(providerAllowNetwork),
        requestBudgetDefault: parseOptionalNumber(providerRequestBudget),
        maxRetriesDefault: parseOptionalNumber(providerMaxRetries),
        timeoutSecondsDefault: parseOptionalNumber(providerTimeoutSeconds)
      }),
    onSuccess: async () => {
      setFeedback(`Saved provider config for ${selectedProvider}.`);
      setProviderApiKey("");
      setProviderClearApiKey(false);
      await invalidateOpsQueries();
    }
  });

  const waveMonitorPreferenceMutation = useMutation({
    mutationFn: () => {
      if (!selectedMonitorId) {
        throw new Error("Select a wave before saving a wave-specific provider preference.");
      }
      return postJson<WaveLlmConfigResponse>(
        `/api/tools/waves/llm/config/monitors/${encodeURIComponent(selectedMonitorId)}`,
        {
          provider: monitorProvider || null,
          model: monitorModel.trim() || null,
          allowNetwork: parseOptionalBoolean(monitorAllowNetwork),
          requestBudget: parseOptionalNumber(monitorRequestBudget),
          maxRetries: parseOptionalNumber(monitorMaxRetries),
          timeoutSeconds: parseOptionalNumber(monitorTimeoutSeconds)
        }
      );
    },
    onSuccess: async () => {
      setFeedback(`Saved wave-specific provider preference for ${selectedMonitorId}.`);
      await invalidateOpsQueries();
    }
  });

  const runtimeStatus = runtimeStatusQuery.data;
  const runtimeServices = runtimeServicesQuery.data;

  return (
    <InspectorSection eyebrow="Platform Ops">
      <EvidenceCard
        compact
        className="operator-console-card"
        heading={<strong>Single-page operator console</strong>}
        badge={<StatusBadge tone="info">Phase 2 backend ops</StatusBadge>}
      >
        <span>
          This surface controls backend runtime workers, OS-managed service install state, Source
          Discovery review actions, Wave LLM provider management, and claim application without
          leaving the main page.
        </span>
        {feedback ? <span>{feedback}</span> : null}
      </EvidenceCard>

      <div className="operator-grid">
        <EvidenceCard compact className="operator-console-card" heading={<strong>Operator identity</strong>}>
          <label className="field-row">
            <span>Reviewed by</span>
            <input
              className="panel__input"
              value={operatorName}
              onChange={(event) => setOperatorName(event.currentTarget.value)}
            />
          </label>
          <label className="field-row">
            <span>Owner lane</span>
            <input
              className="panel__input"
              value={ownerLane}
              onChange={(event) => setOwnerLane(event.currentTarget.value)}
            />
          </label>
          <label className="field-row">
            <span>Review note</span>
            <textarea
              className="panel__input operator-console-textarea"
              value={reviewReason}
              onChange={(event) => setReviewReason(event.currentTarget.value)}
            />
          </label>
          <label className="field-row">
            <span>Claim approval note</span>
            <textarea
              className="panel__input operator-console-textarea"
              value={approvalReason}
              onChange={(event) => setApprovalReason(event.currentTarget.value)}
            />
          </label>
        </EvidenceCard>

        <EvidenceCard compact className="operator-console-card" heading={<strong>Runtime status</strong>}>
          {runtimeStatusQuery.isLoading ? (
            <EmptyState compact heading="Loading runtime status" variant="loading" />
          ) : runtimeStatus ? (
            <>
              <div className="operator-pill-row">
                <StatusBadge tone="info">{runtimeStatus.runtimeMode}</StatusBadge>
                <StatusBadge tone="available">
                  {runtimeStatus.recommendedRuntimeDeployment}
                </StatusBadge>
              </div>
              <span>{runtimeStatus.serviceWorkerEntrypoint}</span>
              <span>Service managers: {runtimeStatus.supportedServiceManagers.join(", ")}</span>
              <span>User data: {runtimeStatus.runtimePaths.userDataDir}</span>
              <span>Service artifacts: {runtimeStatus.runtimePaths.serviceArtifactDir}</span>
              {runtimeStatus.caveats.slice(0, 2).map((caveat) => (
                <span key={caveat}>{caveat}</span>
              ))}
            </>
          ) : (
            <EmptyState compact heading="Runtime status unavailable" variant="unavailable" />
          )}
        </EvidenceCard>
      </div>

      <EvidenceCard heading={<strong>Runtime workers</strong>} className="operator-console-card">
        {runtimeStatusQuery.isLoading ? (
          <EmptyState compact heading="Loading workers" variant="loading" />
        ) : (
          <div className="stack">
            {(runtimeStatus?.workers ?? []).map((worker) => (
              <div key={worker.workerName} className="data-card data-card--compact operator-subcard">
                <div className="operator-subcard__header">
                  <strong>{worker.workerName}</strong>
                  <StatusBadge tone={workerTone(worker.desiredState)}>{worker.desiredState}</StatusBadge>
                </div>
                <span>
                  Poll {worker.pollSeconds}s | last {formatDate(worker.lastTickFinishedAt)} | status{" "}
                  {worker.lastStatus ?? "unknown"}
                </span>
                <span>{worker.lastSummary ?? worker.lastError ?? "No scheduler summary yet."}</span>
                <div className="operator-action-row">
                  {worker.desiredState !== "running" ? (
                    <button
                      type="button"
                      className="ghost-button ghost-button--small"
                      onClick={() =>
                        runtimeControlMutation.mutate({
                          workerName: worker.workerName,
                          action: "resume"
                        })
                      }
                    >
                      Resume
                    </button>
                  ) : (
                    <button
                      type="button"
                      className="ghost-button ghost-button--small"
                      onClick={() =>
                        runtimeControlMutation.mutate({
                          workerName: worker.workerName,
                          action: "pause"
                        })
                      }
                    >
                      Pause
                    </button>
                  )}
                  <button
                    type="button"
                    className="ghost-button ghost-button--small"
                    onClick={() =>
                      runtimeControlMutation.mutate({
                        workerName: worker.workerName,
                        action: "run_now"
                      })
                    }
                  >
                    Run now
                  </button>
                  <button
                    type="button"
                    className="ghost-button ghost-button--small"
                    onClick={() =>
                      runtimeControlMutation.mutate({
                        workerName: worker.workerName,
                        action: "stop"
                      })
                    }
                  >
                    Stop
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </EvidenceCard>

      <EvidenceCard heading={<strong>Service install and lifecycle</strong>} className="operator-console-card">
        {runtimeServicesQuery.isLoading ? (
          <EmptyState compact heading="Loading service bundle" variant="loading" />
        ) : runtimeServices ? (
          <div className="stack">
            {runtimeServices.services.map((service) => {
              const installation = runtimeServices.installations.find(
                (item) => item.workerName === service.workerName
              );
              return (
                <div key={service.workerName} className="data-card data-card--compact operator-subcard">
                  <div className="operator-subcard__header">
                    <strong>{service.serviceName}</strong>
                    <StatusBadge tone={installTone(installation?.installState)}>
                      {installation?.installState ?? "planned"}
                    </StatusBadge>
                  </div>
                  <span>
                    {service.serviceManager} | platform {service.platform} | worker {service.workerName}
                  </span>
                  <span>Artifact: {service.artifactPath ?? service.artifactFileName}</span>
                  <span>Target: {service.targetPath ?? "task-scheduler entry only"}</span>
                  <span>
                    Last action: {installation?.lastAction ?? "none"} | {installation?.lastActionStatus ?? "n/a"}
                  </span>
                  {installation?.lastSummary ? <span>{installation.lastSummary}</span> : null}
                  <div className="operator-action-row">
                    {SERVICE_ACTIONS.map((action) => (
                      <button
                        key={`${service.workerName}-${action}`}
                        type="button"
                        className="ghost-button ghost-button--small"
                        onClick={() =>
                          runtimeServiceMutation.mutate({
                            workerName: service.workerName,
                            action
                          })
                        }
                      >
                        {serviceActionLabel(action)}
                      </button>
                    ))}
                  </div>
                  <CaveatBlock compact tone="source" heading="Install guidance">
                    {service.caveats.join(" ")}
                  </CaveatBlock>
                </div>
              );
            })}
          </div>
        ) : (
          <EmptyState compact heading="Service bundle unavailable" variant="unavailable" />
        )}
      </EvidenceCard>

      <div className="operator-grid">
        <EvidenceCard heading={<strong>Wave LLM defaults</strong>} className="operator-console-card">
          {waveLlmConfigQuery.isLoading ? (
            <EmptyState compact heading="Loading LLM defaults" variant="loading" />
          ) : (
            <>
              <label className="field-row">
                <span>Default provider</span>
                <select
                  className="panel__select"
                  value={defaultProvider}
                  onChange={(event) => setDefaultProvider(event.currentTarget.value as WaveLlmProvider)}
                >
                  {waveLlmConfigQuery.data?.providers.map((provider) => (
                    <option key={provider.provider} value={provider.provider}>
                      {provider.provider}
                    </option>
                  ))}
                </select>
              </label>
              <label className="field-row">
                <span>Default model</span>
                <input
                  className="panel__input"
                  value={defaultModel}
                  onChange={(event) => setDefaultModel(event.currentTarget.value)}
                />
              </label>
              <label className="field-row">
                <span>Allow network by default</span>
                <input
                  type="checkbox"
                  checked={defaultAllowNetwork}
                  onChange={(event) => setDefaultAllowNetwork(event.currentTarget.checked)}
                />
              </label>
              <label className="field-row">
                <span>Default request budget</span>
                <input
                  className="panel__input"
                  value={defaultRequestBudget}
                  onChange={(event) => setDefaultRequestBudget(event.currentTarget.value)}
                />
              </label>
              <label className="field-row">
                <span>Default max retries</span>
                <input
                  className="panel__input"
                  value={defaultMaxRetries}
                  onChange={(event) => setDefaultMaxRetries(event.currentTarget.value)}
                />
              </label>
              <label className="field-row">
                <span>Default timeout seconds</span>
                <input
                  className="panel__input"
                  value={defaultTimeoutSeconds}
                  onChange={(event) => setDefaultTimeoutSeconds(event.currentTarget.value)}
                />
              </label>
              <button type="button" className="ghost-button" onClick={() => waveDefaultsMutation.mutate()}>
                Save global defaults
              </button>
              <CaveatBlock compact tone="source" heading="Guardrail">
                Global defaults apply only when a wave-specific override or explicit task override is absent.
              </CaveatBlock>
            </>
          )}
        </EvidenceCard>

        <EvidenceCard heading={<strong>Provider config</strong>} className="operator-console-card">
          {waveLlmConfigQuery.isLoading ? (
            <EmptyState compact heading="Loading provider config" variant="loading" />
          ) : selectedProviderConfig ? (
            <>
              <label className="field-row">
                <span>Provider</span>
                <select
                  className="panel__select"
                  value={selectedProvider}
                  onChange={(event) => setSelectedProvider(event.currentTarget.value as WaveLlmProvider)}
                >
                  {waveLlmConfigQuery.data?.providers.map((provider) => (
                    <option key={provider.provider} value={provider.provider}>
                      {provider.provider}
                    </option>
                  ))}
                </select>
              </label>
              <div className="operator-pill-row">
                <StatusBadge tone={selectedProviderConfig.configured ? "available" : "warning"}>
                  {selectedProviderConfig.configured ? "configured" : "not configured"}
                </StatusBadge>
                <StatusBadge tone={selectedProviderConfig.adapterMode === "live" ? "available" : "info"}>
                  {selectedProviderConfig.adapterMode}
                </StatusBadge>
              </div>
              <span>Key source: {selectedProviderConfig.keySource}</span>
              {selectedProviderConfig.maskedSecret ? (
                <span>Saved secret: {selectedProviderConfig.maskedSecret}</span>
              ) : null}
              {selectedProviderConfig.supportsApiKey ? (
                <>
                  <label className="field-row">
                    <span>New API key</span>
                    <input
                      className="panel__input"
                      type="password"
                      value={providerApiKey}
                      onChange={(event) => setProviderApiKey(event.currentTarget.value)}
                    />
                  </label>
                  <label className="field-row">
                    <span>Clear saved key</span>
                    <input
                      type="checkbox"
                      checked={providerClearApiKey}
                      onChange={(event) => setProviderClearApiKey(event.currentTarget.checked)}
                    />
                  </label>
                </>
              ) : null}
              {selectedProviderConfig.supportsBaseUrl ? (
                <label className="field-row">
                  <span>Base URL</span>
                  <input
                    className="panel__input"
                    value={providerBaseUrl}
                    onChange={(event) => setProviderBaseUrl(event.currentTarget.value)}
                  />
                </label>
              ) : null}
              <label className="field-row">
                <span>Provider default model</span>
                <input
                  className="panel__input"
                  value={providerDefaultModel}
                  onChange={(event) => setProviderDefaultModel(event.currentTarget.value)}
                />
              </label>
              <label className="field-row">
                <span>Allow network default</span>
                <select
                  className="panel__select"
                  value={providerAllowNetwork}
                  onChange={(event) => setProviderAllowNetwork(event.currentTarget.value)}
                >
                  <option value="">inherit global</option>
                  <option value="true">true</option>
                  <option value="false">false</option>
                </select>
              </label>
              <label className="field-row">
                <span>Request budget default</span>
                <input
                  className="panel__input"
                  value={providerRequestBudget}
                  onChange={(event) => setProviderRequestBudget(event.currentTarget.value)}
                />
              </label>
              <label className="field-row">
                <span>Max retries default</span>
                <input
                  className="panel__input"
                  value={providerMaxRetries}
                  onChange={(event) => setProviderMaxRetries(event.currentTarget.value)}
                />
              </label>
              <label className="field-row">
                <span>Timeout seconds default</span>
                <input
                  className="panel__input"
                  value={providerTimeoutSeconds}
                  onChange={(event) => setProviderTimeoutSeconds(event.currentTarget.value)}
                />
              </label>
              <button
                type="button"
                className="ghost-button"
                onClick={() => waveProviderConfigMutation.mutate()}
              >
                Save provider config
              </button>
              <CaveatBlock compact tone="source" heading="Provider caveats">
                {selectedProviderConfig.caveats.join(" ")}
              </CaveatBlock>
            </>
          ) : (
            <EmptyState compact heading="No provider selected" />
          )}
        </EvidenceCard>
      </div>

      <div className="operator-grid">
        <EvidenceCard heading={<strong>Per-wave provider overrides</strong>} className="operator-console-card">
          {waveOverviewQuery.isLoading ? (
            <EmptyState compact heading="Loading waves" variant="loading" />
          ) : waveOverviewQuery.data?.monitors.length ? (
            <>
              <label className="field-row">
                <span>Wave</span>
                <select
                  className="panel__select"
                  value={selectedMonitorId ?? ""}
                  onChange={(event) => setSelectedMonitorId(event.currentTarget.value || null)}
                >
                  {waveOverviewQuery.data.monitors.map((monitor) => (
                    <option key={monitor.monitorId} value={monitor.monitorId}>
                      {monitor.title}
                    </option>
                  ))}
                </select>
              </label>
              <label className="field-row">
                <span>Provider override</span>
                <select
                  className="panel__select"
                  value={monitorProvider}
                  onChange={(event) => setMonitorProvider(event.currentTarget.value)}
                >
                  <option value="">inherit global/provider defaults</option>
                  {waveLlmConfigQuery.data?.providers.map((provider) => (
                    <option key={`${selectedMonitorId}-${provider.provider}`} value={provider.provider}>
                      {provider.provider}
                    </option>
                  ))}
                </select>
              </label>
              <label className="field-row">
                <span>Model override</span>
                <input
                  className="panel__input"
                  value={monitorModel}
                  onChange={(event) => setMonitorModel(event.currentTarget.value)}
                />
              </label>
              <label className="field-row">
                <span>Allow network</span>
                <select
                  className="panel__select"
                  value={monitorAllowNetwork}
                  onChange={(event) => setMonitorAllowNetwork(event.currentTarget.value)}
                >
                  <option value="">inherit</option>
                  <option value="true">true</option>
                  <option value="false">false</option>
                </select>
              </label>
              <label className="field-row">
                <span>Request budget</span>
                <input
                  className="panel__input"
                  value={monitorRequestBudget}
                  onChange={(event) => setMonitorRequestBudget(event.currentTarget.value)}
                />
              </label>
              <label className="field-row">
                <span>Max retries</span>
                <input
                  className="panel__input"
                  value={monitorMaxRetries}
                  onChange={(event) => setMonitorMaxRetries(event.currentTarget.value)}
                />
              </label>
              <label className="field-row">
                <span>Timeout seconds</span>
                <input
                  className="panel__input"
                  value={monitorTimeoutSeconds}
                  onChange={(event) => setMonitorTimeoutSeconds(event.currentTarget.value)}
                />
              </label>
              <button
                type="button"
                className="ghost-button"
                onClick={() => waveMonitorPreferenceMutation.mutate()}
              >
                Save wave override
              </button>
              {selectedMonitorPreference?.updatedAt ? (
                <span>Last updated: {formatDate(selectedMonitorPreference.updatedAt)}</span>
              ) : (
                <span>No wave-specific override saved yet.</span>
              )}
            </>
          ) : (
            <EmptyState compact heading="No waves available" />
          )}
        </EvidenceCard>

        <EvidenceCard heading={<strong>Recent provider executions</strong>} className="operator-console-card">
          {waveLlmExecutionHistoryQuery.isLoading ? (
            <EmptyState compact heading="Loading execution history" variant="loading" />
          ) : waveLlmExecutionHistoryQuery.data?.items.length ? (
            <div className="stack">
              {waveLlmExecutionHistoryQuery.data.items.map((item) => (
                <div key={item.executionId} className="data-card data-card--compact operator-subcard">
                  <div className="operator-subcard__header">
                    <strong>{item.provider}</strong>
                    <StatusBadge tone={executionTone(item)}>{item.status}</StatusBadge>
                  </div>
                  <span>
                    {item.taskType} | model {item.model} | requests {item.usedRequests}/{item.requestBudget}
                  </span>
                  <span>
                    {item.allowNetwork ? "network enabled" : "network disabled"} | timeout {item.timeoutSeconds}s | retry count {item.retryCount}
                  </span>
                  <span>{item.errorSummary ?? item.inputSummary}</span>
                </div>
              ))}
            </div>
          ) : (
            <EmptyState
              compact
              heading="No execution history yet"
              description="Blocked, failed, and completed Wave LLM executions will appear here."
            />
          )}
        </EvidenceCard>
      </div>

      <div className="operator-grid">
        <EvidenceCard heading={<strong>Source Discovery review queue</strong>} className="operator-console-card">
          {reviewQueueQuery.isLoading ? (
            <EmptyState compact heading="Loading review queue" variant="loading" />
          ) : reviewQueueQuery.data?.items.length ? (
            <div className="stack">
              {reviewQueueQuery.data.items.map((item) => (
                <button
                  key={item.sourceId}
                  type="button"
                  className={`ghost-button operator-queue-button${selectedSourceId === item.sourceId ? " operator-queue-button--selected" : ""}`}
                  onClick={() => setSelectedSourceId(item.sourceId)}
                >
                  <span>{item.title}</span>
                  <span>
                    {item.sourceClass} | {item.lifecycleState} | {item.sourceHealth}
                  </span>
                </button>
              ))}
            </div>
          ) : (
            <EmptyState
              compact
              heading="No Source Discovery review items"
              description="The queue is currently empty for the selected lane."
            />
          )}
        </EvidenceCard>

        <EvidenceCard heading={<strong>Selected source packet</strong>} className="operator-console-card">
          {memoryDetailQuery.isLoading ? (
            <EmptyState compact heading="Loading source detail" variant="loading" />
          ) : memoryDetailQuery.data ? (
            <>
              <div className="operator-subcard__header">
                <strong>{memoryDetailQuery.data.memory.title}</strong>
                <PriorityBadge
                  priority={
                    reviewQueueQuery.data?.items.find(
                      (item) => item.sourceId === memoryDetailQuery.data?.memory.sourceId
                    )?.priority ?? "low"
                  }
                />
              </div>
              <span>{memoryDetailQuery.data.memory.canonicalUrl}</span>
              <span>
                Reputation {memoryDetailQuery.data.memory.globalReputationScore.toFixed(2)} | next
                check {formatDate(memoryDetailQuery.data.memory.nextCheckAt)}
              </span>
              <span>
                Snapshots {memoryDetailQuery.data.snapshots.length} | review actions{" "}
                {memoryDetailQuery.data.reviewActions.length} | claim outcomes{" "}
                {memoryDetailQuery.data.claimOutcomes.length}
              </span>
              <div className="operator-action-row">
                {REVIEW_ACTIONS.map((action) => (
                  <button
                    key={action}
                    type="button"
                    className="ghost-button ghost-button--small"
                    onClick={() =>
                      reviewActionMutation.mutate({
                        sourceId: memoryDetailQuery.data.memory.sourceId,
                        action
                      })
                    }
                  >
                    {reviewActionLabel(action)}
                  </button>
                ))}
              </div>
              <div className="stack">
                {memoryDetailQuery.data.memory.caveats.slice(0, 3).map((caveat) => (
                  <span key={caveat}>{caveat}</span>
                ))}
              </div>
            </>
          ) : (
            <EmptyState
              compact
              heading="Select a source"
              description="Choose a queue item to inspect its source-memory packet."
            />
          )}
        </EvidenceCard>
      </div>

      <EvidenceCard heading={<strong>Wave LLM review packets</strong>} className="operator-console-card">
        {waveReviewQueueQuery.isLoading ? (
          <EmptyState compact heading="Loading review packets" variant="loading" />
        ) : waveReviewQueueQuery.data?.items.length ? (
          <div className="operator-grid">
            <div className="stack">
              {waveReviewQueueQuery.data.items.map((item) => (
                <button
                  key={item.review.reviewId}
                  type="button"
                  className={`ghost-button operator-queue-button${selectedReviewId === item.review.reviewId ? " operator-queue-button--selected" : ""}`}
                  onClick={() => setSelectedReviewId(item.review.reviewId)}
                >
                  <span>{item.task.taskType}</span>
                  <span>
                    {item.review.validationState} | accepted {item.review.acceptedClaimCount}
                  </span>
                </button>
              ))}
            </div>
            <div className="stack">
              {selectedReviewItem ? (
                <>
                  <div className="operator-subcard__header">
                    <strong>{selectedReviewItem.task.taskType}</strong>
                    <StatusBadge tone="warning">{selectedReviewItem.review.validationState}</StatusBadge>
                  </div>
                  <span>Source ids: {selectedReviewItem.sourceIds.join(", ") || "none"}</span>
                  <span>Provider: {selectedReviewItem.review.provider} | model {selectedReviewItem.review.model}</span>
                  <div className="stack">
                    {selectedReviewItem.review.claims.map((claim, index) => (
                      <div key={`${selectedReviewItem.review.reviewId}-${index}`} className="data-card data-card--compact operator-subcard">
                        <div className="operator-subcard__header">
                          <strong>{claim.claimType}</strong>
                          <StatusBadge tone={claim.status === "accepted_for_review" ? "available" : "danger"}>
                            {claim.status}
                          </StatusBadge>
                        </div>
                        <span>{claim.claimText}</span>
                        <span>
                          {claim.evidenceBasis} | confidence {claim.confidence.toFixed(2)}
                        </span>
                        {claim.status === "accepted_for_review" ? (
                          <label className="field-row">
                            <span>Outcome</span>
                            <select
                              className="panel__select"
                              value={claimSelections[selectedReviewItem.review.reviewId]?.[index] ?? "confirmed"}
                              onChange={(event) =>
                                setClaimSelections((current) => ({
                                  ...current,
                                  [selectedReviewItem.review.reviewId]: {
                                    ...(current[selectedReviewItem.review.reviewId] ?? {}),
                                    [index]: event.currentTarget.value
                                  }
                                }))
                              }
                            >
                              <option value="confirmed">confirmed</option>
                              <option value="contradicted">contradicted</option>
                              <option value="corrected">corrected</option>
                              <option value="outdated">outdated</option>
                              <option value="unresolved">unresolved</option>
                              <option value="not_applicable">not_applicable</option>
                            </select>
                          </label>
                        ) : claim.rejectionReason ? (
                          <span>{claim.rejectionReason}</span>
                        ) : null}
                      </div>
                    ))}
                  </div>
                  <button
                    type="button"
                    className="ghost-button"
                    disabled={
                      !selectedReviewItem.primarySourceId ||
                      selectedReviewItem.review.acceptedClaimCount === 0
                    }
                    onClick={() => applyClaimsMutation.mutate(selectedReviewItem)}
                  >
                    Apply accepted claims
                  </button>
                  {!selectedReviewItem.primarySourceId ? (
                    <CaveatBlock compact tone="warning" heading="Application blocked">
                      This review packet references multiple or zero source ids, so the UI cannot
                      safely auto-apply it without a more specific source target.
                    </CaveatBlock>
                  ) : null}
                </>
              ) : (
                <EmptyState compact heading="Select a review packet" />
              )}
            </div>
          </div>
        ) : (
          <EmptyState
            compact
            heading="No pending Wave LLM review packets"
            description="Scheduler-created interpretation work will appear here once it produces reviewed packets."
          />
        )}
      </EvidenceCard>

      {runtimeControlMutation.error instanceof Error ? (
        <CaveatBlock heading="Worker control error" tone="danger">
          {runtimeControlMutation.error.message}
        </CaveatBlock>
      ) : null}
      {runtimeServiceMutation.error instanceof Error ? (
        <CaveatBlock heading="Service action error" tone="danger">
          {runtimeServiceMutation.error.message}
        </CaveatBlock>
      ) : null}
      {reviewActionMutation.error instanceof Error ? (
        <CaveatBlock heading="Review action error" tone="danger">
          {reviewActionMutation.error.message}
        </CaveatBlock>
      ) : null}
      {applyClaimsMutation.error instanceof Error ? (
        <CaveatBlock heading="Claim application error" tone="danger">
          {applyClaimsMutation.error.message}
        </CaveatBlock>
      ) : null}
      {waveDefaultsMutation.error instanceof Error ? (
        <CaveatBlock heading="LLM defaults error" tone="danger">
          {waveDefaultsMutation.error.message}
        </CaveatBlock>
      ) : null}
      {waveProviderConfigMutation.error instanceof Error ? (
        <CaveatBlock heading="Provider config error" tone="danger">
          {waveProviderConfigMutation.error.message}
        </CaveatBlock>
      ) : null}
      {waveMonitorPreferenceMutation.error instanceof Error ? (
        <CaveatBlock heading="Wave override error" tone="danger">
          {waveMonitorPreferenceMutation.error.message}
        </CaveatBlock>
      ) : null}
    </InspectorSection>
  );
}

function reviewActionLabel(action: SourceDiscoveryReviewAction) {
  return action.replaceAll("_", " ");
}

function serviceActionLabel(action: SourceDiscoveryRuntimeServiceAction) {
  return action.replaceAll("_", " ");
}

function workerTone(state: SourceDiscoveryRuntimeStatusResponse["workers"][number]["desiredState"]) {
  if (state === "running") {
    return "available";
  }
  if (state === "paused") {
    return "warning";
  }
  return "danger";
}

function installTone(state?: string | null) {
  if (state === "running" || state === "installed") {
    return "available";
  }
  if (state === "materialized" || state === "stopped") {
    return "warning";
  }
  if (state === "error") {
    return "danger";
  }
  return "info";
}

function executionTone(item: WaveLlmExecutionHistoryItem) {
  if (item.status === "completed") {
    return "available";
  }
  if (item.status === "blocked") {
    return "warning";
  }
  return "danger";
}

function parseOptionalBoolean(value: string) {
  if (value === "true") {
    return true;
  }
  if (value === "false") {
    return false;
  }
  return null;
}

function parseOptionalNumber(value: string) {
  if (!value.trim()) {
    return null;
  }
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : null;
}

function formatDate(value?: string | null) {
  if (!value) {
    return "n/a";
  }
  return new Date(value).toLocaleString();
}
