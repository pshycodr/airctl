#!/usr/bin/env bash
set -e

uv run ruff check --fix .
uv run ruff format .

git add -u