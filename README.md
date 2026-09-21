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
├── decks/                        # Quiz decks, one folder per module
│   └── <module>/*.json           #   e.g. decks/frontend/week1.json (override with COSMO_DECK_DIR)
├── artifacts/docs/               # Study materials (PDFs, markdown) for ingestion
├── chroma_db/                    # ChromaDB vector store (generated, gitignored)
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

# 2. Pull the required Ollama models (start-dev.sh checks for these and
#    prints the pull commands if they're missing):
ollama pull nomic-embed-text     # Required — embedding model
ollama pull qwen2.5-coder:7b     # Default — chat + short-answer grader

# 3. One-command startup (creates venv, installs deps, starts both servers):
chmod +x scripts/start-dev.sh
./scripts/start-dev.sh

# 4. Open http://localhost:5173
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

### Stopping and Teardown

`start-dev.sh` traps Ctrl+C and shuts down both the Flask and Vite servers. If you started them manually, press Ctrl+C in each terminal, or kill whatever is holding the ports:

```bash
lsof -ti :5173 :5174 | xargs kill
```

To reset the environment, remove the generated directories. The venv and `node_modules` are rebuilt on the next start:

```bash
rm -rf .venv frontend/node_modules      # dependencies, rebuilt on next start
```

Deleting the local data also wipes your ingested knowledge base and uploaded files:

```bash
rm -rf chroma_db uploads                # destroys the knowledge base
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

# Take a quiz (decks live under decks/<module>/)
python -m backend.cli quiz -i decks/frontend/week13.json
python -m backend.cli quiz -i decks/frontend/week13.json --sections tf,mc --limit 10
python -m backend.cli quiz -i decks/frontend/week13.json --quiz-id week13 --broad
python -m backend.cli quiz -i decks/frontend/week13.json --list

# Benchmark across model/RAG configurations
python -m backend.cli benchmark -i decks/frontend/week13.json --sections tf --limit 15
python -m backend.cli benchmark --dir decks/frontend/ --configs "qwen-7b:rag,qwen-14b:rag"

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

- **Study Mode** — Flashcard review with tag-based filtering, question type filtering (T/F, MC, SA), and three ordering modes (sequential by default, shuffle within type, shuffle all). Tags are grouped by category for easy navigation.
- **Quiz Mode** — Assessment with configurable question counts (presets or custom sliders per type), automatic T/F and MC grading, and AI-graded short answers via Ollama. Failed short-answer grading is marked "ungraded" and excluded from the score, with a Retry.
- **Debug Mode** — Reached via the "Edit deck" link under the two main modes. Review and remove questions from quiz JSON files. Mark cards for removal, undo individual removals, then confirm to save changes back to disk (the file is backed up to `<name>.json.bak` first). Useful for pruning low-quality or duplicate questions after benchmarking.

## Deck JSON schema

Decks live at `decks/<module>/<file>.json`. Each file holds a `quizzes` array;
a quiz has an `id` (unique **within its module** — the same id may exist in two
different modules), a `title`, an optional `scope`, an optional numeric `order`
(used for sorting the deck list; falls back to filename), and a `sections`
array. Each section has a `type` and a `questions` array. A minimal complete
example covering all three question types:

```json
{
  "quizzes": [
    {
      "id": "week1",
      "title": "Week 1: TypeScript Fundamentals",
      "scope": "The Basics, Everyday Types, Narrowing",
      "order": 1,
      "sections": [
        {
          "type": "true_false",
          "title": "True / False",
          "questions": [
            {
              "id": "TF-1",
              "question": "All valid JavaScript is valid TypeScript.",
              "answer": true,
              "explanation": "TypeScript is a superset of JavaScript.",
              "tags": ["typescript-basics"]
            }
          ]
        },
        {
          "type": "multiple_choice",
          "title": "Multiple Choice",
          "questions": [
            {
              "id": "MC-1",
              "question": "What is the inferred type of `value`?",
              "code": "let value = [1, 2, 3];",
              "options": ["[number, number, number]", "number[]", "any[]"],
              "answer": 1,
              "explanation": "Array literals widen to `T[]`, here `number[]`.",
              "tags": ["type-inference", "array-types"]
            }
          ]
        },
        {
          "type": "short_answer",
          "title": "Short Answer",
          "questions": [
            {
              "id": "SA-1",
              "question": "How does a `typeof` type guard narrow a union?",
              "model_answer": "In a branch where `typeof x === \"string\"`, TypeScript narrows x to string for that branch.",
              "tags": ["type-guards", "type-narrowing"]
            }
          ]
        }
      ]
    }
  ]
}
```

Field notes: `answer` is a boolean for `true_false` and a **0-based option index**
for `multiple_choice`; `code` (optional) renders as a fenced block above the
options; `short_answer` uses `model_answer` as the grading reference; `tags` is
optional everywhere and drives Study/Debug filtering.

## API Endpoints

The Flask backend exposes these routes (all prefixed with `/api`):

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Backend + Ollama status |
| `GET` | `/stats` | Knowledge base statistics |
| `GET` | `/models` | Configured chat modes that are installed in Ollama |
| `POST` | `/chat` | Streaming chat via SSE (emits `no_results` when grounded and nothing is relevant) |
| `POST` | `/ingest` | Upload and ingest a file (PDF/.md/.markdown) |
| `POST` | `/ingest/directory` | Ingest from a local directory path |
| `POST` | `/history/clear` | Clear conversation history |
| `GET` | `/modules` | List module folders under the deck directory |
| `POST` | `/modules` | Create an empty module folder |
| `GET` | `/quizzes` | List loaded quizzes |
| `GET` | `/quizzes/:module/:id` | Get full quiz data (scoped to a module) |
| `POST` | `/quizzes/ingest` | Upload a quiz JSON into a module (409 on duplicate quiz id) |
| `POST` | `/quizzes/evaluate` | AI-grade a short answer |
| `DELETE` | `/quizzes/:module/:id/questions` | Remove questions from a quiz JSON (scoped to a module) |

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
| `COSMO_DECK_DIR` | `./decks` | Quiz deck directory (module subfolders) |
| `COSMO_CHUNK_SIZE` | `1200` | Markdown chunk size (chars) |
| `COSMO_CHUNK_OVERLAP` | `200` | Chunk overlap (chars) |
| `COSMO_EMBED_MAX_TOKENS` | `500` | Max tokens per embedding |
| `COSMO_RETRIEVAL_MAX_DISTANCE` | `0.42` | Docs-only relevance cutoff (cosine distance) |

## Troubleshooting

**"Connection refused"** — Start Ollama with `ollama serve` in a separate terminal.

**"Model not found"** — Run `ollama pull <model-name>`.

**"No module named..."** — Activate the venv: `source .venv/bin/activate`.

**Slow first ingestion** — Normal. Large PDFs take 5-10 minutes. Subsequent runs are cached via file hash deduplication.

## Tech Stack

- **Backend:** Python, Flask, ChromaDB, Ollama, pymupdf4llm, tiktoken
- **Frontend:** React 19, TypeScript (strict), Vite 6, vanilla CSS
- **Markdown rendering:** react-markdown + remark-gfm with custom citation markers

# Deployment: Local Container + Cloudflare Tunnel

Serves a Vite/React/TypeScript app from a local Docker container, exposed to the internet via Cloudflare Tunnel and protected by Cloudflare Access authentication.

## Architecture

```
Browser → Cloudflare CDN → Cloudflare Tunnel → cloudflared container → nginx container (app)
                ↑
        Cloudflare Access
        (auth gate)
```

No inbound ports are opened on your machine. The `cloudflared` container maintains an outbound-only connection to Cloudflare's edge.

## Prerequisites

- Docker and Docker Compose
- A Cloudflare account with a domain (free plan works)
- Domain's DNS managed by Cloudflare

## Setup

### 1. Cloudflare Tunnel

1. Go to [Cloudflare Zero Trust](https://one.dash.cloudflare.com/) > Networks > Tunnels
2. Click **Create a tunnel**, choose **Cloudflared** as the connector
3. Name it (e.g., `study-app`)
4. Skip the connector install step (Docker handles this)
5. Add a **Public Hostname**:
   - Subdomain: your choice (e.g., `study`)
   - Domain: select your domain
   - Service Type: `HTTP`
   - URL: `app:80`
6. Save. Copy the tunnel token from the install command (the long string after `--token`)

### 2. Cloudflare Access (Authentication)

1. In Zero Trust, go to Access > Applications
2. Click **Add an application** > Self-hosted
3. Configure:
   - Application name: your choice
   - Session duration: 24 hours (or your preference)
   - Application domain: match your tunnel hostname (e.g., `study.yourdomain.com`)
4. Add a policy:
   - Policy name: e.g., `Allow me`
   - Action: **Allow**
   - Selector: **Emails** — enter your email address
5. Save

When you visit the site, Cloudflare will prompt for your email and send a one-time PIN. Only your email gets through.

### 3. Local Configuration

```bash
# Copy the example env file and add your tunnel token
cp .env.example .env
# Edit .env and replace the placeholder with your actual tunnel token
```

### 4. Build and Run

```bash
# Build and start both containers
docker compose up -d --build

# Check status
docker compose ps

# View logs
docker compose logs -f

# Rebuild after code changes
docker compose up -d --build
```

Your site should be live at `https://study.yourdomain.com` (or whatever hostname you configured).

## Day-to-Day Usage

```bash
# Start
docker compose up -d

# Stop
docker compose down

# Rebuild after changes
docker compose up -d --build

# Check tunnel connectivity
docker compose logs tunnel
```

### Full Teardown

`docker compose down` removes the containers and network but keeps your data: the `uploads` named volume and the images built by compose both persist. To remove those too:

```bash
docker compose down -v --rmi local
```

`-v` deletes the `uploads` volume; `--rmi local` deletes the built app and backend images. The bind-mounted `chroma_db/`, `decks/`, and `quizzes/` directories live on the host and are untouched — delete them by hand to reset that data.

## File Overview

| File                | Purpose                                          |
|---------------------|--------------------------------------------------|
| `Dockerfile`        | Multi-stage build: npm install + build, then nginx |
| `docker-compose.yml`| Orchestrates app and cloudflared containers       |
| `nginx.conf`        | SPA routing, static asset caching, security headers|
| `.dockerignore`     | Keeps node_modules etc. out of Docker build context|
| `.env`              | Tunnel token (not committed to git)               |

## Troubleshooting

**Site not loading**: Check `docker compose logs tunnel` — the tunnel container should show a successful connection. Verify the tunnel token is correct in `.env`.

**502 errors**: The tunnel is connected but can't reach the app. Check `docker compose logs app` and ensure nginx started correctly. Verify the tunnel's service URL is set to `http://app:80` in the Cloudflare dashboard.

**Auth not appearing**: Confirm the Access application domain exactly matches your tunnel's public hostname. Check that the Access policy is active.

**Stale content after rebuild**: Hard-refresh your browser (Ctrl+Shift+R) or clear the Cloudflare cache from the dashboard.
