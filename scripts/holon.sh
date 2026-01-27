#!/bin/bash
# Convenient wrapper for running holon CLI during development
# Usage: ./scripts/holon.sh [command] [args...]

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Change to project root
cd "$PROJECT_ROOT"

# Activate venv if it exists, otherwise look for uv
if [ -f /tmp/holon-env/bin/activate ]; then
    source /tmp/holon-env/bin/activate
    python -m holon.cli "$@"
elif command -v uv &> /dev/null; then
    uv run -m holon.cli "$@"
else
    echo "Error: Neither venv at /tmp/holon-env nor uv command found"
    echo "Please install uv or create a venv at /tmp/holon-env"
    exit 1
fi
