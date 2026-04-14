#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MCP_FILE="${ROOT_DIR}/.vscode/mcp.json"
TEMPLATE_FILE="${ROOT_DIR}/.vscode/mcp.template.json"

if [[ -z "${SATURN_API_KEY:-}" ]]; then
  echo "SATURN_API_KEY is not set; skipping MCP auth hydration"
  exit 0
fi

if [[ ! -f "${MCP_FILE}" ]]; then
  echo "No .vscode/mcp.json found; skipping MCP auth hydration"
  exit 0
fi

if [[ ! -f "${TEMPLATE_FILE}" ]]; then
  cp "${MCP_FILE}" "${TEMPLATE_FILE}"
fi

if ! grep -q '\${env:SATURN_API_KEY}' "${TEMPLATE_FILE}"; then
  echo "Template missing env placeholder; skipping MCP auth hydration"
  exit 0
fi

awk -v key="${SATURN_API_KEY}" '{ gsub(/\$\{env:SATURN_API_KEY\}/, key); print }' "${TEMPLATE_FILE}" > "${MCP_FILE}"

git -C "${ROOT_DIR}" update-index --skip-worktree .vscode/mcp.json >/dev/null 2>&1 || true

echo "Hydrated .vscode/mcp.json with startup SATURN_API_KEY"
