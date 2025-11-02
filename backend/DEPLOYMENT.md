# Meeting Summarizer Backend - Deployment Guide

## Quick Start

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Start API server
./start.sh api

# Or run CLI
./start.sh cli conversation.txt

# Run tests
./start.sh test
```

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

## Configuration

All configuration via environment variables. See `.env.example` for all options.

Key settings:
- `MODEL_PATH`: Path to GGUF model file
- `API_PORT`: API server port (default: 8000)
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `ENABLE_FILE_LOGGING`: Enable rotating file logs (default: true)
- `N_THREADS`: CPU threads for inference (default: 4)

## Docker Setup

### Building the Image

```bash
docker build -t meeting-summarizer-backend .
```

### Running the Container

```bash
docker run -d \
  -p 8000:8000 \
  -v $(pwd)/models:/app/models:ro \
  -v $(pwd)/logs:/app/logs \
  -e MODEL_PATH=models/mistral-7b-instruct-v0.2.Q4_K_M.gguf \
  --name summarizer \
  meeting-summarizer-backend
```

## Logging

Dual logging system:
- **Console**: Always enabled, useful for development
- **File**: Rotating logs in `logs/` directory (10MB max, 5 backups)

Configure with:
```bash
export ENABLE_FILE_LOGGING=true
export LOG_DIR=logs
export LOG_FILE=meeting_summarizer.log
export LOG_LEVEL=INFO
```

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html

# Run specific test file
pytest tests/test_api.py -v
```

## CI/CD

GitHub Actions workflow automatically:
- Runs tests on Python 3.10, 3.11, 3.12
- Checks code formatting (black)
- Lints code (ruff)
- Type checks (mypy)
- Generates coverage reports

## Production Checklist

- [ ] Set `LOG_LEVEL=WARNING` or `ERROR`
- [ ] Configure `N_THREADS` based on CPU cores
- [ ] Set appropriate `MAX_INPUT_LENGTH` limits
- [ ] Enable file logging for audit trails
- [ ] Configure CORS origins for your frontend
- [ ] Use volume mounts for logs and models
- [ ] Set resource limits in docker-compose.yml
- [ ] Monitor disk space for log rotation

## Troubleshooting

**Model not loading:**
```bash
# Verify model path
ls -lh models/

# Check logs
docker-compose logs backend
```

**High memory usage:**
```bash
# Reduce context window
export N_CTX=4096

# Reduce threads
export N_THREADS=2
```

**API not responding:**
```bash
# Check health endpoint
curl http://localhost:8000/api/health

# View startup logs
./start.sh api
```
