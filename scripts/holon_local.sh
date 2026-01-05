#!/bin/bash
set -e

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

export HOLON_HOST="http://localhost:8000"
VENV_DIR="$PROJECT_ROOT/.venv"

# Check for uv
if ! command -v uv &> /dev/null; then
    echo "uv not found. Installing..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    # Add to path for this session
    export PATH="$HOME/.cargo/bin:$PATH"
fi

# Create venv if not exists
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    uv venv "$VENV_DIR"
fi

# Activate venv
source "$VENV_DIR/bin/activate"

# Install CLI if not installed
if ! python -c "import holon_cli" &> /dev/null; then
    echo "Installing CLI dependencies..."
    uv pip install -e "$PROJECT_ROOT/cli"
fi

python -m holon_cli "$@"
