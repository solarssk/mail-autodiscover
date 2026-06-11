# Deployment with Docker or Portainer

This project is designed to be deployed as a small container behind an HTTPS reverse proxy.

## Recommended path

Use the published GHCR image and pin a semver tag in production:

```text
ghcr.io/solarssk/autodiscover:0.2.0
```

Avoid `latest` for long-lived environments.

## Docker Compose with GHCR image

Use [`docker-compose.ghcr.yml`](../docker-compose.ghcr.yml) as your starting point.

The file is written to consume values from `.env` or from Portainer environment variables, so you can keep the stack file itself close to upstream defaults.

Important values to review before deployment:

- `PUBLIC_BASE_URL`
- `ALLOWED_DOMAINS`
- `IMAP_HOST` and `SMTP_HOST`
- `TRUST_PROXY_HEADERS`
- `TRUSTED_PROXY_IPS`
- `OUTLOOK_ENABLED`
- `THUNDERBIRD_ENABLED`
- `APPLE_MOBILECONFIG_ENABLED`

## Portainer workflow

1. Open Portainer.
2. Go to `Stacks`.
3. Create a new stack.
4. Paste the contents of `docker-compose.ghcr.yml`.
5. Replace all example values.
6. Deploy the stack.

## Local image build

If you want to build from source:

```bash
docker compose up -d --build
```

That path is useful for development and local verification.

## After deployment

Confirm:

- `/health` returns `200`,
- the landing page does not expose private hostnames,
- client endpoints are reachable through your proxy,
- logs show the real client IP when trusted proxy settings are correct.
