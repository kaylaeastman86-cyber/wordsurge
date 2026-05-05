#!/usr/bin/env bash
# Sets up the daily 6 AM cron job for the House of Lushella marketing workflow.
# Usage: bash setup_cron.sh
# Requires: ANTHROPIC_API_KEY set in your shell environment before running.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PYTHON="${SCRIPT_DIR}/.venv/bin/python"
ORCHESTRATOR="${SCRIPT_DIR}/orchestrator.py"
LOG_DIR="${SCRIPT_DIR}/logs"
LOG_FILE="${LOG_DIR}/workflow.log"
CRON_TAG="# house-of-lushella-workflow"

# ── Preflight checks ─────────────────────────────────────────────────────────

if [[ -z "${ANTHROPIC_API_KEY:-}" ]]; then
  echo "ERROR: ANTHROPIC_API_KEY is not set."
  echo "Export it before running this script:"
  echo "  export ANTHROPIC_API_KEY=sk-ant-..."
  exit 1
fi

if [[ ! -f "${VENV_PYTHON}" ]]; then
  echo "Virtual environment not found at ${VENV_PYTHON}"
  echo "Creating it now..."
  python3 -m venv "${SCRIPT_DIR}/.venv"
  "${SCRIPT_DIR}/.venv/bin/pip" install --quiet -r "${SCRIPT_DIR}/requirements.txt"
  echo "Virtual environment ready."
fi

mkdir -p "${LOG_DIR}"

# ── Build cron line ───────────────────────────────────────────────────────────

# Runs at 06:00 every day; ANTHROPIC_API_KEY is baked in at install time.
CRON_LINE="0 6 * * * ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY} ${VENV_PYTHON} ${ORCHESTRATOR} >> ${LOG_FILE} 2>&1 ${CRON_TAG}"

# ── Install cron job (idempotent) ─────────────────────────────────────────────

# Remove any existing entry for this workflow, then append the new one.
( crontab -l 2>/dev/null | grep -v "${CRON_TAG}" ; echo "${CRON_LINE}" ) | crontab -

echo ""
echo "Cron job installed successfully."
echo ""
echo "Schedule  : 06:00 AM daily"
echo "Command   : ${VENV_PYTHON} ${ORCHESTRATOR}"
echo "Log file  : ${LOG_FILE}"
echo ""
echo "Verify with:  crontab -l"
echo "Run now   :  ${VENV_PYTHON} ${ORCHESTRATOR} --now"
echo ""
