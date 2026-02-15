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

CHUNK_SIZE = int(os.environ.get("COSMO_CHUNK_SIZE", 1500))
CHUNK_OVERLAP = int(os.environ.get("COSMO_CHUNK_OVERLAP", 200))
EMBEDDING_BATCH_SIZE = 50
EMBED_MAX_TOKENS = int(os.environ.get("COSMO_EMBED_MAX_TOKENS", 512))
# ---------------------------------------------------------------------------
# LLM models (Ollama)
#
# Mode names reflect actual model identity rather than implying
# a quality hierarchy. Benchmark data (192 questions, 6 quizzes)
# showed qwen-7b as the best all-round performer.
# ---------------------------------------------------------------------------

EMBED_MODEL = "mxbai-embed-large"

CHAT_MODELS = {
    "gemma2-9b": "gemma2:9b",
    "llama3-3b": "llama3.2:3b",
    "llama3-8b":    "llama3.1:8b",
    "mistral-7b":  "mistral:7b",
    "phi4-14b": "phi4:14b",
    "qwen-7b":  "qwen2.5-coder:7b",
    "qwen-14b": "qwen2.5-coder:14b",
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
    "gemma2-9b": {
        "num_ctx": 16384,
        "num_thread": NUM_THREAD,
        "num_batch": 1024,
    },
    "llama3-3b": {
        "num_ctx": 4096,
        "num_thread": NUM_THREAD,
        "num_batch": 512,
    },
    "llama3-8b": {
        "num_ctx": 8192,
        "num_thread": NUM_THREAD,
        "num_batch": 512,
    },
    "mistral-7b": {
        "num_ctx": 4096,
        "num_thread": NUM_THREAD,
        "num_batch": 512,
    },
    "phi4-14b": {
        "num_ctx": 16384,
        "num_thread": NUM_THREAD,
        "num_batch": 1024,
    },
    "qwen-7b": {
        "num_ctx": 8192,
        "num_thread": NUM_THREAD,
        "num_batch": 512,
    },
    "qwen-14b": {
        "num_ctx": 16384,
        "num_thread": NUM_THREAD,
        "num_batch": 1024,
    },
}

# Quiz — deterministic, per-question-type token limits
QUIZ_OPTIONS = {
    "gemma2-9b": {
        "num_ctx": 8192,
        "num_thread": NUM_THREAD,
        "num_batch": 1024,
        "temperature": 0,
    },
    "llama3-3b": {
        "num_ctx": 4096,
        "num_thread": NUM_THREAD,
        "num_batch": 512,
        "temperature": 0,
    },
    "llama3-8b": {
        "num_ctx": 8192,
        "num_thread": NUM_THREAD,
        "num_batch": 512,
        "temperature": 0,
    },
    "mistral-7b": {
        "num_ctx": 4096,
        "num_thread": NUM_THREAD,
        "num_batch": 512,
        "temperature": 0,
    },
    "phi4-14b": {
        "num_ctx": 16384,
        "num_thread": NUM_THREAD,
        "num_batch": 1024,
        "temperature": 0,
    },
    "qwen-7b": {
        "num_ctx": 8192,
        "num_thread": NUM_THREAD,
        "num_batch": 512,
        "temperature": 0,
    },
    "qwen-14b": {
        "num_ctx": 16384,
        "num_thread": NUM_THREAD,
        "num_batch": 1024,
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