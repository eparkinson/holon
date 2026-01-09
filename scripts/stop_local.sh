#!/bin/bash
set -e

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

echo "🛑 Stopping Holon services..."

CONTAINER_NAME="holon-unified"

# 1. Stop Unified Container if running
if command -v docker &> /dev/null; then
    if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        echo "   Stopping unified container..."
        docker stop ${CONTAINER_NAME} > /dev/null 2>&1 || true
        docker rm ${CONTAINER_NAME} > /dev/null 2>&1 || true
        echo "   Unified container stopped."
    fi
fi

# 2. Stop Local Background Processes
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

# 3. Stop Docker Compose Services
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
