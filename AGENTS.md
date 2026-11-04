# Agent guide

Shared context for coding agents. `CLAUDE.md` imports this file.

## Scope and standard

Stateless FastAPI service returning mail client settings for allowed domains.
No database, admin panel, mailbox lookup, LDAP, password storage, or outbound mail calls.
Keep the service small; do not add infrastructure to solve a local problem.

Standard: https://github.com/solarssk/playbook
Tier: 2

The service ships a container image. `.github/workflows/verify-standard.yml`
checks the Tier 2 file and workflow requirements.

## Security invariants

- Every syntactically valid address in an allowed domain gets the same response
  shape, regardless of mailbox existence. Preserve `tests/test_no_mailbox_enumeration.py`.
- Never log full email addresses, query strings, or request bodies. Application
  access logs use domain hashes; proxies need their own privacy-safe logging.
- Keep `TRUST_PROXY_HEADERS=false` by default. Enable trust only for configured
  proxy IPs/CIDRs, and do not weaken production startup validation.
- Parse request XML with `defusedxml`. Escape XML text with
  `html.escape(..., quote=False)`, not `xml.sax.saxutils.escape` (Bandit B406).
- The rate limiter is bounded and in-process, with a separate counter per worker.
- The landing page must not expose configured domains or mail servers.
  Keep it static, with no scripts, external assets, or password forms.
  Use semantic headings and visible protocol details, not invented status,
  badges, gradients, repetitive hero labels, or decorative numbered steps.

## Code map

| File | Responsibility |
|------|----------------|
| `app/main.py` | App factory, routes, bounded request reads |
| `app/config.py` | ENV/YAML settings and startup validation |
| `app/security.py` | Headers, rate limits, proxy trust, safe access logs |
| `app/email_utils.py` | Address validation and username formatting |
| `app/templates.py` | Outlook and Thunderbird XML |
| `app/mobileconfig.py` | Apple Mail profiles |
| `app/landing.py`, `app/static/` | Public page, robots.txt, icons |
| `tests/` | pytest, enforced branch coverage of at least 90% on `app/` |
| `docs/` | Deployment, DNS, endpoints, client guides |

Read the relevant code and tests before changing behavior. Prefer existing
helpers and standard-library tools over new dependencies or one-use abstractions.
Add regression tests and update affected user documentation.

## Configuration

- ENV mode uses `ALLOWED_DOMAINS` and global `IMAP_*`, `SMTP_*`, `POP3_*`.
- Empty `CONFIG_FILE` selects ENV. A nonempty path is required to exist and contain
  valid YAML; it replaces ENV domain routing. See `config/config.example.yaml`.
- `USERNAME_FORMAT` always comes from ENV, including in YAML mode.
- Validate effective mail settings through `MailServerSettings` in both modes.
  Do not reject unused ENV host/port/authentication values in YAML mode.
- Production rejects `plain` transport unless `ALLOW_INSECURE_MAIL=true`.
  `password-cleartext` over SSL/STARTTLS is still encrypted in transit.
- Production rejects placeholders and unsafe proxy settings.
  Use `APP_ENV=development` or `test` only for local development/tests.

## Development and checks

Use Python 3.12 or newer, not an OS-provided older `python3`/`pytest`.
CI covers 3.12 and the Docker runtime, 3.14.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install ".[dev]"
pre-commit install
cp .env.example .env
# Set APP_ENV=development in .env before starting.
uvicorn app.main:app --reload --no-access-log --no-proxy-headers
./scripts/check.sh
```

Run focused tests during edits, then the full local check before handing off.
`scripts/check.sh` prefers `.venv/bin/` and covers Ruff, pytest, mypy, Bandit,
lock drift, pip-audit, and deptry. Docker/Trivy, gitleaks, and workflow checks run
separately in CI. Never bypass commit hooks with `--no-verify`.

Uvicorn's proxy parsing must stay disabled; the application checks the actual
TCP peer. Use exact route paths: trailing-slash variants return 404 rather than
redirecting clients to HTTP behind a TLS-terminating proxy.

## Dependencies and images

- Five generated requirements files are hash-pinned. After any dependency change,
  including Dependabot updates, run `./scripts/lock_dependencies.sh`.
  The wrapper uses isolated Python 3.14 runtime and Python 3.12 dev environments.
- Verify without modifying files: `./scripts/lock_dependencies.sh all --check`.
  Only comments and blank lines are ignored; never ignore version/hash drift.
- New transitive dependencies can be missing after Dependabot edits. Regenerate
  all locks instead of disabling hash verification.
- Ruff is pinned in the `lint` extra. Reinstall `.[dev]` after changing the pin;
  local pre-commit uses the active environment.
- Preserve Docker's `CACHEBUST=${{ github.run_id }}-${{ github.run_attempt }}`.
  A commit SHA does not force OS updates on same-commit rebuilds/retries.
  Keep `ARG CACHEBUST` and `apt-get upgrade` after dependency installation to
  avoid reinstalling Python dependencies on every build.
- Source builds on `main` are scanned before publishing. Version tags promote
  the already-scanned digest to GHCR and Docker Hub, without rebuilding it.
  Never move an existing release tag to a rebuilt image.

## PRs and releases

- Prepare changes on a feature branch; the maintainer decides and merges.
- Use `.github/pull_request_template.md`. Include exact validation commands
  and results. Do not add `Co-authored-by` trailers or em dashes to new prose.
- Documentation impact is checked by `scripts/check_pr_docs_impact.py`.
  Only `docs/`, `README.md`, `SECURITY.md`, `CHANGELOG.md`, and `CONTRIBUTING.md`
  count. Agent-guide-only changes need "No doc update needed" with a real reason.
- Each PR needs one `type:` label; add relevant topic labels. See `CONTRIBUTING.md`.
- Release only after compatibility and security findings are resolved. Bump
  `pyproject.toml`, add the hybrid CHANGELOG entry and comparison links, and
  align Compose/example image tags. Do not bump a version during preparation.
- `release.yml` creates the tag and release on merge, dispatches image promotion,
  and closes the matching milestone. No manual tag push.
- Read `CONTRIBUTING.md` for release formatting and recovery. Do not guess how
  retries, changelog recovery, or image promotion work from workflow names.
