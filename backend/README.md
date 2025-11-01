# Meeting Summarizer Backend

Real-time meeting transcription and summarization system that processes live meeting transcripts and generates intelligent summaries using a local LLM.

---

## 🎯 What Does It Do?

This backend automatically:
- **Ingests** meeting transcripts in real-time (segment by segment)
- **Generates** intelligent summaries as the meeting progresses
- **Extracts** decisions, action items, and key topics
- **Provides** final comprehensive summaries when meetings end

**Key Innovation**: Unlike services that require external APIs (OpenAI, etc.), this runs entirely on your own hardware with local LLM models, giving you complete privacy and control.

---

## 🏗️ Architecture

```
Meeting Audio → Transcription → Backend API → Processing → Summary
                                     ↓
                              ┌──────────────┐
                              │  FastAPI     │
                              │  REST API    │
                              └──────────────┘
                                     ↓
                    ┌────────────────┼────────────────┐
                    ↓                ↓                ↓
              ┌──────────┐    ┌──────────┐    ┌──────────┐
              │PostgreSQL│    │  Worker  │    │   LLM    │
              │ Database │    │  Queue   │    │Inference │
              └──────────┘    └──────────┘    └──────────┘
```

### Core Components

1. **FastAPI Server** - REST API + WebSocket for real-time updates
2. **Worker Queue** - Background job processor with retry logic
3. **LLM Inference** - Local llama-cpp-python for AI summarization
4. **PostgreSQL** - Persistent storage with pub/sub messaging
5. **Chunker** - Intelligent text splitting with sliding windows
6. **Merger** - Summary deduplication and consolidation

---

## 🚀 Quick Start

### 1. Setup

```bash
# Clone and navigate
cd backend

# Run setup script (creates venv, installs dependencies)
bash setup.sh

# Or manual setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure

```bash
# Copy example config
cp .env.example .env

# Edit configuration
nano .env
```

**Key settings:**
```env
# API Server
API_HOST=0.0.0.0
API_PORT=8000

# Database (for production)
DATABASE_URL=postgresql://user:pass@localhost:5432/meetings

# LLM Settings
MODEL_PATH=/path/to/model.gguf
INFERENCE_GPU_LAYERS=35  # Set to 0 for CPU-only
```

### 3. Run - Development Mode (Quick Testing)

```bash
# Start test server (no PostgreSQL needed, uses mock LLM)
python run_test_server.py

# In another terminal, test it
./test_cli.sh
```

The test server runs on **http://localhost:8000** with:
- ✅ In-memory storage
- ✅ Mock summaries
- ✅ All API endpoints working
- ✅ Perfect for testing/development

### 4. Run - Production Mode

#### Option A: Quick Start (All-in-one)

```bash
# Start all services
bash setup.sh        # First time only
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

#### Option B: Full Setup (Separate Services)

```bash
# 1. Start PostgreSQL (if not running)
sudo systemctl start postgresql

# 2. Initialize database
source venv/bin/activate
python db/migrate.py

# 3. Start inference service
python inference/serve.py &

# 4. Start worker
python workers/worker.py &

# 5. Start API server
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

## 📚 API Usage

### Create Meeting

```bash
curl -X POST http://localhost:8000/meetings \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Q4 Planning Meeting",
    "metadata": {"department": "Engineering"}
  }'

# Returns: {"id": "meeting-uuid", "title": "Q4 Planning Meeting", ...}
```

### Add Transcript Segment

```bash
curl -X POST http://localhost:8000/ingest/segment \
  -H "Content-Type: application/json" \
  -d '{
    "meeting_id": "meeting-uuid",
    "speaker": "Alice",
    "timestamp_iso": "2025-11-01T14:00:00Z",
    "text_segment": "Let us discuss Q4 goals and revenue targets."
  }'
```

### Get Current Summary

```bash
curl http://localhost:8000/meetings/meeting-uuid/summary
```

**Response:**
```json
{
  "id": "summary-uuid",
  "type": "incremental",
  "content": {
    "summary": "Team discussed Q4 goals...",
    "decisions": [
      {"text": "Hire 3 engineers", "confidence": 0.95}
    ],
    "action_items": [
      {
        "text": "Prepare job descriptions",
        "owner": "Alice",
        "due_date_iso": "2025-11-07",
        "confidence": 0.9
      }
    ],
    "topics": [
      {"name": "Hiring", "confidence": 0.95}
    ]
  }
}
```

### Finalize Meeting

```bash
# Mark meeting as complete
curl -X POST http://localhost:8000/meetings/meeting-uuid/finalize

# Wait 3 seconds for final summary generation
sleep 3

# Get final summary
curl http://localhost:8000/meetings/meeting-uuid/summary
```

### WebSocket (Real-time Updates)

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/meeting-uuid');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Update:', data.type); // 'segment_added', 'summary_update', etc.
};
```

---

## 🧪 Testing

### Automated CLI Test

```bash
# Run complete test flow
./test_cli.sh

# This will:
# 1. Check health
# 2. Create meeting
# 3. Add 5 segments
# 4. Get summary
# 5. Finalize
# 6. Get final summary
```

### Frontend UI Testing

```bash
# Start frontend server
./restart_servers.sh

# Opens on http://localhost:8080/
# - Create meetings via UI
# - Add segments with quick buttons
# - View live summaries
# - Test WebSocket updates
```

### Manual Testing

```bash
# Health check
curl http://localhost:8000/healthz

# View API docs
xdg-open http://localhost:8000/docs
```

---

## 📦 Project Structure

```
backend/
├── app/                    # FastAPI application
│   ├── main.py            # Main API server
│   ├── notifications.py   # WebSocket & pub/sub
│   └── setup_logging.py   # Logging configuration
│
├── workers/               # Background processing
│   ├── worker.py         # Job processor
│   ├── chunker.py        # Text chunking
│   └── merger.py         # Summary merging
│
├── inference/            # LLM service
│   └── serve.py         # llama-cpp inference
│
├── db/                   # Database layer
│   ├── connection.py    # DB connection pool
│   ├── repositories.py  # CRUD operations
│   └── migrations/      # SQL migrations
│
├── models/              # Data models
│   └── schemas.py       # Pydantic models
│
├── config/              # Configuration
│   └── settings.py      # Environment settings
│
├── tests/               # Test suite
│   ├── unit/           # Unit tests
│   └── integration/    # Integration tests
│
├── frontend/           # Web UI for testing
│   └── index.html     # Browser interface
│
├── examples/           # Usage examples
│   ├── curl_examples.sh
│   └── websocket_client.py
│
├── run_test_server.py  # Development server (no DB needed)
├── test_cli.sh         # Automated CLI tests
├── restart_servers.sh  # Server management
├── setup.sh           # Initial setup
├── verify.sh          # Health checks
└── requirements.txt   # Python dependencies
```

---

## 🔧 Configuration

### Environment Variables

```bash
# API Server
API_HOST=0.0.0.0              # Listen address
API_PORT=8000                 # API port
API_WORKERS=4                 # Uvicorn workers

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/meetings
DB_POOL_SIZE=20              # Connection pool size

# Redis (optional, for job queue)
REDIS_URL=redis://localhost:6379/0

# LLM Inference
MODEL_PATH=/path/to/model.gguf
INFERENCE_PORT=8001
INFERENCE_GPU_LAYERS=35      # GPU layers (0 = CPU only)
INFERENCE_CONTEXT_SIZE=4096
INFERENCE_BATCH_SIZE=512

# Worker
WORKER_BATCH_SIZE=2000       # Tokens per batch
WORKER_BATCH_TIMEOUT=45      # Seconds
WORKER_MAX_RETRIES=3
WORKER_RETRY_DELAY=5
```

---

## 🖥️ Hardware Requirements

### Minimum (CPU-only)
- **CPU**: 8+ cores
- **RAM**: 16 GB
- **Storage**: 20 GB
- **Model**: Mistral-7B Q4_K_M (~4 GB)
- **Latency**: 10-30 seconds per chunk

### Recommended (GPU)
- **GPU**: NVIDIA GPU with 10+ GB VRAM (RTX 3080+)
- **CPU**: 8+ cores
- **RAM**: 32 GB
- **Storage**: 50 GB
- **Model**: Mistral-7B Q5_K_M (~6 GB)
- **Latency**: 2-5 seconds per chunk

### Optimal (Production)
- **GPU**: NVIDIA GPU with 24+ GB VRAM (RTX 4090, A6000)
- **CPU**: 16+ cores
- **RAM**: 64 GB
- **Storage**: 100 GB
- **Model**: LLaMA-3 8B or Mistral-7B
- **Latency**: 1-3 seconds per chunk

---

## 🗄️ Database Setup

### PostgreSQL Installation

```bash
# Ubuntu/Debian
sudo apt install postgresql postgresql-contrib

# macOS
brew install postgresql

# Start service
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### Database Creation

```bash
# Create user and database
sudo -u postgres psql

CREATE USER meeting_user WITH PASSWORD 'your_password';
CREATE DATABASE meetings OWNER meeting_user;
\q

# Update .env with connection string
DATABASE_URL=postgresql://meeting_user:your_password@localhost:5432/meetings
```

### Run Migrations

```bash
source venv/bin/activate
python db/migrate.py
```

---

## 🤖 LLM Model Setup

### Download Model

```bash
# Create models directory
mkdir -p models

# Download model (example: Mistral-7B)
cd models
wget https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q5_K_M.gguf

# Update .env
MODEL_PATH=/absolute/path/to/backend/models/mistral-7b-instruct-v0.2.Q5_K_M.gguf
```

### Recommended Models

| Model | Size | VRAM | Quality | Speed |
|-------|------|------|---------|-------|
| Mistral-7B Q4_K_M | 4.4 GB | 6 GB | Good | Fast |
| Mistral-7B Q5_K_M | 5.7 GB | 8 GB | Better | Medium |
| LLaMA-3 8B Q4_K_M | 4.9 GB | 8 GB | Good | Fast |
| LLaMA-3 8B Q5_K_M | 6.3 GB | 10 GB | Excellent | Medium |

---

## 🐛 Troubleshooting

### Server Not Starting

```bash
# Check if port is in use
sudo netstat -tuln | grep 8000

# Kill existing process
pkill -f run_test_server
pkill -f uvicorn

# Check logs
tail -f server.log
```

### Database Connection Error

```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Test connection
psql -U meeting_user -d meetings -h localhost

# Check DATABASE_URL in .env
```

### LLM Inference Slow

```bash
# Check GPU is being used
nvidia-smi

# Increase GPU layers in .env
INFERENCE_GPU_LAYERS=35  # Increase this number

# Use smaller/quantized model
# Q4_K_M is faster than Q5_K_M
```

### Out of Memory

```bash
# Reduce context size
INFERENCE_CONTEXT_SIZE=2048  # Down from 4096

# Reduce batch size
WORKER_BATCH_SIZE=1000  # Down from 2000

# Use smaller model (Q4 instead of Q5)
```

---

## 📊 Performance Tips

### For Development
- Use `run_test_server.py` (no DB, mock LLM)
- Quick iteration and testing
- No GPU needed

### For Production
- Use PostgreSQL for persistence
- Enable GPU acceleration
- Run worker pool (multiple worker instances)
- Use Redis for better job queue performance
- Monitor with Prometheus/Grafana

### Scaling
```bash
# Run multiple workers
python workers/worker.py &
python workers/worker.py &
python workers/worker.py &

# Run API with multiple workers
uvicorn app.main:app --workers 4 --host 0.0.0.0 --port 8000
```

---

## 🔐 Security Notes

- **Local Processing**: All data stays on your infrastructure
- **No External APIs**: LLM runs locally
- **Authentication**: Add JWT/OAuth as needed (extensible)
- **HTTPS**: Use reverse proxy (nginx/traefik) in production
- **Database**: Use strong passwords, limit network access

---

## 📝 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/healthz` | Health check |
| GET | `/docs` | Interactive API documentation |
| POST | `/meetings` | Create new meeting |
| POST | `/ingest/segment` | Add transcript segment |
| GET | `/meetings/{id}/summary` | Get current/final summary |
| POST | `/meetings/{id}/finalize` | Mark meeting complete |
| WS | `/ws/{id}` | WebSocket for real-time updates |

---

## 🎓 Use Cases

- **Corporate**: Board meetings, standups, planning sessions
- **Education**: Lectures, student discussions
- **Healthcare**: Consultations, medical rounds
- **Legal**: Depositions, client meetings
- **Remote Work**: Zoom/Teams meeting notes

---

## 📦 Dependencies

- **Python**: 3.10+
- **FastAPI**: Web framework
- **PostgreSQL**: Database (production)
- **llama-cpp-python**: LLM inference
- **Uvicorn**: ASGI server
- **AsyncPG**: Async PostgreSQL driver
- **Pydantic**: Data validation
- **Redis**: Optional job queue

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Run tests: `pytest tests/`
5. Submit pull request

---

## 📄 License

See LICENSE file in repository root.

---

## �� Quick Commands Reference

```bash
# Setup
bash setup.sh

# Start development server
python run_test_server.py

# Start production services
python inference/serve.py &
python workers/worker.py &
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Test
./test_cli.sh
curl http://localhost:8000/healthz

# Stop services
pkill -f run_test_server
pkill -f uvicorn
pkill -f worker.py
pkill -f serve.py
```

---

**Happy Meeting Summarizing! 🎉**
