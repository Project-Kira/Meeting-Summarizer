"""
Configuration module for Meeting Summarizer.
Loads settings from environment variables with sensible defaults.
"""

import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent

# Model configuration
MODEL_PATH = os.getenv(
    "MODEL_PATH",
    str(BASE_DIR / "models" / "mistral-7b-instruct-v0.2.Q4_K_M.gguf")
)

# LLM inference parameters
N_CTX = int(os.getenv("N_CTX", "32768"))
N_THREADS = int(os.getenv("N_THREADS", "4"))
N_GPU_LAYERS = int(os.getenv("N_GPU_LAYERS", "1"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.3"))
TOP_P = float(os.getenv("TOP_P", "0.9"))

# Summarization parameters
CHARS_PER_TOKEN = int(os.getenv("CHARS_PER_TOKEN", "4"))
CHUNK_SIZE_TOKENS = int(os.getenv("CHUNK_SIZE_TOKENS", "4000"))
OVERLAP_PERCENTAGE = float(os.getenv("OVERLAP_PERCENTAGE", "0.1"))
MAX_CONTEXT_TOKENS = int(os.getenv("MAX_CONTEXT_TOKENS", "6000"))
MAX_TOKENS_CHUNK = int(os.getenv("MAX_TOKENS_CHUNK", "512"))
MAX_TOKENS_FINAL = int(os.getenv("MAX_TOKENS_FINAL", "1024"))

# Input validation
MAX_INPUT_LENGTH = int(os.getenv("MAX_INPUT_LENGTH", "10000000"))  # 10MB chars

# Logging configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DIR = Path(os.getenv("LOG_DIR", str(BASE_DIR / "logs")))
LOG_FILE = os.getenv("LOG_FILE", "meeting_summarizer.log")
LOG_MAX_BYTES = int(os.getenv("LOG_MAX_BYTES", str(10 * 1024 * 1024)))  # 10MB
LOG_BACKUP_COUNT = int(os.getenv("LOG_BACKUP_COUNT", "5"))
ENABLE_FILE_LOGGING = os.getenv("ENABLE_FILE_LOGGING", "true").lower() == "true"

# API configuration (for future use)
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
API_CORS_ORIGINS = os.getenv("API_CORS_ORIGINS", "http://localhost:3000,http://localhost:5173").split(",")
