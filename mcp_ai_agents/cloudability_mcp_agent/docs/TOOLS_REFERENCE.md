# Cloudability MCP Server - Complete Tools Reference

## Tool Count: 20 Tools

This document provides a complete reference for all available tools in the Cloudability MCP Server.

---

## Cost Reporting Tools

### 1. `get_cost_report_by_view`
Get cost report data for a specific dashboard view.

**Parameters:**
- `view_name` (required): Dashboard view name
- `product_id` (optional): Filter by product ID
- `start_date` (optional): Start date (YYYY-MM-DD)
- `end_date` (optional): End date (YYYY-MM-DD)
- `limit` (optional): Max records (default: 50)
- `offset` (optional): Pagination offset

**Example:**
```
Get cost report for "AWS Cost Overview" view
```

### 2. `get_cost_report_with_filters`
Get cost report with advanced filtering.

**Parameters:**
- `view_name` (required): Dashboard view name
- `filters` (optional): Filter conditions
- `dimensions` (optional): Dimensions to group by
- `metrics` (optional): Metrics to retrieve
- `start_date` (optional): Start date
- `end_date` (optional): End date

**Example:**
```
Get cost report for "AWS Cost Overview" with filters for product_id K8s and vendor AWS
```

### 3. `get_amortized_costs`
Get amortized cost data with view/namespace/product_id filters.

**Parameters:**
- `start_date` (optional): Start date (defaults to 30 days ago)
- `end_date` (optional): End date (defaults to today)
- `filters` (optional): Filter conditions (namespace, product_id, etc.)
- `dimensions` (optional): Dimensions to group by (default: ['service'])
- `view_name` (optional): View restriction
- `granularity` (optional): 'daily' or 'monthly' (default: 'monthly')
- `export_format` (optional): 'json' or 'csv' (default: 'json')

**Example:**
```
Get amortized costs for all services in the last 30 days, export as CSV
```

### 4. `export_cost_report`
Export custom cost report.

**Parameters:**
- `start_date` (required): Start date
- `end_date` (required): End date
- `filters` (optional): Filter conditions
- `dimensions` (optional): Dimensions to group by
- `metrics` (optional): Metrics to include
- `export_format` (optional): 'json' or 'csv'
- `file_name` (optional): Custom file name

**Example:**
```
Export cost report for AWS EC2 in us-east-1 as CSV
```

### 5. `generate_cost_report`
Generate comprehensive amortized cost reports with flexible filtering and multiple export formats.

**Parameters:**
- `view_name` (required): Dashboard view name
- `report_type` (optional): 'condensed' (all namespaces) or 'detailed' (specific namespace)
- `time_range` (optional): 'last_month', 'YYYY-MM', or 'YYYY-MM-DD,YYYY-MM-DD'
- `account_id` (optional): Filter by AWS account ID
- `cluster_name` (optional): Filter by Kubernetes cluster name
- `namespace` (optional): Filter by Kubernetes namespace (required for detailed reports)
- `product_id` (optional): Filter by product ID (e.g., 'K8s')
- `dimensions` (optional): Custom dimensions to group by
- `export_format` (optional): 'json', 'csv', or 'markdown'
- `granularity` (optional): 'daily' or 'monthly'

**Example:**
```
Generate detailed cost report for view "Product-12284-OFT - self-managed Kubernetes" with namespace "ici*" for October 2025, export as markdown
```

**See Also:** [Comprehensive Report Guide](COMPREHENSIVE_REPORT_USAGE.md) for detailed documentation.

---

## Container/Kubernetes Tools

### 6. `get_container_costs`
Get container/Kubernetes cost breakdown.

**Parameters:**
- `start_date` (optional): Start date
- `end_date` (optional): End date
- `filters` (optional): Filter conditions (cluster_name, namespace, etc.)
- `group_by` (optional): Group by (cluster, namespace, pod, container, service)
- `metrics` (optional): Metrics to retrieve
- `export_format` (optional): 'json' or 'csv'

**Example:**
```
Get container costs for production cluster grouped by namespace and pod
```

### 7. `get_container_resource_usage`
Get container resource usage metrics.

**Parameters:**
- `start_date` (optional): Start date
- `end_date` (optional): End date
- `filters` (optional): Filter conditions
- `metrics` (optional): Resource metrics (cpu/reserved, memory/reserved_rss, etc.)

**Example:**
```
Get container resource usage for production cluster showing CPU and memory metrics
```

### 8. `analyze_container_cost_allocation`
Analyze container cost allocation.

**Parameters:**
- `start_date` (optional): Start date
- `end_date` (optional): End date
- `group` (optional): Group by (namespace, pod, service, labels)
- `metrics` (optional): Metrics to analyze
- `filters` (optional): Filter conditions (array format)
- `cost_type` (optional): 'total_cost' or 'adjusted_amortized_cost'

**Example:**
```
Analyze container cost allocation by namespace for production cluster
```

---

## Budget Management Tools

### 9. `list_budgets`
List all budgets.

**Parameters:** None

**Example:**
```
List all budgets in my Cloudability account
```

### 10. `get_budget`
Get budget details.

**Parameters:**
- `budget_id` (required): Budget ID

**Example:**
```
Get detailed information for budget "Q1 2024 Budget"
```

### 11. `create_budget`
Create a new budget.

**Parameters:**
- `name` (required): Budget name
- `basis` (required): 'cash', 'adjusted', or 'amortized'
- `view_id` (required): View ID
- `months` (required): List of month thresholds

**Example:**
```
Create a quarterly budget for Q1 2024 with thresholds: January $50k, February $55k, March $60k
```

### 12. `update_budget`
Update budget.

**Parameters:**
- `budget_id` (required): Budget ID
- `months` (optional): Updated month thresholds
- `name` (optional): Updated budget name

**Example:**
```
Update budget budget-123 to set January threshold to $45k
```

---

## Forecast & Estimate Tools

### 13. `get_spending_estimate`
Get current month spending estimate.

**Parameters:**
- `view_id` (optional): View ID (default: "0")
- `basis` (optional): 'cash', 'adjusted', or 'amortized' (default: 'cash')

**Example:**
```
Get current month spending estimate
```

### 14. `get_spending_forecast`
Generate spending forecast.

**Parameters:**
- `view_id` (optional): View ID (default: "0")
- `basis` (optional): Forecast basis (default: 'cash')
- `months_back` (optional): Months of history (default: 6)
- `months_forward` (optional): Months to forecast (default: 12)
- `use_current_estimate` (optional): Use current estimate (default: true)
- `remove_one_time_charges` (optional): Remove one-time charges (default: true)

**Example:**
```
Generate 12-month spending forecast based on 6 months of history
```

---

## Tag Explorer Tools

### 15. `list_available_tags`
List available tag keys.

**Parameters:**
- `limit` (optional): Maximum tag keys to return

**Example:**
```
What tags are available in my Cloudability account?
```

### 16. `explore_tags`
Explore costs by tags.

**Parameters:**
- `tag_key` (required): Tag key to explore
- `tag_value` (optional): Specific tag value
- `start_date` (optional): Start date
- `end_date` (optional): End date
- `additional_filters` (optional): Additional filter conditions
- `export_format` (optional): 'json' or 'csv'

**Example:**
```
What are the costs by Environment tag for Production environment?
```

---

## Anomaly Detection Tools

### 17. `get_anomaly_detection`
Detect cost anomalies.

**Parameters:**
- `start_date` (optional): Start date
- `end_date` (optional): End date
- `filters` (optional): Filter conditions
- `severity` (optional): 'low', 'medium', 'high', or 'all' (default: 'all')
- `min_cost_change_percent` (optional): Minimum change % (default: 10.0)
- `export_format` (optional): 'json' or 'csv'

**Example:**
```
Find high-severity cost anomalies in AWS for the last month
```

---

## Discovery Tools

### 18. `list_views`
List all available views.

**Parameters:**
- `limit` (optional): Maximum views to return
- `offset` (optional): Pagination offset

**Example:**
```
List all available views in my Cloudability account
```

### 19. `get_available_measures`
Discover available dimensions and metrics.

**Parameters:** None

**Example:**
```
What dimensions and metrics are available for cost reports?
```

### 20. `get_filter_operators`
Get available filter operators.

**Parameters:** None

**Example:**
```
What filter operators can I use in cost reports?
```

---

## Quick Reference by Use Case

### Cost Analysis
- `get_amortized_costs` - Amortized cost analysis
- `get_cost_report_by_view` - View-based reports
- `get_cost_report_with_filters` - Advanced filtering
- `export_cost_report` - Custom exports
- `generate_cost_report` - Comprehensive reporting (condensed/detailed)

### Container/Kubernetes
- `get_container_costs` - Container cost breakdown
- `get_container_resource_usage` - Resource metrics
- `analyze_container_cost_allocation` - Cost allocation

### Budget Management
- `list_budgets` - List budgets
- `get_budget` - Budget details
- `create_budget` - Create budget
- `update_budget` - Update budget

### Forecasting
- `get_spending_estimate` - Current estimate
- `get_spending_forecast` - Future forecast

### Tag Analysis
- `list_available_tags` - List tags
- `explore_tags` - Explore by tags

### Anomaly Detection
- `get_anomaly_detection` - Detect anomalies

### Discovery
- `list_views` - List views
- `get_available_measures` - Discover measures
- `get_filter_operators` - Get operators

---

## Export Formats

All reporting tools support multiple export formats:

- **JSON** (default) - Structured data for programmatic use
- **CSV** - Spreadsheet-compatible format  
- **Markdown** - Formatted tables (for `generate_cost_report` only)

## See Also

- [Usage Examples](USAGE_EXAMPLES.md) - Practical examples
- [Comprehensive Report Guide](COMPREHENSIVE_REPORT_USAGE.md) - Advanced reporting tool
- [Framework Guide](FRAMEWORK_GUIDE.md) - For developers extending the server

