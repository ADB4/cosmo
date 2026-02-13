#!/bin/bash
# Start both Cosmo backend (Flask) and frontend (Vite) dev servers

set -e

echo "=========================================="
echo "  Cosmo Web — Study Companion"
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

# Activate Python venv if it exists, otherwise create one
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

if [ ! -d "$SCRIPT_DIR/venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv "$SCRIPT_DIR/env"
fi

source "$SCRIPT_DIR/env/bin/activate"

echo "Installing Python dependencies..."
pip install --quiet --upgrade pip
pip install --quiet -r "$SCRIPT_DIR/requirements.txt"

# Install frontend dependencies if needed
if [ ! -d "$SCRIPT_DIR/client/node_modules" ]; then
    echo "Installing frontend dependencies..."
    cd "$SCRIPT_DIR/client"
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

# Start Flask in background
cd "$SCRIPT_DIR"
python server.py &
FLASK_PID=$!

# Start Vite dev server
cd "$SCRIPT_DIR/client"
npx vite --host &
VITE_PID=$!

# Cleanup on exit
cleanup() {
    echo ""
    echo "Shutting down..."
    kill $FLASK_PID 2>/dev/null
    kill $VITE_PID 2>/dev/null
    wait
    echo "Done."
}
trap cleanup EXIT INT TERM

# Wait for either to exit
wait
