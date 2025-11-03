"""
FastAPI server that exposes summarization endpoints.
Provides REST API for frontend to communicate with the backend.
"""

import logging
from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional
import config
from backend.utils.summarize import summarize_conversation

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
        from backend.utils.summarize import estimate_tokens
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
        from backend.utils.summarize import estimate_tokens
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


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Meeting Summarizer API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/api/health",
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
