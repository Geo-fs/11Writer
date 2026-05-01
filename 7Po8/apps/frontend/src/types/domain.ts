export type WaveStatus = "active" | "paused" | "archived";
export type FocusType = "location" | "keyword" | "event" | "mixed";

export interface Wave {
  id: number;
  name: string;
  description: string;
  status: WaveStatus;
  focus_type: FocusType;
  created_at: string;
  updated_at: string;
  last_run_at: string | null;
  last_success_at: string | null;
  last_error_at: string | null;
  last_error_message: string | null;
  connector_count: number;
  record_count: number;
}

export interface Connector {
  id: number;
  wave_id: number;
  type: string;
  name: string;
  enabled: boolean;
  config_json: Record<string, unknown>;
  polling_interval_minutes: number;
  created_at: string;
  updated_at: string;
  last_run_at: string | null;
  last_success_at: string | null;
  last_error_at: string | null;
  last_error_message: string | null;
  next_run_at: string | null;
}

export interface WaveRecord {
  id: number;
  wave_id: number;
  connector_id: number | null;
  external_id: string | null;
  title: string;
  content: string;
  source_type: string;
  source_name: string;
  source_url: string | null;
  collected_at: string;
  event_time: string | null;
  latitude: number | null;
  longitude: number | null;
  tags_json: string[];
  raw_payload_json: Record<string, unknown> | null;
}

export interface IngestResult {
  wave_id: number;
  executed_connectors: number;
  successful_runs: number;
  failed_runs: number;
  ingested_count: number;
}

export type RunStatus = "running" | "success" | "failed";

export interface RunHistoryEntry {
  id: number;
  wave_id: number;
  connector_id: number;
  connector_name: string | null;
  started_at: string;
  finished_at: string | null;
  status: RunStatus;
  records_created: number;
  error_message: string | null;
}

export interface SchedulerTickResult {
  scanned_connectors: number;
  eligible_connectors: number;
  successful_runs: number;
  failed_runs: number;
  scanned_sources: number;
  eligible_sources: number;
  successful_source_checks: number;
  failed_source_checks: number;
  skipped_source_checks: number;
}

export type SignalSeverity = "low" | "medium" | "high";
export type SignalStatus = "new" | "acknowledged" | "resolved";
export type DiscoveredSourceStatus =
  | "candidate"
  | "sandboxed"
  | "approved"
  | "degraded"
  | "rejected"
  | "archived"
  | "ignored";
export type SourceCheckStatus = "success" | "failed" | "skipped";
export type DomainTrustLevel = "trusted" | "neutral" | "blocked";
export type SourceTrustTier = "tier_1" | "tier_2" | "tier_3" | "tier_4" | "tier_5";
export type DomainApprovalPolicy =
  | "manual_review"
  | "auto_approve_stable"
  | "auto_reject"
  | "always_review";
export type SourcePolicyState =
  | "blocked"
  | "auto_approved"
  | "auto_approvable"
  | "manual_review"
  | "ineligible";
export type PolicyResolutionSource = "wave_override" | "global_domain_trust" | "default";

export interface SignalItem {
  id: number;
  wave_id: number;
  connector_id: number | null;
  type: string;
  severity: SignalSeverity;
  title: string;
  summary: string;
  status: SignalStatus;
  created_at: string;
  metadata_json: Record<string, unknown> | null;
}

export interface DiscoveredSource {
  id: number;
  wave_id: number | null;
  url: string;
  title: string;
  source_type: string;
  parent_domain: string | null;
  status: DiscoveredSourceStatus;
  trust_tier: SourceTrustTier;
  discovery_method: string;
  relevance_score: number;
  stability_score: number | null;
  free_access: boolean | null;
  suggested_connector_type: string | null;
  description_summary: string | null;
  metadata_json: Record<string, unknown> | null;
  discovered_at: string;
  auto_check_enabled: boolean;
  check_interval_minutes: number;
  next_check_at: string | null;
  degradation_reason: string | null;
  sandbox_progress: Record<string, unknown> | null;
  consecutive_failures: number;
  last_checked_at: string | null;
  last_success_at: string | null;
  failure_count: number;
  last_http_status: number | null;
  last_content_type: string | null;
  domain_trust_level: DomainTrustLevel;
  domain_approval_policy: DomainApprovalPolicy;
  policy_state: SourcePolicyState;
  policy_reason: string;
  approval_origin: string | null;
  policy_source: PolicyResolutionSource;
  wave_trust_override_id: number | null;
  global_domain_trust_profile_id: number | null;
}

export interface DomainTrustProfile {
  id: number;
  domain: string;
  trust_level: DomainTrustLevel;
  approval_policy: DomainApprovalPolicy;
  notes: string | null;
  created_at: string;
  updated_at: string;
  source_count: number;
  approved_source_count: number;
  blocked_source_count: number;
  average_stability_score: number | null;
  last_seen_at: string | null;
}

export interface WaveTrustOverride {
  id: number;
  wave_id: number;
  domain: string;
  trust_level: DomainTrustLevel | null;
  approval_policy: DomainApprovalPolicy | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
  source_count: number;
  approved_source_count: number;
  rejected_source_count: number;
}

export interface WaveTrustOverrideCreateInput {
  domain: string;
  trust_level?: DomainTrustLevel | null;
  approval_policy?: DomainApprovalPolicy | null;
  notes?: string | null;
}

export interface WaveTrustOverrideUpdateInput {
  trust_level?: DomainTrustLevel | null;
  approval_policy?: DomainApprovalPolicy | null;
  notes?: string | null;
}

export interface PolicyActionLog {
  id: number;
  wave_id: number;
  discovered_source_id: number;
  domain: string | null;
  action_type: string;
  previous_status: DiscoveredSourceStatus;
  new_status: DiscoveredSourceStatus;
  previous_lifecycle_state: DiscoveredSourceStatus;
  new_lifecycle_state: DiscoveredSourceStatus;
  previous_trust_tier: SourceTrustTier;
  new_trust_tier: SourceTrustTier;
  previous_policy_context: Record<string, unknown> | null;
  new_policy_context: Record<string, unknown> | null;
  reason: string;
  triggered_by: string;
  created_at: string;
}

export interface DiscoverSourcesResult {
  wave_id: number;
  discovered_count: number;
  deduped_count: number;
}

export interface SourceCheck {
  id: number;
  discovered_source_id: number;
  checked_at: string;
  status: SourceCheckStatus;
  http_status: number | null;
  content_type: string | null;
  latency_ms: number | null;
  reachable: boolean;
  parseable: boolean;
  metadata_json: Record<string, unknown> | null;
}

export interface BatchSourceCheckResult {
  wave_id: number;
  checked_count: number;
  success_count: number;
  failed_count: number;
  skipped_count: number;
}

export type SortDirection = "newest" | "oldest";
export type SourceSortOption =
  | "newest"
  | "oldest"
  | "relevance_desc"
  | "relevance_asc"
  | "stability_desc"
  | "stability_asc";

export interface RecordFilters {
  text_search?: string;
  connector_id?: number;
  source_type?: string;
  start_date?: string;
  end_date?: string;
  has_coordinates?: boolean;
  sort?: SortDirection;
}

export interface SignalFilters {
  severity?: SignalSeverity;
  status?: SignalStatus;
  signal_type?: string;
  start_date?: string;
  end_date?: string;
  sort?: SortDirection;
  limit?: number;
}

export interface DiscoveredSourceFilters {
  status?: DiscoveredSourceStatus;
  source_type?: string;
  min_relevance_score?: number;
  min_stability_score?: number;
  parent_domain?: string;
  approved_only?: boolean;
  new_only?: boolean;
  sort?: SourceSortOption;
  limit?: number;
}

export interface SourceCheckFilters {
  status?: SourceCheckStatus;
  reachable?: boolean;
  parseable?: boolean;
  start_date?: string;
  end_date?: string;
  content_type?: string;
  sort?: SortDirection;
  limit?: number;
}

export interface WaveCreateInput {
  name: string;
  description: string;
  status: WaveStatus;
  focus_type: FocusType;
}

export interface ConnectorCreateInput {
  type: string;
  name: string;
  enabled: boolean;
  config_json: Record<string, unknown>;
  polling_interval_minutes: number;
}

export interface ConnectorUpdateInput {
  type?: string;
  name?: string;
  enabled?: boolean;
  config_json?: Record<string, unknown>;
  polling_interval_minutes?: number;
}

export interface DomainTrustCreateInput {
  domain: string;
  trust_level: DomainTrustLevel;
  approval_policy: DomainApprovalPolicy;
  notes?: string | null;
}

export interface DomainTrustUpdateInput {
  trust_level?: DomainTrustLevel;
  approval_policy?: DomainApprovalPolicy;
  notes?: string | null;
}
