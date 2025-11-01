#!/bin/bash
# Restart both frontend and backend servers

echo "🔄 Restarting Meeting Summarizer Services..."
echo ""

# Stop existing servers
echo "Stopping existing servers..."
pkill -f 'run_test_server' 2>/dev/null
pkill -f 'http.server 8080' 2>/dev/null
sleep 2

# Start backend
echo "Starting backend server..."
cd /home/user/kali/projects/30days/Meeting-Summarizer/backend
source venv/bin/activate
python run_test_server.py > server.log 2>&1 &
BACKEND_PID=$!
echo "✅ Backend started (PID: $BACKEND_PID)"

# Wait for backend to start
sleep 3

# Test backend
if curl -s http://localhost:8000/healthz > /dev/null; then
    echo "✅ Backend is healthy"
else
    echo "❌ Backend failed to start"
    exit 1
fi

# Start frontend
echo "Starting frontend server..."
cd frontend
python3 -m http.server 8080 > /tmp/frontend-server.log 2>&1 &
FRONTEND_PID=$!
echo "✅ Frontend started (PID: $FRONTEND_PID)"

sleep 2

# Test frontend
if curl -s http://localhost:8080/ > /dev/null; then
    echo "✅ Frontend is accessible"
else
    echo "❌ Frontend failed to start"
    exit 1
fi

echo ""
echo "============================================"
echo "✅ Both services are running!"
echo "============================================"
echo "Frontend: http://localhost:8080/"
echo "Backend:  http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo "============================================"
echo ""
echo "To view logs:"
echo "  Backend:  tail -f server.log"
echo "  Frontend: tail -f /tmp/frontend-server.log"
echo ""
echo "To stop services:"
echo "  pkill -f 'run_test_server'"
echo "  pkill -f 'http.server 8080'"
echo ""

# Open browser
echo "Opening browser..."
xdg-open http://localhost:8080/ || firefox http://localhost:8080/

echo "✅ Ready to test!"
