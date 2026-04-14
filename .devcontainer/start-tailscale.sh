#!/usr/bin/env bash
set -euo pipefail

EFFECTIVE_TAILSCALE_AUTHKEY="${TAILSCALE_AUTHKEY_V2:-${TAILSCALE_AUTHKEY:-}}"
SOCKET="/var/run/tailscale/tailscaled.sock"
STATE="/var/lib/tailscale/tailscaled.state"
HOSTNAME="${TAILSCALE_HOSTNAME:-codespace-${CODESPACE_NAME:-wrp-lm}}"
UP_TIMEOUT="${TAILSCALE_UP_TIMEOUT:-45s}"
MAX_LOGIN_ATTEMPTS="${TAILSCALE_LOGIN_ATTEMPTS:-3}"
LOGIN_RETRY_DELAY_SECONDS="${TAILSCALE_LOGIN_RETRY_DELAY_SECONDS:-5}"
CONTROLPLANE_URL="${TAILSCALE_CONTROLPLANE_URL:-https://controlplane.tailscale.com/key?v=133}"
CONTROLPLANE_WAIT_SECONDS="${TAILSCALE_CONTROLPLANE_WAIT_SECONDS:-90}"
CONTROLPLANE_CHECK_INTERVAL_SECONDS="${TAILSCALE_CONTROLPLANE_CHECK_INTERVAL_SECONDS:-5}"

can_reach_controlplane() {
  curl -4fsS --max-time 5 "${CONTROLPLANE_URL}" >/dev/null 2>&1 || \
    curl -fsS --max-time 5 "${CONTROLPLANE_URL}" >/dev/null 2>&1
}

if ! command -v tailscaled >/dev/null 2>&1 || ! command -v tailscale >/dev/null 2>&1; then
  echo "Tailscale is not installed yet; run postCreateCommand or execute .devcontainer/install-tailscale.sh"
  exit 0
fi

if ! pgrep -x tailscaled >/dev/null 2>&1; then
  echo "Starting tailscaled..."
  sudo mkdir -p /var/run/tailscale /var/lib/tailscale
  sudo nohup tailscaled --socket="${SOCKET}" --state="${STATE}" >/tmp/tailscaled.log 2>&1 &
fi

if [[ -z "${EFFECTIVE_TAILSCALE_AUTHKEY}" ]]; then
  echo "TAILSCALE_AUTHKEY_V2 is not set (or is empty); tailscaled is running but login is skipped"
  exit 0
fi

if [[ "${EFFECTIVE_TAILSCALE_AUTHKEY}" == tskey-api-* ]]; then
  echo "Provided Tailscale key looks like an API key (tskey-api-*), not an auth key."
  echo "Create a reusable auth key in Tailscale Admin > Settings > Keys and store it as TAILSCALE_AUTHKEY_V2."
  exit 0
fi

if [[ "${EFFECTIVE_TAILSCALE_AUTHKEY}" != tskey-auth-* ]]; then
  echo "Provided Tailscale key format is unexpected. Expected an auth key starting with tskey-auth-."
  exit 0
fi

if sudo tailscale --socket="${SOCKET}" ip -4 >/dev/null 2>&1; then
  echo "Tailscale already connected"
  exit 0
fi

echo "Checking Tailscale control-plane reachability..."
waited=0
while ! can_reach_controlplane; do
  if [[ "${waited}" -ge "${CONTROLPLANE_WAIT_SECONDS}" ]]; then
    echo "controlplane.tailscale.com is still unreachable after ${CONTROLPLANE_WAIT_SECONDS}s"
    echo "Skipping tailscale up for now; startup will retry on next container start"
    exit 1
  fi
  echo "Control plane not reachable yet; retrying in ${CONTROLPLANE_CHECK_INTERVAL_SECONDS}s..."
  sleep "${CONTROLPLANE_CHECK_INTERVAL_SECONDS}"
  waited=$((waited + CONTROLPLANE_CHECK_INTERVAL_SECONDS))
done

echo "Bringing up Tailscale as ${HOSTNAME}..."
attempt=1
while [[ "${attempt}" -le "${MAX_LOGIN_ATTEMPTS}" ]]; do
  echo "tailscale up attempt ${attempt}/${MAX_LOGIN_ATTEMPTS}..."
  if sudo tailscale --socket="${SOCKET}" up \
    --authkey="${EFFECTIVE_TAILSCALE_AUTHKEY}" \
    --hostname="${HOSTNAME}" \
    --accept-routes \
    --accept-dns=false \
    --timeout="${UP_TIMEOUT}"; then
    echo "Tailscale is up"
    exit 0
  fi
  if sudo tailscale --socket="${SOCKET}" ip -4 >/dev/null 2>&1; then
    echo "Tailscale is up"
    exit 0
  fi
  if [[ "${attempt}" -lt "${MAX_LOGIN_ATTEMPTS}" ]]; then
    sleep "${LOGIN_RETRY_DELAY_SECONDS}"
  fi
  attempt=$((attempt + 1))
done

echo "Tailscale failed to connect after ${MAX_LOGIN_ATTEMPTS} attempts."
echo "Latest tailscale status:"
sudo tailscale --socket="${SOCKET}" status || true
echo "Health summary:"
sudo tailscale --socket="${SOCKET}" status --json 2>/dev/null | grep -E '"BackendState"|"Health"|"AuthURL"' || true
exit 1
