# Braze MCP Server - Technical Documentation

## Project Overview

The **Braze MCP Server** is a Model Context Protocol (MCP) server that provides comprehensive read-only access to Braze's REST API through Large Language Model tooling. This enables AI assistants and other MCP clients to interact with Braze workspace data, analytics, and campaign management functions without exposing PII or write operations.

### Key Statistics
- **2 main MCP tools** (`list_functions` and `call_function`)
- **38 Braze API functions** across 15 categories
- **Read-only operations** with strict security focus
- **Python 3.12+** requirement with modern async architecture

## Architecture Overview

### Core Components

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
├── docs/                    # Documentation and conventions
├── DEVELOPMENT.md           # Development setup and contribution guide
└── README.md                # User-facing documentation
```

### MCP Server Architecture

The server uses a **two-layer architecture**:

1. **MCP Layer**: Two main tools exposed to clients
   - `list_functions()` - Discovers and lists all available Braze API functions
   - `call_function(function_name, parameters)` - Executes specific Braze API functions

2. **Tool Layer**: 38 individual Braze API functions auto-discovered from `tools/` modules
   - Functions marked with `__register_mcp_tools__ = True` are automatically registered
   - Strict docstring validation ensures consistent metadata generation
   - Type hints and introspection provide parameter validation

### Auto-Discovery System

The registry builder (`registry_builder.py`) uses Python reflection to:
- Scan `braze_mcp.tools.*` modules for functions marked with `__register_mcp_tools__ = True`
- Extract metadata from docstrings using Google-style conventions
- Validate docstring format (STRICT mode - invalid docstrings fail registration)
- Generate JSON schema for parameters and return types
- Build function registry with implementation references

## API Functions by Category

### Campaigns (3 functions)
- `get_campaign_list` - Export list with metadata, pagination, filtering
- `get_campaign_details` - Detailed information for specific campaigns
- `get_campaign_dataseries` - Time series analytics data

### Canvases (4 functions)
- `get_canvas_list` - Export list with metadata
- `get_canvas_details` - Detailed Canvas information including steps/variants
- `get_canvas_data_summary` - Summary analytics for performance
- `get_canvas_data_series` - Time series analytics data

### Catalogs (3 functions)
- `get_catalogs` - List all catalogs in workspace
- `get_catalog_items` - Multiple catalog items with pagination
- `get_catalog_item` - Specific catalog item by ID

### Events (3 functions)
- `get_events_list` - Custom events recorded for app
- `get_events_data_series` - Time series data for custom events
- `get_events` - Detailed event data with pagination

### KPI Analytics (4 functions)
- `get_new_users_data_series` - Daily new user counts
- `get_dau_data_series` - Daily Active Users time series
- `get_mau_data_series` - Monthly Active Users time series
- `get_uninstalls_data_series` - App uninstall time series

### Additional Categories
- **Purchases** (3): Product lists, revenue/quantity series
- **Segments** (3): List, details, analytics data series
- **Sessions** (1): App session time series data
- **Subscription Groups** (2): User subscription management
- **SDK Authentication** (1): Authentication keys management
- **Messages** (1): Scheduled broadcasts
- **Preference Centers** (2): List and detailed preference center data
- **CDI Integrations** (2): Integration management and sync status
- **Templates** (4): Content blocks and email templates
- **Custom Attributes** (1): App custom attributes export
- **Sends** (1): Campaign send analytics

## Development Standards

### Docstring Conventions (STRICT)

**All tool functions MUST follow Google-style docstrings** or registration fails:

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

**Critical Requirements:**
- `Args:` and `Returns:` sections (case-insensitive)
- Document ALL parameters except `ctx`
- Proper indentation (4+ spaces for descriptions)
- Format: `param_name: description`

**Validation Enforcement:**
- Functions validate during registration
- Invalid docstrings cause build failures
- Pre-commit hooks prevent invalid docstrings
- Manual validation: `uv run python scripts/validate_docstrings.py`

### Code Quality Standards

**Build System:** Uses `uv` for dependency management and Python package handling

**Quality Tools:**
- **Formatting:** `ruff format` (100 char line length)
- **Linting:** `ruff check` with comprehensive rules
- **Type Checking:** `mypy` with implicit optionals
- **Security:** `bandit` for vulnerability scanning
- **Testing:** `pytest` with 80% coverage requirement

**Available Make Targets:**
```bash
# Code Quality
make format          # Auto-format with ruff
make lint            # Check and fix code quality
make type-check      # Run mypy type checking
make security-check  # Run bandit security scan
make test            # Run tests with coverage
make precommit       # Run all quality checks

# Development
make install         # Install dependencies and dev setup
make dev-install     # Quick dev installation
make run             # Run MCP server locally
make build           # Build distribution packages
make install-tool    # Install as binary tool
```

### Testing Strategy

**Three-tier Testing Approach:**

1. **Unit Tests** (`tests/braze_mcp/`):
   - Tool function logic validation
   - Parameter handling and validation
   - Error handling scenarios
   - Mock API responses

2. **Integration Tests** (`tests/braze_mcp/tools/`):
   - Category-specific tool testing
   - HTTP client behavior
   - Response parsing and model validation

3. **Real API Validation Tests** (`tests/validation/`):
   - Tests against actual Braze API endpoints
   - Requires real workspace data
   - Disabled by default, enabled with `BRAZE_REAL_API_TEST=1`
   - Organized by tool category

**Test Execution:**
```bash
# Regular tests (mocked)
make test

# Real API tests (requires credentials)
BRAZE_REAL_API_TEST=1 \
BRAZE_API_KEY=your_key \
BRAZE_BASE_URL=https://your.endpoint \
uv run pytest tests/validation/ -m real_api -v
```

## Configuration and Deployment

### Environment Variables

**Required:**
- `BRAZE_API_KEY` - Braze REST API key with appropriate scopes
- `BRAZE_BASE_URL` - Braze REST endpoint (e.g., `https://rest.iad-01.braze.com`)

**Optional:**
- `LOG_LEVEL` - Logging level (default: INFO)

### API Key Scopes

The server requires specific API key scopes for each endpoint:

| Function Category | Required Scope |
|------------------|----------------|
| Campaigns | `campaigns.list`, `campaigns.details`, `campaigns.data_series` |
| Canvases | `canvas.list`, `canvas.details`, `canvas.data_series`, `canvas.data_summary` |
| Catalogs | `catalogs.get`, `catalogs.get_items`, `catalogs.get_item` |
| Events | `events.list`, `events.data_series`, `events.get` |
| KPI | `kpi.new_users.data_series`, `kpi.dau.data_series`, `kpi.mau.data_series`, `kpi.uninstalls.data_series` |
| Purchases | `purchases.product_list`, `purchases.revenue_series`, `purchases.quantity_series` |
| Segments | `segments.list`, `segments.details`, `segments.data_series` |
| Sessions | `sessions.data_series` |
| Templates | `content_blocks.list`, `content_blocks.info`, `templates.email.list`, `templates.email.info` |
| Other categories | Various specific scopes (see README.md for complete mapping) |

### Installation Methods

**1. Automated Setup (Recommended):**
```bash
# For Cursor
./setup/setup_cursor_from_source.sh

# For Claude Desktop  
./setup/setup_claude_desktop.sh
```

**2. Manual Installation:**
```bash
git clone <repository>
cd braze_mcp_server
make install-tool

# Configure MCP client with:
# Command: /Users/USERNAME/.local/bin/braze-mcp-server
# Environment: BRAZE_API_KEY, BRAZE_BASE_URL
```

**3. Development Setup:**
```bash
make install          # Full development environment
make dev-install      # Quick development setup
make run             # Run from source
```

## Security Considerations

### Read-Only Design
- **No write operations** - Server only implements GET endpoints
- **No PII exposure** - Functions designed to avoid personally identifiable information
- **Minimal scope principle** - API key should have only required scopes

### Error Handling
- Structured error responses with consistent format
- Internal errors logged but sanitized for client responses
- Parameter validation prevents malformed requests
- HTTP client configured with appropriate timeouts and limits

### Authentication
- API key passed via environment variables (not in code)
- HTTPS enforced for all Braze API communications
- Context-based authentication with proper lifecycle management

## Usage Examples

### Working with Cursor/Claude Desktop

**"Show me my recent campaigns"**
```
Uses get_campaign_list to display campaigns with IDs, names, last edited dates
```

**"Get performance data for campaign X from last month"**
```
Uses get_campaign_dataseries with date filtering to show analytics
```

**"What Canvas templates do I have available?"**
```
Uses get_canvas_list to show all Canvas configurations and metadata
```

**"List all my product catalog items"**
```
Uses get_catalogs and get_catalog_items to display product information
```

## Data Models

The server uses **Pydantic models** for type safety and validation:

- `models/campaigns.py` - Campaign list, details, and data series models
- `models/canvases.py` - Canvas configurations and analytics models  
- `models/catalogs.py` - Catalog and catalog item models
- `models/events.py` - Custom event and analytics models
- `models/common.py` - Shared models and utilities
- Additional models for each API category

**Response Structure:**
```json
{
  "data": { /* Pydantic model data */ },
  "schema": {
    "model_name": "CampaignListResponse",
    "fields": { /* JSON schema */ },
    "description": "Response data structured according to the model"
  }
}
```

## Development Workflow

### Adding New Tools

1. **Create module** in `src/braze_mcp/tools/`:
```python
# src/braze_mcp/tools/my_tools.py
__register_mcp_tools__ = True

async def my_function(ctx: Context, param: str) -> dict:
    """Function description following docstring conventions.
    
    Args:
        ctx: The MCP context
        param: Parameter description
        
    Returns:
        Description of return value
    """
    # Implementation
```

2. **Add Pydantic models** in `src/braze_mcp/models/`
3. **Write tests** in `tests/braze_mcp/tools/`
4. **Add validation tests** in `tests/validation/`
5. **Run quality checks**: `make precommit`

### Git Workflow

- **Pre-commit hooks** automatically run `make precommit`
- **Quality gates** prevent commits with failing tests or linting issues
- **Docstring validation** prevents registration of invalid functions
- **Coverage requirements** ensure adequate test coverage (80% minimum)

## Distribution and Packaging

### Build Targets
```bash
make build                    # Create wheel distribution
make dist-with-setup-cursor   # Cursor distribution with setup script
make dist-with-setup-claude   # Claude Desktop distribution with setup script
make dist-with-setup         # Both distributions
```

### Package Structure
- **Wheel format** for Python package distribution
- **Setup scripts** for automated client configuration
- **Documentation** included in distributions
- **Binary installation** via `uv tool install`

## Monitoring and Debugging

### Logging
- **Structured logging** with configurable levels
- **Context-aware** logging throughout request lifecycle
- **HTTP request/response** logging for debugging
- **Function registration** logging for troubleshooting

### Error Tracking
- **Comprehensive error handling** with specific error types
- **Function registration failures** clearly reported
- **API communication errors** properly categorized
- **Parameter validation errors** with helpful messages

This documentation provides a complete technical overview of the Braze MCP Server project, covering architecture, development practices, security considerations, and operational aspects.