#!/bin/bash
# Quick setup script for Meeting Summarizer backend

set -e

echo "===================================="
echo "Meeting Summarizer - Quick Setup"
echo "===================================="
echo ""

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $PYTHON_VERSION"

# Check PostgreSQL
if command -v psql &> /dev/null; then
    echo "✓ PostgreSQL installed"
else
    echo "✗ PostgreSQL not found. Install with: sudo apt install postgresql"
    exit 1
fi

# Create virtual environment
if [ ! -d "venv" ]; then
    echo ""
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✓ Dependencies installed"

# Setup .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo ""
    echo "Creating .env file..."
    cp .env.example .env
    echo "✓ .env file created"
    echo ""
    echo "⚠️  Please edit .env and configure:"
    echo "   - DATABASE_URL"
    echo "   - INFERENCE_MODEL_PATH"
    echo "   - INFERENCE_API_KEY"
fi

# Check if database exists
echo ""
echo "Checking database..."
DB_EXISTS=$(psql -U postgres -tAc "SELECT 1 FROM pg_database WHERE datname='meeting_summarizer'" 2>/dev/null || echo "0")

if [ "$DB_EXISTS" != "1" ]; then
    echo "Creating database..."
    sudo -u postgres psql -c "CREATE DATABASE meeting_summarizer;"
    sudo -u postgres psql -c "CREATE USER meeting_user WITH PASSWORD 'meeting_pass';"
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE meeting_summarizer TO meeting_user;"
    echo "✓ Database created"
else
    echo "✓ Database already exists"
fi

# Run migrations
echo ""
echo "Running database migrations..."
python -m db.migrate
echo "✓ Migrations completed"

echo ""
echo "===================================="
echo "✓ Setup completed successfully!"
echo "===================================="
echo ""
echo "Next steps:"
echo "1. Edit .env file with your configuration"
echo "2. Download a model (see README.md)"
echo "3. Run services:"
echo "   make start-all"
echo ""
echo "Or start services individually:"
echo "   make start-inference  # Terminal 1"
echo "   make start-worker     # Terminal 2"
echo "   make start-api        # Terminal 3"
echo ""
echo "Test the API:"
echo "   ./examples/curl_examples.sh"
echo ""
