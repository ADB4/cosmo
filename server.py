"""
Web API server for Cosmo — React/TypeScript Study Companion

Exposes the DocumentProcessor via a REST + SSE API.
Run with: python server.py
"""

from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
from werkzeug.utils import secure_filename
from document_processor import DocumentProcessor, ChatHistory, OllamaConnectionError
from pathlib import Path
import json
import tempfile
import shutil
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# ---------------------------------------------------------------------------
# Globals — initialised lazily so the server can start even if Ollama is down
# ---------------------------------------------------------------------------
_processor: DocumentProcessor | None = None
_history = ChatHistory(max_turns=10)

UPLOAD_DIR = Path("./uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {".pdf", ".md", ".markdown"}


def get_processor() -> DocumentProcessor:
    """Lazy-init the processor on first real request."""
    global _processor
    if _processor is None:
        _processor = DocumentProcessor()
    return _processor


# ---------------------------------------------------------------------------
# Health / status
# ---------------------------------------------------------------------------

@app.route("/api/health", methods=["GET"])
def health():
    """Check if the backend + Ollama are reachable."""
    try:
        proc = get_processor()
        stats = proc.get_stats()
        return jsonify({
            "status": "ok",
            "total_chunks": stats["total_chunks"],
            "total_documents": stats["total_documents"],
        })
    except OllamaConnectionError as e:
        return jsonify({"status": "error", "message": str(e)}), 503
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/stats", methods=["GET"])
def stats():
    """Return knowledge-base statistics."""
    try:
        proc = get_processor()
        return jsonify(proc.get_stats())
    except OllamaConnectionError as e:
        return jsonify({"error": str(e)}), 503
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------------------------------------------------------------------------
# Chat — streaming via Server-Sent Events
# ---------------------------------------------------------------------------

@app.route("/api/chat", methods=["POST"])
def chat():
    """
    Ask a question. Returns an SSE stream of tokens.

    Body JSON:
        question: str
        mode: "quick" | "deep" | "general" | "fast"  (default "quick")
        n_results: int  (default 4)
    """
    data = request.get_json(silent=True) or {}
    question = data.get("question", "").strip()
    mode = data.get("mode", "quick")
    n_results = data.get("n_results", 4)

    if not question:
        return jsonify({"error": "question is required"}), 400

    if mode not in ("quick", "deep", "general", "fast"):
        return jsonify({"error": f"invalid mode: {mode}"}), 400

    def generate():
        try:
            proc = get_processor()
            for token in proc.ask_stream(
                question, mode=mode, n_results=n_results, history=_history
            ):
                # SSE format: each event is "data: <payload>\n\n"
                payload = json.dumps({"token": token})
                yield f"data: {payload}\n\n"
            yield "data: [DONE]\n\n"
        except OllamaConnectionError as e:
            payload = json.dumps({"error": str(e)})
            yield f"data: {payload}\n\n"
        except Exception as e:
            logger.exception("Error during chat stream")
            payload = json.dumps({"error": str(e)})
            yield f"data: {payload}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


# ---------------------------------------------------------------------------
# History management
# ---------------------------------------------------------------------------

@app.route("/api/history/clear", methods=["POST"])
def clear_history():
    """Clear conversation history."""
    _history.clear()
    return jsonify({"status": "cleared"})


# ---------------------------------------------------------------------------
# Document ingestion
# ---------------------------------------------------------------------------

@app.route("/api/ingest", methods=["POST"])
def ingest():
    """
    Upload and ingest a file (PDF or Markdown).

    Expects multipart/form-data with a 'file' field.
    Optional query param: force=true
    """
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    if not file.filename:
        return jsonify({"error": "Empty filename"}), 400

    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        return jsonify({"error": f"Unsupported file type: {ext}. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"}), 400

    force = request.args.get("force", "false").lower() == "true"

    # Save to uploads directory
    safe_name = secure_filename(file.filename)
    dest = UPLOAD_DIR / safe_name
    file.save(str(dest))

    try:
        proc = get_processor()
        if ext == ".pdf":
            count = proc.ingest_pdf(str(dest), force=force)
        else:
            count = proc.ingest_markdown(str(dest), force=force)

        return jsonify({
            "status": "ok",
            "filename": safe_name,
            "chunks_indexed": count,
        })
    except OllamaConnectionError as e:
        return jsonify({"error": str(e)}), 503
    except Exception as e:
        logger.exception("Ingestion error")
        return jsonify({"error": str(e)}), 500


@app.route("/api/ingest/directory", methods=["POST"])
def ingest_directory():
    """
    Ingest all supported files from a local directory path.

    Body JSON:
        path: str — absolute or relative directory path
        force: bool (default false)
    """
    data = request.get_json(silent=True) or {}
    dir_path = data.get("path", "").strip()
    force = data.get("force", False)

    if not dir_path:
        return jsonify({"error": "path is required"}), 400

    p = Path(dir_path)
    if not p.exists() or not p.is_dir():
        return jsonify({"error": f"Directory not found: {dir_path}"}), 404

    results = []
    try:
        proc = get_processor()
        for ext_glob in ("**/*.pdf", "**/*.md", "**/*.markdown"):
            for filepath in p.glob(ext_glob):
                try:
                    ext = filepath.suffix.lower()
                    if ext == ".pdf":
                        count = proc.ingest_pdf(str(filepath), force=force)
                    else:
                        count = proc.ingest_markdown(str(filepath), force=force)
                    results.append({"file": filepath.name, "chunks": count})
                except Exception as e:
                    results.append({"file": filepath.name, "error": str(e)})

        return jsonify({"status": "ok", "files": results})
    except OllamaConnectionError as e:
        return jsonify({"error": str(e)}), 503
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    port = int(os.environ.get("COSMO_PORT", 5174))
    print(f"\n  Cosmo API server starting on http://localhost:{port}")
    print(f"  Uploads directory: {UPLOAD_DIR.resolve()}\n")
    app.run(host="0.0.0.0", port=port, debug=True)
