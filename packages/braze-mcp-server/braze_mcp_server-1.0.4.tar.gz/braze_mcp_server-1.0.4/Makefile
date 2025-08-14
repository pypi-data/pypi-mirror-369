.PHONY: format lint test precommit run type-check install dev-install build install-tool

# Precommit workflow targets
format:
	uv run ruff format src/ tests/

lint:
	uv run ruff check --fix src/ tests/

type-check:
	uv run mypy --implicit-optional src/

security-check:
	uv run bandit -r src/

test: install
	uv run pytest --cov=src --cov-fail-under=80 tests/

# Run all precommit checks
precommit: type-check security-check format lint test

# Development targets
# Install dependencies and set up development environment
install:
	uv sync --extra dev
	uv pip install -e .

# Quick development installation (if dependencies already installed)
dev-install:
	uv pip install -e .

# Build the package
build:
	uv build

# Install as a binary tool (for production use)
install-tool:
	uv tool install . --force --native-tls

# Create distribution package with setup script for Cursor
dist-with-setup-cursor:
	make build
	mkdir -p build/braze-mcp-distribution-cursor
	cp dist/braze_mcp_server-0.1.0-py3-none-any.whl build/braze-mcp-distribution-cursor/
	cp setup/setup_cursor_from_wheel.sh build/braze-mcp-distribution-cursor/setup_cursor_from_wheel.sh
	cp README.md build/braze-mcp-distribution-cursor/
	tar -czf dist/braze-mcp-distribution-cursor.tar.gz -C build braze-mcp-distribution-cursor
	rm -rf build/

# Create distribution package with setup script for Claude Desktop
dist-with-setup-claude:
	make build
	mkdir -p build/braze-mcp-distribution-claude
	cp dist/braze_mcp_server-0.1.0-py3-none-any.whl build/braze-mcp-distribution-claude/
	cp setup/setup_claude_from_wheel.sh build/braze-mcp-distribution-claude/setup_claude_from_wheel.sh

	cp README.md build/braze-mcp-distribution-claude/
	tar -czf dist/braze-mcp-distribution-claude.tar.gz -C build braze-mcp-distribution-claude
	rm -rf build/

# Create both distribution packages
dist-with-setup: dist-with-setup-cursor dist-with-setup-claude

# PyPI publishing targets
publish-test:
	@echo "📦 Building and publishing to Test PyPI..."
	uv build
	uv run twine upload --repository testpypi dist/*

publish:
	@echo "📦 Building and publishing to PyPI..."
	@echo "⚠️  This will publish to the real PyPI. Are you sure? (Press Ctrl+C to cancel)"
	@read -p "Enter 'yes' to continue: " confirm && [ "$$confirm" = "yes" ] || exit 1
	uv build
	uv run twine upload dist/*

# Clean build artifacts
clean:
	rm -rf dist/ build/ *.egg-info/

run:
	uv run src/braze_mcp/main.py
