import { FormEvent, useCallback, useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";

import {
  approveDiscoveredSource,
  checkWaveDiscoveredSources,
  createDomainTrustProfile,
  createWaveTrustOverride,
  deleteConnector,
  deleteDomainTrustProfile,
  deleteWaveTrustOverride,
  discoverSources,
  getWave,
  ingestSample,
  listDomainTrustProfiles,
  listDiscoveredSources,
  listWavePolicyActions,
  listWaveTrustOverrides,
  listSourceChecks,
  reevaluateDiscoveredSourceLifecycle,
  reevaluateWaveSources,
  listConnectors,
  listRecords,
  listWaveRuns,
  listWaveSignals,
  runSourceCheck,
  triggerSchedulerTick,
  updateConnector,
  updateDomainTrustProfile,
  updateWaveTrustOverride,
  updateSignalStatus,
  updateDiscoveredSourceStatus,
  createConnector,
} from "../api/waves";
import { createConnectorPayload, getConnectorFormSpec, listConnectorFormSpecs, summarizeConnectorConfig } from "../features/connectors/connectorFormRegistry";
import type { ConnectorConfigDraft } from "../features/connectors/forms/types";
import type {
  Connector,
  DomainApprovalPolicy,
  DomainTrustLevel,
  DomainTrustProfile,
  PolicyActionLog,
  DiscoveredSource,
  DiscoveredSourceStatus,
  DiscoveredSourceFilters,
  RecordFilters,
  RunHistoryEntry,
  SignalFilters,
  SignalItem,
  SourceCheck,
  SourceCheckFilters,
  WaveTrustOverride,
  Wave,
  WaveRecord,
} from "../types/domain";

function prettyDate(value: string | null) {
  if (!value) {
    return "-";
  }
  return new Date(value).toLocaleString();
}

function connectorHealth(connector: Connector): "paused" | "healthy" | "error" | "idle" {
  if (!connector.enabled) {
    return "paused";
  }
  if (
    connector.last_error_at &&
    (!connector.last_success_at || connector.last_error_at > connector.last_success_at)
  ) {
    return "error";
  }
  if (connector.last_success_at) {
    return "healthy";
  }
  return "idle";
}

function severityClass(severity: SignalItem["severity"]): string {
  if (severity === "high") {
    return "signal-high";
  }
  if (severity === "medium") {
    return "signal-medium";
  }
  return "signal-low";
}

function discoveredStatusClass(status: DiscoveredSourceStatus): string {
  if (status === "approved") {
    return "healthy";
  }
  if (status === "sandboxed") {
    return "active";
  }
  if (status === "degraded") {
    return "signal-medium";
  }
  if (status === "rejected") {
    return "error";
  }
  if (status === "ignored" || status === "archived") {
    return "archived";
  }
  return "idle";
}

function trustTierClass(tier: DiscoveredSource["trust_tier"]): string {
  if (tier === "tier_1" || tier === "tier_2") {
    return "healthy";
  }
  if (tier === "tier_3") {
    return "active";
  }
  if (tier === "tier_5") {
    return "error";
  }
  return "idle";
}

function checkStatusClass(status: SourceCheck["status"]): string {
  if (status === "success") {
    return "healthy";
  }
  if (status === "failed") {
    return "error";
  }
  return "idle";
}

function trustClass(level: DomainTrustLevel): string {
  if (level === "trusted") {
    return "healthy";
  }
  if (level === "blocked") {
    return "error";
  }
  return "idle";
}

function policyStateClass(state: DiscoveredSource["policy_state"]): string {
  if (state === "blocked") {
    return "error";
  }
  if (state === "auto_approved") {
    return "healthy";
  }
  if (state === "auto_approvable") {
    return "active";
  }
  if (state === "ineligible") {
    return "archived";
  }
  return "idle";
}

function policySourceLabel(source: DiscoveredSource["policy_source"]): string {
  if (source === "wave_override") {
    return "Wave Override";
  }
  if (source === "global_domain_trust") {
    return "Global Domain Trust";
  }
  return "Default Policy";
}

type ConnectorFormState = {
  type: string;
  name: string;
  enabled: boolean;
  polling_interval_minutes: number;
  draft: ConnectorConfigDraft;
};

type RecordFilterDraft = {
  text_search: string;
  connector_id: string;
  source_type: string;
  has_coordinates: "any" | "yes" | "no";
  sort: "newest" | "oldest";
};

type SignalFilterDraft = {
  severity: "" | "low" | "medium" | "high";
  status: "" | "new" | "acknowledged" | "resolved";
  signal_type: string;
  sort: "newest" | "oldest";
};

type SourceFilterDraft = {
  status: "" | "candidate" | "sandboxed" | "approved" | "degraded" | "rejected" | "archived" | "ignored";
  source_type: string;
  min_relevance_score: string;
  min_stability_score: string;
  parent_domain: string;
  sort:
    | "newest"
    | "oldest"
    | "relevance_desc"
    | "relevance_asc"
    | "stability_desc"
    | "stability_asc";
};

type CheckFilterDraft = {
  status: "" | "success" | "failed" | "skipped";
  reachable: "any" | "yes" | "no";
  parseable: "any" | "yes" | "no";
  content_type: string;
  sort: "newest" | "oldest";
};

type DomainTrustFormState = {
  id: number | null;
  domain: string;
  trust_level: DomainTrustLevel;
  approval_policy: DomainApprovalPolicy;
  notes: string;
};

type WaveTrustOverrideFormState = {
  id: number | null;
  domain: string;
  trust_level: DomainTrustLevel | "";
  approval_policy: DomainApprovalPolicy | "";
  notes: string;
};

function createDefaultConnectorForm(type = "sample_news"): ConnectorFormState {
  const spec = getConnectorFormSpec(type) ?? listConnectorFormSpecs()[0];
  return {
    type: spec.type,
    name: spec.defaultName,
    enabled: true,
    polling_interval_minutes: 15,
    draft: spec.createDefaultDraft(),
  };
}

function toOptionalNumber(value: string): number | undefined {
  const trimmed = value.trim();
  if (!trimmed) {
    return undefined;
  }
  const parsed = Number(trimmed);
  return Number.isFinite(parsed) ? parsed : undefined;
}

export function WaveDetailPage() {
  const { waveId } = useParams();
  const parsedWaveId = useMemo(() => Number(waveId), [waveId]);

  const [wave, setWave] = useState<Wave | null>(null);
  const [connectors, setConnectors] = useState<Connector[]>([]);
  const [records, setRecords] = useState<WaveRecord[]>([]);
  const [runHistory, setRunHistory] = useState<RunHistoryEntry[]>([]);
  const [signals, setSignals] = useState<SignalItem[]>([]);
  const [discoveredSources, setDiscoveredSources] = useState<DiscoveredSource[]>([]);
  const [domainTrustProfiles, setDomainTrustProfiles] = useState<DomainTrustProfile[]>([]);
  const [waveTrustOverrides, setWaveTrustOverrides] = useState<WaveTrustOverride[]>([]);
  const [policyActions, setPolicyActions] = useState<PolicyActionLog[]>([]);
  const [sourceChecksBySource, setSourceChecksBySource] = useState<
    Record<number, SourceCheck[]>
  >({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [ingestMessage, setIngestMessage] = useState<string | null>(null);
  const [tickMessage, setTickMessage] = useState<string | null>(null);
  const [discoveryMessage, setDiscoveryMessage] = useState<string | null>(null);
  const [sourceCheckMessage, setSourceCheckMessage] = useState<string | null>(null);
  const [trustMessage, setTrustMessage] = useState<string | null>(null);
  const [waveOverrideMessage, setWaveOverrideMessage] = useState<string | null>(null);
  const [seedUrlsText, setSeedUrlsText] = useState("");
  const [domainTrustForm, setDomainTrustForm] = useState<DomainTrustFormState>({
    id: null,
    domain: "",
    trust_level: "neutral",
    approval_policy: "manual_review",
    notes: "",
  });
  const [waveTrustOverrideForm, setWaveTrustOverrideForm] = useState<WaveTrustOverrideFormState>({
    id: null,
    domain: "",
    trust_level: "",
    approval_policy: "",
    notes: "",
  });
  const [connectorForm, setConnectorForm] = useState<ConnectorFormState>(() =>
    createDefaultConnectorForm()
  );
  const [recordFilters, setRecordFilters] = useState<RecordFilterDraft>({
    text_search: "",
    connector_id: "",
    source_type: "",
    has_coordinates: "any",
    sort: "newest",
  });
  const [signalFilters, setSignalFilters] = useState<SignalFilterDraft>({
    severity: "",
    status: "",
    signal_type: "",
    sort: "newest",
  });
  const [sourceFilters, setSourceFilters] = useState<SourceFilterDraft>({
    status: "",
    source_type: "",
    min_relevance_score: "",
    min_stability_score: "",
    parent_domain: "",
    sort: "relevance_desc",
  });
  const [checkFilters, setCheckFilters] = useState<CheckFilterDraft>({
    status: "",
    reachable: "any",
    parseable: "any",
    content_type: "",
    sort: "newest",
  });

  const currentConnectorSpec = getConnectorFormSpec(connectorForm.type);

  const recordApiFilters = useMemo<RecordFilters>(
    () => ({
      text_search: recordFilters.text_search || undefined,
      connector_id: toOptionalNumber(recordFilters.connector_id),
      source_type: recordFilters.source_type || undefined,
      has_coordinates:
        recordFilters.has_coordinates === "yes"
          ? true
          : recordFilters.has_coordinates === "no"
            ? false
            : undefined,
      sort: recordFilters.sort,
    }),
    [recordFilters]
  );
  const signalApiFilters = useMemo<SignalFilters>(
    () => ({
      severity: signalFilters.severity || undefined,
      status: signalFilters.status || undefined,
      signal_type: signalFilters.signal_type || undefined,
      sort: signalFilters.sort,
      limit: 50,
    }),
    [signalFilters]
  );
  const discoveredApiFilters = useMemo<DiscoveredSourceFilters>(
    () => ({
      status: sourceFilters.status || undefined,
      source_type: sourceFilters.source_type || undefined,
      min_relevance_score: toOptionalNumber(sourceFilters.min_relevance_score),
      min_stability_score: toOptionalNumber(sourceFilters.min_stability_score),
      parent_domain: sourceFilters.parent_domain || undefined,
      sort: sourceFilters.sort,
      limit: 100,
    }),
    [sourceFilters]
  );
  const sourceCheckApiFilters = useMemo<SourceCheckFilters>(
    () => ({
      status: checkFilters.status || undefined,
      reachable:
        checkFilters.reachable === "yes"
          ? true
          : checkFilters.reachable === "no"
            ? false
            : undefined,
      parseable:
        checkFilters.parseable === "yes"
          ? true
          : checkFilters.parseable === "no"
            ? false
            : undefined,
      content_type: checkFilters.content_type || undefined,
      sort: checkFilters.sort,
      limit: 5,
    }),
    [checkFilters]
  );

  const recordFilterActive = [
    recordFilters.text_search ? `text:${recordFilters.text_search}` : "",
    recordFilters.connector_id ? `connector:${recordFilters.connector_id}` : "",
    recordFilters.source_type ? `source:${recordFilters.source_type}` : "",
    recordFilters.has_coordinates !== "any" ? `coords:${recordFilters.has_coordinates}` : "",
    recordFilters.sort !== "newest" ? `sort:${recordFilters.sort}` : "",
  ]
    .filter(Boolean)
    .join(" | ");

  const signalFilterActive = [
    signalFilters.severity ? `severity:${signalFilters.severity}` : "",
    signalFilters.status ? `status:${signalFilters.status}` : "",
    signalFilters.signal_type ? `type:${signalFilters.signal_type}` : "",
    signalFilters.sort !== "newest" ? `sort:${signalFilters.sort}` : "",
  ]
    .filter(Boolean)
    .join(" | ");

  const sourceFilterActive = [
    sourceFilters.status ? `status:${sourceFilters.status}` : "",
    sourceFilters.source_type ? `type:${sourceFilters.source_type}` : "",
    sourceFilters.min_relevance_score ? `min relevance:${sourceFilters.min_relevance_score}` : "",
    sourceFilters.min_stability_score ? `min stability:${sourceFilters.min_stability_score}` : "",
    sourceFilters.parent_domain ? `domain:${sourceFilters.parent_domain}` : "",
    sourceFilters.sort !== "relevance_desc" ? `sort:${sourceFilters.sort}` : "",
  ]
    .filter(Boolean)
    .join(" | ");

  const checkFilterActive = [
    checkFilters.status ? `status:${checkFilters.status}` : "",
    checkFilters.reachable !== "any" ? `reachable:${checkFilters.reachable}` : "",
    checkFilters.parseable !== "any" ? `parseable:${checkFilters.parseable}` : "",
    checkFilters.content_type ? `type:${checkFilters.content_type}` : "",
    checkFilters.sort !== "newest" ? `sort:${checkFilters.sort}` : "",
  ]
    .filter(Boolean)
    .join(" | ");

  const loadAll = useCallback(async () => {
    if (!Number.isFinite(parsedWaveId) || parsedWaveId <= 0) {
      setError("Invalid wave id");
      setLoading(false);
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const [
        waveData,
        connectorsData,
        recordsData,
        runData,
        signalData,
        discoveredData,
        trustProfiles,
        overrideRows,
        policyActionRows,
      ] =
        await Promise.all([
          getWave(parsedWaveId),
          listConnectors(parsedWaveId),
          listRecords(parsedWaveId, recordApiFilters),
          listWaveRuns(parsedWaveId, 20),
          listWaveSignals(parsedWaveId, signalApiFilters),
          listDiscoveredSources(parsedWaveId, discoveredApiFilters),
          listDomainTrustProfiles(),
          listWaveTrustOverrides(parsedWaveId),
          listWavePolicyActions(parsedWaveId, 100),
        ]);
      setWave(waveData);
      setConnectors(connectorsData);
      setRecords(recordsData);
      setRunHistory(runData);
      setSignals(signalData);
      setDiscoveredSources(discoveredData);
      setDomainTrustProfiles(trustProfiles);
      setWaveTrustOverrides(overrideRows);
      setPolicyActions(policyActionRows);
      setSourceChecksBySource({});
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load wave details");
    } finally {
      setLoading(false);
    }
  }, [discoveredApiFilters, parsedWaveId, recordApiFilters, signalApiFilters]);

  useEffect(() => {
    void loadAll();
  }, [loadAll]);

  async function onConnectorCreate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!Number.isFinite(parsedWaveId) || parsedWaveId <= 0) {
      return;
    }

    setError(null);
    try {
      const pollingInterval =
        Number.isFinite(connectorForm.polling_interval_minutes) &&
        connectorForm.polling_interval_minutes > 0
          ? connectorForm.polling_interval_minutes
          : 15;
      const payload = createConnectorPayload({
        type: connectorForm.type,
        name: connectorForm.name,
        enabled: connectorForm.enabled,
        polling_interval_minutes: pollingInterval,
        draft: connectorForm.draft,
      });
      await createConnector(parsedWaveId, payload);
      setConnectorForm(createDefaultConnectorForm(connectorForm.type));
      await loadAll();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create connector");
    }
  }

  async function onToggleConnector(connector: Connector) {
    try {
      await updateConnector(connector.id, { enabled: !connector.enabled });
      await loadAll();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to toggle connector");
    }
  }

  async function onDeleteConnector(connectorId: number) {
    try {
      await deleteConnector(connectorId);
      await loadAll();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete connector");
    }
  }

  async function onIngest() {
    if (!Number.isFinite(parsedWaveId) || parsedWaveId <= 0) {
      return;
    }
    setIngestMessage(null);
    setTickMessage(null);
    setDiscoveryMessage(null);
    setSourceCheckMessage(null);
    setTrustMessage(null);
    setWaveOverrideMessage(null);
    setError(null);
    try {
      const result = await ingestSample(parsedWaveId);
      setIngestMessage(
        `Ingested ${result.ingested_count} record(s). Success ${result.successful_runs}, failed ${result.failed_runs}.`
      );
      await loadAll();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to run sample ingest");
    }
  }

  async function onSchedulerTick() {
    setError(null);
    setIngestMessage(null);
    setTickMessage(null);
    setDiscoveryMessage(null);
    setSourceCheckMessage(null);
    setTrustMessage(null);
    setWaveOverrideMessage(null);
    try {
      const result = await triggerSchedulerTick();
      setTickMessage(
        `Scheduler tick: connectors scanned ${result.scanned_connectors}, eligible ${result.eligible_connectors}, success ${result.successful_runs}, failed ${result.failed_runs}; sources scanned ${result.scanned_sources}, eligible ${result.eligible_sources}, check success ${result.successful_source_checks}, check failed ${result.failed_source_checks}, check skipped ${result.skipped_source_checks}.`
      );
      await loadAll();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to run scheduler tick");
    }
  }

  async function onSignalStatusChange(signalId: number, status: "acknowledged" | "resolved") {
    try {
      await updateSignalStatus(signalId, status);
      await loadAll();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update signal");
    }
  }

  async function onRunDiscovery() {
    if (!Number.isFinite(parsedWaveId) || parsedWaveId <= 0) {
      return;
    }
    setError(null);
    setIngestMessage(null);
    setTickMessage(null);
    setDiscoveryMessage(null);
    setSourceCheckMessage(null);
    setTrustMessage(null);
    setWaveOverrideMessage(null);
    const seedUrls = seedUrlsText
      .split(/[\n,]+/)
      .map((item) => item.trim())
      .filter((item) => item.length > 0);
    try {
      const result = await discoverSources(parsedWaveId, seedUrls);
      setDiscoveryMessage(
        `Discovery found ${result.discovered_count} new source(s); deduped ${result.deduped_count}.`
      );
      await loadAll();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to run discovery");
    }
  }

  async function onDiscoveredSourceStatusChange(
    sourceId: number,
    status: DiscoveredSourceStatus
  ) {
    try {
      await updateDiscoveredSourceStatus(sourceId, status);
      await loadAll();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update discovered source");
    }
  }

  async function onApproveDiscoveredSource(sourceId: number) {
    try {
      await approveDiscoveredSource(sourceId);
      await loadAll();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to approve discovered source");
    }
  }

  async function onRunSourceCheck(sourceId: number) {
    try {
      await runSourceCheck(sourceId);
      setSourceCheckMessage("Source check completed.");
      await loadAll();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to run source check");
    }
  }

  async function onRunBatchSourceChecks() {
    if (!Number.isFinite(parsedWaveId) || parsedWaveId <= 0) {
      return;
    }
    try {
      const result = await checkWaveDiscoveredSources(parsedWaveId, 100);
      setSourceCheckMessage(
        `Checked ${result.checked_count} source(s): success ${result.success_count}, failed ${result.failed_count}, skipped ${result.skipped_count}.`
      );
      await loadAll();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to check discovered sources");
    }
  }

  async function onReevaluateSourceLifecycle(sourceId: number) {
    try {
      await reevaluateDiscoveredSourceLifecycle(sourceId);
      setSourceCheckMessage("Source lifecycle reevaluated.");
      await loadAll();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to reevaluate source lifecycle");
    }
  }

  async function onReevaluateWaveSources() {
    if (!Number.isFinite(parsedWaveId) || parsedWaveId <= 0) {
      return;
    }
    try {
      const result = await reevaluateWaveSources(parsedWaveId);
      setSourceCheckMessage(
        `Lifecycle reevaluation: evaluated ${result.evaluated_count}, changed ${result.changed_count}.`
      );
      await loadAll();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to reevaluate source lifecycle");
    }
  }

  async function onSaveDomainTrust(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    try {
      if (domainTrustForm.id) {
        await updateDomainTrustProfile(domainTrustForm.id, {
          trust_level: domainTrustForm.trust_level,
          approval_policy: domainTrustForm.approval_policy,
          notes: domainTrustForm.notes || null,
        });
        setTrustMessage(`Updated trust profile for ${domainTrustForm.domain}.`);
      } else {
        await createDomainTrustProfile({
          domain: domainTrustForm.domain,
          trust_level: domainTrustForm.trust_level,
          approval_policy: domainTrustForm.approval_policy,
          notes: domainTrustForm.notes || null,
        });
        setTrustMessage(`Created trust profile for ${domainTrustForm.domain}.`);
      }
      setDomainTrustForm({
        id: null,
        domain: "",
        trust_level: "neutral",
        approval_policy: "manual_review",
        notes: "",
      });
      await loadAll();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save domain trust profile");
    }
  }

  function onEditDomainTrust(profile: DomainTrustProfile) {
    setDomainTrustForm({
      id: profile.id,
      domain: profile.domain,
      trust_level: profile.trust_level,
      approval_policy: profile.approval_policy,
      notes: profile.notes || "",
    });
  }

  async function onDeleteDomainTrust(profileId: number) {
    try {
      await deleteDomainTrustProfile(profileId);
      setTrustMessage("Deleted domain trust profile.");
      if (domainTrustForm.id === profileId) {
        setDomainTrustForm({
          id: null,
          domain: "",
          trust_level: "neutral",
          approval_policy: "manual_review",
          notes: "",
        });
      }
      await loadAll();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete domain trust profile");
    }
  }

  function onEditWaveTrustOverride(override: WaveTrustOverride) {
    setWaveTrustOverrideForm({
      id: override.id,
      domain: override.domain,
      trust_level: override.trust_level || "",
      approval_policy: override.approval_policy || "",
      notes: override.notes || "",
    });
  }

  async function onSaveWaveTrustOverride(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!Number.isFinite(parsedWaveId) || parsedWaveId <= 0) {
      return;
    }
    if (!waveTrustOverrideForm.domain.trim()) {
      return;
    }
    if (!waveTrustOverrideForm.trust_level && !waveTrustOverrideForm.approval_policy) {
      setError("Select a trust level or approval policy for the override.");
      return;
    }

    try {
      if (waveTrustOverrideForm.id) {
        await updateWaveTrustOverride(waveTrustOverrideForm.id, {
          trust_level: waveTrustOverrideForm.trust_level || null,
          approval_policy: waveTrustOverrideForm.approval_policy || null,
          notes: waveTrustOverrideForm.notes || null,
        });
        setWaveOverrideMessage(`Updated wave override for ${waveTrustOverrideForm.domain}.`);
      } else {
        await createWaveTrustOverride(parsedWaveId, {
          domain: waveTrustOverrideForm.domain,
          trust_level: waveTrustOverrideForm.trust_level || null,
          approval_policy: waveTrustOverrideForm.approval_policy || null,
          notes: waveTrustOverrideForm.notes || null,
        });
        setWaveOverrideMessage(`Created wave override for ${waveTrustOverrideForm.domain}.`);
      }
      setWaveTrustOverrideForm({
        id: null,
        domain: "",
        trust_level: "",
        approval_policy: "",
        notes: "",
      });
      await loadAll();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save wave trust override");
    }
  }

  async function onDeleteWaveTrustOverride(overrideId: number) {
    try {
      await deleteWaveTrustOverride(overrideId);
      setWaveOverrideMessage("Deleted wave override.");
      if (waveTrustOverrideForm.id === overrideId) {
        setWaveTrustOverrideForm({
          id: null,
          domain: "",
          trust_level: "",
          approval_policy: "",
          notes: "",
        });
      }
      await loadAll();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete wave trust override");
    }
  }

  async function onLoadSourceChecks(sourceId: number) {
    try {
      const checks = await listSourceChecks(sourceId, sourceCheckApiFilters);
      setSourceChecksBySource((prev) => ({ ...prev, [sourceId]: checks }));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load source check history");
    }
  }

  if (loading) {
    return <p className="panel">Loading wave...</p>;
  }

  if (!wave) {
    return (
      <section className="panel">
        <p>Wave not found.</p>
        <Link className="text-link" to="/">
          Back to Waves
        </Link>
      </section>
    );
  }

  return (
    <section className="stack">
      <Link className="text-link text-link--back" to="/">
        Back to Waves
      </Link>
      {error ? <p className="notice notice--error">{error}</p> : null}
      <div className="hero-panel hero-panel--compact">
        <div className="between">
          <div>
            <p className="eyebrow">Wave detail</p>
            <h2>{wave.name}</h2>
            <p>{wave.description || "No description provided."}</p>
          </div>
          <span className={`status ${wave.status}`}>{wave.status}</span>
        </div>
        <div className="stat-grid">
          <article className="stat-card">
            <span className="stat-card__label">Focus</span>
            <strong className="stat-card__value stat-card__value--text">
              {wave.focus_type}
            </strong>
            <span className="stat-card__hint">wave strategy</span>
          </article>
          <article className="stat-card">
            <span className="stat-card__label">Connectors</span>
            <strong className="stat-card__value">{connectors.length}</strong>
            <span className="stat-card__hint">configured inputs</span>
          </article>
          <article className="stat-card">
            <span className="stat-card__label">Records</span>
            <strong className="stat-card__value">{records.length}</strong>
            <span className="stat-card__hint">current filtered result set</span>
          </article>
          <article className="stat-card">
            <span className="stat-card__label">Signals</span>
            <strong className="stat-card__value">{signals.length}</strong>
            <span className="stat-card__hint">current filtered issues</span>
          </article>
        </div>
        <p className="hero-copy hero-copy--tight">
          Last Run: {prettyDate(wave.last_run_at)} | Last Success:{" "}
          {prettyDate(wave.last_success_at)} | Last Error:{" "}
          {prettyDate(wave.last_error_at)}
        </p>
        <div className="actions">
          <button onClick={onIngest} type="button">
            Trigger Sample Ingestion
          </button>
          <button onClick={onSchedulerTick} type="button">
            Run Scheduler Tick
          </button>
        </div>
        {ingestMessage ? <p className="notice notice--success">{ingestMessage}</p> : null}
        {tickMessage ? <p className="notice notice--success">{tickMessage}</p> : null}
        {discoveryMessage ? (
          <p className="notice notice--success">{discoveryMessage}</p>
        ) : null}
        {sourceCheckMessage ? (
          <p className="notice notice--success">{sourceCheckMessage}</p>
        ) : null}
        {wave.last_error_message ? (
          <p className="notice notice--error">{wave.last_error_message}</p>
        ) : null}
      </div>

      <div className="grid grid-2">
        <div className="panel">
          <div className="section-head">
            <div>
              <h3>Add Connector</h3>
              <p className="section-copy">
                Attach a source feed and tune how often it should poll.
              </p>
            </div>
          </div>
          <form className="stack" onSubmit={onConnectorCreate}>
            <label>
              Type
              <select
                value={connectorForm.type}
                onChange={(event) =>
                  setConnectorForm(createDefaultConnectorForm(event.target.value))
                }
              >
                {listConnectorFormSpecs().map((spec) => (
                  <option key={spec.type} value={spec.type}>
                    {spec.label}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Name
              <input
                value={connectorForm.name}
                onChange={(event) =>
                  setConnectorForm({ ...connectorForm, name: event.target.value })
                }
              />
            </label>
            <label>
              Polling Interval (minutes)
              <input
                min={1}
                type="number"
                value={connectorForm.polling_interval_minutes}
                onChange={(event) =>
                  setConnectorForm({
                    ...connectorForm,
                    polling_interval_minutes: Number(event.target.value),
                  })
                }
              />
            </label>
            {currentConnectorSpec ? (
              <currentConnectorSpec.component
                draft={connectorForm.draft}
                onChange={(nextDraft) =>
                  setConnectorForm({
                    ...connectorForm,
                    draft: nextDraft,
                  })
                }
              />
            ) : null}
            <label className="inline">
              <input
                checked={connectorForm.enabled}
                type="checkbox"
                onChange={(event) =>
                  setConnectorForm({ ...connectorForm, enabled: event.target.checked })
                }
              />
              Enabled
            </label>
            <button type="submit">Create Connector</button>
          </form>
        </div>

        <div className="panel">
          <div className="section-head">
            <div>
              <h3>Connectors</h3>
              <p className="section-copy">
                Review live connector health, cadence, and recent run context.
              </p>
            </div>
          </div>
          {connectors.length === 0 ? <p>No connectors for this wave.</p> : null}
          <ul className="stack">
            {connectors.map((connector) => (
              <li key={connector.id} className="card">
                <div className="between">
                  <strong>{connector.name}</strong>
                  <span className={`status ${connectorHealth(connector)}`}>
                    {connectorHealth(connector)}
                  </span>
                </div>
                <p>
                  {connector.type} | every {connector.polling_interval_minutes} min
                </p>
                <p>{summarizeConnectorConfig(connector)}</p>
                <p>
                  Last Run: {prettyDate(connector.last_run_at)} | Last Success:{" "}
                  {prettyDate(connector.last_success_at)}
                </p>
                <p>
                  Last Error: {prettyDate(connector.last_error_at)} | Next Run:{" "}
                  {prettyDate(connector.next_run_at)}
                </p>
                {connector.last_error_message ? (
                  <p className="error">{connector.last_error_message}</p>
                ) : null}
                <div className="actions">
                  <button onClick={() => onToggleConnector(connector)} type="button">
                    Toggle Enabled
                  </button>
                  <button onClick={() => onDeleteConnector(connector.id)} type="button">
                    Delete
                  </button>
                </div>
              </li>
            ))}
          </ul>
        </div>
      </div>

      <div className="panel">
        <div className="section-head">
          <div>
            <h3>Source Discovery</h3>
            <p className="section-copy">
              Manage trust policy, candidate review, and automated source checks.
            </p>
          </div>
        </div>
        <div className="panel">
          <h4>Domain Trust</h4>
          <form className="stack" onSubmit={onSaveDomainTrust}>
            <div className="grid grid-2">
              <label>
                Domain
                <input
                  disabled={domainTrustForm.id !== null}
                  onChange={(event) =>
                    setDomainTrustForm({
                      ...domainTrustForm,
                      domain: event.target.value,
                    })
                  }
                  placeholder="example.gov"
                  value={domainTrustForm.domain}
                />
              </label>
              <label>
                Trust Level
                <select
                  onChange={(event) =>
                    setDomainTrustForm({
                      ...domainTrustForm,
                      trust_level: event.target.value as DomainTrustLevel,
                    })
                  }
                  value={domainTrustForm.trust_level}
                >
                  <option value="neutral">neutral</option>
                  <option value="trusted">trusted</option>
                  <option value="blocked">blocked</option>
                </select>
              </label>
              <label>
                Approval Policy
                <select
                  onChange={(event) =>
                    setDomainTrustForm({
                      ...domainTrustForm,
                      approval_policy: event.target.value as DomainApprovalPolicy,
                    })
                  }
                  value={domainTrustForm.approval_policy}
                >
                  <option value="manual_review">manual_review</option>
                  <option value="auto_approve_stable">auto_approve_stable</option>
                  <option value="always_review">always_review</option>
                  <option value="auto_reject">auto_reject</option>
                </select>
              </label>
              <label>
                Notes
                <input
                  onChange={(event) =>
                    setDomainTrustForm({
                      ...domainTrustForm,
                      notes: event.target.value,
                    })
                  }
                  placeholder="why this domain is trusted"
                  value={domainTrustForm.notes}
                />
              </label>
            </div>
            <div className="actions">
              <button disabled={!domainTrustForm.domain.trim()} type="submit">
                {domainTrustForm.id ? "Update Domain Trust" : "Add Domain Trust"}
              </button>
              <button
                onClick={() =>
                  setDomainTrustForm({
                    id: null,
                    domain: "",
                    trust_level: "neutral",
                    approval_policy: "manual_review",
                    notes: "",
                  })
                }
                type="button"
              >
                Clear Domain Form
              </button>
            </div>
          </form>
          {trustMessage ? <p className="notice notice--success">{trustMessage}</p> : null}
          {domainTrustProfiles.length === 0 ? <p>No domain trust profiles yet.</p> : null}
          {domainTrustProfiles.length > 0 ? (
            <table className="run-table">
              <thead>
                <tr>
                  <th>Domain</th>
                  <th>Trust</th>
                  <th>Policy</th>
                  <th>Sources</th>
                  <th>Approved</th>
                  <th>Avg Stability</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {domainTrustProfiles.map((profile) => (
                  <tr key={profile.id}>
                    <td>{profile.domain}</td>
                    <td>
                      <span className={`status ${trustClass(profile.trust_level)}`}>
                        {profile.trust_level}
                      </span>
                    </td>
                    <td>{profile.approval_policy}</td>
                    <td>{profile.source_count}</td>
                    <td>{profile.approved_source_count}</td>
                    <td>
                      {profile.average_stability_score !== null
                        ? profile.average_stability_score.toFixed(2)
                        : "-"}
                    </td>
                    <td>
                      <div className="actions">
                        <button onClick={() => onEditDomainTrust(profile)} type="button">
                          Edit
                        </button>
                        <button onClick={() => onDeleteDomainTrust(profile.id)} type="button">
                          Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : null}
        </div>
        <div className="panel">
          <h4>Wave Trust Overrides</h4>
          <form className="stack" onSubmit={onSaveWaveTrustOverride}>
            <div className="grid grid-2">
              <label>
                Domain
                <input
                  disabled={waveTrustOverrideForm.id !== null}
                  onChange={(event) =>
                    setWaveTrustOverrideForm({
                      ...waveTrustOverrideForm,
                      domain: event.target.value,
                    })
                  }
                  placeholder="example.gov"
                  value={waveTrustOverrideForm.domain}
                />
              </label>
              <label>
                Trust Override
                <select
                  onChange={(event) =>
                    setWaveTrustOverrideForm({
                      ...waveTrustOverrideForm,
                      trust_level: event.target.value as WaveTrustOverrideFormState["trust_level"],
                    })
                  }
                  value={waveTrustOverrideForm.trust_level}
                >
                  <option value="">inherit global/default</option>
                  <option value="neutral">neutral</option>
                  <option value="trusted">trusted</option>
                  <option value="blocked">blocked</option>
                </select>
              </label>
              <label>
                Policy Override
                <select
                  onChange={(event) =>
                    setWaveTrustOverrideForm({
                      ...waveTrustOverrideForm,
                      approval_policy: event.target.value as WaveTrustOverrideFormState["approval_policy"],
                    })
                  }
                  value={waveTrustOverrideForm.approval_policy}
                >
                  <option value="">inherit global/default</option>
                  <option value="manual_review">manual_review</option>
                  <option value="auto_approve_stable">auto_approve_stable</option>
                  <option value="always_review">always_review</option>
                  <option value="auto_reject">auto_reject</option>
                </select>
              </label>
              <label>
                Notes
                <input
                  onChange={(event) =>
                    setWaveTrustOverrideForm({
                      ...waveTrustOverrideForm,
                      notes: event.target.value,
                    })
                  }
                  placeholder="wave-specific trust rationale"
                  value={waveTrustOverrideForm.notes}
                />
              </label>
            </div>
            <div className="actions">
              <button disabled={!waveTrustOverrideForm.domain.trim()} type="submit">
                {waveTrustOverrideForm.id ? "Update Wave Override" : "Add Wave Override"}
              </button>
              <button
                onClick={() =>
                  setWaveTrustOverrideForm({
                    id: null,
                    domain: "",
                    trust_level: "",
                    approval_policy: "",
                    notes: "",
                  })
                }
                type="button"
              >
                Clear Override Form
              </button>
            </div>
          </form>
          {waveOverrideMessage ? (
            <p className="notice notice--success">{waveOverrideMessage}</p>
          ) : null}
          {waveTrustOverrides.length === 0 ? <p>No wave trust overrides yet.</p> : null}
          {waveTrustOverrides.length > 0 ? (
            <table className="run-table">
              <thead>
                <tr>
                  <th>Domain</th>
                  <th>Trust</th>
                  <th>Policy</th>
                  <th>Sources</th>
                  <th>Rejected</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {waveTrustOverrides.map((override) => (
                  <tr key={override.id}>
                    <td>{override.domain}</td>
                    <td>{override.trust_level || "inherit"}</td>
                    <td>{override.approval_policy || "inherit"}</td>
                    <td>{override.source_count}</td>
                    <td>{override.rejected_source_count}</td>
                    <td>
                      <div className="actions">
                        <button onClick={() => onEditWaveTrustOverride(override)} type="button">
                          Edit
                        </button>
                        <button onClick={() => onDeleteWaveTrustOverride(override.id)} type="button">
                          Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : null}
        </div>
        <div className="grid grid-2">
          <label>
            Status
            <select
              value={sourceFilters.status}
              onChange={(event) =>
                setSourceFilters({ ...sourceFilters, status: event.target.value as SourceFilterDraft["status"] })
              }
            >
              <option value="">Any</option>
              <option value="candidate">candidate</option>
              <option value="sandboxed">sandboxed</option>
              <option value="approved">approved</option>
              <option value="degraded">degraded</option>
              <option value="rejected">rejected</option>
              <option value="archived">archived</option>
              <option value="ignored">ignored</option>
            </select>
          </label>
          <label>
            Source Type
            <input
              value={sourceFilters.source_type}
              onChange={(event) => setSourceFilters({ ...sourceFilters, source_type: event.target.value })}
              placeholder="rss, api_json, document_pdf..."
            />
          </label>
          <label>
            Min Relevance
            <input
              value={sourceFilters.min_relevance_score}
              onChange={(event) =>
                setSourceFilters({ ...sourceFilters, min_relevance_score: event.target.value })
              }
              placeholder="0.0 - 1.0"
              type="number"
              min={0}
              max={1}
              step={0.05}
            />
          </label>
          <label>
            Min Stability
            <input
              value={sourceFilters.min_stability_score}
              onChange={(event) =>
                setSourceFilters({ ...sourceFilters, min_stability_score: event.target.value })
              }
              placeholder="0.0 - 1.0"
              type="number"
              min={0}
              max={1}
              step={0.05}
            />
          </label>
          <label>
            Parent Domain
            <input
              value={sourceFilters.parent_domain}
              onChange={(event) => setSourceFilters({ ...sourceFilters, parent_domain: event.target.value })}
              placeholder="example.gov"
            />
          </label>
          <label>
            Sort
            <select
              value={sourceFilters.sort}
              onChange={(event) =>
                setSourceFilters({ ...sourceFilters, sort: event.target.value as SourceFilterDraft["sort"] })
              }
            >
              <option value="relevance_desc">Relevance desc</option>
              <option value="relevance_asc">Relevance asc</option>
              <option value="stability_desc">Stability desc</option>
              <option value="stability_asc">Stability asc</option>
              <option value="newest">Newest</option>
              <option value="oldest">Oldest</option>
            </select>
          </label>
        </div>
        <p className="filter-note">
          {sourceFilterActive ? `Active filters: ${sourceFilterActive}` : "Active filters: none"}
        </p>
        <div className="actions">
          <button
            onClick={() =>
              setSourceFilters({
                status: "",
                source_type: "",
                min_relevance_score: "",
                min_stability_score: "",
                parent_domain: "",
                sort: "relevance_desc",
              })
            }
            type="button"
          >
            Clear Source Filters
          </button>
        </div>
        <label>
          Seed URLs (optional, comma or newline separated)
          <textarea
            onChange={(event) => setSeedUrlsText(event.target.value)}
            placeholder="https://city.example.gov/alerts, https://agency.example.gov/open-data"
            rows={3}
            value={seedUrlsText}
          />
        </label>
        <div className="actions">
          <button onClick={onRunDiscovery} type="button">
            Run Discovery
          </button>
          <button onClick={onRunBatchSourceChecks} type="button">
            Check All Sources
          </button>
          <button onClick={onReevaluateWaveSources} type="button">
            Reevaluate Lifecycle
          </button>
        </div>
        <div className="grid grid-2">
          <label>
            Check Status
            <select
              value={checkFilters.status}
              onChange={(event) =>
                setCheckFilters({ ...checkFilters, status: event.target.value as CheckFilterDraft["status"] })
              }
            >
              <option value="">Any</option>
              <option value="success">success</option>
              <option value="failed">failed</option>
              <option value="skipped">skipped</option>
            </select>
          </label>
          <label>
            Reachable
            <select
              value={checkFilters.reachable}
              onChange={(event) =>
                setCheckFilters({
                  ...checkFilters,
                  reachable: event.target.value as CheckFilterDraft["reachable"],
                })
              }
            >
              <option value="any">Any</option>
              <option value="yes">Yes</option>
              <option value="no">No</option>
            </select>
          </label>
          <label>
            Parseable
            <select
              value={checkFilters.parseable}
              onChange={(event) =>
                setCheckFilters({
                  ...checkFilters,
                  parseable: event.target.value as CheckFilterDraft["parseable"],
                })
              }
            >
              <option value="any">Any</option>
              <option value="yes">Yes</option>
              <option value="no">No</option>
            </select>
          </label>
          <label>
            Content Type
            <input
              value={checkFilters.content_type}
              onChange={(event) => setCheckFilters({ ...checkFilters, content_type: event.target.value })}
              placeholder="application/json"
            />
          </label>
          <label>
            Check Sort
            <select
              value={checkFilters.sort}
              onChange={(event) =>
                setCheckFilters({
                  ...checkFilters,
                  sort: event.target.value as CheckFilterDraft["sort"],
                })
              }
            >
              <option value="newest">Newest</option>
              <option value="oldest">Oldest</option>
            </select>
          </label>
        </div>
        <p className="filter-note">
          {checkFilterActive ? `Check filters: ${checkFilterActive}` : "Check filters: none"}
        </p>
        <div className="actions">
          <button
            onClick={() =>
              setCheckFilters({
                status: "",
                reachable: "any",
                parseable: "any",
                content_type: "",
                sort: "newest",
              })
            }
            type="button"
          >
            Clear Check Filters
          </button>
        </div>
        {discoveredSources.length === 0 ? <p>No discovered sources yet.</p> : null}
        <ul className="stack">
          {discoveredSources.map((source) => (
            <li key={source.id} className="card">
              <div className="between">
                <strong>{source.title || source.url}</strong>
                <span className={`status ${discoveredStatusClass(source.status)}`}>
                  {source.status}
                </span>
              </div>
              <p>
                Type: {source.source_type} | Domain: {source.parent_domain || "-"} | Relevance:{" "}
                {source.relevance_score.toFixed(2)}
              </p>
              <p>
                Trust:{" "}
                <span className={`status ${trustClass(source.domain_trust_level)}`}>
                  {source.domain_trust_level}
                </span>
                {" | "}Tier:{" "}
                <span className={`status ${trustTierClass(source.trust_tier)}`}>
                  {source.trust_tier}
                </span>
                {" | "}Policy: {source.domain_approval_policy} | Decision:{" "}
                <span className={`status ${policyStateClass(source.policy_state)}`}>
                  {source.policy_state}
                </span>
              </p>
              <p>
                Lifecycle: <strong>{source.status}</strong>
                {" | "}
                Policy Source: {policySourceLabel(source.policy_source)}
                {source.wave_trust_override_id ? ` (#${source.wave_trust_override_id})` : ""}
                {" | "}
                Policy Reason: {source.policy_reason} | Approval Origin:{" "}
                {source.approval_origin || "-"}
              </p>
              {source.sandbox_progress ? (
                <p>
                  Sandbox: checks {(source.sandbox_progress["successful_checks"] as number | undefined) ?? 0}/
                  {(source.sandbox_progress["required_successful_checks"] as number | undefined) ?? 0}
                  {" | "}Latest Check Success:{" "}
                  {(source.sandbox_progress["latest_check_success"] as boolean | undefined) ? "yes" : "no"}
                </p>
              ) : null}
              {source.degradation_reason ? <p>Degradation Reason: {source.degradation_reason}</p> : null}
              <p>
                Stability:{" "}
                {source.stability_score !== null ? source.stability_score.toFixed(2) : "-"} | Last
                Checked: {prettyDate(source.last_checked_at)} | Last Success:{" "}
                {prettyDate(source.last_success_at)} | Failures: {source.failure_count}
              </p>
              <p>
                Auto Check: {source.auto_check_enabled ? "active" : "disabled"} | Interval:{" "}
                {source.check_interval_minutes} min | Next Check: {prettyDate(source.next_check_at)}
                {" | "}Consecutive Failures: {source.consecutive_failures}
              </p>
              <p>
                Last HTTP: {source.last_http_status ?? "-"} | Last Content-Type:{" "}
                {source.last_content_type || "-"}
              </p>
              <p>
                Method: {source.discovery_method} | Suggested Connector:{" "}
                {source.suggested_connector_type || "-"}
              </p>
              {source.description_summary ? <p>{source.description_summary}</p> : null}
              <a href={source.url} rel="noreferrer" target="_blank">
                Open source
              </a>
              <div className="actions">
                {source.parent_domain ? (
                  <button
                    onClick={() =>
                      setDomainTrustForm({
                        id: null,
                        domain: source.parent_domain || "",
                        trust_level: source.domain_trust_level,
                        approval_policy: source.domain_approval_policy,
                        notes: "",
                      })
                    }
                    type="button"
                  >
                    Use Domain in Trust Form
                  </button>
                ) : null}
                {source.parent_domain ? (
                  <button
                    onClick={() =>
                      setWaveTrustOverrideForm({
                        id: null,
                        domain: source.parent_domain || "",
                        trust_level: source.domain_trust_level,
                        approval_policy: source.domain_approval_policy,
                        notes: "",
                      })
                    }
                    type="button"
                  >
                    Use Domain in Override Form
                  </button>
                ) : null}
                {source.status !== "approved" ? (
                  <button onClick={() => onApproveDiscoveredSource(source.id)} type="button">
                    Approve
                  </button>
                ) : null}
                <button onClick={() => onRunSourceCheck(source.id)} type="button">
                  Check Source
                </button>
                <button onClick={() => onLoadSourceChecks(source.id)} type="button">
                  Show Checks
                </button>
                <button onClick={() => onReevaluateSourceLifecycle(source.id)} type="button">
                  Reevaluate
                </button>
                {source.status !== "rejected" ? (
                  <button
                    onClick={() => onDiscoveredSourceStatusChange(source.id, "rejected")}
                    type="button"
                  >
                    Reject
                  </button>
                ) : null}
                {source.status !== "archived" ? (
                  <button
                    onClick={() => onDiscoveredSourceStatusChange(source.id, "archived")}
                    type="button"
                  >
                    Archive
                  </button>
                ) : null}
              </div>
              {sourceChecksBySource[source.id]?.length ? (
                <table className="run-table">
                  <thead>
                    <tr>
                      <th>Checked</th>
                      <th>Status</th>
                      <th>HTTP</th>
                      <th>Type</th>
                      <th>Latency</th>
                      <th>Parseable</th>
                    </tr>
                  </thead>
                  <tbody>
                    {sourceChecksBySource[source.id].map((check) => (
                      <tr key={check.id}>
                        <td>{prettyDate(check.checked_at)}</td>
                        <td>
                          <span className={`status ${checkStatusClass(check.status)}`}>
                            {check.status}
                          </span>
                        </td>
                        <td>{check.http_status ?? "-"}</td>
                        <td>{check.content_type || "-"}</td>
                        <td>{check.latency_ms ?? "-"}</td>
                        <td>{check.parseable ? "yes" : "no"}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              ) : null}
            </li>
          ))}
        </ul>
        <div className="panel">
          <h4>Policy Action History</h4>
          {policyActions.length === 0 ? <p>No policy actions logged yet.</p> : null}
          {policyActions.length > 0 ? (
            <table className="run-table">
              <thead>
                <tr>
                  <th>When</th>
                  <th>Action</th>
                  <th>Source</th>
                  <th>Lifecycle</th>
                  <th>Tier</th>
                  <th>Triggered By</th>
                  <th>Reason</th>
                </tr>
              </thead>
              <tbody>
                {policyActions.map((row) => (
                  <tr key={row.id}>
                    <td>{prettyDate(row.created_at)}</td>
                    <td>{row.action_type}</td>
                    <td>#{row.discovered_source_id}</td>
                    <td>
                      {row.previous_lifecycle_state} {"->"} {row.new_lifecycle_state}
                    </td>
                    <td>{row.previous_trust_tier} {"->"} {row.new_trust_tier}</td>
                    <td>{row.triggered_by}</td>
                    <td>{row.reason}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : null}
        </div>
      </div>

      <div className="panel">
        <div className="section-head">
          <div>
            <h3>Recent Signals</h3>
            <p className="section-copy">
              Triage surfaced issues, then acknowledge or resolve them in place.
            </p>
          </div>
        </div>
        <div className="grid grid-2">
          <label>
            Severity
            <select
              value={signalFilters.severity}
              onChange={(event) =>
                setSignalFilters({
                  ...signalFilters,
                  severity: event.target.value as SignalFilterDraft["severity"],
                })
              }
            >
              <option value="">Any</option>
              <option value="low">low</option>
              <option value="medium">medium</option>
              <option value="high">high</option>
            </select>
          </label>
          <label>
            Status
            <select
              value={signalFilters.status}
              onChange={(event) =>
                setSignalFilters({
                  ...signalFilters,
                  status: event.target.value as SignalFilterDraft["status"],
                })
              }
            >
              <option value="">Any</option>
              <option value="new">new</option>
              <option value="acknowledged">acknowledged</option>
              <option value="resolved">resolved</option>
            </select>
          </label>
          <label>
            Type
            <input
              value={signalFilters.signal_type}
              onChange={(event) =>
                setSignalFilters({ ...signalFilters, signal_type: event.target.value })
              }
              placeholder="matching_record"
            />
          </label>
          <label>
            Sort
            <select
              value={signalFilters.sort}
              onChange={(event) =>
                setSignalFilters({
                  ...signalFilters,
                  sort: event.target.value as SignalFilterDraft["sort"],
                })
              }
            >
              <option value="newest">Newest</option>
              <option value="oldest">Oldest</option>
            </select>
          </label>
        </div>
        <p className="filter-note">
          {signalFilterActive ? `Active filters: ${signalFilterActive}` : "Active filters: none"}
        </p>
        <div className="actions">
          <button
            onClick={() =>
              setSignalFilters({
                severity: "",
                status: "",
                signal_type: "",
                sort: "newest",
              })
            }
            type="button"
          >
            Clear Signal Filters
          </button>
        </div>
        {signals.length === 0 ? <p>No signals yet.</p> : null}
        <ul className="stack">
          {signals.map((signal) => (
            <li key={signal.id} className="card">
              <div className="between">
                <strong>{signal.title}</strong>
                <span className={`status ${severityClass(signal.severity)}`}>
                  {signal.severity}
                </span>
              </div>
              <p>{signal.summary}</p>
              <p>
                Type: {signal.type} | Status: {signal.status} | Created:{" "}
                {prettyDate(signal.created_at)}
              </p>
              <div className="actions">
                {signal.status === "new" ? (
                  <button
                    onClick={() => onSignalStatusChange(signal.id, "acknowledged")}
                    type="button"
                  >
                    Acknowledge
                  </button>
                ) : null}
                {signal.status !== "resolved" ? (
                  <button onClick={() => onSignalStatusChange(signal.id, "resolved")} type="button">
                    Resolve
                  </button>
                ) : null}
              </div>
            </li>
          ))}
        </ul>
      </div>

      <div className="panel">
        <div className="section-head">
          <div>
            <h3>Recent Runs</h3>
            <p className="section-copy">
              Inspect connector execution history and quick failure context.
            </p>
          </div>
        </div>
        {runHistory.length === 0 ? <p>No runs yet.</p> : null}
        {runHistory.length > 0 ? (
          <table className="run-table">
            <thead>
              <tr>
                <th>Connector</th>
                <th>Status</th>
                <th>Started</th>
                <th>Finished</th>
                <th>Records</th>
                <th>Error</th>
              </tr>
            </thead>
            <tbody>
              {runHistory.map((run) => (
                <tr key={run.id}>
                  <td>{run.connector_name || `#${run.connector_id}`}</td>
                  <td>
                    <span
                      className={`status ${
                        run.status === "failed"
                          ? "error"
                          : run.status === "success"
                            ? "healthy"
                            : "active"
                      }`}
                    >
                      {run.status}
                    </span>
                  </td>
                  <td>{prettyDate(run.started_at)}</td>
                  <td>{prettyDate(run.finished_at)}</td>
                  <td>{run.records_created}</td>
                  <td>{run.error_message || "-"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : null}
      </div>

      <div className="panel">
        <div className="section-head">
          <div>
            <h3>Records</h3>
            <p className="section-copy">
              Search the collected dataset by connector, source type, and
              coordinate availability.
            </p>
          </div>
        </div>
        <div className="grid grid-2">
          <label>
            Search
            <input
              value={recordFilters.text_search}
              onChange={(event) =>
                setRecordFilters({ ...recordFilters, text_search: event.target.value })
              }
              placeholder="title/content/source..."
            />
          </label>
          <label>
            Connector Id
            <input
              value={recordFilters.connector_id}
              onChange={(event) =>
                setRecordFilters({ ...recordFilters, connector_id: event.target.value })
              }
              placeholder="e.g. 1"
            />
          </label>
          <label>
            Source Type
            <input
              value={recordFilters.source_type}
              onChange={(event) =>
                setRecordFilters({ ...recordFilters, source_type: event.target.value })
              }
              placeholder="rss_news, weather..."
            />
          </label>
          <label>
            Coordinates
            <select
              value={recordFilters.has_coordinates}
              onChange={(event) =>
                setRecordFilters({
                  ...recordFilters,
                  has_coordinates: event.target.value as RecordFilterDraft["has_coordinates"],
                })
              }
            >
              <option value="any">Any</option>
              <option value="yes">With coordinates</option>
              <option value="no">Without coordinates</option>
            </select>
          </label>
          <label>
            Sort
            <select
              value={recordFilters.sort}
              onChange={(event) =>
                setRecordFilters({
                  ...recordFilters,
                  sort: event.target.value as RecordFilterDraft["sort"],
                })
              }
            >
              <option value="newest">Newest</option>
              <option value="oldest">Oldest</option>
            </select>
          </label>
        </div>
        <p className="filter-note">
          {recordFilterActive ? `Active filters: ${recordFilterActive}` : "Active filters: none"}
        </p>
        <div className="actions">
          <button
            onClick={() =>
              setRecordFilters({
                text_search: "",
                connector_id: "",
                source_type: "",
                has_coordinates: "any",
                sort: "newest",
              })
            }
            type="button"
          >
            Clear Record Filters
          </button>
        </div>
        {records.length === 0 ? <p>No records collected yet.</p> : null}
        <ul className="stack">
          {records.map((record) => (
            <li key={record.id} className="card">
              <h4>{record.title}</h4>
              <p>{record.content}</p>
              <p>
                Source: {record.source_name} ({record.source_type})
              </p>
              <p>Collected: {prettyDate(record.collected_at)}</p>
              <p>Event Time: {prettyDate(record.event_time)}</p>
              {record.source_url ? (
                <a href={record.source_url} rel="noreferrer" target="_blank">
                  Open source URL
                </a>
              ) : null}
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
