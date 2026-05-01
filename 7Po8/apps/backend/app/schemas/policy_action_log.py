from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict

from app.models.common import SourceLifecycleState, SourceTrustTier


class PolicyActionLogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    wave_id: int
    discovered_source_id: int
    domain: str | None
    action_type: str
    previous_status: SourceLifecycleState
    new_status: SourceLifecycleState
    previous_lifecycle_state: SourceLifecycleState
    new_lifecycle_state: SourceLifecycleState
    previous_trust_tier: SourceTrustTier
    new_trust_tier: SourceTrustTier
    previous_policy_context: dict[str, Any] | None
    new_policy_context: dict[str, Any] | None
    reason: str
    triggered_by: str
    created_at: datetime
