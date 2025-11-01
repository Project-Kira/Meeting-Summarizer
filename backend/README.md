# Meeting Summarizer Backend# Meeting Summarizer Backend



Real-time meeting transcription and summarization system that processes live meeting transcripts and generates intelligent summaries using a local LLM.Real-time meeting transcription and summarization backend with local LLM inference.



---## Architecture



## 🎯 What Does It Do?```

┌─────────────┐     ┌──────────────┐     ┌─────────────┐

This backend automatically:│   Client    │────▶│  FastAPI     │────▶│  PostgreSQL │

- **Ingests** meeting transcripts in real-time (segment by segment)│  (WebSocket)│◀────│  Server      │◀────│  Database   │

- **Generates** intelligent summaries as the meeting progresses└─────────────┘     └──────────────┘     └─────────────┘

- **Extracts** decisions, action items, and key topics                           │

- **Provides** final comprehensive summaries when meetings end                           ▼

                    ┌──────────────┐     ┌─────────────┐

**Key Innovation**: Unlike services that require external APIs (OpenAI, etc.), this runs entirely on your own hardware with local LLM models, giving you complete privacy and control.                    │   Worker     │────▶│  Inference  │

                    │   Queue      │◀────│  Service    │

---                    └──────────────┘     └─────────────┘

```

## 🏗️ Architecture

## Features

```

Meeting Audio → Transcription → Backend API → Processing → Summary- **Real-time Ingestion**: WebSocket-based streaming of meeting segments

                                     ↓- **Async Summarization**: Background workers with retry logic and exponential backoff

                              ┌──────────────┐- **Chunking**: Sliding window with 10-20% overlap for context preservation

                              │  FastAPI     │- **Local LLM**: llama.cpp-based inference with GPU acceleration

                              │  REST API    │- **Structured Output**: JSON summaries with action items, decisions, topics

                              └──────────────┘- **Incremental Updates**: PostgreSQL LISTEN/NOTIFY for real-time updates

                                     ↓

                    ┌────────────────┼────────────────┐## Hardware Requirements

                    ↓                ↓                ↓

              ┌──────────┐    ┌──────────┐    ┌──────────┐### Minimum (CPU-only)

              │PostgreSQL│    │  Worker  │    │   LLM    │- **CPU**: 8+ cores

              │ Database │    │  Queue   │    │Inference │- **RAM**: 16 GB

              └──────────┘    └──────────┘    └──────────┘- **Storage**: 20 GB

```- **Model**: Mistral-7B Q4_K_M (~4 GB)

- **Latency**: 10-30 seconds per chunk

### Core Components

### Recommended (GPU)

1. **FastAPI Server** - REST API + WebSocket for real-time updates- **GPU**: NVIDIA GPU with 10+ GB VRAM (RTX 3080, RTX 4080, A4000, etc.)

2. **Worker Queue** - Background job processor with retry logic- **CPU**: 8+ cores

3. **LLM Inference** - Local llama-cpp-python for AI summarization- **RAM**: 32 GB

4. **PostgreSQL** - Persistent storage with pub/sub messaging- **Storage**: 50 GB

5. **Chunker** - Intelligent text splitting with sliding windows- **Model**: Mistral-7B Q5_K_M or LLaMA-3 8B Q5_K_M (~6-8 GB)

6. **Merger** - Summary deduplication and consolidation- **Latency**: 2-5 seconds per chunk



---### Optimal (High-throughput)

- **GPU**: NVIDIA GPU with 24+ GB VRAM (RTX 4090, A6000, etc.)

## 🚀 Quick Start- **CPU**: 16+ cores

- **RAM**: 64 GB

### 1. Setup- **Storage**: 100 GB

- **Model**: LLaMA-3 13B Q5_K_M or Mistral 7B Q8 (~12-16 GB)

```bash- **Latency**: 1-3 seconds per chunk

# Clone and navigate

cd backend## Quick Start



# Run setup script (creates venv, installs dependencies)### 1. Prerequisites

bash setup.sh

```bash

# Or manual setup# Install PostgreSQL

python3 -m venv venvsudo apt install postgresql postgresql-contrib

source venv/bin/activate

pip install -r requirements.txt# Create database

```sudo -u postgres createdb meeting_summarizer

sudo -u postgres createuser meeting_user -P

### 2. Configure

# Grant privileges

```bashsudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE meeting_summarizer TO meeting_user;"

# Copy example config```

cp .env.example .env

### 2. Install Dependencies

# Edit configuration

nano .env```bash

```cd backend/

pip install -r requirements.txt

**Key settings:**

```env# For GPU support (CUDA 12.x)

# API ServerCMAKE_ARGS="-DLLAMA_CUBLAS=on" pip install llama-cpp-python --force-reinstall --no-cache-dir

API_HOST=0.0.0.0

API_PORT=8000# For CPU-only

pip install llama-cpp-python

# Database (for production)```

DATABASE_URL=postgresql://user:pass@localhost:5432/meetings

### 3. Download Model

# LLM Settings

MODEL_PATH=/path/to/model.gguf```bash

INFERENCE_GPU_LAYERS=35  # Set to 0 for CPU-onlymkdir -p /path/to/models

```

# Download Mistral-7B (recommended for GPU with 10GB+ VRAM)

### 3. Run - Development Mode (Quick Testing)wget https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q5_K_M.gguf \

  -O /path/to/models/mistral-7b-instruct-v0.2.Q5_K_M.gguf

```bash

# Start test server (no PostgreSQL needed, uses mock LLM)# OR download smaller model for CPU/low VRAM

python run_test_server.pywget https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf \

  -O /path/to/models/mistral-7b-instruct-v0.2.Q4_K_M.gguf

# In another terminal, test it```

./test_cli.sh

```### 4. Configure



The test server runs on **http://localhost:8000** with:```bash

- ✅ In-memory storagecp .env.example .env

- ✅ Mock summariesnano .env  # Update with your settings

- ✅ All API endpoints working```

- ✅ Perfect for testing/development

Key settings:

### 4. Run - Production Mode```env

DATABASE_URL=postgresql://meeting_user:your_password@localhost:5432/meeting_summarizer

#### Option A: Quick Start (All-in-one)INFERENCE_MODEL_PATH=/path/to/models/mistral-7b-instruct-v0.2.Q5_K_M.gguf

INFERENCE_GPU_LAYERS=35  # Set to 0 for CPU-only

```bash```

# Start all services

bash setup.sh        # First time only### 5. Run Migrations

uvicorn app.main:app --host 0.0.0.0 --port 8000

``````bash

make migrate

#### Option B: Full Setup (Separate Services)```



```bash### 6. Start Services

# 1. Start PostgreSQL (if not running)

sudo systemctl start postgresql```bash

# Start all services (API + Worker + Inference)

# 2. Initialize databasemake start-all

source venv/bin/activate

python db/migrate.py# OR start individually in separate terminals:

make start-inference  # Terminal 1

# 3. Start inference servicemake start-worker     # Terminal 2

python inference/serve.py &make start-api        # Terminal 3

```

# 4. Start worker

python workers/worker.py &## API Usage



# 5. Start API server### Create Meeting

uvicorn app.main:app --host 0.0.0.0 --port 8000

``````bash

curl -X POST http://localhost:8000/meetings \

---  -H "Content-Type: application/json" \

  -d '{

## 📚 API Usage    "title": "Q4 Planning Meeting",

    "metadata": {"department": "Engineering", "attendees": 5}

### Create Meeting  }'



```bash# Response:

curl -X POST http://localhost:8000/meetings \# {

  -H "Content-Type: application/json" \#   "id": "123e4567-e89b-12d3-a456-426614174000",

  -d '{#   "title": "Q4 Planning Meeting",

    "title": "Q4 Planning Meeting",#   "metadata": {...},

    "metadata": {"department": "Engineering"}#   "created_at": "2025-10-31T14:00:00Z",

  }'#   "finalized": false

# }

# Returns: {"id": "meeting-uuid", "title": "Q4 Planning Meeting", ...}```

```

### Ingest Segments

### Add Transcript Segment

```bash

```bashMEETING_ID="123e4567-e89b-12d3-a456-426614174000"

curl -X POST http://localhost:8000/ingest/segment \

  -H "Content-Type: application/json" \curl -X POST http://localhost:8000/ingest/segment \

  -d '{  -H "Content-Type: application/json" \

    "meeting_id": "meeting-uuid",  -d '{

    "speaker": "Alice",    "meeting_id": "'$MEETING_ID'",

    "timestamp_iso": "2025-11-01T14:00:00Z",    "speaker": "Alice",

    "text_segment": "Let us discuss Q4 goals and revenue targets."    "timestamp_iso": "2025-10-31T14:00:00Z",

  }'    "text_segment": "Let'\''s discuss our Q4 goals and budget allocation."

```  }'



### Get Current Summary# Response:

# {

```bash#   "segment_id": "223e4567-e89b-12d3-a456-426614174001",

curl http://localhost:8000/meetings/meeting-uuid/summary#   "status": "accepted"

```# }

```

**Response:**

```json### WebSocket Stream

{

  "id": "summary-uuid",```javascript

  "type": "incremental",// JavaScript client example

  "content": {const ws = new WebSocket(`ws://localhost:8000/meetings/${meetingId}/stream`);

    "summary": "Team discussed Q4 goals...",

    "decisions": [ws.onmessage = (event) => {

      {"text": "Hire 3 engineers", "confidence": 0.95}  const data = JSON.parse(event.data);

    ],  console.log('Summary update:', data);

    "action_items": [};

      {

        "text": "Prepare job descriptions",ws.onerror = (error) => {

        "owner": "Alice",  console.error('WebSocket error:', error);

        "due_date_iso": "2025-11-07",};

        "confidence": 0.9```

      }

    ],### Get Summary

    "topics": [

      {"name": "Hiring", "confidence": 0.95}```bash

    ]curl http://localhost:8000/meetings/$MEETING_ID/summary

  }

}# Response:

```# {

#   "id": "323e4567-e89b-12d3-a456-426614174002",

### Finalize Meeting#   "meeting_id": "123e4567-e89b-12d3-a456-426614174000",

#   "type": "incremental",

```bash#   "content": {

# Mark meeting as complete#     "summary": "Discussion about Q4 goals and budget",

curl -X POST http://localhost:8000/meetings/meeting-uuid/finalize#     "decisions": [

#       {"text": "Allocate 40% to engineering", "confidence": 0.9}

# Wait 3 seconds for final summary generation#     ],

sleep 3#     "action_items": [

#       {

# Get final summary#         "text": "Prepare budget breakdown",

curl http://localhost:8000/meetings/meeting-uuid/summary#         "owner": "Bob",

```#         "due_date_iso": "2025-11-07",

#         "confidence": 0.85

### WebSocket (Real-time Updates)#       }

#     ],

```javascript#     "topics": [

const ws = new WebSocket('ws://localhost:8000/ws/meeting-uuid');#       {"name": "Budget Planning", "confidence": 0.95}

#     ]

ws.onmessage = (event) => {#   },

  const data = JSON.parse(event.data);#   "created_at": "2025-10-31T14:05:00Z"

  console.log('Update:', data.type); // 'segment_added', 'summary_update', etc.# }

};```

```

### Finalize Meeting

---

```bash

## 🧪 Testingcurl -X POST http://localhost:8000/meetings/$MEETING_ID/finalize



### Automated CLI Test# Response:

# {

```bash#   "status": "finalized",

# Run complete test flow#   "meeting_id": "123e4567-e89b-12d3-a456-426614174000"

./test_cli.sh# }

```

# This will:

# 1. Check health### Health Check

# 2. Create meeting

# 3. Add 5 segments```bash

# 4. Get summarycurl http://localhost:8000/healthz

# 5. Finalize

# 6. Get final summary# Response:

```# {

#   "status": "healthy",

### Frontend UI Testing#   "database": "healthy",

#   "redis": "healthy",

```bash#   "inference": "healthy",

# Start frontend server#   "timestamp": "2025-10-31T14:10:00Z"

./restart_servers.sh# }

```

# Opens on http://localhost:8080/

# - Create meetings via UI## Testing

# - Add segments with quick buttons

# - View live summaries### Run All Tests

# - Test WebSocket updates

``````bash

make test

### Manual Testing```



```bash### Run Unit Tests Only

# Health check

curl http://localhost:8000/healthz```bash

make test-unit

# View API docs```

xdg-open http://localhost:8000/docs

```### Run Integration Tests



---```bash

# Ensure services are running first

## 📦 Project Structuremake start-all



```# In another terminal:

backend/make test-integration

├── app/                    # FastAPI application```

│   ├── main.py            # Main API server

│   ├── notifications.py   # WebSocket & pub/sub### Manual Integration Test

│   └── setup_logging.py   # Logging configuration

│```bash

├── workers/               # Background processingpython tests/integration/test_full_flow.py

│   ├── worker.py         # Job processor```

│   ├── chunker.py        # Text chunking

│   └── merger.py         # Summary merging## Development

│

├── inference/            # LLM service### Format Code

│   └── serve.py         # llama-cpp inference

│```bash

├── db/                   # Database layermake format

│   ├── connection.py    # DB connection pool```

│   ├── repositories.py  # CRUD operations

│   └── migrations/      # SQL migrations### Lint Code

│

├── models/              # Data models```bash

│   └── schemas.py       # Pydantic modelsmake lint

│```

├── config/              # Configuration

│   └── settings.py      # Environment settings### Clean Cache

│

├── tests/               # Test suite```bash

│   ├── unit/           # Unit testsmake clean

│   └── integration/    # Integration tests```

│

├── frontend/           # Web UI for testing## Configuration Reference

│   └── index.html     # Browser interface

│| Variable | Default | Description |

├── examples/           # Usage examples|----------|---------|-------------|

│   ├── curl_examples.sh| `DATABASE_URL` | `postgresql://...` | PostgreSQL connection string |

│   └── websocket_client.py| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection string |

│| `API_HOST` | `127.0.0.1` | FastAPI bind address |

├── run_test_server.py  # Development server (no DB needed)| `API_PORT` | `8000` | FastAPI port |

├── test_cli.sh         # Automated CLI tests| `INFERENCE_HOST` | `127.0.0.1` | Inference service host |

├── restart_servers.sh  # Server management| `INFERENCE_PORT` | `8001` | Inference service port |

├── setup.sh           # Initial setup| `INFERENCE_MODEL_PATH` | `/models/...` | Path to GGUF model file |

├── verify.sh          # Health checks| `INFERENCE_GPU_LAYERS` | `35` | Number of layers to offload to GPU (0 for CPU) |

└── requirements.txt   # Python dependencies| `WORKER_BATCH_TOKENS` | `2000` | Token threshold for triggering summarization |

```| `WORKER_BATCH_TIMEOUT` | `45` | Seconds before forcing summarization |

| `CHUNK_SIZE` | `2000` | Tokens per chunk |

---| `CHUNK_OVERLAP` | `0.15` | Overlap ratio between chunks |



## 🔧 Configuration## Troubleshooting



### Environment Variables### Model Loading Issues



```bash```bash

# API Server# Check GPU availability

API_HOST=0.0.0.0              # Listen addressnvidia-smi

API_PORT=8000                 # API port

API_WORKERS=4                 # Uvicorn workers# Test model loading

python -c "from llama_cpp import Llama; print('llama-cpp-python OK')"

# Database

DATABASE_URL=postgresql://user:pass@localhost:5432/meetings# If GPU not detected, reinstall with CUDA support

DB_POOL_SIZE=20              # Connection pool sizeCMAKE_ARGS="-DLLAMA_CUBLAS=on" pip install llama-cpp-python --force-reinstall

```

# Redis (optional, for job queue)

REDIS_URL=redis://localhost:6379/0### Database Connection Issues



# LLM Inference```bash

MODEL_PATH=/path/to/model.gguf# Check PostgreSQL status

INFERENCE_PORT=8001sudo systemctl status postgresql

INFERENCE_GPU_LAYERS=35      # GPU layers (0 = CPU only)

INFERENCE_CONTEXT_SIZE=4096# Test connection

INFERENCE_BATCH_SIZE=512psql -U meeting_user -d meeting_summarizer -h localhost -c "SELECT 1;"

```

# Worker

WORKER_BATCH_SIZE=2000       # Tokens per batch### Performance Tuning

WORKER_BATCH_TIMEOUT=45      # Seconds

WORKER_MAX_RETRIES=31. **Increase batch size** for fewer but larger inference calls

WORKER_RETRY_DELAY=52. **Adjust GPU layers** based on your VRAM

```3. **Use quantized models** (Q4, Q5) for faster inference

4. **Enable streaming** for lower perceived latency

---

## License

## 🖥️ Hardware Requirements

MIT License - see LICENSE file

### Minimum (CPU-only)

- **CPU**: 8+ cores## Contributing

- **RAM**: 16 GB

- **Storage**: 20 GBContributions welcome! Please submit issues and pull requests.

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

## 🚀 Quick Commands Reference

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
