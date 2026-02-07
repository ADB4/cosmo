# Quick Reference Card

## Installation (One-time)
```bash
# 1. Install Ollama
brew install ollama

# 2. Extract project
unzip react-ts-rag-study.zip
cd react-ts-rag-study

# 3. Run setup script
./setup.sh

# OR manually:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Pull Models (One-time)
```bash
ollama pull nomic-embed-text      # Required - 274MB
ollama pull qwen2.5-coder:7b      # Recommended - 4.7GB
ollama pull llama3.1:8b           # Optional - 4.7GB
```

## Daily Usage

### Start Session
```bash
cd react-ts-rag-study
source venv/bin/activate
python cli.py interactive
```

### Common Commands

| Command | Description |
|---------|-------------|
| `python cli.py ingest --path <file>` | Add single document |
| `python cli.py ingest --dir docs/` | Add all docs in folder |
| `python cli.py ask -q "question"` | Ask one question |
| `python cli.py interactive` | Interactive mode (best for study) |
| `python cli.py list` | Show indexed documents |

### Interactive Mode Commands

While in interactive mode:
- Just type your question
- `mode deep` - Switch to slower, better model
- `mode quick` - Switch back to fast model
- `stats` - Show what's indexed
- `quit` - Exit

## Model Modes

| Mode | Speed | Use For |
|------|-------|---------|
| quick | Fast | Default - most questions |
| deep | Slow | Complex explanations |
| general | Fast | Non-code questions |
| fast | Fastest | Quick lookups |

## File Structure
```
react-ts-rag-study/
├── cli.py              # Main interface
├── document_processor.py   # Core logic
├── setup.sh            # Setup script
├── docs/               # YOUR DOCUMENTS GO HERE
│   ├── typescript-handbook.pdf
│   └── react-docs.md
└── chroma_db/          # Database (auto-created)
```

## Troubleshooting

**"Model not found"**
```bash
ollama pull <model-name>
```

**"Connection refused"**
```bash
ollama serve  # Start in separate terminal
```

**"No module named..."**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

**Slow ingestion**
- Normal for first time
- Large PDFs take 5-10 min
- Only happens once per file

## Example Study Session
```bash
# Start session
cd react-ts-rag-study
source venv/bin/activate
python cli.py interactive

# In interactive mode:
[quick] Question: What's the difference between type and interface?
# ... answer ...

[quick] Question: mode deep
Switched to deep mode

[deep] Question: Explain discriminated unions with examples
# ... detailed answer ...

[deep] Question: quit
Goodbye!
```

## Memory Usage (M2 Pro 32GB)
- Quick mode: ~6GB
- Deep mode: ~10GB
- Plenty of room for browser/IDE

## Getting Documentation

**TypeScript:**
```bash
git clone --depth 1 https://github.com/microsoft/TypeScript-Website.git
cp -r TypeScript-Website/packages/documentation/copy/en/handbook-v2/*.md docs/
```

**React:**
```bash
git clone --depth 1 https://github.com/reactjs/react.dev.git
cp react.dev/src/content/learn/*.md docs/
```

**Or just copy your PDFs:**
```bash
cp ~/Downloads/your-book.pdf docs/
```

## Tips

- Use interactive mode for study sessions
- Index documents once, query many times
- Start with quick mode, switch to deep when stuck
- Markdown files process faster than PDFs
- Add more documents anytime - they're cached

---
Save this card for reference!
