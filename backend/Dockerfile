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

CMD ["python", "-m", "backend.server"]