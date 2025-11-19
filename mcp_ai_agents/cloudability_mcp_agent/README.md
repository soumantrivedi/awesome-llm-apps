# Cloudability MCP Server

A simple, straightforward MCP (Model Context Protocol) server for extracting cost reports from IBM Cloudability API. This server provides tools to query cost data by dashboard view name and filter by fields like `product_id` (e.g., Kubernetes/K8s).

## Quick Start

1. **Get API Key**: [Cloudability Preferences](https://app.apptio.com/cloudability#/settings/preferences) → Enable API
2. **Install**: `pip install -r requirements.txt`
3. **Configure**: Create `.env` file with `CLOUDABILITY_API_KEY=your_key`
4. **Test**: `python3 test_server.py` (or `python test_server.py`)
5. **Configure in Cursor**: Add MCP server to Cursor settings (see [Configuring MCP Server in Cursor](#configuring-mcp-server-in-cursor))

> **⚠️ Common Issue**: If you see "spawn python ENOENT" error, use `python3` instead of `python` in your Cursor MCP configuration. See [Troubleshooting](#issue-mcp-server-not-connecting-in-cursor) for details.

## Features

- ✅ **Get Cost Reports by View Name**: Retrieve cost data for any dashboard view
- ✅ **Filter by Product ID**: Filter reports by product (e.g., K8s, EC2, S3)
- ✅ **List Available Views**: Discover all dashboard views in your Cloudability account
- ✅ **Advanced Filtering**: Support for multiple filter conditions and custom dimensions
- ✅ **Simple & Clear**: No ambiguous results, well-documented code
- ✅ **MCP Protocol Compliant**: Follows official MCP standards for stdio communication

## Prerequisites

- Python 3.8 or higher
- Cloudability API key (see [Getting Your API Key](#getting-your-api-key))
- Cursor IDE (for MCP integration)

## Getting Your API Key

1. Navigate to [Cloudability Preferences](https://app.apptio.com/cloudability#/settings/preferences)
2. Under the **Cloudability API** section, select **Enable API**
3. Your API key will be generated and displayed in the text box
4. Copy this key - you'll need it for configuration

**Note**: For EU, APAC, or ME regions, use the appropriate regional API endpoint:
- EU: `https://api-eu.cloudability.com/v3`
- APAC: `https://api-au.cloudability.com/v3`
- ME: `https://api-me.cloudability.com/v3`

## Installation

### Step 1: Clone and Navigate

```bash
cd mcp_ai_agents/cloudability_mcp_agent
```

### Step 2: Install Dependencies

**Option A: Using Virtual Environment (Recommended)**

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# OR
venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt
```

**Option B: Using System Python (if allowed)**

```bash
pip install -r requirements.txt
```

**Note**: If you get an "externally-managed-environment" error, use Option A (virtual environment).

### Step 3: Configure Environment Variables

Create a `.env` file in the `cloudability_mcp_agent` directory:

```bash
# Create .env file
cat > .env << EOF
CLOUDABILITY_API_KEY=your_api_key_here
CLOUDABILITY_BASE_URL=https://api.cloudability.com/v3
EOF
```

Or manually create `.env` with this content:

```
CLOUDABILITY_API_KEY=your_api_key_here
CLOUDABILITY_BASE_URL=https://api.cloudability.com/v3
```

**For different regions**, update `CLOUDABILITY_BASE_URL`:
- EU: `https://api-eu.cloudability.com/v3`
- APAC: `https://api-au.cloudability.com/v3`
- ME: `https://api-me.cloudability.com/v3`

**Important**: Replace `your_api_key_here` with your actual Cloudability API key.

### Step 4: Test the Server (Recommended)

Test your configuration before setting up in Cursor:

```bash
# If using virtual environment (recommended)
source venv/bin/activate  # On macOS/Linux
python3 test_server.py

# Or if using system Python
python3 test_server.py
```

This will:
- Verify your API key is configured correctly
- Test connection to Cloudability API
- List available tools
- Show available dashboard views

If all tests pass, your server is ready to use!

## Configuring MCP Server in Cursor

### Step 1: Open Cursor Settings

1. Open Cursor IDE
2. Go to **Settings** → **Features** → **MCP** (or search for "MCP" in settings)

### Step 2: Add MCP Server Configuration

Add the following configuration to your Cursor MCP settings:

**Option A: Using JSON Configuration**

If Cursor uses a JSON config file (typically `~/.cursor/mcp.json` or similar), add:

```json
{
  "mcpServers": {
    "cloudability": {
      "command": "/absolute/path/to/venv/bin/python3",
      "args": [
        "/absolute/path/to/cloudability_mcp_server.py"
      ],
      "env": {
        "CLOUDABILITY_API_KEY": "your_api_key_here",
        "CLOUDABILITY_BASE_URL": "https://api.cloudability.com/v3"
      }
    }
  }
}
```

**Important Notes:**
- **If using virtual environment**: Use the full path to `venv/bin/python3` (recommended)
- **If using system Python**: Use `python3` (or full path like `/usr/bin/python3`)
- Replace `/absolute/path/to/` with your actual project path
- Replace `your_api_key_here` with your actual API key

**Example with virtual environment:**
```json
{
  "mcpServers": {
    "cloudability": {
      "command": "/Users/YourName/projects/cloudability_mcp_agent/venv/bin/python3",
      "args": [
        "/Users/YourName/projects/cloudability_mcp_agent/cloudability_mcp_server.py"
      ],
      "env": {
        "CLOUDABILITY_API_KEY": "your_api_key_here",
        "CLOUDABILITY_BASE_URL": "https://api.cloudability.com/v3"
      }
    }
  }
}
```

**Option B: Using Cursor's UI**

1. In Cursor settings, find the MCP section
2. Click "Add Server" or "New Server"
3. Configure:
   - **Name**: `cloudability`
   - **Command**: `python3` (or `python` if that's what works on your system)
   - **Arguments**: `["/absolute/path/to/cloudability_mcp_server.py"]`
   - **Environment Variables**:
     - `CLOUDABILITY_API_KEY`: Your API key
     - `CLOUDABILITY_BASE_URL`: `https://api.cloudability.com/v3` (or your region)

**Finding the correct Python command:**
- On macOS/Linux: Usually `python3`
- On Windows: Usually `python`
- Test with: `which python3` or `python3 --version`
- **Helper script**: Run `./find_python.sh` to automatically detect the correct Python command and generate a sample configuration

### Step 3: Verify Configuration

1. Restart Cursor IDE
2. The MCP server should automatically connect
3. You can verify by checking Cursor's MCP status or trying to use the tools

## Available Tools

### Core Tools

### 1. `get_cost_report_by_view`

Get cost report data for a specific dashboard view with optional filtering.

**Parameters:**
- `view_name` (required): Name of the dashboard view (e.g., "AWS Cost Overview", "Kubernetes Costs")
- `product_id` (optional): Filter by product ID (e.g., "K8s", "EC2", "S3")
- `start_date` (optional): Start date in YYYY-MM-DD format
- `end_date` (optional): End date in YYYY-MM-DD format
- `limit` (optional): Maximum records to return (default: 50, max: 250)
- `offset` (optional): Pagination offset (default: 0)

**Example Usage:**
```json
{
  "view_name": "AWS Cost Overview",
  "product_id": "K8s",
  "start_date": "2024-01-01",
  "end_date": "2024-01-31"
}
```

### 2. `list_views`

List all available dashboard views in your Cloudability account.

**Parameters:**
- `limit` (optional): Maximum views to return (default: 50)
- `offset` (optional): Pagination offset (default: 0)

**Example Usage:**
```json
{
  "limit": 100
}
```

### 3. `get_cost_report_with_filters`

Get cost report with advanced filtering options.

**Parameters:**
- `view_name` (required): Name of the dashboard view
- `filters` (optional): Object with filter conditions (e.g., `{"product_id": "K8s", "vendor": "AWS"}`)
- `dimensions` (optional): Array of dimensions to group by (e.g., `["product_id", "vendor"]`)
- `metrics` (optional): Array of metrics to retrieve (e.g., `["cost", "usage"]`)
- `start_date` (optional): Start date in YYYY-MM-DD format
- `end_date` (optional): End date in YYYY-MM-DD format

**Example Usage:**
```json
{
  "view_name": "AWS Cost Overview",
  "filters": {
    "product_id": "K8s",
    "vendor": "AWS"
  },
  "dimensions": ["product_id", "service"],
  "metrics": ["cost", "usage"]
}
```

### TrueCost Explorer Insights Tools

### 4. `get_amortized_costs`

Get amortized cost data from TrueCost Explorer. Amortized costs spread upfront payments (like Reserved Instances) over their term.

**Cursor Chat Example:**
```
Get amortized costs for AWS EC2 services for January 2024, grouped by account
```

**Parameters:**
- `start_date` (optional): Start date in YYYY-MM-DD format (defaults to last 30 days)
- `end_date` (optional): End date in YYYY-MM-DD format (defaults to today)
- `filters` (optional): Filter conditions (e.g., `{"vendor": "AWS", "service": "EC2"}`)
- `dimensions` (optional): Dimensions to group by (default: `["vendor", "service"]`)
- `export_format` (optional): "json" or "csv" (default: "json")

### 5. `get_container_costs`

Get container-wise cost breakdown from TrueCost Explorer. Perfect for Kubernetes cost analysis.

**Cursor Chat Example:**
```
Get container costs for production cluster, grouped by namespace and pod
```

**Parameters:**
- `start_date` (optional): Start date in YYYY-MM-DD format
- `end_date` (optional): End date in YYYY-MM-DD format
- `filters` (optional): Filter conditions (e.g., `{"cluster_name": "prod-cluster", "namespace": "default"}`)
- `group_by` (optional): How to group costs (default: `["cluster", "namespace"]`)
- `export_format` (optional): "json" or "csv"

### 6. `explore_tags`

Explore costs by tags from TrueCost Explorer. Analyze costs based on custom tags like Environment, Team, Project.

**Cursor Chat Example:**
```
What are the costs by Environment tag for Production environment?
```

**Parameters:**
- `tag_key` (required): The tag key to explore (e.g., "Environment", "Team")
- `tag_value` (optional): Specific tag value to filter by
- `start_date` (optional): Start date in YYYY-MM-DD format
- `end_date` (optional): End date in YYYY-MM-DD format
- `additional_filters` (optional): Additional filters to combine
- `export_format` (optional): "json" or "csv"

### 7. `get_anomaly_detection`

Get anomaly detection results from TrueCost Explorer. Identifies unusual spending patterns and cost spikes.

**Cursor Chat Example:**
```
Find high-severity cost anomalies in AWS for the last month
```

**Parameters:**
- `start_date` (optional): Start date in YYYY-MM-DD format
- `end_date` (optional): End date in YYYY-MM-DD format
- `severity` (optional): "low", "medium", "high", or "all" (default: "all")
- `filters` (optional): Filter conditions
- `min_cost_change_percent` (optional): Minimum cost change % (default: 10.0)
- `export_format` (optional): "json" or "csv"

### 8. `list_available_tags`

List all available tag keys in your Cloudability account.

**Cursor Chat Example:**
```
What tags are available in my Cloudability account?
```

**Parameters:**
- `limit` (optional): Maximum tag keys to return (default: 100)

### 9. `export_cost_report`

Export cost report with custom filters to JSON or CSV format. Most flexible tool for custom reports.

**Cursor Chat Example:**
```
Export a cost report for AWS EC2 t3.medium instances in us-east-1 as CSV
```

**Parameters:**
- `start_date` (required): Start date in YYYY-MM-DD format
- `end_date` (required): End date in YYYY-MM-DD format
- `filters` (optional): Filter conditions (any valid Cloudability filter keys)
- `dimensions` (optional): Dimensions to group by
- `metrics` (optional): Metrics to include (default: `["cost"]`)
- `export_format` (optional): "json" or "csv" (default: "json")
- `file_name` (optional): Custom file name (without extension)

## Usage Examples

For detailed usage examples including Cursor chat prompts and Python scripts, see [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md).

### Quick Examples

### Example 1: Get Kubernetes Costs

```python
# Via MCP protocol (automatically handled by Cursor)
{
  "method": "tools/call",
  "params": {
    "name": "get_cost_report_by_view",
    "arguments": {
      "view_name": "AWS Cost Overview",
      "product_id": "K8s"
    }
  }
}
```

### Example 2: List All Views

```python
{
  "method": "tools/call",
  "params": {
    "name": "list_views",
    "arguments": {}
  }
}
```

### Example 3: Advanced Filtering

```python
{
  "method": "tools/call",
  "params": {
    "name": "get_cost_report_with_filters",
    "arguments": {
      "view_name": "AWS Cost Overview",
      "filters": {
        "product_id": "K8s",
        "vendor": "AWS"
      },
      "start_date": "2024-01-01",
      "end_date": "2024-01-31"
    }
  }
}
```

### Example 4: Get Amortized Costs (Cursor Chat)

Simply ask in Cursor chat:
```
Get amortized costs for AWS EC2 services for January 2024
```

### Example 5: Container Costs (Cursor Chat)

```
Show me container costs for production cluster grouped by namespace
```

### Example 6: Tag Explorer (Cursor Chat)

```
What are the costs by Environment tag for Production?
```

### Example 7: Anomaly Detection (Cursor Chat)

```
Find high-severity cost anomalies in the last 30 days
```

### Example 8: Export Custom Report (Cursor Chat)

```
Export a cost report for AWS EC2 in us-east-1 as CSV
```

For more examples, see [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md) or run:
```bash
python3 examples_insights_tools.py
```

## Response Format

All successful responses follow this structure:

```json
{
  "success": true,
  "view_name": "AWS Cost Overview",
  "view_id": "12345",
  "filters": {
    "product_id": "K8s"
  },
  "data": {
    "result": [...],
    "meta": {...}
  }
}
```

Error responses:

```json
{
  "success": false,
  "error": "Error message here",
  "status_code": 404
}
```

## Troubleshooting

### Issue: "CLOUDABILITY_API_KEY environment variable is required"

**Solution**: Make sure you've set the `CLOUDABILITY_API_KEY` environment variable in your MCP server configuration.

### Issue: "View 'X' not found"

**Solution**: 
1. Use `list_views` tool to see all available views
2. Check that the view name matches exactly (case-sensitive)
3. Verify you have access to the view in Cloudability

### Issue: "API request failed: 401 Unauthorized"

**Solution**:
1. Verify your API key is correct
2. Check that API access is enabled in Cloudability settings
3. Ensure you're using the correct regional endpoint

### Issue: "API request failed: 404 Not Found"

**Solution**:
1. Verify the API endpoint URL is correct
2. Check Cloudability API documentation for the correct endpoint structure
3. Ensure your Cloudability account has access to the requested data

### Issue: MCP Server Not Connecting in Cursor

**Error: "spawn python ENOENT" or "spawn python3 ENOENT"**

**Solution**:
1. **Find the correct Python command:**
   ```bash
   # On macOS/Linux
   which python3
   python3 --version
   
   # Or try
   which python
   python --version
   ```

2. **Update Cursor configuration** to use the correct command:
   - If `python3` works: Use `python3` in the command field
   - If `python` works: Use `python` in the command field
   - If neither works: You may need to use the full path like `/usr/bin/python3`

3. **Verify the script path is absolute:**
   ```bash
   # Get absolute path
   cd /Users/Souman_Trivedi/IdeaProjects/awesome-llm-apps/mcp_ai_agents/cloudability_mcp_agent
   pwd
   # Use this full path in your configuration
   ```

4. **Ensure Python 3.8+ is installed:**
   ```bash
   python3 --version  # Should show 3.8 or higher
   ```

5. **Check Cursor's MCP logs** for detailed error messages
   - Look for the exact error in Cursor's developer console or MCP logs

6. **Restart Cursor** after configuration changes

**Common fixes:**
- macOS: Change `python` to `python3` in Cursor config
- Windows: Usually `python` works, but verify with `python --version`
- Linux: Usually `python3` works

## API Documentation Reference

For detailed API documentation, refer to:
- [Cloudability API V3 Getting Started](https://www.ibm.com/docs/en/cloudability-commercial/cloudability-premium/saas?topic=api-getting-started-cloudability-v3)

## Architecture

```
┌─────────────┐    ┌──────────────────────┐    ┌─────────────────┐
│   Cursor    │◄──►│  Cloudability MCP    │◄──►│  Cloudability   │
│     IDE     │    │      Server          │    │      API        │
└─────────────┘    └──────────────────────┘    └─────────────────┘
     (MCP)              (stdio protocol)          (REST API)
```

The MCP server:
- Communicates with Cursor via stdio (standard input/output)
- Uses JSON-RPC 2.0 protocol
- Makes HTTP requests to Cloudability API
- Returns structured data to Cursor

## Development

### Project Structure

```
cloudability_mcp_agent/
├── cloudability_mcp_server.py  # Main MCP server implementation
├── requirements.txt            # Python dependencies
├── README.md                   # This file
└── .env                        # Environment variables (create this)
```

### Code Structure

- `CloudabilityMCPServer`: Main server class implementing MCP protocol
- `get_tools()`: Returns available tool definitions
- `handle_request()`: Processes MCP protocol requests
- `call_tool()`: Executes specific tools
- Tool methods: `_get_cost_report_by_view()`, `_list_views()`, `_get_cost_report_with_filters()`

## Security Notes

- **Never commit your `.env` file** to version control
- Keep your API key secure and rotate it regularly
- Use environment variables for sensitive configuration
- The API key is used for Basic Authentication (username only, empty password)

## Support

For issues or questions:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review Cloudability API documentation
3. Check Cursor MCP logs for detailed error messages

## License

This project is part of the awesome-llm-apps repository.

