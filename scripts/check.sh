#!/usr/bin/env bash
# Run the same Python checks as GitHub CI (without Docker/Trivy/gitleaks).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ -x "${ROOT}/.venv/bin/python" ]]; then
  PYTHON="${ROOT}/.venv/bin/python"
  RUFF="${ROOT}/.venv/bin/ruff"
  PYTEST="${ROOT}/.venv/bin/pytest"
  MYPY="${ROOT}/.venv/bin/mypy"
  BANDIT="${ROOT}/.venv/bin/bandit"
  PIP_AUDIT="${ROOT}/.venv/bin/pip-audit"
  DEPTRY="${ROOT}/.venv/bin/deptry"
else
  PYTHON="python3"
  RUFF="ruff"
  PYTEST="pytest"
  MYPY="mypy"
  BANDIT="bandit"
  PIP_AUDIT="pip-audit"
  DEPTRY="deptry"
fi

echo "==> ruff"
"$RUFF" check .

echo "==> pytest"
"$PYTEST" -q

echo "==> mypy"
"$MYPY" app

echo "==> bandit"
"$BANDIT" -r app -ll -c pyproject.toml

if [[ "${SKIP_PIP_AUDIT:-}" != "1" ]]; then
  echo "==> pip-audit"
  "$PIP_AUDIT"
fi

if [[ "${SKIP_DEPTRY:-}" != "1" ]]; then
  echo "==> deptry"
  "$DEPTRY" .
fi

echo "All local checks passed."
