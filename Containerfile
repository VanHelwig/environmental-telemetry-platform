FROM docker.io/library/python:3.12-slim

WORKDIR /app

COPY pyproject.toml ./
COPY src/ ./src/

RUN pip install --no-cache-dir .

RUN useradd --create-home --uid 10001 telemetry
USER telemetry

ENTRYPOINT ["python", "-m", "telemetry.ingest"]
CMD ["--state", "48", "--parameter", "00060", "--limit", "5"]