# Troubleshooting

## Service Does Not Start In Production

Check:

- `PUBLIC_BASE_URL` uses `https://`
- `PUBLIC_BASE_URL` does not contain `localhost`
- `TRUSTED_PROXY_IPS` is set when `TRUST_PROXY_HEADERS=true`
- placeholder `example.com` and `mail.example.com` values are gone

If you use multi-domain mode, validate `config/config.yaml` against the example file shape.

## Thunderbird Or Apple Mail Returns 404

Most common causes:

- mailbox domain is not present in `ALLOWED_DOMAINS`
- mailbox domain is not present in `CONFIG_FILE`
- `THUNDERBIRD_ENABLED=false` or `APPLE_MOBILECONFIG_ENABLED=false`

## Reverse Proxy Shows Wrong Client IP

- keep `TRUST_PROXY_HEADERS=false` unless traffic really comes from your proxy
- add the proxy IP or container CIDR to `TRUSTED_PROXY_IPS`
- verify the proxy forwards `X-Forwarded-For` or `X-Real-IP`

## Apple Mail Warns About Unsigned Profile

This is expected. Profiles are generated unsigned by default.

If you need a managed distribution workflow, sign the `.mobileconfig` file outside this application.

## Multi-Domain Config Does Not Apply

- confirm the file is mounted into `/config/config.yaml`
- confirm `CONFIG_FILE=/config/config.yaml`
- confirm the domain key is lowercase and matches the mailbox domain
- remember that YAML mode replaces the global domain routing from `ALLOWED_DOMAINS`
- `USERNAME_FORMAT` is global from ENV in YAML mode; it is not per-domain in the config file
