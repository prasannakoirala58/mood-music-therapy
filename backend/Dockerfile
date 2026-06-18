FROM python:3.11-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copy dependency manifest first — Docker layer cache: deps only rebuild when pyproject.toml changes
COPY pyproject.toml .

# Install dependencies (skip installing the project itself — we run src directly)
RUN uv sync --no-install-project

# Copy all source code
COPY . .

# Default: run the CLI pipeline
CMD ["uv", "run", "python", "src/pipeline.py"]
