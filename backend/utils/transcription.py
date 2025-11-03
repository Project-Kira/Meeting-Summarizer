"""
Audio transcription module using OpenAI Whisper.
Handles audio file transcription with support for multiple formats.
"""

from pathlib import Path
from typing import Optional, Dict, Any, List
import logging
import whisper
from whisper.model import Whisper
import config

logger = logging.getLogger(__name__)

# Global model instance (loaded once, reused for all requests)
_whisper_model: Optional[Whisper] = None

# Supported audio formats
SUPPORTED_FORMATS = {'.mp3', '.wav', '.m4a', '.ogg', '.flac', '.aac', '.wma', '.webm'}


def _get_whisper_model() -> Whisper:
    """
    Get or initialize the Whisper model.
    Model is loaded once and cached for subsequent requests.
    """
    global _whisper_model
    
    if _whisper_model is None:
        try:
            logger.info(f"Loading Whisper model: {config.WHISPER_MODEL} on {config.WHISPER_DEVICE}")
            _whisper_model = whisper.load_model(config.WHISPER_MODEL, device=config.WHISPER_DEVICE)
            logger.info("Whisper model loaded successfully")
        except Exception as e:
            error_msg = f"Failed to load Whisper model: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
    
    return _whisper_model


def validate_audio_file(file_path: str) -> bool:
    """
    Validate that the audio file exists and has a supported format.
    
    Args:
        file_path: Path to the audio file
        
    Returns:
        True if valid, False otherwise
    """
    path = Path(file_path)
    
    if not path.exists():
        logger.error(f"Audio file not found: {file_path}")
        return False
    
    if not path.is_file():
        logger.error(f"Path is not a file: {file_path}")
        return False
    
    if path.suffix.lower() not in SUPPORTED_FORMATS:
        logger.error(f"Unsupported format: {path.suffix}. Supported: {', '.join(SUPPORTED_FORMATS)}")
        return False
    
    return True


def transcribe_audio(
    audio_path: str,
    language: Optional[str] = None,
    task: str = "transcribe",
    verbose: bool = False
) -> Dict[str, Any]:
    """
    Transcribe audio file to text using Whisper.
    
    Args:
        audio_path: Path to the audio file
        language: Language code (e.g., 'en', 'es'). None for auto-detection
        task: Either 'transcribe' or 'translate' (translate converts to English)
        verbose: Whether to print progress
        
    Returns:
        Dictionary containing:
            - text: Full transcription text
            - segments: List of timestamped segments
            - language: Detected/specified language
            - duration: Total audio duration in seconds
            
    Raises:
        ValueError: If input is invalid
        RuntimeError: If transcription fails
    """
    # Validate inputs
    if not audio_path or not audio_path.strip():
        raise ValueError("Audio path cannot be empty")
    
    if not validate_audio_file(audio_path):
        raise ValueError(f"Invalid audio file: {audio_path}")
    
    if task not in ["transcribe", "translate"]:
        raise ValueError(f"Invalid task: {task}. Must be 'transcribe' or 'translate'")
    
    # Use config language if not specified
    if language is None:
        language = config.WHISPER_LANGUAGE if config.WHISPER_LANGUAGE != "auto" else None
    
    try:
        logger.info(f"Transcribing: {audio_path} (lang: {language or 'auto'}, task: {task})")
        
        # Load model and transcribe
        model = _get_whisper_model()
        
        result = model.transcribe(
            audio_path,
            language=language,
            task=task,
            verbose=verbose,
            fp16=False  # Disable FP16 for better compatibility
        )
        
        # Extract and format results
        transcription = {
            'text': result['text'].strip(),
            'segments': result.get('segments', []),
            'language': result.get('language', language or 'unknown'),
            'duration': sum(seg.get('end', 0) for seg in result.get('segments', [])),
        }
        
        logger.info(
            f"Transcription complete: {transcription['language']}, "
            f"{transcription['duration']:.1f}s, {len(transcription['text'])} chars"
        )
        
        return transcription
        
    except Exception as e:
        error_msg = f"Transcription failed: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg)


def transcribe_audio_simple(audio_path: str) -> str:
    """
    Simple transcription that returns just the text.
    
    Args:
        audio_path: Path to the audio file
        
    Returns:
        Transcribed text as string
    """
    result = transcribe_audio(audio_path)
    return result['text']


def get_supported_formats() -> List[str]:
    """
    Get list of supported audio file formats.
    
    Returns:
        Sorted list of supported file extensions (e.g., ['.mp3', '.wav', ...])
    """
    return sorted(list(SUPPORTED_FORMATS))
