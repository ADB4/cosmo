#!/bin/bash
# Download React Testing Library documentation for Cosmo ingestion
#
# Sources:
#   - testing-library/testing-library-docs (core + React-specific docs)
#   - testing-library/jest-dom (custom matchers)
#   - testing-library/user-event (user interaction simulation)
#
# Usage:
#   chmod +x download-rtl-docs.sh
#   ./download-rtl-docs.sh
#   python -m backend.cli ingest --path artifacts/docs/rtl --force

set -e

BASE_URL="https://raw.githubusercontent.com/testing-library/testing-library-docs/main/docs"
DEST="artifacts/docs/rtl"

mkdir -p "$DEST"

echo "Downloading React Testing Library documentation..."
echo "Target: $DEST"
echo ""

# -----------------------------------------------------------------------
# Core Testing Library concepts (DOM Testing Library)
# These are the foundation -- queries, firing events, async utilities
# -----------------------------------------------------------------------
echo "=== Core Testing Library ==="

# Queries -- this is the critical one you're missing
curl -sL "$BASE_URL/queries/about.mdx"             -o "$DEST/queries-about.md"
curl -sL "$BASE_URL/queries/byrole.mdx"             -o "$DEST/queries-byrole.md"
curl -sL "$BASE_URL/queries/bylabeltext.mdx"        -o "$DEST/queries-bylabeltext.md"
curl -sL "$BASE_URL/queries/byplaceholdertext.mdx"  -o "$DEST/queries-byplaceholdertext.md"
curl -sL "$BASE_URL/queries/bytext.mdx"             -o "$DEST/queries-bytext.md"
curl -sL "$BASE_URL/queries/bydisplayvalue.mdx"     -o "$DEST/queries-bydisplayvalue.md"
curl -sL "$BASE_URL/queries/byalttext.mdx"          -o "$DEST/queries-byalttext.md"
curl -sL "$BASE_URL/queries/bytitle.mdx"            -o "$DEST/queries-bytitle.md"
curl -sL "$BASE_URL/queries/bytestid.mdx"           -o "$DEST/queries-bytestid.md"

echo "  Downloaded: queries (9 files)"

# Async utilities -- waitFor, findBy, etc.
curl -sL "$BASE_URL/dom-testing-library/api-async.mdx"  -o "$DEST/api-async.md"

# Firing events
curl -sL "$BASE_URL/dom-testing-library/api-events.mdx" -o "$DEST/api-events.md"

# Helpers (within, screen, etc.)
curl -sL "$BASE_URL/dom-testing-library/api-helpers.mdx" -o "$DEST/api-helpers.md"

# Configuration
curl -sL "$BASE_URL/dom-testing-library/api-configuration.mdx" -o "$DEST/api-configuration.md"

# Debugging
curl -sL "$BASE_URL/dom-testing-library/api-debugging.mdx" -o "$DEST/api-debugging.md"

echo "  Downloaded: DOM Testing Library API (5 files)"

# -----------------------------------------------------------------------
# React Testing Library specifics
# -----------------------------------------------------------------------
echo ""
echo "=== React Testing Library ==="

# Core API (render, cleanup, act, renderHook)
curl -sL "$BASE_URL/react-testing-library/api.mdx"     -o "$DEST/react-api.md"

# Setup / configuration
curl -sL "$BASE_URL/react-testing-library/setup.mdx"   -o "$DEST/react-setup.md"

# FAQ
curl -sL "$BASE_URL/react-testing-library/faq.mdx"     -o "$DEST/react-faq.md"

# Cheatsheet
curl -sL "$BASE_URL/react-testing-library/cheatsheet.mdx" -o "$DEST/react-cheatsheet.md"

echo "  Downloaded: React Testing Library (4 files)"

# -----------------------------------------------------------------------
# Guides and best practices
# -----------------------------------------------------------------------
echo ""
echo "=== Guides ==="

# Guiding principles
curl -sL "$BASE_URL/guiding-principles.mdx"             -o "$DEST/guiding-principles.md"

# Which query should I use?
curl -sL "$BASE_URL/guide-which-query.mdx"              -o "$DEST/guide-which-query.md"

# Disappearance (testing removal of elements)
curl -sL "$BASE_URL/guide-disappearance.mdx"            -o "$DEST/guide-disappearance.md"

# Appearance and disappearance
curl -sL "$BASE_URL/dom-testing-library/api-accessibility.mdx" -o "$DEST/api-accessibility.md" 2>/dev/null || true

echo "  Downloaded: Guides (3-4 files)"

# -----------------------------------------------------------------------
# Examples
# -----------------------------------------------------------------------
echo ""
echo "=== Examples ==="

curl -sL "$BASE_URL/example-input-event.mdx"           -o "$DEST/example-input-event.md"
curl -sL "$BASE_URL/example-update-props.mdx"          -o "$DEST/example-update-props.md"
curl -sL "$BASE_URL/example-react-context.mdx"         -o "$DEST/example-react-context.md"
curl -sL "$BASE_URL/example-react-hooks-useReducer.mdx" -o "$DEST/example-react-hooks-useReducer.md"
curl -sL "$BASE_URL/example-react-router.mdx"          -o "$DEST/example-react-router.md"
curl -sL "$BASE_URL/example-react-transition-group.mdx" -o "$DEST/example-react-transition-group.md"

echo "  Downloaded: Examples (6 files)"

# -----------------------------------------------------------------------
# user-event (separate repo -- the modern way to simulate user actions)
# -----------------------------------------------------------------------
echo ""
echo "=== user-event ==="

UE_URL="https://raw.githubusercontent.com/testing-library/testing-library-docs/main/docs/user-event"

curl -sL "$UE_URL/intro.mdx"       -o "$DEST/user-event-intro.md"
curl -sL "$UE_URL/setup.mdx"       -o "$DEST/user-event-setup.md"
curl -sL "$UE_URL/utility.mdx"     -o "$DEST/user-event-utility.md"
curl -sL "$UE_URL/convenience.mdx" -o "$DEST/user-event-convenience.md"
curl -sL "$UE_URL/clipboard.mdx"   -o "$DEST/user-event-clipboard.md"
curl -sL "$UE_URL/keyboard.mdx"    -o "$DEST/user-event-keyboard.md"
curl -sL "$UE_URL/pointer.mdx"     -o "$DEST/user-event-pointer.md"

echo "  Downloaded: user-event (7 files)"

# -----------------------------------------------------------------------
# jest-dom custom matchers (toBeInTheDocument, toHaveTextContent, etc.)
# -----------------------------------------------------------------------
echo ""
echo "=== jest-dom ==="

JD_URL="https://raw.githubusercontent.com/testing-library/jest-dom/main"

curl -sL "$JD_URL/README.md" -o "$DEST/jest-dom-readme.md"

echo "  Downloaded: jest-dom (1 file)"

# -----------------------------------------------------------------------
# Summary
# -----------------------------------------------------------------------
echo ""
echo "=== Done ==="
TOTAL=$(ls -1 "$DEST"/*.md 2>/dev/null | wc -l | tr -d ' ')
echo "Downloaded $TOTAL files to $DEST"
echo ""
echo "Next steps:"
echo "  python -m backend.cli ingest --path $DEST --force"