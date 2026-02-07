#!/bin/bash
# Quick start script for React/TypeScript Study Companion

set -e  # Exit on error

echo "=========================================="
echo "React/TypeScript Study Companion Setup"
echo "=========================================="
echo ""

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "ERROR: Ollama not found. Please install it first:"
    echo "   brew install ollama"
    echo "   or visit https://ollama.ai"
    exit 1
fi
echo "Ollama is installed"

# Check if Ollama is running (with timeout)
if ! curl -s --max-time 5 http://localhost:11434/api/tags &> /dev/null; then
    echo ""
    echo "WARNING: Ollama is not running."
    echo "Starting Ollama in the background..."
    ollama serve &>/dev/null &
    sleep 2
    if ! curl -s --max-time 5 http://localhost:11434/api/tags &> /dev/null; then
        echo "ERROR: Could not start Ollama. Start it manually:"
        echo "   ollama serve"
        exit 1
    fi
fi
echo "Ollama is running"

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 not found. Install it with:"
    echo "   brew install python3"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
PYTHON_MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)
echo "Python version: $PYTHON_VERSION"

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 9 ]); then
    echo "ERROR: Python 3.9+ required. Found $PYTHON_VERSION"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo ""
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate
echo "Virtual environment activated"

# Install/upgrade dependencies
echo ""
echo "Installing dependencies..."
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt
echo "Dependencies installed"

# Verify Python imports work
echo ""
echo "Verifying Python packages..."
if ! python -c "import ollama; import chromadb; import pypdf" 2>/dev/null; then
    echo "ERROR: Package import failed. Try:"
    echo "   pip install -r requirements.txt"
    exit 1
fi
echo "All packages verified"

# Check if models are installed
echo ""
echo "Checking Ollama models..."

MODELS_NEEDED=("nomic-embed-text" "qwen2.5-coder:7b")
MISSING_MODELS=()

for model in "${MODELS_NEEDED[@]}"; do
    if ! ollama list | grep -q "$model"; then
        MISSING_MODELS+=("$model")
    else
        echo "  $model is installed"
    fi
done

if [ ${#MISSING_MODELS[@]} -gt 0 ]; then
    echo ""
    echo "Missing required models:"
    for model in "${MISSING_MODELS[@]}"; do
        echo "   - $model"
    done
    echo ""
    read -p "Install missing models now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        for model in "${MISSING_MODELS[@]}"; do
            echo "Installing $model (this may take a few minutes)..."
            ollama pull "$model"
        done
    else
        echo "Skipping model installation. You'll need to install them manually."
    fi
fi

# Create docs directory if it doesn't exist
if [ ! -d "docs" ]; then
    mkdir docs
    echo ""
    echo "Created docs/ directory - add your study materials here"
fi

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Add your PDFs and markdown files to the docs/ folder"
echo "2. Ingest them: python cli.py ingest --dir docs/"
echo "3. Start studying: python cli.py interactive"
echo ""
echo "Quick reference:"
echo "  python cli.py ingest --path <file>     # Ingest single file"
echo "  python cli.py ingest --dir docs/       # Ingest all files"
echo "  python cli.py ask -q \"your question\"   # Ask a question"
echo "  python cli.py interactive              # Interactive mode"
echo "  python cli.py list                     # Show indexed docs"
echo ""
echo "Remember to activate the virtual environment each session:"
echo "  source venv/bin/activate"
echo ""
