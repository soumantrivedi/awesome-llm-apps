# Example Prompts for Cloudability V2 MCP Server

## List Views

### Basic Usage
```
List all available views in my Cloudability account
```

### With Pagination
```
List the first 10 views in my Cloudability account
```

## List Budgets

### Basic Usage
```
List all budgets in my Cloudability account
```

## Get Amortized Costs

### Basic Usage - By Vendor
```
Get amortized costs grouped by vendor for the last 30 days
```

### By Service
```
Get amortized costs grouped by service for October 2025
```

### By Region
```
Get amortized costs grouped by region for the last month, export as CSV
```

### By Account ID
```
Get amortized costs grouped by account_id for the last 30 days
```

### Multiple Dimensions
```
Get amortized costs grouped by vendor and region for the last 30 days
```

### With Filters
```
Get amortized costs for AWS services only, grouped by service, for the last 30 days
```

### Daily Granularity
```
Get daily amortized costs grouped by vendor for the last 30 days
```

### Export as CSV
```
Get amortized costs grouped by vendor for the last 30 days and export as CSV
```

### Custom Date Range
```
Get amortized costs grouped by vendor from 2025-10-01 to 2025-10-31
```

### Relative Time Ranges

**Last Month:**
```
Get amortized costs for last month grouped by vendor and region, export as CSV
```

**Last 2 Months:**
```
Get amortized costs for last 2 months grouped by vendor, export as JSON
```

### Cluster Name Filters

**Wildcard Pattern:**
```
Get amortized costs for last month with cluster name filter mvp01*, grouped by tag10, tag3, tag7
```

**Regex-like Pattern:**
```
Get amortized costs for last 2 months with cluster name matching .*mvp01.* pattern
```

**Contains Operator:**
```
Get amortized costs for last month with container_cluster_name containing mvp01
```

### With View Restriction (RECOMMENDED for Access Control)
```
Get amortized costs for view "Product-12284-OFT - self-managed Kubernetes" grouped by vendor for the last 30 days
```

**Important:** Always specify a view_name when generating cost reports. Users may only have access to specific views. Use `list_views` first to see available views.

**Example workflow:**
1. First, list available views:
```
List all views I have access to
```

2. Then, generate report with view:
```
Get amortized costs for view [View Name] for last month, grouped by vendor and region
```

3. With additional filters:
```
Get amortized costs for view [View Name] for last month, with cluster name filter mvp01*, grouped by tag10, tag3, tag7
```

## TrueCost Explorer Example

### Replicate UI Configuration
The `test_truecost_explorer.py` example demonstrates how to replicate TrueCost Explorer UI configurations.

**Note:** Some dimensions available in the UI (like `lease_type`, `transaction_type`, `usage_family`) are not supported by the amortized costs API endpoint. The example shows:
1. Attempting to match exact UI configuration (will fail validation for unsupported dimensions)
2. Using validated dimensions that work with the API (`enhanced_service_name`, `vendor`, `region`)
3. Different export formats (CSV, JSON, Markdown)

**Run the example:**
```bash
make test-truecost
```

**Example matching UI configuration:**
```
Get amortized costs for November 2025 (2025-11-01 to 2025-11-19) grouped by enhanced_service_name, vendor, and region, export as CSV
```

## Tag Dimensions with Filters Example

### Using Tag Dimensions
The `test_tag_dimensions_example.py` demonstrates using tag dimensions (tag1-tag10) with filters.

**Run the example:**
```bash
make test-tags
```

### Conversational Prompts for Tag Dimensions

**Example 1: Tag dimensions with wildcard filter**
```
Get amortized costs for November 2025 grouped by tag10, tag3, and tag7, 
filtered by container cluster name containing mvp01, export as CSV
```

**Example 2: Tag dimensions with specific filter**
```
Generate a cost report for tag10, tag3, tag7 dimensions with 
container_cluster_name filter matching mvp01 for dates 2025-11-01 to 2025-11-19
```

**Example 3: Natural language query**
```
Show me amortized costs by tags (tag10, tag3, tag7) for clusters 
with mvp01 in the name, for this month, export as JSON
```

### Filter Syntax

**Wildcard/Contains Filter:**
```
Get amortized costs with container_cluster_name filter containing "mvp01"
```
This translates to: `{"container_cluster_name": "=@mvp01"}`

**Equality Filter:**
```
Get amortized costs with vendor equals AWS
```
This translates to: `{"vendor": "AWS"}`

**Multiple Filters:**
```
Get amortized costs with vendor AWS and region us-east-1
```
This translates to: `{"vendor": "AWS", "region": "us-east-1"}`

