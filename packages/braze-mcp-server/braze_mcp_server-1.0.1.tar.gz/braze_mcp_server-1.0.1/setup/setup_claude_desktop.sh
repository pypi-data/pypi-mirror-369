#!/bin/bash
# Setup script for Claude Desktop - installs and configures Braze MCP Server
# Automatically handles installation, configuration, and provides demo examples
set -e

# Source shared functions
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

echo "🎯 Braze MCP Server Setup for Claude Desktop"
echo "============================================="
echo ""

# Run setup steps using shared functions
install_uv
install_server_from_source
get_user_credentials
create_claude_config
show_claude_success