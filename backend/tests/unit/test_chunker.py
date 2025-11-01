import pytest
from workers.chunker import TranscriptChunker, Chunk


@pytest.fixture
def chunker():
    return TranscriptChunker(chunk_size=100, overlap_ratio=0.15)


def test_count_tokens(chunker):
    text = "This is a test sentence with multiple words."
    token_count = chunker.count_tokens(text)
    assert token_count > 0
    assert isinstance(token_count, int)


def test_chunk_segments(chunker):
    segments = [
        {
            "id": "seg1",
            "speaker": "Alice",
            "ts": "2025-10-31T10:00:00",
            "text": "Hello everyone, let's start the meeting.",
        },
        {
            "id": "seg2",
            "speaker": "Bob",
            "ts": "2025-10-31T10:01:00",
            "text": "Sounds good. I have three items on my agenda today.",
        },
        {
            "id": "seg3",
            "speaker": "Alice",
            "ts": "2025-10-31T10:02:00",
            "text": "Great! Let's go through them one by one.",
        },
    ]
    
    chunks = chunker.chunk_segments(segments)
    
    assert len(chunks) > 0
    assert all(isinstance(chunk, Chunk) for chunk in chunks)
    assert all(chunk.token_count > 0 for chunk in chunks)
    assert all(len(chunk.segment_ids) > 0 for chunk in chunks)


def test_create_prompt(chunker):
    chunk = Chunk(
        text="[Alice @ 2025-10-31T10:00:00]: Let's discuss the project timeline.",
        tokens=[1, 2, 3, 4],
        token_count=4,
        segment_ids=["seg1"],
        start_idx=0,
        end_idx=4,
    )
    
    prompt = chunker.create_prompt(chunk)
    
    assert "System:" in prompt
    assert "User:" in prompt
    assert "JSON" in prompt
    assert chunk.text in prompt


def test_chunk_overlap(chunker):
    segments = [
        {
            "id": f"seg{i}",
            "speaker": "Speaker",
            "ts": f"2025-10-31T10:00:{i:02d}",
            "text": " ".join([f"word{j}" for j in range(50)]),
        }
        for i in range(10)
    ]
    
    chunks = chunker.chunk_segments(segments)
    
    if len(chunks) > 1:
        first_chunk_end = chunks[0].end_idx
        second_chunk_start = chunks[1].start_idx
        overlap = first_chunk_end - second_chunk_start
        assert overlap > 0, "Chunks should have overlap"
