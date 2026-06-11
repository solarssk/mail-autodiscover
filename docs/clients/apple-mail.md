# Apple Mail

## What Users Do

1. Open the generated `.mobileconfig` URL in Safari.
2. Download and install the profile.
3. Enter the mailbox password when prompted by iOS or macOS.

Example:

```text
https://autodiscover.example.com/mail/ios.mobileconfig?emailaddress=user@example.com
```

## Important Notes

- generated profiles are unsigned by default
- unsigned-profile warning on iOS/macOS is expected
- profiles do not contain mailbox passwords
- re-downloading the same profile updates it because identifiers are stable per mailbox

## Managed Environments

If you need signed profiles, sign the file externally before distribution.
