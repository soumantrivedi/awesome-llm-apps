# Cloudability V2 MCP Server

A simplified, validated MCP (Model Context Protocol) server for IBM Cloudability API v3. This server includes only three carefully validated tools that are known to work correctly with the Cloudability API.

## Features

- **Validated Tools**: Only includes tools that have been tested and validated
- **Simplified Architecture**: Clean, modular codebase for easy maintenance
- **Error Handling**: Proper error handling to avoid 4xx/5xx errors
- **Dimension Validation**: Only allows dimensions that work with amortized costs API
- **Multiple Export Formats**: Supports JSON and CSV export

## Available Tools

1. **list_views** - List all available dashboard views in your Cloudability account
2. **list_budgets** - List all budgets in your Cloudability account
3. **get_amortized_costs** - Get amortized cost data with validated dimensions

## Valid Dimensions for Amortized Costs

The `get_amortized_costs` tool only accepts dimensions that are known to work with the Cloudability API:

- `vendor` - Cloud provider (AWS, Azure, GCP)
- `service` - Service name
- `service_name` - Alternative service name
- `enhanced_service_name` - Enhanced service name with details
- `account_id` - Cloud account identifier
- `region` - Geographic region
- `date` - Date dimension for time-series

**Note**: Dimensions like `cluster_name`, `namespace`, etc. are not supported for amortized costs and will be rejected with a validation error.

## Installation

1. Clone this repository
2. Install dependencies:
   ```bash
   make install
   ```
3. Set up your credentials:
   ```bash
   make secrets
   ```
4. Register the MCP server in Cursor IDE:
   ```bash
   make register
   ```

## Configuration

Create a `.env` file with your Cloudability credentials:

### Basic Authentication (API Key)
```env
CLOUDABILITY_API_KEY=your-api-key-here
CLOUDABILITY_AUTH_TYPE=basic
CLOUDABILITY_BASE_URL=https://api.cloudability.com/v3
```

### Enhanced Access Administration (Public/Private Key)
```env
CLOUDABILITY_PUBLIC_KEY=your-public-key-here
CLOUDABILITY_PRIVATE_KEY=your-private-key-here
CLOUDABILITY_ENVIRONMENT_ID=your-environment-id-here
CLOUDABILITY_AUTH_TYPE=opentoken
CLOUDABILITY_BASE_URL=https://api.cloudability.com/v3
```

## Usage

### In Cursor IDE

Once registered, you can use the tools in Cursor IDE chat:

```
List all views in my Cloudability account
```

```
Get amortized costs grouped by vendor for the last 30 days
```

```
Get amortized costs grouped by service for October 2025, export as CSV
```

### Programmatic Usage

```python
import asyncio
from src.main import CloudabilityV2MCPServer

async def main():
    server = CloudabilityV2MCPServer()
    result = await server.call_tool("list_views", {"limit": 10})
    print(result)

asyncio.run(main())
```

## Testing

Run the test suite to validate all tools:

```bash
make test
```

Run example scripts:

```bash
make test-examples
```

## Project Structure

```
cloudability_v2_mcp/
├── ai-summary/          # AI summaries and prompts
├── docs/                # User-facing and technical documentation
│   ├── README.md
│   ├── API_REFERENCE.md
│   └── USAGE_EXAMPLES.md
├── src/                 # Source code
│   ├── framework/       # Tool framework
│   ├── tools/           # Tool implementations
│   ├── api_client.py    # API client
│   ├── auth.py          # Authentication
│   ├── config.py        # Configuration
│   ├── main.py          # MCP server main
│   └── utils.py         # Utilities
├── examples/            # Example prompts and scripts
├── tests/               # Test suite
├── Makefile            # Build automation
└── requirements.txt    # Dependencies
```

## Makefile Targets

- `make install` - Install dependencies
- `make register` - Show instructions for registering MCP server in Cursor IDE
- `make secrets` - Interactive setup for credentials
- `make test` - Run test suite
- `make test-examples` - Run example scripts
- `make docs` - Show documentation information
- `make clean` - Clean generated files
- `make verify` - Verify installation

## Documentation

- [API Reference](docs/API_REFERENCE.md) - Complete API reference
- [Usage Examples](docs/USAGE_EXAMPLES.md) - Usage examples and patterns
- [Example Prompts](examples/example_prompts.md) - Example prompts for Cursor IDE

## Limitations

This V2 server is intentionally simplified:

- Only includes 3 validated tools
- Only supports dimensions that work with amortized costs
- Does not include experimental or untested features
- Focuses on reliability over feature completeness

## Contributing

When adding new tools:

1. Validate the tool works with the Cloudability API
2. Test thoroughly to avoid 4xx/5xx errors
3. Add tests to the test suite
4. Update documentation
5. Follow the existing code structure

## License

See LICENSE file for details.

