"""
Cosmo API server — Flask + SSE.

Run with:  python -m backend.server   (from project root)
"""

import json
import logging
import os

from flask import Flask, Response, jsonify, request, stream_with_context
from flask_cors import CORS
from pathlib import Path
from werkzeug.utils import secure_filename

from backend.config import (
    ALLOWED_EXTENSIONS,
    DEFAULT_HISTORY_TURNS,
    QUIZ_DIR,
    SERVER_HOST,
    SERVER_PORT,
    UPLOAD_DIR,
    VALID_MODES,
)
from backend.document_processor import (
    ChatHistory,
    DocumentProcessor,
    OllamaConnectionError,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# ---------------------------------------------------------------------------
# Globals — initialised lazily so the server can start even if Ollama is down
# ---------------------------------------------------------------------------

_processor: DocumentProcessor | None = None
_history = ChatHistory(max_turns=DEFAULT_HISTORY_TURNS)

UPLOAD_DIR.mkdir(exist_ok=True)
QUIZ_DIR.mkdir(exist_ok=True)


def get_processor() -> DocumentProcessor:
    global _processor
    if _processor is None:
        _processor = DocumentProcessor()
    return _processor


# ===================================================================
# Health / status
# ===================================================================

@app.route("/api/health", methods=["GET"])
def health():
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
    try:
        proc = get_processor()
        return jsonify(proc.get_stats())
    except OllamaConnectionError as e:
        return jsonify({"error": str(e)}), 503
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ===================================================================
# Chat — streaming via Server-Sent Events
# ===================================================================

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    question = data.get("question", "").strip()
    mode = data.get("mode", "quick")
    n_results = data.get("n_results", 4)

    if not question:
        return jsonify({"error": "question is required"}), 400
    if mode not in VALID_MODES:
        return jsonify({"error": f"invalid mode: {mode}"}), 400

    def generate():
        try:
            proc = get_processor()
            for token in proc.ask_stream(
                question, mode=mode, n_results=n_results, history=_history
            ):
                yield f"data: {json.dumps({'token': token})}\n\n"
            yield "data: [DONE]\n\n"
        except OllamaConnectionError as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
        except Exception as e:
            logger.exception("Error during chat stream")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# ===================================================================
# History management
# ===================================================================

@app.route("/api/history/clear", methods=["POST"])
def clear_history():
    _history.clear()
    return jsonify({"status": "cleared"})


# ===================================================================
# Document ingestion
# ===================================================================

@app.route("/api/ingest", methods=["POST"])
def ingest():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    if not file.filename:
        return jsonify({"error": "Empty filename"}), 400

    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        allowed = ", ".join(ALLOWED_EXTENSIONS)
        return jsonify({"error": f"Unsupported file type: {ext}. Allowed: {allowed}"}), 400

    force = request.args.get("force", "false").lower() == "true"
    safe_name = secure_filename(file.filename)
    dest = UPLOAD_DIR / safe_name
    file.save(str(dest))

    try:
        proc = get_processor()
        count = (
            proc.ingest_pdf(str(dest), force=force)
            if ext == ".pdf"
            else proc.ingest_markdown(str(dest), force=force)
        )
        return jsonify({"status": "ok", "filename": safe_name, "chunks_indexed": count})
    except OllamaConnectionError as e:
        return jsonify({"error": str(e)}), 503
    except Exception as e:
        logger.exception("Ingestion error")
        return jsonify({"error": str(e)}), 500


@app.route("/api/ingest/directory", methods=["POST"])
def ingest_directory():
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
                    count = (
                        proc.ingest_pdf(str(filepath), force=force)
                        if ext == ".pdf"
                        else proc.ingest_markdown(str(filepath), force=force)
                    )
                    results.append({"file": filepath.name, "chunks": count})
                except Exception as e:
                    results.append({"file": filepath.name, "error": str(e)})
        return jsonify({"status": "ok", "files": results})
    except OllamaConnectionError as e:
        return jsonify({"error": str(e)}), 503
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ===================================================================
# Quiz / Apollo endpoints
# ===================================================================

def _validate_quiz_json(data: dict) -> str | None:
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
    # Handle file upload
    if "file" in request.files:
        file = request.files["file"]
        if not file.filename:
            return jsonify({"error": "Empty filename"}), 400
        safe_name = secure_filename(file.filename)
        if not safe_name.endswith(".json"):
            return jsonify({"error": "Only .json files accepted"}), 400
        dest = QUIZ_DIR / safe_name
        file.save(str(dest))
    else:
        # Handle path-based ingest
        data = request.get_json(silent=True) or {}
        src = data.get("path", "").strip()
        if not src:
            return jsonify({"error": "No file or path provided"}), 400
        src_path = Path(src)
        if not src_path.exists():
            return jsonify({"error": f"File not found: {src}"}), 404
        safe_name = secure_filename(src_path.name)
        dest = QUIZ_DIR / safe_name
        import shutil
        shutil.copy2(str(src_path), str(dest))

    # Validate
    try:
        with open(dest) as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        dest.unlink(missing_ok=True)
        return jsonify({"error": f"Invalid JSON: {e}"}), 400

    err = _validate_quiz_json(data)
    if err:
        dest.unlink(missing_ok=True)
        return jsonify({"error": err}), 400

    quiz_ids = [q.get("id", "?") for q in data["quizzes"]]
    total_q = sum(
        len(s.get("questions", []))
        for q in data["quizzes"]
        for s in q.get("sections", [])
    )

    return jsonify({
        "status": "ok",
        "filename": safe_name,
        "quiz_ids": quiz_ids,
        "total_questions": total_q,
    })


@app.route("/api/quizzes/evaluate", methods=["POST"])
def evaluate_answer():
    data = request.get_json(silent=True) or {}
    question = data.get("question", "")
    user_answer = data.get("user_answer", "")
    model_answer = data.get("model_answer", "")
    mode = data.get("mode", "quick")

    if not question or not user_answer:
        return jsonify({"error": "question and user_answer are required"}), 400

    try:
        proc = get_processor()
    except OllamaConnectionError as e:
        return jsonify({"error": str(e)}), 503

    # Optional RAG context
    doc_block = ""
    try:
        results = proc.query(question, n_results=2)
        if results["documents"][0]:
            doc_block = (
                "\n\nRelevant documentation:\n"
                + "\n".join(results["documents"][0][:2])
            )
    except Exception:
        pass

    prompt = (
        f"You are grading a technical quiz answer.\n\n"
        f"Question:\n{question}\n\n"
        f"Model answer (reference):\n{model_answer}\n\n"
        f"Student's answer:\n{user_answer}\n"
        f"{doc_block}\n"
        "Evaluate the student's answer. Consider:\n"
        "1. Does it capture the key concepts from the model answer?\n"
        "2. Is it technically accurate based on the documentation?\n"
        "3. Are there any misconceptions or missing critical points?\n\n"
        'Respond in EXACTLY this JSON format and nothing else:\n'
        '{"score": "<correct|partial|incorrect>", "feedback": "<1-3 sentence explanation>"}'
    )

    llm_model = proc.models.get(mode, proc.models["quick"])

    try:
        import ollama as _ollama

        response = _ollama.chat(
            model=llm_model,
            messages=[{"role": "user", "content": prompt}],
            options={"num_ctx": 8192, "num_thread": 8},
        )
        raw = response["message"]["content"].strip()

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
            raw_lower = raw.lower()
            if "correct" in raw_lower and "incorrect" not in raw_lower:
                score = "correct"
            elif "incorrect" in raw_lower:
                score = "incorrect"
            else:
                score = "partial"
            feedback = raw

        if score not in ("correct", "partial", "incorrect"):
            score = "partial"

        return jsonify({"score": score, "feedback": feedback})

    except Exception as e:
        logger.exception("Evaluation error")
        return jsonify({"error": str(e)}), 500


# ===================================================================
# Main
# ===================================================================

if __name__ == "__main__":
    port = SERVER_PORT
    print(f"\n  Cosmo API server starting on http://localhost:{port}")
    print(f"  Uploads directory: {UPLOAD_DIR.resolve()}\n")
    app.run(host=SERVER_HOST, port=port, debug=True)
