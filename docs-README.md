# Your Study Documents

Place your React/TypeScript study materials here.

## Recommended Sources

### Official Documentation (Free)

1. **TypeScript Handbook**
   - Clone: `git clone https://github.com/microsoft/TypeScript-Website.git`
   - Copy markdown files from `packages/documentation/copy/en/handbook-v2/`

2. **React Documentation**
   - Clone: `git clone https://github.com/reactjs/react.dev.git`
   - Copy markdown files from `src/content/`

3. **TypeScript Deep Dive** (Free Book)
   - Visit: https://basarat.gitbook.io/typescript/
   - Export as PDF from the site

### Your Own Materials

Add any PDFs or markdown files you have:
- Course materials
- Books you own
- Conference talks (PDF format)
- Your own notes

## Organizing Your Docs

You can organize however you like. Examples:

**By Topic:**
```
docs/
├── typescript/
│   ├── handbook.pdf
│   └── advanced-types.md
├── react/
│   ├── official-docs/
│   └── hooks-deep-dive.pdf
└── mui/
    └── component-library.pdf
```

**By Source:**
```
docs/
├── official/
├── books/
├── courses/
└── notes/
```

**Flat (simplest):**
```
docs/
├── typescript-handbook.pdf
├── react-docs.pdf
└── my-notes.md
```

## Quick Start

1. Add your files to this folder
2. Run: `python cli.py ingest --dir docs/`
3. Start studying: `python cli.py interactive`

The system will:
- Automatically detect PDFs and markdown files
- Process them once (cached for future runs)
- Build a searchable knowledge base
- Let you query everything together

## Tips

- **Large PDFs are fine** - the system streams them efficiently
- **Markdown is faster** to process than PDFs
- **Re-indexing**: Use `--force` flag only if you update files
- **Check what's indexed**: `python cli.py list`
