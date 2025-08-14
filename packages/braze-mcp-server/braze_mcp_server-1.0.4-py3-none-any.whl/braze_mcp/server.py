import json
from typing import Any

from mcp.server.fastmcp import Context, FastMCP
from pydantic import BaseModel

from braze_mcp.models.errors import (
    function_not_found_error,
    internal_error,
    invalid_params_error,
)
from braze_mcp.registry_builder import FUNCTION_REGISTRY
from braze_mcp.utils.context import braze_lifespan

# Defined here to avoid circular dependencies with the tools
mcp = FastMCP(
    "Braze MCP Server",
    lifespan=braze_lifespan,
)

# Cache available function names for better performance
AVAILABLE_FUNCTION_NAMES = list(FUNCTION_REGISTRY.keys())


@mcp.tool()
async def list_functions() -> dict[str, Any]:
    """Lists all available Braze API functions with their descriptions and parameters.

    Returns:
        Dictionary containing all available functions and their metadata
    """
    try:
        available_functions = {}
        for func_name, func_info in FUNCTION_REGISTRY.items():
            available_functions[func_name] = {
                "description": func_info["description"],
                "parameters": func_info["parameters"],
                "returns": func_info["returns"],
            }

        return {
            "available_functions": available_functions,
            "total_functions": len(available_functions),
        }
    except Exception:
        return internal_error("Error listing functions", "list_functions")


@mcp.tool()
async def call_function(
    ctx: Context,
    function_name: str,
    parameters: dict[str, Any] | str | None = None,
) -> Any:
    """Call a specific Braze API function with the provided parameters.

    Args:
        ctx: The MCP context
        function_name: Name of the function to call (use list_functions to see available options)
        parameters: Dictionary of parameters to pass to the function, or JSON string that will be parsed to dictionary (optional)

    Returns:
        The function result as a dictionary or error dictionary
    """
    try:
        if function_name not in FUNCTION_REGISTRY:
            return function_not_found_error(function_name, AVAILABLE_FUNCTION_NAMES)

        func_info = FUNCTION_REGISTRY[function_name]
        implementation = func_info["implementation"]

        # Handle both dict and string parameters
        parsed_parameters = {}
        if parameters is not None:
            if isinstance(parameters, str):
                try:
                    parsed_parameters = json.loads(parameters)
                    if not isinstance(parsed_parameters, dict):
                        return invalid_params_error(
                            "Parameters string must parse to a JSON object/dictionary",
                            "call_function",
                        )
                except json.JSONDecodeError:
                    return invalid_params_error(
                        "Invalid JSON in parameters string", "call_function"
                    )
            elif isinstance(parameters, dict):
                parsed_parameters = parameters
            else:
                return invalid_params_error(
                    f"Parameters must be a dictionary or JSON string, got {type(parameters).__name__}",
                    "call_function",
                )

        # Call the function with context as first parameter
        result = await implementation(ctx, **parsed_parameters)

        # Convert Pydantic models to dictionaries for MCP transport with schema context
        if isinstance(result, BaseModel):
            return {
                "data": result.model_dump(),
                "schema": {
                    "model_name": result.__class__.__name__,
                    "fields": result.model_json_schema(),
                    "description": f"Response data structured according to the {result.__class__.__name__} model",
                },
            }

        return result

    except Exception:
        return internal_error(f"Error calling function '{function_name}'", "call_function")
