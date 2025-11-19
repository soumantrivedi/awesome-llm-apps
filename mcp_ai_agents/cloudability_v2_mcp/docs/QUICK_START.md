# Quick Start Guide - Cloudability V2 MCP Server

## Installation

1. **Navigate to the project directory:**
   ```bash
   cd mcp_ai_agents/cloudability_v2_mcp
   ```

2. **Install dependencies:**
   ```bash
   make install
   ```

3. **Set up credentials:**
   ```bash
   make secrets
   ```
   Follow the prompts to enter your Cloudability credentials.

## Register in Cursor IDE

1. **Get registration instructions:**
   ```bash
   make register
   ```

2. **Add to Cursor IDE MCP settings:**
   - Open Cursor IDE settings
   - Navigate to MCP settings (usually in `~/.cursor/mcp.json` or Cursor settings)
   - Add the configuration shown by `make register`

## Verify Installation

```bash
make verify
```

This will:
- Verify Python imports work
- Initialize the server
- List available tools

## Run Tests

```bash
make test
```

This runs the test suite to validate all tools work correctly.

## Basic Usage

### In Cursor IDE Chat

Once registered, you can use the tools directly in Cursor IDE:

```
List all views in my Cloudability account
```

```
Get amortized costs grouped by vendor for the last 30 days
```

```
List all budgets
```

### Programmatic Usage

```python
import asyncio
from src.main import CloudabilityV2MCPServer

async def main():
    server = CloudabilityV2MCPServer()
    
    # List views
    views = await server.call_tool("list_views", {"limit": 10})
    print(views)
    
    # Get amortized costs
    from datetime import datetime, timedelta
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    costs = await server.call_tool("get_amortized_costs", {
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "dimensions": ["vendor"],
        "granularity": "monthly"
    })
    print(costs)

asyncio.run(main())
```

## Available Tools

1. **list_views** - List dashboard views
2. **list_budgets** - List budgets
3. **get_amortized_costs** - Get amortized costs (with validated dimensions)

## Valid Dimensions

For `get_amortized_costs`, only these dimensions are supported:
- `vendor`
- `service`
- `service_name`
- `enhanced_service_name`
- `account_id`
- `region`
- `date`

## Troubleshooting

### Authentication Errors

If you get authentication errors:
1. Check your `.env` file has correct credentials
2. Verify credentials are valid in Cloudability
3. Check `CLOUDABILITY_AUTH_TYPE` matches your authentication method

### Invalid Dimension Errors

If you get "Invalid dimensions" errors:
- Only use dimensions from the validated list above
- Dimensions like `cluster_name`, `namespace` are not supported for amortized costs

### Import Errors

If you get import errors:
```bash
make install
make verify
```

## Next Steps

- Read [API Reference](API_REFERENCE.md) for complete API documentation
- Check [Usage Examples](USAGE_EXAMPLES.md) for more examples
- See [Example Prompts](../examples/example_prompts.md) for Cursor IDE prompts

## Getting Help

- Check the [README](../README.md) for overview
- Review [API Reference](API_REFERENCE.md) for detailed API docs
- See [Usage Examples](USAGE_EXAMPLES.md) for code examples

