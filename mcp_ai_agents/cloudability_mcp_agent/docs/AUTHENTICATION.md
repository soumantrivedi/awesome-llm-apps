# Authentication Guide

Cloudability MCP Server supports multiple authentication methods for the Cloudability API.

## Authentication Methods

### 1. Cloudability API Keys (Basic Auth) - Legacy

This is the traditional authentication method using a single API key.

**Setup:**
```bash
# In .env file
CLOUDABILITY_API_KEY=your_api_key_here
CLOUDABILITY_AUTH_TYPE=basic
```

**Get your API key:**
1. Go to [Cloudability Preferences](https://app.apptio.com/cloudability#/settings/preferences)
2. Under "Cloudability API" section, select "Enable API"
3. Copy the generated API key

**Usage:**
The API key is used as the username with an empty password in Basic Authentication.

---

### 2. Enhanced Access Administration (Public/Private Key Pair) - Recommended

This is the modern, more secure authentication method that uses public and private key pairs. It supports multiple API keys, key rotation, and better security.

#### Step 1: Create API Keys

1. Log in to your Cloudability account
2. Navigate to your **User Profile** → **API Keys** tab
3. Click **Create API Key**
4. Provide:
   - Name and description
   - Expiration policy
5. **Important**: Copy both the **Public Key** (keyAccess) and **Private Key** (keySecret)
   - ⚠️ The private key is only shown once during creation - store it securely!
6. Assign necessary environment access and roles to the API key
7. Retrieve the **Environment ID** from the **Environment Access** tab

#### Step 2: Configure Environment Variables

**Option A: Using .env file (Recommended)**

```bash
# Enhanced Access Administration (Public/Private Key Pair)
CLOUDABILITY_PUBLIC_KEY=your_public_key_here
CLOUDABILITY_PRIVATE_KEY=your_private_key_here
CLOUDABILITY_ENVIRONMENT_ID=your_environment_id_here
CLOUDABILITY_AUTH_TYPE=opentoken

# Regional Frontdoor URL (optional, defaults to US)
# For EU: https://frontdoor-eu.apptio.com
# For APAC: https://frontdoor-au.apptio.com
CLOUDABILITY_FRONTDOOR_URL=https://frontdoor.apptio.com
```

**Option B: Using Cursor MCP Configuration**

```json
{
  "mcpServers": {
    "cloudability": {
      "command": "/path/to/venv/bin/python3",
      "args": ["-u", "/path/to/cloudability_mcp_server.py"],
      "env": {
        "CLOUDABILITY_PUBLIC_KEY": "your_public_key_here",
        "CLOUDABILITY_PRIVATE_KEY": "your_private_key_here",
        "CLOUDABILITY_ENVIRONMENT_ID": "your_environment_id_here",
        "CLOUDABILITY_AUTH_TYPE": "opentoken",
        "CLOUDABILITY_FRONTDOOR_URL": "https://frontdoor.apptio.com",
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

#### Step 3: How It Works

1. The server authenticates with your public/private key pair to `frontdoor.apptio.com/service/apikeylogin`
2. Receives an `apptio-opentoken` in response
3. Uses this token for all subsequent API requests
4. Token is cached and reused until it expires

#### Regional Frontdoor URLs

| Region | Frontdoor URL |
|--------|---------------|
| US (Default) | `https://frontdoor.apptio.com` |
| EU | `https://frontdoor-eu.apptio.com` |
| APAC | `https://frontdoor-au.apptio.com` |

---

### 3. Bearer Token (Direct OpenToken)

If you already have an OpenToken, you can use it directly:

```bash
CLOUDABILITY_API_KEY=your_opentoken_here
CLOUDABILITY_AUTH_TYPE=bearer
CLOUDABILITY_ENVIRONMENT_ID=your_environment_id_here
```

---

## Configuration Priority

The authentication system checks credentials in this order:

1. **Public/Private Key Pair** (if both `CLOUDABILITY_PUBLIC_KEY` and `CLOUDABILITY_PRIVATE_KEY` are set)
   - Automatically uses Enhanced Access Administration
   - Sets `AUTH_TYPE=opentoken`

2. **API Key** (if `CLOUDABILITY_API_KEY` is set)
   - Uses Basic or Bearer auth based on `CLOUDABILITY_AUTH_TYPE`

---

## Security Best Practices

1. **Never commit credentials to version control**
   - Add `.env` to `.gitignore`
   - Use environment variables or secure secret management

2. **Store private keys securely**
   - Private keys are only shown once during creation
   - Use a password manager or secure vault

3. **Rotate keys regularly**
   - Enhanced Access Administration supports multiple keys
   - Rotate keys periodically for better security

4. **Use least privilege**
   - Assign only necessary permissions to API keys
   - Use environment-specific keys when possible

5. **Monitor API key usage**
   - Review API key access logs regularly
   - Revoke unused or compromised keys immediately

---

## Troubleshooting

### Error: "Authentication failed"

**Possible causes:**
- Invalid public/private key pair
- Expired API key
- Incorrect frontdoor URL for your region
- Missing environment ID (if required)

**Solutions:**
1. Verify keys are correct (no extra spaces, complete keys)
2. Check API key expiration in Cloudability
3. Verify frontdoor URL matches your region
4. Ensure environment ID is set if required

### Error: "OpenToken not found in authentication response"

**Possible causes:**
- Frontdoor authentication endpoint issue
- Network connectivity problem
- Invalid key pair

**Solutions:**
1. Check network connectivity to frontdoor URL
2. Verify public/private keys are correct
3. Try regenerating API keys in Cloudability

### Error: "API key is required"

**Possible causes:**
- No authentication credentials provided
- Environment variables not loaded

**Solutions:**
1. Set either:
   - `CLOUDABILITY_API_KEY` (for basic/bearer), or
   - `CLOUDABILITY_PUBLIC_KEY` and `CLOUDABILITY_PRIVATE_KEY` (for Enhanced Access Administration)
2. Ensure `.env` file is in the correct location
3. Restart the MCP server after changing credentials

---

## References

- [Enhanced Access Administration API: Authentication via API keys](https://www.ibm.com/docs/en/cloudability-commercial/cloudability-msp/saas?topic=cmgscmae-enhanced-access-administration-api-authentication-via-api-keys)
- [Enhanced Access Administration API: Overview of API keys and FAQ](https://www.ibm.com/docs/en/apptio-platform/datalink-classic/saas?topic=dcacg-enhanced-access-administration-api-overview-api-keys-faq)



