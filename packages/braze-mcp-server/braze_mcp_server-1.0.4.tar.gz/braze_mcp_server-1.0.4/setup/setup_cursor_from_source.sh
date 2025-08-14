#!/bin/bash
# Setup script for Cursor IDE - installs Braze MCP Server from source code
# Use this when you have the full source repository cloned locally
set -e

# Source shared functions
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

echo "🎯 Braze MCP Server Setup for Cursor"
echo "====================================="
echo ""

# Run setup steps using shared functions
install_uv
install_server_from_source
get_user_credentials
create_cursor_config
show_cursor_success
