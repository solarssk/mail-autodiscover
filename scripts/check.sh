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

# The two lock checks below each need a specific Python version -- not
# whatever single interpreter backs .venv above -- because pip-compile
# records its own interpreter in the generated header and resolves
# marker-conditional dependencies using it: running both checks through the
# same interpreter necessarily gets one of them wrong (see the version note
# on each check). A throwaway per-version venv, not a direct `pip install
# pip-tools` against python3.X itself, because Homebrew's Python (and most
# system Pythons) refuses that outside a venv (PEP 668).
lock_python() {
  local version="$1" venv_dir="${ROOT}/.venv-lock-${1}"
  command -v "python${version}" >/dev/null 2>&1 || return 1
  if [[ ! -x "${venv_dir}/bin/python" ]]; then
    "python${version}" -m venv "$venv_dir" >/dev/null
    "${venv_dir}/bin/pip" install --quiet "pip-tools==7.6.1"
  fi
  echo "${venv_dir}/bin/python"
}

echo "==> ruff"
"$RUFF" check .

echo "==> pytest"
"$PYTEST" -q

echo "==> mypy"
"$MYPY" app

echo "==> bandit"
"$BANDIT" -r app -ll -c pyproject.toml

if [[ "${SKIP_REQUIREMENTS_LOCK:-}" != "1" ]]; then
  echo "==> requirements.txt (pip-compile drift check, Python 3.14)"
  # Must match the Dockerfile's base image Python version -- see CI's
  # dependency-lock job for why.
  if PY314="$(lock_python 3.14)"; then
    "$PY314" -m piptools compile --generate-hashes --allow-unsafe -o requirements.txt pyproject.toml
    git diff --exit-code requirements.txt
  else
    echo "python3.14 not found on PATH -- install it (e.g. 'brew install python@3.14') to run this" \
         "check locally, or set SKIP_REQUIREMENTS_LOCK=1 to skip it (CI still verifies it)." >&2
    exit 1
  fi
fi

if [[ "${SKIP_DEV_REQUIREMENTS_LOCK:-}" != "1" ]]; then
  echo "==> requirements-*.txt (dev-tool pip-compile drift check, Python 3.12)"
  # This repo's requires-python floor, matching what those CI jobs actually
  # run on -- see CI's dev-dependency-lock job for why this must be a
  # different interpreter than the check above.
  if PY312="$(lock_python 3.12)"; then
    for extra in test lint typecheck security; do
      "$PY312" -m piptools compile --extra "$extra" --generate-hashes --allow-unsafe \
        -o "requirements-${extra}.txt" pyproject.toml
    done
    git diff --exit-code requirements-test.txt requirements-lint.txt requirements-typecheck.txt \
      requirements-security.txt
  else
    echo "python3.12 not found on PATH -- install it (e.g. 'brew install python@3.12') to run this" \
         "check locally, or set SKIP_DEV_REQUIREMENTS_LOCK=1 to skip it (CI still verifies it)." >&2
    exit 1
  fi
fi

if [[ "${SKIP_PIP_AUDIT:-}" != "1" ]]; then
  echo "==> pip-audit"
  # Scoped to requirements.txt (the exact runtime lockfile Dockerfile installs
  # with --require-hashes), matching CI -- not the local .venv's full dev
  # toolchain, which pip-audit would otherwise scan by default.
  "$PIP_AUDIT" -r requirements.txt
fi

if [[ "${SKIP_DEPTRY:-}" != "1" ]]; then
  echo "==> deptry"
  "$DEPTRY" .
fi

echo "All local checks passed."
