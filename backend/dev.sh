#!/bin/bash
# Development helper script - start, stop, verify services

set -e

case "$1" in
  start)
    echo "�� Starting services..."
    pkill -f 'run_test_server\|http.server 8080' 2>/dev/null || true
    sleep 1
    
    # Start backend
    source venv/bin/activate 2>/dev/null || true
    python run_test_server.py > server.log 2>&1 &
    echo "✅ Backend: http://localhost:8000"
    
    # Start frontend
    cd frontend && python3 -m http.server 8080 > /tmp/frontend.log 2>&1 &
    echo "✅ Frontend: http://localhost:8080"
    
    sleep 2
    curl -sf http://localhost:8000/healthz > /dev/null && echo "✅ Ready" || echo "❌ Check logs"
    ;;
    
  stop)
    echo "🛑 Stopping services..."
    pkill -f 'run_test_server\|http.server 8080' 2>/dev/null || true
    echo "✅ Stopped"
    ;;
    
  restart)
    $0 stop && sleep 1 && $0 start
    ;;
    
  status)
    echo "📊 Service Status:"
    if pgrep -f run_test_server > /dev/null; then
      echo "✅ Backend running (PID: $(pgrep -f run_test_server))"
      curl -sf http://localhost:8000/healthz > /dev/null && echo "   Health: OK" || echo "   Health: FAIL"
    else
      echo "❌ Backend not running"
    fi
    
    if pgrep -f 'http.server 8080' > /dev/null; then
      echo "✅ Frontend running (PID: $(pgrep -f 'http.server 8080'))"
    else
      echo "❌ Frontend not running"
    fi
    ;;
    
  verify)
    echo "🔍 Verifying installation..."
    
    # Branch
    BRANCH=$(git branch --show-current)
    [ "$BRANCH" = "backend-implementation" ] && echo "✅ Branch: $BRANCH" || echo "⚠️  Branch: $BRANCH"
    
    # Structure
    for d in app workers models db inference config; do
      [ -d "$d" ] && echo "✅ $d/" || echo "❌ Missing $d/"
    done
    
    # Files
    for f in README.md requirements.txt setup.sh run_test_server.py; do
      [ -f "$f" ] && echo "✅ $f" || echo "❌ Missing $f"
    done
    
    # Venv
    [ -d "venv" ] && echo "✅ venv/" || echo "❌ Run: bash setup.sh"
    
    # Dependencies
    if [ -d "venv" ]; then
      source venv/bin/activate
      python -c "import fastapi, pydantic" 2>/dev/null && echo "✅ Dependencies" || echo "❌ Run: pip install -r requirements.txt"
    fi
    ;;
    
  logs)
    echo "📋 Recent logs:"
    [ -f server.log ] && tail -20 server.log || echo "No server.log found"
    ;;
    
  *)
    echo "Usage: bash dev.sh {start|stop|restart|status|verify|logs}"
    echo ""
    echo "Commands:"
    echo "  start    - Start backend + frontend"
    echo "  stop     - Stop all services"
    echo "  restart  - Restart all services"
    echo "  status   - Show service status"
    echo "  verify   - Verify installation"
    echo "  logs     - Show recent logs"
    exit 1
    ;;
esac
