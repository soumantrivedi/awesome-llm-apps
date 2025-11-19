# Troubleshooting: No Tools Available

## Quick Checks

### 1. Verify Tools Are Registered
```bash
cd mcp_ai_agents/cloudability_mcp_agent
python3 -c "from src.framework.tool_base import get_registry; from src import tools; registry = get_registry(); print('Tools:', len(registry.list_tools())); print(registry.list_tools())"
```

Expected output: Should show 20 tools including `generate_cost_report`

### 2. Check Server Can Start
```bash
cd mcp_ai_agents/cloudability_mcp_agent
python3 -c "from src.main import CloudabilityMCPServer; print('Server import OK')"
```

### 3. Verify Tool Definitions
```bash
cd mcp_ai_agents/cloudability_mcp_agent
python3 -c "from src.framework.tool_base import get_registry; from src import tools; registry = get_registry(); defs = registry.get_all_definitions(); print(f'Definitions: {len(defs)}'); print(defs[0]['name'] if defs else 'None')"
```

## Common Issues

### Issue: Server Not Restarted
**Solution**: Restart the MCP server after code changes
- Stop the current server process
- Restart it using your MCP client configuration

### Issue: Import Errors
**Solution**: Check for missing dependencies or syntax errors
```bash
python3 -m py_compile src/tools/comprehensive_report_tool.py
python3 -c "from src import tools"
```

### Issue: MCP Client Not Connecting
**Solution**: Check your MCP client configuration
- Verify the server path is correct
- Check that environment variables are set (CLOUDABILITY_API_KEY)
- Ensure the virtual environment is activated if using one

### Issue: Tools Not Exposed
**Solution**: Verify the MCP protocol handler
- Check that `tools/list` request is handled correctly
- Verify `get_tools()` returns tool definitions
- Check server logs for errors

## Testing the Server

### Test Tool Registration
```python
from src.framework.tool_base import get_registry
from src import tools

registry = get_registry()
print(f"Total tools: {len(registry.list_tools())}")
print(f"Tools: {registry.list_tools()}")
```

### Test Tool Definitions
```python
from src.framework.tool_base import get_registry
from src import tools

registry = get_registry()
definitions = registry.get_all_definitions()
print(f"Total definitions: {len(definitions)}")
for tool in definitions[:3]:
    print(f"- {tool['name']}: {tool['description'][:50]}...")
```

### Test Specific Tool
```python
from src.framework.tool_base import get_registry
from src import tools

registry = get_registry()
tool = registry.get_tool('generate_cost_report')
if tool:
    print(f"Tool found: {tool.get_name()}")
    print(f"Description: {tool.get_description()[:100]}...")
    print(f"Schema keys: {list(tool.get_input_schema().keys())}")
else:
    print("Tool not found!")
```

## MCP Client Configuration

Ensure your MCP client configuration includes:
```json
{
  "mcpServers": {
    "cloudability": {
      "command": "python3",
      "args": [
        "-u",
        "/path/to/cloudability_mcp_server.py"
      ],
      "env": {
        "CLOUDABILITY_API_KEY": "your-api-key"
      }
    }
  }
}
```

## Server Logs

Check server logs for:
- Import errors
- Registration messages: "Registered tool: ..."
- Initialization errors
- Request handling errors

## Expected Tools List

The server should expose these 20 tools:
1. analyze_container_cost_allocation
2. create_budget
3. explore_tags
4. export_cost_report
5. **generate_cost_report** (new)
6. get_amortized_costs
7. get_anomaly_detection
8. get_available_measures
9. get_budget
10. get_container_costs
11. get_container_resource_usage
12. get_cost_report_by_view
13. get_cost_report_with_filters
14. get_filter_operators
15. get_spending_estimate
16. get_spending_forecast
17. list_available_tags
18. list_budgets
19. list_views
20. update_budget

