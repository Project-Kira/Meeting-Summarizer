"""
FastAPI server that exposes summarization endpoints.
Provides REST API for frontend to communicate with the backend.
"""

import logging
import os
import tempfile
from pathlib import Path
from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional
import config
from summarize import summarize_conversation
from transcription import transcribe_audio_simple, get_supported_formats

# Setup logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format=config.LOG_FORMAT
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Meeting Summarizer API",
    description="REST API for summarizing conversation text using local LLM",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.API_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response models
class SummarizeRequest(BaseModel):
    """Request model for text summarization."""
    text: str = Field(..., description="Conversation text to summarize", min_length=1)
    
    model_config = {
        "json_schema_extra": {
            "examples": [{
                "text": "Meeting started at 10 AM. John discussed Q3 budget..."
            }]
        }
    }


class SummarizeResponse(BaseModel):
    """Response model for summarization."""
    summary: str = Field(..., description="Generated summary")
    input_length: int = Field(..., description="Length of input text in characters")
    estimated_tokens: int = Field(..., description="Estimated number of tokens in input")
    
    model_config = {
        "json_schema_extra": {
            "examples": [{
                "summary": "* Q3 budget discussion\n* Action items assigned",
                "input_length": 1500,
                "estimated_tokens": 375
            }]
        }
    }


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    model_path: str
    version: str


class ErrorResponse(BaseModel):
    """Error response model."""
    detail: str


class ProcessAudioResponse(BaseModel):
    """Response model for audio processing (transcription + summarization)."""
    transcription: str = Field(..., description="Transcribed text from audio")
    summary: str = Field(..., description="Summary of the transcription")
    language: str = Field(..., description="Detected language")
    duration: float = Field(..., description="Audio duration in seconds")
    
    model_config = {
        "json_schema_extra": {
            "examples": [{
                "transcription": "Hello everyone, today we discussed the Q3 budget...",
                "summary": "* Q3 budget discussion\n* Action items assigned",
                "language": "en",
                "duration": 120.5
            }]
        }
    }


# Endpoints
@app.get("/api/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint.
    Returns server status and model information.
    """
    return HealthResponse(
        status="ok",
        model_path=config.MODEL_PATH,
        version="1.0.0"
    )


@app.post(
    "/api/summarize",
    response_model=SummarizeResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid input"},
        500: {"model": ErrorResponse, "description": "Summarization failed"}
    },
    tags=["Summarization"]
)
async def summarize_text(request: SummarizeRequest):
    """
    Summarize conversation text.
    
    Accepts plain text and returns a structured summary.
    Handles long conversations by automatically chunking them.
    """
    try:
        logger.info(f"Received summarization request (length: {len(request.text)} chars)")
        
        # Estimate tokens for response
        from summarize import estimate_tokens
        estimated_tokens = estimate_tokens(request.text)
        
        # Perform summarization
        summary = summarize_conversation(request.text)
        
        logger.info("Summarization completed successfully")
        
        return SummarizeResponse(
            summary=summary,
            input_length=len(request.text),
            estimated_tokens=estimated_tokens
        )
        
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        logger.error(f"Summarization error: {e}")
        raise HTTPException(status_code=500, detail=f"Summarization failed: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post(
    "/api/summarize-file",
    response_model=SummarizeResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid file"},
        500: {"model": ErrorResponse, "description": "File processing failed"}
    },
    tags=["Summarization"]
)
async def summarize_file(file: UploadFile = File(...)):
    """
    Summarize conversation from uploaded text file.
    
    Accepts .txt files and returns a structured summary.
    Maximum file size is determined by MAX_INPUT_LENGTH config.
    """
    try:
        # Validate file type
        if not file.filename or not file.filename.endswith('.txt'):
            raise HTTPException(
                status_code=400,
                detail="Only .txt files are supported"
            )
        
        logger.info(f"Received file upload: {file.filename}")
        
        # Read file content
        content = await file.read()
        
        # Decode text
        try:
            text = content.decode('utf-8')
        except UnicodeDecodeError:
            logger.error("File encoding error")
            raise HTTPException(
                status_code=400,
                detail="File must be UTF-8 encoded"
            )
        
        # Validate content
        if not text.strip():
            raise HTTPException(
                status_code=400,
                detail="File is empty"
            )
        
        # Estimate tokens for response
        from summarize import estimate_tokens
        estimated_tokens = estimate_tokens(text)
        
        # Perform summarization
        summary = summarize_conversation(text)
        
        logger.info(f"File summarization completed for: {file.filename}")
        
        return SummarizeResponse(
            summary=summary,
            input_length=len(text),
            estimated_tokens=estimated_tokens
        )
        
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        logger.error(f"Summarization error: {e}")
        raise HTTPException(status_code=500, detail=f"File processing failed: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post(
    "/api/process",
    response_model=ProcessAudioResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid audio file"},
        500: {"model": ErrorResponse, "description": "Processing failed"}
    },
    tags=["Audio Processing"]
)
async def process_audio(file: UploadFile = File(...)):
    """
    Process audio file: transcribe and summarize.
    
    This is the main endpoint for the frontend.
    It accepts an audio file, transcribes it using Whisper AI,
    then summarizes the transcription using Mistral AI.
    
    Supported formats: mp3, wav, m4a, ogg, flac, aac, wma, webm
    
    Returns both transcription and summary in a single response.
    """
    temp_file_path = None
    
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Check file extension
        file_ext = Path(file.filename).suffix.lower()
        supported_formats = get_supported_formats()
        
        if file_ext not in supported_formats:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported audio format: {file_ext}. Supported: {', '.join(supported_formats)}"
            )
        
        logger.info(f"Processing audio file: {file.filename} ({file_ext})")
        
        # Save uploaded file to temporary location
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=file_ext,
            dir=config.TEMP_AUDIO_DIR
        ) as temp_file:
            # Read and write file content
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
            
        logger.info(f"Audio saved to temporary file: {temp_file_path}")
        
        # Step 1: Transcribe audio using Whisper
        logger.info("Starting transcription...")
        transcription_result = transcribe_audio_simple(temp_file_path)
        
        if not transcription_result or not transcription_result.strip():
            raise HTTPException(
                status_code=400,
                detail="No speech detected in audio file"
            )
        
        logger.info(f"Transcription complete: {len(transcription_result)} characters")
        
        # Step 2: Summarize transcription using Mistral
        logger.info("Starting summarization...")
        summary = summarize_conversation(transcription_result)
        logger.info("Summarization complete")
        
        # Get additional info (we need full result for metadata)
        from transcription import transcribe_audio
        full_result = transcribe_audio(temp_file_path)
        
        return ProcessAudioResponse(
            transcription=transcription_result,
            summary=summary,
            language=full_result.get('language', 'unknown'),
            duration=full_result.get('duration', 0.0)
        )
        
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        logger.error(f"Processing error: {e}")
        raise HTTPException(status_code=500, detail=f"Audio processing failed: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    finally:
        # Clean up temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
                logger.info(f"Cleaned up temporary file: {temp_file_path}")
            except Exception as e:
                logger.warning(f"Failed to delete temporary file: {e}")


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Meeting Summarizer API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/api/health",
            "process_audio": "/api/process",
            "summarize_text": "/api/summarize",
            "summarize_file": "/api/summarize-file",
            "docs": "/docs"
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting server on {config.API_HOST}:{config.API_PORT}")
    
    uvicorn.run(
        app,
        host=config.API_HOST,
        port=config.API_PORT,
        log_level=config.LOG_LEVEL.lower()
    )
