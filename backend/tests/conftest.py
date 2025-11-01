import pytest
import asyncio
from uuid import uuid4
from datetime import datetime


pytest_plugins = ('pytest_asyncio',)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def sample_meeting_id():
    return uuid4()


@pytest.fixture
def sample_segments():
    return [
        {
            "id": str(uuid4()),
            "speaker": "Alice",
            "ts": "2025-10-31T10:00:00",
            "text": "Let's start the meeting. First, I'd like to discuss our Q4 goals.",
        },
        {
            "id": str(uuid4()),
            "speaker": "Bob",
            "ts": "2025-10-31T10:01:30",
            "text": "Sounds good. I think we should focus on three main objectives.",
        },
        {
            "id": str(uuid4()),
            "speaker": "Alice",
            "ts": "2025-10-31T10:02:15",
            "text": "Agreed. Let's make sure everyone reviews the budget by next week.",
        },
        {
            "id": str(uuid4()),
            "speaker": "Charlie",
            "ts": "2025-10-31T10:03:00",
            "text": "I'll send out the updated spreadsheet tomorrow morning.",
        },
    ]


@pytest.fixture
def sample_summary():
    return {
        "summary": "Team meeting discussing Q4 goals and budget review",
        "decisions": [
            {"text": "Focus on three main objectives for Q4", "confidence": 0.9}
        ],
        "action_items": [
            {
                "text": "Review budget by next week",
                "owner": "Everyone",
                "due_date_iso": "2025-11-07",
                "confidence": 0.85,
            },
            {
                "text": "Send updated spreadsheet",
                "owner": "Charlie",
                "due_date_iso": "2025-11-01",
                "confidence": 0.9,
            },
        ],
        "topics": [
            {"name": "Q4 Goals", "confidence": 0.95},
            {"name": "Budget Review", "confidence": 0.9},
        ],
    }
