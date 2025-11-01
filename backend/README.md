# Meeting Summarizer Backend

Real-time meeting transcription and summarization backend with local LLM inference.

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Client    │────▶│  FastAPI     │────▶│  PostgreSQL │
│  (WebSocket)│◀────│  Server      │◀────│  Database   │
└─────────────┘     └──────────────┘     └─────────────┘
                           │
                           ▼
                    ┌──────────────┐     ┌─────────────┐
                    │   Worker     │────▶│  Inference  │
                    │   Queue      │◀────│  Service    │
                    └──────────────┘     └─────────────┘
```

## Features

- **Real-time Ingestion**: WebSocket-based streaming of meeting segments
- **Async Summarization**: Background workers with retry logic and exponential backoff
- **Chunking**: Sliding window with 10-20% overlap for context preservation
- **Local LLM**: llama.cpp-based inference with GPU acceleration
- **Structured Output**: JSON summaries with action items, decisions, topics
- **Incremental Updates**: PostgreSQL LISTEN/NOTIFY for real-time updates

## Hardware Requirements

### Minimum (CPU-only)
- **CPU**: 8+ cores
- **RAM**: 16 GB
- **Storage**: 20 GB
- **Model**: Mistral-7B Q4_K_M (~4 GB)
- **Latency**: 10-30 seconds per chunk

### Recommended (GPU)
- **GPU**: NVIDIA GPU with 10+ GB VRAM (RTX 3080, RTX 4080, A4000, etc.)
- **CPU**: 8+ cores
- **RAM**: 32 GB
- **Storage**: 50 GB
- **Model**: Mistral-7B Q5_K_M or LLaMA-3 8B Q5_K_M (~6-8 GB)
- **Latency**: 2-5 seconds per chunk

### Optimal (High-throughput)
- **GPU**: NVIDIA GPU with 24+ GB VRAM (RTX 4090, A6000, etc.)
- **CPU**: 16+ cores
- **RAM**: 64 GB
- **Storage**: 100 GB
- **Model**: LLaMA-3 13B Q5_K_M or Mistral 7B Q8 (~12-16 GB)
- **Latency**: 1-3 seconds per chunk

## Quick Start

### 1. Prerequisites

```bash
# Install PostgreSQL
sudo apt install postgresql postgresql-contrib

# Create database
sudo -u postgres createdb meeting_summarizer
sudo -u postgres createuser meeting_user -P

# Grant privileges
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE meeting_summarizer TO meeting_user;"
```

### 2. Install Dependencies

```bash
cd backend/
pip install -r requirements.txt

# For GPU support (CUDA 12.x)
CMAKE_ARGS="-DLLAMA_CUBLAS=on" pip install llama-cpp-python --force-reinstall --no-cache-dir

# For CPU-only
pip install llama-cpp-python
```

### 3. Download Model

```bash
mkdir -p /path/to/models

# Download Mistral-7B (recommended for GPU with 10GB+ VRAM)
wget https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q5_K_M.gguf \
  -O /path/to/models/mistral-7b-instruct-v0.2.Q5_K_M.gguf

# OR download smaller model for CPU/low VRAM
wget https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf \
  -O /path/to/models/mistral-7b-instruct-v0.2.Q4_K_M.gguf
```

### 4. Configure

```bash
cp .env.example .env
nano .env  # Update with your settings
```

Key settings:
```env
DATABASE_URL=postgresql://meeting_user:your_password@localhost:5432/meeting_summarizer
INFERENCE_MODEL_PATH=/path/to/models/mistral-7b-instruct-v0.2.Q5_K_M.gguf
INFERENCE_GPU_LAYERS=35  # Set to 0 for CPU-only
```

### 5. Run Migrations

```bash
make migrate
```

### 6. Start Services

```bash
# Start all services (API + Worker + Inference)
make start-all

# OR start individually in separate terminals:
make start-inference  # Terminal 1
make start-worker     # Terminal 2
make start-api        # Terminal 3
```

## API Usage

### Create Meeting

```bash
curl -X POST http://localhost:8000/meetings \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Q4 Planning Meeting",
    "metadata": {"department": "Engineering", "attendees": 5}
  }'

# Response:
# {
#   "id": "123e4567-e89b-12d3-a456-426614174000",
#   "title": "Q4 Planning Meeting",
#   "metadata": {...},
#   "created_at": "2025-10-31T14:00:00Z",
#   "finalized": false
# }
```

### Ingest Segments

```bash
MEETING_ID="123e4567-e89b-12d3-a456-426614174000"

curl -X POST http://localhost:8000/ingest/segment \
  -H "Content-Type: application/json" \
  -d '{
    "meeting_id": "'$MEETING_ID'",
    "speaker": "Alice",
    "timestamp_iso": "2025-10-31T14:00:00Z",
    "text_segment": "Let'\''s discuss our Q4 goals and budget allocation."
  }'

# Response:
# {
#   "segment_id": "223e4567-e89b-12d3-a456-426614174001",
#   "status": "accepted"
# }
```

### WebSocket Stream

```javascript
// JavaScript client example
const ws = new WebSocket(`ws://localhost:8000/meetings/${meetingId}/stream`);

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Summary update:', data);
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};
```

### Get Summary

```bash
curl http://localhost:8000/meetings/$MEETING_ID/summary

# Response:
# {
#   "id": "323e4567-e89b-12d3-a456-426614174002",
#   "meeting_id": "123e4567-e89b-12d3-a456-426614174000",
#   "type": "incremental",
#   "content": {
#     "summary": "Discussion about Q4 goals and budget",
#     "decisions": [
#       {"text": "Allocate 40% to engineering", "confidence": 0.9}
#     ],
#     "action_items": [
#       {
#         "text": "Prepare budget breakdown",
#         "owner": "Bob",
#         "due_date_iso": "2025-11-07",
#         "confidence": 0.85
#       }
#     ],
#     "topics": [
#       {"name": "Budget Planning", "confidence": 0.95}
#     ]
#   },
#   "created_at": "2025-10-31T14:05:00Z"
# }
```

### Finalize Meeting

```bash
curl -X POST http://localhost:8000/meetings/$MEETING_ID/finalize

# Response:
# {
#   "status": "finalized",
#   "meeting_id": "123e4567-e89b-12d3-a456-426614174000"
# }
```

### Health Check

```bash
curl http://localhost:8000/healthz

# Response:
# {
#   "status": "healthy",
#   "database": "healthy",
#   "redis": "healthy",
#   "inference": "healthy",
#   "timestamp": "2025-10-31T14:10:00Z"
# }
```

## Testing

### Run All Tests

```bash
make test
```

### Run Unit Tests Only

```bash
make test-unit
```

### Run Integration Tests

```bash
# Ensure services are running first
make start-all

# In another terminal:
make test-integration
```

### Manual Integration Test

```bash
python tests/integration/test_full_flow.py
```

## Development

### Format Code

```bash
make format
```

### Lint Code

```bash
make lint
```

### Clean Cache

```bash
make clean
```

## Configuration Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql://...` | PostgreSQL connection string |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection string |
| `API_HOST` | `127.0.0.1` | FastAPI bind address |
| `API_PORT` | `8000` | FastAPI port |
| `INFERENCE_HOST` | `127.0.0.1` | Inference service host |
| `INFERENCE_PORT` | `8001` | Inference service port |
| `INFERENCE_MODEL_PATH` | `/models/...` | Path to GGUF model file |
| `INFERENCE_GPU_LAYERS` | `35` | Number of layers to offload to GPU (0 for CPU) |
| `WORKER_BATCH_TOKENS` | `2000` | Token threshold for triggering summarization |
| `WORKER_BATCH_TIMEOUT` | `45` | Seconds before forcing summarization |
| `CHUNK_SIZE` | `2000` | Tokens per chunk |
| `CHUNK_OVERLAP` | `0.15` | Overlap ratio between chunks |

## Troubleshooting

### Model Loading Issues

```bash
# Check GPU availability
nvidia-smi

# Test model loading
python -c "from llama_cpp import Llama; print('llama-cpp-python OK')"

# If GPU not detected, reinstall with CUDA support
CMAKE_ARGS="-DLLAMA_CUBLAS=on" pip install llama-cpp-python --force-reinstall
```

### Database Connection Issues

```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Test connection
psql -U meeting_user -d meeting_summarizer -h localhost -c "SELECT 1;"
```

### Performance Tuning

1. **Increase batch size** for fewer but larger inference calls
2. **Adjust GPU layers** based on your VRAM
3. **Use quantized models** (Q4, Q5) for faster inference
4. **Enable streaming** for lower perceived latency

## License

MIT License - see LICENSE file

## Contributing

Contributions welcome! Please submit issues and pull requests.
