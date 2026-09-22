#!/bin/bash
# Start both Cosmo backend (Flask) and frontend (Vite) dev servers
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

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

# Check that the models Cosmo needs are pulled:
#   - the default chat model (qwen3-coder:30b),
#   - the short-answer grader (qwen3:4b, or the gemma4:e4b fallback),
#   - the active embedding model (qwen3-embedding:0.6b unless COSMO_EMBED_MODEL is set).
# Missing models only produce a warning + the pull commands; the app still starts.
EMBED_MODEL="${COSMO_EMBED_MODEL:-qwen3-embedding:0.6b}"
DEFAULT_CHAT="qwen3-coder:30b"

# Approximate download size (GB) for a model tag — bash 3.2 compatible (macOS
# ships no associative arrays).
model_size() {
    case "$1" in
        "qwen3-coder:30b") echo 19 ;;
        "qwen3.6:27b") echo 17 ;;
        "gpt-oss:20b") echo 13 ;;
        "gemma4:12b") echo 8 ;;
        "qwen3:4b") echo 2.6 ;;
        "gemma4:e4b") echo 3 ;;
        "nomic-embed-text") echo 0.3 ;;
        "qwen3-embedding:0.6b") echo 0.6 ;;
        "embeddinggemma") echo 0.6 ;;
        *) echo "?" ;;
    esac
}

if command -v ollama &> /dev/null && ollama list &> /dev/null; then
    INSTALLED="$(ollama list 2>/dev/null)"

    # Default chat model — required for chat + quiz.
    MISSING=()
    if ! echo "$INSTALLED" | grep -q "$DEFAULT_CHAT"; then
        MISSING+=("$DEFAULT_CHAT")
    fi

    # Grader — satisfied if qwen3:4b OR the gemma4:e4b fallback is present.
    if ! echo "$INSTALLED" | grep -q "qwen3:4b" && ! echo "$INSTALLED" | grep -q "gemma4:e4b"; then
        MISSING+=("qwen3:4b")
    fi

    # Active embedding model.
    if ! echo "$INSTALLED" | grep -q "$EMBED_MODEL"; then
        MISSING+=("$EMBED_MODEL")
    fi

    if [ ${#MISSING[@]} -gt 0 ]; then
        echo "WARNING: required Ollama model(s) not found. Pull them with:"
        TOTAL=0
        for model in "${MISSING[@]}"; do
            SIZE="$(model_size "$model")"
            echo "  ollama pull $model    (~${SIZE} GB)"
            if [ "$SIZE" != "?" ]; then
                TOTAL="$(awk "BEGIN{print $TOTAL + $SIZE}")"
            fi
        done
        echo "  Estimated total download: ~${TOTAL} GB"
        echo ""
    fi
fi

# Ollama server tuning (set these in the environment where `ollama serve`
# runs — NOT here; the Flask process cannot change the running server):
#   OLLAMA_NUM_PARALLEL=4   grade several short answers concurrently instead
#                           of serialising them per model.
#   OLLAMA_KEEP_ALIVE=30m   keep the chat model + grader resident between quiz
#                           and chat use, avoiding a reload on every switch.
echo "TIP: for faster grading, start Ollama with:"
echo "  OLLAMA_NUM_PARALLEL=4 OLLAMA_KEEP_ALIVE=30m ollama serve"
echo ""

# Python venv
VENV_DIR="$ROOT_DIR/.venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"

echo "Installing Python dependencies..."
pip install --quiet --upgrade pip
pip install --quiet -r "$ROOT_DIR/requirements.txt"

# Optional Marker PDF engine: only a hint. Without it (or without llama.cpp),
# PDF ingestion still works via the pymupdf4llm fallback.
if ! python -c "import marker" 2>/dev/null; then
    echo "NOTE: Marker (layout-aware PDF engine) not installed — PDFs will use"
    echo "  the pymupdf4llm fallback. To enable Marker: scripts/setup-extraction.sh"
elif ! command -v llama-server &>/dev/null; then
    echo "NOTE: Marker is installed but 'llama-server' is missing — Marker will"
    echo "  fall back to pymupdf4llm. Install it with: brew install llama.cpp"
fi

# Frontend deps
if [ ! -d "$ROOT_DIR/frontend/node_modules" ]; then
    echo "Installing frontend dependencies..."
    cd "$ROOT_DIR/frontend"
    yarn install
    cd "$ROOT_DIR"
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
cd "$ROOT_DIR"
python -m backend.server &
FLASK_PID=$!

# Start Vite frontend
cd "$ROOT_DIR/frontend"
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
