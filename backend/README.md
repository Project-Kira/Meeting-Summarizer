# Meeting Summarizer Backend# Meeting Summarizer Backend# Meeting Summarizer Backend



Real-time meeting transcription and summarization system that processes live meeting transcripts and generates intelligent summaries using a local LLM.



---Real-time meeting transcription and summarization system that processes live meeting transcripts and generates intelligent summaries using a local LLM.Real-time meeting transcription and summarization backend with local LLM inference.



## 🎯 What Does It Do?



This backend automatically:---## Architecture

- **Ingests** meeting transcripts in real-time (segment by segment)

- **Generates** intelligent summaries as the meeting progresses

- **Extracts** decisions, action items, and key topics

- **Provides** final comprehensive summaries when meetings end## 🎯 What Does It Do?```



**Key Innovation**: Unlike services that require external APIs (OpenAI, etc.), this runs entirely on your own hardware with local LLM models, giving you complete privacy and control.┌─────────────┐     ┌──────────────┐     ┌─────────────┐



---This backend automatically:│   Client    │────▶│  FastAPI     │────▶│  PostgreSQL │



## 🏗️ Architecture- **Ingests** meeting transcripts in real-time (segment by segment)│  (WebSocket)│◀────│  Server      │◀────│  Database   │



```- **Generates** intelligent summaries as the meeting progresses└─────────────┘     └──────────────┘     └─────────────┘

Meeting Audio → Transcription → Backend API → Processing → Summary

                                     ↓- **Extracts** decisions, action items, and key topics                           │

                              ┌──────────────┐

                              │  FastAPI     │- **Provides** final comprehensive summaries when meetings end                           ▼

                              │  REST API    │

                              └──────────────┘                    ┌──────────────┐     ┌─────────────┐

                                     ↓

                    ┌────────────────┼────────────────┐**Key Innovation**: Unlike services that require external APIs (OpenAI, etc.), this runs entirely on your own hardware with local LLM models, giving you complete privacy and control.                    │   Worker     │────▶│  Inference  │

                    ↓                ↓                ↓

              ┌──────────┐    ┌──────────┐    ┌──────────┐                    │   Queue      │◀────│  Service    │

              │PostgreSQL│    │  Worker  │    │   LLM    │

              │ Database │    │  Queue   │    │Inference │---                    └──────────────┘     └─────────────┘

              └──────────┘    └──────────┘    └──────────┘

``````



### Core Components## 🏗️ Architecture



1. **FastAPI Server** - REST API + WebSocket for real-time updates## Features

2. **Worker Queue** - Background job processor with retry logic

3. **LLM Inference** - Local llama-cpp-python for AI summarization```

4. **PostgreSQL** - Persistent storage with pub/sub messaging

5. **Chunker** - Intelligent text splitting with sliding windowsMeeting Audio → Transcription → Backend API → Processing → Summary- **Real-time Ingestion**: WebSocket-based streaming of meeting segments

6. **Merger** - Summary deduplication and consolidation

                                     ↓- **Async Summarization**: Background workers with retry logic and exponential backoff

---

                              ┌──────────────┐- **Chunking**: Sliding window with 10-20% overlap for context preservation

## 🚀 Quick Start

                              │  FastAPI     │- **Local LLM**: llama.cpp-based inference with GPU acceleration

### 1. Setup

                              │  REST API    │- **Structured Output**: JSON summaries with action items, decisions, topics

```bash

# Clone and navigate                              └──────────────┘- **Incremental Updates**: PostgreSQL LISTEN/NOTIFY for real-time updates

cd backend

                                     ↓

# Run setup script (creates venv, installs dependencies)

bash setup.sh                    ┌────────────────┼────────────────┐## Hardware Requirements



# Or manual setup                    ↓                ↓                ↓

python3 -m venv venv

source venv/bin/activate              ┌──────────┐    ┌──────────┐    ┌──────────┐### Minimum (CPU-only)

pip install -r requirements.txt

```              │PostgreSQL│    │  Worker  │    │   LLM    │- **CPU**: 8+ cores



### 2. Configure              │ Database │    │  Queue   │    │Inference │- **RAM**: 16 GB



```bash              └──────────┘    └──────────┘    └──────────┘- **Storage**: 20 GB

# Copy example config

cp .env.example .env```- **Model**: Mistral-7B Q4_K_M (~4 GB)



# Edit configuration- **Latency**: 10-30 seconds per chunk

nano .env

```### Core Components



**Key settings:**### Recommended (GPU)

```env

# API Server1. **FastAPI Server** - REST API + WebSocket for real-time updates- **GPU**: NVIDIA GPU with 10+ GB VRAM (RTX 3080, RTX 4080, A4000, etc.)

API_HOST=0.0.0.0

API_PORT=80002. **Worker Queue** - Background job processor with retry logic- **CPU**: 8+ cores



# Database (for production)3. **LLM Inference** - Local llama-cpp-python for AI summarization- **RAM**: 32 GB

DATABASE_URL=postgresql://user:pass@localhost:5432/meetings

4. **PostgreSQL** - Persistent storage with pub/sub messaging- **Storage**: 50 GB

# LLM Settings

MODEL_PATH=/path/to/model.gguf5. **Chunker** - Intelligent text splitting with sliding windows- **Model**: Mistral-7B Q5_K_M or LLaMA-3 8B Q5_K_M (~6-8 GB)

INFERENCE_GPU_LAYERS=35  # Set to 0 for CPU-only

```6. **Merger** - Summary deduplication and consolidation- **Latency**: 2-5 seconds per chunk



### 3. Run - Development Mode (Quick Testing)



```bash---### Optimal (High-throughput)

# Start test server (no PostgreSQL needed, uses mock LLM)

python run_test_server.py- **GPU**: NVIDIA GPU with 24+ GB VRAM (RTX 4090, A6000, etc.)



# In another terminal, test it## 🚀 Quick Start- **CPU**: 16+ cores

./test_cli.sh

```- **RAM**: 64 GB



The test server runs on **http://localhost:8000** with:### 1. Setup- **Storage**: 100 GB

- ✅ In-memory storage

- ✅ Mock summaries- **Model**: LLaMA-3 13B Q5_K_M or Mistral 7B Q8 (~12-16 GB)

- ✅ All API endpoints working

- ✅ Perfect for testing/development```bash- **Latency**: 1-3 seconds per chunk



### 4. Run - Production Mode# Clone and navigate



#### Option A: Quick Start (All-in-one)cd backend## Quick Start



```bash

# Start all services

bash setup.sh        # First time only# Run setup script (creates venv, installs dependencies)### 1. Prerequisites

uvicorn app.main:app --host 0.0.0.0 --port 8000

```bash setup.sh



#### Option B: Full Setup (Separate Services)```bash



```bash# Or manual setup# Install PostgreSQL

# 1. Start PostgreSQL (if not running)

sudo systemctl start postgresqlpython3 -m venv venvsudo apt install postgresql postgresql-contrib



# 2. Initialize databasesource venv/bin/activate

source venv/bin/activate

python db/migrate.pypip install -r requirements.txt# Create database



# 3. Start inference service```sudo -u postgres createdb meeting_summarizer

python inference/serve.py &

sudo -u postgres createuser meeting_user -P

# 4. Start worker

python workers/worker.py &### 2. Configure



# 5. Start API server# Grant privileges

uvicorn app.main:app --host 0.0.0.0 --port 8000

``````bashsudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE meeting_summarizer TO meeting_user;"



---# Copy example config```



## 📚 API Usagecp .env.example .env



### Create Meeting### 2. Install Dependencies



```bash# Edit configuration

curl -X POST http://localhost:8000/meetings \

  -H "Content-Type: application/json" \nano .env```bash

  -d '{

    "title": "Q4 Planning Meeting",```cd backend/

    "metadata": {"department": "Engineering"}

  }'pip install -r requirements.txt



# Returns: {"id": "meeting-uuid", "title": "Q4 Planning Meeting", ...}**Key settings:**

```

```env# For GPU support (CUDA 12.x)

### Add Transcript Segment

# API ServerCMAKE_ARGS="-DLLAMA_CUBLAS=on" pip install llama-cpp-python --force-reinstall --no-cache-dir

```bash

curl -X POST http://localhost:8000/ingest/segment \API_HOST=0.0.0.0

  -H "Content-Type: application/json" \

  -d '{API_PORT=8000# For CPU-only

    "meeting_id": "meeting-uuid",

    "speaker": "Alice",pip install llama-cpp-python

    "timestamp_iso": "2025-11-01T14:00:00Z",

    "text_segment": "Let us discuss Q4 goals and revenue targets."# Database (for production)```

  }'

```DATABASE_URL=postgresql://user:pass@localhost:5432/meetings



### Get Current Summary### 3. Download Model



```bash# LLM Settings

curl http://localhost:8000/meetings/meeting-uuid/summary

```MODEL_PATH=/path/to/model.gguf```bash



**Response:**INFERENCE_GPU_LAYERS=35  # Set to 0 for CPU-onlymkdir -p /path/to/models

```json

{```

  "id": "summary-uuid",

  "type": "incremental",# Download Mistral-7B (recommended for GPU with 10GB+ VRAM)

  "content": {

    "summary": "Team discussed Q4 goals...",### 3. Run - Development Mode (Quick Testing)wget https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q5_K_M.gguf \

    "decisions": [

      {"text": "Hire 3 engineers", "confidence": 0.95}  -O /path/to/models/mistral-7b-instruct-v0.2.Q5_K_M.gguf

    ],

    "action_items": [```bash

      {

        "text": "Prepare job descriptions",# Start test server (no PostgreSQL needed, uses mock LLM)# OR download smaller model for CPU/low VRAM

        "owner": "Alice",

        "due_date_iso": "2025-11-07",python run_test_server.pywget https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf \

        "confidence": 0.9

      }  -O /path/to/models/mistral-7b-instruct-v0.2.Q4_K_M.gguf

    ],

    "topics": [# In another terminal, test it```

      {"name": "Hiring", "confidence": 0.95}

    ]./test_cli.sh

  }

}```### 4. Configure

```



### Finalize Meeting

The test server runs on **http://localhost:8000** with:```bash

```bash

# Mark meeting as complete- ✅ In-memory storagecp .env.example .env

curl -X POST http://localhost:8000/meetings/meeting-uuid/finalize

- ✅ Mock summariesnano .env  # Update with your settings

# Wait 3 seconds for final summary generation

sleep 3- ✅ All API endpoints working```



# Get final summary- ✅ Perfect for testing/development

curl http://localhost:8000/meetings/meeting-uuid/summary

```Key settings:



### WebSocket (Real-time Updates)### 4. Run - Production Mode```env



```javascriptDATABASE_URL=postgresql://meeting_user:your_password@localhost:5432/meeting_summarizer

const ws = new WebSocket('ws://localhost:8000/ws/meeting-uuid');

#### Option A: Quick Start (All-in-one)INFERENCE_MODEL_PATH=/path/to/models/mistral-7b-instruct-v0.2.Q5_K_M.gguf

ws.onmessage = (event) => {

  const data = JSON.parse(event.data);INFERENCE_GPU_LAYERS=35  # Set to 0 for CPU-only

  console.log('Update:', data.type); // 'segment_added', 'summary_update', etc.

};```bash```

```

# Start all services

---

bash setup.sh        # First time only### 5. Run Migrations

## 🧪 Testing

uvicorn app.main:app --host 0.0.0.0 --port 8000

### Automated CLI Test

``````bash

```bash

# Run complete test flowmake migrate

./test_cli.sh

#### Option B: Full Setup (Separate Services)```

# This will:

# 1. Check health

# 2. Create meeting

# 3. Add 5 segments```bash### 6. Start Services

# 4. Get summary

# 5. Finalize# 1. Start PostgreSQL (if not running)

# 6. Get final summary

```sudo systemctl start postgresql```bash



### Frontend UI Testing# Start all services (API + Worker + Inference)



```bash# 2. Initialize databasemake start-all

# Start frontend server

./restart_servers.shsource venv/bin/activate



# Opens on http://localhost:8080/python db/migrate.py# OR start individually in separate terminals:

# - Create meetings via UI

# - Add segments with quick buttonsmake start-inference  # Terminal 1

# - View live summaries

# - Test WebSocket updates# 3. Start inference servicemake start-worker     # Terminal 2

```

python inference/serve.py &make start-api        # Terminal 3

### Manual Testing

```

```bash

# Health check# 4. Start worker

curl http://localhost:8000/healthz

python workers/worker.py &## API Usage

# View API docs

xdg-open http://localhost:8000/docs

```

# 5. Start API server### Create Meeting

---

uvicorn app.main:app --host 0.0.0.0 --port 8000

## 📦 Project Structure

``````bash

```

backend/curl -X POST http://localhost:8000/meetings \

├── app/                    # FastAPI application

│   ├── main.py            # Main API server---  -H "Content-Type: application/json" \

│   ├── notifications.py   # WebSocket & pub/sub

│   └── setup_logging.py   # Logging configuration  -d '{

│

├── workers/               # Background processing## 📚 API Usage    "title": "Q4 Planning Meeting",

│   ├── worker.py         # Job processor

│   ├── chunker.py        # Text chunking    "metadata": {"department": "Engineering", "attendees": 5}

│   └── merger.py         # Summary merging

│### Create Meeting  }'

├── inference/            # LLM service

│   └── serve.py         # llama-cpp inference

│

├── db/                   # Database layer```bash# Response:

│   ├── connection.py    # DB connection pool

│   ├── repositories.py  # CRUD operationscurl -X POST http://localhost:8000/meetings \# {

│   └── migrations/      # SQL migrations

│  -H "Content-Type: application/json" \#   "id": "123e4567-e89b-12d3-a456-426614174000",

├── models/              # Data models

│   └── schemas.py       # Pydantic models  -d '{#   "title": "Q4 Planning Meeting",

│

├── config/              # Configuration    "title": "Q4 Planning Meeting",#   "metadata": {...},

│   └── settings.py      # Environment settings

│    "metadata": {"department": "Engineering"}#   "created_at": "2025-10-31T14:00:00Z",

├── tests/               # Test suite

│   ├── unit/           # Unit tests  }'#   "finalized": false

│   └── integration/    # Integration tests

│# }

├── frontend/           # Web UI for testing

│   └── index.html     # Browser interface# Returns: {"id": "meeting-uuid", "title": "Q4 Planning Meeting", ...}```

│

├── examples/           # Usage examples```

│   ├── curl_examples.sh

│   └── websocket_client.py### Ingest Segments

│

├── run_test_server.py  # Development server (no DB needed)### Add Transcript Segment

├── test_cli.sh         # Automated CLI tests

├── restart_servers.sh  # Server management```bash

├── setup.sh           # Initial setup

├── verify.sh          # Health checks```bashMEETING_ID="123e4567-e89b-12d3-a456-426614174000"

└── requirements.txt   # Python dependencies

```curl -X POST http://localhost:8000/ingest/segment \



---  -H "Content-Type: application/json" \curl -X POST http://localhost:8000/ingest/segment \



## 🔧 Configuration  -d '{  -H "Content-Type: application/json" \



### Environment Variables    "meeting_id": "meeting-uuid",  -d '{



```bash    "speaker": "Alice",    "meeting_id": "'$MEETING_ID'",

# API Server

API_HOST=0.0.0.0              # Listen address    "timestamp_iso": "2025-11-01T14:00:00Z",    "speaker": "Alice",

API_PORT=8000                 # API port

API_WORKERS=4                 # Uvicorn workers    "text_segment": "Let us discuss Q4 goals and revenue targets."    "timestamp_iso": "2025-10-31T14:00:00Z",



# Database  }'    "text_segment": "Let'\''s discuss our Q4 goals and budget allocation."

DATABASE_URL=postgresql://user:pass@localhost:5432/meetings

DB_POOL_SIZE=20              # Connection pool size```  }'



# Redis (optional, for job queue)

REDIS_URL=redis://localhost:6379/0

### Get Current Summary# Response:

# LLM Inference

MODEL_PATH=/path/to/model.gguf# {

INFERENCE_PORT=8001

INFERENCE_GPU_LAYERS=35      # GPU layers (0 = CPU only)```bash#   "segment_id": "223e4567-e89b-12d3-a456-426614174001",

INFERENCE_CONTEXT_SIZE=4096

INFERENCE_BATCH_SIZE=512curl http://localhost:8000/meetings/meeting-uuid/summary#   "status": "accepted"



# Worker```# }

WORKER_BATCH_SIZE=2000       # Tokens per batch

WORKER_BATCH_TIMEOUT=45      # Seconds```

WORKER_MAX_RETRIES=3

WORKER_RETRY_DELAY=5**Response:**

```

```json### WebSocket Stream

---

{

## 🖥️ Hardware Requirements

  "id": "summary-uuid",```javascript

### Minimum (CPU-only)

- **CPU**: 8+ cores  "type": "incremental",// JavaScript client example

- **RAM**: 16 GB

- **Storage**: 20 GB  "content": {const ws = new WebSocket(`ws://localhost:8000/meetings/${meetingId}/stream`);

- **Model**: Mistral-7B Q4_K_M (~4 GB)

- **Latency**: 10-30 seconds per chunk    "summary": "Team discussed Q4 goals...",



### Recommended (GPU)    "decisions": [ws.onmessage = (event) => {

- **GPU**: NVIDIA GPU with 10+ GB VRAM (RTX 3080+)

- **CPU**: 8+ cores      {"text": "Hire 3 engineers", "confidence": 0.95}  const data = JSON.parse(event.data);

- **RAM**: 32 GB

- **Storage**: 50 GB    ],  console.log('Summary update:', data);

- **Model**: Mistral-7B Q5_K_M (~6 GB)

- **Latency**: 2-5 seconds per chunk    "action_items": [};



### Optimal (Production)      {

- **GPU**: NVIDIA GPU with 24+ GB VRAM (RTX 4090, A6000)

- **CPU**: 16+ cores        "text": "Prepare job descriptions",ws.onerror = (error) => {

- **RAM**: 64 GB

- **Storage**: 100 GB        "owner": "Alice",  console.error('WebSocket error:', error);

- **Model**: LLaMA-3 8B or Mistral-7B

- **Latency**: 1-3 seconds per chunk        "due_date_iso": "2025-11-07",};



---        "confidence": 0.9```



## 🗄️ Database Setup      }



### PostgreSQL Installation    ],### Get Summary



```bash    "topics": [

# Ubuntu/Debian

sudo apt install postgresql postgresql-contrib      {"name": "Hiring", "confidence": 0.95}```bash



# macOS    ]curl http://localhost:8000/meetings/$MEETING_ID/summary

brew install postgresql

  }

# Start service

sudo systemctl start postgresql}# Response:

sudo systemctl enable postgresql

``````# {



### Database Creation#   "id": "323e4567-e89b-12d3-a456-426614174002",



```bash### Finalize Meeting#   "meeting_id": "123e4567-e89b-12d3-a456-426614174000",

# Create user and database

sudo -u postgres psql#   "type": "incremental",



CREATE USER meeting_user WITH PASSWORD 'your_password';```bash#   "content": {

CREATE DATABASE meetings OWNER meeting_user;

\q# Mark meeting as complete#     "summary": "Discussion about Q4 goals and budget",



# Update .env with connection stringcurl -X POST http://localhost:8000/meetings/meeting-uuid/finalize#     "decisions": [

DATABASE_URL=postgresql://meeting_user:your_password@localhost:5432/meetings

```#       {"text": "Allocate 40% to engineering", "confidence": 0.9}



### Run Migrations# Wait 3 seconds for final summary generation#     ],



```bashsleep 3#     "action_items": [

source venv/bin/activate

python db/migrate.py#       {

```

# Get final summary#         "text": "Prepare budget breakdown",

---

curl http://localhost:8000/meetings/meeting-uuid/summary#         "owner": "Bob",

## 🤖 LLM Model Setup

```#         "due_date_iso": "2025-11-07",

### Download Model

#         "confidence": 0.85

```bash

# Create models directory### WebSocket (Real-time Updates)#       }

mkdir -p models

#     ],

# Download model (example: Mistral-7B)

cd models```javascript#     "topics": [

wget https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q5_K_M.gguf

const ws = new WebSocket('ws://localhost:8000/ws/meeting-uuid');#       {"name": "Budget Planning", "confidence": 0.95}

# Update .env

MODEL_PATH=/absolute/path/to/backend/models/mistral-7b-instruct-v0.2.Q5_K_M.gguf#     ]

```

ws.onmessage = (event) => {#   },

### Recommended Models

  const data = JSON.parse(event.data);#   "created_at": "2025-10-31T14:05:00Z"

| Model | Size | VRAM | Quality | Speed |

|-------|------|------|---------|-------|  console.log('Update:', data.type); // 'segment_added', 'summary_update', etc.# }

| Mistral-7B Q4_K_M | 4.4 GB | 6 GB | Good | Fast |

| Mistral-7B Q5_K_M | 5.7 GB | 8 GB | Better | Medium |};```

| LLaMA-3 8B Q4_K_M | 4.9 GB | 8 GB | Good | Fast |

| LLaMA-3 8B Q5_K_M | 6.3 GB | 10 GB | Excellent | Medium |```



---### Finalize Meeting



## 🐛 Troubleshooting---



### Server Not Starting```bash



```bash## 🧪 Testingcurl -X POST http://localhost:8000/meetings/$MEETING_ID/finalize

# Check if port is in use

sudo netstat -tuln | grep 8000



# Kill existing process### Automated CLI Test# Response:

pkill -f run_test_server

pkill -f uvicorn# {



# Check logs```bash#   "status": "finalized",

tail -f server.log

```# Run complete test flow#   "meeting_id": "123e4567-e89b-12d3-a456-426614174000"



### Database Connection Error./test_cli.sh# }



```bash```

# Check PostgreSQL is running

sudo systemctl status postgresql# This will:



# Test connection# 1. Check health### Health Check

psql -U meeting_user -d meetings -h localhost

# 2. Create meeting

# Check DATABASE_URL in .env

```# 3. Add 5 segments```bash



### LLM Inference Slow# 4. Get summarycurl http://localhost:8000/healthz



```bash# 5. Finalize

# Check GPU is being used

nvidia-smi# 6. Get final summary# Response:



# Increase GPU layers in .env```# {

INFERENCE_GPU_LAYERS=35  # Increase this number

#   "status": "healthy",

# Use smaller/quantized model

# Q4_K_M is faster than Q5_K_M### Frontend UI Testing#   "database": "healthy",

```

#   "redis": "healthy",

### Out of Memory

```bash#   "inference": "healthy",

```bash

# Reduce context size# Start frontend server#   "timestamp": "2025-10-31T14:10:00Z"

INFERENCE_CONTEXT_SIZE=2048  # Down from 4096

./restart_servers.sh# }

# Reduce batch size

WORKER_BATCH_SIZE=1000  # Down from 2000```



# Use smaller model (Q4 instead of Q5)# Opens on http://localhost:8080/

```

# - Create meetings via UI## Testing

---

# - Add segments with quick buttons

## 📊 Performance Tips

# - View live summaries### Run All Tests

### For Development

- Use `run_test_server.py` (no DB, mock LLM)# - Test WebSocket updates

- Quick iteration and testing

- No GPU needed``````bash



### For Productionmake test

- Use PostgreSQL for persistence

- Enable GPU acceleration### Manual Testing```

- Run worker pool (multiple worker instances)

- Use Redis for better job queue performance

- Monitor with Prometheus/Grafana

```bash### Run Unit Tests Only

### Scaling

```bash# Health check

# Run multiple workers

python workers/worker.py &curl http://localhost:8000/healthz```bash

python workers/worker.py &

python workers/worker.py &make test-unit



# Run API with multiple workers# View API docs```

uvicorn app.main:app --workers 4 --host 0.0.0.0 --port 8000

```xdg-open http://localhost:8000/docs



---```### Run Integration Tests



## 🔐 Security Notes



- **Local Processing**: All data stays on your infrastructure---```bash

- **No External APIs**: LLM runs locally

- **Authentication**: Add JWT/OAuth as needed (extensible)# Ensure services are running first

- **HTTPS**: Use reverse proxy (nginx/traefik) in production

- **Database**: Use strong passwords, limit network access## 📦 Project Structuremake start-all



---



## 📝 API Endpoints```# In another terminal:



| Method | Endpoint | Description |backend/make test-integration

|--------|----------|-------------|

| GET | `/healthz` | Health check |├── app/                    # FastAPI application```

| GET | `/docs` | Interactive API documentation |

| POST | `/meetings` | Create new meeting |│   ├── main.py            # Main API server

| POST | `/ingest/segment` | Add transcript segment |

| GET | `/meetings/{id}/summary` | Get current/final summary |│   ├── notifications.py   # WebSocket & pub/sub### Manual Integration Test

| POST | `/meetings/{id}/finalize` | Mark meeting complete |

| WS | `/ws/{id}` | WebSocket for real-time updates |│   └── setup_logging.py   # Logging configuration



---│```bash



## 🎓 Use Cases├── workers/               # Background processingpython tests/integration/test_full_flow.py



- **Corporate**: Board meetings, standups, planning sessions│   ├── worker.py         # Job processor```

- **Education**: Lectures, student discussions

- **Healthcare**: Consultations, medical rounds│   ├── chunker.py        # Text chunking

- **Legal**: Depositions, client meetings

- **Remote Work**: Zoom/Teams meeting notes│   └── merger.py         # Summary merging## Development



---│



## 📦 Dependencies├── inference/            # LLM service### Format Code



- **Python**: 3.10+│   └── serve.py         # llama-cpp inference

- **FastAPI**: Web framework

- **PostgreSQL**: Database (production)│```bash

- **llama-cpp-python**: LLM inference

- **Uvicorn**: ASGI server├── db/                   # Database layermake format

- **AsyncPG**: Async PostgreSQL driver

- **Pydantic**: Data validation│   ├── connection.py    # DB connection pool```

- **Redis**: Optional job queue

│   ├── repositories.py  # CRUD operations

---

│   └── migrations/      # SQL migrations### Lint Code

## 🤝 Contributing

│

1. Fork the repository

2. Create feature branch├── models/              # Data models```bash

3. Make changes

4. Run tests: `pytest tests/`│   └── schemas.py       # Pydantic modelsmake lint

5. Submit pull request

│```

---

├── config/              # Configuration

## 📄 License

│   └── settings.py      # Environment settings### Clean Cache

See LICENSE file in repository root.

│

---

├── tests/               # Test suite```bash

## 🚀 Quick Commands Reference

│   ├── unit/           # Unit testsmake clean

```bash

# Setup│   └── integration/    # Integration tests```

bash setup.sh

│

# Start development server

python run_test_server.py├── frontend/           # Web UI for testing## Configuration Reference



# Start production services│   └── index.html     # Browser interface

python inference/serve.py &

python workers/worker.py &│| Variable | Default | Description |

uvicorn app.main:app --host 0.0.0.0 --port 8000

├── examples/           # Usage examples|----------|---------|-------------|

# Test

./test_cli.sh│   ├── curl_examples.sh| `DATABASE_URL` | `postgresql://...` | PostgreSQL connection string |

curl http://localhost:8000/healthz

│   └── websocket_client.py| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection string |

# Stop services

pkill -f run_test_server│| `API_HOST` | `127.0.0.1` | FastAPI bind address |

pkill -f uvicorn

pkill -f worker.py├── run_test_server.py  # Development server (no DB needed)| `API_PORT` | `8000` | FastAPI port |

pkill -f serve.py

```├── test_cli.sh         # Automated CLI tests| `INFERENCE_HOST` | `127.0.0.1` | Inference service host |



---├── restart_servers.sh  # Server management| `INFERENCE_PORT` | `8001` | Inference service port |



**Happy Meeting Summarizing! 🎉**├── setup.sh           # Initial setup| `INFERENCE_MODEL_PATH` | `/models/...` | Path to GGUF model file |


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
