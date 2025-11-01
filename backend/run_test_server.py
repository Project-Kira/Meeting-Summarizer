#!/usr/bin/env python3
"""
Simple standalone test server for Meeting Summarizer
Run with: python run_test_server.py
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from datetime import datetime
from uuid import uuid4
from typing import Dict, List, Set
import asyncio
import json

# In-memory storage
meetings = {}
segments = {}
summaries = {}
ws_connections = {}

app = FastAPI(title="Meeting Summarizer Test Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/meetings")
async def create_meeting(meeting: dict):
    meeting_id = str(uuid4())
    meeting_data = {
        "id": meeting_id,
        "title": meeting.get("title", "Untitled"),
        "metadata": meeting.get("metadata", {}),
        "created_at": datetime.utcnow().isoformat(),
        "finalized": False,
        "finalized_at": None,
    }
    meetings[meeting_id] = meeting_data
    segments[meeting_id] = []
    summaries[meeting_id] = []
    return meeting_data


@app.post("/ingest/segment")
async def ingest_segment(request: dict):
    meeting_id = str(request["meeting_id"])
    
    if meeting_id not in meetings:
        raise HTTPException(404, "Meeting not found")
    
    segment_id = str(uuid4())
    segment = {
        "id": segment_id,
        "meeting_id": meeting_id,
        "speaker": request["speaker"],
        "ts": request["timestamp_iso"],
        "text": request["text_segment"],
        "token_count": len(request["text_segment"].split()),
        "created_at": datetime.utcnow().isoformat(),
    }
    
    segments[meeting_id].append(segment)
    
    # Generate summary after 3 segments
    if len(segments[meeting_id]) >= 3 and len(summaries[meeting_id]) == 0:
        asyncio.create_task(generate_summary(meeting_id))
    
    # Notify WebSocket
    await broadcast(meeting_id, {"type": "segment_added", "segment_id": segment_id})
    
    return {"segment_id": segment_id, "status": "accepted"}


async def generate_summary(meeting_id: str):
    await asyncio.sleep(2)
    
    segs = segments.get(meeting_id, [])
    if not segs:
        return
    
    summary = {
        "id": str(uuid4()),
        "meeting_id": meeting_id,
        "type": "incremental",
        "content": {
            "summary": f"Meeting with {len(segs)} segments discussed.",
            "decisions": [{"text": "Main decisions identified", "confidence": 0.9}],
            "action_items": [
                {
                    "text": "Follow up on items",
                    "owner": segs[0]["speaker"],
                    "due_date_iso": "2025-11-07",
                    "confidence": 0.85
                }
            ],
            "topics": [{"name": "Planning", "confidence": 0.9}]
        },
        "created_at": datetime.utcnow().isoformat(),
    }
    
    summaries[meeting_id].append(summary)
    await broadcast(meeting_id, {"type": "summary_update", "meeting_id": meeting_id})


@app.get("/meetings/{meeting_id}/summary")
async def get_summary(meeting_id: str):
    if meeting_id not in meetings:
        raise HTTPException(404, "Meeting not found")
    
    sums = summaries.get(meeting_id, [])
    return sums[-1] if sums else None


@app.post("/meetings/{meeting_id}/finalize")
async def finalize_meeting(meeting_id: str):
    if meeting_id not in meetings:
        raise HTTPException(404, "Meeting not found")
    
    meetings[meeting_id]["finalized"] = True
    meetings[meeting_id]["finalized_at"] = datetime.utcnow().isoformat()
    
    asyncio.create_task(generate_final_summary(meeting_id))
    
    return {"status": "finalized", "meeting_id": meeting_id}


async def generate_final_summary(meeting_id: str):
    await asyncio.sleep(3)
    
    segs = segments.get(meeting_id, [])
    summary = {
        "id": str(uuid4()),
        "meeting_id": meeting_id,
        "type": "final",
        "content": {
            "summary": f"Final summary: {len(segs)} segments completed.",
            "decisions": [{"text": "All decisions finalized", "confidence": 0.95}],
            "action_items": [
                {
                    "text": "Complete all tasks",
                    "owner": "Team",
                    "due_date_iso": "2025-11-15",
                    "confidence": 0.9
                }
            ],
            "topics": [{"name": "Completion", "confidence": 0.95}]
        },
        "created_at": datetime.utcnow().isoformat(),
    }
    
    summaries[meeting_id].append(summary)
    await broadcast(meeting_id, {"type": "final_summary", "meeting_id": meeting_id})


@app.websocket("/meetings/{meeting_id}/stream")
async def websocket_endpoint(websocket: WebSocket, meeting_id: str):
    await websocket.accept()
    
    if meeting_id not in ws_connections:
        ws_connections[meeting_id] = set()
    ws_connections[meeting_id].add(websocket)
    
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_connections[meeting_id].discard(websocket)


async def broadcast(meeting_id: str, message: dict):
    if meeting_id in ws_connections:
        for ws in list(ws_connections[meeting_id]):
            try:
                await ws.send_json(message)
            except:
                ws_connections[meeting_id].discard(ws)


@app.get("/healthz")
async def health():
    return {
        "status": "healthy",
        "database": "in-memory",
        "redis": "disabled",
        "inference": "mock",
        "timestamp": datetime.utcnow().isoformat(),
        "meetings": len(meetings),
        "total_segments": sum(len(s) for s in segments.values()),
    }


@app.get("/")
async def root():
    return HTMLResponse("""
    <html>
    <head><title>Meeting Summarizer</title></head>
    <body style="font-family: Arial; padding: 40px; text-align: center;">
        <h1>🎙️ Meeting Summarizer Test Server</h1>
        <p>Server is running!</p>
        <p><a href="/docs">📚 API Documentation</a></p>
        <p><a href="/healthz">❤️ Health Check</a></p>
        <p><strong>Open frontend/index.html in your browser to test</strong></p>
    </body>
    </html>
    """)


if __name__ == "__main__":
    import uvicorn
    print("=" * 60)
    print("🚀 Meeting Summarizer Test Server")
    print("=" * 60)
    print("📝 API:      http://localhost:8000")
    print("📚 Docs:     http://localhost:8000/docs")
    print("❤️  Health:   http://localhost:8000/healthz")
    print("🖥️  Frontend: Open frontend/index.html in browser")
    print("=" * 60)
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
