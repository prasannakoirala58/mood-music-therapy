FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends make \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app/backend

# Copy dependency manifest first — Docker layer cache: deps only rebuild when pyproject.toml changes
COPY backend/pyproject.toml backend/uv.lock ./

# Install dependencies (skip installing the project itself — we run src directly)
RUN uv sync --no-install-project

# Copy the root Makefile plus backend source so Docker can start the API through make
WORKDIR /app
COPY Makefile ./Makefile
COPY backend ./backend

# Default standalone container behavior: run the CLI pipeline.
# docker-compose overrides this with `make api` for the web backend.
CMD ["make", "run"]
