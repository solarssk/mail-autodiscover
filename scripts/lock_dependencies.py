#!/usr/bin/env python3
"""Regenerate locks, or check install-relevant content without changing files."""

import argparse
import difflib
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]


def install_content(text: str) -> list[str]:
    """Ignore full-line comments and blank lines; preserve every install option."""
    return [line for line in text.splitlines(keepends=True)
            if line.strip() and not line.lstrip().startswith("#")]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--group", choices=("runtime", "dev"), required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    expected = (3, 14) if args.group == "runtime" else (3, 12)
    if sys.version_info[:2] != expected:
        parser.error(f"{args.group} locks require Python {expected[0]}.{expected[1]}")
    extras = [None] if args.group == "runtime" else ["test", "lint", "typecheck", "security"]
    failed = False
    for extra in extras:
        name = f"requirements-{extra}.txt" if extra else "requirements.txt"
        source = ROOT / name
        # Seed with the existing pins so this checks consistency, not upgrades.
        # A temporary output also avoids requiring git add before local checks.
        with TemporaryDirectory() as directory:
            output = Path(directory) / name if args.check else source
            if args.check:
                output.write_bytes(source.read_bytes())
            command = [sys.executable, "-m", "piptools", "compile",
                       "--generate-hashes", "--allow-unsafe", "--output-file", str(output)]
            if extra:
                command.extend(["--extra", extra])
            subprocess.run([*command, "pyproject.toml"], cwd=ROOT, check=True)
            if args.check:
                before = install_content(source.read_text())
                after = install_content(output.read_text())
                if before != after:
                    failed = True
                    sys.stderr.writelines(difflib.unified_diff(
                        before, after, fromfile=name, tofile=f"regenerated/{name}"))
    if failed:
        print("Lock drift detected. Run ./scripts/lock_dependencies.sh to regenerate.",
              file=sys.stderr)
    return int(failed)


if __name__ == "__main__":
    raise SystemExit(main())
