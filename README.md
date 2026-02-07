# React/TypeScript Study Companion

A RAG (Retrieval-Augmented Generation) powered study companion that lets you query your React and TypeScript documentation using local LLMs via Ollama.

## Features

- **Large Document Support**: Efficiently processes PDFs with hundreds of pages
- **Smart Chunking**: Maintains document structure for better context
- **Persistent Storage**: ChromaDB-backed vector store with deduplication
- **Fast Queries**: Optimized for M1/M2 Macs with Metal acceleration
- **Source Citations**: Every answer includes references to source documents
- **Multiple Models**: Switch between fast/deep modes based on your needs

## Prerequisites

1. **Ollama** installed on your Mac
   ```bash
   brew install ollama
   ```

2. **Python 3.9+**
   ```bash
   python3 --version
   ```

## Installation

1. **Clone or extract this project**
   ```bash
   cd react-ts-rag-study
   ```

2. **Create a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On macOS/Linux
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Pull recommended Ollama models**
   ```bash
   # Essential models
   ollama pull nomic-embed-text      # For embeddings (required)
   ollama pull qwen2.5-coder:7b      # Primary study model (recommended)
   
   # Optional additional models
   ollama pull llama3.1:8b           # Alternative for general questions
   ollama pull qwen2.5-coder:14b     # For deeper analysis (slower)
   ollama pull mistral:7b            # Fastest responses
   ```

## Quick Start

### 1. Organize Your Documents

Create a `docs` folder and add your React/TypeScript materials:

```bash
mkdir docs
# Add your PDFs and markdown files to docs/
```

Example structure:
```
docs/
├── typescript-handbook.pdf
├── react-documentation.pdf
├── advanced-typescript.md
└── react-patterns.md
```

### 2. Ingest Documents

**Single file:**
```bash
python cli.py ingest --path docs/typescript-handbook.pdf
```

**Entire directory:**
```bash
python cli.py ingest --dir docs/
```

**Re-index everything:**
```bash
python cli.py ingest --dir docs/ --force
```

### 3. Ask Questions

**One-off question:**
```bash
python cli.py ask --question "How do I type a generic React component?"
```

**With different model modes:**
```bash
# Quick responses (default)
python cli.py ask -q "What's the difference between type and interface?"

# Deep analysis (slower, better quality)
python cli.py ask -q "Explain discriminated unions" --mode deep

# Fast mode
python cli.py ask -q "Quick overview of useCallback" --mode fast
```

### 4. Interactive Mode (Recommended for Study Sessions)

```bash
python cli.py interactive
```

In interactive mode:
- Ask questions naturally
- Type `mode deep` to switch to deeper analysis
- Type `stats` to see indexed documents
- Type `quit` to exit

## Model Modes

Optimized for MacBook Pro M2 with 32GB RAM:

| Mode | Model | Speed | Best For |
|------|-------|-------|----------|
| `quick` | qwen2.5-coder:7b | ~35 tok/s | Default - code & TypeScript questions |
| `deep` | qwen2.5-coder:14b | ~18 tok/s | Complex explanations, refactoring advice |
| `general` | llama3.1:8b | ~40 tok/s | Conceptual questions, non-code topics |
| `fast` | mistral:7b | ~45 tok/s | Quick lookups, simple questions |

## Usage Examples

### Study Session Workflow

```bash
# 1. Start interactive mode
python cli.py interactive

# 2. Ask questions as you study
[quick] Question: What are the rules of hooks?

[quick] Question: mode deep

[deep] Question: Show me how to properly type a compound component pattern

[deep] Question: stats

[deep] Question: quit
```

### Bulk Ingestion

```bash
# Download the TypeScript handbook
git clone https://github.com/microsoft/TypeScript-Website.git
python cli.py ingest --dir TypeScript-Website/packages/documentation/copy/en/handbook-v2/

# Add React documentation
git clone https://github.com/reactjs/react.dev.git
python cli.py ingest --dir react.dev/src/content/
```

### Check What's Indexed

```bash
python cli.py list
```

Output:
```
============================================================
Knowledge Base Statistics
============================================================
Total chunks: 1,234
Total documents: 15

Indexed Documents:
------------------------------------------------------------
  typescript-handbook.pdf
    Type: pdf, Chunks: 456
  react-hooks.md
    Type: markdown, Chunks: 89
...
```

## Project Structure

```
react-ts-rag-study/
├── cli.py                   # Command-line interface
├── document_processor.py    # Core RAG logic
├── requirements.txt         # Python dependencies
├── README.md               # This file
├── SETUP.md                # Detailed setup guide
├── chroma_db/              # Vector database (created on first run)
└── docs/                   # Your study materials (you create this)
```

## Performance Tips

### For M2 Pro (32GB):
- Use `quick` mode for most questions (~35 tok/s)
- Switch to `deep` mode only when you need detailed explanations
- Keep 2-3 models pulled for switching between modes
- The embedding model (`nomic-embed-text`) stays in memory

### Memory Usage:
- Embedding model: ~500MB
- Quick mode (7B): ~6GB
- Deep mode (14B): ~10GB
- ChromaDB + overhead: ~2GB
- **Comfortable usage with browser/IDE open**

## Troubleshooting

### "Model not found" error
```bash
ollama pull <model-name>
```

### Slow embeddings during ingestion
This is normal for large documents. Embeddings are generated once and cached.

### Out of memory
Use smaller models or close other applications:
```bash
# Switch to lighter model
python cli.py ask -q "your question" --mode fast
```

### No results for questions
1. Check documents are indexed: `python cli.py list`
2. Re-ingest with force: `python cli.py ingest --dir docs/ --force`
3. Try rephrasing your question

## Advanced Usage

### Custom Database Location
```bash
python cli.py --db-path /path/to/custom/db ingest --dir docs/
python cli.py --db-path /path/to/custom/db ask -q "your question"
```

### More Context Chunks
```bash
python cli.py ask -q "your question" --results 8
```

### Python API Usage

```python
from document_processor import DocumentProcessor

processor = DocumentProcessor()

# Ingest
processor.ingest_pdf("docs/handbook.pdf")

# Query
answer = processor.ask(
    "How do I use generics with React hooks?",
    mode='quick',
    n_results=4
)
print(answer)

# Get stats
stats = processor.get_stats()
print(f"Indexed {stats['total_chunks']} chunks")
```

## What to Study With

Recommended free documentation sources:

1. **TypeScript Handbook** (official)
   - https://github.com/microsoft/TypeScript-Website

2. **React Documentation** (official)
   - https://github.com/reactjs/react.dev

3. **TypeScript Deep Dive** (free book)
   - https://basarat.gitbook.io/typescript/

4. **MUI Documentation**
   - Clone from MUI repo or save as PDFs

5. **Your course materials**
   - PDFs from courses, bootcamps, or books you own

## License

MIT License - feel free to modify and use for your studies.

## Contributing

This is a study tool - fork it and customize to your learning style.

---

For questions or issues, refer to the troubleshooting section above.
