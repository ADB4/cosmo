"""
Cosmo backend configuration.

Centralizes paths, ports, model settings, and other constants.
Override via environment variables where noted.
"""

import os
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

# Root of the project (one level up from backend/)
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# ChromaDB persistent storage
DB_PATH = os.environ.get("COSMO_DB_PATH", str(PROJECT_ROOT / "chroma_db"))

# File upload directory (created at startup)
UPLOAD_DIR = Path(os.environ.get("COSMO_UPLOAD_DIR", str(PROJECT_ROOT / "uploads")))

# Quiz JSON directory (created at startup)
QUIZ_DIR = Path(os.environ.get("COSMO_QUIZ_DIR", str(PROJECT_ROOT / "quizzes")))

# User study documents
DOCS_DIR = PROJECT_ROOT / "docs"

# ---------------------------------------------------------------------------
# Server
# ---------------------------------------------------------------------------

SERVER_PORT = int(os.environ.get("COSMO_PORT", 5174))
SERVER_HOST = os.environ.get("COSMO_HOST", "0.0.0.0")

# ---------------------------------------------------------------------------
# Document processing
# ---------------------------------------------------------------------------

ALLOWED_EXTENSIONS = {".pdf", ".md", ".markdown"}

CHUNK_SIZE = int(os.environ.get("COSMO_CHUNK_SIZE", 800))
CHUNK_OVERLAP = int(os.environ.get("COSMO_CHUNK_OVERLAP", 150))
EMBEDDING_BATCH_SIZE = 50

# ---------------------------------------------------------------------------
# LLM models (Ollama)
# ---------------------------------------------------------------------------

EMBED_MODEL = "nomic-embed-text"

CHAT_MODELS = {
    "quick": "qwen2.5-coder:7b",
    "deep": "qwen2.5-coder:14b",
    "general": "llama3.1:8b",
    "fast": "mistral:7b",
}

VALID_MODES = tuple(CHAT_MODELS.keys())

# ---------------------------------------------------------------------------
# Ollama inference options
#
# Tuned for M2 Pro 32GB. Adjust num_ctx and num_batch if running on
# a machine with less memory.
# ---------------------------------------------------------------------------

NUM_THREAD = 8  # M2 Pro has 12 cores; 8 avoids OS contention

# Chat (interactive streaming) — needs headroom for conversation history
CHAT_OPTIONS = {
    "quick": {
        "num_ctx": 8192,
        "num_thread": NUM_THREAD,
        "num_batch": 512,
    },
    "deep": {
        "num_ctx": 16384,
        "num_thread": NUM_THREAD,
        "num_batch": 1024,
    },
    "general": {
        "num_ctx": 8192,
        "num_thread": NUM_THREAD,
        "num_batch": 512,
    },
    "fast": {
        "num_ctx": 4096,
        "num_thread": NUM_THREAD,
        "num_batch": 512,
    },
}

# Quiz — deterministic, per-question-type token limits
QUIZ_OPTIONS = {
    "quick": {
        "num_ctx": 8192,
        "num_thread": NUM_THREAD,
        "num_batch": 512,
        "temperature": 0,
    },
    "deep": {
        "num_ctx": 16384,
        "num_thread": NUM_THREAD,
        "num_batch": 1024,
        "temperature": 0,
    },
    "general": {
        "num_ctx": 8192,
        "num_thread": NUM_THREAD,
        "num_batch": 512,
        "temperature": 0,
    },
    "fast": {
        "num_ctx": 4096,
        "num_thread": NUM_THREAD,
        "num_batch": 512,
        "temperature": 0,
    },
}

# Max tokens to generate per question type in quiz mode
QUIZ_NUM_PREDICT = {
    "tf": 256,
    "mc": 256,
    "sa": 512,
}

# Evaluation endpoint (SA grading in Apollo)
EVAL_OPTIONS = {
    "num_ctx": 8192,
    "num_thread": NUM_THREAD,
    "num_batch": 512,
    "temperature": 0,
    "num_predict": 256,
}

# ---------------------------------------------------------------------------
# Chat history
# ---------------------------------------------------------------------------

DEFAULT_HISTORY_TURNS = 10