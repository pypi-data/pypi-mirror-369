from braze_mcp.server import mcp

# Import tools to register them with the MCP server
from braze_mcp.tools import *  # noqa: F401, F403


def main():
    """Entry point for the braze-mcp-server command."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
