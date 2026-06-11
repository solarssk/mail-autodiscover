# mail-autodiscover

`mail-autodiscover` is a small HTTP service that helps mail clients configure themselves for your self-hosted mail server.

It is built for admins who run their own mail stack and want Outlook, Thunderbird, and Apple Mail to pick up the correct IMAP/SMTP settings automatically.

If you want to get started quickly, copy [`.env.example`](.env.example), review the values, and deploy with [`docker-compose.ghcr.yml`](docker-compose.ghcr.yml). The rest of the documentation lives in the project's GitHub Wiki instead of one long README.

## Is this for me?

Use this project if:

- you run your own mail server,
- you want automatic client configuration for your users,
- you are happy to provide the same configuration for every valid email address in your allowed domains,
- you want a small service with environment-based configuration.

This project is not for you if:

- you need a mail server, webmail, or an admin panel,
- you need mailbox existence checks,
- you need Exchange, EWS, ActiveSync, calendars, or contacts,
- you want per-user or per-mailbox dynamic logic.

## What it does

The service exposes standard autodiscovery endpoints used by mail clients:

- Outlook Autodiscover
- Thunderbird Autoconfig
- Apple Mail `.mobileconfig` profiles

When a client asks for settings, the service returns IMAP/SMTP details from your environment variables. It does not log full email addresses and it does not check whether a mailbox exists.

## Quick start for admins

1. Copy [`.env.example`](.env.example) to `.env`.
2. Set your public URL, allowed domains, and IMAP/SMTP hostnames.
3. Deploy with Docker Compose or Portainer.
4. Put the service behind HTTPS and configure your reverse proxy.
5. Point `autodiscover.` and `autoconfig.` DNS records to your proxy.
6. Test the endpoints before sharing them with users.

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
TRUST_PROXY_HEADERS=true
TRUSTED_PROXY_IPS=127.0.0.1,10.0.0.0/8
```

### Docker / Portainer

Prebuilt images are published to GHCR:

```text
ghcr.io/solarssk/mail-autodiscover:latest
ghcr.io/solarssk/mail-autodiscover:0.2.1
```

`latest` is published on every `main` build. Prefer a pinned semver tag such as `0.2.1` in production. `docker-compose.ghcr.yml` defaults to `0.2.1`; override `IMAGE_TAG` in `.env` or Portainer when needed.

```bash
cp .env.example .env
docker compose -f docker-compose.ghcr.yml up -d
```

The GHCR compose file reads the values you set in `.env` or in your Portainer environment settings.

## Wiki

The full documentation lives in the [GitHub Wiki](https://github.com/solarssk/mail-autodiscover/wiki):

- [`Home`](https://github.com/solarssk/mail-autodiscover/wiki)
- [`What This Project Does`](https://github.com/solarssk/mail-autodiscover/wiki/What-This-Project-Does)
- [`Quick Start`](https://github.com/solarssk/mail-autodiscover/wiki/Quick-Start)
- [`Deployment with Docker or Portainer`](https://github.com/solarssk/mail-autodiscover/wiki/Deployment-with-Docker-or-Portainer)
- [`Reverse Proxy and DNS`](https://github.com/solarssk/mail-autodiscover/wiki/Reverse-Proxy-and-DNS)
- [`Client Setup`](https://github.com/solarssk/mail-autodiscover/wiki/Client-Setup-Outlook-Thunderbird-Apple-Mail)
- [`Configuration Reference`](https://github.com/solarssk/mail-autodiscover/wiki/Configuration-Reference)
- [`Upgrade Guide`](https://github.com/solarssk/mail-autodiscover/wiki/Upgrade-Guide)
- [`Security Model`](https://github.com/solarssk/mail-autodiscover/wiki/Security-Model)
- [`Troubleshooting`](https://github.com/solarssk/mail-autodiscover/wiki/Troubleshooting)

## End-user setup

Your users do not need to know how Autodiscover works. They only need the correct address or profile URL.

### Outlook

1. Open Outlook and add the mailbox address.
2. Enter the password when asked.
3. If Autodiscover is reachable and the domain is allowed, Outlook should fill in the server settings automatically.

### Thunderbird

1. Open account setup in Thunderbird.
2. Enter the name, email address, and password.
3. Thunderbird should fetch settings from `/mail/config-v1.1.xml` or the `.well-known` alias.

### Apple Mail

Open this URL in Safari and replace the domain and address:

```text
https://autodiscover.example.com/mail/ios.mobileconfig?emailaddress=user@example.com
```

Then install the downloaded profile and enter the mailbox password when prompted.

## Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/health` | Health check for monitoring |
| `GET` | `/` | Simple landing page with no sensitive configuration |
| `GET` | `/robots.txt` | Tells crawlers not to index the host |
| `GET` | `/mail/config-v1.1.xml?emailaddress=...` | Thunderbird Autoconfig |
| `GET` | `/.well-known/autoconfig/mail/config-v1.1.xml?emailaddress=...` | Thunderbird alias |
| `GET` | `/mail/ios.mobileconfig?emailaddress=...` | Apple Mail profile |
| `GET` | `/.well-known/apple-mail.mobileconfig?emailaddress=...` | Apple Mail alias |
| `POST` | `/autodiscover/autodiscover.xml` | Outlook Autodiscover |
| `GET` | `/autodiscover/autodiscover.xml` | Neutral Outlook response |

## Security at a glance

- No mailbox enumeration
- No full email address logging
- In-memory rate limiting per IP
- Safe XML parsing
- Security headers enabled by default
- No admin panel in the current version

For the detailed security model, see [`SECURITY.md`](SECURITY.md) and the wiki page [`Security Model`](https://github.com/solarssk/mail-autodiscover/wiki/Security-Model).

## Local development

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install ".[dev]"
pre-commit install
cp .env.example .env
uvicorn app.main:app --host 0.0.0.0 --port 8000 --no-access-log --reload
```

## Quality checks

Run the same Python checks as GitHub CI:

```bash
./scripts/check.sh
```

`pre-commit install` also runs `ruff`, `mypy`, and `pytest` automatically before each commit.

Developer workflow and release process live in [`CONTRIBUTING.md`](CONTRIBUTING.md).
