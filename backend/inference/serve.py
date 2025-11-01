#!/usr/bin/env python3
import asyncio
import os
import json
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
import subprocess
import psutil

from config import get_settings

settings = get_settings()

try:
    from llama_cpp import Llama
    LLAMA_CPP_AVAILABLE = True
except ImportError:
    LLAMA_CPP_AVAILABLE = False
    print("Warning: llama-cpp-python not installed. Install with: pip install llama-cpp-python")


class CompletionRequest(BaseModel):
    prompt: str
    max_tokens: int = 512
    temperature: float = 0.7
    stop: List[str] = []
    model: Optional[str] = None


class CompletionResponse(BaseModel):
    choices: List[dict]
    usage: dict
    model: str


class GPUInfo(BaseModel):
    available: bool
    vram_gb: float
    name: str


app = FastAPI(title="Inference Service", version="0.1.0")

llm: Optional[Llama] = None


def detect_gpu() -> GPUInfo:
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader,nounits"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        
        if result.returncode == 0:
            lines = result.stdout.strip().split("\n")
            if lines:
                parts = lines[0].split(",")
                name = parts[0].strip()
                vram_mb = float(parts[1].strip())
                vram_gb = vram_mb / 1024
                return GPUInfo(available=True, vram_gb=vram_gb, name=name)
    except Exception as e:
        print(f"GPU detection failed: {e}")
    
    return GPUInfo(available=False, vram_gb=0.0, name="CPU")


def initialize_model():
    global llm
    
    if not LLAMA_CPP_AVAILABLE:
        print("llama-cpp-python not available, using mock inference")
        return None
    
    model_path = settings.inference_model_path
    
    if not os.path.exists(model_path):
        print(f"Model not found at {model_path}")
        print("Using mock inference mode")
        return None
    
    gpu_info = detect_gpu()
    print(f"GPU Info: {gpu_info}")
    
    n_gpu_layers = 0
    if gpu_info.available:
        if gpu_info.vram_gb >= 10:
            n_gpu_layers = settings.inference_gpu_layers
            print(f"Using GPU with {n_gpu_layers} layers")
        else:
            print(f"GPU VRAM ({gpu_info.vram_gb:.1f}GB) insufficient, using CPU")
    else:
        print("No GPU detected, using CPU inference")
    
    print(f"Loading model from {model_path}...")
    
    try:
        llm = Llama(
            model_path=model_path,
            n_ctx=settings.inference_context_size,
            n_threads=settings.inference_threads,
            n_gpu_layers=n_gpu_layers,
            verbose=False,
        )
        print("Model loaded successfully!")
        return llm
    except Exception as e:
        print(f"Failed to load model: {e}")
        print("Using mock inference mode")
        return None


def verify_api_key(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization format")
    
    token = authorization[7:]
    if token != settings.inference_api_key:
        raise HTTPException(status_code=403, detail="Invalid API key")


@app.on_event("startup")
async def startup():
    initialize_model()


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "model_loaded": llm is not None,
        "gpu_available": detect_gpu().available,
    }


@app.post("/v1/completions", response_model=CompletionResponse, dependencies=[])
async def create_completion(
    request: CompletionRequest,
    authorization: str = Header(None)
):
    verify_api_key(authorization)
    
    if len(request.prompt) > settings.max_tokens_per_request * 4:
        raise HTTPException(
            status_code=400,
            detail=f"Prompt too long. Max {settings.max_tokens_per_request} tokens",
        )
    
    if llm is None:
        mock_response = generate_mock_response(request.prompt)
        return CompletionResponse(
            choices=[{"text": mock_response, "index": 0, "finish_reason": "stop"}],
            usage={"prompt_tokens": 100, "completion_tokens": 50, "total_tokens": 150},
            model="mock-model",
        )
    
    try:
        output = llm(
            request.prompt,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            stop=request.stop if request.stop else None,
        )
        
        text = output["choices"][0]["text"]
        
        return CompletionResponse(
            choices=[{"text": text, "index": 0, "finish_reason": "stop"}],
            usage=output.get("usage", {}),
            model=settings.inference_model_path,
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference failed: {str(e)}")


def generate_mock_response(prompt: str) -> str:
    if "JSON" in prompt or "json" in prompt:
        return json.dumps({
            "summary": "Mock summary of the meeting discussion",
            "decisions": [
                {"text": "Decided to proceed with the proposed plan", "confidence": 0.9}
            ],
            "action_items": [
                {
                    "text": "Follow up with stakeholders",
                    "owner": "John Doe",
                    "due_date_iso": "2025-11-15",
                    "confidence": 0.85
                }
            ],
            "topics": [
                {"name": "Project Planning", "confidence": 0.9},
                {"name": "Budget Review", "confidence": 0.8}
            ]
        })
    return "This is a mock response from the inference service."


if __name__ == "__main__":
    import uvicorn
    from app.logging import setup_logging
    
    setup_logging()
    
    uvicorn.run(
        app,
        host=settings.inference_host,
        port=settings.inference_port,
        log_level=settings.log_level.lower(),
    )
