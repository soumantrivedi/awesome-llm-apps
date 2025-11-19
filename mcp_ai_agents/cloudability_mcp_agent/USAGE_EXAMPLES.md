# Cloudability MCP Tools - Usage Examples

This guide provides examples of how to use the TrueCost Explorer Insights tools from Cursor chat and via Python scripts.

## Table of Contents

1. [Using Tools in Cursor Chat](#using-tools-in-cursor-chat)
2. [Amortized Costs](#amortized-costs)
3. [Container Costs](#container-costs)
4. [Tag Explorer](#tag-explorer)
5. [Anomaly Detection](#anomaly-detection)
6. [Export Cost Reports](#export-cost-reports)
7. [Python Script Examples](#python-script-examples)

---

## Using Tools in Cursor Chat

You can invoke these tools directly from Cursor's chat interface. The AI assistant will automatically use the appropriate MCP tool based on your request.

### Example Chat Prompts

#### Get Amortized Costs
```
Get amortized costs for AWS EC2 services for January 2024, grouped by account
```

```
Show me amortized costs for all services in the last 30 days, export as CSV
```

#### Container Costs
```
Get container costs for production cluster, grouped by namespace and pod
```

```
Show me Kubernetes costs for the default namespace in January 2024
```

#### Tag Explorer
```
What are the costs by Environment tag for Production environment?
```

```
List all available tags, then show costs for Team tag
```

#### Anomaly Detection
```
Find high-severity cost anomalies in AWS for the last month
```

```
Detect any cost anomalies with more than 20% change in January 2024
```

#### Export Reports
```
Export a cost report for AWS EC2 t3.medium instances in us-east-1 as CSV
```

```
Create a custom report for all S3 costs grouped by account and region
```

---

## Amortized Costs

### What are Amortized Costs?

Amortized costs spread upfront payments (like Reserved Instances) over their term, providing a more accurate view of daily/monthly costs.

### Cursor Chat Examples

**Simple request:**
```
Get amortized costs for the last 30 days
```

**With filters:**
```
Get amortized costs for AWS EC2 services in January 2024, grouped by account_id
```

**With export:**
```
Get amortized costs for all AWS services and export as CSV
```

### Python Script Example

```python
from cloudability_mcp_server import CloudabilityMCPServer
import asyncio

async def get_amortized_costs():
    server = CloudabilityMCPServer(api_key="your_key", base_url="https://api.cloudability.com/v3")
    
    result = await server._get_amortized_costs({
        "start_date": "2024-01-01",
        "end_date": "2024-01-31",
        "filters": {
            "vendor": "AWS",
            "service": "EC2"
        },
        "dimensions": ["vendor", "service", "account_id"],
        "export_format": "csv"
    })
    
    print(f"Total records: {result.get('total_records')}")
    print(f"Export path: {result.get('export_path')}")

asyncio.run(get_amortized_costs())
```

### Common Filter Keys

- `vendor`: AWS, Azure, GCP
- `service`: EC2, S3, RDS, etc.
- `account_id`: Your cloud account ID
- `region`: us-east-1, eu-west-1, etc.
- `product_id`: K8s, EC2, etc.

---

## Container Costs

### What are Container Costs?

Container costs show Kubernetes or containerized workload costs split by container/pod level, helping you understand container resource consumption.

### Cursor Chat Examples

**Basic container costs:**
```
Get container costs for the last 30 days, grouped by cluster and namespace
```

**Specific cluster:**
```
Show me container costs for prod-cluster in the default namespace
```

**Detailed breakdown:**
```
Get container costs grouped by cluster, namespace, pod, and container
```

### Python Script Example

```python
result = await server._get_container_costs({
    "start_date": "2024-01-01",
    "end_date": "2024-01-31",
    "filters": {
        "cluster_name": "prod-cluster",
        "namespace": "default"
    },
    "group_by": ["cluster", "namespace", "pod"],
    "export_format": "csv"
})
```

### Common Filter Keys

- `cluster_name`: Your Kubernetes cluster name
- `namespace`: Kubernetes namespace
- `pod_name`: Specific pod name
- `container_name`: Container name
- `product_id`: K8s (for Kubernetes)

### Group By Options

- `cluster`: Group by cluster
- `namespace`: Group by namespace
- `pod`: Group by pod
- `container`: Group by container
- `service`: Group by service

---

## Tag Explorer

### What is Tag Explorer?

Tag explorer helps you analyze costs based on custom tags (like Environment, Team, Project, etc.), providing business dimension cost allocation.

### Cursor Chat Examples

**List available tags:**
```
What tags are available in my Cloudability account?
```

**Explore by tag:**
```
Show me costs by Environment tag for Production environment
```

**All values for a tag:**
```
What are the costs for all values of the Team tag?
```

**With additional filters:**
```
Get costs by Project tag for AWS services only
```

### Python Script Example

```python
# First, list available tags
tags_result = await server._list_available_tags({})
print(f"Available tags: {tags_result.get('tag_keys')}")

# Then explore a specific tag
result = await server._explore_tags({
    "tag_key": "Environment",
    "tag_value": "Production",  # Leave empty to see all values
    "start_date": "2024-01-01",
    "end_date": "2024-01-31",
    "additional_filters": {
        "vendor": "AWS"
    },
    "export_format": "csv"
})
```

### Common Tag Keys

- `Environment`: Production, Development, Staging
- `Team`: Engineering, Marketing, Sales
- `Project`: Project name or ID
- `CostCenter`: Cost center code
- `Owner`: Resource owner

---

## Anomaly Detection

### What is Anomaly Detection?

Anomaly detection identifies unusual spending patterns, cost spikes, or unexpected changes in cloud costs, helping detect billing issues, resource leaks, or optimization opportunities.

### Cursor Chat Examples

**Basic anomaly detection:**
```
Find cost anomalies in the last 30 days
```

**High severity only:**
```
Show me high-severity cost anomalies for AWS
```

**Custom threshold:**
```
Detect anomalies with more than 25% cost change in January
```

**Filtered by account:**
```
Find anomalies for account 123456789 with at least 15% change
```

### Python Script Example

```python
result = await server._get_anomaly_detection({
    "start_date": "2024-01-01",
    "end_date": "2024-01-31",
    "severity": "high",  # Options: low, medium, high, all
    "filters": {
        "vendor": "AWS",
        "account_id": "123456789"
    },
    "min_cost_change_percent": 20.0,
    "export_format": "json"
})
```

### Severity Levels

- `low`: Minor cost changes
- `medium`: Moderate cost changes
- `high`: Significant cost changes
- `all`: All anomalies regardless of severity

### Parameters

- `min_cost_change_percent`: Minimum percentage change to consider as anomaly (default: 10.0)

---

## Export Cost Reports

### What is Export Cost Report?

A flexible tool that allows you to create custom cost reports by specifying any filter keys and values you know. Perfect for creating tailored reports for specific analysis needs.

### Cursor Chat Examples

**Simple export:**
```
Export cost report for AWS EC2 in January 2024 as CSV
```

**Multiple filters:**
```
Export costs for AWS S3 in us-east-1, grouped by account, as JSON
```

**Custom dimensions:**
```
Create a report for all services grouped by vendor, service, account, and region
```

**Named export:**
```
Export EC2 costs to a file named 'ec2_monthly_report'
```

### Python Script Example

```python
result = await server._export_cost_report({
    "start_date": "2024-01-01",
    "end_date": "2024-01-31",
    "filters": {
        "vendor": "AWS",
        "service": "EC2",
        "region": "us-east-1",
        "instance_type": "t3.medium"
    },
    "dimensions": ["vendor", "service", "account_id", "region", "instance_type"],
    "metrics": ["cost", "usage"],
    "export_format": "csv",
    "file_name": "aws_ec2_t3_medium_costs"
})
```

### Common Filter Keys

You can use any valid Cloudability filter key. Common ones include:

- `vendor`: AWS, Azure, GCP
- `service`: EC2, S3, RDS, Lambda, etc.
- `account_id`: Cloud account ID
- `region`: us-east-1, eu-west-1, etc.
- `product_id`: K8s, EC2, etc.
- `instance_type`: t3.medium, m5.large, etc.
- `tag:Environment`: Tag-based filtering
- `tag:Team`: Tag-based filtering

### Common Dimensions

- `vendor`: Cloud provider
- `service`: Cloud service
- `account_id`: Account identifier
- `region`: Geographic region
- `instance_type`: Instance type
- `tag:*`: Any tag key

### Common Metrics

- `cost`: Total cost
- `usage`: Usage amount
- `amortized_cost`: Amortized cost
- `unblended_cost`: Unblended cost

---

## Python Script Examples

### Running the Example Scripts

```bash
cd mcp_ai_agents/cloudability_mcp_agent
source venv/bin/activate
python3 examples_insights_tools.py
```

### Individual Tool Examples

Each tool can be called independently. See `examples_insights_tools.py` for complete working examples.

### Error Handling

All tools return a dictionary with a `success` field. Check this before accessing data:

```python
result = await server._get_amortized_costs({...})

if result.get("success"):
    data = result.get("data")
    total = result.get("total_records")
    export_path = result.get("export_path")
else:
    error = result.get("error")
    error_detail = result.get("error_detail")
    print(f"Error: {error}")
```

### Export Formats

Both JSON and CSV formats are supported:

- **JSON**: Best for programmatic access and further processing
- **CSV**: Best for spreadsheet analysis and sharing

Files are saved in the current working directory with descriptive names.

---

## Tips and Best Practices

1. **Start with list_available_tags**: Before exploring tags, use `list_available_tags` to see what's available
2. **Use date ranges**: Always specify date ranges for accurate reports
3. **Combine filters**: Use multiple filters to narrow down results
4. **Export for analysis**: Use CSV export for spreadsheet analysis, JSON for programmatic use
5. **Check error details**: If a request fails, check `error_detail` for specific API error information
6. **Default dates**: If you don't specify dates, tools default to the last 30 days
7. **Pagination**: For large datasets, you may need to handle pagination (future enhancement)

---

## Troubleshooting

### "API request failed: 400 Bad Request"

- Check that your filter keys and values are correct
- Verify date format is YYYY-MM-DD
- Ensure dimensions and metrics are valid

### "No data returned"

- Try expanding your date range
- Remove some filters to see if data exists
- Check that you have access to the requested data in Cloudability

### "Tag not found"

- Use `list_available_tags` to see available tag keys
- Verify tag key spelling (case-sensitive)
- Check that resources are tagged in Cloudability

---

## Next Steps

- Explore the [README.md](README.md) for setup and configuration
- Run `python3 examples_insights_tools.py` to see all tools in action
- Try the tools in Cursor chat with natural language prompts
- Customize filters and dimensions for your specific needs

