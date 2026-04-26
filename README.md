# Dev Onboarding — Universal Setup System

Drop these 4 files into any repo. A new dev runs one command and is ready.

```
python bootstrap.py
```

That's it.

---

## What happens

```
python bootstrap.py
       ↓
installs required tools (git, node, just, pnpm, uv — whatever is listed)
       ↓
just setup
       ↓
installs project dependencies
generates ONBOARDING.md  ← auto-generated from README, package.json, justfile etc.
       ↓
just dev  ← project is running
```

---

## Files

| File | What it is | Do you edit it? |
|------|-----------|-----------------|
| `bootstrap.py` | Installs system tools | No |
| `.devsetup.yml` | Config — what tools to install | **Yes** |
| `justfile` | Task runner — setup/dev/test commands | **Yes** |
| `generate-onboarding.py` | Auto-generates ONBOARDING.md | No |

---

## What to customize

### 1. `.devsetup.yml`
Tell bootstrap what tools your project needs:

```yaml
name: your-project-name

required:
  - git
  - node        # remove if not a Node project
  # - docker    # add if needed

install:
  - just        # remove if not using justfile
  - pnpm        # remove if not a Node project
  - uv          # remove if not a Python project
```

### 2. `justfile`
Fill in your actual commands wherever you see `# TODO`:

```
setup:   → pnpm install && uv sync && python generate-onboarding.py
sync:    → pnpm install && uv sync
dev:     → pnpm dev  (or uvicorn main:app --reload, etc.)
test:    → pnpm test  (or uv run pytest, etc.)
check:   → pnpm typecheck  (or ruff check, etc.)
build:   → pnpm build
clean:   → rm -rf dist/ __pycache__/
```

---

## The generated ONBOARDING.md

After `just setup` runs, `generate-onboarding.py` reads the repo and creates `ONBOARDING.md` automatically. It reads:

- `README.md` — project description
- `package.json` — project name, scripts
- `pyproject.toml` — Python project info
- `justfile` — available commands
- Git history — recent contributors
- Directory structure — folder layout

The result is a doc that tells a new dev: what the project does, how it's structured, and what commands to use. **No manual writing needed.**

---

## If you're NOT using Claude / any LLM

Right now `bootstrap.py` installs tools and `just setup` runs the commands you define. This works fine without any AI.

**But** if you want fully automatic setup — where the system *reads your docs and figures out the setup steps itself* without you having to fill in `.devsetup.yml` or `justfile` — you need an AI layer.

### Option A: Use Claude (current approach)
Just install Claude Code CLI. Bootstrap can call `claude` to read `README.md`, `package.json`, `pyproject.toml`, `docker-compose.yml`, `Makefile`, any setup docs — and have it figure out and run the setup commands automatically. No config files needed at all.

### Option B: Use a local LLM (no Claude subscription)
Replace the `claude` CLI call in bootstrap with any local model via `ollama` or `llama.cpp`:
- Install `ollama` + pull a model (e.g. `ollama pull llama3`)
- In `bootstrap.py`, replace `subprocess.run(["claude", ...])` with `subprocess.run(["ollama", "run", "llama3", ...])`

### Option C: RAG-based setup (no LLM at all)
Build a small Python script that:
1. Reads `README.md`, `package.json`, `pyproject.toml`, `Makefile`, `docker-compose.yml`, `.env.example`
2. Extracts setup commands using regex patterns (`npm install`, `pip install`, `docker compose up`, etc.)
3. Runs them in order

This is deterministic — no AI needed. Covers 80% of repos since most README files have a "Getting Started" section with explicit commands.

**The key file to modify for any of these options: `bootstrap.py`** — specifically the `run_setup_steps()` function (add it after the tool installation section).

---

## Quick start for your repo

```bash
# 1. Copy these 4 files to your repo root
# 2. Edit .devsetup.yml — set your project name, tools
# 3. Edit justfile — fill in setup/dev/test commands
# 4. Commit them
# 5. New dev clones repo and runs:
python bootstrap.py
```
