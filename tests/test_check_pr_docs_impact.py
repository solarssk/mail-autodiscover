"""Tests for the PR documentation-impact declaration check."""

import json
from pathlib import Path

import pytest

from scripts import check_pr_docs_impact as check

DOCS_UPDATED = "- [x] Docs updated\n- [ ] No doc update needed: <state the reason>"
NO_DOCS_NEEDED = "- [ ] Docs updated\n- [x] No doc update needed: pure CI change"


def run(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    *,
    body: str,
    user: str = "solarssk",
    head_ref: str = "feature/x",
    files: list[str] | None = None,
) -> int:
    event = {
        "pull_request": {
            "user": {"login": user},
            "head": {"ref": head_ref, "sha": "head"},
            "base": {"sha": "base"},
            "body": body,
        }
    }
    event_file = tmp_path / "event.json"
    event_file.write_text(json.dumps(event), encoding="utf-8")
    monkeypatch.setenv("GITHUB_EVENT_PATH", str(event_file))
    monkeypatch.setattr(check, "changed_files", lambda base, head: files or [])
    return check.main()


def test_no_event_path_is_a_no_op(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GITHUB_EVENT_PATH", raising=False)
    assert check.main() == 0


def test_non_pull_request_event_is_a_no_op(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    event_file = tmp_path / "event.json"
    event_file.write_text(json.dumps({"ref": "refs/heads/main"}), encoding="utf-8")
    monkeypatch.setenv("GITHUB_EVENT_PATH", str(event_file))
    assert check.main() == 0


def test_dependabot_author_is_exempt(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    assert run(monkeypatch, tmp_path, body="", user="dependabot[bot]") == 0


def test_dependabot_branch_name_alone_is_not_exempt(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Anyone can open a PR from a branch named dependabot/...; only the
    author identifies a real Dependabot PR."""
    assert run(monkeypatch, tmp_path, body="", head_ref="dependabot/pip/fake") == 1


def test_missing_declaration_fails(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    assert run(monkeypatch, tmp_path, body="just a summary") == 1


def test_both_declarations_fail(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    body = "- [x] Docs updated\n- [x] No doc update needed: because"
    assert run(monkeypatch, tmp_path, body=body, files=["README.md"]) == 1


def test_unfilled_placeholder_reason_does_not_count(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    body = "- [ ] Docs updated\n- [x] No doc update needed: <state the reason>"
    assert run(monkeypatch, tmp_path, body=body) == 1


def test_docs_updated_with_a_docs_change_passes(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    assert run(monkeypatch, tmp_path, body=DOCS_UPDATED, files=["README.md", "app/main.py"]) == 0


def test_docs_updated_without_a_docs_change_fails(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    assert run(monkeypatch, tmp_path, body=DOCS_UPDATED, files=["app/main.py"]) == 1


def test_no_docs_needed_without_a_docs_change_passes(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    assert run(monkeypatch, tmp_path, body=NO_DOCS_NEEDED, files=["app/main.py"]) == 0


def test_no_docs_needed_but_a_docs_file_changed_fails(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    assert run(monkeypatch, tmp_path, body=NO_DOCS_NEEDED, files=["CONTRIBUTING.md"]) == 1
