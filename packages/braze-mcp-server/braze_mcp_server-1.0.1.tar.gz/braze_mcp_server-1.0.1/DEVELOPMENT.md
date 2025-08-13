# Braze MCP Server - Development Guide

This guide covers development setup, contribution guidelines, and internal documentation for the Braze MCP Server.

## Table of Contents

- [Development Setup](#development-setup)
  - [Prerequisites](#prerequisites)
  - [Quick Development Setup](#quick-development-setup)
- [Documentation Standards](#documentation-standards)
- [Adding New Tools](#adding-new-tools)
- [Available Make Targets](#available-make-targets)
  - [Code Quality & Testing](#code-quality--testing)
  - [Development](#development)
  - [Build & Distribution](#build--distribution)
- [Testing](#testing)
- [Development: Run from Source](#development-run-from-source)
  - [Direct Binary Path](#direct-binary-path)
  - [Alternative Installation Methods](#alternative-installation-methods)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [Release Process](#release-process)
- [Environment Variables for Development](#environment-variables-for-development)

## Development Setup

### Prerequisites

This project uses [uv](https://github.com/astral-sh/uv) for dependency management and Python package handling.

#### Installing uv

**macOS and Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

For more installation options, see the [uv documentation](https://docs.astral.sh/uv/getting-started/installation/).

### Quick Development Setup

```bash
# Clone the repository
git clone <repository-url>
cd braze_mcp_server

# Install dependencies and set up development environment
make install

# Run tests to verify setup
make test
```

## Documentation Standards

This project uses **strict docstring conventions** for auto-generating MCP tool metadata. All tool functions must follow Google-style docstrings:

```python
async def my_tool_function(ctx: Context, param1: str, param2: Optional[int] = None) -> dict:
    """Brief description of what the function does.
    Can be multi-line.
    
    Args:
        ctx: The MCP context
        param1: Description of param1
        param2: Description of param2 with default behavior
        
    Returns:
        Description of the return value structure
    """
```

**📖 See [docs/DOCSTRING_CONVENTIONS.md](docs/DOCSTRING_CONVENTIONS.md) for complete requirements and validation details.**

**🛑 Functions with invalid docstrings will FAIL to register and cause build errors.**

## Adding New Tools

Create modules in `src/braze_mcp/tools/` with `__register_mcp_tools__ = True` - tools are automatically discovered:

```python
# src/braze_mcp/tools/my_tools.py
__register_mcp_tools__ = True

async def my_function(ctx: Context, param: str) -> dict:
    # Implementation with proper docstring (see Documentation Standards above)
```

## Available Make Targets

### Code Quality & Testing
- **`make format`** - Auto-format code with ruff
- **`make lint`** - Check code quality with ruff
- **`make type-check`** - Run type checking with mypy
- **`make security-check`** - Run code vulnerability checks with bandit
- **`make test`** - Run all tests with pytest (and creates a coverage report)
- **`make precommit`** - Run type-check, format, lint, and test in sequence

### Development
- **`make install`** - Install dependencies and set up development environment
- **`make dev-install`** - Quick development installation (if dependencies already installed)
- **`make run`** - Run the MCP server (requires an MCP client to test with)

The project includes a git pre-commit hook that automatically runs `make precommit` before each commit to ensure code quality.

### Build & Distribution
- **`make build`** - Build the package distribution files
- **`make install-tool`** - Install as a binary tool for production use

## Testing

```bash
# Run all tests
make test

# Run tests directly with uv
uv run pytest tests/

# Run specific test categories
uv run pytest tests/braze_mcp/tools/campaigns/
uv run pytest tests/braze_mcp/tools/events/
```

## Development: Run from Source

### Direct Binary Path
Use the direct path to avoid caching issues:

```json
{
  "mcpServers": {
    "braze": {
      "command": "/path/to/braze_mcp_server/.venv/bin/braze-mcp-server",
      "args": [],
      "cwd": "/path/to/braze_mcp_server",
      "env": {
        "BRAZE_API_KEY": "your-braze-api-key-here",
        "BRAZE_BASE_URL": "https://rest.iad-01.braze.com"
      }
    }
  }
}
```

**Development Notes:**
- **Restart your MCP client**: After code changes, disable and re-enable the Braze MCP server in your client (e.g., Cursor) to reload the server with updated code

### Alternative Installation Methods

#### Easy Setup (Recommended)

1. **Download and extract** the project:
   ```bash
   git clone <repository-url>
   cd braze_mcp_server
   ```

2. **Run the interactive setup script:**
   ```bash
   # For Cursor
   ./setup/setup_cursor_from_source.sh
   
   # For Claude Desktop
   ./setup/setup_claude_desktop.sh
   ```

3. **Follow the prompts** to enter your Braze API key and base URL

4. **Restart your MCP client**

The setup script will automatically install the server and configure your client! 🎉

#### Manual Setup (Alternative)

```bash
# Clone and install the binary
git clone <repository-url>
cd braze_mcp_server
make install-tool
```

Then configure your MCP client manually with the installed binary path.

## Project Structure

```
braze_mcp_server/
├── src/braze_mcp/
│   ├── main.py              # Entry point and command registration
│   ├── server.py            # FastMCP server with 2 main tools
│   ├── registry_builder.py  # Auto-discovery system for tools
│   ├── models/              # Pydantic models for API responses
│   ├── tools/               # Individual API function implementations
│   ├── utils/               # Context management, HTTP client, logging
│   └── prompts/             # LLM prompt templates
├── setup/                   # Installation scripts for different clients
├── tests/                   # Unit tests and real API validation tests
└── docs/                    # Documentation and conventions
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes following the coding standards
4. Run `make precommit` to ensure code quality
5. Submit a pull request

## Release Process

1. Update version in `pyproject.toml`
2. Create a git tag: `git tag v0.x.x`
3. Push the tag: `git push origin v0.x.x`
4. GitHub Actions will automatically build and publish to PyPI

## Environment Variables for Development

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `BRAZE_API_KEY` | ✅ | Your Braze REST API key | `c1234567-89ab-cdef-0123-456789abcdef-12` |
| `BRAZE_BASE_URL` | ✅ | Your Braze REST endpoint URL | `https://rest.iad-01.braze.com` |

For the complete list of Braze base URLs, see the [Braze documentation](https://www.braze.com/docs/api/basics/#endpoints).