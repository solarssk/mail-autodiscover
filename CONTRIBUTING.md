# Contributing

Thank you for contributing to **mail-autodiscover**. Please also read the
[Code of Conduct](CODE_OF_CONDUCT.md).

## Workflow

All changes to `main` must go through a **pull request**. Direct pushes to `main` are blocked by branch protection.

1. Create a branch from `main`:
   ```bash
   git checkout main
   git pull
   git checkout -b feat/your-change
   ```
2. Make your changes and add tests where relevant.
3. Install dev tools once:
   ```bash
   pip install ".[dev]"
   pre-commit install
   ```
   After that, `ruff`, `mypy`, and `pytest` run automatically before each `git commit`.
4. Before pushing, run the full local CI mirror (optional but recommended):
   ```bash
   ./scripts/check.sh
   ```
   Skip slower dependency scans when needed:
   ```bash
   SKIP_PIP_AUDIT=1 SKIP_DEPTRY=1 ./scripts/check.sh
   ```
5. Open a pull request against `main`.
6. Wait for all CI checks to pass.
7. Merge when ready (squash merge is fine).

## Dependencies

Runtime dependencies (`[project.dependencies]` in `pyproject.toml`) are locked in
`requirements.txt`, a hash-pinned file generated with `pip-compile`. This is what the
Docker image actually installs from, so the exact same versions and artifacts get
installed on every build instead of whatever happens to satisfy the `>=` bounds in
`pyproject.toml` on a given day.

Whenever you add, remove, or change a runtime dependency, regenerate the lockfile in the
same PR, using Python 3.14 (matching the Dockerfile's base image — `pip-compile` resolves
marker-conditional dependencies using whatever interpreter runs it, and CI regenerates
under 3.14 too):

```bash
pip-compile --generate-hashes --allow-unsafe -o requirements.txt pyproject.toml
```

CI fails the PR if `requirements.txt` doesn't match what regenerating it produces, so this
can't be forgotten silently.

CI's own dev-tool installs (`test`, `lint`, `typecheck`, `security` — the extras each CI
job installs from, per-job, so no job pays for tools it never runs) are hash-pinned the
same way, in `requirements-test.txt`, `requirements-lint.txt`, `requirements-typecheck.txt`,
and `requirements-security.txt`. This used to be considered not worth the extra maintenance
surface, since these tools never ship in the container — but they still run with full
access to CI secrets and the repository checkout, so an unpinned `pip install ruff` (or
mypy, or bandit) is exactly the kind of unverified, untrusted-index install a supply-chain
attack on PyPI would target; CI is as much a "build" step as the Docker image is.
`[project.optional-dependencies].dev` itself (for local setup, below) stays unlocked — it's
never installed by CI, only by a developer's own machine.

Regenerate a dev-tool lockfile the same way, under Python 3.12 (this repo's
`requires-python` floor, and what those CI jobs actually run on):

```bash
pip-compile --extra test --generate-hashes --allow-unsafe -o requirements-test.txt pyproject.toml
```

(swap `test` and the output filename for `lint`, `typecheck`, or `security` as needed). CI
regenerates and diffs `requirements.txt` (Python 3.14) and the four dev-tool lockfiles
(Python 3.12) in two separate jobs — not one, since each set needs the interpreter it was
actually compiled under — so a forgotten regeneration still fails the PR either way.

## CI checks

| Check | What it does |
|-------|----------------|
| Secret scan (gitleaks) | Scans this run's own commit range for leaked secrets |
| Documentation impact declaration | Verifies the PR's "Documentation impact" checkbox against the actual diff (skipped for PRs authored by Dependabot); its own workflow, so it re-runs when you edit the PR description |
| Lint (ruff) | Python style and lint |
| Tests and coverage | `pytest` with ≥90% coverage on `app/`; also uploads to Codecov (report-only, not a merge gate) |
| Compatibility tests (Python 3.14) | Re-runs the suite on the Dockerfile's actual runtime Python version, not just the 3.12 floor used elsewhere |
| SonarCloud analysis | Separate, non-required job — kept off the required "Tests and coverage" path since a SonarCloud scan alone took ~46s, longer than pytest itself |
| Type check (mypy) | Static typing on `app/` |
| Security (bandit + pip-audit) | Code and dependency security |
| Verify requirements.txt matches pyproject.toml | Regenerates the runtime lockfile (Python 3.14) and diffs it against what's committed |
| Verify requirements-*.txt matches pyproject.toml | Same, for the four dev-tool lockfiles (Python 3.12) |
| Docker build and scan | Image build + Trivy scan (blocks HIGH/CRITICAL on PR; advisory SARIF upload on `main`) |
| Lint workflows (actionlint, zizmor) | Only when `.github/workflows/**` or `dependabot.yml` change: actionlint for correctness, zizmor for safety (template injection, excessive permissions, missing Dependabot cooldown) |

`docker-publish.yml` only ever builds from source on a push to `main`: each platform
(`linux/amd64`, `linux/arm64`) builds and scans in parallel, gated on fixable HIGH/CRITICAL,
before the real `latest`/`sha-<short>` tags are created from the two already-scanned digests
and published to GHCR. Only `latest` is then copied by digest to Docker Hub — `sha-<short>`
stays GHCR-only, since nothing ever reads it back from Docker Hub and it would otherwise just
accumulate there, one new tag per merge, with no reader. Both registries still carry the exact
same scanned image; nothing is rebuilt for the Docker Hub copy. A version tag never triggers a
second build:
it promotes the digest main already published for that same commit straight to the version
tag (in both registries), and generates the CycloneDX SBOM attached to the GitHub Release
from that same digest. See [SECURITY.md](SECURITY.md#security-controls--ci) for the full
control-to-workflow mapping.

## Labels and milestones

Every issue and PR carries **exactly one `type:` label** (the playbook's standard taxonomy),
plus any **topic labels** that apply, and — once it is part of a release — the open `vX.Y.Z`
milestone.

| `type:` label | When to use |
|---------------|-------------|
| `type: bug` | Something is broken |
| `type: feature` | New feature or improvement |
| `type: docs` | Docs only |
| `type: chore` | Maintenance with no behavior change (refactor, cleanup, tooling, CI) |

Topic labels say *where* or *what area*, and are added because a filter is actually useful:

| Topic label | When to use |
|-------------|-------------|
| `security` | Security hardening or vulnerability |
| `testing` | Tests and coverage |
| `ci/cd` | CI, releases, GHCR |
| `dependencies` | Dependency updates (Dependabot adds this, plus `type: chore`) |
| `outlook` | Outlook Autodiscover |
| `thunderbird` | Thunderbird Autoconfig |
| `mail-server` | Synology / IMAP / SMTP integration topics |

Milestones group the work for each release (`v0.4.1`, ...); `release.yml` closes the matching
one when the release is cut.

## Releases

- Merge **all** open PRs (including Dependabot) before cutting a release.
- Update `CHANGELOG.md` and `pyproject.toml` version on `main` via PR.
- Images are published to **GHCR and Docker Hub** on every push to `main` and on version tags `v*`.

Keep the audience in mind:

- `README.md` is the user/admin landing page.
- the `docs/` directory contains the user and admin documentation.
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

After `main` is clean, open a PR that bumps `version` in `pyproject.toml` and adds the
matching `## [X.Y.Z] - YYYY-MM-DD` entry to `CHANGELOG.md`, then merge it. That's the whole
manual part — no `git tag` step.

`release.yml` runs on every push to `main`. It compares `pyproject.toml`'s version before and
after the push; if it changed and `CHANGELOG.md` has a matching heading for it, it:

- creates the `vX.Y.Z` tag (pinned to the exact merge commit) and a GitHub Release, with notes
  formatted from that CHANGELOG entry — a short human summary, a clear `Action required` or
  `No action required` section, the technical emoji sections, Docker tags, and documentation
  links,
- dispatches `docker-publish.yml` for that tag (GHCR + Docker Hub),
- closes the `vX.Y.Z` milestone if one is open.

Any other push (no version change) is a no-op for this workflow. If the version bumped but the
CHANGELOG heading is missing, misdated, or the release already exists, it skips with a warning
instead of creating a broken release.

Preview the notes locally before merging:

```bash
python scripts/format_release_notes.py v0.1.2
```

If the automation needs to be bypassed (e.g. it's broken, or you need to re-cut a release),
do it manually with the same formatting:

```bash
python scripts/format_release_notes.py v0.1.2 > /tmp/notes.md
gh release create v0.1.2 --target main --notes-file /tmp/notes.md
gh workflow run docker-publish.yml --ref v0.1.2
```

## Security

See [SECURITY.md](SECURITY.md). Do not open public issues for vulnerabilities — use GitHub private security advisories.
