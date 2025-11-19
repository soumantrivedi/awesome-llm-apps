# Usage Examples - Cloudability V2 MCP Server

## Basic Usage

### List Views

**Cursor Chat:**
```
List all views in my Cloudability account
```

**Programmatic:**
```python
import asyncio
from src.main import CloudabilityV2MCPServer

async def main():
    server = CloudabilityV2MCPServer()
    result = await server.call_tool("list_views", {"limit": 10})
    print(result)

asyncio.run(main())
```

### List Budgets

**Cursor Chat:**
```
List all budgets in my Cloudability account
```

**Programmatic:**
```python
import asyncio
from src.main import CloudabilityV2MCPServer

async def main():
    server = CloudabilityV2MCPServer()
    result = await server.call_tool("list_budgets", {})
    print(result)

asyncio.run(main())
```

### Get Amortized Costs

**Cursor Chat:**
```
Get amortized costs grouped by vendor for the last 30 days
```

**Programmatic:**
```python
import asyncio
from datetime import datetime, timedelta
from src.main import CloudabilityV2MCPServer

async def main():
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    server = CloudabilityV2MCPServer()
    result = await server.call_tool("get_amortized_costs", {
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "dimensions": ["vendor"],
        "granularity": "monthly"
    })
    print(result)

asyncio.run(main())
```

## Advanced Examples

### Multiple Dimensions

**Cursor Chat:**
```
Get amortized costs grouped by vendor and region for the last 30 days
```

**Programmatic:**
```python
result = await server.call_tool("get_amortized_costs", {
    "start_date": "2025-10-01",
    "end_date": "2025-10-31",
    "dimensions": ["vendor", "region"],
    "granularity": "monthly"
})
```

### With Filters

**Cursor Chat:**
```
Get amortized costs for AWS services only, grouped by service, for the last 30 days
```

**Programmatic:**
```python
result = await server.call_tool("get_amortized_costs", {
    "start_date": "2025-10-01",
    "end_date": "2025-10-31",
    "dimensions": ["service"],
    "filters": {"vendor": "AWS"},
    "granularity": "monthly"
})
```

### Daily Granularity

**Cursor Chat:**
```
Get daily amortized costs grouped by vendor for the last 30 days
```

**Programmatic:**
```python
result = await server.call_tool("get_amortized_costs", {
    "start_date": "2025-10-01",
    "end_date": "2025-10-31",
    "dimensions": ["vendor", "date"],
    "granularity": "daily"
})
```

### CSV Export

**Cursor Chat:**
```
Get amortized costs grouped by vendor for the last 30 days and export as CSV
```

**Programmatic:**
```python
result = await server.call_tool("get_amortized_costs", {
    "start_date": "2025-10-01",
    "end_date": "2025-10-31",
    "dimensions": ["vendor"],
    "granularity": "monthly",
    "export_format": "csv"
})

# CSV file is automatically saved
print(f"CSV exported to: {result.get('export_path')}")
```

### Custom Date Range

**Cursor Chat:**
```
Get amortized costs grouped by vendor from 2025-10-01 to 2025-10-31
```

**Programmatic:**
```python
result = await server.call_tool("get_amortized_costs", {
    "start_date": "2025-10-01",
    "end_date": "2025-10-31",
    "dimensions": ["vendor"],
    "granularity": "monthly"
})
```

### By Account ID

**Cursor Chat:**
```
Get amortized costs grouped by account_id for the last 30 days
```

**Programmatic:**
```python
result = await server.call_tool("get_amortized_costs", {
    "start_date": "2025-10-01",
    "end_date": "2025-10-31",
    "dimensions": ["account_id"],
    "granularity": "monthly"
})
```

### By Service

**Cursor Chat:**
```
Get amortized costs grouped by service for October 2025
```

**Programmatic:**
```python
result = await server.call_tool("get_amortized_costs", {
    "start_date": "2025-10-01",
    "end_date": "2025-10-31",
    "dimensions": ["service"],
    "granularity": "monthly"
})
```

## Error Handling

### Invalid Dimension

**Example:**
```python
result = await server.call_tool("get_amortized_costs", {
    "start_date": "2025-10-01",
    "end_date": "2025-10-31",
    "dimensions": ["cluster_name"],  # Invalid!
    "granularity": "monthly"
})

# Result will have success=False with validation error
if not result.get("success"):
    print(f"Error: {result.get('error')}")
```

### Missing Required Parameters

**Example:**
```python
result = await server.call_tool("get_amortized_costs", {
    # Missing start_date and end_date
    "dimensions": ["vendor"]
})

# Result will have success=False with validation error
if not result.get("success"):
    print(f"Error: {result.get('error')}")
```

## Best Practices

1. **Always validate dimensions** - Only use dimensions from the validated list
2. **Use appropriate granularity** - Use `monthly` for summaries, `daily` for detailed analysis
3. **Handle errors gracefully** - Check `success` field before processing results
4. **Use filters wisely** - Filters can help reduce data size and improve performance
5. **Export to CSV for large datasets** - CSV format is more efficient for large result sets

## Common Patterns

### Last 30 Days Pattern

```python
from datetime import datetime, timedelta

end_date = datetime.now()
start_date = end_date - timedelta(days=30)

result = await server.call_tool("get_amortized_costs", {
    "start_date": start_date.strftime("%Y-%m-%d"),
    "end_date": end_date.strftime("%Y-%m-%d"),
    "dimensions": ["vendor"],
    "granularity": "monthly"
})
```

### Specific Month Pattern

```python
result = await server.call_tool("get_amortized_costs", {
    "start_date": "2025-10-01",
    "end_date": "2025-10-31",
    "dimensions": ["vendor", "service"],
    "granularity": "monthly"
})
```

### AWS Only Pattern

```python
result = await server.call_tool("get_amortized_costs", {
    "start_date": "2025-10-01",
    "end_date": "2025-10-31",
    "dimensions": ["service"],
    "filters": {"vendor": "AWS"},
    "granularity": "monthly"
})
```

