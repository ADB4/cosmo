# Cosmo — Study Companion

A local-first RAG system for querying your React/TypeScript/MUI documentation using Ollama. Includes a CLI for terminal study sessions, a web GUI with streaming chat, and Apollo -- a quiz/study/debug tool with AI-graded short answers, tag-based filtering, and deck management.

## Architecture

```
cosmo/
├── backend/                      # Python — Flask API + RAG engine
│   ├── config.py                 # Centralized configuration (models, paths, options)
│   ├── document_processor.py     # Core RAG: ingest, embed, query, stream, PDF→markdown
│   ├── markdown_chunking.py      # Heading-hierarchy-aware section parsing + chunking
│   ├── quiz_processor.py         # Quiz parsing, grading, and benchmarking
│   ├── retrieval_bench.py        # RAG retrieval quality benchmarking
│   ├── server.py                 # Flask API (SSE streaming, upload, quizzes, evaluation)
│   └── cli.py                    # Command-line interface
├── frontend/                     # React 19 + TypeScript + Vite
│   ├── src/
│   │   ├── App.tsx               # Root layout (tab bar, model selector)
│   │   ├── pages/
│   │   │   ├── chat/             # Chat page (ChatPanel, MessageBubble)
│   │   │   └── apollo/           # Apollo (StudyMode, QuizMode, DebugMode)
│   │   ├── components/           # Shared components (renderMarkdown)
│   │   ├── lib/                  # Shared logic (api, types, normalizeQuiz)
│   │   └── styles/               # Vanilla CSS
│   ├── vite.config.ts            # Dev server + API proxy
│   ├── tsconfig.json             # Strict mode
│   └── package.json              # React 19, Vite 6, yarn
├── scripts/
│   ├── start-dev.sh              # One-command startup for both servers
│   └── download-rtl.sh           # Download React Testing Library docs for ingestion
├── quizzes/                      # Quiz JSON files (week1.json, week2.json, etc.)
├── docs/                         # Your study materials (PDFs, markdown)
├── requirements.txt              # Python dependencies
└── .gitignore
```

## Prerequisites

- **Ollama** running locally with models pulled
- **Python 3.9+**
- **Node.js 18+** and **yarn**

## Quick Start

```bash
# 1. Clone and enter the project
git clone https://github.com/ADB4/cosmo.git
cd cosmo

# 2. One-command startup (creates venv, installs deps, starts both servers):
chmod +x scripts/start-dev.sh
./scripts/start-dev.sh

# 3. Open http://localhost:5173
```

### Manual Setup

```bash
# Backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Frontend
cd frontend
yarn install
cd ..

# Pull required Ollama models
ollama pull nomic-embed-text      # Required — embedding model
ollama pull qwen2.5-coder:7b     # Recommended — best all-round performer
ollama pull phi4:14b              # Optional — deep reasoning mode

# Start servers (separate terminals)
python -m backend.server          # http://localhost:5174
cd frontend && yarn dev           # http://localhost:5173
```

## CLI Usage

All CLI commands run from the project root with the venv activated:

```bash
# Ingest documents
python -m backend.cli ingest --dir docs/
python -m backend.cli ingest --path docs/handbook.pdf --force
python -m backend.cli ingest --path docs/effective-typescript.pdf --top-level-only

# Ask a question
python -m backend.cli ask -q "How do I type a useState hook?"
python -m backend.cli ask -q "Explain generics" --mode phi4-14b

# Convert PDF to markdown (no Ollama required)
python -m backend.cli convert --path docs/effective-typescript.pdf -o converted/
python -m backend.cli convert --path docs/ -o converted/

# Take a quiz
python -m backend.cli quiz -i quizzes/week13.json
python -m backend.cli quiz -i quizzes/week13.json --sections tf,mc --limit 10
python -m backend.cli quiz -i quizzes/week13.json --quiz-id week13 --broad
python -m backend.cli quiz -i quizzes/week13.json --list

# Benchmark across model/RAG configurations
python -m backend.cli benchmark -i quizzes/week13.json --sections tf --limit 15
python -m backend.cli benchmark --dir quizzes/ --configs "qwen-7b:rag,qwen-14b:rag"

# Interactive study session
python -m backend.cli interactive

# List indexed documents
python -m backend.cli list
```

### Interactive Mode Commands

While in interactive mode, type your question directly, or use these commands: `mode qwen-7b|qwen-14b|llama3-8b|phi4-14b` to switch models, `clear` to reset history, `stats` to check the knowledge base, `quit` to exit.

## Web GUI

The web interface provides two tabs:

**Chat** — Streaming RAG answers with citation markers, model switching via dropdown, grounded/broad toggle, and conversation history.

**Apollo** — Three modes for working with quiz JSON files:

- **Study Mode** — Flashcard review with tag-based filtering, question type filtering (T/F, MC, SA), and three ordering modes (sequential, shuffle within type, shuffle all). Tags are grouped by category for easy navigation.
- **Quiz Mode** — Timed assessment with configurable question counts (presets or custom sliders per type), automatic T/F and MC grading, and AI-graded short answers via Ollama.
- **Debug Mode** — Review and remove questions from quiz JSON files. Mark cards for removal, undo individual removals, then save changes back to disk. Useful for pruning low-quality or duplicate questions after benchmarking.

## API Endpoints

The Flask backend exposes these routes (all prefixed with `/api`):

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Backend + Ollama status |
| `GET` | `/stats` | Knowledge base statistics |
| `POST` | `/chat` | Streaming chat via SSE |
| `POST` | `/ingest` | Upload and ingest a file |
| `POST` | `/ingest/directory` | Ingest from a local directory path |
| `POST` | `/history/clear` | Clear conversation history |
| `GET` | `/quizzes` | List loaded quizzes |
| `GET` | `/quizzes/:id` | Get full quiz data |
| `POST` | `/quizzes/ingest` | Upload a quiz JSON |
| `POST` | `/quizzes/evaluate` | AI-grade a short answer |
| `DELETE` | `/quizzes/:id/questions` | Remove questions from a quiz JSON |

## Model Modes

| Mode | Model | Use case |
|------|-------|----------|
| `qwen-7b` | qwen2.5-coder:7b | Default — fast and accurate, best all-round |
| `qwen-14b` | qwen2.5-coder:14b | Complex explanations, slower |
| `llama3-8b` | llama3.1:8b | General-purpose, non-code questions |
| `phi4-14b` | phi4:14b | Deep reasoning, best response quality |

Additional models available for CLI benchmarking: `gemma2-9b`, `llama3-3b`, `mistral-7b`. All models are configured in `backend/config.py` with per-model context window sizes and inference options tuned for M2 Pro 32GB.

## Sharing the ChromaDB

The web GUI and CLI share the same ChromaDB at `./chroma_db`. Override with `COSMO_DB_PATH`:

```bash
COSMO_DB_PATH=/other/path python -m backend.server
```

## Configuration

All backend settings live in `backend/config.py` and can be overridden via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `COSMO_DB_PATH` | `./chroma_db` | ChromaDB storage path |
| `COSMO_PORT` | `5174` | Flask server port |
| `COSMO_UPLOAD_DIR` | `./uploads` | File upload directory |
| `COSMO_QUIZ_DIR` | `./quizzes` | Quiz JSON directory |
| `COSMO_CHUNK_SIZE` | `1200` | Markdown chunk size (chars) |
| `COSMO_CHUNK_OVERLAP` | `200` | Chunk overlap (chars) |
| `COSMO_EMBED_MAX_TOKENS` | `500` | Max tokens per embedding |

## Troubleshooting

**"Connection refused"** — Start Ollama with `ollama serve` in a separate terminal.

**"Model not found"** — Run `ollama pull <model-name>`.

**"No module named..."** — Activate the venv: `source .venv/bin/activate`.

**Slow first ingestion** — Normal. Large PDFs take 5-10 minutes. Subsequent runs are cached via file hash deduplication.

## Tech Stack

- **Backend:** Python, Flask, ChromaDB, Ollama, pymupdf4llm, tiktoken
- **Frontend:** React 19, TypeScript (strict), Vite 6, vanilla CSS
- **Markdown rendering:** react-markdown + remark-gfm with custom citation markers
- **Styling:** CSS custom properties, monospace terminal aesthetic