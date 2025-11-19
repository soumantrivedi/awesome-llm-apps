#!/bin/bash
# Helper script to find the correct Python executable for MCP server configuration

echo "Finding Python executable for Cloudability MCP Server..."
echo ""

# Try python3 first
if command -v python3 &> /dev/null; then
    PYTHON3_VERSION=$(python3 --version 2>&1)
    PYTHON3_PATH=$(which python3)
    echo "✓ Found python3:"
    echo "  Path: $PYTHON3_PATH"
    echo "  Version: $PYTHON3_VERSION"
    echo ""
    echo "Recommended command for Cursor MCP config: python3"
    echo ""
fi

# Try python
if command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version 2>&1)
    PYTHON_PATH=$(which python)
    echo "✓ Found python:"
    echo "  Path: $PYTHON_PATH"
    echo "  Version: $PYTHON_VERSION"
    echo ""
    if [ -z "$PYTHON3_PATH" ]; then
        echo "Recommended command for Cursor MCP config: python"
    else
        echo "Alternative command for Cursor MCP config: python"
    fi
    echo ""
fi

# Get absolute path to server script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVER_SCRIPT="$SCRIPT_DIR/cloudability_mcp_server.py"

if [ -f "$SERVER_SCRIPT" ]; then
    echo "✓ Server script found:"
    echo "  $SERVER_SCRIPT"
    echo ""
    echo "Use this absolute path in your Cursor MCP configuration."
else
    echo "⚠ Server script not found at: $SERVER_SCRIPT"
fi

echo ""
echo "Example Cursor MCP configuration:"
echo "{"
echo "  \"mcpServers\": {"
echo "    \"cloudability\": {"
if [ -n "$PYTHON3_PATH" ]; then
    echo "      \"command\": \"python3\","
else
    echo "      \"command\": \"python\","
fi
echo "      \"args\": ["
echo "        \"$SERVER_SCRIPT\""
echo "      ],"
echo "      \"env\": {"
echo "        \"CLOUDABILITY_API_KEY\": \"your_api_key_here\","
echo "        \"CLOUDABILITY_BASE_URL\": \"https://api.cloudability.com/v3\""
echo "      }"
echo "    }"
echo "  }"
echo "}"

