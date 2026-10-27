"""Repeatable local setup. Keeps existing environment files intact."""
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
API = ROOT / "apps" / "api"


def run(command, cwd=ROOT):
    subprocess.run([str(part) for part in command], cwd=cwd, check=True)


def main():
    if sys.version_info < (3, 12):
        raise SystemExit("Python 3.12+ is required. Run: make setup PYTHON=/path/to/python3.12")
    if os.name == "nt":
        raise SystemExit("Use WSL for the documented Makefile workflow.")
    run(["node", "-e", "if (+process.versions.node.split('.')[0] < 22) process.exit(1)"])
    for source, target in [
        (API / ".env.example", API / ".env"),
        (ROOT / "apps/web/.env.example", ROOT / "apps/web/.env.local"),
    ]:
        if not target.exists():
            shutil.copyfile(source, target)
    if not (API / ".venv").exists():
        run([sys.executable, "-m", "venv", API / ".venv"])
    python = API / ".venv/bin/python"
    run([python, "-m", "pip", "install", "-c", "requirements.lock", "-e", ".[dev]"], API)
    run(["npm", "ci"])
    print("Ready. Run 'make api' and 'make web' in separate terminals.")


if __name__ == "__main__":
    main()
