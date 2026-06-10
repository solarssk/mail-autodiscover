# mail-autodiscover

A lightweight HTTP service for automatic mail client configuration (Outlook Autodiscover and Thunderbird Autoconfig) for self-hosted mail servers, especially **Synology MailPlus Server**.

## What this is not

- Not a mail server
- Not a replacement for Synology MailPlus Server
- Does not implement Exchange, EWS, or ActiveSync
- Does not handle calendars or contacts
- Does not verify whether a mailbox exists

## How it works

A mail client (Outlook, Thunderbird) sends a request to the autodiscover/autoconfig endpoint. The service returns XML with IMAP/SMTP settings based on environment variable configuration.

For every syntactically valid address `@allowed-domain`, the **same configuration** is returned — with no account existence check.

## Security model

- **No mailbox enumeration** — the service does not connect to Synology API, LDAP, or IMAP
- **No email address logging** — logs contain only `request_id`, endpoint, status, and `domain_allowed=true/false`
- **Rate limiting** — in-memory, per IP (`RATE_LIMIT_PER_MINUTE`)
- **Safe XML parsing** — `defusedxml`, request body size limit
- **Security headers** — `X-Content-Type-Options`, `Referrer-Policy`, `X-Frame-Options`, `Cache-Control: no-store`
- **No admin panel in MVP** — configuration via ENV only
- **No public domain list** — the `/` endpoint does not expose hosts or domains

## Quick start

### Example `.env`

```env
APP_NAME=mail-autodiscover
APP_ENV=production
PUBLIC_BASE_URL=https://autodiscover.example.com
ALLOWED_DOMAINS=example.com
MAIL_DISPLAY_NAME=Example Mail
MAIL_DISPLAY_SHORT_NAME=Example
IMAP_HOST=mail.example.com
IMAP_PORT=993
IMAP_SOCKET_TYPE=SSL
SMTP_HOST=mail.example.com
SMTP_PORT=587
SMTP_SOCKET_TYPE=STARTTLS
USERNAME_FORMAT=email
```

Full list of variables: [.env.example](.env.example)

### Docker Compose (build locally)

```bash
cp .env.example .env
# edit .env as needed
docker compose up -d --build
```

### Portainer / GHCR (recommended)

Pre-built images are published to GitHub Container Registry on every push to `main` and on version tags (`v*`):

```text
ghcr.io/solarssk/autodiscover:latest
ghcr.io/solarssk/autodiscover:<git-sha>
ghcr.io/solarssk/autodiscover:v0.1.0
```

**Portainer — Stack example:**

```yaml
services:
  mail-autodiscover:
    image: ghcr.io/solarssk/autodiscover:latest
    container_name: mail-autodiscover
    restart: unless-stopped
    env_file:
      - .env
    ports:
      - "${HOST_PORT:-8088}:8000"
```

1. Make the GHCR package **public** (first time): GitHub → Packages → `autodiscover` → Package settings → Change visibility.
2. In Portainer: Stacks → Add stack → paste the compose above → add `.env` from [`.env.example`](.env.example).
3. Pin a specific tag in production (`v0.1.0` or SHA) instead of `latest`.

See [CONTRIBUTING.md](CONTRIBUTING.md) for release workflow.

### Local (without Docker)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install ".[dev]"
cp .env.example .env
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Healthcheck |
| `GET` | `/` | Application name and status |
| `GET` | `/mail/config-v1.1.xml?emailaddress=...` | Thunderbird Autoconfig |
| `GET` | `/.well-known/autoconfig/mail/config-v1.1.xml?emailaddress=...` | Thunderbird (well-known) |
| `POST` | `/autodiscover/autodiscover.xml` | Outlook Autodiscover |
| `GET` | `/autodiscover/autodiscover.xml` | Neutral Outlook response |

## Reverse proxy

Route traffic to the container:

```text
https://autodiscover.example.com/autodiscover/autodiscover.xml
https://autoconfig.example.com/mail/config-v1.1.xml
https://autoconfig.example.com/.well-known/autoconfig/mail/config-v1.1.xml
```

Set `TRUST_PROXY_HEADERS=true` only when the application runs behind a trusted reverse proxy (nginx, Caddy, Traefik, NPM). Also set `TRUSTED_PROXY_IPS` (alias `FORWARDED_ALLOW_IPS`) to the proxy/Docker CIDRs that may set `X-Forwarded-For` / `X-Real-IP`, e.g. `127.0.0.1,172.16.2.0/24`. Otherwise clients can spoof forwarded headers and bypass rate limits.

## DNS

Example records:

```text
autodiscover.example.com  CNAME  proxy.example.com
autoconfig.example.com    CNAME  proxy.example.com
mail.example.com          A/CNAME  <mail server>
```

Optional SRV records:

```text
_imaps._tcp.example.com.       SRV 0 1 993 mail.example.com.
_submission._tcp.example.com.  SRV 0 1 587 mail.example.com.
```

## Testing (curl)

### Thunderbird

```bash
curl "http://localhost:8088/mail/config-v1.1.xml?emailaddress=user@example.com"
```

### Outlook

```bash
curl -X POST "http://localhost:8088/autodiscover/autodiscover.xml" \
  -H "Content-Type: text/xml" \
  --data '<?xml version="1.0" encoding="utf-8"?><Autodiscover xmlns="http://schemas.microsoft.com/exchange/autodiscover/outlook/requestschema/2006"><Request><EMailAddress>user@example.com</EMailAddress><AcceptableResponseSchema>http://schemas.microsoft.com/exchange/autodiscover/outlook/responseschema/2006a</AcceptableResponseSchema></Request></Autodiscover>'
```

## Tests

```bash
pip install ".[dev]"
pytest -v          # includes coverage gate (≥90%)
ruff check .
mypy app
bandit -r app -ll -c pyproject.toml
```

CI runs on every pull request. See [CONTRIBUTING.md](CONTRIBUTING.md).

## Roadmap

### v0.1 (MVP)

- ENV-based configuration
- Outlook Autodiscover
- Thunderbird Autoconfig
- Docker + Docker Compose
- Tests + GitHub Actions CI

### v0.2

- Multi-domain config per domain
- Different IMAP/SMTP hosts per domain
- Improved rate limiting
- Optional POP3

### v0.3

- Admin panel
- Database
- OIDC login via Authentik
- Admin/viewer roles
- Configuration change audit log

### v0.4

- SAML/OIDC hardening
- Backup/restore config
- Import/export config
- Docker image published to GHCR

## License

MIT — see [LICENSE](LICENSE).
