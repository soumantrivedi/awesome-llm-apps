# Cloudability MCP Server - API Fixes Summary

## Overview

This document summarizes the comprehensive fixes applied to align the Cloudability MCP Server with the official IBM Cloudability API v3 documentation.

## Key Fixes Applied

### 1. API Parameter Names
**Issue:** Code was using `start`/`end` instead of `start_date`/`end_date`  
**Fix:** Updated all API calls to use `start_date` and `end_date` as per documentation  
**Files Changed:**
- `src/api_client.py` - `get_amortized_costs()`, `export_cost_report()`
- `src/api_client_extended.py` - `get_container_costs()`, `get_container_resource_usage()`

### 2. Filter Parameter Format
**Issue:** Using `filter` (singular) instead of `filters` (plural)  
**Fix:** Changed to `filters` parameter as per API documentation  
**Files Changed:**
- `src/api_client.py`
- `src/api_client_extended.py`

### 3. Filter String Building
**Issue:** Limited filter support (only equality)  
**Fix:** Enhanced `build_filter_string()` to support:
- Wildcards: `namespace=@ici` (for patterns like `ici*`)
- IN operator: `region[]==us-east-1,us-west-2`
- Comparison operators: `cost>100`, `cost<=500`
- Contains operator: `region=@us-east-`  
**Files Changed:**
- `src/utils.py` - `build_filter_string()`

### 4. Filters with Views
**Issue:** Code was removing filters when a view was specified  
**Fix:** API supports filters with views - they can be combined  
**Files Changed:**
- `src/api_client.py` - `get_amortized_costs()`
- `src/api_validator.py` - `validate_view_parameters()`

### 5. Date Parameters with Views
**Issue:** Views have their own date ranges and don't accept date parameters  
**Fix:** When a view is specified, date parameters are omitted (view's date range is used)  
**Files Changed:**
- `src/api_client.py` - `get_amortized_costs()`

### 6. Metric Names
**Issue:** Using incorrect metric names  
**Fix:** Updated to use `total_amortized_cost` and `total_cost` as per documentation  
**Files Changed:**
- `src/api_client.py` - Default metrics updated
- `src/api_client_extended.py` - Default metrics updated

### 7. Default Dimensions
**Issue:** Using `service` as default dimension (not always valid)  
**Fix:** Changed default to `vendor` (more universal)  
**Files Changed:**
- `src/api_client.py` - `get_amortized_costs()`

### 8. Error Handling
**Issue:** Limited error handling and retry logic  
**Fix:** Enhanced error handling with:
- Automatic fallback to alternative parameter formats
- Special handling for views (no date parameters)
- Better error messages and logging  
**Files Changed:**
- `src/api_client.py` - Error handling in `get_amortized_costs()` and `export_cost_report()`

## API Endpoint Updates

### `/reporting/cost/run`
**Parameters:**
- `start_date` / `end_date` (not `start`/`end`)
- `filters` (not `filter`)
- `dimensions` - comma-separated list
- `metrics` - metric name (e.g., `total_amortized_cost`)
- `view` - view ID (optional)
- `granularity` - "daily" or "monthly" (optional)

**Notes:**
- When `view` is specified, `start_date`/`end_date` should be omitted
- `filters` can be combined with `view`
- Filters support wildcards using `@` operator (e.g., `namespace=@ici`)

## Testing

Run tests using the Makefile:

```bash
make test              # Run all tests
make test-working      # Run working combinations
make test-comprehensive # Run comprehensive tests
make test-api          # Run API combination tests
```

## Example Usage

### Get Amortized Costs with View and Filters

```python
from src.main import CloudabilityMCPServer
import asyncio

async def example():
    server = CloudabilityMCPServer(api_key="your_key")
    result = await server.call_tool("get_amortized_costs", {
        "view_name": "Product-12284-OFT - self-managed Kubernetes",
        "filters": {
            "namespace": "ici*",  # Wildcard converted to namespace=@ici
            "product_id": "K8s"
        },
        "dimensions": ["vendor"],
        "granularity": "monthly",
        "export_format": "json"
    })
    print(result)

asyncio.run(example())
```

**Note:** When a view is specified, date parameters are automatically omitted as views have their own date ranges.

## Migration Notes

If you have existing code using the old parameter names:

1. **Date Parameters:** Change `start`/`end` to `start_date`/`end_date`
2. **Filter Parameter:** Change `filter` to `filters`
3. **Views with Dates:** Remove date parameters when using views
4. **Wildcard Filters:** Use `*` in filter values (e.g., `"namespace": "ici*"`) - automatically converted to `namespace=@ici`

## Known Limitations

1. **Views and Dates:** Views have their own date ranges and don't accept date parameters. The view's configured date range will be used.
2. **Dimension Validation:** Some dimension/metric combinations may not be valid for all views. The API will return 422 errors for invalid combinations.
3. **Filter Operators:** Not all filter operators may be supported for all dimensions. Check API documentation for specific dimension support.

## References

- [Cloudability API Documentation](https://www.ibm.com/docs/en/cloudability-commercial/cloudability-premium/saas?topic=api-cost-reporting-end-point)
- [Cost Reporting Endpoint](https://www.ibm.com/docs/en/cloudability-commercial/cloudability-premium/saas?topic=api-cost-reporting-end-point)
- [Containers Endpoints](https://www.ibm.com/docs/en/cloudability-commercial/cloudability-premium/saas?topic=api-containers-end-points)

