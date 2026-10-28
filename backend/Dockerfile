FROM python:3.12-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY alembic.ini ./
COPY alembic ./alembic
COPY scripts ./scripts
RUN chmod +x ./scripts/start.sh

# Run as an unprivileged user. The service never needs root, and a container that
# drops it limits what a compromise of the app can do to the host.
RUN useradd --create-home --uid 10001 appuser
USER appuser

EXPOSE 8000

# Reports the container unhealthy when the app stops answering. Uses the Python
# standard library rather than curl, which the slim base image does not ship.
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health', timeout=3)"

# One container, two processes: `scripts/start.sh` runs `alembic upgrade head`
# (idempotent, so a restart that finds the schema already current just moves
# on), then starts uvicorn and an RQ worker on the 'documents' queue
# concurrently via `wait -n`, so a crash in either one stops the container
# with that process's exit status instead of being silently absorbed by the
# other staying up.
CMD ["./scripts/start.sh"]
