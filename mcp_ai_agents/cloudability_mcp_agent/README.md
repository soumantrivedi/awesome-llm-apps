# Cloudability MCP Server

A comprehensive Model Context Protocol (MCP) server for IBM Cloudability API, providing 20 tools for cost analysis, budget management, container costs, and more.

## Quick Start

### Installation

```bash
cd mcp_ai_agents/cloudability_mcp_agent

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Configure Authentication

**Option 1: Public/Private Key Pair (Recommended)**

See **[SETUP_KEYS.md](SETUP_KEYS.md)** for step-by-step instructions on adding your keys.

Quick setup - create `.env` file:
```bash
CLOUDABILITY_PUBLIC_KEY=your_public_key_here
CLOUDABILITY_PRIVATE_KEY=your_private_key_here
CLOUDABILITY_ENVIRONMENT_ID=your_environment_id_here
CLOUDABILITY_AUTH_TYPE=opentoken
CLOUDABILITY_BASE_URL=https://api.cloudability.com/v3
```

**Option 2: Legacy API Key**

```bash
echo "CLOUDABILITY_API_KEY=your_api_key_here" > .env
echo "CLOUDABILITY_BASE_URL=https://api.cloudability.com/v3" >> .env
```

### Configure in Cursor

Add to `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "cloudability": {
      "command": "/absolute/path/to/venv/bin/python3",
      "args": ["-u", "/absolute/path/to/cloudability_mcp_server.py"],
      "env": {
        "CLOUDABILITY_API_KEY": "your_api_key_here",
        "CLOUDABILITY_BASE_URL": "https://api.cloudability.com/v3",
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

**Get your credentials:**
- **Public/Private Keys**: User Profile → API Keys in Cloudability
- **Legacy API Key**: [Cloudability Preferences](https://app.apptio.com/cloudability#/settings/preferences) → Enable API

**See [SETUP_KEYS.md](SETUP_KEYS.md) for detailed setup instructions.**

## Features

- **20 Tools** covering cost analysis, budgets, containers, and more
- **Multiple Export Formats** - JSON, CSV, and Markdown
- **Comprehensive Reporting** - Condensed and detailed report types
- **Flexible Filtering** - Filter by account, cluster, namespace, product_id
- **API v3 Compliant** - Based on official IBM Cloudability API v3 documentation
- **Framework-based** - Easy to extend with new tools

## Available Tools

### Cost Reporting (5 tools)
- `get_cost_report_by_view` - View-based reports
- `get_cost_report_with_filters` - Advanced filtering
- `get_amortized_costs` - Amortized cost analysis
- `export_cost_report` - Custom report export
- `generate_cost_report` - Comprehensive reporting (condensed/detailed)

### Container/Kubernetes (3 tools)
- `get_container_costs` - Container cost breakdown
- `get_container_resource_usage` - Resource metrics
- `analyze_container_cost_allocation` - Cost allocation

### Budget Management (4 tools)
- `list_budgets` - List all budgets
- `get_budget` - Get budget details
- `create_budget` - Create new budget
- `update_budget` - Update existing budget

### Forecasts & Estimates (2 tools)
- `get_spending_estimate` - Current month estimate
- `get_spending_forecast` - Multi-month forecast

### Tag Explorer (2 tools)
- `list_available_tags` - List tag keys
- `explore_tags` - Explore costs by tags

### Anomaly Detection (1 tool)
- `get_anomaly_detection` - Detect cost anomalies

### Discovery (3 tools)
- `list_views` - List dashboard views
- `get_available_measures` - Discover dimensions/metrics
- `get_filter_operators` - Get filter operators

## Usage Examples

### In Cursor Chat

```
List all available views in Cloudability
```

```
Get amortized costs for all services in the last 30 days, export as CSV
```

```
Generate detailed cost report for view "Product-12284-OFT - self-managed Kubernetes" with namespace "ici*" for October 2025, export as markdown
```

### Python Script

```python
from src.main import CloudabilityMCPServer
import asyncio

async def example():
    server = CloudabilityMCPServer(api_key="your_key")
    result = await server.call_tool("get_amortized_costs", {
        "start_date": "2025-10-01",
        "end_date": "2025-10-31",
        "export_format": "csv"
    })
    print(result)

asyncio.run(example())
```

## Documentation

All documentation is in the `docs/` folder:

- **[Quick Start Guide](docs/QUICK_START.md)** - Get up and running
- **[API Reference](docs/API_REFERENCE.md)** - Complete Cloudability API v3 reference (dimensions, metrics, operators)
- **[Tools Reference](docs/TOOLS_REFERENCE.md)** - Complete tool documentation
- **[Usage Examples](docs/USAGE_EXAMPLES.md)** - Practical examples
- **[Comprehensive Report Guide](docs/COMPREHENSIVE_REPORT_USAGE.md)** - Advanced reporting tool
- **[Framework Guide](docs/FRAMEWORK_GUIDE.md)** - For developers extending the server
- **[Security Guidelines](docs/SECURITY.md)** - Security best practices

## Testing

```bash
# Run all tests
make test

# Run specific test suites
make test-working      # Working combinations
make test-comprehensive # Comprehensive tests
make test-api          # API combination tests
```

## Project Structure

```
cloudability_mcp_agent/
├── src/                    # Source code
│   ├── framework/          # Framework components
│   ├── tools/              # Tool implementations
│   ├── api_client.py       # Base API client
│   ├── api_client_extended.py  # Extended API client
│   └── main.py             # MCP server
├── tests/                   # Test suite
├── docs/                    # Documentation
├── cloudability_mcp_server.py  # Entry point
└── requirements.txt        # Dependencies
```

## Troubleshooting

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues and solutions.

## License

See LICENSE file.
