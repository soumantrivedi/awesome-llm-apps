# Quick Start Guide

Get the Cloudability MCP Server up and running in minutes.

## Prerequisites

- Python 3.8 or higher
- Cloudability API key ([Get your API key](https://app.apptio.com/cloudability#/settings/preferences))
- Cursor IDE (for MCP integration)

## Installation

### Step 1: Navigate to Project

```bash
cd mcp_ai_agents/cloudability_mcp_agent
```

### Step 2: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Authentication

**Option A: Enhanced Access Administration (Public/Private Key Pair) - Recommended**

Create a `.env` file:

```bash
# Enhanced Access Administration (Public/Private Key Pair)
CLOUDABILITY_PUBLIC_KEY=your_public_key_here
CLOUDABILITY_PRIVATE_KEY=your_private_key_here
CLOUDABILITY_ENVIRONMENT_ID=your_environment_id_here
CLOUDABILITY_AUTH_TYPE=opentoken
CLOUDABILITY_BASE_URL=https://api.cloudability.com/v3
```

**Get your keys:**
1. Go to User Profile → API Keys in Cloudability
2. Create API Key and copy both Public Key and Private Key
3. Get Environment ID from Environment Access tab

**Option B: Legacy API Key (Basic Auth)**

```bash
CLOUDABILITY_API_KEY=your_api_key_here
CLOUDABILITY_BASE_URL=https://api.cloudability.com/v3
```

**Get your API key:** [Cloudability Preferences](https://app.apptio.com/cloudability#/settings/preferences) → Enable API

**For different regions:**
- EU: `https://api-eu.cloudability.com/v3` (Frontdoor: `https://frontdoor-eu.apptio.com`)
- APAC: `https://api-au.cloudability.com/v3` (Frontdoor: `https://frontdoor-au.apptio.com`)
- ME: `https://api-me.cloudability.com/v3`

**See [Authentication Guide](AUTHENTICATION.md) for detailed setup instructions.**

## Configure in Cursor

Add to `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "cloudability": {
      "command": "/absolute/path/to/venv/bin/python3",
      "args": ["-u", "/absolute/path/to/cloudability_mcp_server.py"],
      "env": {
        "CLOUDABILITY_PUBLIC_KEY": "your_public_key_here",
        "CLOUDABILITY_PRIVATE_KEY": "your_private_key_here",
        "CLOUDABILITY_ENVIRONMENT_ID": "your_environment_id_here",
        "CLOUDABILITY_AUTH_TYPE": "opentoken",
        "CLOUDABILITY_BASE_URL": "https://api.cloudability.com/v3",
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

**Important:**
- Use absolute paths
- Replace `/absolute/path/to/` with your actual project path
- Restart Cursor after configuration

## Verify Installation

Test the server:

```bash
python3 -c "from src.framework.tool_base import get_registry; from src import tools; registry = get_registry(); print(f'Tools: {len(registry.list_tools())}')"
```

Should show: `Tools: 20`

## First Steps

### 1. List Available Views

In Cursor chat:
```
List all available views in Cloudability
```

### 2. Get a Cost Report

```
Get cost report for "AWS Cost Overview" view
```

### 3. Generate Comprehensive Report

```
Generate cost report for view "Product-12284-OFT - self-managed Kubernetes" with namespace filter "ici*" for last month, export as markdown
```

## Troubleshooting

### Server Not Starting

- Check Python version: `python3 --version` (should be 3.8+)
- Verify virtual environment is activated
- Check API key is set correctly

### No Tools Available

- Restart Cursor after configuration changes
- Check server logs for errors
- Verify tools are registered: See [Troubleshooting](../TROUBLESHOOTING.md)

### API Errors

- Verify API key is correct
- Check you're using the correct regional endpoint
- Ensure API access is enabled in Cloudability settings

## Next Steps

- **[Tools Reference](TOOLS_REFERENCE.md)** - Learn about all available tools
- **[Usage Examples](USAGE_EXAMPLES.md)** - See practical examples
- **[Comprehensive Report Guide](COMPREHENSIVE_REPORT_USAGE.md)** - Advanced reporting
