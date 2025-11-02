"""
Summarization module that handles chunking and summarizing conversation text.
"""

import logging
from typing import List
from inference import run_local_llm
import config

# Setup logging
logger = logging.getLogger(__name__)


def estimate_tokens(text: str) -> int:
    """
    Estimate the number of tokens in a text string.
    Uses a simple approximation: 1 token ≈ 4 characters.
    
    Args:
        text: Input text string
    
    Returns:
        Estimated token count
    """
    return len(text) // config.CHARS_PER_TOKEN


def chunk_text(text: str) -> List[str]:
    """
    Split text into overlapping chunks for processing.
    
    Args:
        text: The full conversation text
    
    Returns:
        List of text chunks with overlap
    """
    estimated_tokens = estimate_tokens(text)
    
    # If text is small enough, return as single chunk
    if estimated_tokens <= config.MAX_CONTEXT_TOKENS:
        return [text]
    
    # Calculate chunk and overlap sizes in characters
    chunk_size_chars = config.CHUNK_SIZE_TOKENS * config.CHARS_PER_TOKEN
    overlap_chars = int(chunk_size_chars * config.OVERLAP_PERCENTAGE)
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size_chars
        chunk = text[start:end]
        chunks.append(chunk)
        
        # Move start forward by chunk_size minus overlap
        start += (chunk_size_chars - overlap_chars)
    
    logger.info(f"Text split into {len(chunks)} chunks")
    return chunks


def summarize_chunk(chunk: str, chunk_num: int, total_chunks: int) -> str:
    """
    Summarize a single chunk of conversation text.
    
    Args:
        chunk: Text chunk to summarize
        chunk_num: Current chunk number (1-indexed)
        total_chunks: Total number of chunks
    
    Returns:
        Summary of the chunk
    """
    prompt = f"""You are summarizing a conversation text into concise key points.

This is part {chunk_num} of {total_chunks}.

Conversation text:
{chunk}

Provide a concise summary of the key points discussed in this section. Use bullet points if appropriate."""
    
    logger.info(f"Summarizing chunk {chunk_num}/{total_chunks}...")
    summary = run_local_llm(prompt, max_tokens=config.MAX_TOKENS_CHUNK)
    return summary


def combine_summaries(chunk_summaries: List[str]) -> str:
    """
    Combine multiple chunk summaries into a final cohesive summary.
    
    Args:
        chunk_summaries: List of individual chunk summaries
    
    Returns:
        Final combined summary
    """
    if len(chunk_summaries) == 1:
        return chunk_summaries[0]
    
    combined_text = "\n\n".join([
        f"Part {i+1}:\n{summary}" 
        for i, summary in enumerate(chunk_summaries)
    ])
    
    prompt = f"""You are creating a final cohesive summary from multiple partial summaries of a conversation.

Partial summaries:
{combined_text}

Combine these partial summaries into one cohesive, well-organized summary. Remove redundancies and organize the key points logically."""
    
    logger.info("Combining summaries into final output...")
    final_summary = run_local_llm(prompt, max_tokens=config.MAX_TOKENS_FINAL)
    return final_summary


def summarize_conversation(text: str) -> str:
    """
    Main function to summarize a conversation text.
    Handles chunking if needed and returns a final summary.
    
    Args:
        text: The full conversation text from a file
    
    Returns:
        Final summary of the conversation
        
    Raises:
        ValueError: If text is empty or too large
        RuntimeError: If summarization fails
    """
    # Input validation
    if not text or not text.strip():
        raise ValueError("Conversation text cannot be empty")
    
    if len(text) > config.MAX_INPUT_LENGTH:
        raise ValueError(
            f"Input text too large: {len(text)} characters. "
            f"Maximum allowed: {config.MAX_INPUT_LENGTH} characters"
        )
    
    try:
        logger.info(f"Input text length: {len(text)} characters (~{estimate_tokens(text)} tokens)")
        
        # Step 1: Chunk the text if necessary
        chunks = chunk_text(text)
        
        # Step 2: Summarize each chunk
        chunk_summaries = []
        for i, chunk in enumerate(chunks, 1):
            summary = summarize_chunk(chunk, i, len(chunks))
            chunk_summaries.append(summary)
        
        # Step 3: Combine summaries if there are multiple chunks
        final_summary = combine_summaries(chunk_summaries)
        
        logger.info("Summarization completed successfully")
        return final_summary
        
    except Exception as e:
        logger.error(f"Summarization failed: {e}")
        raise RuntimeError(f"Failed to summarize conversation: {e}") from e


if __name__ == "__main__":
    result = summarize_conversation(test_text)
    print("\nFinal Summary:")
    print(result)
