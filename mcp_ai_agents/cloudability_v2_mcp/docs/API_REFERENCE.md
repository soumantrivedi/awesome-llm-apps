# API Reference - Cloudability V2 MCP Server

## Overview

This document provides a complete reference for the Cloudability V2 MCP Server tools.

## Tools

### 1. list_views

List all available dashboard views in your Cloudability account.

**Parameters:**
- `limit` (optional, integer): Maximum views to return (1-250, default: 50)
- `offset` (optional, integer): Pagination offset (default: 0)

**Example:**
```json
{
  "name": "list_views",
  "arguments": {
    "limit": 10
  }
}
```

**Response:**
```json
{
  "success": true,
  "total_views": 169,
  "views": [
    {
      "id": "298479",
      "name": "Product-12284-OFT - self-managed Kubernetes",
      "description": "",
      "ownerEmail": "user@example.com",
      "viewSource": "SYSTEM"
    }
  ]
}
```

---

### 2. list_budgets

List all budgets in your Cloudability account.

**Parameters:**
None

**Example:**
```json
{
  "name": "list_budgets",
  "arguments": {}
}
```

**Response:**
```json
{
  "success": true,
  "total_budgets": 5,
  "budgets": [
    {
      "id": "12345",
      "name": "Q1 2025 Budget",
      "basis": "amortized",
      "view_id": "298479"
    }
  ]
}
```

---

### 3. get_amortized_costs

Get amortized cost data from TrueCost Explorer with validated dimensions.

**Parameters:**
- `start_date` (required, string): Start date in YYYY-MM-DD format
- `end_date` (required, string): End date in YYYY-MM-DD format
- `dimensions` (optional, array): Dimensions to group by. Valid options:
  - `vendor` - Cloud provider (AWS, Azure, GCP)
  - `service` - Service name
  - `service_name` - Alternative service name
  - `enhanced_service_name` - Enhanced service name with details
  - `account_id` - Cloud account identifier
  - `region` - Geographic region
  - `date` - Date dimension for time-series
- `metrics` (optional, array): Metrics to retrieve. Valid options:
  - `total_amortized_cost` (default)
  - `amortized_cost`
  - `total_cost`
  - `cost`
- `filters` (optional, object): Filter conditions (e.g., `{"vendor": "AWS"}`)
- `view_name` (optional, string): View name to restrict data
- `granularity` (optional, string): Time granularity - `daily` or `monthly` (default: `monthly`)
- `export_format` (optional, string): Export format - `json` or `csv` (default: `json`)

**Example:**
```json
{
  "name": "get_amortized_costs",
  "arguments": {
    "start_date": "2025-10-01",
    "end_date": "2025-10-31",
    "dimensions": ["vendor", "region"],
    "granularity": "monthly",
    "export_format": "json"
  }
}
```

**Response (JSON):**
```json
{
  "success": true,
  "report_type": "amortized_costs",
  "start_date": "2025-10-01",
  "end_date": "2025-10-31",
  "dimensions": ["vendor", "region"],
  "granularity": "monthly",
  "total_records": 10,
  "data": [
    {
      "vendor": "Amazon",
      "region": "us-east-1",
      "total_amortized_cost": 1234.56
    }
  ],
  "export_format": "json"
}
```

**Response (CSV):**
```json
{
  "success": true,
  "report_type": "amortized_costs",
  "start_date": "2025-10-01",
  "end_date": "2025-10-31",
  "dimensions": ["vendor"],
  "granularity": "monthly",
  "csv_data": "vendor,total_amortized_cost\nAmazon,1234.56\n",
  "export_format": "csv",
  "export_path": "amortized_costs_2025-10-01_to_2025-10-31.csv"
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Invalid dimensions for amortized costs: ['cluster_name']. Valid dimensions: ['vendor', 'service', 'service_name', 'enhanced_service_name', 'account_id', 'region', 'date']",
  "status_code": null
}
```

## Dimension Validation

The `get_amortized_costs` tool validates dimensions before making API calls. Only dimensions that are known to work with the Cloudability amortized costs API are accepted:

- ✅ `vendor`
- ✅ `service`
- ✅ `service_name`
- ✅ `enhanced_service_name`
- ✅ `account_id`
- ✅ `region`
- ✅ `date`

- ❌ `cluster_name` (not supported for amortized costs)
- ❌ `namespace` (not supported for amortized costs)
- ❌ `pod_name` (not supported for amortized costs)
- ❌ `container_name` (not supported for amortized costs)

## Filter Operators

Filters support the following operators:

- `==` - Equals (e.g., `{"vendor": "AWS"}`)
- `!=` - Does not equal
- `>` - Greater than (e.g., `{"total_amortized_cost": ">100"}`)
- `<` - Less than
- `>=` - Greater than or equal to
- `<=` - Less than or equal to
- `=@` - Contains/wildcard (e.g., `{"region": "us-east-*"}` becomes `region=@us-east-`)
- `!=@` - Does not contain

## Date Format

All dates must be in **YYYY-MM-DD** format (ISO 8601).

Examples:
- `2025-10-01` - October 1, 2025
- `2025-11-19` - November 19, 2025

## Error Handling

All tools return standardized error responses:

```json
{
  "success": false,
  "error": "Error message here",
  "status_code": 422
}
```

Common error codes:
- `400` - Bad Request (invalid parameters)
- `401` - Unauthorized (authentication failed)
- `422` - Unprocessable Entity (API doesn't support the request)
- `500` - Internal Server Error

## Authentication

The server supports two authentication methods:

1. **Basic Authentication** (API Key)
   - Set `CLOUDABILITY_API_KEY` environment variable
   - Set `CLOUDABILITY_AUTH_TYPE=basic`

2. **Enhanced Access Administration** (Public/Private Key)
   - Set `CLOUDABILITY_PUBLIC_KEY` and `CLOUDABILITY_PRIVATE_KEY`
   - Set `CLOUDABILITY_AUTH_TYPE=opentoken`
   - Optionally set `CLOUDABILITY_ENVIRONMENT_ID`

## Regional Endpoints

The server supports regional endpoints:

- US: `https://api.cloudability.com/v3` (default)
- EU: `https://api-eu.cloudability.com/v3`
- APAC: `https://api-au.cloudability.com/v3`
- ME: `https://api-me.cloudability.com/v3`

Set `CLOUDABILITY_BASE_URL` to use a different region.

