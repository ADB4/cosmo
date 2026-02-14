# Cosmo — Study Companion

A local-first RAG system for querying your React/TypeScript/MUI documentation using Ollama. Includes a CLI for terminal study sessions, a web GUI with streaming chat, and Apollo -- a quiz/study mode with AI-graded short answers.

## Architecture

```
cosmo/
├── backend/                  # Python — Flask API + RAG engine
│   ├── config.py             # Centralized configuration
│   ├── document_processor.py # Core RAG: ingest, embed, query, stream
│   ├── quiz_processor.py     # Quiz parsing and grading (CLI)
│   ├── server.py             # Flask API (SSE streaming, upload, quizzes)
│   └── cli.py                # Command-line interface
├── frontend/                 # React 19 + TypeScript + Vite
│   ├── src/
│   │   ├── App.tsx           # Root layout (tab bar, model selector)
│   │   ├── pages/
│   │   │   ├── chat/         # Chat page (ChatPanel, MessageBubble)
│   │   │   └── apollo/       # Quiz page (Apollo, StudyMode, QuizMode)
│   │   ├── components/       # Shared components (renderMarkdown)
│   │   ├── lib/              # Shared logic (api, types, normalizeQuiz)
│   │   └── styles/           # Vanilla CSS
│   ├── vite.config.ts        # Dev server + API proxy
│   ├── tsconfig.json         # Strict mode
│   └── package.json          # React 19, Vite 6, yarn
├── scripts/
│   └── start-dev.sh          # One-command startup for both servers
├── requirements.txt          # Python dependencies
└── docs/                     # Your study materials (PDFs, markdown)
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
ollama pull nomic-embed-text    # Required — embedding model
ollama pull qwen2.5-coder:7b   # Recommended — fast code model

# Start servers (separate terminals)
python -m backend.server        # http://localhost:5174
cd frontend && yarn dev         # http://localhost:5173
```

## CLI Usage

All CLI commands run from the project root with the venv activated:

```bash
# Ingest documents
python -m backend.cli ingest --dir docs/
python -m backend.cli ingest --path docs/handbook.pdf --force

# Ask a question
python -m backend.cli ask -q "How do I type a useState hook?" --mode deep

# Interactive study session
python -m backend.cli interactive

# Take a quiz
python -m backend.cli quiz --input quizzes/w1.md --output results/w1-results.md

# List indexed documents
python -m backend.cli list
```

### Interactive Mode Commands

While in interactive mode, type your question directly, or use these commands: `mode quick|deep|general|fast` to switch models, `clear` to reset history, `stats` to check the knowledge base, `quit` to exit.

## Web GUI

The web interface provides two tabs:

**Chat** — streaming RAG answers with citation markers, model switching, and conversation history.

**Apollo** — quiz and study mode. Upload quiz JSON files, then choose between flashcard study mode or timed quiz mode with configurable question counts and AI-graded short answers.

## API Endpoints

The Flask backend exposes these routes (all prefixed with `/api`):

- `GET /health` — backend + Ollama status
- `GET /stats` — knowledge base statistics
- `POST /chat` — streaming chat via SSE
- `POST /ingest` — upload and ingest a file
- `POST /ingest/directory` — ingest from a local path
- `POST /history/clear` — clear conversation history
- `GET /quizzes` — list loaded quizzes
- `GET /quizzes/:id` — get full quiz data
- `POST /quizzes/ingest` — upload a quiz JSON
- `POST /quizzes/evaluate` — AI-grade a short answer

## Model Modes

| Mode | Model | Use case |
|------|-------|----------|
| quick | qwen2.5-coder:7b | Default, fast and accurate for code |
| deep | qwen2.5-coder:14b | Complex explanations, slower |
| general | llama3.1:8b | Non-code questions |
| fast | mistral:7b | Fastest responses |

## Sharing the ChromaDB

The web GUI and CLI share the same ChromaDB at `./chroma_db`. Override with `COSMO_DB_PATH`:

```bash
COSMO_DB_PATH=/other/path python -m backend.server
```

## Configuration

All backend settings live in `backend/config.py` and can be overridden via environment variables: `COSMO_DB_PATH`, `COSMO_PORT`, `COSMO_UPLOAD_DIR`, `COSMO_QUIZ_DIR`, `COSMO_CHUNK_SIZE`, `COSMO_CHUNK_OVERLAP`.

## Troubleshooting

**"Connection refused"** — start Ollama with `ollama serve` in a separate terminal.

**"Model not found"** — run `ollama pull <model-name>`.

**"No module named..."** — activate the venv: `source .venv/bin/activate`.

**Slow first ingestion** — normal. Large PDFs take 5-10 minutes. Subsequent runs are cached.

## Tech Stack

- **Backend:** Python, Flask, ChromaDB, Ollama, pypdf
- **Frontend:** React 19, TypeScript (strict), Vite 6, vanilla CSS
- **Styling:** CSS custom properties, monospace terminal aesthetic
- **No external markdown library** — lightweight inline renderer for code blocks, inline code, citations
