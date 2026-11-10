FROM docker.io/library/python:3.12-slim

WORKDIR /app

COPY pyproject.toml ./
COPY src/ ./src/

RUN pip install --no-cache-dir .

RUN useradd --create-home --uid 10001 telemetry
USER telemetry

EXPOSE 8000

CMD ["python", "-m", "telemetry.ingest", "--state", "48", "--parameter", "00060", "--limit", "5"]
