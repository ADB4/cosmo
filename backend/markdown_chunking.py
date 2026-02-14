"""
Improved markdown chunking for Cosmo's DocumentProcessor.

Replaces the existing ingest_markdown method and adds:
  1. Heading-hierarchy-aware section parsing
  2. Rich metadata (heading text, heading level, heading breadcrumb path)
  3. Section-boundary-aware overlap (overlap pulls from the same section,
     never bleeds across heading boundaries)

Drop-in replacements for DocumentProcessor methods.
"""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class MarkdownSection:
    """A logical section extracted from a markdown file."""
    heading: str                     # e.g. "## Props and State"
    heading_text: str                # e.g. "Props and State"
    heading_level: int               # e.g. 2
    body: str                        # The text content under this heading
    breadcrumb: List[str]            # e.g. ["React Basics", "Components", "Props and State"]

    @property
    def breadcrumb_path(self) -> str:
        """Slash-separated breadcrumb for metadata storage."""
        return " > ".join(self.breadcrumb)


@dataclass
class ChunkWithMetadata:
    """A text chunk with all the metadata needed for ChromaDB storage."""
    text: str
    metadata: Dict[str, str]
    # metadata keys: source, file_hash, doc_type, heading, heading_level,
    #                breadcrumb, chunk_index_in_section, section_index


# ---------------------------------------------------------------------------
# Section parser
# ---------------------------------------------------------------------------

def parse_markdown_sections(content: str) -> List[MarkdownSection]:
    """
    Parse markdown into sections split by headings, preserving hierarchy.

    Handles:
    - ATX headings (# through ######)
    - Content before the first heading (assigned level 0, heading "Introduction")
    - Nested heading breadcrumbs (an h3 under an h2 under an h1 gets all three)

    Does NOT handle:
    - Setext-style headings (underline with === or ---)
    - Headings inside fenced code blocks (they'll be mis-detected; rare in docs)
    """
    lines = content.split("\n")
    heading_pattern = re.compile(r"^(#{1,6})\s+(.+)$")

    # First pass: identify all heading positions
    heading_positions: List[Tuple[int, int, str]] = []  # (line_idx, level, text)
    in_code_block = False

    for i, line in enumerate(lines):
        # Track fenced code blocks to skip headings inside them
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue

        match = heading_pattern.match(line)
        if match:
            level = len(match.group(1))
            text = match.group(2).strip()
            heading_positions.append((i, level, text))

    # Second pass: extract sections with body text
    sections: List[MarkdownSection] = []

    # Handle content before first heading
    first_heading_line = heading_positions[0][0] if heading_positions else len(lines)
    preamble = "\n".join(lines[:first_heading_line]).strip()
    if preamble:
        sections.append(MarkdownSection(
            heading="",
            heading_text="Introduction",
            heading_level=0,
            body=preamble,
            breadcrumb=["Introduction"],
        ))

    # Build breadcrumb stack: tracks the most recent heading at each level
    # e.g. breadcrumb_stack[1] = "Getting Started", breadcrumb_stack[2] = "Installation"
    breadcrumb_stack: Dict[int, str] = {}

    for idx, (line_num, level, text) in enumerate(heading_positions):
        # Determine where this section's body ends
        if idx + 1 < len(heading_positions):
            next_line = heading_positions[idx + 1][0]
        else:
            next_line = len(lines)

        body = "\n".join(lines[line_num + 1 : next_line]).strip()

        # Update breadcrumb: set this level, clear anything deeper
        breadcrumb_stack[level] = text
        for deeper_level in list(breadcrumb_stack.keys()):
            if deeper_level > level:
                del breadcrumb_stack[deeper_level]

        # Build ordered breadcrumb from the stack
        breadcrumb = [
            breadcrumb_stack[lvl]
            for lvl in sorted(breadcrumb_stack.keys())
        ]

        sections.append(MarkdownSection(
            heading="#" * level + " " + text,
            heading_text=text,
            heading_level=level,
            body=body,
            breadcrumb=breadcrumb,
        ))

    return sections


# ---------------------------------------------------------------------------
# Section-aware chunking with overlap
# ---------------------------------------------------------------------------

def chunk_section(
    section: MarkdownSection,
    max_size: int = 800,
    overlap: int = 150,
) -> List[str]:
    """
    Chunk a single section's body text, respecting paragraph boundaries.
    Overlap is applied only within the section (never across headings).

    Returns a list of chunk strings. The heading line is prepended to the
    FIRST chunk so the embedding captures what section the content belongs to.
    """
    body = section.body
    if not body.strip():
        return []

    paragraphs = body.split("\n\n")
    raw_chunks: List[str] = []
    current = ""

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        if len(current) + len(para) + 2 <= max_size:
            current += ("" if not current else "\n\n") + para
        else:
            if current:
                raw_chunks.append(current)
            # Handle paragraphs longer than max_size
            if len(para) > max_size:
                words = para.split()
                temp = ""
                for word in words:
                    if len(temp) + len(word) + 1 <= max_size:
                        temp += ("" if not temp else " ") + word
                    else:
                        if temp:
                            raw_chunks.append(temp)
                        temp = word
                current = temp
            else:
                current = para

    if current:
        raw_chunks.append(current)

    if not raw_chunks:
        return []

    # Apply overlap: prepend tail of previous chunk to current chunk
    overlapped: List[str] = []
    for i, chunk in enumerate(raw_chunks):
        if i == 0:
            # Prepend the heading to the first chunk for embedding context
            prefix = section.heading + "\n\n" if section.heading else ""
            overlapped.append(prefix + chunk)
        else:
            prev_text = raw_chunks[i - 1]
            # Take the last `overlap` characters, snapped to a word boundary
            tail = prev_text[-overlap:]
            first_space = tail.find(" ")
            if first_space != -1:
                tail = tail[first_space + 1 :]
            overlapped.append(f"[...] {tail}\n\n{chunk}")

    return overlapped


# ---------------------------------------------------------------------------
# Top-level function: parse + chunk + attach metadata
# ---------------------------------------------------------------------------

def chunk_markdown_file(
    content: str,
    filename: str,
    file_hash: str,
    max_size: int = 800,
    overlap: int = 150,
) -> List[ChunkWithMetadata]:
    """
    Full pipeline: parse markdown into sections, chunk each section,
    and attach rich metadata to every chunk.

    Returns a list of ChunkWithMetadata ready for embedding and ChromaDB storage.
    """
    sections = parse_markdown_sections(content)
    results: List[ChunkWithMetadata] = []
    global_chunk_idx = 0

    for section_idx, section in enumerate(sections):
        chunks = chunk_section(section, max_size=max_size, overlap=overlap)

        for chunk_in_section_idx, chunk_text in enumerate(chunks):
            results.append(ChunkWithMetadata(
                text=chunk_text,
                metadata={
                    "source": filename,
                    "file_hash": file_hash,
                    "doc_type": "markdown",
                    "heading": section.heading_text,
                    "heading_level": str(section.heading_level),
                    "breadcrumb": section.breadcrumb_path,
                    "chunk_index_in_section": str(chunk_in_section_idx),
                    "section_index": str(section_idx),
                },
            ))
            global_chunk_idx += 1

    return results