#!/bin/bash
# Install the optional Marker PDF extraction engine into Cosmo's venv and warm
# up its models. Marker is the default PDF extractor; without it, Cosmo falls
# back to pymupdf4llm automatically.
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
VENV_DIR="$ROOT_DIR/.venv"

echo "=========================================="
echo "  Cosmo — Marker extraction setup"
echo "=========================================="
echo ""
echo "This installs marker-pdf + torch + Surya models (several GB of wheels,"
echo "plus ~2-3 GB of model weights on first extraction). Cleanup uses the"
echo "already-installed qwen2.5:14b Ollama model — no extra pull needed."
echo ""

if [ ! -d "$VENV_DIR" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"

echo "Installing marker-pdf (this can take a few minutes)..."
pip install --upgrade pip
pip install -r "$ROOT_DIR/requirements-marker.txt"

echo ""
echo "Verifying Marker import..."
python -c "import marker; from marker.converters.pdf import PdfConverter; print('  Marker OK')"

echo ""
echo "Checking the cleanup model (qwen2.5:14b) is present in Ollama..."
if command -v ollama &> /dev/null && ollama list 2>/dev/null | grep -q "qwen2.5:14b"; then
    echo "  qwen2.5:14b found."
else
    echo "  WARNING: qwen2.5:14b not found. Pull it for the cleanup pass:"
    echo "    ollama pull qwen2.5:14b   (~9 GB)"
    echo "  (Or run ingest with --no-cleanup to skip the cleanup pass.)"
fi

echo ""
echo "Done. Marker is now the default PDF extractor."
echo "Try:  python -m backend.cli convert --path <some.pdf> -o converted/"
