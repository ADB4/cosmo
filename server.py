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

QUIZ_DIR = Path("./quizzes")
QUIZ_DIR.mkdir(exist_ok=True)

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
# Quiz / Apollo endpoints
# ---------------------------------------------------------------------------

def _validate_quiz_json(data: dict) -> str | None:
    """Return an error string if the quiz JSON is malformed, else None."""
    if "quizzes" not in data or not isinstance(data["quizzes"], list):
        return "Missing or invalid 'quizzes' array"
    for qi, quiz in enumerate(data["quizzes"]):
        if "id" not in quiz or "sections" not in quiz:
            return f"Quiz at index {qi} missing 'id' or 'sections'"
        for si, section in enumerate(quiz.get("sections", [])):
            if "type" not in section or "questions" not in section:
                return f"Section {si} in quiz '{quiz.get('id')}' missing 'type' or 'questions'"
    return None


@app.route("/api/quizzes", methods=["GET"])
def list_quizzes():
    """List all ingested quiz files and their quiz IDs."""
    results = []
    for fp in sorted(QUIZ_DIR.glob("*.json")):
        try:
            with open(fp) as f:
                data = json.load(f)
            for quiz in data.get("quizzes", []):
                total_q = sum(
                    len(s.get("questions", []))
                    for s in quiz.get("sections", [])
                )
                results.append({
                    "file": fp.name,
                    "id": quiz.get("id", fp.stem),
                    "title": quiz.get("title", fp.stem),
                    "scope": quiz.get("scope", ""),
                    "total_questions": total_q,
                    "sections": [
                        {"type": s["type"], "count": len(s.get("questions", []))}
                        for s in quiz.get("sections", [])
                    ],
                })
        except Exception as e:
            logger.warning(f"Error reading quiz file {fp.name}: {e}")
    return jsonify({"quizzes": results})


@app.route("/api/quizzes/<quiz_id>", methods=["GET"])
def get_quiz(quiz_id: str):
    """Return full quiz data for a given quiz ID."""
    for fp in QUIZ_DIR.glob("*.json"):
        try:
            with open(fp) as f:
                data = json.load(f)
            for quiz in data.get("quizzes", []):
                if quiz.get("id") == quiz_id:
                    return jsonify(quiz)
        except Exception:
            continue
    return jsonify({"error": f"Quiz '{quiz_id}' not found"}), 404


@app.route("/api/quizzes/ingest", methods=["POST"])
def ingest_quiz():
    """
    Ingest a quiz JSON file.

    Accepts either:
    - multipart/form-data with a 'file' field (.json file upload)
    - application/json body with {"path": "/absolute/path/to/quizzes.json"}
    """
    # Path-based ingestion
    if request.content_type and "json" in request.content_type:
        body = request.get_json(silent=True) or {}
        file_path = body.get("path", "").strip()
        if not file_path:
            return jsonify({"error": "path is required"}), 400
        p = Path(file_path)
        if not p.exists() or not p.is_file():
            return jsonify({"error": f"File not found: {file_path}"}), 404
        if p.suffix.lower() != ".json":
            return jsonify({"error": "File must be .json"}), 400
        try:
            with open(p) as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            return jsonify({"error": f"Invalid JSON: {e}"}), 400

        err = _validate_quiz_json(data)
        if err:
            return jsonify({"error": err}), 400

        dest = QUIZ_DIR / p.name
        shutil.copy2(str(p), str(dest))

        quiz_ids = [q["id"] for q in data.get("quizzes", [])]
        total = sum(
            len(s.get("questions", []))
            for q in data["quizzes"]
            for s in q.get("sections", [])
        )
        return jsonify({
            "status": "ok",
            "filename": p.name,
            "quiz_ids": quiz_ids,
            "total_questions": total,
        })

    # File upload
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    if not file.filename:
        return jsonify({"error": "Empty filename"}), 400

    if not file.filename.lower().endswith(".json"):
        return jsonify({"error": "File must be .json"}), 400

    try:
        raw = file.read()
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        return jsonify({"error": f"Invalid JSON: {e}"}), 400

    err = _validate_quiz_json(data)
    if err:
        return jsonify({"error": err}), 400

    safe_name = secure_filename(file.filename)
    dest = QUIZ_DIR / safe_name
    with open(dest, "wb") as f:
        f.write(raw)

    quiz_ids = [q["id"] for q in data.get("quizzes", [])]
    total = sum(
        len(s.get("questions", []))
        for q in data["quizzes"]
        for s in q.get("sections", [])
    )
    return jsonify({
        "status": "ok",
        "filename": safe_name,
        "quiz_ids": quiz_ids,
        "total_questions": total,
    })


# ---------------------------------------------------------------------------
# Short-answer evaluation via Ollama + RAG
# ---------------------------------------------------------------------------

@app.route("/api/quizzes/evaluate", methods=["POST"])
def evaluate_answer():
    """
    Evaluate a short-answer response using Ollama with RAG context.

    Body JSON:
        question: str       — the quiz question text
        user_answer: str    — what the user wrote
        model_answer: str   — the reference/model answer from the answer key
        mode: str           — LLM mode (default "quick")
    
    Returns JSON:
        score: str          — "correct", "partial", or "incorrect"
        feedback: str       — explanation of the evaluation
    """
    data = request.get_json(silent=True) or {}
    question = data.get("question", "").strip()
    user_answer = data.get("user_answer", "").strip()
    model_answer = data.get("model_answer", "").strip()
    mode = data.get("mode", "quick")

    if not question or not user_answer:
        return jsonify({"error": "question and user_answer are required"}), 400

    try:
        proc = get_processor()
    except OllamaConnectionError as e:
        return jsonify({"error": str(e)}), 503

    # Retrieve RAG context related to the question topic
    rag_context = ""
    try:
        results = proc.query(question, n_results=4)
        if results["documents"][0]:
            parts = []
            for i, (doc, meta) in enumerate(
                zip(results["documents"][0], results["metadatas"][0])
            ):
                source = meta.get("source", "unknown")
                page = meta.get("page", "?")
                parts.append(f"[{i+1}] From {source}, page {page}:\n{doc}")
            rag_context = "\n\n".join(parts)
    except Exception as e:
        logger.warning(f"RAG context retrieval failed: {e}")

    # Build evaluation prompt
    doc_block = ""
    if rag_context:
        doc_block = f"""
Relevant documentation excerpts:
{rag_context}

"""

    prompt = f"""You are grading a short-answer question from a React/TypeScript quiz.

Question:
{question}

Model answer (reference):
{model_answer}

Student's answer:
{user_answer}
{doc_block}
Evaluate the student's answer. Consider:
1. Does it capture the key concepts from the model answer?
2. Is it technically accurate based on the documentation?
3. Are there any misconceptions or missing critical points?

Respond in EXACTLY this JSON format and nothing else:
{{"score": "<correct|partial|incorrect>", "feedback": "<1-3 sentence explanation>"}}"""

    llm_model = proc.models.get(mode, proc.models["quick"])

    try:
        import ollama as _ollama
        response = _ollama.chat(
            model=llm_model,
            messages=[{"role": "user", "content": prompt}],
            options={"num_ctx": 8192, "num_thread": 8},
        )
        raw = response["message"]["content"].strip()

        # Try to parse JSON from the response
        # Strip markdown fences if present
        cleaned = raw
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[-1]
        if cleaned.endswith("```"):
            cleaned = cleaned.rsplit("```", 1)[0]
        cleaned = cleaned.strip()

        try:
            result = json.loads(cleaned)
            score = result.get("score", "partial")
            feedback = result.get("feedback", raw)
        except json.JSONDecodeError:
            # Fallback: try to extract score from raw text
            raw_lower = raw.lower()
            if "correct" in raw_lower and "incorrect" not in raw_lower:
                score = "correct"
            elif "incorrect" in raw_lower:
                score = "incorrect"
            else:
                score = "partial"
            feedback = raw

        # Normalize score
        if score not in ("correct", "partial", "incorrect"):
            score = "partial"

        return jsonify({"score": score, "feedback": feedback})

    except Exception as e:
        logger.exception("Evaluation error")
        return jsonify({"error": str(e)}), 500


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    port = int(os.environ.get("COSMO_PORT", 5174))
    print(f"\n  Cosmo API server starting on http://localhost:{port}")
    print(f"  Uploads directory: {UPLOAD_DIR.resolve()}\n")
    app.run(host="0.0.0.0", port=port, debug=True)