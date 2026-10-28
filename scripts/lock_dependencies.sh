#!/usr/bin/env bash
# One entry point for local regeneration/checking and CI; preserves existing pins.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
group="${1:-all}"
case "$group" in
  runtime|dev|all) ;;
  *) echo "Usage: $0 [runtime|dev|all] [--check]" >&2; exit 2 ;;
esac
if [[ $# -gt 0 ]]; then shift; fi
for current in runtime dev; do
  [[ "$group" == all || "$group" == "$current" ]] || continue
  version=3.12
  [[ "$current" != runtime ]] || version=3.14
  interpreter="python${version}"
  command -v "$interpreter" >/dev/null || { echo "Install Python $version first." >&2; exit 1; }
  lock_env="$ROOT/.venv-lock-${version}"
  if [[ ! -x "$lock_env/bin/python" ]]; then
    "$interpreter" -m venv "$lock_env"
  fi
  # Recheck even for an existing environment, so stale tooling cannot drift.
  "$lock_env/bin/python" -m pip install --quiet "pip-tools==7.6.1"
  "$lock_env/bin/python" scripts/lock_dependencies.py --group "$current" "$@"
done
