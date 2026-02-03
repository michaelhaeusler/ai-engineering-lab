#!/bin/bash

# Check status of development servers
echo "📊 RAG PDF Chat Development Server Status"
echo "=============================================="

# Check backend server
backend_pid=$(lsof -ti :8000 2>/dev/null)
if [ -n "$backend_pid" ]; then
    echo "✅ Backend (FastAPI):  RUNNING on port 8000 (PID: $backend_pid)"
    echo "   🔗 http://localhost:8000"
else
    echo "❌ Backend (FastAPI):  NOT RUNNING"
fi

# Check frontend server
frontend_pid=$(lsof -ti :3000 2>/dev/null)
if [ -n "$frontend_pid" ]; then
    echo "✅ Frontend (Next.js): RUNNING on port 3000 (PID: $frontend_pid)"
    echo "   🔗 http://localhost:3000"
else
    echo "❌ Frontend (Next.js): NOT RUNNING"
fi

echo ""
if [ -f ".dev-pids" ]; then
    echo "📝 PID file exists - servers were started with ./start-dev.sh"
else
    echo "📝 No PID file found - servers may have been started manually"
fi

echo ""
echo "💡 Commands:"
echo "   ./start-dev.sh     - Start both frontend and backend servers"
echo "   ./stop-dev.sh      - Stop both servers"
echo "   ./start-backend.sh - Start only backend (alternative)"
echo ""
echo "✨ Beautiful new Apple-inspired frontend ready!"
