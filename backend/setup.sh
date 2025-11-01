#!/bin/bash
# Quick setup script

set -e

echo "🚀 Meeting Summarizer Setup"

# Check dependencies
command -v python3 >/dev/null || { echo "❌ Python 3 required"; exit 1; }
echo "✅ Python: $(python3 --version)"

# Virtual environment
if [ ! -d "venv" ]; then
  echo "📦 Creating virtual environment..."
  python3 -m venv venv
fi

# Install
echo "📦 Installing dependencies..."
source venv/bin/activate
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo "✅ Dependencies installed"

# Config
if [ ! -f ".env" ]; then
  [ -f ".env.example" ] && cp .env.example .env && echo "✅ Created .env" || echo "⚠️  No .env.example found"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  bash dev.sh start    # Start dev servers"
echo "  bash test_cli.sh     # Run tests"
