#!/usr/bin/env bash
set -euo pipefail

EFFECTIVE_TAILSCALE_AUTHKEY="${TAILSCALE_AUTHKEY_V2:-${TAILSCALE_AUTHKEY:-}}"

if [[ -z "${EFFECTIVE_TAILSCALE_AUTHKEY}" ]]; then
  echo "TAILSCALE_AUTHKEY_V2 (or fallback TAILSCALE_AUTHKEY) is not set; skipping Tailscale startup"
  exit 0
fi

if [[ "${EFFECTIVE_TAILSCALE_AUTHKEY}" == tskey-api-* ]]; then
  echo "Provided Tailscale key looks like an API key (tskey-api-*), not an auth key."
  echo "Create a reusable auth key in Tailscale Admin > Settings > Keys and store it as TAILSCALE_AUTHKEY_V2."
  exit 1
fi

if [[ "${EFFECTIVE_TAILSCALE_AUTHKEY}" != tskey-auth-* ]]; then
  echo "Provided Tailscale key format is unexpected. Expected an auth key starting with tskey-auth-."
  exit 1
fi

if [[ "${EFFECTIVE_TAILSCALE_AUTHKEY}" == *CNTRL-* ]]; then
  echo "Provided Tailscale key appears to be a control/API-style key and is invalid for tailscale up."
  echo "Create a new reusable auth key in Tailscale Admin > Settings > Keys and replace TAILSCALE_AUTHKEY_V2."
  exit 1
fi

if ! command -v tailscaled >/dev/null 2>&1 || ! command -v tailscale >/dev/null 2>&1; then
  echo "Tailscale is not installed yet; run postCreateCommand or execute .devcontainer/install-tailscale.sh"
  exit 0
fi

SOCKET="/var/run/tailscale/tailscaled.sock"
STATE="/var/lib/tailscale/tailscaled.state"
HOSTNAME="${TAILSCALE_HOSTNAME:-codespace-${CODESPACE_NAME:-wrp-lm}}"

if ! pgrep -x tailscaled >/dev/null 2>&1; then
  echo "Starting tailscaled..."
  sudo mkdir -p /var/run/tailscale /var/lib/tailscale
  sudo nohup tailscaled --socket="${SOCKET}" --state="${STATE}" >/tmp/tailscaled.log 2>&1 &
fi

if sudo tailscale --socket="${SOCKET}" ip -4 >/dev/null 2>&1; then
  echo "Tailscale already connected"
  exit 0
fi

echo "Bringing up Tailscale as ${HOSTNAME}..."
sudo tailscale --socket="${SOCKET}" up \
  --authkey="${EFFECTIVE_TAILSCALE_AUTHKEY}" \
  --hostname="${HOSTNAME}" \
  --accept-routes \
  --accept-dns=false

echo "Tailscale is up"
