"""Public landing page and robots.txt (no sensitive configuration)."""

from html import escape


def landing_page_html(app_name: str) -> str:
    """Render the public root page without exposing mail configuration."""
    title = escape(app_name, quote=False)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="robots" content="noindex, nofollow">
  <meta name="theme-color" content="#fafaf8" media="(prefers-color-scheme: light)">
  <meta name="theme-color" content="#141719" media="(prefers-color-scheme: dark)">
  <title>{title}</title>
  <link rel="icon" href="/favicon.ico" sizes="16x16 32x32 48x48">
  <link rel="apple-touch-icon" href="/apple-touch-icon.png" sizes="180x180">
  <style>
    :root {{
      color-scheme: light dark;
      font-family: system-ui, -apple-system, sans-serif;
      --page: #fafaf8;
      --text: #20282c;
      --muted: #59666b;
      --border: #d8dedc;
      --accent: #286350;
      --accent-hover: #174b3a;
    }}
    @media (prefers-color-scheme: dark) {{
      :root {{
        --page: #141719;
        --text: #edf0ed;
        --muted: #a6b1ae;
        --border: #37413e;
        --accent: #9bc5b3;
        --accent-hover: #c3e3d4;
      }}
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--page);
      color: var(--text);
      line-height: 1.6;
    }}
    .page {{
      width: min(100% - 3rem, 64rem);
      margin-inline: auto;
      overflow-wrap: anywhere;
    }}
    header {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 0.75rem 2rem;
      padding-block: 1.5rem;
      border-bottom: 1px solid var(--border);
    }}
    .brand {{ display: flex; align-items: center; gap: 0.75rem; font-weight: 600; }}
    .brand span {{ min-width: 0; }}
    .brand svg {{ flex-shrink: 0; color: var(--accent); }}
    a {{
      color: var(--accent);
      text-underline-offset: 0.25em;
      touch-action: manipulation;
    }}
    a:hover {{ color: var(--accent-hover); }}
    a:focus-visible {{
      outline: 3px solid var(--accent);
      outline-offset: 4px;
    }}
    .skip {{
      position: absolute;
      top: 0.75rem;
      left: 1.5rem;
      transform: translateY(-200%);
      padding: 0.5rem 1rem;
      background: var(--page);
      border: 1px solid var(--border);
    }}
    .skip:focus-visible {{ transform: translateY(0); }}
    .project {{ display: inline-flex; align-items: center; min-height: 2.75rem; }}
    .hero {{
      display: grid;
      grid-template-columns: 1.5fr 1fr;
      align-items: center;
      gap: 3rem;
      padding-block: clamp(3rem, 7vw, 5.5rem);
    }}
    .method, .transport {{
      font-family: ui-monospace, SFMono-Regular, Consolas, monospace;
      font-size: 0.75rem;
      color: var(--muted);
    }}
    h1, h2, h3 {{ font-weight: 550; line-height: 1.15; text-wrap: balance; }}
    h1 {{
      margin: 0 0 1.5rem;
      font-size: clamp(2.25rem, 5vw, 3.25rem);
      letter-spacing: -0.045em;
    }}
    h2 {{ margin: 0; font-size: 1.125rem; }}
    h3 {{ margin: 0 0 0.25rem; font-size: 1.125rem; }}
    p {{ margin: 0; color: var(--muted); }}
    .intro {{ max-width: 31rem; font-size: 1.0625rem; }}
    .illustration {{ text-align: center; color: var(--accent); }}
    .illustration svg {{ display: block; width: 100%; max-width: 17rem; margin: auto; }}
    .transport {{ margin-top: 1rem; letter-spacing: 0.08em; }}
    .section-heading {{
      display: flex;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 0.75rem;
      padding-bottom: 1.25rem;
      border-bottom: 1px solid var(--border);
    }}
    .protocol {{
      display: grid;
      grid-template-columns: 1fr 1.25fr;
      align-items: baseline;
      gap: 1rem;
      padding-block: 1.5rem;
      border-bottom: 1px solid var(--border);
    }}
    .protocol p {{ font-size: 0.875rem; }}
    .endpoint {{ display: flex; flex-wrap: wrap; gap: 0.25rem 0.75rem; }}
    .method {{ color: var(--accent); }}
    code {{ font-family: ui-monospace, SFMono-Regular, Consolas, monospace;
            font-size: 0.75rem; color: var(--text); }}
    .guidance {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 3rem;
      padding-block: 2.5rem;
    }}
    .guidance h2 {{ margin-bottom: 0.75rem; }}
    .guidance p {{ font-size: 0.875rem; }}
    footer {{
      display: flex;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 0.5rem 2rem;
      padding-block: 1.25rem 2rem;
      border-top: 1px solid var(--border);
      font-size: 0.75rem;
      color: var(--muted);
    }}
    @media (max-width: 42rem) {{
      .hero {{ grid-template-columns: 1fr; gap: 2rem; }}
      .illustration {{ display: none; }}
      .protocol {{ grid-template-columns: 1fr; gap: 0.75rem; }}
      .guidance {{ grid-template-columns: 1fr; gap: 2rem; }}
    }}
  </style>
</head>
<body>
  <a class="skip" href="#main">Skip to content</a>
  <div class="page">
    <header>
      <div class="brand">
        <svg width="28" height="24" viewBox="0 0 28 24" fill="none"
             stroke="currentColor" stroke-width="1.5" aria-hidden="true" focusable="false">
          <rect x="1" y="3" width="26" height="18" rx="2"/>
          <path d="m2 4 12 9L26 4"/>
        </svg>
        <span translate="no">{title}</span>
      </div>
      <a class="project" href="https://github.com/solarssk/mail-autodiscover">Project on GitHub</a>
    </header>
    <main id="main" tabindex="-1">
      <section class="hero" aria-labelledby="page-heading">
        <div>
          <h1 id="page-heading">Mail client<br>configuration.</h1>
          <p class="intro">This host publishes connection settings for compatible mail apps.
            Add your account in your mail app; it can retrieve the settings from here.</p>
        </div>
        <div class="illustration" aria-hidden="true">
          <svg width="272" height="190" viewBox="0 0 272 190" fill="none"
               stroke="currentColor" stroke-width="1.5" focusable="false">
            <path d="M16 35h30m-20 20h20M226 135h30m-30 20h20"/>
            <rect x="56" y="30" width="160" height="130" rx="4"/>
            <path d="m57 32 79 65 79-65M57 158l57-57m101 57-57-57"/>
            <path d="M121 14h30M121 176h30" stroke-dasharray="2 4"/>
          </svg>
          <p class="transport">IMAP / SMTP</p>
        </div>
      </section>
      <section aria-labelledby="formats-heading">
        <div class="section-heading">
          <h2 id="formats-heading">Configuration formats</h2>
        </div>
        <article class="protocol">
          <div>
            <h3 translate="no">Outlook</h3>
            <p>Autodiscover XML for IMAP and SMTP.</p>
          </div>
          <div class="endpoint">
            <span class="method">POST</span>
            <code>/autodiscover/autodiscover.xml</code>
          </div>
        </article>
        <article class="protocol">
          <div>
            <h3 translate="no">Thunderbird</h3>
            <p>Autoconfig XML with optional POP3 settings.</p>
          </div>
          <div class="endpoint">
            <span class="method">GET</span>
            <code>/mail/config-v1.1.xml</code>
          </div>
        </article>
        <article class="protocol">
          <div>
            <h3 translate="no">Apple Mail</h3>
            <p>Mail account profiles for iOS and macOS.</p>
          </div>
          <div class="endpoint">
            <span class="method">GET</span>
            <code>/mail/ios.mobileconfig</code>
          </div>
        </article>
      </section>
      <section class="guidance" aria-label="Using this service">
        <div>
          <h2>Looking for your inbox?</h2>
          <p>Open your mail app or your provider&#39;s webmail.
            This address is not a webmail interface or administration panel.</p>
        </div>
        <div>
          <h2>No passwords here.</h2>
          <p>Your mail app handles sign-in directly with your mail server.
            This service does not ask for, store, or verify mailbox passwords.</p>
        </div>
      </section>
    </main>
    <footer>
      <span>Open-source mail autodiscovery.</span>
      <a href="https://github.com/solarssk/mail-autodiscover/tree/main/docs">
        Setup documentation
      </a>
    </footer>
  </div>
</body>
</html>"""


def robots_txt() -> str:
    """Discourage indexing of the autodiscovery host."""
    return "User-agent: *\nDisallow: /\n"
