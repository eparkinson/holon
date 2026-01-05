#!/bin/bash
set -e

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

# Check if any containers exist (running or stopped)
if [ -z "$(docker-compose ps -q 2>/dev/null)" ]; then
    echo "ℹ️  No Holon containers found. Verifying cleanup..."
else
    echo "🛑 Stopping Holon services..."
fi

# Run down to ensure containers are stopped/removed and networks cleaned
if docker-compose down; then
    echo "✅  Holon services are stopped."
else
    echo "❌  Error: Failed to stop Holon services."
    exit 1
fi
