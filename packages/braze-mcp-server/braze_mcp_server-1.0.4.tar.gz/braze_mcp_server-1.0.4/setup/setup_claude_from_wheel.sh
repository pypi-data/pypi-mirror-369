#!/bin/bash
# Setup script for Claude Desktop - installs Braze MCP Server from pre-built wheel file
# Use this when you have downloaded a distribution package (*.whl file)
set -e

# Source shared functions
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

echo "🎯 Braze MCP Server Setup for Claude Desktop"
echo "============================================="
echo ""

# Run setup steps using shared functions
check_wheel_exists
install_uv
install_server_from_wheel
get_user_credentials
create_claude_config
show_claude_success