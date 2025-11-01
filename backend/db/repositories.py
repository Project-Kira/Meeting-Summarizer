from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID
import json
import asyncpg

from db.connection import get_connection
from models.schemas import (
    SummaryType,
    JobStatus,
    JobType,
    MeetingResponse,
    SegmentResponse,
    SummaryResponse,
    JobResponse,
)


class MeetingRepository:
    @staticmethod
    async def create(title: str, metadata: Dict[str, Any] = None) -> UUID:
        async with get_connection() as conn:
            row = await conn.fetchrow(
                "INSERT INTO meetings (title, metadata) VALUES ($1, $2) RETURNING id",
                title,
                json.dumps(metadata or {}),
            )
            return row["id"]

    @staticmethod
    async def get_by_id(meeting_id: UUID) -> Optional[MeetingResponse]:
        async with get_connection() as conn:
            row = await conn.fetchrow("SELECT * FROM meetings WHERE id = $1", meeting_id)
            if not row:
                return None
            return MeetingResponse(**dict(row))

    @staticmethod
    async def finalize(meeting_id: UUID) -> bool:
        async with get_connection() as conn:
            result = await conn.execute(
                "UPDATE meetings SET finalized = TRUE, finalized_at = NOW() WHERE id = $1",
                meeting_id,
            )
            return result != "UPDATE 0"

    @staticmethod
    async def count_active() -> int:
        async with get_connection() as conn:
            return await conn.fetchval("SELECT COUNT(*) FROM meetings WHERE NOT finalized")


class SegmentRepository:
    @staticmethod
    async def create(
        meeting_id: UUID, speaker: str, ts: datetime, text: str, token_count: int
    ) -> UUID:
        async with get_connection() as conn:
            row = await conn.fetchrow(
                """INSERT INTO segments (meeting_id, speaker, ts, text, token_count)
                   VALUES ($1, $2, $3, $4, $5) RETURNING id""",
                meeting_id,
                speaker,
                ts,
                text,
                token_count,
            )
            return row["id"]

    @staticmethod
    async def get_by_meeting(meeting_id: UUID, limit: int = 1000) -> List[SegmentResponse]:
        async with get_connection() as conn:
            rows = await conn.fetch(
                "SELECT * FROM segments WHERE meeting_id = $1 ORDER BY ts LIMIT $2",
                meeting_id,
                limit,
            )
            return [SegmentResponse(**dict(row)) for row in rows]

    @staticmethod
    async def get_unsummarized_segments(
        meeting_id: UUID, since: Optional[datetime] = None
    ) -> List[SegmentResponse]:
        async with get_connection() as conn:
            if since:
                rows = await conn.fetch(
                    "SELECT * FROM segments WHERE meeting_id = $1 AND created_at > $2 ORDER BY ts",
                    meeting_id,
                    since,
                )
            else:
                rows = await conn.fetch(
                    "SELECT * FROM segments WHERE meeting_id = $1 ORDER BY ts", meeting_id
                )
            return [SegmentResponse(**dict(row)) for row in rows]

    @staticmethod
    async def get_total_tokens(meeting_id: UUID) -> int:
        async with get_connection() as conn:
            result = await conn.fetchval(
                "SELECT COALESCE(SUM(token_count), 0) FROM segments WHERE meeting_id = $1",
                meeting_id,
            )
            return result or 0


class SummaryRepository:
    @staticmethod
    async def create(
        meeting_id: UUID, summary_type: SummaryType, content: Dict[str, Any]
    ) -> UUID:
        async with get_connection() as conn:
            row = await conn.fetchrow(
                "INSERT INTO summaries (meeting_id, type, content) VALUES ($1, $2, $3) RETURNING id",
                meeting_id,
                summary_type.value,
                json.dumps(content),
            )
            await conn.execute("NOTIFY summary_update, $1", str(meeting_id))
            return row["id"]

    @staticmethod
    async def get_latest(
        meeting_id: UUID, summary_type: Optional[SummaryType] = None
    ) -> Optional[SummaryResponse]:
        async with get_connection() as conn:
            if summary_type:
                row = await conn.fetchrow(
                    """SELECT * FROM summaries WHERE meeting_id = $1 AND type = $2
                       ORDER BY created_at DESC LIMIT 1""",
                    meeting_id,
                    summary_type.value,
                )
            else:
                row = await conn.fetchrow(
                    "SELECT * FROM summaries WHERE meeting_id = $1 ORDER BY created_at DESC LIMIT 1",
                    meeting_id,
                )
            if not row:
                return None
            return SummaryResponse(**dict(row))

    @staticmethod
    async def get_all_incremental(meeting_id: UUID) -> List[SummaryResponse]:
        async with get_connection() as conn:
            rows = await conn.fetch(
                """SELECT * FROM summaries WHERE meeting_id = $1 AND type = 'incremental'
                   ORDER BY created_at""",
                meeting_id,
            )
            return [SummaryResponse(**dict(row)) for row in rows]


class JobRepository:
    @staticmethod
    async def create(meeting_id: UUID, job_type: JobType, payload: Dict[str, Any] = None) -> UUID:
        async with get_connection() as conn:
            row = await conn.fetchrow(
                "INSERT INTO jobs (meeting_id, type, payload) VALUES ($1, $2, $3) RETURNING id",
                meeting_id,
                job_type.value,
                json.dumps(payload or {}),
            )
            return row["id"]

    @staticmethod
    async def get_pending(limit: int = 10) -> List[JobResponse]:
        async with get_connection() as conn:
            rows = await conn.fetch(
                """SELECT * FROM jobs WHERE status = 'pending'
                   ORDER BY created_at LIMIT $1""",
                limit,
            )
            return [JobResponse(**dict(row)) for row in rows]

    @staticmethod
    async def update_status(
        job_id: UUID, status: JobStatus, error: Optional[str] = None
    ) -> bool:
        async with get_connection() as conn:
            if status == JobStatus.COMPLETED:
                result = await conn.execute(
                    """UPDATE jobs SET status = $1, completed_at = NOW()
                       WHERE id = $2""",
                    status.value,
                    job_id,
                )
            else:
                result = await conn.execute(
                    "UPDATE jobs SET status = $1, last_error = $2 WHERE id = $3",
                    status.value,
                    error,
                    job_id,
                )
            return result != "UPDATE 0"

    @staticmethod
    async def increment_attempts(job_id: UUID) -> int:
        async with get_connection() as conn:
            row = await conn.fetchrow(
                "UPDATE jobs SET attempts = attempts + 1 WHERE id = $1 RETURNING attempts",
                job_id,
            )
            return row["attempts"] if row else 0

    @staticmethod
    async def count_by_status(status: JobStatus) -> int:
        async with get_connection() as conn:
            return await conn.fetchval(
                "SELECT COUNT(*) FROM jobs WHERE status = $1", status.value
            )
