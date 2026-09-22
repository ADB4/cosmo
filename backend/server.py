"""
Cosmo API server — Flask + SSE.

Run with:  python -m backend.server   (from project root)
"""

import json
import logging
import os
from typing import Generator, Tuple

from flask import Flask, Response, jsonify, request, stream_with_context
from pathlib import Path
from werkzeug.exceptions import HTTPException
from werkzeug.utils import secure_filename

from backend.config import (
    ALLOWED_EXTENSIONS,
    CHAT_MODELS,
    CHAT_OPTIONS,
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    DB_PATH,
    DEFAULT_HISTORY_TURNS,
    DEFAULT_MODE,
    EMBED_MODEL,
    EMBEDDING_BATCH_SIZE,
    DECK_DIR,
    GRADER_FALLBACKS,
    GRADER_MODEL,
    GRADER_OPTIONS,
    INGEST_ROOTS,
    SERVER_HOST,
    SERVER_PORT,
    UPLOAD_DIR,
    VALID_MODES,
)
from backend.document_processor import (
    ChatHistory,
    DocumentProcessor,
    OllamaConnectionError,
    strip_think,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# No CORS: the frontend is same-origin in both modes (the Vite proxy in dev,
# nginx in Docker), so the API never needs cross-origin access. A wildcard
# CORS policy would only re-open the door to drive-by requests from any web
# page in local mode.

# ---------------------------------------------------------------------------
# Cloudflare Access JWT verification (optional defense in depth)
#
# In deployment Cloudflare Access is the only auth gate. When
# COSMO_CF_ACCESS_TEAM and COSMO_CF_ACCESS_AUD are set, every /api/* request
# must carry a valid `Cf-Access-Jwt-Assertion` header (RS256, signed by the
# team's JWKS, audience == the AUD tag) or it is rejected with 401. This means
# a request that somehow reaches the backend without passing Access — e.g. a
# tunnel/network misconfiguration — is still refused. Unset by default (local
# dev), so the block below is skipped entirely and PyJWT is never imported.
# ---------------------------------------------------------------------------

CF_ACCESS_TEAM = os.environ.get("COSMO_CF_ACCESS_TEAM", "").strip()
CF_ACCESS_AUD = os.environ.get("COSMO_CF_ACCESS_AUD", "").strip()

if CF_ACCESS_TEAM and CF_ACCESS_AUD:
    _CF_ISSUER = f"https://{CF_ACCESS_TEAM}.cloudflareaccess.com"
    _CF_CERTS_URL = f"{_CF_ISSUER}/cdn-cgi/access/certs"
    _cf_jwk_client = None  # created lazily so import needs no network

    def _cf_jwks_client():
        global _cf_jwk_client
        if _cf_jwk_client is None:
            import jwt
            # PyJWKClient fetches and caches the signing keys itself.
            _cf_jwk_client = jwt.PyJWKClient(_CF_CERTS_URL, cache_keys=True)
        return _cf_jwk_client

    @app.before_request
    def _verify_cf_access():
        if not request.path.startswith("/api/"):
            return None
        token = request.headers.get("Cf-Access-Jwt-Assertion", "")
        if not token:
            return jsonify({"error": "missing Cloudflare Access token"}), 401
        try:
            import jwt
            signing_key = _cf_jwks_client().get_signing_key_from_jwt(token)
            jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                audience=CF_ACCESS_AUD,
                issuer=_CF_ISSUER,
            )
        except Exception:
            logger.warning("Rejected /api request with invalid Cloudflare Access token")
            return jsonify({"error": "invalid Cloudflare Access token"}), 401
        return None

    logger.info("Cloudflare Access JWT verification enabled (aud=%s)", CF_ACCESS_AUD)

# ---------------------------------------------------------------------------
# Globals — initialised lazily so the server can start even if Ollama is down
# ---------------------------------------------------------------------------

_processor: DocumentProcessor | None = None
# NB: no process-global ChatHistory. It would be shared by every client — one
# user's turns leaking into another's prompt, one client's Clear wiping
# everyone, and format_for_prompt racing add() under the threaded server. Each
# /api/chat request builds its own ChatHistory from history sent in the body.

UPLOAD_DIR.mkdir(exist_ok=True)
DECK_DIR.mkdir(exist_ok=True)


def get_processor() -> DocumentProcessor:
    global _processor
    if _processor is None:
        _processor = DocumentProcessor()
    return _processor


# ---------------------------------------------------------------------------
# Request validation + error handling
#
# Unhandled exceptions must never leak a traceback (or, with the Werkzeug
# debugger, an interactive console) to the client: the API is reachable by
# every Cloudflare Access user in deployment and by the whole LAN locally.
# ---------------------------------------------------------------------------

class BadRequest(Exception):
    """A client error that should be reported as 400 JSON."""


def _json_body() -> dict:
    """The request's JSON object, or {} if there is none / it is not an object."""
    data = request.get_json(silent=True)
    return data if isinstance(data, dict) else {}


def _str_field(data: dict, key: str, default: str = "") -> str:
    """
    Return `data[key]` stripped, or `default` when absent. Raises BadRequest
    (-> 400 JSON) when the value is present but not a string, instead of
    letting `.strip()` raise AttributeError into a 500.
    """
    value = data.get(key, default)
    if not isinstance(value, str):
        raise BadRequest(f"{key} must be a string")
    return value.strip()


@app.errorhandler(BadRequest)
def _handle_bad_request(e: BadRequest):
    return jsonify({"error": str(e)}), 400


@app.errorhandler(Exception)
def _handle_unexpected(e: Exception):
    # Let Flask's own 404/405/413 etc. pass through unchanged.
    if isinstance(e, HTTPException):
        return e
    logger.exception("Unhandled error in %s %s", request.method, request.path)
    return jsonify({"error": "internal error"}), 500


# ---------------------------------------------------------------------------
# Grader model resolution
#
# The short-answer grader is a small, separate model — not the chat mode.
# We check `ollama.list()` once and cache the first installed candidate from
# [GRADER_MODEL, *GRADER_FALLBACKS], falling back to the default chat model
# (which is virtually always resident) with a logged warning.
# ---------------------------------------------------------------------------

_grader_model: str | None = None


def _installed_models() -> set[str]:
    import ollama as _ollama
    raw = _ollama.list()
    installed: set[str] = set()
    for m in raw.get("models", []):
        name = m.get("model") if isinstance(m, dict) else getattr(m, "model", None)
        if not name and isinstance(m, dict):
            name = m.get("name")
        if not name:
            name = getattr(m, "name", None)
        if name:
            installed.add(name)
    return installed


def resolve_grader_model() -> str:
    """
    Pick the grader model once and cache it. Returns the first of
    [GRADER_MODEL, *GRADER_FALLBACKS] that is installed; if none are, falls
    back to the default chat model's Ollama tag with a warning.
    """
    global _grader_model
    if _grader_model is not None:
        return _grader_model

    default_tag = CHAT_MODELS[DEFAULT_MODE]
    try:
        installed = _installed_models()
    except Exception as e:
        logger.warning(
            f"Could not list Ollama models to resolve grader ({e}); "
            f"falling back to default chat model '{default_tag}'."
        )
        _grader_model = default_tag
        return _grader_model

    for candidate in [GRADER_MODEL, *GRADER_FALLBACKS]:
        if candidate in installed:
            _grader_model = candidate
            return _grader_model

    logger.warning(
        f"No grader model installed (tried {[GRADER_MODEL, *GRADER_FALLBACKS]}); "
        f"falling back to default chat model '{default_tag}'. "
        f"Install one with: ollama pull {GRADER_MODEL}"
    )
    _grader_model = default_tag
    return _grader_model


# ---------------------------------------------------------------------------
# Ingest path containment
#
# The directory- and (historically) path-based ingest routes must never read
# outside a small set of allowed roots (see INGEST_ROOTS). A caller-supplied
# path is resolved and checked against those roots before anything is read.
# ---------------------------------------------------------------------------

def _ingest_root_for(resolved: Path) -> Path | None:
    """Return the first INGEST_ROOT that `resolved` sits inside, or None."""
    for root in INGEST_ROOTS:
        if resolved == root or resolved.is_relative_to(root):
            return root
    return None


def _ingest_roots_message() -> str:
    roots = ", ".join(str(r) for r in INGEST_ROOTS) or "(none configured)"
    return f"path must be inside an allowed ingest root: {roots}"


# ---------------------------------------------------------------------------
# Deck file discovery — walks module subdirectories under DECK_DIR
# ---------------------------------------------------------------------------

def _iter_deck_files() -> Generator[Tuple[Path, str], None, None]:
    """
    Yield (filepath, module_name) for every .json file inside DECK_DIR subdirectories.
    Only one level of nesting is supported: decks/<module>/<file>.json
    Loose files directly in DECK_DIR are ignored (everything must be in a module folder).
    """
    for subdir in sorted(DECK_DIR.iterdir()):
        if subdir.is_dir() and not subdir.name.startswith("."):
            for fp in sorted(subdir.glob("*.json")):
                yield fp, subdir.name


def _module_dir(module: str) -> Path | None:
    """
    Resolve a module name to its directory under DECK_DIR, guarding against
    path traversal. Returns None if the sanitized name is empty or the
    directory does not exist.
    """
    safe = secure_filename(module)
    if not safe:
        return None
    d = DECK_DIR / safe
    return d if d.is_dir() else None


def _iter_module_deck_files(module: str) -> Generator[Path, None, None]:
    """Yield every .json deck file inside a single module folder."""
    d = _module_dir(module)
    if d is None:
        return
    for fp in sorted(d.glob("*.json")):
        yield fp


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


@app.route("/api/models", methods=["GET"])
def list_models():
    """
    Return the configured chat modes whose underlying model is actually
    present in `ollama list`, so the UI can collapse its model dropdown to
    what's installed. On Ollama being unreachable, returns 503 and the UI
    falls back to showing all configured modes.
    """
    try:
        import ollama as _ollama
        raw = _ollama.list()
    except Exception as e:
        return jsonify({"error": f"Cannot reach Ollama: {e}"}), 503

    # ollama.list() entries expose the model tag as `.model` (newer) or
    # `.name` (older); normalise to a set of installed model strings.
    installed: set[str] = set()
    for m in raw.get("models", []):
        name = m.get("model") if isinstance(m, dict) else getattr(m, "model", None)
        if not name and isinstance(m, dict):
            name = m.get("name")
        if not name:
            name = getattr(m, "name", None)
        if name:
            installed.add(name)

    modes = [
        {"mode": mode, "model": model}
        for mode, model in CHAT_MODELS.items()
        if model in installed
    ]
    return jsonify({"modes": modes})


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

def _history_from_body(raw) -> ChatHistory:
    """
    Build a per-request ChatHistory from client-supplied prior turns.

    Accepts at most 10 objects, each {"question": str, "answer": str};
    anything malformed is skipped, and answers are truncated to 600 chars.
    The deque's maxlen caps it regardless. Isolating history per request is
    what keeps one client's conversation out of another's prompt.
    """
    hist = ChatHistory(max_turns=DEFAULT_HISTORY_TURNS)
    if not isinstance(raw, list):
        return hist
    for item in raw[:10]:
        if not isinstance(item, dict):
            continue
        q = item.get("question")
        a = item.get("answer")
        if not isinstance(q, str) or not isinstance(a, str):
            continue
        q = q.strip()
        if not q:
            continue
        hist.add(q, a[:600])
    return hist


@app.route("/api/chat", methods=["POST"])
def chat():
    data = _json_body()
    question = _str_field(data, "question")
    mode = data.get("mode", DEFAULT_MODE)
    n_results = data.get("n_results", 8)
    grounded = data.get("grounded", True)
    history = _history_from_body(data.get("history"))

    if not question:
        return jsonify({"error": "question is required"}), 400
    if mode not in VALID_MODES:
        return jsonify({"error": f"invalid mode: {mode}"}), 400

    def generate():
        try:
            proc = get_processor()
            for token in proc.ask_question(
                question, mode=mode, n_results=n_results, history=history,
                grounded=grounded,
            ):
                if token == proc.NO_RESULTS_SIGNAL:
                    # Grounded mode found nothing relevant — signal the client
                    # to show its "no relevant docs" state, never as answer text.
                    yield f"data: {json.dumps({'no_results': True})}\n\n"
                    continue
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
    finally:
        # Free Marker's models/MPS memory so it doesn't sit resident in the
        # long-lived Flask process alongside a large chat model.
        try:
            proc.release_extractor()
        except Exception:
            pass


@app.route("/api/ingest/directory", methods=["POST"])
def ingest_directory():
    data = _json_body()
    dir_path = _str_field(data, "path")
    force = data.get("force", False)

    if not dir_path:
        return jsonify({"error": "path is required"}), 400

    try:
        p = Path(dir_path).resolve(strict=True)
    except (OSError, RuntimeError):
        return jsonify({"error": f"Directory not found: {dir_path}"}), 404
    if not p.is_dir():
        return jsonify({"error": f"Directory not found: {dir_path}"}), 404

    # Refuse anything outside the allowed roots so this route can't be turned
    # into an arbitrary filesystem read.
    root = _ingest_root_for(p)
    if root is None:
        return jsonify({"error": _ingest_roots_message()}), 400

    results = []
    try:
        proc = get_processor()
        for ext_glob in ("**/*.pdf", "**/*.md", "**/*.markdown"):
            for filepath in p.glob(ext_glob):
                # Report paths relative to the matched root, never absolute,
                # so the response can't be used to map the filesystem.
                rel = str(filepath.relative_to(root))
                try:
                    ext = filepath.suffix.lower()
                    count = (
                        proc.ingest_pdf(str(filepath), force=force)
                        if ext == ".pdf"
                        else proc.ingest_markdown(str(filepath), force=force)
                    )
                    results.append({"file": rel, "chunks": count})
                except Exception as e:
                    results.append({"file": rel, "error": str(e)})
        return jsonify({"status": "ok", "files": results})
    except OllamaConnectionError as e:
        return jsonify({"error": str(e)}), 503
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        try:
            proc.release_extractor()
        except Exception:
            pass


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


@app.route("/api/modules", methods=["GET"])
def list_modules():
    """Return list of module subdirectories under DECK_DIR."""
    modules = []
    for subdir in sorted(DECK_DIR.iterdir()):
        if subdir.is_dir() and not subdir.name.startswith("."):
            modules.append(subdir.name)
    return jsonify({"modules": modules})


@app.route("/api/modules", methods=["POST"])
def create_module():
    """Create an (empty) module folder under DECK_DIR."""
    data = _json_body()
    name = _str_field(data, "name")
    if not name:
        return jsonify({"error": "name is required"}), 400

    safe = secure_filename(name)
    if not safe:
        return jsonify({"error": f"Invalid module name: {name}"}), 400

    module_dir = DECK_DIR / safe
    if module_dir.exists():
        return jsonify({"error": f"Module '{safe}' already exists"}), 409

    try:
        module_dir.mkdir(parents=False)
    except Exception as e:
        return jsonify({"error": f"Could not create module: {e}"}), 500

    return jsonify({"status": "ok", "module": safe}), 201


@app.route("/api/quizzes", methods=["GET"])
def list_quizzes():
    results = []
    for fp, module in _iter_deck_files():
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
                    "module": module,
                    "id": quiz.get("id", fp.stem),
                    "title": quiz.get("title", fp.stem),
                    "scope": quiz.get("scope", ""),
                    "order": quiz.get("order"),
                    "total_questions": total_q,
                    "sections": [
                        {"type": s["type"], "count": len(s.get("questions", []))}
                        for s in quiz.get("sections", [])
                    ],
                })
        except Exception as e:
            logger.warning(f"Error reading quiz file {fp.name}: {e}")
    return jsonify({"quizzes": results})


@app.route("/api/quizzes/<module>/<quiz_id>", methods=["GET"])
def get_quiz(module: str, quiz_id: str):
    """
    Fetch a quiz scoped to its module folder. The (module, quiz_id) pair is
    the real key — quiz ids are only unique within a module, so the same id
    can legitimately exist in two different modules (e.g. daily/week1 vs
    frontend/week1) and must not collide.
    """
    if _module_dir(module) is None:
        return jsonify({"error": f"Module '{module}' not found"}), 404
    for fp in _iter_module_deck_files(module):
        try:
            with open(fp) as f:
                data = json.load(f)
            for quiz in data.get("quizzes", []):
                if quiz.get("id") == quiz_id:
                    return jsonify(quiz)
        except Exception:
            continue
    return jsonify({"error": f"Quiz '{quiz_id}' not found in module '{module}'"}), 404


@app.route("/api/quizzes/ingest", methods=["POST"])
def ingest_quiz():
    # Determine target module subdirectory
    module = request.args.get("module", "").strip() or request.form.get("module", "").strip()
    if not module:
        return jsonify({"error": "module is required (query param or form field)"}), 400

    # Sanitize module name
    safe_module = secure_filename(module)
    if not safe_module:
        return jsonify({"error": f"Invalid module name: {module}"}), 400

    module_dir = DECK_DIR / safe_module
    module_dir.mkdir(exist_ok=True)

    # Only multipart file uploads are accepted. (Path-based ingest was removed:
    # it let any caller copy an arbitrary readable file into the decks folder.)
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400
    file = request.files["file"]
    if not file.filename:
        return jsonify({"error": "Empty filename"}), 400
    safe_name = secure_filename(file.filename)
    if not safe_name.endswith(".json"):
        return jsonify({"error": "Only .json files accepted"}), 400
    dest = module_dir / safe_name

    # Write the upload to a temp file in the same directory, validate it there,
    # and only os.replace() over the real deck once it passes. Saving straight
    # onto `dest` meant a malformed re-upload (bad JSON, schema failure, or an
    # id collision) destroyed the existing deck via the unlink on those paths.
    import tempfile
    tmp = tempfile.NamedTemporaryFile(
        dir=str(module_dir), suffix=".json.tmp", delete=False
    )
    tmp_path = Path(tmp.name)
    moved = False
    try:
        file.save(tmp)
        tmp.close()

        # Validate
        try:
            with open(tmp_path) as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            return jsonify({"error": f"Invalid JSON: {e}"}), 400

        err = _validate_quiz_json(data)
        if err:
            return jsonify({"error": err}), 400

        # Reject decks that reuse a quiz id already present in this module —
        # otherwise the (module, quiz_id) key stops being unique and lookups
        # would silently return the wrong deck.
        incoming_ids = [q.get("id") for q in data.get("quizzes", []) if q.get("id")]
        # Ids defined in *other* files in this module are what we clash against;
        # ids in the deck we're about to replace (same name = a re-upload) don't
        # count — compare against the final `dest`, not the temp file.
        own_ids: set[str] = set()
        for other_fp in _iter_module_deck_files(safe_module):
            if other_fp.resolve() == dest.resolve():
                continue
            try:
                with open(other_fp) as f:
                    other = json.load(f)
                for q in other.get("quizzes", []):
                    if q.get("id"):
                        own_ids.add(q["id"])
            except Exception:
                continue
        collisions = sorted({qid for qid in incoming_ids if qid in own_ids})
        if collisions:
            return jsonify({
                "error": (
                    f"Quiz id(s) already exist in module '{safe_module}': "
                    f"{', '.join(collisions)}. Rename the quiz id(s) or choose a "
                    f"different module."
                )
            }), 409

        # Passed every check — atomically put it in place.
        os.replace(str(tmp_path), str(dest))
        moved = True
    finally:
        if not moved:
            tmp_path.unlink(missing_ok=True)

    quiz_ids = [q.get("id", "?") for q in data.get("quizzes", [])]
    total_q = sum(
        len(s.get("questions", []))
        for q in data["quizzes"]
        for s in q.get("sections", [])
    )

    return jsonify({
        "status": "ok",
        "filename": safe_name,
        "module": safe_module,
        "quiz_ids": quiz_ids,
        "total_questions": total_q,
    })


@app.route("/api/quizzes/evaluate", methods=["POST"])
def evaluate_answer():
    data = _json_body()
    question = data.get("question", "")
    user_answer = data.get("user_answer", "")
    model_answer = data.get("model_answer", "")

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

    grader_model = resolve_grader_model()

    try:
        import ollama as _ollama
        response = _ollama.chat(
            model=grader_model,
            messages=[{"role": "user", "content": prompt}],
            think=False,  # suppress reasoning tokens (qwen3, gemma4)
            options=GRADER_OPTIONS,
        )
        # Strip any leaked <think>...</think> before JSON-parsing the response.
        raw = strip_think(response["message"]["content"]).strip()

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

        return jsonify({"score": score, "feedback": feedback, "grader": grader_model})

    except Exception as e:
        logger.exception("Evaluation error")
        return jsonify({"error": str(e)}), 500


@app.route("/api/quizzes/<module>/<quiz_id>/questions", methods=["DELETE"])
def delete_questions(module: str, quiz_id: str):
    """
    Remove questions from a quiz JSON file on disk.

    Scoped to the module folder so a quiz id shared across modules edits the
    correct file. A timestamp-free `<name>.json.bak` backup is written before
    the file is overwritten.

    Expects JSON body: { "question_ids": ["TF-3", "MC-7", ...] }

    Removes matching questions from their sections without renumbering.
    Updates section counts. Writes the file back to disk.
    """
    data = _json_body()
    question_ids = data.get("question_ids", [])

    if not question_ids or not isinstance(question_ids, list):
        return jsonify({"error": "question_ids array is required"}), 400

    if _module_dir(module) is None:
        return jsonify({"error": f"Module '{module}' not found"}), 404

    ids_to_remove = set(question_ids)

    # Find the file containing this quiz within the given module only
    target_path = None
    target_data = None
    target_quiz_idx = None

    for fp in _iter_module_deck_files(module):
        try:
            with open(fp) as f:
                file_data = json.load(f)
            for qi, quiz in enumerate(file_data.get("quizzes", [])):
                if quiz.get("id") == quiz_id:
                    target_path = fp
                    target_data = file_data
                    target_quiz_idx = qi
                    break
            if target_path:
                break
        except Exception:
            continue

    if target_path is None or target_data is None or target_quiz_idx is None:
        return jsonify({"error": f"Quiz '{quiz_id}' not found in module '{module}'"}), 404

    quiz = target_data["quizzes"][target_quiz_idx]
    removed = []

    for section in quiz.get("sections", []):
        original = section.get("questions", [])
        filtered = [q for q in original if q.get("id") not in ids_to_remove]
        removed_here = [q.get("id") for q in original if q.get("id") in ids_to_remove]
        removed.extend(removed_here)
        section["questions"] = filtered
        section["count"] = len(filtered)

    if not removed:
        return jsonify({"error": "No matching question IDs found"}), 404

    # Back up the file before overwriting (overwrites any previous .bak)
    try:
        import shutil
        shutil.copy2(str(target_path), str(target_path) + ".bak")
    except Exception as e:
        logger.warning(f"Could not write backup for {target_path}: {e}")

    # Write back to disk
    try:
        with open(target_path, "w", encoding="utf-8") as f:
            json.dump(target_data, f, indent=2, ensure_ascii=False)
            f.write("\n")
    except Exception as e:
        return jsonify({"error": f"Failed to write file: {e}"}), 500

    total_remaining = sum(
        len(s.get("questions", []))
        for s in quiz.get("sections", [])
    )

    return jsonify({
        "status": "ok",
        "removed": removed,
        "remaining": total_remaining,
    })


# ===================================================================
# Main
# ===================================================================

if __name__ == "__main__":
    port = SERVER_PORT
    # The Werkzeug debugger (interactive tracebacks + console) is opt-in only;
    # it must never be on by default because this server is network-reachable.
    debug = os.environ.get("COSMO_DEBUG") == "1"
    print(f"\n  Cosmo API server starting on http://{SERVER_HOST}:{port}")
    print(f"  Uploads directory: {UPLOAD_DIR.resolve()}\n")
    app.run(host=SERVER_HOST, port=port, debug=debug)