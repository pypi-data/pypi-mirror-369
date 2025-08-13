#!/bin/bash
# Shared functions for Braze MCP Server setup scripts
# This library contains common functionality used across all setup scripts

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Install uv package manager if not present
install_uv() {
    if ! command -v uv &> /dev/null; then
        echo "📦 Installing package manager..."
        curl -LsSf https://astral.sh/uv/install.sh | sh
        export PATH="$HOME/.local/bin:$PATH"
    fi
}

# Get user credentials for Braze API
get_user_credentials() {
    echo "🔧 Let's configure your Braze connection:"
    echo ""
    read -p "Enter your Braze API Key: " BRAZE_API_KEY
    read -p "Enter your Braze Base URL (e.g., https://rest.iad-01.braze.com): " BRAZE_BASE_URL
    
    # Export for use in calling scripts
    export BRAZE_API_KEY
    export BRAZE_BASE_URL
}

# Check if wheel file exists in dist/ or current directory
check_wheel_exists() {
    if ls dist/*.whl 1> /dev/null 2>&1; then
        WHEEL_PATH="dist/*.whl"
        echo "📦 Found wheel file in dist/ directory"
    elif ls *.whl 1> /dev/null 2>&1; then
        WHEEL_PATH="*.whl"
        echo "📦 Found wheel file in current directory"
    else
        echo "❌ No wheel file found in dist/ or current directory."
        echo "   Run 'make build' first to generate the wheel file."
        exit 1
    fi
}

# Install server from source code
install_server_from_source() {
    echo "📦 Installing Braze MCP Server from source..."
    uv tool install . --force
    echo "✅ Server installed successfully!"
    echo ""
}

# Install server from wheel file
install_server_from_wheel() {
    echo "📦 Installing Braze MCP Server from wheel..."
    uv tool install $WHEEL_PATH --force
    echo "✅ Server installed successfully!"
    echo ""
}

# Create Cursor MCP configuration
create_cursor_config() {
    local config_file="$HOME/.cursor/mcp.json"
    
    mkdir -p ~/.cursor
    
    # Create backup if file exists
    if [ -f "$config_file" ]; then
        echo "⚠️  Existing MCP config found. Creating backup..."
        cp "$config_file" "$config_file.backup.$(date +%Y%m%d_%H%M%S)"
    fi
    
    # Create new braze server config
    local braze_config='{
  "command": "'$HOME'/.local/bin/braze-mcp-server",
  "env": {
    "BRAZE_API_KEY": "'$BRAZE_API_KEY'",
    "BRAZE_BASE_URL": "'$BRAZE_BASE_URL'"
  }
}'
    
    # Check if jq is available for JSON manipulation
    if command -v jq &> /dev/null; then
        # Use jq for proper JSON merging
        if [ -f "$config_file" ]; then
            # Merge with existing config
            jq --argjson braze "$braze_config" '.mcpServers.braze = $braze' "$config_file" > "$config_file.tmp" && mv "$config_file.tmp" "$config_file"
        else
            # Create new config file
            echo '{"mcpServers":{}}' | jq --argjson braze "$braze_config" '.mcpServers.braze = $braze' > "$config_file"
        fi
    else
        # Fallback: manual JSON handling
        if [ -f "$config_file" ] && [ -s "$config_file" ]; then
            # Try to merge manually (basic approach)
            merge_cursor_config_manual "$config_file" "$braze_config"
        else
            # Create new config file
            cat > "$config_file" << EOL
{
  "mcpServers": {
    "braze": {
      "command": "$HOME/.local/bin/braze-mcp-server",
      "env": {
        "BRAZE_API_KEY": "$BRAZE_API_KEY",
        "BRAZE_BASE_URL": "$BRAZE_BASE_URL"
      }
    }
  }
}
EOL
        fi
    fi
    
    echo "📁 Configuration updated: $config_file"
    echo "✅ Braze MCP server added/updated while preserving existing servers"
}

# Manual JSON merge for Cursor config (fallback when jq unavailable)
merge_cursor_config_manual() {
    local config_file="$1"
    local braze_config="$2"
    
    # Read existing config and look for mcpServers section
    if grep -q '"mcpServers"' "$config_file"; then
        # Remove existing braze entry if present, then add new one
        # This is a simple approach - create temp file with braze entry added
        python3 -c "
import json, sys
try:
    with open('$config_file', 'r') as f:
        config = json.load(f)
    if 'mcpServers' not in config:
        config['mcpServers'] = {}
    config['mcpServers']['braze'] = {
        'command': '$HOME/.local/bin/braze-mcp-server',
        'env': {
            'BRAZE_API_KEY': '$BRAZE_API_KEY',
            'BRAZE_BASE_URL': '$BRAZE_BASE_URL'
        }
    }
    with open('$config_file', 'w') as f:
        json.dump(config, f, indent=2)
except Exception as e:
    print(f'Error: {e}', file=sys.stderr)
    sys.exit(1)
" 2>/dev/null || {
            echo "⚠️  Could not merge with existing config. Creating new file..."
            cat > "$config_file" << EOL
{
  "mcpServers": {
    "braze": {
      "command": "$HOME/.local/bin/braze-mcp-server",
      "env": {
        "BRAZE_API_KEY": "$BRAZE_API_KEY",
        "BRAZE_BASE_URL": "$BRAZE_BASE_URL"
      }
    }
  }
}
EOL
        }
    else
        # File exists but no mcpServers section - add it
        echo "⚠️  Existing file doesn't contain mcpServers. Creating new configuration..."
        cat > "$config_file" << EOL
{
  "mcpServers": {
    "braze": {
      "command": "$HOME/.local/bin/braze-mcp-server",
      "env": {
        "BRAZE_API_KEY": "$BRAZE_API_KEY",
        "BRAZE_BASE_URL": "$BRAZE_BASE_URL"
      }
    }
  }
}
EOL
    fi
}

# Create Claude Desktop configuration
create_claude_config() {
    # Determine OS and config path
    if [[ "$OSTYPE" == "darwin"* ]]; then
        local config_dir="$HOME/Library/Application Support/Claude"
        local config_file="$config_dir/claude_desktop_config.json"
    elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        local config_dir="$APPDATA/Claude"
        local config_file="$config_dir/claude_desktop_config.json"
    else
        echo "❌ Unsupported operating system. Please configure manually."
        echo "   Config file should be at:"
        echo "   - macOS: ~/Library/Application Support/Claude/claude_desktop_config.json"
        echo "   - Windows: %APPDATA%\\Claude\\claude_desktop_config.json"
        exit 1
    fi
    
    # Create config directory if it doesn't exist
    mkdir -p "$config_dir"
    
    # Get the correct binary path
    local binary_path=$(which braze-mcp-server 2>/dev/null || echo "$HOME/.local/bin/braze-mcp-server")
    
    # Create backup if file exists
    if [ -f "$config_file" ]; then
        echo "⚠️  Existing Claude Desktop config found. Creating backup..."
        cp "$config_file" "$config_file.backup.$(date +%Y%m%d_%H%M%S)"
    fi
    
    # Create new braze server config
    local braze_config='{
  "command": "'$binary_path'",
  "env": {
    "BRAZE_API_KEY": "'$BRAZE_API_KEY'",
    "BRAZE_BASE_URL": "'$BRAZE_BASE_URL'"
  }
}'
    
    # Check if jq is available for JSON manipulation
    if command -v jq &> /dev/null; then
        # Use jq for proper JSON merging
        if [ -f "$config_file" ]; then
            # Merge with existing config
            jq --argjson braze "$braze_config" '.mcpServers.braze = $braze' "$config_file" > "$config_file.tmp" && mv "$config_file.tmp" "$config_file"
        else
            # Create new config file
            echo '{"mcpServers":{}}' | jq --argjson braze "$braze_config" '.mcpServers.braze = $braze' > "$config_file"
        fi
    else
        # Fallback: manual JSON handling
        if [ -f "$config_file" ] && [ -s "$config_file" ]; then
            # Try to merge manually (basic approach)
            merge_claude_config_manual "$config_file" "$binary_path"
        else
            # Create new config file
            cat > "$config_file" << EOL
{
  "mcpServers": {
    "braze": {
      "command": "$binary_path",
      "env": {
        "BRAZE_API_KEY": "$BRAZE_API_KEY",
        "BRAZE_BASE_URL": "$BRAZE_BASE_URL"
      }
    }
  }
}
EOL
        fi
    fi
    
    echo "📁 Configuration updated: $config_file"
    echo "🔧 Binary path: $binary_path"
    echo "✅ Braze MCP server added/updated while preserving existing servers"
}

# Manual JSON merge for Claude Desktop config (fallback when jq unavailable)
merge_claude_config_manual() {
    local config_file="$1"
    local binary_path="$2"
    
    # Read existing config and look for mcpServers section
    if grep -q '"mcpServers"' "$config_file"; then
        # Remove existing braze entry if present, then add new one
        # This is a simple approach - create temp file with braze entry added
        python3 -c "
import json, sys
try:
    with open('$config_file', 'r') as f:
        config = json.load(f)
    if 'mcpServers' not in config:
        config['mcpServers'] = {}
    config['mcpServers']['braze'] = {
        'command': '$binary_path',
        'env': {
            'BRAZE_API_KEY': '$BRAZE_API_KEY',
            'BRAZE_BASE_URL': '$BRAZE_BASE_URL'
        }
    }
    with open('$config_file', 'w') as f:
        json.dump(config, f, indent=2)
except Exception as e:
    print(f'Error: {e}', file=sys.stderr)
    sys.exit(1)
" 2>/dev/null || {
            echo "⚠️  Could not merge with existing config. Creating new file..."
            cat > "$config_file" << EOL
{
  "mcpServers": {
    "braze": {
      "command": "$binary_path",
      "env": {
        "BRAZE_API_KEY": "$BRAZE_API_KEY",
        "BRAZE_BASE_URL": "$BRAZE_BASE_URL"
      }
    }
  }
}
EOL
        }
    else
        # File exists but no mcpServers section - add it
        echo "⚠️  Existing file doesn't contain mcpServers. Creating new configuration..."
        cat > "$config_file" << EOL
{
  "mcpServers": {
    "braze": {
      "command": "$binary_path",
      "env": {
        "BRAZE_API_KEY": "$BRAZE_API_KEY",
        "BRAZE_BASE_URL": "$BRAZE_BASE_URL"
      }
    }
  }
}
EOL
    fi
}

# Show success message for Cursor
show_cursor_success() {
    echo ""
    echo "🎉 Setup complete!"
    echo ""
    echo "🚀 Next steps:"
    echo "1. Restart Cursor"
    echo "2. Try asking Cursor: 'List my Braze campaigns'"
    echo ""
    echo "ℹ️  The Braze MCP server has been added to your existing MCP configuration."
    echo ""
    echo "🔍 Troubleshooting:"
    echo "- In Cursor open Settings > Cursor Settings > Tools & Integrations"
    echo "  - You should see 'braze' listed as an available server"
    echo "- Check MCP logs in Cursor: View > Output > MCP Logs"
    echo "- Verify your API key has the required permissions"
}

# Show success message for Claude Desktop
show_claude_success() {
    echo ""
    echo "🎉 Setup complete!"
    echo ""
    echo "🚀 Next steps:"
    echo "1. Restart Claude Desktop completely"
    echo "2. Try asking Claude: 'List my Braze campaigns'"
    echo "3. Or ask: 'What Braze functions are available?'"
    echo ""
    echo "ℹ️  The Braze MCP server has been added to your existing MCP configuration."
    echo ""
    echo "🔍 Troubleshooting:"
    echo "- Ensure Claude Desktop is completely closed and reopened"
    echo "- Verify your API key has the required permissions"
    echo "- Check that your Base URL matches your Braze instance"
    echo "- If the binary path is incorrect, run: which braze-mcp-server"
}