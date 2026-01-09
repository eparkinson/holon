#!/bin/bash
set -e

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

USE_DOCKER=0
USE_CONTAINER=0
SKIP_ENGINE=0
SKIP_WEB=0

for arg in "$@"
do
    if [ "$arg" == "--docker" ]; then
        USE_DOCKER=1
    fi
    if [ "$arg" == "--container" ]; then
        USE_CONTAINER=1
    fi
    if [ "$arg" == "--no-engine" ]; then
        SKIP_ENGINE=1
    fi
    if [ "$arg" == "--no-web" ]; then
        SKIP_WEB=1
    fi
done

# Ensure holon_data directory exists
if [ ! -d "holon_data" ]; then
    echo "Creating holon_data directory..."
    mkdir holon_data
fi

if [ $USE_CONTAINER -eq 1 ]; then
    echo "🐳 Starting Holon unified container..."
    
    CONTAINER_NAME="holon-unified"
    
    # Check if container is already running
    if docker ps -a --filter "name=^${CONTAINER_NAME}$" --format '{{.Names}}' | grep -q "${CONTAINER_NAME}"; then
        echo "Stopping existing container..."
        docker stop ${CONTAINER_NAME} > /dev/null 2>&1 || true
        docker rm ${CONTAINER_NAME} > /dev/null 2>&1 || true
    fi
    
    # Build web app if dist directory doesn't exist
    if [ ! -d "web/dist" ]; then
        echo "Building web app..."
        cd web
        if command -v pnpm &> /dev/null; then
            pnpm install && pnpm build
        elif command -v npm &> /dev/null; then
            npm install && npm run build
        else
            echo "❌ Neither pnpm nor npm found. Please install Node.js and npm/pnpm first."
            exit 1
        fi
        cd ..
    fi
    
    echo "Building unified container image..."
    if ! docker build -f Dockerfile.unified -t holon-unified:latest . > /dev/null 2>&1; then
        echo ""
        echo "❌ Failed to build container. Retrying with full logging to diagnose:"
        docker build -f Dockerfile.unified -t holon-unified:latest .
        exit 1
    fi
    
    echo "Starting container..."
    docker run -d \
        --name ${CONTAINER_NAME} \
        -p 80:80 \
        -v "${PROJECT_ROOT}/holon_data:/app/holon_data" \
        holon-unified:latest
    
    echo ""
    echo "----------------------------------------------------------------"
    echo "🚀 Holon unified container is ready!"
    echo "----------------------------------------------------------------"
    echo "📱 Web Dashboard:  http://localhost"
    echo "🔌 API Swagger UI: http://localhost/docs"
    echo ""
    echo "Commands:"
    echo "  - View logs:    docker logs -f ${CONTAINER_NAME}"
    echo "  - Stop:         docker stop ${CONTAINER_NAME}"
    echo "  - Remove:       docker rm ${CONTAINER_NAME}"
    echo "----------------------------------------------------------------"

elif [ $USE_DOCKER -eq 1 ]; then
    echo "🐳 Starting Holon services with Docker..."

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
    echo "🚀 Holon local environment is ready (Docker)!"
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

else
    echo "💻 Starting Holon services in Local Development mode..."

    # Check for uv
    if ! command -v uv &> /dev/null; then
        echo "❌ 'uv' is not installed. Please install it (curl -LsSf https://astral.sh/uv/install.sh | sh) or use --docker"
        exit 1
    fi

    # Check for pnpm (only if web is needed)
    if [ $SKIP_WEB -eq 0 ]; then
        if ! command -v pnpm &> /dev/null; then
            echo "❌ 'pnpm' is not installed. Please install it or use --docker"
            exit 1
        fi
    fi

    # Env vars
    export HOLON_STORAGE_URI="file://${PROJECT_ROOT}/holon_data"
    export VITE_API_BASE_URL="http://localhost:8000/api/v1"

    PIDS=""

    # Start Engine
    if [ $SKIP_ENGINE -eq 0 ]; then
        echo "🔌 Starting Engine (uvicorn)..."
        cd engine
        # Install deps if needed
        if [ ! -d ".venv" ]; then
            echo "   Creating engine venv..."
            uv venv
            uv pip install -e ".[dev]"
        fi
        
        # We assume dependencies are up to date or user runs update manually
        source .venv/bin/activate
        
        # Run uvicorn in background
        nohup uvicorn holon_engine.api:app --reload --port 8000 > "${PROJECT_ROOT}/engine.log" 2>&1 &
        ENGINE_PID=$!
        PIDS="$PIDS $ENGINE_PID"
        echo "   Engine running (PID: $ENGINE_PID). Logs: ${PROJECT_ROOT}/engine.log"
        cd ..
    fi

    # Start Web
    if [ $SKIP_WEB -eq 0 ]; then
        echo "📱 Starting Web Dashboard (vite)..."
        cd web
        if [ ! -d "node_modules" ]; then
            echo "   Installing web dependencies..."
            pnpm install
        fi
        
        # Run vite in background
        nohup pnpm dev --port 3000 > "${PROJECT_ROOT}/web.log" 2>&1 &
        WEB_PID=$!
        PIDS="$PIDS $WEB_PID"
        echo "   Web running (PID: $WEB_PID). Logs: ${PROJECT_ROOT}/web.log"
        cd ..
    fi

    echo ""
    echo "----------------------------------------------------------------"
    echo "🚀 Holon local dev environment is running!"
    echo "----------------------------------------------------------------"
    if [ $SKIP_WEB -eq 0 ]; then
        echo "📱 Web Dashboard:  http://localhost:3000"
    fi
    if [ $SKIP_ENGINE -eq 0 ]; then
        echo "🔌 API Swagger UI: http://localhost:8000/docs"
    fi
    echo ""
    echo "⚠️  Running in background. To stop processes:"
    echo "   kill $PIDS"
    echo "   (or run ./scripts/stop_local.sh)"
    echo "----------------------------------------------------------------"
    
    # Write PIDs to file for stop script
    echo "$PIDS" > .holon_pids
fi
