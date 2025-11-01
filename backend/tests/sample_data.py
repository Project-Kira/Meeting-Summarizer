"""
Sample meeting transcript for testing
"""

SAMPLE_TRANSCRIPT = [
    {
        "speaker": "Sarah (CEO)",
        "timestamp_iso": "2025-10-31T14:00:00Z",
        "text_segment": "Good afternoon everyone. Thank you for joining our quarterly planning meeting. Today we need to make some important decisions about our product roadmap and resource allocation for Q4."
    },
    {
        "speaker": "Mike (CTO)",
        "timestamp_iso": "2025-10-31T14:01:30Z",
        "text_segment": "Thanks Sarah. From the engineering side, we've identified three major initiatives: migrating to microservices, implementing the new analytics dashboard, and upgrading our security infrastructure."
    },
    {
        "speaker": "Lisa (CFO)",
        "timestamp_iso": "2025-10-31T14:03:00Z",
        "text_segment": "I've reviewed the budget projections. We have approximately $500K available for Q4. I recommend prioritizing security first, then the analytics dashboard, and migrating to microservices in Q1."
    },
    {
        "speaker": "Sarah (CEO)",
        "timestamp_iso": "2025-10-31T14:05:00Z",
        "text_segment": "That makes sense. Let's make that decision official. Mike, can you prepare a detailed timeline for the security upgrade by next Friday? We'll need to present this to the board."
    },
    {
        "speaker": "Mike (CTO)",
        "timestamp_iso": "2025-10-31T14:06:00Z",
        "text_segment": "Absolutely. I'll coordinate with the security team and have a comprehensive plan ready. I'm thinking November 8th for the deadline."
    },
    {
        "speaker": "Lisa (CFO)",
        "timestamp_iso": "2025-10-31T14:07:30Z",
        "text_segment": "On the hiring front, we approved three positions last quarter but only filled one. Should we continue with the other two openings or adjust our hiring plan?"
    },
    {
        "speaker": "Sarah (CEO)",
        "timestamp_iso": "2025-10-31T14:09:00Z",
        "text_segment": "Let's keep one senior engineer position open and pause the other for now. We can revisit in December based on Q4 performance. Tom, can you update the job posting and restart recruitment?"
    },
    {
        "speaker": "Tom (HR Director)",
        "timestamp_iso": "2025-10-31T14:10:00Z",
        "text_segment": "Will do. I'll have the updated posting live by Monday and start scheduling interviews. I'm targeting to have candidates by November 15th."
    },
    {
        "speaker": "Sarah (CEO)",
        "timestamp_iso": "2025-10-31T14:11:30Z",
        "text_segment": "Perfect. Let's wrap up. To summarize our decisions: prioritize security upgrade, Mike delivers timeline by November 8th, keep one engineering position open with interviews by November 15th. Anything else?"
    },
    {
        "speaker": "Mike (CTO)",
        "timestamp_iso": "2025-10-31T14:12:00Z",
        "text_segment": "That covers everything from my end. Thanks everyone."
    },
]

EXPECTED_SUMMARY_SCHEMA = {
    "summary": str,
    "agenda": list,
    "decisions": list,
    "action_items": list,
    "topics": list,
}

EXPECTED_DECISION_EXAMPLE = {
    "text": "Prioritize security upgrade for Q4",
    "confidence": float,
}

EXPECTED_ACTION_ITEM_EXAMPLE = {
    "text": "Prepare detailed timeline for security upgrade",
    "owner": "Mike (CTO)",
    "due_date_iso": "2025-11-08",
    "confidence": float,
}
