#!/usr/bin/env bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="/home/shatix/venv-skm"

echo "======================================================"
echo "  Unified Agentic Skill Manager"
echo "  A Living Ecosystem for AI Agent Capabilities"
echo "======================================================"

if [ ! -d "$VENV_DIR" ]; then
    echo "[*] Creating virtual environment at $VENV_DIR..."
    python3 -m venv "$VENV_DIR"
    "$VENV_DIR/bin/pip" install --upgrade pip
    "$VENV_DIR/bin/pip" install -r "$DIR/backend/requirements.txt"
fi

echo "[*] Starting FastAPI Server on http://localhost:8000..."
cd "$DIR/backend"
exec "$VENV_DIR/bin/uvicorn" app.main:app --host 0.0.0.0 --port 8000 --reload
