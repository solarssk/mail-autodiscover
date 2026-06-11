# Upgrade Guide

Use this page when moving between released versions.

## General upgrade rules

1. Read the release notes for the target version.
2. Look for the `Action required` section first.
3. Pin the target image tag in production.
4. Review `.env.example` for any new variables.
5. Test Thunderbird and Outlook endpoints after deployment.

## Upgrading to 0.2.0

Key change:

- forwarded headers can now be restricted to your own proxy networks with `TRUSTED_PROXY_IPS`.

What to do:

1. Keep `TRUST_PROXY_HEADERS=true` only if you really run behind a proxy.
2. Set `TRUSTED_PROXY_IPS` to your reverse-proxy or Docker bridge CIDRs.
3. Redeploy the container with the `0.2.0` image tag.
4. Confirm that logs now show the real client IP instead of only the proxy peer.

Also in `0.2.0`:

- Apple Mail profile endpoints were added,
- the root page became a simple landing page,
- health checks stopped consuming rate-limit budget.

## When no action is required

Some releases are maintenance-only. In those cases the release notes will explicitly say `No action required.`
