from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field
from enum import Enum


class SummaryType(str, Enum):
    INCREMENTAL = "incremental"
    FINAL = "final"


class JobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class JobType(str, Enum):
    CHUNK_SUMMARY = "chunk_summary"
    COMPOSE_SUMMARY = "compose_summary"
    ANNOTATE_ACTION_ITEMS = "annotate_action_items"


class ActionItem(BaseModel):
    text: str
    owner: Optional[str] = None
    due_date_iso: Optional[str] = None
    confidence: Optional[float] = None
    source_segment_ids: List[UUID] = Field(default_factory=list)


class Decision(BaseModel):
    text: str
    confidence: Optional[float] = None
    source_segment_ids: List[UUID] = Field(default_factory=list)


class Topic(BaseModel):
    name: str
    confidence: Optional[float] = None


class SummaryContent(BaseModel):
    summary: str
    agenda: List[str] = Field(default_factory=list)
    decisions: List[Decision] = Field(default_factory=list)
    action_items: List[ActionItem] = Field(default_factory=list)
    topics: List[Topic] = Field(default_factory=list)


class SegmentIngestRequest(BaseModel):
    meeting_id: UUID
    speaker: str
    timestamp_iso: str
    text_segment: str


class SegmentIngestResponse(BaseModel):
    segment_id: UUID
    status: str


class MeetingCreate(BaseModel):
    title: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class MeetingResponse(BaseModel):
    id: UUID
    title: str
    metadata: Dict[str, Any]
    created_at: datetime
    finalized: bool
    finalized_at: Optional[datetime] = None


class SegmentResponse(BaseModel):
    id: UUID
    meeting_id: UUID
    speaker: str
    ts: datetime
    text: str
    token_count: int
    created_at: datetime


class SummaryResponse(BaseModel):
    id: UUID
    meeting_id: UUID
    type: SummaryType
    content: SummaryContent
    created_at: datetime


class JobResponse(BaseModel):
    id: UUID
    meeting_id: UUID
    type: JobType
    status: JobStatus
    attempts: int
    last_error: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None


class HealthResponse(BaseModel):
    status: str
    database: str
    redis: str
    inference: str
    timestamp: datetime


class MetricsResponse(BaseModel):
    segments_per_second: float
    avg_summary_latency_ms: float
    queue_length: int
    active_meetings: int
