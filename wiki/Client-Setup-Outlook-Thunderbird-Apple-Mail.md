# Client Setup: Outlook, Thunderbird, Apple Mail

This page is for the last mile: what your users should do once the service is deployed correctly.

## Outlook

Tell the user to:

1. Open Outlook.
2. Add a new mail account.
3. Enter the full email address.
4. Enter the password when prompted.

If the public Autodiscover endpoint is reachable and the address belongs to an allowed domain, Outlook should fetch the configuration automatically.

## Thunderbird

Tell the user to:

1. Open Thunderbird account setup.
2. Enter name, email address, and password.
3. Wait for Thunderbird to fetch settings.
4. Confirm the detected incoming and outgoing servers.

Thunderbird normally checks `/mail/config-v1.1.xml` or the `.well-known` variant.

## Apple Mail

For Apple Mail, the easiest path is the generated profile URL:

```text
https://autodiscover.example.com/mail/ios.mobileconfig?emailaddress=user@example.com
```

The user should:

1. Open the link in Safari.
2. Download the configuration profile.
3. Install the profile in Settings or System Settings.
4. Enter the mailbox password when prompted.

Unsigned profiles may show a warning. That is expected unless you manage signed profiles through MDM.

## If setup fails

Check:

- the email domain is in `ALLOWED_DOMAINS`,
- the client can reach the public HTTPS endpoint,
- DNS points to the right reverse proxy,
- the returned IMAP and SMTP hostnames are valid.
