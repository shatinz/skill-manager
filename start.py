#!/usr/bin/env python3
"""
Unified Agentic Skill Manager — One-Click Launcher

This script starts the FastAPI application using either the installed virtualenv or system Python.
It also auto-seeds initial data on first run if the database is empty.
"""

import os
import sys
import subprocess
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = ROOT_DIR / "backend"

def main():
    print("=" * 60)
    print("  Unified Agentic Skill Manager — Starting Server")
    print("=" * 60)

    # Check for venv python
    home_venv_py = Path("/home/shatix/venv-skm/bin/python3")
    venv_py = BACKEND_DIR / ".venv" / "bin" / "python3"
    tmp_venv_py = Path("/tmp/skm-venv/bin/python3")

    if home_venv_py.exists():
        py_exe = str(home_venv_py)
    elif venv_py.exists():
        py_exe = str(venv_py)
    elif tmp_venv_py.exists():
        py_exe = str(tmp_venv_py)
    else:
        py_exe = sys.executable

    print(f"[*] Python executable: {py_exe}")
    print(f"[*] Working directory: {BACKEND_DIR}")
    print(f"[*] Web UI & API available at: http://localhost:8000")
    print("=" * 60)

    # Set PYTHONPATH
    env = os.environ.copy()
    env["PYTHONPATH"] = str(BACKEND_DIR)

    # Run uvicorn
    cmd = [
        py_exe, "-m", "uvicorn",
        "app.main:app",
        "--host", "0.0.0.0",
        "--port", "8000",
        "--reload"
    ]
    
    try:
        subprocess.run(cmd, cwd=str(BACKEND_DIR), env=env)
    except KeyboardInterrupt:
        print("\n[!] Server stopped by user.")

if __name__ == "__main__":
    main()
