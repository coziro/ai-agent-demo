# uvとPython 3.12が含まれたベースイメージを使用
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# 開発ツールをインストール
RUN apt-get update && apt-get install -y \
    git \
    curl \
    vim \
    && rm -rf /var/lib/apt/lists/*

# 作業ディレクトリを設定
WORKDIR /workspaces/ai-agent-demo

# 依存関係ファイルをコピー
COPY pyproject.toml uv.lock ./

# 依存関係をインストール
RUN uv sync --frozen

# ソースコードをコピー
COPY . .
