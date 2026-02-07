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

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/tags &> /dev/null; then
    echo "ERROR: Ollama is not running. Start it with:"
    echo "   ollama serve"
    exit 1
fi
echo "Ollama is running"

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $PYTHON_VERSION"

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

# Check if models are installed
echo ""
echo "Checking Ollama models..."

MODELS_NEEDED=("nomic-embed-text" "qwen2.5-coder:7b")
MISSING_MODELS=()

for model in "${MODELS_NEEDED[@]}"; do
    if ! ollama list | grep -q "$model"; then
        MISSING_MODELS+=("$model")
    else
        echo "$model is installed"
    fi
done

if [ ${#MISSING_MODELS[@]} -gt 0 ]; then
    echo ""
    echo "WARNING: Missing models detected. Install them with:"
    for model in "${MISSING_MODELS[@]}"; do
        echo "   ollama pull $model"
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
    echo "Created docs/ directory"
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
echo "Remember to activate the virtual environment:"
echo "  source venv/bin/activate"
echo ""
