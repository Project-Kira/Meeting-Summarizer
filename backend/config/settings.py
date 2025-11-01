from functools import lru_cache
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://meeting_user:meeting_pass@localhost:5432/meeting_summarizer"
    database_pool_size: int = 20
    database_max_overflow: int = 10
    
    redis_url: str = "redis://localhost:6379/0"
    
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    api_workers: int = 4
    api_key: str = "dev-secret-key"
    
    inference_host: str = "127.0.0.1"
    inference_port: int = 8001
    inference_api_key: str = "inference-secret"
    inference_model_path: str = "/models/mistral-7b-instruct.gguf"
    inference_context_size: int = 16384
    inference_gpu_layers: int = 35
    inference_threads: int = 8
    
    worker_batch_tokens: int = 2000
    worker_batch_timeout: int = 45
    worker_max_retries: int = 3
    worker_backoff_base: int = 2
    
    chunk_size: int = 2000
    chunk_overlap: float = 0.15
    max_tokens_per_request: int = 15000
    
    log_level: str = "INFO"
    log_format: str = "json"
    
    cors_origins: List[str] = ["http://localhost:3000"]
    allowed_hosts: List[str] = ["127.0.0.1", "localhost"]
    
    enable_metrics: bool = True
    metrics_port: int = 9090

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()
