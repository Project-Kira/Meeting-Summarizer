"""
Simplified in-memory backend for testing without PostgreSQL
"""
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from datetime import datetime
from uuid import UUID, uuid4
from typing import Dict, List, Optional, Set
import json
import asyncio

from models.schemas import (
    SegmentIngestRequest,
    SegmentIngestResponse,
    MeetingCreate,
    MeetingResponse,
    SummaryResponse,
    SummaryType,
)

# In-memory storage
meetings_db: Dict[str, dict] = {}
segments_db: Dict[str, List[dict]] = {}
summaries_db: Dict[str, List[dict]] = {}
ws_connections: Dict[str, Set[WebSocket]] = {}

app = FastAPI(
    title="Meeting Summarizer API (Test Mode)",
    description="Simplified in-memory version for testing",
    version="0.1.0-test",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/meetings", response_model=MeetingResponse)
async def create_meeting(meeting: MeetingCreate):
    meeting_id = str(uuid4())
    meeting_data = {
        "id": meeting_id,
        "title": meeting.title,
        "metadata": meeting.metadata,
        "created_at": datetime.utcnow().isoformat(),
        "finalized": False,
        "finalized_at": None,
    }
    meetings_db[meeting_id] = meeting_data
    segments_db[meeting_id] = []
    summaries_db[meeting_id] = []
    
    return MeetingResponse(**meeting_data)


@app.post("/ingest/segment", response_model=SegmentIngestResponse)
async def ingest_segment(request: SegmentIngestRequest):
    meeting_id = str(request.meeting_id)
    
    if meeting_id not in meetings_db:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    if meetings_db[meeting_id]["finalized"]:
        raise HTTPException(status_code=400, detail="Meeting already finalized")
    
    segment_id = str(uuid4())
    segment = {
        "id": segment_id,
        "meeting_id": meeting_id,
        "speaker": request.speaker,
        "ts": request.timestamp_iso,
        "text": request.text_segment,
        "token_count": len(request.text_segment.split()),
        "created_at": datetime.utcnow().isoformat(),
    }
    
    segments_db[meeting_id].append(segment)
    
    # Auto-generate mock summary after a few segments
    if len(segments_db[meeting_id]) >= 3 and len(summaries_db[meeting_id]) == 0:
        asyncio.create_task(generate_mock_summary(meeting_id))
    
    # Notify WebSocket clients
    await broadcast_to_meeting(meeting_id, {
        "type": "segment_added",
        "segment_id": segment_id,
        "count": len(segments_db[meeting_id])
    })
    
    return SegmentIngestResponse(segment_id=UUID(segment_id), status="accepted")


async def generate_mock_summary(meeting_id: str):
    """Generate a mock summary for testing"""
    await asyncio.sleep(2)  # Simulate processing time
    
    segments = segments_db.get(meeting_id, [])
    if not segments:
        return
    
    # Create mock summary
    summary_content = {
        "summary": f"Meeting discussion involving {len(segments)} segments from {len(set(s['speaker'] for s in segments))} speakers.",
        "decisions": [
            {"text": "Proceed with the proposed plan", "confidence": 0.9}
        ],
        "action_items": [
            {
                "text": "Follow up on discussed items",
                "owner": segments[0]["speaker"] if segments else "Unknown",
                "due_date_iso": "2025-11-07",
                "confidence": 0.85
            }
        ],
        "topics": [
            {"name": "Planning", "confidence": 0.9},
            {"name": "Strategy", "confidence": 0.85}
        ]
    }
    
    summary = {
        "id": str(uuid4()),
        "meeting_id": meeting_id,
        "type": "incremental",
        "content": summary_content,
        "created_at": datetime.utcnow().isoformat(),
    }
    
    summaries_db[meeting_id].append(summary)
    
    # Notify WebSocket clients
    await broadcast_to_meeting(meeting_id, {
        "type": "summary_update",
        "meeting_id": meeting_id
    })


@app.get("/meetings/{meeting_id}/summary")
async def get_summary(meeting_id: str, summary_type: Optional[str] = None):
    if meeting_id not in meetings_db:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    summaries = summaries_db.get(meeting_id, [])
    
    if not summaries:
        return None
    
    if summary_type:
        filtered = [s for s in summaries if s["type"] == summary_type]
        return filtered[-1] if filtered else None
    
    return summaries[-1]


@app.post("/meetings/{meeting_id}/finalize")
async def finalize_meeting(meeting_id: str):
    if meeting_id not in meetings_db:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    if meetings_db[meeting_id]["finalized"]:
        return {"status": "already_finalized"}
    
    meetings_db[meeting_id]["finalized"] = True
    meetings_db[meeting_id]["finalized_at"] = datetime.utcnow().isoformat()
    
    # Generate final summary
    asyncio.create_task(generate_final_summary(meeting_id))
    
    return {"status": "finalized", "meeting_id": meeting_id}


async def generate_final_summary(meeting_id: str):
    """Generate final summary"""
    await asyncio.sleep(3)
    
    segments = segments_db.get(meeting_id, [])
    if not segments:
        return
    
    summary_content = {
        "summary": f"Final summary: Meeting with {len(segments)} segments completed.",
        "decisions": [
            {"text": "All items discussed and decisions made", "confidence": 0.95}
        ],
        "action_items": [
            {
                "text": "Complete follow-up tasks",
                "owner": "Team",
                "due_date_iso": "2025-11-15",
                "confidence": 0.9
            }
        ],
        "topics": [
            {"name": "Completion", "confidence": 0.95},
            {"name": "Next Steps", "confidence": 0.9}
        ]
    }
    
    summary = {
        "id": str(uuid4()),
        "meeting_id": meeting_id,
        "type": "final",
        "content": summary_content,
        "created_at": datetime.utcnow().isoformat(),
    }
    
    summaries_db[meeting_id].append(summary)
    
    await broadcast_to_meeting(meeting_id, {
        "type": "final_summary",
        "meeting_id": meeting_id
    })


@app.websocket("/meetings/{meeting_id}/stream")
async def websocket_endpoint(websocket: WebSocket, meeting_id: str):
    await websocket.accept()
    
    if meeting_id not in ws_connections:
        ws_connections[meeting_id] = set()
    ws_connections[meeting_id].add(websocket)
    
    try:
        while True:
            data = await websocket.receive_text()
            # Echo back for testing
            await websocket.send_json({"echo": data})
    except WebSocketDisconnect:
        ws_connections[meeting_id].discard(websocket)
        if not ws_connections[meeting_id]:
            del ws_connections[meeting_id]


async def broadcast_to_meeting(meeting_id: str, message: dict):
    """Broadcast message to all WebSocket connections for a meeting"""
    if meeting_id in ws_connections:
        disconnected = set()
        for ws in ws_connections[meeting_id]:
            try:
                await ws.send_json(message)
            except:
                disconnected.add(ws)
        
        for ws in disconnected:
            ws_connections[meeting_id].discard(ws)


@app.get("/healthz")
async def health_check():
    return {
        "status": "healthy",
        "database": "in-memory",
        "redis": "disabled",
        "inference": "mock",
        "timestamp": datetime.utcnow().isoformat(),
        "meetings": len(meetings_db),
        "total_segments": sum(len(segs) for segs in segments_db.values()),
    }


@app.get("/")
async def root():
    return {
        "service": "Meeting Summarizer API (Test Mode)",
        "version": "0.1.0-test",
        "mode": "in-memory",
        "docs": "/docs",
        "health": "/healthz",
        "frontend": "Open frontend/index.html in your browser",
    }


@app.get("/frontend")
async def serve_frontend():
    """Redirect to frontend"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse("/docs")


if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Meeting Summarizer Test Server...")
    print("📝 API: http://localhost:8000")
    print("📚 Docs: http://localhost:8000/docs")
    print("🖥️  Frontend: http://localhost:8000/frontend")
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
