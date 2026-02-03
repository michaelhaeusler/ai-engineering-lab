#!/bin/bash

# Stop both frontend and backend development servers
echo "🛑 Stopping RAG PDF Chat Development Servers..."

# Function to kill process by PID
kill_process() {
    local pid=$1
    local name=$2
    
    if kill -0 "$pid" 2>/dev/null; then
        echo "🔴 Stopping $name (PID: $pid)..."
        kill "$pid"
        
        # Wait for graceful shutdown
        local count=0
        while kill -0 "$pid" 2>/dev/null && [ $count -lt 5 ]; do
            sleep 1
            count=$((count + 1))
        done
        
        # Force kill if still running
        if kill -0 "$pid" 2>/dev/null; then
            echo "⚡ Force stopping $name..."
            kill -9 "$pid" 2>/dev/null
        fi
        
        echo "✅ $name stopped"
    else
        echo "ℹ️  $name was not running"
    fi
}

# Read PIDs from file if it exists
if [ -f ".dev-pids" ]; then
    echo "📖 Reading server PIDs from .dev-pids..."
    readarray -t pids < .dev-pids
    
    if [ ${#pids[@]} -ge 2 ]; then
        kill_process "${pids[0]}" "Backend (FastAPI)"
        kill_process "${pids[1]}" "Frontend (Next.js)"
    elif [ ${#pids[@]} -ge 1 ]; then
        kill_process "${pids[0]}" "Backend (FastAPI)"
    fi
    
    # Clean up PID file
    rm -f .dev-pids
    echo "🧹 Cleaned up PID file"
else
    echo "📋 No PID file found, searching for running servers..."
    
    # Find and kill backend server (Python/FastAPI on port 8000)
    backend_pid=$(lsof -ti :8000 2>/dev/null)
    if [ -n "$backend_pid" ]; then
        kill_process "$backend_pid" "Backend (FastAPI on port 8000)"
    else
        echo "ℹ️  No backend server found on port 8000"
    fi
    
    # Find and kill frontend server (Node.js on port 3000)
    frontend_pid=$(lsof -ti :3000 2>/dev/null)
    if [ -n "$frontend_pid" ]; then
        kill_process "$frontend_pid" "Frontend (Next.js on port 3000)"
    else
        echo "ℹ️  No frontend server found on port 3000"
    fi
fi

# Additional cleanup - kill any remaining Node.js processes that might be related
echo "🧹 Cleaning up any remaining development processes..."
pkill -f "npm run dev" 2>/dev/null && echo "✅ Stopped npm dev processes" || echo "ℹ️  No npm dev processes found"
pkill -f "next dev" 2>/dev/null && echo "✅ Stopped Next.js dev processes" || echo "ℹ️  No Next.js dev processes found"

echo ""
echo "🎉 All development servers stopped!"
echo "💡 Run ./start-dev.sh to start them again"
