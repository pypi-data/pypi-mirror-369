import importlib
import inspect
import json
import pkgutil
from typing import Any, Union, get_args, get_origin, get_type_hints

import braze_mcp.tools
from braze_mcp.utils.logging import get_logger

logger = get_logger(__name__)

# ============================================================================
# DOCSTRING CONVENTIONS & VALIDATION
# ============================================================================

"""
DOCSTRING CONVENTIONS FOR MCP TOOLS

This module auto-generates function metadata from docstrings using Google-style conventions.

📖 COMPLETE DOCUMENTATION: docs/DOCSTRING_CONVENTIONS.md

QUICK REFERENCE:
- Use 'Args:' and 'Returns:' sections
- Document all parameters except 'ctx'
- Indent parameter descriptions with spaces
- Follow format: "param_name: description"

VALIDATION: Functions validate automatically during registration. Invalid docstrings FAIL registration.
"""


def validate_docstring(func) -> tuple[bool, list[str]]:
    """Validate that a function's docstring follows MCP conventions.

    Args:
        func: Function to validate

    Returns:
        Tuple of (is_valid, list_of_issues)
    """
    issues = []
    docstring = func.__doc__

    if not docstring:
        issues.append("Missing docstring")
        return False, issues

    lines = docstring.split("\n")
    stripped_lines = [line.strip() for line in lines if line.strip()]

    # Check for description
    if not stripped_lines:
        issues.append("Empty docstring")
        return False, issues

    # Look for section headers
    sections_found = []
    param_sections = ["args:", "arguments:", "parameters:"]

    for line in stripped_lines:
        lower_line = line.lower()
        if lower_line in DOCSTRING_SECTION_HEADERS:
            sections_found.append(lower_line)

    # Check for Args section if function has parameters
    import inspect

    sig = inspect.signature(func)
    has_params = any(name != "ctx" for name in sig.parameters.keys())

    if has_params and not any(section in param_sections for section in sections_found):
        issues.append("Function has parameters but no Args/Arguments/Parameters section")

    # Check parameter documentation
    if any(section in param_sections for section in sections_found):
        for i, line in enumerate(lines):
            if line.strip().lower() in param_sections:
                # Validate parameter entries
                for param_name in sig.parameters.keys():
                    if param_name == "ctx":
                        continue

                    param_documented = False
                    for j in range(i + 1, len(lines)):
                        param_line = lines[j].strip()
                        if param_line and not lines[j].startswith((" ", "\t")):
                            break  # Next section
                        if param_line.startswith(f"{param_name}:"):
                            param_documented = True
                            break

                    if not param_documented:
                        issues.append(f"Parameter '{param_name}' not documented in Args section")
                break

    returns_issues = _validate_returns_section(lines, sections_found)
    issues.extend(returns_issues)

    return len(issues) == 0, issues


def _validate_returns_section(lines: list[str], sections_found: list[str]) -> list[str]:
    """Validate that Returns section exists and has content.

    Args:
        lines: Lines of the docstring
        sections_found: List of section headers found in the docstring

    Returns:
        List of validation issues (empty if valid)
    """
    issues = []
    return_sections = ["returns:", "return:"]

    if not any(section in return_sections for section in sections_found):
        issues.append("Missing Returns section")
    else:
        # Check that Returns section has content
        returns_has_content = False
        for i, line in enumerate(lines):
            if line.strip().lower() in return_sections:
                # Look for content after Returns header
                for j in range(i + 1, len(lines)):
                    returns_line = lines[j].strip()
                    if returns_line and not lines[j].startswith((" ", "\t")):
                        break  # Next section
                    if returns_line and returns_line != "":
                        returns_has_content = True
                        break
                break

        if not returns_has_content:
            issues.append("Returns section must contain a description")

    return issues


def _log_docstring_validation_warnings(func_name: str, issues: list[str]) -> None:
    """Log warnings about docstring validation issues."""
    if issues:
        logger.warning(f"Docstring issues in function '{func_name}':")
        for issue in issues:
            logger.warning(f"  - {issue}")
        logger.warning(
            "  Consider following the docstring conventions documented in registry_builder.py"
        )


# ============================================================================
# CONSTANTS
# ============================================================================

DOCSTRING_SECTION_HEADERS = [
    "args:",
    "arguments:",
    "parameters:",
    "returns:",
    "return:",
    "raises:",
    "raise:",
    "yields:",
    "yield:",
    "examples:",
    "example:",
    "note:",
    "notes:",
    "warning:",
    "warnings:",
]

BASIC_TYPE_MAPPING = {
    str: "string",
    int: "integer",
    bool: "boolean",
    float: "number",
    list: "array",
    dict: "object",
    object: "object",
}

# ============================================================================
# TYPE CONVERSION
# ============================================================================


def _python_type_to_json_type(python_type) -> str:
    """Convert Python type hints to JSON schema types"""
    try:
        if python_type is type(None):
            return "null"

        origin = get_origin(python_type)
        args = get_args(python_type)

        # Handle Union types (including Optional[T])
        # Support both typing.Union and types.UnionType (Python 3.10+)
        if origin is Union or str(type(python_type)).endswith("UnionType'>"):
            non_none_types = [t for t in args if t is not type(None)]
            if non_none_types:
                return _python_type_to_json_type(non_none_types[0])
            return "null"

        # Handle generic types
        if origin is not None:
            if origin in (list, tuple):
                return "array"
            elif origin is dict:
                return "object"
            else:
                python_type = origin

        return BASIC_TYPE_MAPPING.get(python_type, "object")  # fallback to object
    except Exception:
        return "string"


def _safe_serialize_default(default_value) -> Any:
    """Safely serialize default values to JSON-compatible format"""
    try:
        json.dumps(default_value)
        return default_value
    except (TypeError, ValueError):
        if default_value is None:
            return None
        elif callable(default_value):
            return f"<function: {getattr(default_value, '__name__', 'unknown')}>"
        elif hasattr(default_value, "__class__"):
            return f"<{default_value.__class__.__name__}: {str(default_value)}>"
        else:
            return str(default_value)


# ============================================================================
# DOCSTRING PARSING
# ============================================================================


def _extract_description_from_docstring(docstring: str | None) -> str:
    """Extract main description from function docstring"""
    if not docstring:
        return "No description available"

    lines = docstring.split("\n")
    description_lines = []
    found_content = False

    for line in lines:
        stripped = line.strip()

        if not stripped and not found_content:
            continue

        # Stop at section headers
        if _is_section_header(line, DOCSTRING_SECTION_HEADERS, check_indentation=False):
            break

        if stripped:
            description_lines.append(stripped)
            found_content = True

    return " ".join(description_lines) if description_lines else "No description available"


def _is_section_header(
    line: str, valid_sections: list | None = None, check_indentation: bool = True
) -> bool:
    """Check if a line is a docstring section header.

    Args:
        line: The line to check
        valid_sections: Optional list of valid section names. If None, checks any colon-ending header.
        check_indentation: Whether to require the line to be non-indented

    Returns:
        True if the line is a section header
    """
    stripped = line.strip()

    # Must have content and end with colon
    if not (stripped and stripped.endswith(":")):
        return False

    # Check indentation if required
    if check_indentation and line.startswith((" ", "\t")):
        return False

    # If specific sections provided, check against them
    if valid_sections is not None:
        return stripped.lower() in valid_sections

    # Otherwise, any colon-ending line is a section header (subject to indentation check)
    return True


def _find_section_start(lines: list, section_names: list) -> int | None:
    """Find the start line index of a docstring section"""
    for i, line in enumerate(lines):
        if _is_section_header(line, section_names, check_indentation=False):
            return i + 1
    return None


def _parse_args_section(docstring: str, param_name: str) -> str | None:
    """Parse the Args section of a docstring to find parameter descriptions"""
    lines = docstring.split("\n")
    args_start = _find_section_start(lines, ["args:", "arguments:", "parameters:"])

    if args_start is None:
        return None

    for i in range(args_start, len(lines)):
        line = lines[i]
        stripped = line.strip()

        # Stop at next section
        if _is_section_header(line):
            break

        if ":" not in stripped:
            continue

        param_part, desc_part = stripped.split(":", 1)
        param_part = param_part.strip()

        # Match exact parameter name or with type annotation
        if param_part == param_name or param_part.startswith(f"{param_name} ("):
            desc_part = desc_part.strip()
            if desc_part:
                return _extract_multiline_description(lines, i, desc_part)

    return None


def _extract_multiline_description(lines: list, start_index: int, first_line: str) -> str:
    """Extract multiline description starting from a given line"""
    full_description = [first_line]
    base_indent = len(lines[start_index]) - len(lines[start_index].lstrip())

    for j in range(start_index + 1, len(lines)):
        next_line = lines[j]
        if not next_line.strip():
            continue

        next_indent = len(next_line) - len(next_line.lstrip())
        if next_indent > base_indent:
            full_description.append(next_line.strip())
        else:
            break

    return " ".join(full_description)


def _parse_returns_section(docstring: str | None) -> str | None:
    """Parse the Returns section of a docstring"""
    if not docstring:
        return None

    lines = docstring.split("\n")
    returns_start = _find_section_start(lines, ["returns:", "return:"])

    if returns_start is None:
        return None

    description_lines: list[str] = []
    for i in range(returns_start, len(lines)):
        line = lines[i]
        stripped = line.strip()

        # Stop at next section
        if _is_section_header(line):
            break

        if not stripped and not description_lines:
            continue

        if stripped:
            description_lines.append(stripped)
        elif description_lines:
            break

    return " ".join(description_lines) if description_lines else None


# ============================================================================
# PARAMETER EXTRACTION
# ============================================================================


def _extract_param_description(docstring: str | None, param_name: str, param_type) -> str:
    """Extract parameter description from docstring"""
    if not docstring:
        return f"Parameter {param_name}"

    args_description = _parse_args_section(docstring, param_name)
    return args_description if args_description else f"Parameter {param_name}"


def _extract_parameter_info(
    param_name: str,
    param: inspect.Parameter,
    type_hints: dict,
    docstring: str | None,
) -> dict:
    """Extract complete parameter information"""
    try:
        param_type = type_hints.get(param_name, str)
        param_info = {
            "type": _python_type_to_json_type(param_type),
            "required": param.default == inspect.Parameter.empty,
            "description": _extract_param_description(docstring, param_name, param_type),
        }

        if param.default != inspect.Parameter.empty:
            param_info["default"] = _safe_serialize_default(param.default)

        return param_info
    except Exception as e:
        logger.warning(f"Could not extract metadata for parameter {param_name}: {e}")
        return {
            "type": "string",
            "required": param.default == inspect.Parameter.empty,
            "description": f"Parameter {param_name}",
        }


# ============================================================================
# MAIN EXTRACTION FUNCTIONS
# ============================================================================


def extract_function_metadata(func) -> dict[str, Any]:
    """Extract metadata from a function for registry using introspection"""
    try:
        signature = inspect.signature(func)
        type_hints = _get_type_hints_safely(func)
        description = _extract_description_from_docstring(func.__doc__)

        parameters = {}
        for param_name, param in signature.parameters.items():
            parameters[param_name] = _extract_parameter_info(
                param_name, param, type_hints, func.__doc__
            )

        result = {
            "implementation": func,
            "description": description,
            "parameters": parameters,
        }

        # Add returns info if available
        returns_description = _parse_returns_section(func.__doc__)
        if returns_description:
            result["returns"] = {"description": returns_description, "type": "object"}

        return result

    except Exception as e:
        logger.exception(f"Failed to extract metadata for function {func.__name__}")
        return _create_fallback_metadata(func, str(e))


def _get_type_hints_safely(func) -> dict:
    """Safely get type hints from a function"""
    try:
        return get_type_hints(func)
    except (NameError, AttributeError, TypeError) as e:
        logger.warning(f"Could not get type hints for {func.__name__}: {e}")
        return {}


def _create_fallback_metadata(func, error: str) -> dict:
    """Create minimal fallback metadata when extraction fails"""
    return {
        "implementation": func,
        "description": f"Function {func.__name__} (metadata extraction failed)",
        "parameters": {},
        "error": error,
    }


# ============================================================================
# REGISTRY BUILDING
# ============================================================================


def _is_valid_function(obj, name: str) -> bool:
    """Check if an object is a valid function for the registry"""
    return (
        inspect.iscoroutinefunction(obj)
        and not name.startswith("_")
        and hasattr(obj, "__module__")
        and obj.__module__.startswith("braze_mcp.tools")
    )


# ============================================================================
# AUTO-DISCOVERY SYSTEM
# ============================================================================

"""
AUTO-DISCOVERY IMPLEMENTATION

Uses reflection to scan braze_mcp.tools for modules with __register_mcp_tools__ = True.
"""


def _discover_mcp_tool_modules():
    """Discover all modules in the tools package that have __register_mcp_tools__ = True"""
    discovered_modules = []

    # Walk through all modules in the tools package
    for module_info in pkgutil.iter_modules(
        braze_mcp.tools.__path__, braze_mcp.tools.__name__ + "."
    ):
        try:
            # Import the module
            module = importlib.import_module(module_info.name)

            # Check if it has the MCP tools registration marker
            if hasattr(module, "__register_mcp_tools__") and module.__register_mcp_tools__:
                discovered_modules.append(module)
                logger.info(f"Discovered MCP tools module: {module_info.name}")
        except Exception as e:
            logger.warning(f"Failed to import module {module_info.name}: {e}")

    return discovered_modules


def build_function_registry() -> dict[str, dict[str, Any]]:
    """Automatically discover and register functions from tools modules"""
    registry = {}
    modules = _discover_mcp_tool_modules()

    for module in modules:
        module_name = module.__name__.split(".")[-1]

        for name, obj in inspect.getmembers(module):
            if _is_valid_function(obj, name):
                try:
                    # Validate docstring before extracting metadata - STRICT MODE
                    is_valid, issues = validate_docstring(obj)
                    if not is_valid:
                        _log_docstring_validation_warnings(name, issues)
                        raise ValueError(
                            f"Function '{name}' has invalid docstring and cannot be registered. See validation issues above."
                        )

                    registry[name] = extract_function_metadata(obj)
                    logger.info(f"Registered function: {name} from {module_name}")
                except Exception:
                    logger.exception(f"Failed to register function {name}")
                    raise  # Re-raise to fail the entire registry building process

    return registry


def get_function_registry() -> dict[str, dict[str, Any]]:
    """Get the function registry, building it if needed"""
    return build_function_registry()


# For compatibility, expose the registry
FUNCTION_REGISTRY = get_function_registry()
