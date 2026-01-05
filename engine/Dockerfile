FROM python:3.11-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Install build dependencies if needed
RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
COPY src/ src/
# Use uv to install dependencies
RUN uv pip install --system .

EXPOSE 8000

CMD ["uvicorn", "holon_engine.api:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
