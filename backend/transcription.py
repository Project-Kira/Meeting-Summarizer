from pathlib import Path
from typing import Optional, Dict, Any, List
import whisper
from whisper.model import Whisper
import config
from logger import setup_logging

logger = setup_logging(__name__)
_whisper_model: Optional[Whisper] = None
SUPPORTED_FORMATS = {'.mp3', '.wav', '.m4a', '.ogg', '.flac', '.aac', '.wma', '.webm'}


def _get_whisper_model() -> Whisper:
    global _whisper_model
    
    if _whisper_model is None:
        try:
            logger.info(f"Loading Whisper model: {config.WHISPER_MODEL} on {config.WHISPER_DEVICE}")
            _whisper_model = whisper.load_model(config.WHISPER_MODEL, device=config.WHISPER_DEVICE)
            logger.info("Whisper model loaded")
        except Exception as e:
            error_msg = f"Failed to load Whisper model: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
    
    return _whisper_model


def validate_audio_file(file_path: str) -> bool:
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
    if not audio_path or not audio_path.strip():
        raise ValueError("Audio path cannot be empty")
    
    if not validate_audio_file(audio_path):
        raise ValueError(f"Invalid audio file: {audio_path}")
    
    if task not in ["transcribe", "translate"]:
        raise ValueError(f"Invalid task: {task}")
    
    if language is None:
        language = config.WHISPER_LANGUAGE if config.WHISPER_LANGUAGE != "auto" else None
    
    try:
        logger.info(f"Transcribing: {audio_path} (lang: {language or 'auto'}, task: {task})")
        model = _get_whisper_model()
        
        result = model.transcribe(
            audio_path,
            language=language,
            task=task,
            verbose=verbose,
            fp16=False
        )
        
        transcription = {
            'text': result['text'].strip(),
            'segments': result.get('segments', []),
            'language': result.get('language', language or 'unknown'),
            'duration': sum(seg.get('end', 0) for seg in result.get('segments', [])),
        }
        
        logger.info(f"Transcription complete: {transcription['language']}, {transcription['duration']:.1f}s, {len(transcription['text'])} chars")
        return transcription
        
    except Exception as e:
        error_msg = f"Transcription failed: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg)


def transcribe_audio_simple(audio_path: str) -> str:
    result = transcribe_audio(audio_path)
    return result['text']


def get_supported_formats() -> List[str]:
    """Get list of supported audio file formats."""
    return sorted(list(SUPPORTED_FORMATS))
