import pytest
from workers.merger import SummaryMerger


@pytest.fixture
def merger():
    return SummaryMerger(similarity_threshold=0.85)


def test_merge_summaries(merger):
    summaries = [
        {
            "summary": "First part of the meeting",
            "decisions": [{"text": "Approve budget", "confidence": 0.9}],
            "action_items": [{"text": "Send email", "owner": "Alice", "due_date_iso": "2025-11-01"}],
            "topics": [{"name": "Budget", "confidence": 0.9}],
        },
        {
            "summary": "Second part of the meeting",
            "decisions": [{"text": "Hire new developer", "confidence": 0.85}],
            "action_items": [{"text": "Review resumes", "owner": "Bob", "due_date_iso": "2025-11-05"}],
            "topics": [{"name": "Hiring", "confidence": 0.88}],
        },
    ]
    
    merged = merger.merge_summaries(summaries)
    
    assert "summary" in merged
    assert len(merged["decisions"]) == 2
    assert len(merged["action_items"]) == 2
    assert len(merged["topics"]) == 2


def test_deduplicate_decisions(merger):
    summaries = [
        {
            "summary": "Test",
            "decisions": [
                {"text": "Approve the budget for Q4", "confidence": 0.9},
                {"text": "Approve the budget for Q4", "confidence": 0.85},
            ],
            "action_items": [],
            "topics": [],
        }
    ]
    
    merged = merger.merge_summaries(summaries)
    
    assert len(merged["decisions"]) == 1
    assert merged["decisions"][0]["confidence"] == 0.9


def test_deduplicate_action_items(merger):
    summaries = [
        {
            "summary": "Test",
            "decisions": [],
            "action_items": [
                {"text": "Send email to team", "owner": None, "due_date_iso": None},
                {"text": "Send email to team", "owner": "Alice", "due_date_iso": "2025-11-01"},
            ],
            "topics": [],
        }
    ]
    
    merged = merger.merge_summaries(summaries)
    
    assert len(merged["action_items"]) == 1
    assert merged["action_items"][0]["owner"] == "Alice"
    assert merged["action_items"][0]["due_date_iso"] == "2025-11-01"


def test_similarity(merger):
    text1 = "Approve the budget"
    text2 = "Approve the budget"
    text3 = "Reject the proposal"
    
    similarity1 = merger._similarity(text1, text2)
    similarity2 = merger._similarity(text1, text3)
    
    assert similarity1 == 1.0
    assert similarity2 < 0.5
