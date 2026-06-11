# Nginx

Use one HTTPS server block for `autodiscover.` and `autoconfig.` or separate virtual hosts that proxy to the same upstream.

## Required Proxy Headers

Forward at least:

```nginx
proxy_set_header Host $host;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-Proto $scheme;
```

## Logging Warning

Mail autoconfig URLs include `emailaddress=` in the query string. Avoid full request URI logging on those paths if mailbox privacy matters.

## Test

After reload:

```bash
curl -I https://autodiscover.example.com/health
curl -I https://autodiscover.example.com/ready
```
