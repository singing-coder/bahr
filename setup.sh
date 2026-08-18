#!/usr/bin/env bash
# One-shot reproducible setup: creates .venv, installs pinned deps,
# installs taqti in editable mode, runs the full test gate.
set -euo pipefail
cd "$(dirname "$0")"

PYTHON="${PYTHON:-python3}"
"$PYTHON" -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate

python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -e .

echo
echo "== running test gate =="
pytest tests/ -q
echo
echo "Setup complete. Activate with:  source .venv/bin/activate"
echo "Web app:                        streamlit run webapp/app.py"
