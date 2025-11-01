from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
from tokenizers import Tokenizer
import json
from pathlib import Path


@dataclass
class Chunk:
    text: str
    tokens: List[int]
    token_count: int
    segment_ids: List[str]
    start_idx: int
    end_idx: int


class TranscriptChunker:
    def __init__(self, chunk_size: int = 2000, overlap_ratio: float = 0.15):
        self.chunk_size = chunk_size
        self.overlap_ratio = overlap_ratio
        self.overlap_tokens = int(chunk_size * overlap_ratio)
        
        try:
            from tokenizers import Tokenizer
            model_path = Path("/models/tokenizer.json")
            if model_path.exists():
                self.tokenizer = Tokenizer.from_file(str(model_path))
            else:
                self.tokenizer = self._create_simple_tokenizer()
        except Exception:
            self.tokenizer = self._create_simple_tokenizer()

    def _create_simple_tokenizer(self):
        class SimpleTokenizer:
            def encode(self, text: str):
                class Encoding:
                    def __init__(self, tokens):
                        self.ids = tokens
                words = text.split()
                return Encoding([hash(w) % 50000 for w in words])
            
            def decode(self, token_ids: List[int]) -> str:
                return f"<{len(token_ids)} tokens>"
        
        return SimpleTokenizer()

    def count_tokens(self, text: str) -> int:
        encoding = self.tokenizer.encode(text)
        return len(encoding.ids)

    def chunk_segments(self, segments: List[Dict[str, Any]]) -> List[Chunk]:
        formatted_text = []
        segment_boundaries = []
        
        for seg in segments:
            speaker = seg.get("speaker", "Unknown")
            ts = seg.get("ts", "")
            text = seg.get("text", "")
            seg_id = seg.get("id", "")
            
            segment_text = f"[{speaker} @ {ts}]: {text}\n"
            start_pos = len(" ".join(formatted_text))
            formatted_text.append(segment_text)
            end_pos = len(" ".join(formatted_text))
            
            segment_boundaries.append({
                "id": seg_id,
                "start": start_pos,
                "end": end_pos,
                "text": segment_text,
            })
        
        full_text = " ".join(formatted_text)
        encoding = self.tokenizer.encode(full_text)
        all_tokens = encoding.ids
        
        chunks = []
        start_idx = 0
        
        while start_idx < len(all_tokens):
            end_idx = min(start_idx + self.chunk_size, len(all_tokens))
            chunk_tokens = all_tokens[start_idx:end_idx]
            
            chunk_text = self._decode_tokens(chunk_tokens, full_text, start_idx, end_idx)
            
            affected_segments = self._find_segments_in_range(
                segment_boundaries, start_idx, end_idx
            )
            
            chunks.append(
                Chunk(
                    text=chunk_text,
                    tokens=chunk_tokens,
                    token_count=len(chunk_tokens),
                    segment_ids=[s["id"] for s in affected_segments],
                    start_idx=start_idx,
                    end_idx=end_idx,
                )
            )
            
            if end_idx >= len(all_tokens):
                break
            
            start_idx = end_idx - self.overlap_tokens

        return chunks

    def _decode_tokens(
        self, tokens: List[int], original_text: str, start_idx: int, end_idx: int
    ) -> str:
        try:
            return self.tokenizer.decode(tokens)
        except Exception:
            char_per_token = len(original_text) / max(len(self.tokenizer.encode(original_text).ids), 1)
            start_char = int(start_idx * char_per_token)
            end_char = int(end_idx * char_per_token)
            return original_text[start_char:end_char]

    def _find_segments_in_range(
        self, boundaries: List[Dict], start_idx: int, end_idx: int
    ) -> List[Dict]:
        result = []
        for seg in boundaries:
            if seg["start"] < end_idx and seg["end"] > start_idx:
                result.append(seg)
        return result

    def create_prompt(self, chunk: Chunk) -> str:
        prompt = f"""System: You are a concise meeting summarizer. Extract structured information from transcripts.

User: Given the following transcript chunk with speaker names and timestamps, return valid JSON with this exact structure:
{{
  "summary": "brief summary of this chunk",
  "decisions": [
    {{"text": "decision made", "confidence": 0.9}}
  ],
  "action_items": [
    {{"text": "action description", "owner": "person name or null", "due_date_iso": "YYYY-MM-DD or null", "confidence": 0.8}}
  ],
  "topics": [
    {{"name": "topic name", "confidence": 0.9}}
  ]
}}

Transcript chunk:
{chunk.text}
Assistant: Return only valid JSON, no additional text.
"""
        return prompt

