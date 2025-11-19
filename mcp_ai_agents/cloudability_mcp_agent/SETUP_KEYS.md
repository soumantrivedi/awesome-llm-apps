# Setup Public/Private Key Pair Authentication

This guide shows you exactly where to add your Cloudability public and private keys.

## Quick Setup

### Step 1: Create `.env` file

Create or edit the `.env` file in the `cloudability_mcp_agent` directory:

```bash
cd mcp_ai_agents/cloudability_mcp_agent
nano .env  # or use your preferred editor
```

### Step 2: Add Your Credentials

Add the following to your `.env` file (replace with your actual values):

```bash
# Enhanced Access Administration (Public/Private Key Pair)
CLOUDABILITY_PUBLIC_KEY=your_public_key_here
CLOUDABILITY_PRIVATE_KEY=your_private_key_here
CLOUDABILITY_ENVIRONMENT_ID=your_environment_id_here
CLOUDABILITY_AUTH_TYPE=opentoken

# API Base URL (adjust for your region if needed)
CLOUDABILITY_BASE_URL=https://api.cloudability.com/v3

# Frontdoor URL (adjust for your region if needed)
# US (default): https://frontdoor.apptio.com
# EU: https://frontdoor-eu.apptio.com
# APAC: https://frontdoor-au.apptio.com
CLOUDABILITY_FRONTDOOR_URL=https://frontdoor.apptio.com
```

### Step 3: Replace Placeholder Values

Replace the following placeholders with your actual values:

- `your_public_key_here` → Your Public Key (keyAccess) from Cloudability
- `your_private_key_here` → Your Private Key (keySecret) from Cloudability
- `your_environment_id_here` → Your Environment ID from Cloudability

**Example:**
```bash
CLOUDABILITY_PUBLIC_KEY=abc123xyz789
CLOUDABILITY_PRIVATE_KEY=secret_key_here_do_not_share
CLOUDABILITY_ENVIRONMENT_ID=env-12345
CLOUDABILITY_AUTH_TYPE=opentoken
CLOUDABILITY_BASE_URL=https://api.cloudability.com/v3
CLOUDABILITY_FRONTDOOR_URL=https://frontdoor.apptio.com
```

### Step 4: Verify Configuration

The server will automatically:
1. Use your public/private key pair to authenticate
2. Get an OpenToken from the frontdoor service
3. Use that token for all API requests

## For Cursor MCP Configuration

If you're configuring in Cursor's `~/.cursor/mcp.json`, add:

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
        "CLOUDABILITY_FRONTDOOR_URL": "https://frontdoor.apptio.com",
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

## Security Notes

⚠️ **Important:**
- Never commit your `.env` file to version control
- The `.env` file should already be in `.gitignore`
- Keep your private key secure - it's only shown once when created
- Use environment variables in production instead of `.env` files

## Testing

After adding your credentials, restart the MCP server and test with:

```bash
# Test authentication
python3 -c "from src.config import Config; Config.validate(); print('✓ Configuration valid')"
```

## Need Help?

- See [Authentication Guide](docs/AUTHENTICATION.md) for detailed instructions
- See [Quick Start Guide](docs/QUICK_START.md) for full setup
- Check [Troubleshooting](TROUBLESHOOTING.md) for common issues



