#!/usr/bin/env bash
set -e

echo "Building AIRCTL..."

if [ ! -f "pyproject.toml" ]; then
  echo "Error: Run this script from the project root directory."
  exit 1
fi

if [ ! -d ".venv" ]; then
  echo "Error: .venv not found."
  echo "Run: uv sync"
  exit 1
fi

if [ -z "$VIRTUAL_ENV" ]; then
  echo "Error: Virtual environment not activated."
  echo "Run: source .venv/bin/activate"
  exit 1
fi

if ! command -v nuitka >/dev/null 2>&1; then
  echo "Error: nuitka not found in virtual environment."
  exit 1
fi

echo "Starting Nuitka build..."

nuitka \
  --onefile \
  --enable-plugin=implicit-imports \
  --include-package=gi \
  --include-package=gi.repository \
  --include-package=rich \
  --include-package-data=rich \
  --include-module=nmcli \
  --include-data-files=airctl/styles/style.css=airctl/styles/style.css \
  --assume-yes-for-downloads \
  --output-dir=out \
  --output-filename=airctl.bin \
  airctl/main.py

echo "Build complete."
echo "Binary available at: out/airctl.bin"
