#!/bin/bash
set -e

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

echo "🛑 Stopping Holon services..."

# 1. Stop Local Background Processes
if [ -f ".holon_pids" ]; then
    echo "   Found local background processes..."
    PIDS=$(cat .holon_pids)
    
    for PID in $PIDS; do
        if ps -p $PID > /dev/null; then
            echo "   Killing PID $PID..."
            kill $PID || true
        else
            echo "   PID $PID already stopped."
        fi
    done
    
    rm .holon_pids
    echo "   Local processes stopped."
fi

# 2. Stop Docker Containers
# Only run if docker-compose file exists and docker is available
if command -v docker-compose &> /dev/null && [ -f "docker-compose.yaml" ]; then
    # Quiet check if anything is running
    if [ -n "$(docker-compose ps -q 2>/dev/null)" ]; then
        echo "   Stopping Docker containers..."
        docker-compose down > /dev/null 2>&1
        echo "   Docker services stopped."
    fi
fi

echo "✅  All Holon services stopped."
