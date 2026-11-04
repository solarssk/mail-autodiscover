# Nginx

Use one HTTPS server block for `autodiscover.` and `autoconfig.` or separate virtual hosts that proxy to the same upstream.

For a same-host Nginx installation, use `http://127.0.0.1:8088`. For a containerized or remote proxy, follow the [proxy topology table](../../README.md#docker--portainer).

## Required Proxy Headers

Forward at least:

```nginx
proxy_set_header Host $host;
proxy_set_header X-Forwarded-For $remote_addr;
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-Proto $scheme;
```

## Security Note

Do not use `$proxy_add_x_forwarded_for` for a single-hop reverse proxy. It appends to any client-supplied `X-Forwarded-For` value, which lets attackers spoof the leftmost IP when an app reads the chain naively.

From `0.3.1` onward, this service prefers `X-Real-IP` and parses `X-Forwarded-For` from right to left, but setting both headers to `$remote_addr` remains the recommended default for one proxy hop.

Do not forward a client-supplied `X-Real-IP` unchanged. Uvicorn's proxy parsing stays disabled; the application's trust rules apply to the TCP peer.

## Logging Warning

Mail autoconfig URLs include `emailaddress=` in the query string. Avoid full request URI logging on those paths if mailbox privacy matters.

## Test

After reload:

```bash
curl -I https://autodiscover.example.com/health
curl -I https://autodiscover.example.com/ready
```
