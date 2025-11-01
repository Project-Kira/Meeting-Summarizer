#!/usr/bin/env python3
"""
Example WebSocket client for meeting summarization
"""
import asyncio
import websockets
import json
import httpx
from uuid import UUID


async def stream_meeting_updates(meeting_id: str):
    """Connect to WebSocket and receive real-time summary updates"""
    
    uri = f"ws://localhost:8000/meetings/{meeting_id}/stream"
    
    print(f"Connecting to {uri}...")
    
    try:
        async with websockets.connect(uri) as websocket:
            print(f"✓ Connected to meeting {meeting_id}")
            print("Listening for summary updates...\n")
            
            async for message in websocket:
                data = json.loads(message)
                print(f"[{data.get('type')}] Update received:")
                print(json.dumps(data, indent=2))
                print("-" * 60)
                
    except websockets.exceptions.ConnectionClosed:
        print("Connection closed")
    except Exception as e:
        print(f"Error: {e}")


async def simulate_meeting():
    """Create a meeting, send segments, and listen for updates"""
    
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient() as client:
        print("Creating new meeting...")
        response = await client.post(
            f"{base_url}/meetings",
            json={
                "title": "Example Meeting",
                "metadata": {"source": "example_client"}
            }
        )
        
        meeting_data = response.json()
        meeting_id = meeting_data["id"]
        print(f"✓ Created meeting: {meeting_id}\n")
        
        ws_task = asyncio.create_task(stream_meeting_updates(meeting_id))
        
        await asyncio.sleep(2)
        
        segments = [
            ("Alice", "Let's start with our product roadmap discussion."),
            ("Bob", "I think we should prioritize the mobile app development."),
            ("Charlie", "Agreed. We also need to allocate budget for the marketing campaign."),
            ("Alice", "Good points. Bob, can you prepare a timeline by next Friday?"),
            ("Bob", "Sure, I'll have it ready by November 8th."),
        ]
        
        print("Sending segments...\n")
        for i, (speaker, text) in enumerate(segments):
            await client.post(
                f"{base_url}/ingest/segment",
                json={
                    "meeting_id": meeting_id,
                    "speaker": speaker,
                    "timestamp_iso": f"2025-10-31T14:0{i}:00Z",
                    "text_segment": text,
                }
            )
            print(f"✓ Sent: [{speaker}] {text}")
            await asyncio.sleep(1)
        
        print("\nWaiting for summaries...")
        await asyncio.sleep(10)
        
        print("\nFinalizing meeting...")
        await client.post(f"{base_url}/meetings/{meeting_id}/finalize")
        
        await asyncio.sleep(5)
        
        response = await client.get(f"{base_url}/meetings/{meeting_id}/summary?summary_type=final")
        if response.status_code == 200:
            summary = response.json()
            print("\n" + "=" * 60)
            print("FINAL SUMMARY")
            print("=" * 60)
            print(json.dumps(summary["content"], indent=2))
        
        ws_task.cancel()


if __name__ == "__main__":
    print("Meeting Summarizer - WebSocket Client Example")
    print("=" * 60)
    print()
    
    try:
        asyncio.run(simulate_meeting())
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
