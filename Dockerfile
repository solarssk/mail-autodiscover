# Pin to bookworm for predictable Debian security updates, and to an exact
# digest (not just the mutable tag) for a reproducible build starting point.
# Dependabot proposes digest bumps via .github/dependabot.yml (docker ecosystem).
FROM python:3.14-slim-bookworm@sha256:82bc3c539b8813ada9d68c63b40158fa002f7f33de9bf3312a3dfdc0620dff56

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY pyproject.toml README.md requirements.txt ./
COPY app ./app
# app/static includes favicon.ico and apple-touch-icon.png
# Runtime dependencies install from the hash-pinned lockfile (requirements.txt,
# regenerated with `pip-compile --generate-hashes`; see CONTRIBUTING.md) so the
# exact same versions and artifacts get installed on every build, not whatever
# happens to satisfy the >= bounds in pyproject.toml on a given day. The app
# itself installs with --no-deps since its dependencies are already locked.
# pip is removed after install: the app runs via uvicorn and never invokes pip
# at runtime, and pip vendors its own copies of packages like msgpack and
# pkg_resources/setuptools that periodically pick up CVEs of their own
# (unrelated to anything this app actually uses) if left in the shipped image.
RUN pip install --no-cache-dir --upgrade "pip>=26.1.2" \
    && pip install --no-cache-dir --require-hashes -r requirements.txt \
    && pip install --no-cache-dir --no-deps . \
    && pip uninstall -y pip

# CACHEBUST forces this layer to actually re-run on every build instead of
# being served from Docker's build cache indefinitely -- its cache key would
# otherwise depend only on this unchanging RUN command text and the base
# image's own pinned digest above, so apt-get upgrade silently stopped doing
# anything after the first build off a given digest (confirmed: every build
# log showed this step as "CACHED", including ones weeks apart) while this
# image kept shipping whatever OS packages existed at that one build. Passed
# as a real build-arg (docker-publish.yml uses run_id-run_attempt, unique
# per workflow run/retry -- not the commit SHA, which would stay identical
# across a workflow_dispatch or re-run on an unchanged commit and let the
# cache serve the same stale layer again) rather than left at its default,
# so every published image gets that day's Debian security patches
# regardless of how stale the pinned base digest is.
# Placed as late as possible, after COPY/pip install, so busting it doesn't
# also force those layers -- correctly keyed on actual file content -- to
# redo on every build.
ARG CACHEBUST=1
RUN : "${CACHEBUST}" \
    && apt-get update \
    && apt-get upgrade -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/* \
    && addgroup --system app \
    && adduser --system --ingroup app app

USER app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD python -c "import os, urllib.request; urllib.request.urlopen(f'http://127.0.0.1:{os.environ.get(\"CONTAINER_PORT\", \"8000\")}/health')"

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${CONTAINER_PORT:-8000} --no-access-log"]
