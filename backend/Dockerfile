FROM python:3.12-slim@sha256:ccc7089399c8bb65dd1fb3ed6d55efa538a3f5e7fca3f5988ac3b5b87e593bf0 AS base

WORKDIR /app

# Tectonic runtime libraries + binary (HTTPS/TLS secures transit)
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl fontconfig libgraphite2-3 libharfbuzz0b libicu76 libssl3t64 && \
    curl -sSL -o /tmp/tectonic.tar.gz \
      https://github.com/tectonic-typesetting/tectonic/releases/download/tectonic%400.15.0/tectonic-0.15.0-x86_64-unknown-linux-gnu.tar.gz && \
    tar xz -C /usr/local/bin/ -f /tmp/tectonic.tar.gz && \
    rm /tmp/tectonic.tar.gz && \
    apt-get purge -y curl && apt-get autoremove -y && rm -rf /var/lib/apt/lists/*

# Pre-warm Tectonic package cache (downloads amsmath, amssymb, etc. at build time)
RUN printf '\\documentclass{article}\n\\usepackage{amsmath,amssymb}\n\\usepackage[margin=1in]{geometry}\n\\usepackage{enumitem}\n\\usepackage{fancyhdr}\n\\begin{document}\n$x^2$\n\\end{document}\n' > /tmp/warmup.tex && \
    tectonic /tmp/warmup.tex && \
    rm -f /tmp/warmup.*

# -------------------------------------------------------------------
# Development: includes dev deps, hot reload, runs as root (acceptable)
# -------------------------------------------------------------------
FROM base AS development

COPY requirements-dev.txt requirements.txt ./
RUN pip install --no-cache-dir -r requirements-dev.txt

COPY . .

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# -------------------------------------------------------------------
# Production: minimal deps, non-root user, no dev tools
# -------------------------------------------------------------------
FROM base AS production

# Production: pinned versions from lock file for reproducible builds
COPY requirements.lock .
RUN pip install --no-cache-dir -r requirements.lock

COPY . .

# Non-root user for least-privilege security
RUN addgroup --system app && adduser --system --ingroup app app
USER app

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--forwarded-allow-ips", "10.0.0.0/8,172.16.0.0/12,192.168.0.0/16"]
