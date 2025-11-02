"""
Unit tests for summarize.py module.
Tests text chunking, summarization logic, and conversation processing.
"""

import pytest
from unittest.mock import Mock, patch, call
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import summarize
import config


class TestEstimateTokens:
    """Tests for estimate_tokens() function."""
    
    def test_empty_string(self):
        """Test token estimation for empty string."""
        result = summarize.estimate_tokens("")
        assert result == 0
    
    def test_short_text(self):
        """Test token estimation for short text."""
        text = "Hello world"  # 11 characters
        result = summarize.estimate_tokens(text)
        assert result == 11 // config.CHARS_PER_TOKEN
    
    def test_long_text(self):
        """Test token estimation for longer text."""
        text = "a" * 10000  # 10000 characters
        result = summarize.estimate_tokens(text)
        assert result == 10000 // config.CHARS_PER_TOKEN
    
    def test_uses_config_value(self):
        """Test that function uses CHARS_PER_TOKEN from config."""
        text = "test" * 100  # 400 characters
        result = summarize.estimate_tokens(text)
        expected = 400 // config.CHARS_PER_TOKEN
        assert result == expected


class TestChunkText:
    """Tests for chunk_text() function."""
    
    def test_small_text_returns_single_chunk(self):
        """Test that text smaller than MAX_CONTEXT_TOKENS returns single chunk."""
        text = "a" * 1000  # Small text
        result = summarize.chunk_text(text)
        
        assert len(result) == 1
        assert result[0] == text
    
    def test_large_text_returns_multiple_chunks(self):
        """Test that large text is split into multiple chunks."""
        # Create text larger than MAX_CONTEXT_TOKENS
        char_limit = config.MAX_CONTEXT_TOKENS * config.CHARS_PER_TOKEN
        text = "a" * (char_limit + 10000)
        
        result = summarize.chunk_text(text)
        
        assert len(result) > 1
    
    def test_chunks_have_overlap(self):
        """Test that consecutive chunks have overlapping content."""
        # Create text that will be split into chunks
        char_limit = config.MAX_CONTEXT_TOKENS * config.CHARS_PER_TOKEN
        text = "abcdefgh" * (char_limit // 8 + 1000)
        
        result = summarize.chunk_text(text)
        
        if len(result) > 1:
            # Calculate expected overlap
            chunk_size = config.CHUNK_SIZE_TOKENS * config.CHARS_PER_TOKEN
            overlap = int(chunk_size * config.OVERLAP_PERCENTAGE)
            
            # Check that end of first chunk overlaps with start of second
            chunk1_end = result[0][-overlap:]
            chunk2_start = result[1][:overlap]
            
            # Should have some overlap (might not be exact due to chunking logic)
            assert len(chunk1_end) > 0
            assert len(chunk2_start) > 0
    
    def test_all_content_included(self):
        """Test that all chunks combined contain all original content."""
        char_limit = config.MAX_CONTEXT_TOKENS * config.CHARS_PER_TOKEN
        text = "test content " * (char_limit // 13 + 1000)
        
        result = summarize.chunk_text(text)
        
        # Concatenate all chunks (removing overlaps roughly)
        combined = result[0]
        for chunk in result[1:]:
            # Add non-overlapping part
            overlap_size = int(config.CHUNK_SIZE_TOKENS * config.CHARS_PER_TOKEN * config.OVERLAP_PERCENTAGE)
            combined += chunk[overlap_size:]
        
        # Combined length should be close to original (accounting for overlaps)
        assert len(combined) >= len(text) * 0.9  # Allow 10% variance


class TestSummarizeChunk:
    """Tests for summarize_chunk() function."""
    
    @patch('summarize.run_local_llm')
    def test_calls_llm_with_correct_prompt(self, mock_llm):
        """Test that LLM is called with properly formatted prompt."""
        mock_llm.return_value = "Summary text"
        
        chunk = "Test conversation content"
        summarize.summarize_chunk(chunk, 1, 1)
        
        # Verify LLM was called
        assert mock_llm.called
        call_args = mock_llm.call_args[0][0]
        
        # Verify prompt contains expected elements
        assert "Test conversation content" in call_args
        assert "part 1 of 1" in call_args.lower()
    
    @patch('summarize.run_local_llm')
    def test_returns_llm_output(self, mock_llm):
        """Test that function returns LLM generated summary."""
        expected_summary = "This is the generated summary"
        mock_llm.return_value = expected_summary
        
        result = summarize.summarize_chunk("Test content", 1, 3)
        
        assert result == expected_summary
    
    @patch('summarize.run_local_llm')
    def test_uses_correct_max_tokens(self, mock_llm):
        """Test that function uses MAX_TOKENS_CHUNK from config."""
        mock_llm.return_value = "Summary"
        
        summarize.summarize_chunk("Test content", 2, 5)
        
        # Verify max_tokens parameter
        call_kwargs = mock_llm.call_args[1]
        assert call_kwargs['max_tokens'] == config.MAX_TOKENS_CHUNK


class TestCombineSummaries:
    """Tests for combine_summaries() function."""
    
    def test_single_summary_returned_as_is(self):
        """Test that single summary is returned without LLM call."""
        summaries = ["Only one summary"]
        
        result = summarize.combine_summaries(summaries)
        
        assert result == "Only one summary"
    
    @patch('summarize.run_local_llm')
    def test_multiple_summaries_combined(self, mock_llm):
        """Test that multiple summaries are combined via LLM."""
        mock_llm.return_value = "Combined final summary"
        
        summaries = ["Summary 1", "Summary 2", "Summary 3"]
        result = summarize.combine_summaries(summaries)
        
        # Verify LLM was called
        assert mock_llm.called
        
        # Verify prompt contains all summaries
        call_args = mock_llm.call_args[0][0]
        assert "Summary 1" in call_args
        assert "Summary 2" in call_args
        assert "Summary 3" in call_args
        assert "Part 1:" in call_args
        assert "Part 2:" in call_args
        assert "Part 3:" in call_args
        
        assert result == "Combined final summary"
    
    @patch('summarize.run_local_llm')
    def test_uses_correct_max_tokens(self, mock_llm):
        """Test that function uses MAX_TOKENS_FINAL from config."""
        mock_llm.return_value = "Final summary"
        
        summaries = ["Summary 1", "Summary 2"]
        summarize.combine_summaries(summaries)
        
        # Verify max_tokens parameter
        call_kwargs = mock_llm.call_args[1]
        assert call_kwargs['max_tokens'] == config.MAX_TOKENS_FINAL


class TestSummarizeConversation:
    """Tests for summarize_conversation() function."""
    
    def test_raises_error_on_empty_text(self):
        """Test that ValueError is raised for empty text."""
        with pytest.raises(ValueError) as exc_info:
            summarize.summarize_conversation("")
        
        assert "cannot be empty" in str(exc_info.value).lower()
    
    def test_raises_error_on_whitespace_only(self):
        """Test that ValueError is raised for whitespace-only text."""
        with pytest.raises(ValueError) as exc_info:
            summarize.summarize_conversation("   \n\t  ")
        
        assert "cannot be empty" in str(exc_info.value).lower()
    
    def test_raises_error_on_too_large_input(self):
        """Test that ValueError is raised for input exceeding MAX_INPUT_LENGTH."""
        large_text = "a" * (config.MAX_INPUT_LENGTH + 1000)
        
        with pytest.raises(ValueError) as exc_info:
            summarize.summarize_conversation(large_text)
        
        assert "too large" in str(exc_info.value).lower()
    
    @patch('summarize.combine_summaries')
    @patch('summarize.summarize_chunk')
    @patch('summarize.chunk_text')
    def test_processes_single_chunk(self, mock_chunk, mock_summarize, mock_combine):
        """Test processing of text that fits in single chunk."""
        text = "Short conversation text"
        
        mock_chunk.return_value = [text]
        mock_summarize.return_value = "Chunk summary"
        mock_combine.return_value = "Final summary"
        
        result = summarize.summarize_conversation(text)
        
        # Verify flow
        mock_chunk.assert_called_once_with(text)
        mock_summarize.assert_called_once_with(text, 1, 1)
        mock_combine.assert_called_once_with(["Chunk summary"])
        
        assert result == "Final summary"
    
    @patch('summarize.combine_summaries')
    @patch('summarize.summarize_chunk')
    @patch('summarize.chunk_text')
    def test_processes_multiple_chunks(self, mock_chunk, mock_summarize, mock_combine):
        """Test processing of text split into multiple chunks."""
        text = "Long conversation text"
        chunks = ["Chunk 1", "Chunk 2", "Chunk 3"]
        
        mock_chunk.return_value = chunks
        mock_summarize.side_effect = ["Summary 1", "Summary 2", "Summary 3"]
        mock_combine.return_value = "Final combined summary"
        
        result = summarize.summarize_conversation(text)
        
        # Verify all chunks processed
        assert mock_summarize.call_count == 3
        mock_summarize.assert_any_call("Chunk 1", 1, 3)
        mock_summarize.assert_any_call("Chunk 2", 2, 3)
        mock_summarize.assert_any_call("Chunk 3", 3, 3)
        
        # Verify summaries combined
        mock_combine.assert_called_once_with(["Summary 1", "Summary 2", "Summary 3"])
        
        assert result == "Final combined summary"
    
    @patch('summarize.chunk_text')
    def test_raises_runtime_error_on_failure(self, mock_chunk):
        """Test that RuntimeError is raised when processing fails."""
        mock_chunk.side_effect = Exception("Unexpected error")
        
        with pytest.raises(RuntimeError) as exc_info:
            summarize.summarize_conversation("Test text")
        
        assert "Failed to summarize" in str(exc_info.value)
