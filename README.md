# AI Agent Demo

A conversational AI chatbot built with Chainlit and LangChain.

## Tech Stack

- **UI Framework**: [Chainlit](https://docs.chainlit.io/) - Conversational AI interface
- **LLM Framework**: [LangChain](https://python.langchain.com/) + [LangGraph](https://langchain-ai.github.io/langgraph/) - LLM application framework
- **LLM Provider**: OpenAI (GPT-5-nano)
- **Language**: Python 3.12
- **Package Manager**: [uv](https://docs.astral.sh/uv/) - Fast Python package manager
- **Development**: DevContainer (Docker-based development environment)

## Quick Start (For Users)

To run the application:

**Prerequisites:**
- Docker
- OpenAI API key

**Steps:**

1. **Clone the repository**
   ```bash
   git clone https://github.com/coziro/ai-agent-demo.git
   cd ai-agent-demo
   ```

2. **Set up your API key**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and add your OpenAI API key (get it from https://platform.openai.com/api-keys)

3. **Run with Docker Compose**
   ```bash
   docker-compose up
   ```

4. **Open your browser**
   - Visit http://localhost:8000

To stop the application, press `Ctrl+C` or run `docker-compose down`.

## Development Setup

For developers who want to modify the code:

**Prerequisites:**
- Docker
- VS Code with Dev Containers extension
- OpenAI API key

**Setup Steps:**

1. **Clone the Repository**
   ```bash
   git clone https://github.com/coziro/ai-agent-demo.git
   cd ai-agent-demo
   ```

2. **Set Up Environment Variables**

   Create a `.env` file from the example:
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add your OpenAI API key:
   ```bash
   OPENAI_API_KEY=sk-proj-your-actual-api-key-here
   ```

   Get your API key from: https://platform.openai.com/api-keys

3. **Open in DevContainer**
   - Open the project in VS Code
   - When prompted, click "Reopen in Container"
   - Or use Command Palette: `Dev Containers: Reopen in Container`
   - Wait for the container to build (dependencies are installed automatically)

4. **Run the Application**

   This project includes two implementations to compare LangChain and LangGraph:

   **LangChain version (with streaming):**
   ```bash
   uv run chainlit run app_langchain.py
   ```

   **LangGraph version (basic graph implementation):**
   ```bash
   uv run chainlit run app_langgraph.py
   ```

   The application will be available at: http://localhost:8000

## Project Structure

```
ai-agent-demo/
├── .devcontainer/          # DevContainer configuration
│   ├── devcontainer.json
│   └── Dockerfile
├── .chainlit/              # Chainlit configuration and runtime files
│   ├── config.toml         # Chainlit settings
│   └── translations/       # UI translations (Japanese, English)
├── .claude/                # Claude Code context management
│   ├── context.md          # Current work context
│   ├── decisions.md        # Design decisions
│   ├── todo.md             # Task management
│   └── references.md       # Reference links and documentation
├── notebooks/              # Jupyter notebooks for experimentation
├── app_langchain.py        # Chainlit app with LangChain (streaming)
├── app_langgraph.py        # Chainlit app with LangGraph (basic)
├── chainlit.md             # Chainlit welcome screen
├── docker-compose.yml      # Docker Compose configuration
├── pyproject.toml          # Python dependencies
├── uv.lock                 # Dependency lock file
├── .env.example            # Environment variable template
├── LICENSE                 # MIT License
├── CLAUDE.md               # Claude Code project guide
└── README.md               # This file
```

## Development

### Using uv

```bash
# Install dependencies
uv sync

# Add a new dependency
# 1. Edit pyproject.toml, add to dependencies array
# 2. Run:
uv sync

# Run the app (LangChain version with streaming)
uv run chainlit run app_langchain.py

# Run the app (LangGraph version)
uv run chainlit run app_langgraph.py

# Run with auto-reload (development mode)
uv run chainlit run app_langchain.py -w
```

### Jupyter Notebooks

The project includes Jupyter support for experimentation:

```bash
# Notebooks are in the notebooks/ directory
# Open .ipynb files in VS Code's Jupyter extension
```

### Claude Code Context Management

This project uses `.claude/` directory to preserve context across Claude Code sessions:

- **context.md**: Current work in progress
- **decisions.md**: Important design decisions
- **todo.md**: Task tracking
- **references.md**: Documentation links

See [CLAUDE.md](CLAUDE.md) for more details.

## Contributing

This is a personal learning project, but suggestions and feedback are welcome! Feel free to open an issue or submit a pull request.
