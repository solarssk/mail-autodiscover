# Troubleshooting

## Outlook does not discover settings

Check:

- `/autodiscover/autodiscover.xml` is reachable publicly,
- the request is routed through HTTPS,
- the email domain is listed in `ALLOWED_DOMAINS`,
- the returned hostnames match your real IMAP and SMTP servers.

## Thunderbird does not fetch config

Check:

- `/mail/config-v1.1.xml` works in a browser or `curl`,
- the `.well-known` alias is also routed if you expect clients to use it,
- the query includes `emailaddress=user@example.com`.

## Apple Mail profile does not install

Check:

- the URL opens in Safari,
- the response downloads as a profile,
- the email address belongs to an allowed domain,
- the user understands that unsigned profiles may show a warning.

## Logs show the proxy IP instead of the client IP

Check:

- `TRUST_PROXY_HEADERS=true`,
- `TRUSTED_PROXY_IPS` contains the proxy or bridge CIDR that connects to the container,
- your reverse proxy forwards the real client IP header correctly.

## Unknown domains still get a response

Check:

- `ALLOWED_DOMAINS` formatting,
- whether the tested address really belongs to one of those domains,
- `RETURN_404_FOR_UNKNOWN_DOMAIN` if you expect a `404` response.

## Health checks fill the logs

Review:

- `ACCESS_LOG_SKIP_PATHS`
- `DISABLE_ACCESS_LOG`

By default, health and icon paths can be excluded from access logs.
