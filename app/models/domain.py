from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class MemoryTier(str, Enum):
    LOCAL_SENSITIVE = "local_sensitive"
    ENCRYPTED_OPERATIONAL = "encrypted_operational"
    EPHEMERAL = "ephemeral"


class Confidence(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class InterventionType(str, Enum):
    RISK = "risk"
    OPPORTUNITY = "opportunity"
    THRESHOLD = "threshold"
    REVIEW = "review"
    ACCOUNTABILITY = "accountability"


class Goal(BaseModel):
    name: str
    description: str
    status: str = "active"
    horizon: str | None = None
    next_action: str | None = None
    review_date: str | None = None
    evidence: list[str] = Field(default_factory=list)
    tier: MemoryTier = MemoryTier.ENCRYPTED_OPERATIONAL


class Commitment(BaseModel):
    title: str
    due_date: str | None = None
    status: str = "open"
    source: str = "manual"
    reason: str | None = None
    tier: MemoryTier = MemoryTier.ENCRYPTED_OPERATIONAL


class Observation(BaseModel):
    category: str
    content: str
    evidence: list[str] = Field(default_factory=list)
    confidence: Confidence = Confidence.MEDIUM
    tier: MemoryTier = MemoryTier.ENCRYPTED_OPERATIONAL
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Intervention(BaseModel):
    type: InterventionType
    message: str
    evidence: list[str] = Field(default_factory=list)
    confidence: Confidence
    recommended_action: str | None = None
    requires_approval: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
