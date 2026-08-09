#!/usr/bin/env bash
# Idempotent Cloud Agent bootstrap for the Nojoom Atlas Flask app.
set -euo pipefail

cd "$(dirname "$0")/.."

# pyswisseph has no prebuilt wheel for this Python/platform and is compiled from
# source, which requires the Python development headers and a C toolchain.
# python3-venv provides the virtualenv/ensurepip support. Install them once
# (idempotent; a no-op when already present).
NEED_PKGS=()
for pkg in python3-dev build-essential python3-venv; do
  dpkg -s "$pkg" >/dev/null 2>&1 || NEED_PKGS+=("$pkg")
done
if [ "${#NEED_PKGS[@]}" -gt 0 ]; then
  echo "Installing system dependencies: ${NEED_PKGS[*]}"
  sudo apt-get update
  sudo DEBIAN_FRONTEND=noninteractive apt-get install -y "${NEED_PKGS[@]}"
fi

# Create an isolated virtualenv for the project's Python dependencies.
VENV_DIR=".venv"
if [ ! -x "${VENV_DIR}/bin/python" ]; then
  echo "Creating virtualenv at ${VENV_DIR}"
  python3 -m venv "${VENV_DIR}"
fi

# shellcheck disable=SC1091
source "${VENV_DIR}/bin/activate"

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# Provide a local .env so the app boots. The committed .env.example uses a
# placeholder API_KEY, which is enough for the core Swiss Ephemeris flow.
# Real AI features (/simplify) require a valid API_KEY/API_URL; set those via
# environment secrets if needed.
if [ ! -f .env ]; then
  echo "Creating .env from .env.example"
  cp .env.example .env
fi

echo "Install complete."
