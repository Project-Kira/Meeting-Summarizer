from contextlib import asynccontextmanager
from typing import Dict, Any
from pathlib import Path
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import config
from summarize import summarize_conversation, estimate_tokens
from logger import setup_logging
from transcription import get_supported_formats
from jobs import get_job_manager
from processor import get_processor

logger = setup_logging(__name__)
job_manager = get_job_manager()
processor = get_processor()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown."""
    # Startup
    if config.AUTO_PROCESS_ON_STARTUP:
        logger.info("Starting audio processor")
        processor.start()
    else:
        logger.info("Auto-processing disabled")
    
    yield
    
    # Shutdown
    logger.info("Stopping audio processor")
    processor.stop()


app = FastAPI(
    title="Meeting Summarizer API",
    description="REST API for summarizing conversation text using local LLM",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.API_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SummarizeRequest(BaseModel):
    text: str = Field(..., description="Conversation text to summarize", min_length=1)
    model_config = {
        "json_schema_extra": {
            "examples": [{"text": "Meeting started at 10 AM. John discussed Q3 budget..."}]
        }
    }


class SummarizeResponse(BaseModel):
    summary: str = Field(..., description="Generated summary")
    input_length: int = Field(..., description="Length of input text in characters")
    estimated_tokens: int = Field(..., description="Estimated number of tokens in input")


class HealthResponse(BaseModel):
    status: str
    model_path: str
    version: str


class ErrorResponse(BaseModel):
    detail: str


@app.get("/api/health", response_model=HealthResponse, tags=["Health"])
async def health_check() -> HealthResponse:
    """Health check endpoint - returns server status and model information."""
    return HealthResponse(
        status="ok",
        model_path=config.MODEL_PATH,
        version="1.0.0"
    )


@app.post("/api/summarize", response_model=SummarizeResponse, tags=["Summarization"])
async def summarize_text(request: SummarizeRequest) -> SummarizeResponse:
    """Summarize conversation text - accepts plain text and returns structured summary."""
    try:
        logger.info(f"Summarization request: {len(request.text)} chars")
        estimated_tokens = estimate_tokens(request.text)
        summary = summarize_conversation(request.text)
        logger.info("Summarization completed")
        
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
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/summarize-file", response_model=SummarizeResponse, tags=["Summarization"])
async def summarize_file(file: UploadFile = File(...)) -> SummarizeResponse:
    """Summarize text file - accepts .txt files and returns structured summary."""
    try:
        if not file.filename or not file.filename.endswith('.txt'):
            raise HTTPException(status_code=400, detail="Only .txt files are supported")
        
        logger.info(f"File upload: {file.filename}")
        content = await file.read()
        
        try:
            text = content.decode('utf-8')
        except UnicodeDecodeError:
            raise HTTPException(status_code=400, detail="File must be UTF-8 encoded")
        
        if not text.strip():
            raise HTTPException(status_code=400, detail="File is empty")
        
        estimated_tokens = estimate_tokens(text)
        summary = summarize_conversation(text)
        logger.info(f"File summarization completed: {file.filename}")
        
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
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/", tags=["Root"])
async def root() -> Dict[str, Any]:
    """Root endpoint - returns API information and available endpoints."""
    return {
        "message": "Meeting Summarizer API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/api/health",
            "summarize_text": "/api/summarize",
            "summarize_file": "/api/summarize-file",
            "process_audio": "/api/process-audio",
            "job_status": "/api/jobs/{job_id}",
            "docs": "/docs"
        }
    }


@app.post("/api/process-audio", tags=["Audio"])
async def process_audio_endpoint(file: UploadFile = File(...)) -> JSONResponse:
    """
    Upload audio file for complete processing (transcription + summarization).
    Returns job ID for status tracking. Frontend polls /api/jobs/{job_id} for summary.
    """
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="Filename is required")
        
        file_ext = Path(file.filename).suffix.lower()
        supported = get_supported_formats()
        
        if file_ext not in supported:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported format: {file_ext}. Supported: {', '.join(supported)}"
            )
        
        input_path = config.INPUT_DIR / file.filename
        content = await file.read()
        input_path.write_bytes(content)
        
        logger.info(f"Audio uploaded: {file.filename}")
        processor.add_file(str(input_path))
        
        job = job_manager.create_job(
            filename=file.filename,
            metadata={'uploaded': True}
        )
        
        return JSONResponse({
            "job_id": job.id,
            "filename": file.filename,
            "status": job.status.value,
            "message": "File queued for processing"
        })
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/jobs/{job_id}", tags=["Jobs"])
async def get_job_status(job_id: str) -> JSONResponse:
    """
    Get processing job status by ID.
    Returns job details with summary when status is 'completed'.
    Transcription field excluded to reduce payload size.
    """
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return JSONResponse(job.to_dict(include_transcription=False))


@app.get("/api/jobs", tags=["Jobs"])
async def list_jobs(limit: int = 100) -> JSONResponse:
    """List recent processing jobs with optional limit."""
    jobs = job_manager.list_jobs(limit=limit)
    return JSONResponse({
        "jobs": [job.to_dict(include_transcription=False) for job in jobs],
        "total": len(jobs)
    })


@app.get("/api/stats", tags=["Stats"])
async def get_stats() -> JSONResponse:
    """Get processing statistics including job counts and queue size."""
    stats = job_manager.get_stats()
    stats['queue_size'] = processor.get_queue_size()
    return JSONResponse(stats)


if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting server on {config.API_HOST}:{config.API_PORT}")
    
    uvicorn.run(
        app,
        host=config.API_HOST,
        port=config.API_PORT,
        log_level=config.LOG_LEVEL.lower()
    )
