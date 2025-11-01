from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime
from uuid import UUID
import logging
from typing import Optional

from config import get_settings
from db import (
    init_db_pool,
    close_db_pool,
    MeetingRepository,
    SegmentRepository,
    SummaryRepository,
    JobRepository,
)
from models import (
    SegmentIngestRequest,
    SegmentIngestResponse,
    MeetingCreate,
    MeetingResponse,
    SummaryResponse,
    HealthResponse,
    JobType,
    SummaryType,
)
from app.notifications import notification_manager
from app.logging import setup_logging
from workers.chunker import TranscriptChunker

logger = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger.info("Starting Meeting Summarizer API...")
    await init_db_pool()
    await notification_manager.start_listener(settings.database_url)
    yield
    await notification_manager.stop_listener()
    await close_db_pool()
    logger.info("API shutdown complete")


app = FastAPI(
    title="Meeting Summarizer API",
    description="Real-time meeting transcription and summarization backend",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

chunker = TranscriptChunker()


@app.post("/meetings", response_model=MeetingResponse)
async def create_meeting(meeting: MeetingCreate):
    meeting_id = await MeetingRepository.create(meeting.title, meeting.metadata)
    result = await MeetingRepository.get_by_id(meeting_id)
    return result


@app.post("/ingest/segment", response_model=SegmentIngestResponse)
async def ingest_segment(request: SegmentIngestRequest):
    try:
        ts = datetime.fromisoformat(request.timestamp_iso.replace("Z", "+00:00"))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid timestamp format")
    
    meeting = await MeetingRepository.get_by_id(request.meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    if meeting.finalized:
        raise HTTPException(status_code=400, detail="Meeting already finalized")
    
    token_count = chunker.count_tokens(request.text_segment)
    
    segment_id = await SegmentRepository.create(
        meeting_id=request.meeting_id,
        speaker=request.speaker,
        ts=ts,
        text=request.text_segment,
        token_count=token_count,
    )
    
    total_tokens = await SegmentRepository.get_total_tokens(request.meeting_id)
    
    if total_tokens >= settings.worker_batch_tokens:
        await JobRepository.create(
            meeting_id=request.meeting_id,
            job_type=JobType.CHUNK_SUMMARY,
            payload={},
        )
        logger.info(f"Triggered chunk summary job for meeting {request.meeting_id}")
    
    return SegmentIngestResponse(segment_id=segment_id, status="accepted")


@app.websocket("/meetings/{meeting_id}/stream")
async def websocket_endpoint(websocket: WebSocket, meeting_id: UUID):
    await notification_manager.connect(meeting_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            logger.debug(f"Received WS data for meeting {meeting_id}: {data}")
    except WebSocketDisconnect:
        notification_manager.disconnect(meeting_id, websocket)
        logger.info(f"WebSocket disconnected for meeting {meeting_id}")


@app.get("/meetings/{meeting_id}/summary", response_model=Optional[SummaryResponse])
async def get_summary(meeting_id: UUID, summary_type: Optional[str] = None):
    meeting = await MeetingRepository.get_by_id(meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    st = SummaryType(summary_type) if summary_type else None
    summary = await SummaryRepository.get_latest(meeting_id, st)
    
    return summary


@app.post("/meetings/{meeting_id}/finalize")
async def finalize_meeting(meeting_id: UUID):
    meeting = await MeetingRepository.get_by_id(meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    if meeting.finalized:
        return {"status": "already_finalized"}
    
    success = await MeetingRepository.finalize(meeting_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to finalize meeting")
    
    await JobRepository.create(
        meeting_id=meeting_id,
        job_type=JobType.COMPOSE_SUMMARY,
        payload={},
    )
    
    await JobRepository.create(
        meeting_id=meeting_id,
        job_type=JobType.ANNOTATE_ACTION_ITEMS,
        payload={},
    )
    
    return {"status": "finalized", "meeting_id": str(meeting_id)}


@app.get("/healthz", response_model=HealthResponse)
async def health_check():
    db_status = "healthy"
    redis_status = "healthy"
    inference_status = "healthy"
    
    try:
        active_meetings = await MeetingRepository.count_active()
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    import httpx
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            response = await client.get(
                f"http://{settings.inference_host}:{settings.inference_port}/health"
            )
            if response.status_code != 200:
                inference_status = "unhealthy"
    except Exception:
        inference_status = "unreachable"
    
    overall_status = "healthy" if all(
        s == "healthy" for s in [db_status, inference_status]
    ) else "degraded"
    
    return HealthResponse(
        status=overall_status,
        database=db_status,
        redis=redis_status,
        inference=inference_status,
        timestamp=datetime.utcnow(),
    )


@app.get("/")
async def root():
    return {
        "service": "Meeting Summarizer API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/healthz",
    }
