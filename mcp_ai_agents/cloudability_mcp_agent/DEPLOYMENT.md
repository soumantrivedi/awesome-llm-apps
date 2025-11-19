# Cloudability MCP Server - Deployment Guide

## ✅ Deployment Status

The Cloudability MCP Server has been successfully deployed in Cursor!

## Current Configuration

The MCP server is configured in `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "cloudability": {
      "command": "/Users/Souman_Trivedi/IdeaProjects/awesome-llm-apps/mcp_ai_agents/cloudability_mcp_agent/venv/bin/python3",
      "args": [
        "-u",
        "/Users/Souman_Trivedi/IdeaProjects/awesome-llm-apps/mcp_ai_agents/cloudability_mcp_agent/cloudability_mcp_server.py"
      ],
      "env": {
        "CLOUDABILITY_API_KEY": "your_api_key_here",
        "CLOUDABILITY_BASE_URL": "https://api.cloudability.com/v3",
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

## Configuration Details

### Command
- **Path**: Uses the virtual environment's Python interpreter
- **Location**: `/Users/Souman_Trivedi/IdeaProjects/awesome-llm-apps/mcp_ai_agents/cloudability_mcp_agent/venv/bin/python3`
- **Flag**: `-u` for unbuffered I/O (required for MCP stdio protocol)

### Arguments
- **Script**: `cloudability_mcp_server.py` (backward-compatible wrapper)
- **Location**: Project root directory

### Environment Variables
- **CLOUDABILITY_API_KEY**: Your Cloudability API key
- **CLOUDABILITY_BASE_URL**: API endpoint (default: US region)
- **PYTHONUNBUFFERED**: Ensures real-time stdio communication

## Verification Steps

### 1. Restart Cursor
After configuration, restart Cursor IDE to load the MCP server.

### 2. Check MCP Status
1. Open Cursor
2. Check the MCP status indicator (usually in the status bar)
3. Verify "cloudability" server is connected

### 3. Test the Server
Try using one of the MCP tools in Cursor chat:

```
List all available views in Cloudability
```

Or:

```
Get amortized costs for all services in the last 30 days, export as CSV
```

## Troubleshooting

### Issue: MCP Server Not Connecting

**Check 1: Verify Python Path**
```bash
cd /Users/Souman_Trivedi/IdeaProjects/awesome-llm-apps/mcp_ai_agents/cloudability_mcp_agent
ls -la venv/bin/python3
```

**Check 2: Verify Script Exists**
```bash
ls -la cloudability_mcp_server.py
```

**Check 3: Test Import**
```bash
cd /Users/Souman_Trivedi/IdeaProjects/awesome-llm-apps/mcp_ai_agents/cloudability_mcp_agent
venv/bin/python3 -c "from cloudability_mcp_server import CloudabilityMCPServer; print('OK')"
```

### Issue: Module Import Errors

If you see import errors, ensure the `src/` directory exists:

```bash
cd /Users/Souman_Trivedi/IdeaProjects/awesome-llm-apps/mcp_ai_agents/cloudability_mcp_agent
ls -la src/
```

You should see:
- `__init__.py`
- `config.py`
- `auth.py`
- `utils.py`
- `api_client.py`
- `main.py`

### Issue: API Authentication Errors

Verify your API key is correct:
1. Check `~/.cursor/mcp.json` has the correct `CLOUDABILITY_API_KEY`
2. Verify the key is valid in Cloudability settings
3. Check the base URL matches your region

### Issue: Tools Not Available

1. **Restart Cursor** - MCP servers load on startup
2. **Check MCP Logs** - Look for errors in Cursor's developer console
3. **Verify Configuration** - Ensure JSON syntax is correct in `mcp.json`

## Alternative Configuration Methods

### Option 1: Using Shell Script (Previous Method)

If you prefer using the shell script wrapper:

```json
{
  "mcpServers": {
    "cloudability": {
      "command": "/bin/bash",
      "args": [
        "/Users/Souman_Trivedi/IdeaProjects/awesome-llm-apps/mcp_ai_agents/cloudability_mcp_agent/run_mcp_server.sh"
      ],
      "env": {
        "CLOUDABILITY_API_KEY": "your_api_key",
        "CLOUDABILITY_BASE_URL": "https://api.cloudability.com/v3"
      }
    }
  }
}
```

### Option 2: Using System Python

If you don't want to use the virtual environment:

```json
{
  "mcpServers": {
    "cloudability": {
      "command": "python3",
      "args": [
        "-u",
        "/Users/Souman_Trivedi/IdeaProjects/awesome-llm-apps/mcp_ai_agents/cloudability_mcp_agent/cloudability_mcp_server.py"
      ],
      "env": {
        "CLOUDABILITY_API_KEY": "your_api_key",
        "CLOUDABILITY_BASE_URL": "https://api.cloudability.com/v3",
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

## Available Tools

Once deployed, the following MCP tools are available:

1. **get_cost_report_by_view** - Get cost data for a specific dashboard view
2. **list_views** - List all available views
3. **get_cost_report_with_filters** - Get cost report with advanced filtering
4. **get_amortized_costs** - Get amortized costs (supports view, namespace, product_id filters)
5. **export_cost_report** - Export custom cost reports

## Next Steps

1. ✅ **Deployment Complete** - Server is configured and ready
2. **Test Tools** - Try using the tools in Cursor chat
3. **Explore Features** - Check out `USAGE_EXAMPLES.md` for examples
4. **Read Documentation** - See `ARCHITECTURE.md` for architecture details

## Support

- **Documentation**: See `README.md` and `ARCHITECTURE.md`
- **Examples**: See `USAGE_EXAMPLES.md`
- **Migration**: See `MIGRATION.md` for migration details

## Notes

- The server uses the new modular architecture (`src/` directory)
- Backward compatibility is maintained through `cloudability_mcp_server.py`
- All existing functionality is preserved
- New features are available (view restrictions, namespace filters, etc.)

