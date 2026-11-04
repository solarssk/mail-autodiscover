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

Compose defaults to `HOST_BIND=127.0.0.1`. A same-host proxy can use port `8088`; a containerized proxy can use a shared Docker network and port `8000`. For a remote proxy, bind to the host's private LAN address and permit only that proxy through the firewall. See the [proxy topology table](../README.md#docker--portainer).

## Testing After Deployment

Use a browser or `curl` to verify:

```bash
curl -i https://autodiscover.example.com/health
curl -i https://autodiscover.example.com/ready
curl -i "https://autoconfig.example.com/mail/config-v1.1.xml?emailaddress=user@example.com"
curl -i "https://autodiscover.example.com/mail/ios.mobileconfig?emailaddress=user@example.com"
```

For Outlook, send a real client request or use the `curl` example in [endpoints.md](endpoints.md#outlook-autodiscover-example).

## Proxy Header Contract

If the service is behind a proxy and you want real client IPs in rate limiting/logging:

- set `TRUST_PROXY_HEADERS=true`
- set `TRUSTED_PROXY_IPS` to your proxy IP or Docker CIDR
- overwrite or remove client-supplied `X-Real-IP`, and construct `X-Forwarded-For` at the proxy

If you do not know those addresses yet, keep proxy trust disabled until you do.

The container disables Uvicorn's independent forwarded-header parsing so the application can inspect the actual peer. For non-container launches, use `--no-proxy-headers` too.

## Query String Logging Warning

Thunderbird and Apple Mail require `emailaddress=` in the URL.

Review proxy access logs so they do not permanently store mailbox addresses for:

- `/mail/config-v1.1.xml`
- `/.well-known/autoconfig/mail/config-v1.1.xml`
- `/mail/ios.mobileconfig`
- `/.well-known/apple-mail.mobileconfig`
