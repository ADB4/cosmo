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

# DECK JSON directory (created at startup)
DECK_DIR = Path(os.environ.get("COSMO_DECK_DIR", str(PROJECT_ROOT / "decks")))

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

CHUNK_SIZE = int(os.environ.get("COSMO_CHUNK_SIZE", 1200))
CHUNK_OVERLAP = int(os.environ.get("COSMO_CHUNK_OVERLAP", 200))
EMBEDDING_BATCH_SIZE = 50

# ---------------------------------------------------------------------------
# Embedding model (Ollama)
#
# The default stays nomic-embed-text so the existing chroma_db keeps working
# without a re-ingest. Opt into a stronger embedder with COSMO_EMBED_MODEL;
# switching embedding models requires a fresh collection and a full re-ingest
# (see `python -m backend.cli reindex`) because vector spaces are not
# comparable across models. The Chroma collection is named after the active
# embedding model (see DocumentProcessor) so the two never mix.
# ---------------------------------------------------------------------------

EMBED_MODEL = os.environ.get("COSMO_EMBED_MODEL", "nomic-embed-text")

# Per-embedding-model tuning. `max_tokens` is the per-chunk truncation limit
# (embedders have different context windows), and `retrieval_max_distance` is
# the cosine-distance relevance cutoff, which must be re-tuned per model
# (see `python -m backend.cli tune-cutoff`). The nomic values are tuned
# empirically; the others are PLACEHOLDERS to re-tune after a reindex.
EMBED_PROFILES = {
    "nomic-embed-text": {"max_tokens": 500, "retrieval_max_distance": 0.42},
    "qwen3-embedding:0.6b": {"max_tokens": 2000, "retrieval_max_distance": 0.60},  # PLACEHOLDER — tune
    "embeddinggemma": {"max_tokens": 2000, "retrieval_max_distance": 0.60},        # PLACEHOLDER — tune
}

# Resolve the active profile, falling back to nomic's numbers for an unknown
# embedding model rather than crashing.
_ACTIVE_EMBED_PROFILE = EMBED_PROFILES.get(EMBED_MODEL, EMBED_PROFILES["nomic-embed-text"])

# Per-chunk embedding token cap. Resolves from the active profile unless the
# env var explicitly overrides it.
EMBED_MAX_TOKENS = int(
    os.environ.get("COSMO_EMBED_MAX_TOKENS", _ACTIVE_EMBED_PROFILE["max_tokens"])
)

# ---------------------------------------------------------------------------
# Retrieval relevance cutoff
#
# Chunks whose vector distance to the query exceeds this are treated as
# irrelevant and dropped. In grounded ("Docs only") mode, if NOTHING passes
# the cutoff the LLM is not called at all — the client is told the docs have
# nothing relevant instead of getting a hallucinated answer.
#
# The collection uses ChromaDB's cosine space (see DocumentProcessor), so
# distances run 0 (identical) .. 2 (opposite). Tuned empirically against
# nomic-embed-text: on-topic React/TS/testing queries retrieve top chunks at
# ~0.25-0.35, while off-topic queries (e.g. "season a cast iron pan") bottom
# out at ~0.46. 0.42 keeps the former and drops the latter with margin.
#
# The default resolves from the active embedding profile (each model needs its
# own cutoff); COSMO_RETRIEVAL_MAX_DISTANCE overrides it per-environment.
# ---------------------------------------------------------------------------

RETRIEVAL_MAX_DISTANCE = float(
    os.environ.get(
        "COSMO_RETRIEVAL_MAX_DISTANCE",
        _ACTIVE_EMBED_PROFILE["retrieval_max_distance"],
    )
)

# ---------------------------------------------------------------------------
# LLM chat models (Ollama)
#
# Mode names reflect actual model identity rather than implying a quality
# hierarchy. Sized for an M2 Pro / 32 GB machine: any single model stays at or
# under ~20 GB of weights, and the default chat model + grader + embedding
# model are meant to be resident at once. Do NOT pair qwen3.6:27b with a
# second large model — it is the slow "deep" option and wants the memory.
# ---------------------------------------------------------------------------

DEFAULT_MODE = "qwen3-coder-30b"

CHAT_MODELS = {
    "qwen3-coder-30b": "qwen3-coder:30b",  # default; MoE, ~3.3B active, ~19 GB
    "qwen3.6-27b": "qwen3.6:27b",          # dense quality mode, ~17-22 GB, slow
    "gpt-oss-20b": "gpt-oss:20b",          # MoE, ~13 GB
    "gemma4-12b": "gemma4:12b",            # ~8 GB, general explanations
}

VALID_MODES = tuple(CHAT_MODELS.keys())

# ---------------------------------------------------------------------------
# Ollama inference options
#
# Tuned for M2 Pro 32GB. Adjust num_ctx and num_batch if running on
# a machine with less memory. All chat modes use a 16K context; MoE models
# and gemma4 use num_batch 512, the dense qwen3.6 uses 1024.
# ---------------------------------------------------------------------------

NUM_THREAD = 8  # M2 Pro has 12 cores; 8 avoids OS contention

# Chat (interactive streaming) — needs headroom for conversation history
CHAT_OPTIONS = {
    "qwen3-coder-30b": {
        "num_ctx": 16384,
        "num_thread": NUM_THREAD,
        "num_batch": 512,
        "num_predict": 1024,
    },
    "qwen3.6-27b": {
        "num_ctx": 16384,
        "num_thread": NUM_THREAD,
        "num_batch": 1024,
        "num_predict": 1024,
    },
    "gpt-oss-20b": {
        "num_ctx": 16384,
        "num_thread": NUM_THREAD,
        "num_batch": 512,
        "num_predict": 1024,
    },
    "gemma4-12b": {
        "num_ctx": 16384,
        "num_thread": NUM_THREAD,
        "num_batch": 512,
        "num_predict": 1024,
    },
}

# Quiz — deterministic; per-question-type token limits applied at call time.
QUIZ_OPTIONS = {
    "qwen3-coder-30b": {
        "num_ctx": 16384,
        "num_thread": NUM_THREAD,
        "num_batch": 512,
        "temperature": 0,
    },
    "qwen3.6-27b": {
        "num_ctx": 16384,
        "num_thread": NUM_THREAD,
        "num_batch": 1024,
        "temperature": 0,
    },
    "gpt-oss-20b": {
        "num_ctx": 16384,
        "num_thread": NUM_THREAD,
        "num_batch": 512,
        "temperature": 0,
    },
    "gemma4-12b": {
        "num_ctx": 16384,
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

# ---------------------------------------------------------------------------
# Short-answer grader (Ollama)
#
# Grading is a separate, cheap job — it does not use the chat mode. A small
# instruct model runs it so the default chat model, the grader, and the
# embedding model can all stay resident at once (no eviction/reload per grade).
# resolve_grader_model() in server.py picks the first of these that is
# installed, falling back to the default chat model with a warning.
# ---------------------------------------------------------------------------

GRADER_MODEL = "qwen3:4b"
GRADER_FALLBACKS = ["gemma4:e4b"]

GRADER_OPTIONS = {
    "num_ctx": 8192,
    "num_thread": NUM_THREAD,
    "temperature": 0,
    "num_predict": 256,
}

# ---------------------------------------------------------------------------
# Chat history
# ---------------------------------------------------------------------------

DEFAULT_HISTORY_TURNS = 10