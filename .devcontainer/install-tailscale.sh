#!/usr/bin/env bash
set -euo pipefail

if command -v tailscale >/dev/null 2>&1 && command -v tailscaled >/dev/null 2>&1; then
  echo "Tailscale is already installed"
  exit 0
fi

echo "Installing Tailscale..."
curl -fsSL https://tailscale.com/install.sh | sh
echo "Tailscale installation complete"
