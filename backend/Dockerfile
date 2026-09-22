FROM python:3.12-slim

WORKDIR /app

# Install system deps for chromadb and pymupdf
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./backend/
COPY decks/ ./decks/

# Create directories the app expects
RUN mkdir -p uploads chroma_db docs

EXPOSE 5174

# One worker on purpose: the DocumentProcessor (Chroma client, Marker
# extractor, cached grader choice) is process state. gthread keeps SSE
# streaming responsive; the long timeout covers slow ingests and generations.
CMD ["gunicorn", "-w", "1", "--threads", "8", "--worker-class", "gthread", "--timeout", "900", "-b", "0.0.0.0:5174", "backend.server:app"]