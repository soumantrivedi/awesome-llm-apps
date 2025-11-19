#!/bin/bash
# Verification script for Cloudability MCP Server deployment

echo "🔍 Verifying Cloudability MCP Server Deployment..."
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check 1: Python executable
echo "1. Checking Python executable..."
PYTHON_EXEC="$SCRIPT_DIR/venv/bin/python3"
if [ -f "$PYTHON_EXEC" ]; then
    echo "   ✓ Python found: $PYTHON_EXEC"
    echo "   Version: $($PYTHON_EXEC --version)"
else
    echo "   ✗ Python not found at $PYTHON_EXEC"
    exit 1
fi
echo ""

# Check 2: Server script
echo "2. Checking server script..."
SERVER_SCRIPT="$SCRIPT_DIR/cloudability_mcp_server.py"
if [ -f "$SERVER_SCRIPT" ]; then
    echo "   ✓ Server script found: $SERVER_SCRIPT"
else
    echo "   ✗ Server script not found at $SERVER_SCRIPT"
    exit 1
fi
echo ""

# Check 3: Source modules
echo "3. Checking source modules..."
if [ -d "$SCRIPT_DIR/src" ]; then
    echo "   ✓ src/ directory exists"
    for module in config.py auth.py utils.py api_client.py main.py; do
        if [ -f "$SCRIPT_DIR/src/$module" ]; then
            echo "   ✓ $module found"
        else
            echo "   ✗ $module not found"
            exit 1
        fi
    done
else
    echo "   ✗ src/ directory not found"
    exit 1
fi
echo ""

# Check 4: Dependencies
echo "4. Checking dependencies..."
if $PYTHON_EXEC -c "import requests; import dotenv" 2>/dev/null; then
    echo "   ✓ Required dependencies installed"
else
    echo "   ✗ Missing dependencies - installing..."
    $PYTHON_EXEC -m pip install -q -r requirements.txt
    if [ $? -eq 0 ]; then
        echo "   ✓ Dependencies installed"
    else
        echo "   ✗ Failed to install dependencies"
        exit 1
    fi
fi
echo ""

# Check 5: Import test
echo "5. Testing imports..."
if $PYTHON_EXEC -c "from cloudability_mcp_server import CloudabilityMCPServer; print('OK')" 2>/dev/null; then
    echo "   ✓ Import successful"
else
    echo "   ✗ Import failed"
    exit 1
fi
echo ""

# Check 6: MCP configuration
echo "6. Checking MCP configuration..."
MCP_CONFIG="$HOME/.cursor/mcp.json"
if [ -f "$MCP_CONFIG" ]; then
    if grep -q "cloudability" "$MCP_CONFIG"; then
        echo "   ✓ MCP configuration found in $MCP_CONFIG"
    else
        echo "   ⚠ MCP configuration exists but cloudability server not found"
    fi
else
    echo "   ⚠ MCP configuration file not found at $MCP_CONFIG"
fi
echo ""

echo "✅ Deployment verification complete!"
echo ""
echo "Next steps:"
echo "1. Restart Cursor IDE to load the MCP server"
echo "2. Check MCP status in Cursor"
echo "3. Try using the tools in Cursor chat"
echo ""
echo "Example commands to try:"
echo "  - 'List all available views in Cloudability'"
echo "  - 'Get amortized costs for all services in the last 30 days, export as CSV'"

