# Cloudability MCP Server Documentation

Welcome to the Cloudability MCP Server documentation. This directory contains detailed guides for using and extending the server.

## Documentation Index

### Getting Started
- **[Quick Start Guide](QUICK_START.md)** - Get up and running in minutes
- **[Main README](../README.md)** - Overview and installation

### User Guides
- **[Quick Start Guide](QUICK_START.md)** - Get up and running in minutes
- **[Authentication Guide](AUTHENTICATION.md)** - Setup public/private key pairs and other auth methods
- **[API Reference](API_REFERENCE.md)** - Complete Cloudability API v3 reference (dimensions, metrics, operators)
- **[Tools Reference](TOOLS_REFERENCE.md)** - Complete reference for all 20 tools
- **[Usage Examples](USAGE_EXAMPLES.md)** - Practical examples for common tasks
- **[Comprehensive Report Tool](COMPREHENSIVE_REPORT_USAGE.md)** - Guide for the advanced reporting tool

### Developer Guides
- **[Framework Guide](FRAMEWORK_GUIDE.md)** - How to extend and add new tools
- **[Security Guidelines](SECURITY.md)** - Security best practices

## Quick Links

### Most Common Tasks

**Get Started:**
1. Read [Quick Start Guide](QUICK_START.md)
2. Configure your API key
3. Start using tools in Cursor

**Find a Tool:**
- See [Tools Reference](TOOLS_REFERENCE.md) for complete list
- Check [Usage Examples](USAGE_EXAMPLES.md) for how to use them
- Reference [API Reference](API_REFERENCE.md) for dimensions, metrics, and filter operators

**Generate Reports:**
- Use `generate_cost_report` - See [Comprehensive Report Guide](COMPREHENSIVE_REPORT_USAGE.md)
- Use `get_amortized_costs` - See [Usage Examples](USAGE_EXAMPLES.md)

**Extend the Server:**
- See [Framework Guide](FRAMEWORK_GUIDE.md) for adding new tools

## Tool Categories

### Cost Reporting (5 tools)
- `get_cost_report_by_view` - View-based reports
- `get_cost_report_with_filters` - Advanced filtering
- `get_amortized_costs` - Amortized cost analysis
- `export_cost_report` - Custom report export
- `generate_cost_report` - Comprehensive reporting tool

### Container/Kubernetes (3 tools)
- `get_container_costs` - Container cost breakdown
- `get_container_resource_usage` - Resource metrics
- `analyze_container_cost_allocation` - Cost allocation

### Budget Management (4 tools)
- `list_budgets` - List all budgets
- `get_budget` - Get budget details
- `create_budget` - Create new budget
- `update_budget` - Update existing budget

### Forecasts & Estimates (2 tools)
- `get_spending_estimate` - Current month estimate
- `get_spending_forecast` - Multi-month forecast

### Tag Explorer (2 tools)
- `list_available_tags` - List tag keys
- `explore_tags` - Explore costs by tags

### Anomaly Detection (1 tool)
- `get_anomaly_detection` - Detect cost anomalies

### Discovery (3 tools)
- `list_views` - List dashboard views
- `get_available_measures` - Discover dimensions/metrics
- `get_filter_operators` - Get filter operators

## Need Help?

1. **Installation Issues**: See [Quick Start Guide](QUICK_START.md)
2. **Tool Usage**: See [Tools Reference](TOOLS_REFERENCE.md) or [Usage Examples](USAGE_EXAMPLES.md)
3. **Security Questions**: See [Security Guidelines](SECURITY.md)
4. **Extending the Server**: See [Framework Guide](FRAMEWORK_GUIDE.md)
