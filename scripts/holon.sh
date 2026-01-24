#!/bin/bash
# Convenient wrapper for running holon CLI during development
# Usage: ./scripts/holon.sh [command] [args...]

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Change to project root
cd "$PROJECT_ROOT"

# Run holon using uv with the local source
uv run -m holon.cli "$@"
