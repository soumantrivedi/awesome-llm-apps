# Usage Examples

Practical examples for using Cloudability MCP Server tools.

## Cost Reporting

### Get Cost Report by View

**Cursor Chat:**
```
Get cost report for "AWS Cost Overview" view filtered by product_id K8s
```

**Parameters:**
```json
{
  "view_name": "AWS Cost Overview",
  "product_id": "K8s",
  "start_date": "2025-10-01",
  "end_date": "2025-10-31"
}
```

### Get Amortized Costs

**Cursor Chat:**
```
Get amortized costs for all services in the last 30 days, export as CSV
```

**Parameters:**
```json
{
  "start_date": "2025-10-01",
  "end_date": "2025-10-31",
  "dimensions": ["service", "vendor"],
  "export_format": "csv"
}
```

### Export Cost Report

**Cursor Chat:**
```
Export cost report for AWS EC2 in us-east-1 region for October 2025 as CSV
```

**Parameters:**
```json
{
  "start_date": "2025-10-01",
  "end_date": "2025-10-31",
  "filters": {
    "vendor": "AWS",
    "service": "EC2",
    "region": "us-east-1"
  },
  "dimensions": ["account_id", "region"],
  "export_format": "csv"
}
```

## Container/Kubernetes

### Get Container Costs

**Cursor Chat:**
```
Get container costs for production cluster grouped by namespace and pod
```

**Parameters:**
```json
{
  "start_date": "2025-10-01",
  "end_date": "2025-10-31",
  "filters": {
    "cluster_name": "prod-cluster",
    "product_id": "K8s"
  },
  "group_by": ["namespace", "pod"],
  "export_format": "json"
}
```

### Analyze Container Cost Allocation

**Cursor Chat:**
```
Analyze container cost allocation by namespace for production cluster
```

**Parameters:**
```json
{
  "start_date": "2025-10-01",
  "end_date": "2025-10-31",
  "group": ["namespace"],
  "filters": ["cluster_name==prod-cluster"],
  "cost_type": "adjusted_amortized_cost"
}
```

## Budget Management

### List Budgets

**Cursor Chat:**
```
List all budgets in my Cloudability account
```

### Create Budget

**Cursor Chat:**
```
Create a quarterly budget for Q1 2025 with thresholds: January $50k, February $55k, March $60k
```

**Parameters:**
```json
{
  "name": "Q1 2025 Budget",
  "basis": "amortized",
  "view_id": "12345",
  "months": [
    {"month": "2025-01", "threshold": 50000},
    {"month": "2025-02", "threshold": 55000},
    {"month": "2025-03", "threshold": 60000}
  ]
}
```

## Tag Exploration

### Explore Costs by Tags

**Cursor Chat:**
```
What are the costs by Environment tag for Production environment?
```

**Parameters:**
```json
{
  "tag_key": "Environment",
  "tag_value": "Production",
  "start_date": "2025-10-01",
  "end_date": "2025-10-31"
}
```

## Anomaly Detection

### Detect Cost Anomalies

**Cursor Chat:**
```
Find high-severity cost anomalies in AWS for the last month
```

**Parameters:**
```json
{
  "start_date": "2025-10-01",
  "end_date": "2025-10-31",
  "filters": {
    "vendor": "AWS"
  },
  "severity": "high",
  "min_cost_change_percent": 20.0
}
```

## Comprehensive Reporting

### Generate Detailed Report

**Cursor Chat:**
```
Generate detailed cost report for view "Product-12284-OFT - self-managed Kubernetes" with namespace "ici*" for October 2025, export as markdown
```

**Parameters:**
```json
{
  "view_name": "Product-12284-OFT - self-managed Kubernetes",
  "report_type": "detailed",
  "namespace": "ici*",
  "time_range": "2025-10",
  "product_id": "K8s",
  "export_format": "markdown"
}
```

### Generate Condensed Report

**Cursor Chat:**
```
Generate condensed cost report for all namespaces in view "Product-12284-OFT - self-managed Kubernetes" for last month
```

**Parameters:**
```json
{
  "view_name": "Product-12284-OFT - self-managed Kubernetes",
  "report_type": "condensed",
  "time_range": "last_month",
  "product_id": "K8s",
  "export_format": "json"
}
```

## Export Formats

All reporting tools support multiple export formats:

- **JSON** (default) - Structured data for programmatic use
- **CSV** - Spreadsheet-compatible format
- **Markdown** - Formatted tables (for `generate_cost_report`)

## Python Script Examples

### Basic Usage

```python
from src.main import CloudabilityMCPServer
import asyncio

async def example():
    server = CloudabilityMCPServer(api_key="your_key")
    
    # List views
    views = await server.call_tool("list_views", {})
    print(views)
    
    # Get amortized costs
    costs = await server.call_tool("get_amortized_costs", {
        "start_date": "2025-10-01",
        "end_date": "2025-10-31",
        "export_format": "csv"
    })
    print(costs)

asyncio.run(example())
```

## See Also

- **[Tools Reference](TOOLS_REFERENCE.md)** - Complete tool documentation
- **[Comprehensive Report Guide](COMPREHENSIVE_REPORT_USAGE.md)** - Advanced reporting tool

