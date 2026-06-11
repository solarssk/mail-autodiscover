# DNS And Deployment Basics

## Required DNS Records

For most deployments you want:

- `autodiscover.example.com` -> your reverse proxy public endpoint
- `autoconfig.example.com` -> your reverse proxy public endpoint

If you serve everything from one hostname, point both names to the same target.

## HTTPS Expectations

- terminate TLS at your reverse proxy
- set `PUBLIC_BASE_URL` to the public HTTPS URL
- do not expose plain HTTP directly to the internet in production

## Testing After Deployment

Use a browser or `curl` to verify:

```bash
curl -i https://autodiscover.example.com/health
curl -i https://autodiscover.example.com/ready
curl -i "https://autoconfig.example.com/mail/config-v1.1.xml?emailaddress=user@example.com"
curl -i "https://autodiscover.example.com/mail/ios.mobileconfig?emailaddress=user@example.com"
```

For Outlook, send a real client request or a POST body similar to the test suite.

## Proxy Header Contract

If the service is behind a proxy and you want real client IPs in rate limiting/logging:

- set `TRUST_PROXY_HEADERS=true`
- set `TRUSTED_PROXY_IPS` to your proxy IP or Docker CIDR

If you do not know those addresses yet, keep proxy trust disabled until you do.

## Query String Logging Warning

Thunderbird and Apple Mail require `emailaddress=` in the URL.

Review proxy access logs so they do not permanently store mailbox addresses for:

- `/mail/config-v1.1.xml`
- `/.well-known/autoconfig/mail/config-v1.1.xml`
- `/mail/ios.mobileconfig`
- `/.well-known/apple-mail.mobileconfig`
