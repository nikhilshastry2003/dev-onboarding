#!/usr/bin/env python3
"""
Universal Bootstrap Script
Reads .devsetup.yml and installs whatever the project needs.
Run this FIRST: python bootstrap.py
"""

import shutil
import subprocess
import sys
import os
import platform

try:
    import yaml
    _HAS_YAML = True
except ImportError:
    _HAS_YAML = False

SYSTEM = platform.system()  # "Windows", "Linux", "Darwin"

CONFIG_FILE = ".devsetup.yml"

# ─── Defaults if no config file ──────────────────────────────────────────────

DEFAULT_REQUIRED = ["git", "node"]
DEFAULT_INSTALL  = ["just", "pnpm", "uv"]
DEFAULT_NEXT_STEPS = [
    {"run": "just setup"},
    {"read": "ONBOARDING.md"},
    {"run": "just dev"},
]

# ─── Installers ──────────────────────────────────────────────────────────────

def install_just():
    if SYSTEM == "Windows":
        if find("winget"):
            return run_command(
                ["winget", "install", "--id", "Casey.Just", "-e", "--accept-source-agreements"],
                "Install just via winget",
            )
        print("  [ERROR] winget not found. Install just manually: https://just.systems/man/en/installation.html")
        return False
    elif SYSTEM == "Darwin":
        if find("brew"):
            return run_command(["brew", "install", "just"], "Install just via brew")
    else:
        if find("snap"):
            return run_command(["sudo", "snap", "install", "just", "--stable", "--classic"], "Install just via snap")
        elif find("brew"):
            return run_command(["brew", "install", "just"], "Install just via brew")
    if find("cargo"):
        return run_command(["cargo", "install", "just"], "Install just via cargo")
    print("  [ERROR] No package manager found. Install just manually: https://just.systems/man/en/installation.html")
    return False


def install_pnpm():
    if not find("node"):
        print("  [SKIP] pnpm install skipped — node not found")
        return False
    return run_command(["npm", "install", "-g", "pnpm@latest"], "Install pnpm via npm")


def install_uv():
    if SYSTEM == "Windows":
        return run_command(
            ["powershell", "-c", "irm https://astral.sh/uv/install.ps1 | iex"],
            "Install uv",
        )
    return run_command(
        ["sh", "-c", "curl -LsSf https://astral.sh/uv/install.sh | sh"],
        "Install uv",
    )


def install_docker():
    print("  [INFO] Docker must be installed manually: https://docs.docker.com/get-docker/")
    return False


INSTALLERS = {
    "just":   install_just,
    "pnpm":   install_pnpm,
    "uv":     install_uv,
    "docker": install_docker,
}

# ─── Helpers ─────────────────────────────────────────────────────────────────

def run_command(cmd, description):
    print(f"  -> {description}...")
    try:
        subprocess.run(cmd, check=True)
        print(f"  [OK] {description} complete")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  [FAIL] {description} failed: {e}")
        return False
    except FileNotFoundError:
        print(f"  [FAIL] {description} — command not found: {cmd[0]}")
        return False


def find(cmd):
    return shutil.which(cmd) is not None


def get_version(cmd):
    try:
        path = shutil.which(cmd) or cmd
        result = subprocess.run([path, "--version"], capture_output=True, text=True, timeout=10)
        line = result.stdout.strip().split("\n")[0]
        return f"{cmd} {line}" if cmd not in line.lower() else line
    except Exception:
        return f"{cmd} (version unknown)"


def add_to_path(directory):
    if directory not in os.environ.get("PATH", ""):
        os.environ["PATH"] = f"{directory}{os.pathsep}{os.environ['PATH']}"

# ─── Config loader ───────────────────────────────────────────────────────────

def load_config():
    if not os.path.exists(CONFIG_FILE):
        print(f"  [INFO] No {CONFIG_FILE} found — using defaults")
        return {
            "name": "project",
            "required": DEFAULT_REQUIRED,
            "install": DEFAULT_INSTALL,
            "next_steps": DEFAULT_NEXT_STEPS,
        }

    if not _HAS_YAML:
        print(f"  [WARN] pyyaml not installed — can't read {CONFIG_FILE}, using defaults")
        print("         Run: pip install pyyaml")
        return {
            "name": "project",
            "required": DEFAULT_REQUIRED,
            "install": DEFAULT_INSTALL,
            "next_steps": DEFAULT_NEXT_STEPS,
        }

    with open(CONFIG_FILE, encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}

    # Normalise: install list can be strings or dicts
    raw_install = cfg.get("install", DEFAULT_INSTALL)
    install = [i if isinstance(i, str) else list(i.keys())[0] for i in raw_install]

    return {
        "name":       cfg.get("name", "project"),
        "required":   cfg.get("required", DEFAULT_REQUIRED),
        "install":    install,
        "next_steps": cfg.get("next_steps", DEFAULT_NEXT_STEPS),
    }

# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    cfg = load_config()

    print("=" * 50)
    print(f"Bootstrap — {cfg['name']}  ({SYSTEM})")
    print("=" * 50)
    print()
    print("Checking prerequisites...")
    print()

    errors = []

    # 1. Check required tools
    for tool in cfg["required"]:
        if not find(tool):
            print(f"  [ERROR] {tool} not found — install it manually, then re-run bootstrap.py")
            errors.append(tool)
        else:
            print(f"  [OK] {get_version(tool)}")

    if errors:
        print()
        print(f"[ABORT] Missing required tools: {', '.join(errors)}")
        sys.exit(1)

    print()

    # 2. Auto-install optional tools
    for tool in cfg["install"]:
        if find(tool):
            print(f"  [OK] {get_version(tool)}")
            continue

        print(f"  [WARN] {tool} not found — installing...")
        installer = INSTALLERS.get(tool)
        if installer:
            installer()
            # Add common install locations to PATH for this session
            home = os.path.expanduser("~")
            add_to_path(os.path.join(home, ".local", "bin"))
            add_to_path(os.path.join(home, ".cargo", "bin"))
        else:
            print(f"  [WARN] No auto-installer for '{tool}' — install it manually")

    # 3. Final check
    print()
    missing = [t for t in cfg["install"] if not find(t)]
    if missing:
        print(f"[WARN] Still missing: {', '.join(missing)}")
        print("You may need to restart your terminal for PATH changes to take effect.")
        print("Then re-run: python bootstrap.py")
        sys.exit(1)

    # 4. Success
    print("=" * 50)
    print("All prerequisites ready!")
    print("=" * 50)
    print()
    print("Next steps:")
    print()
    for step in cfg["next_steps"]:
        if "run" in step:
            print(f"  Run:  {step['run']}")
        elif "read" in step:
            print(f"  Read: {step['read']}")
    print()


if __name__ == "__main__":
    main()
