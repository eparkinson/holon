#!/bin/bash
set -e

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

SKIP_ENGINE=0
SKIP_WEB=0

for arg in "$@"
do
    if [ "$arg" == "--no-engine" ]; then
        SKIP_ENGINE=1
    fi
    if [ "$arg" == "--no-web" ]; then
        SKIP_WEB=1
    fi
done

SERVICES=""
if [ $SKIP_ENGINE -eq 0 ]; then
    SERVICES="$SERVICES engine"
fi
if [ $SKIP_WEB -eq 0 ]; then
    SERVICES="$SERVICES web"
fi

if [ -z "$SERVICES" ]; then
    echo "Nothing to start (both --no-engine and --no-web specified)."
    exit 0
fi

# Ensure holon_data directory exists
if [ ! -d "holon_data" ]; then
    echo "Creating holon_data directory..."
    mkdir holon_data
fi

echo "Starting Holon services (output suppressed)..."

# Start services in detached mode, suppressing output.
# If it fails, we rerun with logs visible to show the error.
if ! docker-compose up -d --build --remove-orphans $SERVICES > /dev/null 2>&1; then
    echo ""
    echo "❌ Failed to start Holon services. Retrying with full logging to diagnose:"
    docker-compose up -d --build --remove-orphans $SERVICES
    exit 1
fi

echo ""
echo "----------------------------------------------------------------"
echo "🚀 Holon local environment is ready!"
echo "----------------------------------------------------------------"
if [ $SKIP_WEB -eq 0 ]; then
    echo "📱 Web Dashboard:  http://localhost:3000"
fi
if [ $SKIP_ENGINE -eq 0 ]; then
    echo "🔌 API Swagger UI: http://localhost:8000/docs"
fi
echo ""
echo "Commands:"
echo "  - View logs:    docker-compose logs -f"
echo "  - Stop:         ./scripts/stop_local.sh"
echo "----------------------------------------------------------------"
