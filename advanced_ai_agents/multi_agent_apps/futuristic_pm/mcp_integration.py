"""
MCP Integration Module for FuturisticPM
Uses official MCP standards (November 2025) for Atlassian, GitHub, Slack, and extensible for other MCP tools

Official MCP Servers:
- Atlassian: Remote MCP Server (SSE) at https://mcp.atlassian.com/v1/sse (OAuth 2.0)
- GitHub: @modelcontextprotocol/server-github (stdio via npx)
- Slack: @modelcontextprotocol/server-slack (stdio via npx)
"""

import asyncio
import os
import json
import logging
from typing import Dict, List, Optional, Any, Union
from mcp import StdioServerParameters

logger = logging.getLogger(__name__)

# Try to import MCP tools
try:
    from agno.tools.mcp import MCPTools, MultiMCPTools
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    MCPTools = None
    MultiMCPTools = None
    logger.warning("MCP tools not available. Install: pip install agno mcp")

# Try to import SSE (Server-Sent Events) client for remote MCP servers
try:
    import httpx
    import sseclient
    SSE_AVAILABLE = True
except ImportError:
    SSE_AVAILABLE = False
    httpx = None
    sseclient = None
    logger.warning("SSE client not available. Install: pip install httpx sseclient-py")


# Official MCP Server Configurations (November 2025)
KNOWN_MCP_SERVERS = {
    "github": {
        "type": "stdio",
        "npx": "npx -y @modelcontextprotocol/server-github",
        "docker": "ghcr.io/github/github-mcp-server",
        "env_vars": ["GITHUB_PERSONAL_ACCESS_TOKEN", "GITHUB_TOOLSETS"],
        "official": True,
        "docs": "https://github.com/modelcontextprotocol/servers/tree/main/src/github"
    },
    "slack": {
        "type": "stdio",
        "npx": "npx -y @modelcontextprotocol/server-slack",
        "env_vars": ["SLACK_BOT_TOKEN", "SLACK_TEAM_ID"],
        "official": True,
        "docs": "https://github.com/modelcontextprotocol/servers/tree/main/src/slack"
    },
    "atlassian": {
        "type": "sse",  # Server-Sent Events (Remote MCP Server)
        "endpoint": "https://mcp.atlassian.com/v1/sse",
        "auth": "oauth2",
        "env_vars": ["ATLASSIAN_CLIENT_ID", "ATLASSIAN_CLIENT_SECRET", "ATLASSIAN_ACCESS_TOKEN"],
        "official": True,
        "docs": "https://www.atlassian.com/platform/remote-mcp-server",
        "note": "Uses OAuth 2.0 authentication. Requires OAuth flow to obtain access token."
    },
    "amazon_q": {
        "type": "stdio",
        "npx": "npx -y @aws-sdk/mcp-server-amazon-q",
        "env_vars": ["AWS_REGION", "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AMAZON_Q_APP_ID"],
        "official": False,
        "docs": "https://github.com/aws-samples/amazon-q-mcp-server"
    },
    "notion": {
        "type": "stdio",
        "npx": "npx -y @notionhq/notion-mcp-server",
        "env_vars": ["NOTION_API_KEY"],
        "official": True,
        "docs": "https://github.com/notionhq/notion-mcp-server"
    },
    "perplexity": {
        "type": "stdio",
        "npx": "npx -y @chatmcp/server-perplexity-ask",
        "env_vars": ["PERPLEXITY_API_KEY"],
        "official": False,
        "docs": "https://github.com/chatmcp/server-perplexity-ask"
    },
    "calendar": {
        "type": "stdio",
        "npx": "npx @gongrzhe/server-calendar-autoauth-mcp",
        "env_vars": [],
        "official": False
    },
    "gmail": {
        "type": "stdio",
        "npx": "npx @gongrzhe/server-gmail-autoauth-mcp",
        "env_vars": [],
        "official": False
    }
}


class MCPIntegrationManager:
    """Manages MCP server connections for multiple services with extensible support"""
    
    def __init__(self):
        self.mcp_tools = None
        self._initialized = False
        self._env = {}
        self._servers = []
        self._active_servers = {}  # Track which servers are active
    
    async def initialize(self, 
                        jira_config: Optional[Dict] = None,
                        confluence_config: Optional[Dict] = None,
                        github_config: Optional[Dict] = None,
                        slack_config: Optional[Dict] = None,
                        amazon_q_config: Optional[Dict] = None,
                        custom_servers: Optional[List[Dict]] = None):
        """
        Initialize MCP server connections
        
        Args:
            jira_config: Jira configuration dict
            confluence_config: Confluence configuration dict
            github_config: GitHub configuration dict
            slack_config: Slack configuration dict
            amazon_q_config: Amazon Q Developer configuration dict
            custom_servers: List of custom MCP server configs
                Format: [{"name": "server_name", "command": "npx -y @package", "env": {...}}]
        """
        if not MCP_AVAILABLE:
            raise ImportError("MCP tools not available. Install: pip install agno mcp")
        
        self._env = {**os.environ}
        self._servers = []
        self._active_servers = {}
        
        # GitHub MCP Server (Official - @modelcontextprotocol/server-github)
        # Documentation: https://github.com/modelcontextprotocol/servers/tree/main/src/github
        if github_config and github_config.get('token'):
            self._env['GITHUB_PERSONAL_ACCESS_TOKEN'] = github_config['token']
            self._env['GITHUB_TOOLSETS'] = github_config.get('toolsets', 'repos,issues,pull_requests')
            
            # Official GitHub MCP Server via npx
            server_cmd = KNOWN_MCP_SERVERS["github"]["npx"]
            self._servers.append(server_cmd)
            self._active_servers["github"] = {
                "type": "stdio",
                "command": server_cmd,
                "official": True
            }
            logger.info("GitHub MCP server configured (official @modelcontextprotocol/server-github)")
        
        # Slack MCP Server (Official - @modelcontextprotocol/server-slack)
        # Documentation: https://github.com/modelcontextprotocol/servers/tree/main/src/slack
        if slack_config and (slack_config.get('bot_token') or slack_config.get('token')):
            token = slack_config.get('bot_token') or slack_config.get('token')
            self._env['SLACK_BOT_TOKEN'] = token
            if slack_config.get('team_id'):
                self._env['SLACK_TEAM_ID'] = slack_config['team_id']
            
            # Official Slack MCP Server via npx
            server_cmd = KNOWN_MCP_SERVERS.get("slack", {}).get("npx", "npx -y @modelcontextprotocol/server-slack")
            self._servers.append(server_cmd)
            self._active_servers["slack"] = {
                "type": "stdio",
                "command": server_cmd,
                "official": True
            }
            logger.info("Slack MCP server configured (official @modelcontextprotocol/server-slack)")
        
        # Atlassian Remote MCP Server (Official - uses SSE/OAuth 2.0)
        # Official endpoint: https://mcp.atlassian.com/v1/sse
        # Documentation: https://www.atlassian.com/platform/remote-mcp-server
        atlassian_configured = False
        atlassian_access_token = None
        atlassian_site_url = None
        
        if jira_config or confluence_config:
            # Check if using OAuth (official MCP) or API token (fallback)
            jira_auth_method = jira_config.get('auth_method', 'api_token') if jira_config else None
            confluence_auth_method = confluence_config.get('auth_method', 'api_token') if confluence_config else None
            
            # Prefer OAuth if available
            atlassian_access_token = (jira_config.get('oauth_access_token') if jira_auth_method == 'oauth' else None) or \
                                   (confluence_config.get('oauth_access_token') if confluence_auth_method == 'oauth' else None)
            
            if atlassian_access_token:
                # Use official Atlassian Remote MCP Server (SSE)
                atlassian_endpoint = KNOWN_MCP_SERVERS.get("atlassian", {}).get("endpoint")
                if atlassian_endpoint:
                    # Store OAuth credentials for SSE connection
                    self._env['ATLASSIAN_ACCESS_TOKEN'] = atlassian_access_token
                    self._env['ATLASSIAN_CLIENT_ID'] = jira_config.get('oauth_client_id', '') or confluence_config.get('oauth_client_id', '')
                    self._env['ATLASSIAN_CLIENT_SECRET'] = jira_config.get('oauth_client_secret', '') or confluence_config.get('oauth_client_secret', '')
                    
                    # Extract site URL
                    site_url = jira_config.get('url', '') or confluence_config.get('url', '')
                    if site_url:
                        # Extract site name from URL (e.g., "yourcompany" from "https://yourcompany.atlassian.net")
                        site_url = site_url.replace('https://', '').replace('http://', '').replace('.atlassian.net', '').replace('/wiki', '')
                        atlassian_site_url = site_url
                        self._env['ATLASSIAN_SITE_URL'] = site_url
                    
                    # Note: SSE-based remote MCP servers require MCP client library support
                    # The connection will be established when the MCP client supports SSE endpoints
                    # For now, we store the configuration
                    atlassian_configured = True
                    self._active_servers["atlassian"] = {
                        "type": "sse",
                        "endpoint": atlassian_endpoint,
                        "site_url": atlassian_site_url
                    }
                    logger.info(f"Atlassian Remote MCP Server (SSE) configured with OAuth token for site: {atlassian_site_url}")
                else:
                    logger.warning("Atlassian Remote MCP Server endpoint not found in configuration")
            else:
                # API Token method: Use custom MCP wrapper
                # Custom MCP server wrapper for API token authentication
                use_custom_mcp = False
                jira_api_token_available = False
                confluence_api_token_available = False
                
                if jira_config and jira_config.get('auth_method') == 'api_token':
                    jira_url = jira_config.get('url', '')
                    jira_email = jira_config.get('email', '')
                    jira_token = jira_config.get('token', '')
                    
                    # Store credentials for custom MCP server
                    self._env['JIRA_URL'] = jira_url
                    self._env['JIRA_EMAIL'] = jira_email
                    self._env['JIRA_API_TOKEN'] = jira_token
                    self._env['JIRA_PROJECT_KEY'] = jira_config.get('project_key', '')
                    self._env['JIRA_BOARD_ID'] = str(jira_config.get('board_id', '0'))
                    use_custom_mcp = True
                    jira_api_token_available = True
                    atlassian_configured = True
                
                if confluence_config and confluence_config.get('auth_method') == 'api_token':
                    confluence_url = confluence_config.get('url', '')
                    confluence_email = confluence_config.get('email', '')
                    confluence_token = confluence_config.get('token', '')
                    
                    # Store credentials for custom MCP server
                    self._env['CONFLUENCE_URL'] = confluence_url
                    self._env['CONFLUENCE_EMAIL'] = confluence_email
                    self._env['CONFLUENCE_API_TOKEN'] = confluence_token
                    self._env['CONFLUENCE_SPACE'] = confluence_config.get('space', '')
                    use_custom_mcp = True
                    confluence_api_token_available = True
                    atlassian_configured = True
                
                # Add custom MCP server command if API tokens are being used
                if use_custom_mcp:
                    # Get the path to the custom MCP server script
                    import pathlib
                    custom_mcp_path = pathlib.Path(__file__).parent / "custom_mcp_atlassian.py"
                    
                    if custom_mcp_path.exists():
                        # Use Python to run the custom MCP server (stdio-based)
                        # MultiMCPTools expects a command string that can be executed
                        # Format: "python /path/to/script.py" or use StdioServerParameters
                        import sys
                        python_exec = sys.executable
                        custom_mcp_abs_path = str(custom_mcp_path.absolute())
                        
                        # Create command string for MultiMCPTools
                        # MultiMCPTools expects command strings that can be executed
                        # Format: "python /path/to/script.py" (space-separated)
                        server_cmd = f"{python_exec} {custom_mcp_abs_path}"
                        
                        # Add to servers list - MultiMCPTools will handle execution
                        self._servers.append(server_cmd)
                        self._active_servers["atlassian_custom"] = {
                            "type": "stdio",
                            "command": server_cmd,
                            "official": False,
                            "description": "Custom MCP server for Atlassian using API tokens",
                            "auth_method": "api_token"
                        }
                        logger.info("✅ Custom Atlassian MCP server configured (API token authentication)")
                        logger.info(f"   Server command: {server_cmd}")
                        logger.info(f"   Jira: {'✅' if jira_api_token_available else '❌'}, Confluence: {'✅' if confluence_api_token_available else '❌'}")
                    else:
                        logger.warning(f"Custom MCP server script not found at {custom_mcp_path}")
                        logger.info("⚠️ Falling back to direct API tools (MCP wrapper not available)")
        
        # Note: Atlassian Remote MCP Server uses SSE (Server-Sent Events), not stdio
        # SSE connections are handled differently and may require additional MCP client support
        
        # Amazon Q Developer MCP Server
        if amazon_q_config and amazon_q_config.get('app_id'):
            self._env['AWS_REGION'] = amazon_q_config.get('region', 'us-east-1')
            self._env['AWS_ACCESS_KEY_ID'] = amazon_q_config.get('access_key_id', '')
            self._env['AWS_SECRET_ACCESS_KEY'] = amazon_q_config.get('secret_access_key', '')
            self._env['AMAZON_Q_APP_ID'] = amazon_q_config.get('app_id', '')
            
            server_cmd = KNOWN_MCP_SERVERS.get("amazon_q", {}).get("npx")
            if server_cmd:
                self._servers.append(server_cmd)
                self._active_servers["amazon_q"] = server_cmd
                logger.info("Amazon Q Developer MCP server configured")
            else:
                logger.warning("Amazon Q Developer MCP server package not found")
        
        # Custom MCP Servers
        if custom_servers:
            for custom_server in custom_servers:
                server_name = custom_server.get('name', 'custom')
                server_cmd = custom_server.get('command')
                custom_env = custom_server.get('env', {})
                
                if server_cmd:
                    # Merge custom environment variables
                    self._env.update(custom_env)
                    self._servers.append(server_cmd)
                    self._active_servers[server_name] = server_cmd
                    logger.info(f"Custom MCP server '{server_name}' configured: {server_cmd}")
        
        # Initialize MCP tools if we have any servers
        # Note: SSE-based servers (like Atlassian) need special handling
        if self._servers:
            try:
                # For stdio-based servers (GitHub, Slack, etc.)
                self.mcp_tools = MultiMCPTools(self._servers, env=self._env)
                await self.mcp_tools.connect()
                self._initialized = True
                logger.info(f"Successfully initialized MCP with {len(self._servers)} stdio servers: {list(self._active_servers.keys())}")
            except Exception as e:
                logger.error(f"Failed to initialize MCP: {e}")
                self._initialized = False
                raise
        elif atlassian_configured and atlassian_access_token:
            # Atlassian Remote MCP Server (SSE) - handled separately
            # The actual connection will be made when needed
            logger.info("Atlassian Remote MCP Server configured (SSE-based, will connect on demand)")
            self._initialized = True
        else:
            logger.warning("No MCP servers configured")
            self._initialized = False
    
    async def close(self):
        """Close MCP connections"""
        if self.mcp_tools:
            try:
                await self.mcp_tools.close()
            except Exception as e:
                logger.error(f"Error closing MCP connection: {e}")
        self._initialized = False
        self._active_servers = {}
    
    def is_initialized(self) -> bool:
        """Check if MCP is initialized"""
        return self._initialized and self.mcp_tools is not None
    
    def get_tools(self):
        """Get MCP tools instance"""
        return self.mcp_tools
    
    def get_env(self) -> Dict:
        """Get environment variables for MCP servers"""
        return self._env.copy()
    
    def get_active_servers(self) -> Dict[str, str]:
        """Get list of active MCP servers"""
        return self._active_servers.copy()
    
    def add_custom_server(self, name: str, command: str, env_vars: Optional[Dict] = None):
        """
        Add a custom MCP server dynamically
        
        Args:
            name: Server identifier
            command: MCP server command (e.g., "npx -y @package/server")
            env_vars: Environment variables for the server
        """
        if env_vars:
            self._env.update(env_vars)
        
        if command not in self._servers:
            self._servers.append(command)
            self._active_servers[name] = command
            logger.info(f"Added custom MCP server '{name}': {command}")


class MCPToolsWrapper:
    """Synchronous wrapper for async MCP operations"""
    
    def __init__(self):
        self.manager = MCPIntegrationManager()
        self._loop = None
    
    def _get_loop(self):
        """Get or create event loop"""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            return loop
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop
    
    def initialize(self, 
                  jira_config: Optional[Dict] = None,
                  confluence_config: Optional[Dict] = None,
                  github_config: Optional[Dict] = None,
                  slack_config: Optional[Dict] = None,
                  amazon_q_config: Optional[Dict] = None,
                  custom_servers: Optional[List[Dict]] = None):
        """Initialize MCP connections (synchronous wrapper)"""
        loop = self._get_loop()
        try:
            loop.run_until_complete(
                self.manager.initialize(
                    jira_config, confluence_config, github_config,
                    slack_config, amazon_q_config, custom_servers
                )
            )
        except Exception as e:
            logger.error(f"Error initializing MCP: {e}")
            raise
    
    def close(self):
        """Close MCP connections (synchronous wrapper)"""
        if self.manager.is_initialized():
            loop = self._get_loop()
            try:
                loop.run_until_complete(self.manager.close())
            except Exception as e:
                logger.error(f"Error closing MCP: {e}")
    
    def is_initialized(self) -> bool:
        """Check if initialized"""
        return self.manager.is_initialized()
    
    def get_tools(self):
        """Get MCP tools"""
        return self.manager.get_tools()
    
    def get_env(self) -> Dict:
        """Get environment variables"""
        return self.manager.get_env()
    
    def get_active_servers(self) -> Dict[str, str]:
        """Get active MCP servers"""
        return self.manager.get_active_servers()
    
    def add_custom_server(self, name: str, command: str, env_vars: Optional[Dict] = None):
        """Add custom MCP server dynamically"""
        self.manager.add_custom_server(name, command, env_vars)


def get_available_mcp_servers() -> Dict[str, Dict]:
    """Get list of known MCP servers and their configurations (November 2025)"""
    return KNOWN_MCP_SERVERS.copy()


def get_atlassian_oauth_info() -> Dict:
    """
    Get information about Atlassian OAuth 2.0 setup for Remote MCP Server
    
    Returns:
        Dictionary with OAuth setup information
    """
    return {
        "endpoint": "https://mcp.atlassian.com/v1/sse",
        "auth_type": "OAuth 2.0",
        "authorization_url": "https://auth.atlassian.com/authorize",
        "token_url": "https://auth.atlassian.com/oauth/token",
        "documentation": "https://www.atlassian.com/platform/remote-mcp-server",
        "github_repo": "https://github.com/atlassian/atlassian-mcp-server",
        "scopes": [
            "read:jira-work",
            "write:jira-work",
            "read:confluence-content.all",
            "write:confluence-content.all",
            "read:confluence-space.summary"
        ],
        "setup_steps": [
            "1. Create an OAuth 2.0 app in Atlassian Developer Console",
            "2. Set redirect URI (e.g., http://localhost:8080/callback)",
            "3. Copy Client ID and Client Secret",
            "4. Initiate OAuth flow to get authorization code",
            "5. Exchange authorization code for access token",
            "6. Use access token with Atlassian Remote MCP Server"
        ]
    }


def create_mcp_server_config(server_type: str, config: Dict) -> Optional[str]:
    """
    Create MCP server command for a given server type
    
    Args:
        server_type: Type of server (github, slack, atlassian, amazon_q, etc.)
        config: Configuration dictionary for the server
    
    Returns:
        MCP server command string or None if not available
    """
    server_info = KNOWN_MCP_SERVERS.get(server_type)
    if not server_info:
        logger.warning(f"Unknown MCP server type: {server_type}")
        return None
    
    return server_info.get("npx") or server_info.get("docker")


def validate_mcp_config(server_type: str, config: Dict) -> tuple[bool, Optional[str]]:
    """
    Validate MCP server configuration
    
    Returns:
        (is_valid, error_message)
    """
    server_info = KNOWN_MCP_SERVERS.get(server_type)
    if not server_info:
        return False, f"Unknown server type: {server_type}"
    
    required_env = server_info.get("env_vars", [])
    missing = [var for var in required_env if not config.get(var.lower().replace('_', '_'))]
    
    if missing:
        return False, f"Missing required configuration: {', '.join(missing)}"
    
    return True, None
