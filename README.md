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
ghcr.io/solarssk/autodiscover:0.2.0
```

See [`docker-compose.ghcr.yml`](docker-compose.ghcr.yml) for a full Portainer-ready stack with inline environment placeholders.

1. Make the GHCR package **public** (first time): GitHub → Packages → `autodiscover` → Package settings → Change visibility.
2. In Portainer: Stacks → Add stack → paste from `docker-compose.ghcr.yml` → set your domains and mail hosts.
3. Pin a semver tag in production (`0.2.0`) instead of `latest`.
4. Set `TRUSTED_PROXY_IPS` to your reverse-proxy / Docker bridge CIDRs (see below).

See [CONTRIBUTING.md](CONTRIBUTING.md) for release workflow.

### Local (without Docker)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install ".[dev]"
cp .env.example .env
uvicorn app.main:app --host 0.0.0.0 --port 8000 --no-access-log --reload
```

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Healthcheck |
| `GET` | `/` | Minimal HTML landing (no configuration exposed) |
| `GET` | `/robots.txt` | `Disallow: /` for crawlers |
| `GET` | `/mail/config-v1.1.xml?emailaddress=...` | Thunderbird Autoconfig |
| `GET` | `/.well-known/autoconfig/mail/config-v1.1.xml?emailaddress=...` | Thunderbird (well-known) |
| `GET` | `/mail/ios.mobileconfig?emailaddress=...` | Apple Mail configuration profile |
| `GET` | `/.well-known/apple-mail.mobileconfig?emailaddress=...` | Apple Mail (well-known alias) |
| `POST` | `/autodiscover/autodiscover.xml` | Outlook Autodiscover |
| `GET` | `/autodiscover/autodiscover.xml` | Neutral Outlook response |

### Apple Mail (iPhone / iPad / Mac)

Open in **Safari** (replace domain and email):

```text
https://autodiscover.example.com/mail/ios.mobileconfig?emailaddress=user@example.com
```

Install the downloaded profile in **Settings**. Enter your mail password when prompted. Unsigned profiles show an Apple verification warning — expected for self-hosted setups without MDM signing.

## Reverse proxy

Route traffic to the container:

```text
https://autodiscover.example.com/autodiscover/autodiscover.xml
https://autoconfig.example.com/mail/config-v1.1.xml
https://autoconfig.example.com/.well-known/autoconfig/mail/config-v1.1.xml
```

Set `TRUST_PROXY_HEADERS=true` only when the application runs behind a trusted reverse proxy (nginx, Caddy, Traefik, NPM).

When using a reverse proxy, also set `TRUSTED_PROXY_IPS` (alias `FORWARDED_ALLOW_IPS`) to **your** proxy or Docker bridge CIDRs — comma-separated IPs or networks. Each deployment is different; use `docker network inspect <network>` or check the access log `client_ip` vs direct peer. Allow that subnet plus `127.0.0.1` if the proxy runs on the same host. If `TRUSTED_PROXY_IPS` is empty, legacy behavior applies (trust any peer).

On Cloudflare + NPM, configure `real_ip_header CF-Connecting-IP` and Cloudflare IP ranges in NPM so the container receives a correct `X-Forwarded-For`.

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

### v0.2 (released)

- `TRUSTED_PROXY_IPS`, unified access logging, landing page, Apple `.mobileconfig`
- (Deferred) per-domain IMAP/SMTP hosts, Redis rate limiting

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
