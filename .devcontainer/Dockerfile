FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

RUN apt-get update && apt-get install -y \
    git \
    curl \
    vim \
    gh \
    libatomic1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspaces/ai-agent-demo

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen

COPY . .
