#!/bin/bash
set -e

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

# Ensure holon.db exists as a file so Docker doesn't create it as a directory
if [ ! -f "holon.db" ]; then
    echo "Creating holon.db..."
    touch holon.db
fi

echo "Starting Holon services (output suppressed)..."

# Start services in detached mode, suppressing output.
# If it fails, we rerun with logs visible to show the error.
if ! docker-compose up -d --build --remove-orphans > /dev/null 2>&1; then
    echo ""
    echo "❌ Failed to start Holon services. Retrying with full logging to diagnose:"
    docker-compose up -d --build --remove-orphans
    exit 1
fi

echo ""
echo "----------------------------------------------------------------"
echo "🚀 Holon local environment is ready!"
echo "----------------------------------------------------------------"
echo "📱 Web Dashboard:  http://localhost:3000"
echo "🔌 API Swagger UI: http://localhost:8000/docs"
echo ""
echo "Commands:"
echo "  - View logs:    docker-compose logs -f"
echo "  - Stop:         ./scripts/stop_local.sh"
echo "----------------------------------------------------------------"
