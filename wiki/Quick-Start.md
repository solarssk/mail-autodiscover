# Quick Start

This page is the shortest path from clone to working deployment.

## Before you begin

You should already have:

- a working mail server,
- a public HTTPS reverse proxy,
- DNS control for your mail domain,
- IMAP and SMTP hostnames you want clients to use.

## 1. Prepare the environment

Copy `.env.example` to `.env` and fill in at least:

- `PUBLIC_BASE_URL`
- `ALLOWED_DOMAINS`
- `MAIL_DISPLAY_NAME`
- `MAIL_DISPLAY_SHORT_NAME`
- `IMAP_HOST`
- `IMAP_PORT`
- `IMAP_SOCKET_TYPE`
- `SMTP_HOST`
- `SMTP_PORT`
- `SMTP_SOCKET_TYPE`
- `USERNAME_FORMAT`
- `TRUST_PROXY_HEADERS`
- `TRUSTED_PROXY_IPS`

## 2. Start the service

For GHCR images:

```bash
cp .env.example .env
docker compose -f docker-compose.ghcr.yml up -d
```

For a local build:

```bash
cp .env.example .env
docker compose up -d --build
```

## 3. Put it behind HTTPS

Route these paths through your reverse proxy:

- `/autodiscover/autodiscover.xml`
- `/mail/config-v1.1.xml`
- `/.well-known/autoconfig/mail/config-v1.1.xml`
- `/mail/ios.mobileconfig`
- `/.well-known/apple-mail.mobileconfig`

## 4. Create DNS records

Typical setup:

```text
autodiscover.example.com  CNAME  proxy.example.com
autoconfig.example.com    CNAME  proxy.example.com
mail.example.com          A/CNAME  <mail server>
```

## 5. Test the endpoints

Thunderbird:

```bash
curl "https://autoconfig.example.com/mail/config-v1.1.xml?emailaddress=user@example.com"
```

Outlook:

```bash
curl -X POST "https://autodiscover.example.com/autodiscover/autodiscover.xml" \
  -H "Content-Type: text/xml" \
  --data '<?xml version="1.0" encoding="utf-8"?><Autodiscover xmlns="http://schemas.microsoft.com/exchange/autodiscover/outlook/requestschema/2006"><Request><EMailAddress>user@example.com</EMailAddress><AcceptableResponseSchema>http://schemas.microsoft.com/exchange/autodiscover/outlook/responseschema/2006a</AcceptableResponseSchema></Request></Autodiscover>'
```

If both return a valid response, you can move on to end-user testing.
