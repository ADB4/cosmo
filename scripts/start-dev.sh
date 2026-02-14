#!/bin/bash
# Start both Cosmo backend (Flask) and frontend (Vite) dev servers
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "=========================================="
echo "  Cosmo — Study Companion"
echo "=========================================="
echo ""

# Check Ollama
if ! command -v ollama &> /dev/null; then
    echo "ERROR: Ollama not found. Install with: brew install ollama"
    exit 1
fi

if ! curl -s --max-time 3 http://localhost:11434/api/tags &> /dev/null; then
    echo "WARNING: Ollama doesn't seem to be running."
    echo "  Start it with: ollama serve"
    echo ""
fi

# Python venv
VENV_DIR="$SCRIPT_DIR/.venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"

echo "Installing Python dependencies..."
pip install --quiet --upgrade pip
pip install --quiet -r "$SCRIPT_DIR/requirements.txt"

# Frontend deps
if [ ! -d "$SCRIPT_DIR/frontend/node_modules" ]; then
    echo "Installing frontend dependencies..."
    cd "$SCRIPT_DIR/frontend"
    yarn install
    cd "$SCRIPT_DIR"
fi

echo ""
echo "Starting servers..."
echo "  Backend:  http://localhost:5174"
echo "  Frontend: http://localhost:5173"
echo ""
echo "Open http://localhost:5173 in your browser."
echo "Press Ctrl+C to stop both servers."
echo ""

# Start Flask backend
cd "$SCRIPT_DIR"
python -m backend.server &
FLASK_PID=$!

# Start Vite frontend
cd "$SCRIPT_DIR/frontend"
npx vite --host &
VITE_PID=$!

cleanup() {
    echo ""
    echo "Shutting down..."
    kill $FLASK_PID 2>/dev/null
    kill $VITE_PID 2>/dev/null
    wait
    echo "Done."
}
trap cleanup EXIT INT TERM

wait
