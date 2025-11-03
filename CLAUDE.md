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

## Static Type Checking

- This project uses **Pyright** with `typeCheckingMode = "standard"` (see `[tool.pyright]` in [pyproject.toml](pyproject.toml#L22)).
- Run checks locally with `uv run pyright`. Execute this command before committing (similar to Ruff).
- Pyright currently targets the `apps/` directory. Expand coverage or tighten strictness incrementally as type hints improve.
- DevContainer installs `libatomic1` to support Pyright’s `nodeenv` dependency; no extra setup is required inside the container.

## Running Code

- **Run Chainlit apps**: This project provides multiple implementations:
  - `uv run chainlit run apps/langchain_sync.py` - LangChain + Sync (complete response at once)
  - `uv run chainlit run apps/langchain_streaming.py` - LangChain + Streaming (real-time token display)
  - `uv run chainlit run apps/langgraph_sync.py` - LangGraph + Sync (graph-based agent)
  - `uv run chainlit run apps/langgraph_streaming.py` - LangGraph + Streaming (graph-based + real-time)
- **Run Jupyter notebooks**: Open `.ipynb` files in [notebooks/](notebooks/) directory using VS Code's Jupyter extension

### Implementation Matrix

This project demonstrates different implementation patterns:

|              | LangChain                   | LangGraph                  |
|--------------|-----------------------------|----------------------------|
| **Sync**     | `langchain_sync.py`         | `langgraph_sync.py`        |
| **Streaming**| `langchain_streaming.py`    | `langgraph_streaming.py`   |

**Terminology:**
- **Sync**: Displays the complete response at once (uses `ainvoke()`)
- **Streaming**: Displays tokens progressively in real-time (uses `astream()`)

Note: Both versions use async/await for non-blocking I/O operations.

### Jupyter Notebook Naming Convention

To distinguish between production notebooks (committed to git) and experimental notebooks (local only):

- **Production notebooks**: `descriptive_name.ipynb` - Committed to git, intended for team use
- **Experimental/temporary notebooks**: `tmp_*.ipynb` - Local only, automatically ignored by git

Examples:
- ✅ `langgraph_tutorial.ipynb` - Production notebook (committed)
- ✅ `tmp_test.ipynb` - Experimental notebook (gitignored)
- ✅ `tmp_langgraph.ipynb` - Experimental notebook (gitignored)

See [.claude/decisions.md](.claude/decisions.md) for the rationale behind this naming convention.

## Project Structure

- **DevContainer configuration**: [.devcontainer/](.devcontainer/) - Contains Dockerfile and devcontainer.json for containerized development
- **Notebooks**: [notebooks/](notebooks/) - Jupyter notebooks for experimentation and demos
- **Application implementations**: [apps/](apps/) - Multiple Chainlit app implementations demonstrating different patterns
  - [apps/langchain_sync.py](apps/langchain_sync.py) - LangChain + Sync
  - [apps/langchain_streaming.py](apps/langchain_streaming.py) - LangChain + Streaming
  - [apps/langgraph_sync.py](apps/langgraph_sync.py) - LangGraph + Sync
  - [apps/langgraph_streaming.py](apps/langgraph_streaming.py) - LangGraph + Streaming
  - [apps/README.md](apps/README.md) - Detailed comparison of implementations
- **Shared code library**: [src/ai_agent_demo/](src/ai_agent_demo/) - Reusable agent implementations
  - [src/ai_agent_demo/simple_chat/](src/ai_agent_demo/simple_chat/) - Simple chat agent (state, nodes, graph)
- **Chainlit configuration**: [.chainlit/](.chainlit/) - Chainlit settings and translations
- **Claude Code context**: [.claude/](.claude/) - Project context, decisions, and session notes for Claude Code

## Chainlit Application

This project includes a Chainlit-based conversational AI application:

- **Application implementations**: [apps/](apps/) - Multiple implementations demonstrating different patterns (see Implementation Matrix above)
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

## Development Workflow (Git Branch Strategy)

This project follows **GitHub Flow** to maintain a stable main branch:

### Branch Strategy

- **main branch**: Always in a deployable state, production-ready code only
- **Feature branches**: `feature/name`, `fix/name`, `refactor/name`
- **No direct commits to main** (except emergency hotfixes)

### Development Flow (Step-by-Step Process)

**IMPORTANT: Follow this process for ALL code changes to avoid mistakes.**

#### Step 1: Select a Task from todo.md

- Open [.claude/todo.md](.claude/todo.md)
- Choose a task to work on based on priority
- Understand the task's purpose, dependencies, and scope

#### Step 2: Create a Feature Branch

**Before writing any code**, create a feature branch:

```bash
git checkout main
git pull
git checkout -b feature/your-feature-name
```

**Naming conventions:**
- `feature/feature-name` - New features
- `fix/bug-name` - Bug fixes
- `refactor/target-name` - Code refactoring

#### Step 3: Plan Subtasks in context.md

**Do NOT start implementation immediately.** First, break down the task:

1. Document the task in [.claude/context.md](.claude/context.md) under "進行中のタスク"
2. List all necessary subtasks
3. Identify what you'll do vs. what Claude Code will do
4. **Get user agreement** on the subtask plan before proceeding

**Template for context.md:**
```markdown
#### [Task Name] - Start Date: YYYY-MM-DD

**Purpose:**
- What you're trying to achieve

**Implementation Approach:**
- Technical decisions and approach

**Branch:** `feature/branch-name`

**Current Status:**
- [ ] Subtask 1
- [ ] Subtask 2
- [ ] Subtask 3

**Your Work vs. Claude Code's Work:**

**Your Work (Learning/Review):**
- Items you want to do yourself

**Claude Code's Work:**
- Items to delegate to Claude Code

**Next Steps:**
1. Specific action 1
2. Specific action 2

**Related Files:**
- [file1.py](file1.py)
- [file2.py](file2.py)
```

#### Step 4: Execute Subtasks (With User Agreement)

**CRITICAL RULES:**
- ❌ **Do NOT execute subtasks immediately**
- ✅ **Discuss the subtask plan with the user first**
- ✅ **Get explicit confirmation** before starting implementation
- ✅ **Clarify which subtasks the user wants to do themselves**

**For each subtask:**
1. Confirm it's ready to be executed
2. Execute and test
3. Update context.md with progress
4. Commit changes with clear messages

#### Step 5: Create a Pull Request

```bash
gh pr create --title "Add feature X" --body "Description of changes"
```

#### Step 6: Review and Test

- Review code changes (especially code written by Claude Code)
- Test locally to ensure functionality
- Check for regressions in existing features

#### Step 7: Merge or Discard

**If successful:**
```bash
gh pr merge
```

**If unsuccessful:**
```bash
git checkout main
git branch -D feature/failed-feature
```

### Quick Checklist (Before Starting ANY Work)

Before writing code, ask yourself:

- [ ] Have I selected a task from todo.md?
- [ ] Am I on a feature branch? (Check with `git branch`)
- [ ] Have I documented the plan in context.md?
- [ ] Have I discussed the subtask plan with the user?
- [ ] Do I have user agreement to proceed?

**Exception (Direct commits to main allowed):**
- Updates to context.md or todo.md only
- Minor configuration changes (.gitignore, etc.)

### Pull Request Guidelines

Every PR should include:
- **Summary**: What changed and why
- **Testing instructions**: How to verify the changes work
- **Screenshots**: If UI changes are involved

### Working with Claude Code

- Ask Claude Code to create feature branches before starting work
- Request Claude Code to create Pull Requests with detailed descriptions
- **Always review Claude Code's changes** before merging to main
- Final merge decision is made by humans

### Special Cases

**`.claude/` directory files:**
- **context.md, todo.md**: Direct commits to main are acceptable (frequent updates, low risk)
- **decisions.md**: PR recommended (important design decisions)
- Rationale: See [.claude/decisions.md](.claude/decisions.md#claudeファイルのコミット方針---2025-10-26)

For detailed decision rationale, see [.claude/decisions.md](.claude/decisions.md#github-flowベースのブランチ戦略---2025-10-26).

## GitHub CLI (gh)

This project includes **GitHub CLI (`gh`)** for managing Pull Requests and GitHub operations from the command line:

### Common Commands

- **Create a Pull Request**:
  ```bash
  gh pr create --title "Add feature X" --body "Description of changes"
  ```

- **List Pull Requests**:
  ```bash
  gh pr list
  ```

- **View Pull Request details**:
  ```bash
  gh pr view [PR number]
  ```

- **Merge a Pull Request**:
  ```bash
  gh pr merge [PR number]
  ```

- **Check authentication status**:
  ```bash
  gh auth status
  ```

### Authentication

GitHub CLI is pre-authenticated in the DevContainer. If you need to re-authenticate:

```bash
gh auth login
```

**Security recommendation**: Use a [Fine-grained Personal Access Token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens) restricted to this repository only.

For more details, see the [GitHub CLI documentation](https://cli.github.com/).

## Important Notes

- Jupyter and ipykernel are included as dependencies for notebook support
- The DevContainer automatically installs VS Code extensions: Python, Jupyter, and Claude Code
- Each Claude Code session is independent, but context can be preserved using the `.claude/` directory files
