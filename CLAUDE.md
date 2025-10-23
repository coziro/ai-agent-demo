# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Environment

This project uses **DevContainers** for a consistent development environment. The container is based on `ghcr.io/astral-sh/uv:python3.12-bookworm-slim` and includes Python 3.12 with `uv` for dependency management.

## Dependency Management

This project uses `uv` for Python dependency management:

- **Install dependencies**: `uv sync`
- **Install with frozen lockfile**: `uv sync --frozen`
- **Add a new dependency**: Add to `pyproject.toml` dependencies array, then run `uv sync`

Dependencies are defined in [pyproject.toml](pyproject.toml) and locked in `uv.lock`.

## Running Code

- **Run main script**: `uv run python main.py`
- **Run Chainlit app**: `uv run chainlit run app.py`
- **Run Jupyter notebooks**: Open `.ipynb` files in [notebooks/](notebooks/) directory using VS Code's Jupyter extension

## Project Structure

- **DevContainer configuration**: [.devcontainer/](.devcontainer/) - Contains Dockerfile and devcontainer.json for containerized development
- **Notebooks**: [notebooks/](notebooks/) - Jupyter notebooks for experimentation and demos
- **Main entry point**: [main.py](main.py) - Simple Python script entry point
- **Chainlit app**: [app.py](app.py) - Chainlit chatbot application
- **Chainlit configuration**: [.chainlit/](.chainlit/) - Chainlit settings and translations

## Chainlit Application

This project includes a Chainlit-based conversational AI application:

- **Main application**: [app.py](app.py) - Currently a simple echo bot that uses the `@cl.on_message` decorator
- **Configuration**: [.chainlit/config.toml](.chainlit/config.toml) - UI settings, feature flags, and session management
- **Welcome screen**: [chainlit.md](chainlit.md) - Markdown content shown when users first open the app
- **Translations**: Only Japanese (`ja.json`) and English (`en-US.json`) are maintained; other languages were removed but can be restored from git history if needed

### Chainlit Configuration Notes

- Translation files use human-readable Japanese characters (not Unicode escapes) for maintainability
- Runtime files (`.chainlit/*.db`, `.chainlit/.files/`, `.chainlit/cache/`) are gitignored
- Configuration and translation files are version-controlled for team consistency

## Important Notes

- Jupyter and ipykernel are included as dependencies for notebook support
- The DevContainer automatically installs VS Code extensions: Python, Jupyter, and Claude Code
- When working inside the DevContainer, each Claude Code session is independent and won't have memory of conversations from outside the container
