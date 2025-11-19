# Comprehensive Cost Report Tool - Usage Guide

## Overview

The `generate_cost_report` tool provides a comprehensive solution for generating amortized cost reports with flexible filtering, multiple export formats, and different report types.

## Features

- **View-based reports**: Restrict data to specific Cloudability dashboard views
- **Flexible filtering**: Filter by AWS account, K8s cluster, namespace, or product_id
- **Multiple export formats**: JSON, CSV, or Markdown (with formatted tables)
- **Report types**: Condensed (summary) or Detailed (breakdown)
- **Time ranges**: Last month, specific month, or custom date range
- **Amortized costs**: Always uses amortized cost metrics

## Tool: `generate_cost_report`

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `view_name` | string | Yes | Name of the dashboard view to restrict data to |
| `report_type` | string | No | `"condensed"` (all namespaces summary) or `"detailed"` (specific breakdown). Default: `"condensed"` |
| `time_range` | string | No | Time range: `"last_month"`, `"YYYY-MM"` (specific month), or `"YYYY-MM-DD,YYYY-MM-DD"` (custom range). Default: `"last_month"` |
| `account_id` | string | No | Filter by AWS account ID |
| `cluster_name` | string | No | Filter by Kubernetes cluster name (supports wildcards like `"prod*"`) |
| `namespace` | string | No | Filter by Kubernetes namespace (supports wildcards like `"ici*"`). Required for detailed reports |
| `product_id` | string | No | Filter by product ID (e.g., `"K8s"` for Kubernetes) |
| `export_format` | string | No | Export format: `"json"`, `"csv"`, or `"markdown"`. Default: `"json"` |
| `granularity` | string | No | Time granularity: `"daily"` or `"monthly"`. Default: `"daily"` |

### Usage Examples

#### Example 1: Condensed Report for All Namespaces (Last Month)

```json
{
  "view_name": "Product-12284-OFT - self-managed Kubernetes",
  "report_type": "condensed",
  "time_range": "last_month",
  "product_id": "K8s",
  "export_format": "markdown"
}
```

**Result**: Summary report showing costs grouped by namespace for the last 30 days.

#### Example 2: Detailed Report for Specific Namespace

```json
{
  "view_name": "Product-12284-OFT - self-managed Kubernetes",
  "report_type": "detailed",
  "namespace": "ici*",
  "time_range": "2025-10",
  "product_id": "K8s",
  "export_format": "csv"
}
```

**Result**: Detailed breakdown of costs for namespaces matching "ici*" in October 2025, grouped by service and pod.

#### Example 3: Custom Date Range with AWS Account Filter

```json
{
  "view_name": "AWS Cost Overview",
  "report_type": "condensed",
  "time_range": "2025-10-01,2025-10-31",
  "account_id": "123456789012",
  "export_format": "json"
}
```

**Result**: JSON report for specific AWS account for October 2025.

#### Example 4: Cluster-Specific Report

```json
{
  "view_name": "Product-12284-OFT - self-managed Kubernetes",
  "report_type": "detailed",
  "namespace": "ici*",
  "time_range": "last_month",
  "product_id": "K8s",
  "export_format": "markdown"
}
```

**Result**: Markdown table showing detailed costs for production namespace in production clusters.

### Time Range Formats

1. **Last Month**: `"last_month"` - Last 30 days from today
2. **Specific Month**: `"YYYY-MM"` - Entire month (e.g., `"2025-10"` for October 2025)
3. **Custom Range**: `"YYYY-MM-DD,YYYY-MM-DD"` - Custom date range (e.g., `"2025-10-01,2025-10-31"`)

### Report Types

#### Condensed Reports
- Groups data by namespace (and optionally cluster, account)
- Provides summary view of all namespaces
- Best for high-level cost overview
- No namespace filter required

#### Detailed Reports
- Includes service and pod-level breakdown
- Requires namespace filter
- Best for deep-dive analysis
- Includes date dimension for time-series analysis

### Export Formats

#### JSON
Returns structured data in JSON format:
```json
{
  "success": true,
  "data": [...],
  "export_format": "json",
  "total_records": 150
}
```

#### CSV
Returns CSV-formatted string in `csv_data` field:
```json
{
  "success": true,
  "csv_data": "namespace,cost,date\n...",
  "export_format": "csv"
}
```

#### Markdown
Returns Markdown table in `markdown_data` field:
```json
{
  "success": true,
  "markdown_data": "# Cost Report - View Name\n\n| Namespace | Cost | ...",
  "export_format": "markdown"
}
```

### Filter Support

The tool supports filtering by:
- **AWS Account**: `account_id` parameter
- **K8s Cluster**: `cluster_name` parameter (supports wildcards)
- **K8s Namespace**: `namespace` parameter (supports wildcards, required for detailed reports)
- **Product ID**: `product_id` parameter (e.g., `"K8s"`)

Wildcard support:
- `"ici*"` matches namespaces starting with "ici"
- `"prod*"` matches clusters starting with "prod"

### Notes

1. **Amortized Costs**: The tool always attempts to use amortized costs. If namespace filtering is not supported for amortized costs, it will fallback to total costs with a warning.

2. **View Restrictions**: The view name must match exactly as it appears in Cloudability dashboard.

3. **Namespace Filtering**: Some API endpoints may not support namespace filtering directly. The tool includes fallback logic to handle this.

4. **Detailed Reports**: Require a namespace filter to provide meaningful breakdown.

## Error Handling

The tool provides helpful error messages and suggestions when:
- Invalid time range format
- Missing required parameters (e.g., namespace for detailed reports)
- API endpoint limitations (e.g., namespace filtering not supported)
- View not found

## Response Format

All responses include:
- `success`: Boolean indicating success/failure
- `export_format`: Format of the exported data
- `report_type`: Type of report generated
- `time_range`: Time range used
- `start_date` / `end_date`: Actual date range
- `filters_applied`: Filters that were applied
- `total_records`: Number of records returned
- Format-specific data field (`data`, `csv_data`, or `markdown_data`)

