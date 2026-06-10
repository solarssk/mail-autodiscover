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

- Images are published to **GHCR** on every push to `main` and on version tags `v*`.
- Create a release by tagging:
  ```bash
  git tag v0.1.1
  git push origin v0.1.1
  ```
- Update `CHANGELOG.md` before tagging.

## Security

See [SECURITY.md](SECURITY.md). Do not open public issues for vulnerabilities — use GitHub private security advisories.
