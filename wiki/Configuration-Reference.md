# Configuration Reference

This page explains the most important environment variables in plain language.

## Identity and public URL

- `APP_NAME`: name shown on the landing page
- `PUBLIC_BASE_URL`: public URL where the service is reachable

## Domain control

- `ALLOWED_DOMAINS`: comma-separated list of domains the service should answer for
- `RETURN_404_FOR_UNKNOWN_DOMAIN`: whether unknown domains should receive a neutral `404`

## Mail settings returned to clients

- `MAIL_DISPLAY_NAME`: long display name
- `MAIL_DISPLAY_SHORT_NAME`: short display name
- `IMAP_HOST`, `IMAP_PORT`, `IMAP_SOCKET_TYPE`, `IMAP_AUTHENTICATION`
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_SOCKET_TYPE`, `SMTP_AUTHENTICATION`
- `USERNAME_FORMAT`: usually `email`

## Proxy and logging

- `TRUST_PROXY_HEADERS`: enables forwarded-header processing
- `TRUSTED_PROXY_IPS`: restricts which peers may supply forwarded headers
- `ACCESS_LOG_SKIP_PATHS`: removes noisy paths from the unified access log
- `DISABLE_ACCESS_LOG`: disables the custom access log entirely
- `LOG_LEVEL`: log verbosity

## Request limits and headers

- `MAX_REQUEST_BODY_BYTES`: maximum accepted request body size
- `RATE_LIMIT_ENABLED`: enables per-IP rate limiting
- `RATE_LIMIT_PER_MINUTE`: number of allowed requests per minute per IP
- `SECURITY_HEADERS_ENABLED`: enables response security headers

## Protocol switches

- `OUTLOOK_ENABLED`
- `THUNDERBIRD_ENABLED`
- `APPLE_MOBILECONFIG_ENABLED`
- `POP3_ENABLED`

Disable endpoints you do not want to expose.

## Related file

See the full example in [`.env.example`](/Users/filipchochol/Documents/Projects/autodiscover/.env.example).
