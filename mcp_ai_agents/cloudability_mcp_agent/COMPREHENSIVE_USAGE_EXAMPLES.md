# Cloudability MCP Server - Comprehensive Usage Examples

This document provides comprehensive examples for all 20+ tools available in the Cloudability MCP Server, covering ~80% of Cloudability API features.

## Table of Contents

1. [Cost Reporting Tools](#cost-reporting-tools)
2. [Container/Kubernetes Tools](#containerkubernetes-tools)
3. [Budget Management Tools](#budget-management-tools)
4. [Forecast & Estimate Tools](#forecast--estimate-tools)
5. [Tag Explorer Tools](#tag-explorer-tools)
6. [Anomaly Detection Tools](#anomaly-detection-tools)
7. [Discovery Tools](#discovery-tools)
8. [Cost Allocation Tools](#cost-allocation-tools)
9. [Python Script Examples](#python-script-examples)

---

## Cost Reporting Tools

### 1. Get Cost Report by View

**Cursor Chat Examples:**
```
Get cost report for "AWS Cost Overview" view
```

```
Show me cost data for "Product-12284-OFT - self-managed Kubernetes" view for January 2024
```

```
Get cost report for "AWS Cost Overview" filtered by product_id K8s
```

**Python Script:**
```python
from src.main import CloudabilityMCPServer
import asyncio

async def example():
    server = CloudabilityMCPServer(api_key="your_key")
    result = await server.call_tool("get_cost_report_by_view", {
        "view_name": "AWS Cost Overview",
        "product_id": "K8s",
        "start_date": "2024-01-01",
        "end_date": "2024-01-31"
    })
    print(result)

asyncio.run(example())
```

### 2. Get Amortized Costs

**Cursor Chat Examples:**
```
Get amortized costs for all services in the last 30 days, export as CSV
```

```
Show me monthly amortized costs for AWS EC2 services grouped by account
```

```
Get amortized costs for Kubernetes namespace "default" filtered by product_id K8s, restricted to view "Product-12284-OFT - self-managed Kubernetes"
```

**Python Script:**
```python
result = await server.call_tool("get_amortized_costs", {
    "start_date": "2024-01-01",
    "end_date": "2024-01-31",
    "filters": {
        "namespace": "default",
        "product_id": "K8s"
    },
    "view_name": "Product-12284-OFT - self-managed Kubernetes",
    "dimensions": ["service", "account_id"],
    "granularity": "monthly",
    "export_format": "csv"
})
```

### 3. Export Cost Report

**Cursor Chat Examples:**
```
Export cost report for AWS EC2 in us-east-1 region for January 2024 as CSV
```

```
Create a custom cost report for all S3 costs grouped by account and region, export as JSON
```

**Python Script:**
```python
result = await server.call_tool("export_cost_report", {
    "start_date": "2024-01-01",
    "end_date": "2024-01-31",
    "filters": {
        "vendor": "AWS",
        "service": "EC2",
        "region": "us-east-1"
    },
    "dimensions": ["vendor", "service", "account_id", "region"],
    "metrics": ["total_amortized_cost", "usage_hours"],
    "export_format": "csv",
    "file_name": "aws_ec2_us_east_1_costs"
})
```

### 4. Get Cost Report with Filters

**Cursor Chat Examples:**
```
Get cost report for "AWS Cost Overview" view with filters for product_id K8s and vendor AWS
```

```
Show me cost data for "Kubernetes Costs" view grouped by namespace and service
```

**Python Script:**
```python
result = await server.call_tool("get_cost_report_with_filters", {
    "view_name": "AWS Cost Overview",
    "filters": {
        "product_id": "K8s",
        "vendor": "AWS"
    },
    "dimensions": ["namespace", "service"],
    "metrics": ["total_cost", "usage"],
    "start_date": "2024-01-01",
    "end_date": "2024-01-31"
})
```

---

## Container/Kubernetes Tools

### 5. Get Container Costs

**Cursor Chat Examples:**
```
Get container costs for production cluster grouped by namespace and pod
```

```
Show me Kubernetes costs for the default namespace in January 2024
```

```
Get container costs grouped by cluster, namespace, pod, and container for the last 30 days
```

**Python Script:**
```python
result = await server.call_tool("get_container_costs", {
    "start_date": "2024-01-01",
    "end_date": "2024-01-31",
    "filters": {
        "cluster_name": "prod-cluster",
        "namespace": "default"
    },
    "group_by": ["cluster", "namespace", "pod"],
    "metrics": ["total_cost", "cpu/reserved", "memory/reserved_rss"],
    "export_format": "csv"
})
```

### 6. Get Container Resource Usage

**Cursor Chat Examples:**
```
Get container resource usage for production cluster showing CPU and memory metrics
```

```
Show me daily resource usage trends for capacity planning in the default namespace
```

**Python Script:**
```python
result = await server.call_tool("get_container_resource_usage", {
    "start_date": "2024-01-01",
    "end_date": "2024-01-31",
    "filters": {
        "cluster_name": "prod-cluster",
        "namespace": "default"
    },
    "metrics": ["cpu/reserved", "memory/reserved_rss", "filesystem/usage", "network/tx"]
})
```

---

## Budget Management Tools

### 7. List Budgets

**Cursor Chat Examples:**
```
List all budgets in my Cloudability account
```

```
Show me all budgets and their current status
```

**Python Script:**
```python
result = await server.call_tool("list_budgets", {})
print(f"Total budgets: {result.get('total')}")
for budget in result.get('budgets', []):
    print(f"- {budget.get('name')}: {budget.get('id')}")
```

### 8. Get Budget

**Cursor Chat Examples:**
```
Get detailed information for budget "Q1 2024 Budget"
```

```
Show me budget details for budget ID budget-123
```

**Python Script:**
```python
result = await server.call_tool("get_budget", {
    "budget_id": "budget-123"
})
print(result.get('budget'))
```

### 9. Create Budget

**Cursor Chat Examples:**
```
Create a quarterly budget for Q1 2024 with thresholds: January $50k, February $55k, March $60k
```

**Python Script:**
```python
result = await server.call_tool("create_budget", {
    "name": "Q1 2024 Budget",
    "basis": "adjusted",
    "view_id": "0",
    "months": [
        {"month": "2024-01", "threshold": 50000},
        {"month": "2024-02", "threshold": 55000},
        {"month": "2024-03", "threshold": 60000}
    ]
})
print(f"Created budget: {result.get('budget', {}).get('id')}")
```

### 10. Update Budget

**Cursor Chat Examples:**
```
Update budget budget-123 to set January threshold to $45k and February to $50k
```

**Python Script:**
```python
result = await server.call_tool("update_budget", {
    "budget_id": "budget-123",
    "months": [
        {"month": "2024-01", "threshold": 45000},
        {"month": "2024-02", "threshold": 50000}
    ]
})
```

---

## Forecast & Estimate Tools

### 11. Get Spending Estimate

**Cursor Chat Examples:**
```
Get current month spending estimate
```

```
Show me spending estimate for view "AWS Cost Overview" using amortized basis
```

**Python Script:**
```python
result = await server.call_tool("get_spending_estimate", {
    "view_id": "0",  # All views
    "basis": "amortized"
})
print(f"Current month estimate: ${result.get('estimate', {}).get('amount', 0):,.2f}")
```

### 12. Get Spending Forecast

**Cursor Chat Examples:**
```
Generate 12-month spending forecast based on 6 months of history
```

```
Get spending forecast for the next 12 months using cash basis, excluding one-time charges
```

**Python Script:**
```python
result = await server.call_tool("get_spending_forecast", {
    "view_id": "0",
    "basis": "cash",
    "months_back": 6,
    "months_forward": 12,
    "use_current_estimate": True,
    "remove_one_time_charges": True
})
print(f"Forecast: {result.get('forecast')}")
```

---

## Tag Explorer Tools

### 13. List Available Tags

**Cursor Chat Examples:**
```
What tags are available in my Cloudability account?
```

```
List all available tag keys
```

**Python Script:**
```python
result = await server.call_tool("list_available_tags", {
    "limit": 100
})
print(f"Available tags: {result.get('tag_keys')}")
```

### 14. Explore Tags

**Cursor Chat Examples:**
```
What are the costs by Environment tag for Production environment?
```

```
Show me costs for all values of the Team tag
```

```
Get costs by Project tag for AWS services only
```

**Python Script:**
```python
# Explore specific tag value
result = await server.call_tool("explore_tags", {
    "tag_key": "Environment",
    "tag_value": "Production",
    "start_date": "2024-01-01",
    "end_date": "2024-01-31",
    "additional_filters": {
        "vendor": "AWS"
    },
    "export_format": "csv"
})

# Explore all values of a tag
result = await server.call_tool("explore_tags", {
    "tag_key": "Team",
    "start_date": "2024-01-01",
    "end_date": "2024-01-31",
    "export_format": "json"
})
```

---

## Anomaly Detection Tools

### 15. Get Anomaly Detection

**Cursor Chat Examples:**
```
Find cost anomalies in the last 30 days
```

```
Show me high-severity cost anomalies for AWS
```

```
Detect anomalies with more than 25% cost change in January
```

```
Find anomalies for account 123456789 with at least 15% change
```

**Python Script:**
```python
result = await server.call_tool("get_anomaly_detection", {
    "start_date": "2024-01-01",
    "end_date": "2024-01-31",
    "severity": "high",
    "filters": {
        "vendor": "AWS",
        "account_id": "123456789"
    },
    "min_cost_change_percent": 20.0,
    "export_format": "json"
})
print(f"Found {result.get('total_anomalies')} anomalies")
```

---

## Discovery Tools

### 16. List Views

**Cursor Chat Examples:**
```
List all available views in my Cloudability account
```

```
Show me all dashboard views
```

**Python Script:**
```python
result = await server.call_tool("list_views", {
    "limit": 100
})
for view in result.get('views', []):
    print(f"- {view.get('name')} (ID: {view.get('id')})")
```

### 17. Get Available Measures

**Cursor Chat Examples:**
```
What dimensions and metrics are available for cost reports?
```

```
Discover available measures for building custom reports
```

**Python Script:**
```python
result = await server.call_tool("get_available_measures", {})
print("Available dimensions:", result.get('measures', {}).get('dimensions', []))
print("Available metrics:", result.get('measures', {}).get('metrics', []))
```

### 18. Get Filter Operators

**Cursor Chat Examples:**
```
What filter operators can I use in cost reports?
```

```
Show me available filter operators
```

**Python Script:**
```python
result = await server.call_tool("get_filter_operators", {})
print("Available operators:", result.get('operators'))
```

---

## Cost Allocation Tools

### 19. Analyze Container Cost Allocation

**Cursor Chat Examples:**
```
Analyze container cost allocation by namespace for production cluster
```

```
Get cost allocation by team labels and namespace
```

```
Show me service-level cost breakdown for specific namespace
```

**Python Script:**
```python
# Namespace-based allocation
result = await server.call_tool("analyze_container_cost_allocation", {
    "start_date": "2024-01-01",
    "end_date": "2024-01-31",
    "group": ["namespace"],
    "metrics": ["cpu/reserved", "memory/reserved_rss"],
    "filters": ["cluster==your-cluster-uuid"]
})

# Team-based allocation using labels
result = await server.call_tool("analyze_container_cost_allocation", {
    "start_date": "2024-01-01",
    "end_date": "2024-01-31",
    "group": ["cldy:labels:team", "namespace"],
    "metrics": ["cpu/reserved", "memory/reserved_rss", "network/tx"],
    "filters": ["cluster==your-cluster-uuid"],
    "cost_type": "adjusted_amortized_cost"
})

# Service-level breakdown
result = await server.call_tool("analyze_container_cost_allocation", {
    "start_date": "2024-01-01",
    "end_date": "2024-01-31",
    "group": ["service", "deployment"],
    "metrics": ["cpu/reserved", "memory/reserved_rss"],
    "filters": ["namespace==production", "cluster==your-cluster-uuid"]
})
```

---

## Python Script Examples

### Complete Example: Comprehensive Cost Analysis

```python
#!/usr/bin/env python3
"""
Comprehensive Cloudability Cost Analysis Script
Demonstrates multiple tools working together
"""

import asyncio
from src.main import CloudabilityMCPServer
from src.config import Config

async def comprehensive_analysis():
    """Run comprehensive cost analysis"""
    
    # Initialize server
    server = CloudabilityMCPServer(
        api_key=Config.API_KEY,
        base_url=Config.BASE_URL
    )
    
    print("=" * 80)
    print("Cloudability Comprehensive Cost Analysis")
    print("=" * 80)
    print()
    
    # 1. List all views
    print("1. Listing available views...")
    views_result = await server.call_tool("list_views", {"limit": 10})
    if views_result.get("success"):
        print(f"   Found {views_result.get('total_views')} views")
        for view in views_result.get('views', [])[:5]:
            print(f"   - {view.get('name')}")
    print()
    
    # 2. Get amortized costs
    print("2. Getting amortized costs for all services...")
    amortized_result = await server.call_tool("get_amortized_costs", {
        "start_date": "2024-01-01",
        "end_date": "2024-01-31",
        "dimensions": ["service", "vendor"],
        "granularity": "monthly",
        "export_format": "json"
    })
    if amortized_result.get("success"):
        print(f"   Found {amortized_result.get('total_records')} records")
    print()
    
    # 3. Get container costs
    print("3. Getting container costs...")
    container_result = await server.call_tool("get_container_costs", {
        "start_date": "2024-01-01",
        "end_date": "2024-01-31",
        "group_by": ["cluster", "namespace"],
        "export_format": "csv"
    })
    if container_result.get("success"):
        print(f"   Export path: {container_result.get('export_path')}")
    print()
    
    # 4. List budgets
    print("4. Listing budgets...")
    budgets_result = await server.call_tool("list_budgets", {})
    if budgets_result.get("success"):
        print(f"   Found {budgets_result.get('total')} budgets")
    print()
    
    # 5. Get spending forecast
    print("5. Getting spending forecast...")
    forecast_result = await server.call_tool("get_spending_forecast", {
        "months_back": 6,
        "months_forward": 12
    })
    if forecast_result.get("success"):
        print("   Forecast generated successfully")
    print()
    
    # 6. Detect anomalies
    print("6. Detecting cost anomalies...")
    anomaly_result = await server.call_tool("get_anomaly_detection", {
        "start_date": "2024-01-01",
        "end_date": "2024-01-31",
        "severity": "high",
        "min_cost_change_percent": 20.0
    })
    if anomaly_result.get("success"):
        print(f"   Found {anomaly_result.get('total_anomalies')} anomalies")
    print()
    
    # 7. Explore tags
    print("7. Exploring costs by tags...")
    tags_result = await server.call_tool("list_available_tags", {})
    if tags_result.get("success"):
        tag_keys = tags_result.get('tag_keys', [])
        if tag_keys:
            explore_result = await server.call_tool("explore_tags", {
                "tag_key": tag_keys[0],
                "start_date": "2024-01-01",
                "end_date": "2024-01-31"
            })
            if explore_result.get("success"):
                print(f"   Explored tag: {tag_keys[0]}")
    print()
    
    print("=" * 80)
    print("Analysis Complete!")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(comprehensive_analysis())
```

### Example: Budget Management Workflow

```python
async def budget_management_workflow():
    """Complete budget management workflow"""
    
    server = CloudabilityMCPServer(api_key=Config.API_KEY)
    
    # 1. List existing budgets
    budgets = await server.call_tool("list_budgets", {})
    print("Existing budgets:", budgets.get('total', 0))
    
    # 2. Create new budget
    new_budget = await server.call_tool("create_budget", {
        "name": "Q1 2024 Budget",
        "basis": "adjusted",
        "view_id": "0",
        "months": [
            {"month": "2024-01", "threshold": 50000},
            {"month": "2024-02", "threshold": 55000},
            {"month": "2024-03", "threshold": 60000}
        ]
    })
    
    if new_budget.get("success"):
        budget_id = new_budget.get('budget', {}).get('id')
        print(f"Created budget: {budget_id}")
        
        # 3. Get budget details
        budget_details = await server.call_tool("get_budget", {
            "budget_id": budget_id
        })
        print("Budget details:", budget_details.get('budget'))
        
        # 4. Update budget
        updated = await server.call_tool("update_budget", {
            "budget_id": budget_id,
            "months": [
                {"month": "2024-01", "threshold": 45000},
                {"month": "2024-02", "threshold": 50000}
            ]
        })
        print("Budget updated:", updated.get("success"))
```

### Example: Container Cost Analysis

```python
async def container_cost_analysis():
    """Comprehensive container cost analysis"""
    
    server = CloudabilityMCPServer(api_key=Config.API_KEY)
    
    # 1. Get container costs by namespace
    namespace_costs = await server.call_tool("get_container_costs", {
        "start_date": "2024-01-01",
        "end_date": "2024-01-31",
        "group_by": ["namespace"],
        "export_format": "csv"
    })
    
    # 2. Get resource usage
    resource_usage = await server.call_tool("get_container_resource_usage", {
        "start_date": "2024-01-01",
        "end_date": "2024-01-31",
        "filters": {
            "cluster_name": "prod-cluster",
            "namespace": "default"
        },
        "metrics": ["cpu/reserved", "memory/reserved_rss", "filesystem/usage"]
    })
    
    # 3. Analyze cost allocation
    allocation = await server.call_tool("analyze_container_cost_allocation", {
        "start_date": "2024-01-01",
        "end_date": "2024-01-31",
        "group": ["namespace", "service"],
        "metrics": ["cpu/reserved", "memory/reserved_rss"],
        "filters": ["cluster==prod-cluster-uuid"]
    })
    
    print("Container analysis complete!")
```

---

## Tool Summary

### Total Tools: 20+

1. **Cost Reporting** (4 tools)
   - get_cost_report_by_view
   - get_cost_report_with_filters
   - get_amortized_costs
   - export_cost_report

2. **Container/Kubernetes** (3 tools)
   - get_container_costs
   - get_container_resource_usage
   - analyze_container_cost_allocation

3. **Budget Management** (4 tools)
   - list_budgets
   - get_budget
   - create_budget
   - update_budget

4. **Forecasts & Estimates** (2 tools)
   - get_spending_estimate
   - get_spending_forecast

5. **Tag Explorer** (2 tools)
   - list_available_tags
   - explore_tags

6. **Anomaly Detection** (1 tool)
   - get_anomaly_detection

7. **Discovery** (4 tools)
   - list_views
   - get_available_measures
   - get_filter_operators
   - (get_cost_report_with_filters - also in cost reporting)

---

## Best Practices

1. **Always list views first** before querying specific views
2. **Use appropriate date ranges** for accurate analysis
3. **Export large datasets as CSV** for better performance
4. **Combine filters** to narrow down results
5. **Use monthly granularity** for trend analysis
6. **Check available measures** before building custom reports
7. **Monitor budgets regularly** using list_budgets
8. **Set up anomaly detection** for proactive cost management

---

## Next Steps

- See `ARCHITECTURE.md` for framework details
- See `FRAMEWORK_GUIDE.md` for adding new tools
- See `README.md` for setup and configuration

