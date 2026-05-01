import { request } from "./client";
import type {
  BatchSourceCheckResult,
  Connector,
  ConnectorCreateInput,
  ConnectorUpdateInput,
  DomainTrustCreateInput,
  DomainTrustProfile,
  DomainTrustUpdateInput,
  PolicyActionLog,
  DiscoveredSource,
  DiscoveredSourceFilters,
  DiscoveredSourceStatus,
  DiscoverSourcesResult,
  IngestResult,
  RecordFilters,
  RunHistoryEntry,
  SchedulerTickResult,
  SignalFilters,
  SignalItem,
  SignalStatus,
  SourceCheckFilters,
  SourceCheck,
  WaveTrustOverride,
  WaveTrustOverrideCreateInput,
  WaveTrustOverrideUpdateInput,
  Wave,
  WaveCreateInput,
  WaveRecord,
} from "../types/domain";

function withQuery(path: string, params?: Record<string, string | number | boolean | undefined>) {
  if (!params) {
    return path;
  }
  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== null && value !== "") {
      search.set(key, String(value));
    }
  }
  const query = search.toString();
  return query ? `${path}?${query}` : path;
}

export function listWaves() {
  return request<Wave[]>("/api/waves");
}

export function createWave(input: WaveCreateInput) {
  return request<Wave>("/api/waves", {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export function getWave(waveId: number) {
  return request<Wave>(`/api/waves/${waveId}`);
}

export function listConnectors(waveId: number) {
  return request<Connector[]>(`/api/waves/${waveId}/connectors`);
}

export function createConnector(waveId: number, input: ConnectorCreateInput) {
  return request<Connector>(`/api/waves/${waveId}/connectors`, {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export function updateConnector(connectorId: number, input: ConnectorUpdateInput) {
  return request<Connector>(`/api/connectors/${connectorId}`, {
    method: "PATCH",
    body: JSON.stringify(input),
  });
}

export function deleteConnector(connectorId: number) {
  return request<void>(`/api/connectors/${connectorId}`, {
    method: "DELETE",
  });
}

export function listRecords(waveId: number, filters?: RecordFilters) {
  return request<WaveRecord[]>(
    withQuery(`/api/waves/${waveId}/records`, {
      text_search: filters?.text_search,
      connector_id: filters?.connector_id,
      source_type: filters?.source_type,
      start_date: filters?.start_date,
      end_date: filters?.end_date,
      has_coordinates: filters?.has_coordinates,
      sort: filters?.sort,
    })
  );
}

export function ingestSample(waveId: number) {
  return request<IngestResult>(`/api/waves/${waveId}/ingest/sample`, {
    method: "POST",
  });
}

export function listWaveRuns(waveId: number, limit = 50) {
  return request<RunHistoryEntry[]>(`/api/waves/${waveId}/runs?limit=${limit}`);
}

export function listConnectorRuns(connectorId: number, limit = 50) {
  return request<RunHistoryEntry[]>(`/api/connectors/${connectorId}/runs?limit=${limit}`);
}

export function triggerSchedulerTick() {
  return request<SchedulerTickResult>("/api/scheduler/tick", {
    method: "POST",
  });
}

export function listWaveSignals(waveId: number, filters?: SignalFilters) {
  return request<SignalItem[]>(
    withQuery(`/api/waves/${waveId}/signals`, {
      limit: filters?.limit ?? 100,
      severity: filters?.severity,
      status: filters?.status,
      signal_type: filters?.signal_type,
      start_date: filters?.start_date,
      end_date: filters?.end_date,
      sort: filters?.sort,
    })
  );
}

export function updateSignalStatus(signalId: number, status: SignalStatus) {
  return request<SignalItem>(`/api/signals/${signalId}`, {
    method: "PATCH",
    body: JSON.stringify({ status }),
  });
}

export function discoverSources(waveId: number, seedUrls: string[] = []) {
  return request<DiscoverSourcesResult>(`/api/waves/${waveId}/discover-sources`, {
    method: "POST",
    body: JSON.stringify({ seed_urls: seedUrls }),
  });
}

export function listDiscoveredSources(waveId: number, filters?: DiscoveredSourceFilters) {
  return request<DiscoveredSource[]>(
    withQuery(`/api/waves/${waveId}/discovered-sources`, {
      limit: filters?.limit ?? 200,
      status: filters?.status,
      source_type: filters?.source_type,
      min_relevance_score: filters?.min_relevance_score,
      min_stability_score: filters?.min_stability_score,
      parent_domain: filters?.parent_domain,
      approved_only: filters?.approved_only,
      new_only: filters?.new_only,
      sort: filters?.sort,
    })
  );
}

export function updateDiscoveredSourceStatus(
  sourceId: number,
  status: DiscoveredSourceStatus
) {
  return request<DiscoveredSource>(`/api/discovered-sources/${sourceId}`, {
    method: "PATCH",
    body: JSON.stringify({ status }),
  });
}

export function approveDiscoveredSource(sourceId: number) {
  return request<{ source_id: number; status: DiscoveredSourceStatus; connector_id: number | null }>(
    `/api/discovered-sources/${sourceId}/approve`,
    { method: "POST" }
  );
}

export function runSourceCheck(sourceId: number) {
  return request<SourceCheck>(`/api/discovered-sources/${sourceId}/check`, {
    method: "POST",
  });
}

export function reevaluateDiscoveredSourceLifecycle(sourceId: number) {
  return request<DiscoveredSource>(`/api/discovered-sources/${sourceId}/reevaluate-lifecycle`, {
    method: "POST",
  });
}

export function listSourceChecks(sourceId: number, filters?: SourceCheckFilters) {
  return request<SourceCheck[]>(
    withQuery(`/api/discovered-sources/${sourceId}/checks`, {
      limit: filters?.limit ?? 20,
      status: filters?.status,
      reachable: filters?.reachable,
      parseable: filters?.parseable,
      start_date: filters?.start_date,
      end_date: filters?.end_date,
      content_type: filters?.content_type,
      sort: filters?.sort,
    })
  );
}

export function checkWaveDiscoveredSources(waveId: number, limit = 100) {
  return request<BatchSourceCheckResult>(
    `/api/waves/${waveId}/check-discovered-sources?limit=${limit}`,
    { method: "POST" }
  );
}

export function reevaluateWaveSources(waveId: number) {
  return request<{
    domain: string;
    evaluated_count: number;
    changed_count: number;
    auto_approved_count: number;
    blocked_count: number;
    reviewable_count: number;
    preserved_count: number;
  }>(`/api/waves/${waveId}/reevaluate-sources`, { method: "POST" });
}

export function listDomainTrustProfiles(limit = 200) {
  return request<DomainTrustProfile[]>(`/api/domain-trust?limit=${limit}`);
}

export function createDomainTrustProfile(input: DomainTrustCreateInput) {
  return request<DomainTrustProfile>("/api/domain-trust", {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export function updateDomainTrustProfile(
  profileId: number,
  input: DomainTrustUpdateInput
) {
  return request<DomainTrustProfile>(`/api/domain-trust/${profileId}`, {
    method: "PATCH",
    body: JSON.stringify(input),
  });
}

export function deleteDomainTrustProfile(profileId: number) {
  return request<void>(`/api/domain-trust/${profileId}`, {
    method: "DELETE",
  });
}

export function listWaveTrustOverrides(waveId: number, limit = 200) {
  return request<WaveTrustOverride[]>(`/api/waves/${waveId}/trust-overrides?limit=${limit}`);
}

export function createWaveTrustOverride(waveId: number, input: WaveTrustOverrideCreateInput) {
  return request<WaveTrustOverride>(`/api/waves/${waveId}/trust-overrides`, {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export function updateWaveTrustOverride(
  overrideId: number,
  input: WaveTrustOverrideUpdateInput
) {
  return request<WaveTrustOverride>(`/api/wave-trust-overrides/${overrideId}`, {
    method: "PATCH",
    body: JSON.stringify(input),
  });
}

export function deleteWaveTrustOverride(overrideId: number) {
  return request<void>(`/api/wave-trust-overrides/${overrideId}`, {
    method: "DELETE",
  });
}

export function listWavePolicyActions(waveId: number, limit = 200) {
  return request<PolicyActionLog[]>(`/api/waves/${waveId}/policy-actions?limit=${limit}`);
}

export function listSourcePolicyActions(sourceId: number, limit = 200) {
  return request<PolicyActionLog[]>(`/api/discovered-sources/${sourceId}/policy-actions?limit=${limit}`);
}
