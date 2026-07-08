#!/usr/bin/env bash
set -uo pipefail

REPO_DIR="/mnt/c/work/projects2026/devops"
LOG_DIR="${HOME}/logs"
LOG_FILE="${LOG_DIR}/git-upd.log"

mkdir -p "${LOG_DIR}"

{
  echo "=== $(date -Iseconds) ==="
  /mnt/c/Windows/System32/cmd.exe /c "cd /d C:\\work\\projects2026\\devops && git-upd.cmd"
  echo "exit: $?"
} >> "${LOG_FILE}" 2>&1
