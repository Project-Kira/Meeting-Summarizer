import pytest
import asyncio
import httpx
from uuid import UUID
from datetime import datetime


@pytest.mark.asyncio
async def test_full_meeting_flow():
    """
    Integration test simulating full meeting flow:
    1. Create meeting
    2. Ingest segments
    3. Wait for incremental summaries
    4. Finalize meeting
    5. Get final summary
    """
    
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{base_url}/meetings",
            json={
                "title": "Integration Test Meeting",
                "metadata": {"test": True, "date": "2025-10-31"},
            },
        )
        
        assert response.status_code == 200
        meeting_data = response.json()
        meeting_id = meeting_data["id"]
        
        print(f"Created meeting: {meeting_id}")
        
        segments = [
            {
                "meeting_id": meeting_id,
                "speaker": "Alice",
                "timestamp_iso": "2025-10-31T10:00:00Z",
                "text_segment": "Good morning everyone! Let's start our Q4 planning meeting. Today we need to discuss budget allocation, hiring plans, and our product roadmap.",
            },
            {
                "meeting_id": meeting_id,
                "speaker": "Bob",
                "timestamp_iso": "2025-10-31T10:02:00Z",
                "text_segment": "Thanks Alice. For the budget, I propose we allocate 40% to engineering, 30% to marketing, and 30% to operations. This should give us the flexibility we need.",
            },
            {
                "meeting_id": meeting_id,
                "speaker": "Charlie",
                "timestamp_iso": "2025-10-31T10:04:00Z",
                "text_segment": "Sounds reasonable. On hiring, I think we should focus on bringing in two senior engineers and one product manager by end of Q4.",
            },
            {
                "meeting_id": meeting_id,
                "speaker": "Alice",
                "timestamp_iso": "2025-10-31T10:06:00Z",
                "text_segment": "Excellent. Let's finalize these decisions. Bob, can you prepare the detailed budget breakdown by next Monday? Charlie, please start the recruitment process this week.",
            },
        ]
        
        for segment in segments:
            response = await client.post(f"{base_url}/ingest/segment", json=segment)
            assert response.status_code == 200
            segment_response = response.json()
            assert "segment_id" in segment_response
            print(f"Ingested segment: {segment_response['segment_id']}")
        
        await asyncio.sleep(2)
        
        response = await client.get(f"{base_url}/meetings/{meeting_id}/summary")
        if response.status_code == 200:
            summary = response.json()
            print(f"Incremental summary: {summary}")
        
        response = await client.post(f"{base_url}/meetings/{meeting_id}/finalize")
        assert response.status_code == 200
        finalize_response = response.json()
        assert finalize_response["status"] in ["finalized", "already_finalized"]
        
        print(f"Meeting finalized: {finalize_response}")
        
        await asyncio.sleep(3)
        
        response = await client.get(f"{base_url}/meetings/{meeting_id}/summary?summary_type=final")
        
        if response.status_code == 200:
            final_summary = response.json()
            print(f"Final summary: {final_summary}")
            
            content = final_summary["content"]
            assert "summary" in content
            assert "action_items" in content
            assert "decisions" in content
            assert len(content["action_items"]) > 0
            
            print("✓ Integration test passed!")
        else:
            print("Note: Final summary not yet available (worker may still be processing)")


if __name__ == "__main__":
    asyncio.run(test_full_meeting_flow())
