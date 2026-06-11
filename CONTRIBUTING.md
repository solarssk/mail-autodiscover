# Contributing

Thank you for contributing to **mail-autodiscover**.

## Workflow

All changes to `main` must go through a **pull request**. Direct pushes to `main` are blocked by branch protection.

1. Create a branch from `main`:
   ```bash
   git checkout main
   git pull
   git checkout -b feat/your-change
   ```
2. Make your changes and add tests where relevant.
3. Run checks locally:
   ```bash
   pip install ".[dev]"
   ruff check .
   pytest -v
   mypy app
   bandit -r app -ll -c pyproject.toml
   ```
4. Open a pull request against `main`.
5. Wait for all CI checks to pass.
6. Merge when ready (squash merge is fine).

## CI checks

| Check | What it does |
|-------|----------------|
| Secret scan (gitleaks) | Scans for leaked secrets |
| Lint (ruff) | Python style and lint |
| Tests and coverage | `pytest` with ≥90% coverage on `app/` |
| Type check (mypy) | Static typing on `app/` |
| Security (bandit + pip-audit) | Code and dependency security |
| Docker build and scan | Image build + Trivy SARIF upload |

## Labels

Use labels to classify issues and PRs:

| Label | When to use |
|-------|-------------|
| `bug` | Something is broken |
| `enhancement` | New feature or improvement |
| `documentation` | Docs only |
| `security` | Security hardening or vulnerability |
| `testing` | Tests and coverage |
| `ci/cd` | CI, releases, GHCR |
| `dependencies` | Dependency updates (often Dependabot) |
| `outlook` | Outlook Autodiscover |
| `thunderbird` | Thunderbird Autoconfig |
| `mail-server` | Synology / IMAP / SMTP integration topics |

## Releases

- Merge **all** open PRs (including Dependabot) before cutting a release.
- Update `CHANGELOG.md` and `pyproject.toml` version on `main` via PR.
- Images are published to **GHCR** on every push to `main` and on version tags `v*`.

Keep the audience in mind:

- `README.md` is the user/admin landing page.
- the GitHub Wiki contains the user and admin documentation.
- `CONTRIBUTING.md` stays maintainer-focused.

### CHANGELOG format

Each release entry should begin with the plain-language sections below:

- `### What's new`
- `### What this means`
- `### Action required`

After that, use [Keep a Changelog](https://keepachangelog.com/) sections for the technical breakdown. They map to emoji in release notes:

| CHANGELOG | Release section |
|-----------|-----------------|
| `### Added` | ✨ Added |
| `### Changed` | 🔄 Changed |
| `### Fixed` | 🐛 Fixed |
| `### Security` | 🔒 Security |
| `### Note` | 📝 Note |

If no upgrade step is needed, write `- No action required.`

### Cut a release

After `main` is clean:

```bash
git checkout main && git pull
git tag v0.1.2
git push origin v0.1.2
```

The **Release** workflow reads `CHANGELOG.md` and publishes formatted notes with:

- a short human summary,
- a clear `Action required` or `No action required` section,
- the technical emoji sections,
- Docker tags and documentation links.

Preview locally:

```bash
python scripts/format_release_notes.py v0.1.2
```

Manual release (same formatting):

```bash
python scripts/format_release_notes.py v0.1.2 > /tmp/notes.md
gh release create v0.1.2 --target main --title "v0.1.2" --notes-file /tmp/notes.md
```

## Security

See [SECURITY.md](SECURITY.md). Do not open public issues for vulnerabilities — use GitHub private security advisories.
