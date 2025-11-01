# 🚀 Deployment Checklist - Meeting Summarizer Backend

## ✅ Pre-Deployment Verification

Run the automated verification:
```bash
cd backend/
./verify.sh
```

Expected output: All checks pass ✓

## 📋 Deployment Steps (Zero Manual Intervention)

### Step 1: Initial Setup
```bash
cd backend/
./setup.sh
```

This automatically:
- Creates virtual environment
- Installs all dependencies
- Creates database (if not exists)
- Runs migrations
- Creates .env file from template

### Step 2: Configure Environment
Edit `.env` file and update:
```bash
nano .env
```

Required changes:
- `INFERENCE_MODEL_PATH` - Point to your downloaded GGUF model
- `DATABASE_URL` - Update password if needed
- `INFERENCE_API_KEY` - Set a secure API key

### Step 3: Download Model (One-time)
```bash
# For GPU with 10GB+ VRAM (recommended)
wget https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q5_K_M.gguf \
  -O /path/to/models/mistral-7b-instruct-v0.2.Q5_K_M.gguf

# For CPU or low VRAM
wget https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf \
  -O /path/to/models/mistral-7b-instruct-v0.2.Q4_K_M.gguf
```

### Step 4: Start Services
```bash
# Option A: Start all services together
make start-all

# Option B: Start individually (3 terminals)
# Terminal 1:
make start-inference

# Terminal 2:
make start-worker

# Terminal 3:
make start-api
```

### Step 5: Verify Deployment
```bash
# Check health
curl http://localhost:8000/healthz

# Run example
./examples/curl_examples.sh
```

## 🧪 Testing Deployment

### Automated Test Suite
```bash
# Run all tests
make test

# Run only unit tests
make test-unit

# Run integration tests (requires services running)
make test-integration
```

### Manual Integration Test
```bash
# Terminal 1: Start services
make start-all

# Terminal 2: Run integration test
python tests/integration/test_full_flow.py
```

### Example Client Test
```bash
# Python WebSocket client
python examples/websocket_client.py

# Bash curl examples
./examples/curl_examples.sh
```

## 📊 Verification Checklist

- [ ] All services start without errors
- [ ] Health check returns "healthy" status
- [ ] Database migrations applied successfully
- [ ] Inference service loads model (or runs in mock mode)
- [ ] Can create meeting via API
- [ ] Can ingest segments
- [ ] Worker processes jobs
- [ ] Summaries are generated
- [ ] WebSocket delivers real-time updates
- [ ] Final summary contains action items

## 🔧 Troubleshooting

### Database Connection Failed
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Restart if needed
sudo systemctl restart postgresql

# Test connection
psql -U meeting_user -d meeting_summarizer -h localhost
```

### Model Not Loading
```bash
# Check file exists
ls -lh $INFERENCE_MODEL_PATH

# Check GPU
nvidia-smi

# Try CPU mode
# Edit .env: INFERENCE_GPU_LAYERS=0
```

### Port Already in Use
```bash
# Check what's using port 8000
sudo lsof -i :8000

# Change port in .env
# API_PORT=8001
```

### Worker Not Processing Jobs
```bash
# Check worker logs
# Should see "Starting worker..." message

# Check job queue
psql -U meeting_user -d meeting_summarizer -c "SELECT * FROM jobs WHERE status='pending';"

# Restart worker
pkill -f "python -m workers.worker"
make start-worker
```

## 📈 Performance Validation

### Expected Latencies

| Component | CPU | GPU (10GB) | GPU (24GB) |
|-----------|-----|------------|------------|
| Segment ingestion | <50ms | <50ms | <50ms |
| Chunk processing | 15-30s | 2-5s | 1-3s |
| Summary merging | <500ms | <500ms | <500ms |
| WebSocket update | <100ms | <100ms | <100ms |

### Load Testing
```bash
# Simulate meeting with multiple segments
for i in {1..10}; do
  curl -X POST http://localhost:8000/ingest/segment \
    -H "Content-Type: application/json" \
    -d "{\"meeting_id\": \"$MEETING_ID\", \"speaker\": \"Speaker$i\", \"timestamp_iso\": \"2025-10-31T14:0$i:00Z\", \"text_segment\": \"Test segment $i\"}"
done
```

## 🔐 Security Checklist

- [ ] API key set for inference service
- [ ] Database password changed from default
- [ ] CORS origins configured for production
- [ ] Services bound to localhost (not 0.0.0.0)
- [ ] .env file not committed to git
- [ ] Logs don't contain sensitive data

## 🎯 Production Readiness

### Minimum Requirements Met
- ✅ All endpoints implemented
- ✅ Error handling with retries
- ✅ Structured logging
- ✅ Health checks
- ✅ Input validation
- ✅ Database migrations
- ✅ Real-time notifications
- ✅ Comprehensive tests

### Optional Enhancements for Scale
- [ ] Redis for pub/sub (vs PostgreSQL NOTIFY)
- [ ] Load balancer for inference
- [ ] Database replication
- [ ] Prometheus metrics export
- [ ] Distributed tracing
- [ ] Rate limiting
- [ ] API authentication
- [ ] Docker containers
- [ ] Kubernetes deployment
- [ ] CI/CD pipeline

## 📝 Deployment Verification Log

After deployment, document:

```
Date: _______________
Deployed by: _______________
Branch: backend-implementation
Commit: 4140ce9

✓ Services Started:
  - API Server: http://localhost:8000
  - Inference: http://localhost:8001
  - Worker: Running
  - Database: Connected

✓ Health Check: PASSED
✓ Example Test: PASSED
✓ Integration Test: PASSED

Performance Metrics:
  - Avg segment ingestion: ___ ms
  - Avg summary generation: ___ seconds
  - Active meetings: ___
  - Queue length: ___

Notes:
_________________________________
_________________________________
```

## 🎉 Deployment Complete!

Your Meeting Summarizer backend is now running and ready to process meetings in real-time with zero manual intervention required during operation.

Access:
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/healthz
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Happy summarizing! 🚀
