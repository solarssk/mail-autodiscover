# Reverse Proxy and DNS

Most production problems with this project come from proxy headers, HTTPS routing, or DNS. This page explains the pieces that must line up.

## Reverse proxy requirements

The service should sit behind nginx, Caddy, Traefik, NPM, or another HTTPS-capable reverse proxy.

Your proxy should:

- terminate TLS,
- route the autodiscovery paths to the container,
- preserve the original host,
- send client IP headers only if you trust the proxy path.

## Trusting forwarded headers safely

Set:

- `TRUST_PROXY_HEADERS=true`
- `TRUSTED_PROXY_IPS=<your proxy IPs or CIDRs>`

Why both matter:

- `TRUST_PROXY_HEADERS=true` tells the app to consider forwarded headers.
- `TRUSTED_PROXY_IPS` limits that trust to requests coming from your own proxy networks.

If `TRUSTED_PROXY_IPS` is empty, the app keeps the legacy behavior and trusts any peer when proxy headers are enabled. That is convenient, but it is weaker and should not be your long-term production setup.

## Paths to route

Route these paths to the container:

- `/autodiscover/autodiscover.xml`
- `/mail/config-v1.1.xml`
- `/.well-known/autoconfig/mail/config-v1.1.xml`
- `/mail/ios.mobileconfig`
- `/.well-known/apple-mail.mobileconfig`

## DNS layout

Typical records:

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

## Cloudflare or Nginx Proxy Manager

If you use Cloudflare with NPM, make sure NPM is configured to trust Cloudflare IP ranges and use the right real-IP header. Otherwise the container may log the proxy instead of the real client.
