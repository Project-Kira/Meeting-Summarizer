#!/bin/bash
# Quick setup script for Meeting Summarizer backend

echo "Setting up Meeting Summarizer Backend..."
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "[OK] Python 3 found: $(python3 --version)"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to create virtual environment"
    exit 1
fi

echo "[OK] Virtual environment created"
echo ""

# Activate virtual environment and install dependencies
echo "Installing dependencies..."
source venv/bin/activate
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to install dependencies"
    exit 1
fi

echo "[OK] Dependencies installed"
echo ""

# Verify model file exists
if [ -f "models/mistral-7b-instruct-v0.2.Q4_K_M.gguf" ]; then
    MODEL_SIZE=$(du -h "models/mistral-7b-instruct-v0.2.Q4_K_M.gguf" | cut -f1)
    echo "[OK] Model file found: $MODEL_SIZE"
else
    echo "[WARNING] Model file not found at models/mistral-7b-instruct-v0.2.Q4_K_M.gguf"
    echo "          Please download the model before running."
fi

echo ""
echo "Setup complete."
echo ""
echo "To use the summarizer:"
echo "  1. Activate the virtual environment: source venv/bin/activate"
echo "  2. Run: python main.py conversation.txt"
echo ""
echo "For more information, see BACKEND_README.md"
