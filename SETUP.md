# Detailed Setup Guide

Complete step-by-step setup instructions for the React/TypeScript Study Companion.

## System Requirements

- **macOS** (optimized for M1/M2 Macs, but works on Intel Macs too)
- **16GB+ RAM** (32GB recommended for larger models)
- **10GB+ free disk space** (for models and vector database)
- **Python 3.9 or later**

## Step 1: Install Ollama

Ollama provides local LLM inference with Apple Silicon optimization.

### Option A: Homebrew (Recommended)
```bash
brew install ollama
```

### Option B: Direct Download
1. Visit https://ollama.ai
2. Download the macOS installer
3. Run the installer

### Verify Installation
```bash
ollama --version
```

### Start Ollama Service
```bash
# Ollama runs as a background service
# If it's not running, start it:
ollama serve
```

## Step 2: Pull Required Models

These models will be downloaded once and cached locally.

### Essential (Required)
```bash
# Embedding model - REQUIRED for document processing
ollama pull nomic-embed-text
# Size: ~274MB, downloads in ~30 seconds on fast connection
```

### Primary Study Model (Highly Recommended)
```bash
# Best for TypeScript/React questions
ollama pull qwen2.5-coder:7b
# Size: ~4.7GB, downloads in ~5-10 minutes
```

### Optional Additional Models
```bash
# General-purpose model
ollama pull llama3.1:8b
# Size: ~4.7GB

# Deeper analysis (slower)
ollama pull qwen2.5-coder:14b
# Size: ~8.7GB

# Fastest responses
ollama pull mistral:7b
# Size: ~4.1GB
```

**Recommended minimal setup for 32GB M2 Pro:**
- `nomic-embed-text` (required)
- `qwen2.5-coder:7b` (primary)
- `llama3.1:8b` (backup)

**Total download: ~9.7GB**

### Verify Models
```bash
ollama list
```

You should see:
```
NAME                    ID              SIZE    MODIFIED
nomic-embed-text:latest a133c5474be3    274 MB  2 minutes ago
qwen2.5-coder:7b        e5d3d0d4eab0    4.7 GB  5 minutes ago
llama3.1:8b            29ea17a26adb    4.7 GB  8 minutes ago
```

## Step 3: Set Up Python Environment

### Check Python Version
```bash
python3 --version
# Should be 3.9 or higher
```

### Install/Upgrade pip
```bash
python3 -m pip install --upgrade pip
```

### Create Project Directory
```bash
cd ~/Documents  # or wherever you want the project
# Extract the provided ZIP file or clone the repo
cd react-ts-rag-study
```

### Create Virtual Environment
```bash
python3 -m venv venv
```

### Activate Virtual Environment
```bash
# On macOS/Linux
source venv/bin/activate

# Your prompt should now show (venv)
```

**Note:** You'll need to activate this environment every time you use the tool:
```bash
cd ~/Documents/react-ts-rag-study
source venv/bin/activate
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

This installs:
- `ollama` - Python client for Ollama
- `chromadb` - Vector database
- `pypdf` - PDF processing

### Verify Installation
```bash
python -c "import ollama; import chromadb; import pypdf; print('All dependencies installed')"
```

## Step 4: Prepare Your Documents

### Create Docs Folder
```bash
mkdir docs
```

### Add Your Study Materials

**Option 1: Copy Existing PDFs**
```bash
# Copy PDFs to docs folder
cp ~/Downloads/typescript-handbook.pdf docs/
cp ~/Downloads/react-documentation.pdf docs/
```

**Option 2: Clone Open Documentation**
```bash
# TypeScript Handbook
cd /tmp
git clone --depth 1 https://github.com/microsoft/TypeScript-Website.git
cp -r TypeScript-Website/packages/documentation/copy/en/handbook-v2/*.md ~/Documents/react-ts-rag-study/docs/

# React Docs
git clone --depth 1 https://github.com/reactjs/react.dev.git
cp react.dev/src/content/learn/*.md ~/Documents/react-ts-rag-study/docs/
```

**Option 3: Download Book PDFs**
- TypeScript Deep Dive: https://basarat.gitbook.io/typescript/ (export as PDF)
- Learning React (O'Reilly) - if you own it
- Any course materials you have

### Recommended Folder Structure
```
docs/
├── typescript/
│   ├── handbook.pdf
│   └── advanced-types.md
├── react/
│   ├── official-docs.pdf
│   └── hooks-guide.md
└── mui/
    └── component-api.pdf
```

## Step 5: First Run

### Make CLI Executable (Optional)
```bash
chmod +x cli.py
```

### Test the Installation
```bash
python cli.py list
```

You should see:
```
============================================================
Knowledge Base Statistics
============================================================
Total chunks: 0
Total documents: 0

Indexed Documents:
------------------------------------------------------------
============================================================
```

### Ingest Your First Document
```bash
# Test with a small markdown file first
python cli.py ingest --path docs/some-file.md
```

You should see:
```
Processing: some-file.md
Indexed 12 chunks from some-file.md
```

### Ingest All Documents
```bash
python cli.py ingest --dir docs/
```

**Note:** This can take a while for large PDFs (2-5 minutes per 100 pages).

### Verify Ingestion
```bash
python cli.py list
```

### Ask Your First Question
```bash
python cli.py ask --question "What is TypeScript?"
```

## Step 6: Daily Usage

### Starting a Study Session
```bash
# 1. Navigate to project
cd ~/Documents/react-ts-rag-study

# 2. Activate virtual environment
source venv/bin/activate

# 3. Start interactive mode
python cli.py interactive

# 4. Ask questions!
```

### Ending a Session
```bash
# In interactive mode
quit

# Deactivate virtual environment
deactivate
```

## Common Setup Issues

### Issue: "ollama: command not found"
**Solution:** Restart your terminal or add Ollama to PATH:
```bash
export PATH="/usr/local/bin:$PATH"
```

### Issue: "No module named 'ollama'"
**Solution:** Activate virtual environment:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Issue: Model download is slow
**Solution:** This is normal. Models are large:
- 7B models: ~5GB (5-10 min on fast connection)
- 14B models: ~9GB (10-15 min)
- Downloads only happen once

### Issue: "Connection refused" when querying
**Solution:** Start Ollama service:
```bash
ollama serve
# Keep this running in a separate terminal
```

### Issue: Out of memory during ingestion
**Solution:** Process files one at a time:
```bash
for file in docs/*.pdf; do
    python cli.py ingest --path "$file"
    sleep 5  # Give memory a moment to clear
done
```

### Issue: Embeddings taking too long
**Solution:** This is normal for first-time ingestion. Subsequent runs are fast because documents are cached (unless you use `--force`).

## Performance Benchmarks

On MacBook Pro M2 Pro (32GB RAM):

### Ingestion Speed
- Markdown: ~50 chunks/minute
- PDF: ~30 chunks/minute
- 200-page PDF: ~5-8 minutes total

### Query Speed (tokens/second)
- qwen2.5-coder:7b: 30-40 tok/s
- llama3.1:8b: 35-45 tok/s
- mistral:7b: 40-50 tok/s
- qwen2.5-coder:14b: 15-20 tok/s

### Memory Usage During Query
- Base (embedding model): ~500MB
- + 7B model: ~6GB total
- + 14B model: ~10GB total
- ChromaDB: ~1-2GB

## Next Steps

1. **Try the interactive mode** - Best for study sessions
2. **Experiment with different modes** - Find what works for your questions
3. **Index more documents** - The more context, the better answers
4. **Customize the prompts** - Edit `document_processor.py` to tune responses

## Getting Help

If you encounter issues:

1. Check Ollama is running: `ollama list`
2. Verify models are installed: `ollama list`
3. Check Python environment: `which python` (should show venv)
4. Review error messages carefully
5. Check the README.md troubleshooting section

## Updating

### Update Models
```bash
ollama pull nomic-embed-text
ollama pull qwen2.5-coder:7b
```

### Update Python Dependencies
```bash
source venv/bin/activate
pip install --upgrade -r requirements.txt
```

### Re-index Documents (if needed)
```bash
python cli.py ingest --dir docs/ --force
```

---

You're all set. Start with `python cli.py interactive` to begin using the system.
