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
- **Claude Code context**: [.claude/](.claude/) - Project context, decisions, and session notes for Claude Code

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

## Claude Code Context Management

This project uses a structured approach to preserve context across Claude Code sessions:

### Context Files (.claude/ directory)

- **[.claude/context.md](.claude/context.md)** - Current work in progress, session notes
- **[.claude/decisions.md](.claude/decisions.md)** - Important design decisions and their rationale
- **[.claude/todo.md](.claude/todo.md)** - Task tracking and prioritization
- **[.claude/references.md](.claude/references.md)** - Links, documentation, and references

### Usage

When starting a new Claude Code session (after VS Code restart or container rebuild):

1. Say: **".claude/context.mdを読んで、前回の続きをお願いします"**
2. Claude Code will read the context and continue where you left off
3. Update context files as you make progress or decisions

### Best Practices

- **Update context.md** when working on multi-session tasks
- **Record decisions in decisions.md** when making important architectural choices
- **Keep todo.md current** to track what's done and what's next
- **Add useful links to references.md** for future reference

All `.claude/` files are version-controlled for team collaboration.

## Important Notes

- Jupyter and ipykernel are included as dependencies for notebook support
- The DevContainer automatically installs VS Code extensions: Python, Jupyter, and Claude Code
- Each Claude Code session is independent, but context can be preserved using the `.claude/` directory files
