# Outlook

The service returns IMAP/SMTP Autodiscover XML. It does not implement Exchange account provisioning. No version-specific compatibility matrix is published; classic Outlook and new Outlook are not interchangeable compatibility claims. See the [compatibility scope](../../README.md#client-compatibility).

## Recorded validation

The maintainer reported a working Outlook setup on macOS on 2026-11-04. The installed application and OS metadata were read locally on that date:

| Item | Recorded evidence |
|------|-------------------|
| Outlook version | 16.114.3 |
| Outlook build | 16.114.26102720 |
| macOS version | 27.0.1 |
| Functional result | Maintainer reports the setup works; not independently reproduced |
| Not separately recorded | New/Legacy Outlook mode, fresh account discovery without manual server settings, send/receive results, and mail transport ports |

This is a partial validation record, not a completed compatibility certification. It does not satisfy all of the [first stable release requirements](../../CONTRIBUTING.md#readiness-before-100). A separate [Thunderbird laboratory result](thunderbird.md#recorded-validation) is recorded; Apple Mail results remain unrecorded.

## What Users Do

1. Add the mailbox address in Outlook.
2. Enter the mailbox password when prompted.
3. Outlook should discover IMAP/SMTP settings through `POST /autodiscover/autodiscover.xml`.

## Admin Validation

- verify `autodiscover.<domain>` resolves publicly
- verify HTTPS certificate is valid
- verify the mailbox domain is allowed in ENV mode or present in YAML mode

## Notes

The application returns a neutral response on `GET /autodiscover/autodiscover.xml` to handle generic probes safely.
