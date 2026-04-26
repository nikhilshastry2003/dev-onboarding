#!/usr/bin/env python3
"""
Universal Onboarding Generator
Reads the repo and generates ONBOARDING.md automatically.
Run: python generate-onboarding.py
Called by: just setup (last step)
"""

import json
import os
import subprocess
from datetime import datetime
from pathlib import Path

try:
    import yaml
    _HAS_YAML = True
except ImportError:
    _HAS_YAML = False


# ─── Readers ─────────────────────────────────────────────────────────────────

def read_file(path: str) -> str:
    p = Path(path)
    return p.read_text(encoding="utf-8") if p.exists() else ""


def read_json(path: str) -> dict:
    p = Path(path)
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}


def read_devsetup() -> dict:
    if not _HAS_YAML:
        return {}
    p = Path(".devsetup.yml")
    if not p.exists():
        return {}
    try:
        with open(p, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}


def get_git_remote() -> str:
    try:
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            capture_output=True, text=True, timeout=5,
        )
        return result.stdout.strip()
    except Exception:
        return ""


def get_recent_contributors() -> list[str]:
    try:
        result = subprocess.run(
            ["git", "log", "--format=%an", "-n", "20"],
            capture_output=True, text=True, timeout=5,
        )
        names = list(dict.fromkeys(result.stdout.strip().splitlines()))
        return names[:5]
    except Exception:
        return []


def detect_stack() -> list[str]:
    """Detect tech stack from files present in the repo."""
    stack = []
    checks = [
        ("package.json",       "Node.js"),
        ("pnpm-lock.yaml",     "pnpm"),
        ("yarn.lock",          "Yarn"),
        ("pyproject.toml",     "Python (uv/poetry)"),
        ("requirements.txt",   "Python (pip)"),
        ("Cargo.toml",         "Rust"),
        ("go.mod",             "Go"),
        ("Gemfile",            "Ruby"),
        ("docker-compose.yml", "Docker Compose"),
        ("Dockerfile",         "Docker"),
    ]
    for filename, label in checks:
        if Path(filename).exists():
            stack.append(label)
    return stack


def get_justfile_recipes() -> list[tuple[str, str]]:
    """Extract recipe names and their first comment from justfile."""
    jf = Path("justfile")
    if not jf.exists():
        return []

    recipes = []
    lines = jf.read_text(encoding="utf-8").splitlines()
    last_comment = ""
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("#"):
            last_comment = stripped.lstrip("# ").strip()
        elif stripped and not stripped.startswith(" ") and ":" in stripped and not stripped.startswith("//"):
            name = stripped.split(":")[0].strip()
            if name and not name.startswith("[") and " " not in name:
                recipes.append((name, last_comment))
                last_comment = ""
        elif not stripped:
            last_comment = ""
    return recipes


def get_node_scripts() -> dict:
    pkg = read_json("package.json")
    return pkg.get("scripts", {})


# ─── Generator ───────────────────────────────────────────────────────────────

def generate() -> str:
    cfg        = read_devsetup()
    pkg        = read_json("package.json")
    pyproject  = read_file("pyproject.toml")
    readme     = read_file("README.md")
    remote     = get_git_remote()
    stack      = detect_stack()
    recipes    = get_justfile_recipes()
    scripts    = get_node_scripts()
    contribs   = get_recent_contributors()

    project_name = (
        cfg.get("name")
        or pkg.get("name")
        or Path.cwd().name
    )
    description = (
        pkg.get("description")
        or cfg.get("description")
        or ""
    )

    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    md = f"""# Welcome to {project_name}!

> Generated: {now}

"""

    if description:
        md += f"{description}\n\n"

    if remote:
        md += f"**Repo:** {remote}\n\n"

    md += "---\n\n"

    # ── Stack ──────────────────────────────────────────────────────────────
    if stack:
        md += "## Tech Stack\n\n"
        for item in stack:
            md += f"- {item}\n"
        md += "\n"

    # ── Getting Started ────────────────────────────────────────────────────
    md += "## Getting Started\n\n"
    md += "If you haven't run bootstrap yet:\n\n"
    md += "```bash\npython bootstrap.py\n```\n\n"
    md += "Then:\n\n"

    next_steps = cfg.get("next_steps", [
        {"run": "just setup"},
        {"read": "ONBOARDING.md"},
        {"run": "just dev"},
    ])
    for step in next_steps:
        if "run" in step:
            md += f"```bash\n{step['run']}\n```\n\n"
        elif "read" in step:
            md += f"Read **{step['read']}** — this file.\n\n"

    # ── Common Commands ────────────────────────────────────────────────────
    if recipes:
        md += "## Common Commands\n\n"
        md += "| Command | What it does |\n"
        md += "|---------|-------------|\n"
        for name, comment in recipes:
            desc = comment if comment else "—"
            md += f"| `just {name}` | {desc} |\n"
        md += "\n"
    elif scripts:
        md += "## Common Commands\n\n"
        md += "| Command | What it does |\n"
        md += "|---------|-------------|\n"
        for name, cmd in list(scripts.items())[:10]:
            md += f"| `pnpm {name}` | `{cmd}` |\n"
        md += "\n"

    # ── Project Structure ──────────────────────────────────────────────────
    md += "## Project Structure\n\n"
    md += "```\n"
    try:
        result = subprocess.run(
            ["find", ".", "-maxdepth", "2",
             "-not", "-path", "*/.git/*",
             "-not", "-path", "*/node_modules/*",
             "-not", "-path", "*/__pycache__/*",
             "-not", "-path", "*/.venv/*",
             "-not", "-name", "*.pyc",
             "-type", "d"],
            capture_output=True, text=True, timeout=5,
        )
        dirs = sorted(result.stdout.strip().splitlines())
        for d in dirs[:20]:
            depth = d.count("/") - 1
            name = Path(d).name
            if name and not name.startswith(".") or depth == 0:
                md += f"{'  ' * max(0, depth)}{name}/\n"
    except Exception:
        md += "(run `find . -maxdepth 2 -type d` to explore)\n"
    md += "```\n\n"

    # ── README excerpt ─────────────────────────────────────────────────────
    if readme:
        lines = [l for l in readme.splitlines() if not l.startswith("# ")]
        excerpt = "\n".join(lines[:30]).strip()
        if excerpt:
            md += "## From the README\n\n"
            md += excerpt + "\n\n"

    # ── Contributors ──────────────────────────────────────────────────────
    if contribs:
        md += "## Recent Contributors\n\n"
        for name in contribs:
            md += f"- {name}\n"
        md += "\n"

    md += "---\n\n"
    md += "*Generated by generate-onboarding.py — re-run after major changes.*\n"

    return md


def main():
    content = generate()
    out = Path("ONBOARDING.md")
    out.write_text(content, encoding="utf-8")
    print(f"Generated {out}")


if __name__ == "__main__":
    main()
