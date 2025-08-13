# MCP Tool Docstring Conventions

**Required** docstring format for MCP tool functions. Functions with invalid docstrings **FAIL to register**.

## Format Requirements

```python
async def my_tool_function(ctx: Context, param1: str, param2: Optional[int] = None) -> dict:
    """Brief description of what the function does.
    Can be multi-line.

    Args:
        ctx: The MCP context
        param1: Description of param1
        param2: Description of param2 (explain defaults)
        
    Returns:
        Description of return value structure
    """
```

### Critical Rules

1. **Section Headers**: Use `Args:` and `Returns:` (case-insensitive, must end with `:`)
2. **Parameters**: Document ALL parameters, use format `param_name: description`
3. **Indentation**: Indent parameter descriptions (4+ spaces)
4. **Returns**: Always document what the function returns

## Validation

Functions validate automatically during registration:

```python
from braze_mcp.registry_builder import validate_docstring
is_valid, issues = validate_docstring(my_function)
```

**Common Errors:**
- Missing docstring
- Missing `Args:` section when function has parameters  
- Undocumented parameters
- Missing `Returns:` section

**Validation Failure:** Registry building stops immediately. **All docstrings must be valid.**

## Development Integration

### Pre-commit Hook
Already configured in `.pre-commit-config.yaml` - runs `scripts/validate_docstrings.py`

### Manual Validation
```bash
uv run python scripts/validate_docstrings.py src/braze_mcp/tools/*.py
```

### Fixing Issues
1. Run validation: `uv run python -c "from braze_mcp.registry_builder import build_function_registry; build_function_registry()"`
2. Fix reported docstring issues
3. Test: Verify system starts successfully