#!/bin/bash
# Wrapper script to ensure python3 is used for MCP server
# This script ensures the correct Python interpreter is used for stdio-based MCP communication

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_EXEC="$SCRIPT_DIR/venv/bin/python3"
SERVER_SCRIPT="$SCRIPT_DIR/cloudability_mcp_server.py"

# Verify Python exists
if [ ! -f "$PYTHON_EXEC" ]; then
    echo "Error: Python not found at $PYTHON_EXEC" >&2
    exit 1
fi

# Verify server script exists
if [ ! -f "$SERVER_SCRIPT" ]; then
    echo "Error: Server script not found at $SERVER_SCRIPT" >&2
    exit 1
fi

# Ensure unbuffered I/O for MCP stdio protocol
export PYTHONUNBUFFERED=1

# Run the server with exec to replace shell process (important for stdio)
exec "$PYTHON_EXEC" -u "$SERVER_SCRIPT"

