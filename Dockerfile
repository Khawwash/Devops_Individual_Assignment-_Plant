FROM python:3.12-slim

# Prevent .pyc, ensure unbuffered logs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/app

WORKDIR /app

# Only copy reqs first, so we leverage layer cache
COPY requirements.txt ./
RUN python -m pip install --upgrade pip \
 && python -m pip install -r requirements.txt

# Copy source
COPY src ./src
COPY .env.example ./.env.example

# Create a mount point for local data (SQLite file)
VOLUME ["/data"]

EXPOSE 3000

# (Optional) Healthcheck (if you already have /health)
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:3000/health', timeout=2)" || exit 1

# Gunicorn: 2 workers is fine for this demo
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:3000", "src.components.Backend.wsgi:app"]
