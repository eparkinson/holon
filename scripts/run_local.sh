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

# Function to handle cleanup on exit
cleanup() {
    echo ""
    echo "Stopping Holon services..."
    docker-compose down
}

# Set trap to call cleanup function on script exit (including Ctrl+C)
trap cleanup EXIT

echo "Starting Holon Engine and Web Dashboard..."
docker-compose up -d --build

echo ""
echo "----------------------------------------------------------------"
echo "🚀 Holon is up and running!"
echo ""
echo "📱 Web Dashboard:  http://localhost:3000"
echo "🔌 API Swagger UI: http://localhost:8000/docs"
echo "----------------------------------------------------------------"
echo ""
echo "Tailing logs (Press Ctrl+C to stop services)..."
echo ""

docker-compose logs -f
