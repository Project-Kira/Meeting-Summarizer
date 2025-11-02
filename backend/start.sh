#!/bin/bash
# Startup script for Meeting Summarizer Backend
# Validates environment and starts the application

set -e

echo "=== Meeting Summarizer Backend Startup ==="
echo "Timestamp: $(date)"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Python is available
if ! command -v python &> /dev/null; then
    echo -e "${RED}Error: Python not found${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} Python found: $(python --version)"

# Check if required dependencies are installed
echo "Checking dependencies..."
if ! python -c "import llama_cpp" 2>/dev/null; then
    echo -e "${RED}Error: llama-cpp-python not installed${NC}"
    echo "Install with: pip install -r requirements.txt"
    exit 1
fi
echo -e "${GREEN}✓${NC} llama-cpp-python installed"

if ! python -c "import fastapi" 2>/dev/null; then
    echo -e "${RED}Error: FastAPI not installed${NC}"
    echo "Install with: pip install -r requirements.txt"
    exit 1
fi
echo -e "${GREEN}✓${NC} FastAPI installed"

# Check if model file exists
MODEL_PATH="${MODEL_PATH:-models/mistral-7b-instruct-v0.2.Q4_K_M.gguf}"
if [ ! -f "$MODEL_PATH" ]; then
    echo -e "${YELLOW}Warning: Model file not found at $MODEL_PATH${NC}"
    echo "The application will fail when attempting to load the model."
    echo "Please place your GGUF model file in the correct location."
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo -e "${GREEN}✓${NC} Model file found: $MODEL_PATH"
fi

# Create logs directory if it doesn't exist
LOG_DIR="${LOG_DIR:-logs}"
mkdir -p "$LOG_DIR"
echo -e "${GREEN}✓${NC} Logs directory: $LOG_DIR"

# Determine startup mode
MODE="${1:-api}"

echo ""
echo "=== Starting Application ==="
echo "Mode: $MODE"
echo "Port: ${API_PORT:-8000}"
echo "Log Level: ${LOG_LEVEL:-INFO}"
echo ""

case "$MODE" in
    api)
        echo "Starting API server..."
        exec python -m uvicorn api:app --host "${API_HOST:-0.0.0.0}" --port "${API_PORT:-8000}"
        ;;
    cli)
        if [ -z "$2" ]; then
            echo -e "${RED}Error: CLI mode requires a file path${NC}"
            echo "Usage: ./start.sh cli <path/to/conversation.txt>"
            exit 1
        fi
        echo "Running CLI with file: $2"
        exec python main.py "$2"
        ;;
    test)
        echo "Running tests..."
        if [ ! -f "requirements-dev.txt" ]; then
            echo -e "${RED}Error: requirements-dev.txt not found${NC}"
            exit 1
        fi
        # Install test dependencies if not present
        if ! python -c "import pytest" 2>/dev/null; then
            echo "Installing test dependencies..."
            pip install -r requirements-dev.txt
        fi
        exec python -m pytest tests/ -v
        ;;
    *)
        echo -e "${RED}Error: Unknown mode '$MODE'${NC}"
        echo "Usage: ./start.sh [api|cli|test] [args...]"
        echo "  api          - Start FastAPI server (default)"
        echo "  cli <file>   - Run CLI with specified file"
        echo "  test         - Run test suite"
        exit 1
        ;;
esac
