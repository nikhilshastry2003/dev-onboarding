# justfile — Universal task runner template
# Copy this to any repo and fill in the recipes below.
# Run: just setup (first time) | just dev (daily) | just sync (after git pull)
#
# Standard recipe names (keep these consistent across all your repos):
#   setup   — first-time full install
#   sync    — re-sync after git pull
#   dev     — start the development environment
#   test    — run tests
#   check   — lint / typecheck
#   build   — production build
#   clean   — wipe generated artifacts

# ─── Setup & Sync ─────────────────────────────────────────────────────────────

# Full first-time setup
setup:
    #!/usr/bin/env bash
    set -euo pipefail
    echo "===================================="
    echo "  Setting up {{PROJECT_NAME}}"
    echo "===================================="

    # TODO: replace with your install steps, e.g:
    # echo "[1/3] Installing Node dependencies..."
    # pnpm install

    # echo "[2/3] Installing Python dependencies..."
    # uv sync

    # echo "[3/3] Generating onboarding docs..."
    # python generate-onboarding.py

    echo "===================================="
    echo "  Done! Read ONBOARDING.md to start."
    echo "===================================="

# Re-sync after git pull
sync:
    #!/usr/bin/env bash
    set -euo pipefail
    echo "Syncing..."

    # TODO: replace with your sync steps, e.g:
    # pnpm install
    # uv sync

    echo "Done."

# ─── Development ──────────────────────────────────────────────────────────────

# Start the dev environment
dev:
    # TODO: replace with your dev command, e.g:
    # pnpm dev
    # uvicorn main:app --reload
    echo "Replace this with your dev command in justfile"

# ─── Quality ──────────────────────────────────────────────────────────────────

# Run tests
test:
    # TODO: replace with your test command, e.g:
    # pnpm test
    # uv run pytest
    echo "Replace this with your test command in justfile"

# Lint + typecheck
check:
    # TODO: replace with your check command, e.g:
    # pnpm typecheck
    # uv run ruff check .
    echo "Replace this with your check command in justfile"

# ─── Build & Clean ────────────────────────────────────────────────────────────

# Production build
build:
    # TODO: replace with your build command, e.g:
    # pnpm build
    echo "Replace this with your build command in justfile"

# Clean generated artifacts
clean:
    # TODO: replace with your clean command, e.g:
    # rm -rf dist/ .next/ __pycache__/
    echo "Replace this with your clean command in justfile"
