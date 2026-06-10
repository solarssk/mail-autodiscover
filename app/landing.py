"""Public landing page and robots.txt (no sensitive configuration)."""


def landing_page_html(app_name: str) -> str:
    title = _escape(app_name)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="robots" content="noindex, nofollow">
  <title>{title}</title>
  <link rel="icon" href="/favicon.ico" sizes="any">
  <link rel="apple-touch-icon" href="/apple-touch-icon.png">
  <style>
    :root {{ color-scheme: light dark; font-family: system-ui, sans-serif; }}
    body {{ margin: 0; min-height: 100vh; display: grid; place-items: center;
            background: #f4f6f8; color: #1a1a1a; }}
    @media (prefers-color-scheme: dark) {{
      body {{ background: #121418; color: #e8eaed; }}
      .card {{ background: #1e2228; border-color: #2d333b; }}
    }}
    .card {{ max-width: 32rem; padding: 2rem; border: 1px solid #d0d7de;
             border-radius: 12px; background: #fff; text-align: center; }}
    h1 {{ font-size: 1.25rem; margin: 0 0 0.75rem; }}
    p {{ margin: 0.5rem 0; line-height: 1.5; color: inherit; opacity: 0.85; }}
    a {{ color: #0969da; }}
  </style>
</head>
<body>
  <main class="card">
    <h1>{title}</h1>
    <p>This host provides <strong>mail client autodiscovery</strong> only
       (Outlook, Thunderbird, Apple Mail profiles).</p>
    <p>It is not a webmail interface or administration panel.</p>
    <p><a href="https://github.com/solarssk/autodiscover">Project on GitHub</a></p>
  </main>
</body>
</html>"""


def robots_txt() -> str:
    return "User-agent: *\nDisallow: /\n"


def _escape(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )
