# Cosmo Web — Study Companion GUI

A web interface for querying your React/TypeScript/MUI documentation using local LLMs via Ollama. This wraps the existing `DocumentProcessor` RAG engine with a Flask API backend and a React/TypeScript/Vite frontend.

## Architecture

```
cosmo-web/
├── server.py                # Flask API (SSE streaming, file upload, stats)
├── document_processor.py    # Core RAG engine (unchanged from CLI version)
├── requirements.txt         # Python deps (flask, flask-cors, ollama, chromadb, pypdf)
├── start-dev.sh             # Launches both servers with one command
├── client/                  # React + TypeScript + Vite frontend
│   ├── src/
│   │   ├── main.tsx         # Entry point
│   │   ├── App.tsx          # Root layout
│   │   ├── ChatPanel.tsx    # Chat messages + input + SSE streaming
│   │   ├── MessageBubble.tsx # Individual message rendering (code blocks, citations)
│   │   ├── Sidebar.tsx      # Mode selector, upload, stats
│   │   ├── api.ts           # API client (fetch + SSE)
│   │   ├── types.ts         # Shared TypeScript types
│   │   └── index.css        # All styles (vanilla CSS, no framework)
│   ├── vite.config.ts       # Vite config with proxy to Flask
│   ├── tsconfig.json        # Strict TypeScript config
│   └── package.json         # yarn / React 19 / Vite 6
└── uploads/                 # Server-side upload directory (auto-created)
```

## Prerequisites

Same as the CLI version:
- **Ollama** running with models pulled (`nomic-embed-text` + at least one chat model)
- **Python 3.9+**
- **Node.js 18+** and **yarn**

## Quick Start

```bash
cd cosmo-web

# One-command startup:
./start-dev.sh

# Or manually:

# Terminal 1 — Backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python server.py

# Terminal 2 — Frontend
cd client
yarn install
yarn dev
```

Then open **http://localhost:5173** in your browser.

## Features

- **Streaming responses** — tokens appear in real-time via Server-Sent Events
- **Model switching** — Quick / Deep / General / Fast modes from the sidebar
- **File upload** — drag PDFs or markdown files into the sidebar to ingest
- **Knowledge base stats** — see what's indexed at a glance
- **Conversation history** — the backend maintains rolling context (last 10 exchanges)
- **Code block rendering** — fenced code blocks with language hints
- **Citation highlighting** — `[1]`, `[2]` markers are visually distinct
- **Mobile responsive** — hamburger menu for sidebar on small screens
- **Keyboard shortcuts** — Enter to send, Shift+Enter for newlines

## API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/api/health` | GET | Backend + Ollama status |
| `/api/stats` | GET | Knowledge base statistics |
| `/api/chat` | POST | Streaming chat (SSE) |
| `/api/ingest` | POST | Upload + ingest a file |
| `/api/ingest/directory` | POST | Ingest files from a local path |
| `/api/history/clear` | POST | Clear conversation history |

## Tech Decisions

- **Vanilla CSS** — no Tailwind, no CSS-in-JS. Single file, CSS custom properties for theming.
- **No markdown library** — lightweight inline renderer handles code blocks, inline code, and citations. Keeps the bundle small (~65KB gzipped).
- **Flask + SSE** — simple streaming without WebSocket complexity. The Vite dev server proxies `/api` to Flask.
- **React 19** — latest stable, no `React.FC`, function components throughout.
- **TypeScript strict mode** — as the syllabus prescribes.

## Sharing the ChromaDB

The web GUI and CLI share the same ChromaDB. By default both use `./chroma_db`. If your CLI project is elsewhere, either:

1. Symlink: `ln -s /path/to/your/chroma_db ./chroma_db`
2. Set the env var: `COSMO_DB_PATH=/path/to/your/chroma_db python server.py`
3. Copy the `chroma_db/` folder into this directory

## Production Build

```bash
cd client
yarn build
# Output in client/dist/ — serve with any static file server
# Point /api routes to the Flask backend
```
