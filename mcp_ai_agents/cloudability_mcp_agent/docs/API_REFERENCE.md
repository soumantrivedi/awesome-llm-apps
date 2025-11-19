# Cloudability API v3 Reference

This document provides a comprehensive reference for the Cloudability API v3 based on the official IBM documentation.

**Source**: [IBM Cloudability API v3 Documentation](https://www.ibm.com/docs/en/cloudability-commercial/cloudability-essentials/saas?topic=api-getting-started-cloudability-v3)

## Table of Contents

1. [Authentication](#authentication)
2. [API Endpoints](#api-endpoints)
3. [Dimensions](#dimensions)
4. [Metrics](#metrics)
5. [Filter Operators](#filter-operators)
6. [Request Parameters](#request-parameters)
7. [Response Format](#response-format)
8. [Examples](#examples)

## Authentication

Cloudability API v3 supports multiple authentication methods:

### 1. Cloudability API Keys (Basic Auth) - Legacy

```bash
curl -u 'Your_API_Key:' https://api.cloudability.com/v3/budgets
```

The API key is used as the username with an empty password in Basic Authentication.

**Get your API key:** [Cloudability Preferences](https://app.apptio.com/cloudability#/settings/preferences) → Enable API

### 2. Enhanced Access Administration (Public/Private Key Pair) - Recommended

This is the modern, more secure authentication method using public and private key pairs.

**Step 1: Authenticate to get OpenToken**

```bash
curl -X POST https://frontdoor.apptio.com/service/apikeylogin \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
    "keyAccess": "your_public_key",
    "keySecret": "your_private_key"
  }'
```

**Step 2: Use OpenToken in subsequent requests**

```bash
curl -H "apptio-opentoken: [token_from_step_1]" \
     -H "apptio-environmentid: [env_id]" \
     https://api.cloudability.com/v3/budgets
```

**Regional Frontdoor URLs:**
- US: `https://frontdoor.apptio.com`
- EU: `https://frontdoor-eu.apptio.com`
- APAC: `https://frontdoor-au.apptio.com`

### 3. Direct OpenToken (Bearer)

If you already have an OpenToken:

```bash
curl -H "apptio-opentoken: [token]" \
     -H "apptio-environmentid: [env_id]" \
     https://api.cloudability.com/v3/budgets
```

**Note**: For EU, APAC, or ME regions, use:
- `api-eu.cloudability.com` (Europe)
- `api-au.cloudability.com` (Asia Pacific)
- `api-me.cloudability.com` (Middle East)

**See Also:** [Authentication Guide](AUTHENTICATION.md) for detailed setup instructions.

## API Endpoints

### Cost Reporting

**Endpoint**: `GET /v3/reporting/cost/run`

Generate cost reports with flexible filtering and grouping.

**Parameters**:
- `start_date` (required): Start date in YYYY-MM-DD format
- `end_date` (required): End date in YYYY-MM-DD format
- `dimensions` (optional): Comma-separated list of dimensions to group by
- `metrics` (optional): Comma-separated list of metrics to retrieve
- `filters` (optional): Filter conditions (can be repeated multiple times)
- `granularity` (optional): `daily` or `monthly` (default: `monthly`)
- `view_name` (optional): Restrict data to a specific view

**Example**:
```bash
curl -u 'API_KEY:' \
  'https://api.cloudability.com/v3/reporting/cost/run?start_date=2025-10-01&end_date=2025-10-31&dimensions=vendor,region,enhanced_service_name&metrics=total_amortized_cost&filters=total_amortized_cost>100&filters=region=@us-east-'
```

## Dimensions

Dimensions are used to group and categorize cost data. The following dimensions are available in Cloudability API v3:

### Core Dimensions

| Dimension | Description | Example Values |
|-----------|-------------|----------------|
| `vendor` | Cloud provider | AWS, Azure, GCP |
| `service` | Service name | AmazonEC2, Compute Engine |
| `service_name` | Alternative service name | EC2-Instance |
| `enhanced_service_name` | Enhanced service name with details | EC2-Instance-Hours |
| `account_id` | Cloud account identifier | 123456789012 |
| `region` | Geographic region | us-east-1, eu-west-1 |
| `date` | Date dimension for time-series | 2025-10-01 |

### Resource-Level Dimensions

| Dimension | Description | Example Values |
|-----------|-------------|----------------|
| `resource_identifier` | Unique resource ID | i-1234567890abcdef0 |
| `product_id` | Product/service identifier | K8s, EC2 |
| `usage_type` | Usage type classification | BoxUsage, DataTransfer-In |
| `operation` | Operation type | RunInstances, StartInstances |
| `availability_zone` | Availability zone | us-east-1a |

### Kubernetes/Container Dimensions

| Dimension | Description | Example Values |
|-----------|-------------|----------------|
| `cluster_name` | Kubernetes cluster name | prod-cluster, dev-cluster |
| `namespace` | Kubernetes namespace | default, kube-system |
| `pod_name` | Kubernetes pod name | my-app-pod-123 |
| `container_name` | Container name | nginx, app-container |

### Cost Allocation Dimensions

| Dimension | Description | Example Values |
|-----------|-------------|----------------|
| `lease_type` | Lease type | On-Demand, Reserved, Spot |
| `transaction_type` | Transaction type | Purchase, Usage, Refund |
| `usage_family` | Usage family classification | Compute Instance, Storage |
| `billing_period` | Billing period | 2025-10 |
| `cost_category` | Cost category | Compute, Storage, Network |

## Metrics

Metrics represent the values you want to retrieve from the API.

### Cost Metrics

| Metric | Description | Use Case |
|--------|-------------|----------|
| `total_amortized_cost` | **Recommended** - Total amortized cost | Standard cost reporting |
| `amortized_cost` | Amortized cost (single value) | Alternative amortized cost |
| `total_cost` | Total cost (unamortized) | Raw cost reporting |
| `cost` | Basic cost | Simple cost queries |
| `unblended_cost` | Unblended cost (raw) | Direct cloud provider costs |
| `blended_cost` | Blended cost | Organization-wide cost allocation |

### Usage Metrics

| Metric | Description | Use Case |
|--------|-------------|----------|
| `usage` | General usage | Usage tracking |
| `usage_quantity` | Usage quantity | Resource consumption |
| `usage_hours` | Usage hours | Time-based usage |
| `usage_amount` | Usage amount | Quantity-based usage |

**Recommendation**: Use `total_amortized_cost` for most cost reporting scenarios as it provides the most accurate cost allocation.

## Filter Operators

Filter operators define how filter conditions are evaluated. Multiple filters can be applied using multiple `filters=` query parameters.

### Supported Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `==` | Equals | `service==AmazonEC2` |
| `!=` | Does not equal | `vendor!=Azure` |
| `>` | Greater than | `total_amortized_cost>100` |
| `<` | Less than | `total_amortized_cost<50` |
| `>=` | Greater than or equal to | `total_amortized_cost>=100` |
| `<=` | Less than or equal to | `total_amortized_cost<=1000` |
| `=@` | Contains (wildcard matching) | `region=@us-east-` |
| `!=@` | Does not contain | `service!=@EC2` |

### Filter Syntax

```
dimension operator value
```

**Examples**:
- `service==AmazonEC2` - Service equals AmazonEC2
- `region=@us-east-` - Region contains "us-east-" (wildcard)
- `total_amortized_cost>100` - Cost greater than 100
- `namespace=@ici` - Namespace contains "ici" (wildcard)

### Multiple Filters

You can apply multiple filters in two ways:

1. **Multiple query parameters** (recommended):
   ```
   filters=service==AmazonEC2&filters=region=@us-east-
   ```

2. **Comma-separated** (single parameter):
   ```
   filters=service==AmazonEC2,region=@us-east-
   ```

## Request Parameters

### Common Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `start_date` | string | Yes* | Start date (YYYY-MM-DD) |
| `end_date` | string | Yes* | End date (YYYY-MM-DD) |
| `dimensions` | string | No | Comma-separated dimensions |
| `metrics` | string | No | Comma-separated metrics |
| `filters` | string | No | Filter conditions (can repeat) |
| `granularity` | string | No | `daily` or `monthly` |
| `view_name` | string | No | View name to restrict data |
| `limit` | integer | No | Maximum records (default: 50) |
| `offset` | integer | No | Pagination offset (default: 0) |

*Required for cost reporting endpoints, optional when using views with date restrictions.

### Date Format

All dates must be in **YYYY-MM-DD** format (ISO 8601).

**Examples**:
- `2025-10-01` - October 1, 2025
- `2025-11-19` - November 19, 2025

## Response Format

All successful API responses follow this structure:

```json
{
  "result": {} or [],
  "meta": {}
}
```

- `result`: Contains the actual data (object or array)
- `meta`: Contains ancillary information (pagination, etc.)

### Error Responses

Error responses include status codes and error messages:

```json
{
  "error": "Error message",
  "status_code": 422
}
```

## Examples

### Example 1: Basic Cost Report

Get total amortized costs by vendor and region for October 2025:

```bash
curl -u 'API_KEY:' \
  'https://api.cloudability.com/v3/reporting/cost/run?start_date=2025-10-01&end_date=2025-10-31&dimensions=vendor,region&metrics=total_amortized_cost'
```

### Example 2: Filtered Cost Report

Get costs for EC2 services in US East regions with cost > $100:

```bash
curl -u 'API_KEY:' \
  'https://api.cloudability.com/v3/reporting/cost/run?start_date=2025-10-01&end_date=2025-10-31&dimensions=vendor,region,enhanced_service_name&metrics=total_amortized_cost&filters=service==AmazonEC2&filters=region=@us-east-&filters=total_amortized_cost>100'
```

### Example 3: Kubernetes Namespace Costs

Get costs for Kubernetes namespaces matching "ici*" with product_id K8s:

```bash
curl -u 'API_KEY:' \
  'https://api.cloudability.com/v3/reporting/cost/run?start_date=2025-10-01&end_date=2025-10-31&dimensions=namespace,vendor&metrics=total_amortized_cost&filters=namespace=@ici&filters=product_id==K8s'
```

### Example 4: Custom Dimensions

Get costs grouped by lease type, enhanced service name, transaction type, and usage family:

```bash
curl -u 'API_KEY:' \
  'https://api.cloudability.com/v3/reporting/cost/run?start_date=2025-10-01&end_date=2025-10-31&dimensions=lease_type&dimensions=enhanced_service_name&dimensions=transaction_type&dimensions=usage_family&metrics=total_amortized_cost'
```

### Example 5: View-Restricted Report

Get costs for a specific view with additional filters:

```bash
curl -u 'API_KEY:' \
  'https://api.cloudability.com/v3/reporting/cost/run?view_name=Product-12284-OFT%20-%20self-managed%20Kubernetes&start_date=2025-10-01&end_date=2025-10-31&dimensions=vendor&metrics=total_amortized_cost&filters=namespace=@ici&filters=product_id==K8s'
```

## Best Practices

1. **Use `total_amortized_cost`** for accurate cost allocation
2. **Use `vendor` as default dimension** when no specific dimension is needed
3. **Use `=@` operator** for wildcard/pattern matching (e.g., `namespace=@ici`)
4. **Use multiple `filters=` parameters** instead of comma-separated filters for clarity
5. **Always specify date ranges** even when using views
6. **Use `daily` granularity** for detailed time-series analysis
7. **Use `monthly` granularity** for high-level summaries

## Additional Resources

- [IBM Cloudability API v3 Getting Started](https://www.ibm.com/docs/en/cloudability-commercial/cloudability-essentials/saas?topic=api-getting-started-cloudability-v3)
- [Cloudability Community](https://community.ibm.com/community/user/cloudability)

