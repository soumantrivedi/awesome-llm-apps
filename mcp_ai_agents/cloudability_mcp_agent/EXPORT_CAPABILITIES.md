# Cloudability MCP Server - CSV & JSON Export Capabilities

## Overview

All reporting tools in the Cloudability MCP Server support both **CSV** and **JSON** export formats. This document provides a complete guide to using export capabilities.

## ✅ Tools with Export Support

### 9 Tools Support CSV/JSON Export

1. **`get_cost_report_by_view`** - Cost reports by view
2. **`get_cost_report_with_filters`** - Advanced filtered reports
3. **`get_amortized_costs`** - Amortized cost analysis
4. **`export_cost_report`** - Custom cost reports
5. **`get_container_costs`** - Container/Kubernetes costs
6. **`get_container_resource_usage`** - Container resource metrics
7. **`analyze_container_cost_allocation`** - Cost allocation analysis
8. **`explore_tags`** - Tag-based cost exploration
9. **`get_anomaly_detection`** - Anomaly detection results

## 📋 Export Format Parameter

All reporting tools accept an `export_format` parameter:

```json
{
  "export_format": "csv"  // or "json"
}
```

**Default**: `"json"` (if not specified)

## 💡 Usage Examples

### CSV Export Examples

#### 1. Get Amortized Costs as CSV

**Cursor Chat:**
```
Get amortized costs for all services in the last 30 days, export as CSV
```

**Python:**
```python
result = await server.call_tool("get_amortized_costs", {
    "start_date": "2024-01-01",
    "end_date": "2024-01-31",
    "dimensions": ["service"],
    "export_format": "csv"
})
# Result includes:
# - csv_data: CSV string
# - export_path: Path to saved CSV file
```

#### 2. Export Container Costs as CSV

**Cursor Chat:**
```
Get container costs for production cluster grouped by namespace, export as CSV
```

**Python:**
```python
result = await server.call_tool("get_container_costs", {
    "start_date": "2024-01-01",
    "end_date": "2024-01-31",
    "filters": {"cluster_name": "prod-cluster"},
    "group_by": ["namespace"],
    "export_format": "csv",
    "file_name": "prod_container_costs"
})
```

#### 3. Export Cost Report by View as CSV

**Cursor Chat:**
```
Get cost report for "AWS Cost Overview" view, export as CSV
```

**Python:**
```python
result = await server.call_tool("get_cost_report_by_view", {
    "view_name": "AWS Cost Overview",
    "start_date": "2024-01-01",
    "end_date": "2024-01-31",
    "export_format": "csv"
})
```

### JSON Export Examples

#### 1. Get Amortized Costs as JSON

**Cursor Chat:**
```
Get amortized costs for all services in the last 30 days as JSON
```

**Python:**
```python
result = await server.call_tool("get_amortized_costs", {
    "start_date": "2024-01-01",
    "end_date": "2024-01-31",
    "dimensions": ["service", "vendor"],
    "export_format": "json"
})
# Result includes:
# - data: JSON array of records
```

#### 2. Export with Custom File Name

**Python:**
```python
result = await server.call_tool("export_cost_report", {
    "start_date": "2024-01-01",
    "end_date": "2024-01-31",
    "filters": {"vendor": "AWS", "service": "EC2"},
    "dimensions": ["account_id", "region"],
    "export_format": "csv",
    "file_name": "aws_ec2_costs_january"
})
# Creates: aws_ec2_costs_january.csv
```

## 📊 Response Format

### CSV Export Response

```json
{
  "success": true,
  "data": [...],  // Original data
  "csv_data": "service,vendor,cost\nEC2,AWS,1000.00\n...",  // CSV string
  "export_format": "csv",
  "export_path": "get_amortized_costs_2024-01-01_to_2024-01-31.csv",
  "total_records": 150,
  "start_date": "2024-01-01",
  "end_date": "2024-01-31"
}
```

### JSON Export Response

```json
{
  "success": true,
  "data": [
    {
      "service": "EC2",
      "vendor": "AWS",
      "cost": 1000.00
    }
  ],
  "export_format": "json",
  "total_records": 150,
  "start_date": "2024-01-01",
  "end_date": "2024-01-31"
}
```

### JSON Export with File Name

```json
{
  "success": true,
  "data": [...],
  "export_format": "json",
  "export_path": "my_report.json",
  "total_records": 150
}
```

## 🔧 Implementation Details

### CSV Generation

- **Header Row**: Automatically included with column names
- **Encoding**: UTF-8
- **Delimiter**: Comma (`,`)
- **Quoting**: Handles special characters and commas in values

### File Naming

**Default CSV File Names:**
- Format: `{tool_name}_{start_date}_to_{end_date}.csv`
- Example: `get_amortized_costs_2024-01-01_to_2024-01-31.csv`

**Custom File Names:**
- Use `file_name` parameter (without extension)
- Example: `file_name: "my_report"` → `my_report.csv`

### File Location

- Files are saved in the **current working directory**
- Path is returned in `export_path` field
- Files are automatically gitignored (see `.gitignore`)

## 📝 Complete Tool Reference

### Cost Reporting Tools

| Tool | CSV | JSON | Notes |
|------|-----|-----|-------|
| `get_cost_report_by_view` | ✅ | ✅ | Default: JSON |
| `get_cost_report_with_filters` | ✅ | ✅ | Default: JSON |
| `get_amortized_costs` | ✅ | ✅ | Default: JSON |
| `export_cost_report` | ✅ | ✅ | Default: JSON |

### Container Tools

| Tool | CSV | JSON | Notes |
|------|-----|-----|-------|
| `get_container_costs` | ✅ | ✅ | Default: JSON |
| `get_container_resource_usage` | ✅ | ✅ | Default: JSON |
| `analyze_container_cost_allocation` | ✅ | ✅ | Default: JSON |

### Tag & Anomaly Tools

| Tool | CSV | JSON | Notes |
|------|-----|-----|-------|
| `explore_tags` | ✅ | ✅ | Default: JSON |
| `get_anomaly_detection` | ✅ | ✅ | Default: JSON |

## 🎯 Best Practices

### When to Use CSV

- ✅ Large datasets (>1000 records)
- ✅ Spreadsheet analysis (Excel, Google Sheets)
- ✅ Data processing pipelines
- ✅ Sharing with non-technical users

### When to Use JSON

- ✅ API integrations
- ✅ Programmatic processing
- ✅ Nested/complex data structures
- ✅ Small to medium datasets

### Performance Tips

1. **Use CSV for large exports** - More efficient for large datasets
2. **Use JSON for nested data** - Better for complex structures
3. **Specify file_name** - Avoids auto-generated names
4. **Check export_path** - Verify file was created successfully

## 🔍 Troubleshooting

### Issue: CSV file not created

**Check:**
- `export_format` is set to `"csv"`
- `result["success"]` is `true`
- `result["csv_data"]` is not empty
- File permissions in current directory

### Issue: JSON export not working

**Check:**
- `export_format` is set to `"json"` or omitted (default)
- `result["success"]` is `true`
- `result["data"]` contains records

### Issue: File name conflicts

**Solution:**
- Use `file_name` parameter for custom names
- Add timestamp to file names if needed
- Check existing files before export

## 📚 Related Documentation

- **COMPREHENSIVE_USAGE_EXAMPLES.md** - Complete usage examples
- **TOOLS_REFERENCE.md** - Complete tools reference
- **FRAMEWORK_GUIDE.md** - Framework documentation

---

**All reporting tools support CSV and JSON exports!** 🎉

