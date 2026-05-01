from enum import Enum


class WaveStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    ARCHIVED = "archived"


class FocusType(str, Enum):
    LOCATION = "location"
    KEYWORD = "keyword"
    EVENT = "event"
    MIXED = "mixed"


class RunStatus(str, Enum):
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"


class SignalSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class SignalStatus(str, Enum):
    NEW = "new"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"


class SourceLifecycleState(str, Enum):
    CANDIDATE = "candidate"
    SANDBOXED = "sandboxed"
    APPROVED = "approved"
    DEGRADED = "degraded"
    REJECTED = "rejected"
    ARCHIVED = "archived"
    IGNORED = "ignored"


class SourceCheckStatus(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


class DomainTrustLevel(str, Enum):
    TRUSTED = "trusted"
    NEUTRAL = "neutral"
    BLOCKED = "blocked"


class DomainApprovalPolicy(str, Enum):
    MANUAL_REVIEW = "manual_review"
    AUTO_APPROVE_STABLE = "auto_approve_stable"
    AUTO_REJECT = "auto_reject"
    ALWAYS_REVIEW = "always_review"


class SourcePolicyState(str, Enum):
    BLOCKED = "blocked"
    AUTO_APPROVED = "auto_approved"
    AUTO_APPROVABLE = "auto_approvable"
    MANUAL_REVIEW = "manual_review"
    INELIGIBLE = "ineligible"


class SourceTrustTier(str, Enum):
    TIER_1 = "tier_1"
    TIER_2 = "tier_2"
    TIER_3 = "tier_3"
    TIER_4 = "tier_4"
    TIER_5 = "tier_5"


class DiscoveredSourceStatus(str, Enum):
    CANDIDATE = "candidate"
    SANDBOXED = "sandboxed"
    APPROVED = "approved"
    DEGRADED = "degraded"
    REJECTED = "rejected"
    ARCHIVED = "archived"
    IGNORED = "ignored"
    NEW = "candidate"


class PolicyResolutionSource(str, Enum):
    WAVE_OVERRIDE = "wave_override"
    GLOBAL_DOMAIN_TRUST = "global_domain_trust"
    DEFAULT = "default"
