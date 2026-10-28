"""Regression coverage for lock drift checks and their non-mutating mode."""

import importlib.util
from pathlib import Path

import pytest

SPEC = importlib.util.spec_from_file_location(
    "lock_dependencies", Path(__file__).resolve().parents[1] / "scripts/lock_dependencies.py"
)
assert SPEC is not None and SPEC.loader is not None
locks = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(locks)


def test_annotations_do_not_change_install_content():
    assert locks.install_content("pkg==1\n    # via parent\n\n") == ["pkg==1\n"]


@pytest.mark.parametrize("replacement", [
    "pkg==2\n", "pkg==1 --hash=sha256:new\n",
    'pkg==1; python_version >= "3.14"\n', "--extra-index-url https://example.invalid\n",
])
def test_install_changes_are_detected(replacement):
    assert locks.install_content("pkg==1\n") != locks.install_content(replacement)


@pytest.mark.parametrize("generated,expected", [
    ("pkg==1\n# via new-parent\n", 0), ("pkg==2\n", 1),
])
def test_check_is_non_mutating_and_reports_drift(tmp_path, monkeypatch, generated, expected):
    source = tmp_path / "requirements.txt"
    original = b"pkg==1\n# via old-parent\n"
    source.write_bytes(original)
    monkeypatch.setattr(locks, "ROOT", tmp_path)
    monkeypatch.setattr(locks.sys, "version_info", (3, 14))
    monkeypatch.setattr(
        locks.sys, "argv", ["lock_dependencies.py", "--group", "runtime", "--check"]
    )

    def compile_lock(command, **kwargs):
        output = Path(command[command.index("--output-file") + 1])
        assert output != source
        assert output.read_bytes() == original
        output.write_text(generated)

    monkeypatch.setattr(locks.subprocess, "run", compile_lock)
    assert locks.main() == expected
    assert source.read_bytes() == original
