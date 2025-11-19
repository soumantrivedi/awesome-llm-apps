"""
MCP Wrapper for Custom Atlassian MCP Server
Provides a synchronous wrapper for the custom MCP server that uses API tokens
"""

import asyncio
import logging
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from mcp import StdioServerParameters

logger = logging.getLogger(__name__)

# Try to import MCP tools
try:
    from agno.tools.mcp import MCPTools
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    MCPTools = None
    logger.warning("MCP tools not available. Install: pip install agno mcp")


class CustomAtlassianMCPWrapper:
    """
    Wrapper for custom Atlassian MCP server using API tokens
    Provides MCP-compatible interface for Jira and Confluence
    """
    
    def __init__(self, jira_config: Optional[Dict] = None, confluence_config: Optional[Dict] = None):
        """
        Initialize custom Atlassian MCP wrapper
        
        Args:
            jira_config: Jira configuration with url, email, token, project_key, board_id
            confluence_config: Confluence configuration with url, email, token, space
        """
        self.jira_config = jira_config
        self.confluence_config = confluence_config
        self.mcp_tools = None
        self._initialized = False
    
    async def initialize(self):
        """Initialize the custom MCP server connection"""
        if not MCP_AVAILABLE:
            raise ImportError("MCP tools not available. Install: pip install agno mcp")
        
        # Get path to custom MCP server script
        custom_mcp_path = Path(__file__).parent / "custom_mcp_atlassian.py"
        
        if not custom_mcp_path.exists():
            raise FileNotFoundError(f"Custom MCP server script not found at {custom_mcp_path}")
        
        # Prepare environment variables
        env = {}
        if self.jira_config:
            env['JIRA_URL'] = self.jira_config.get('url', '')
            env['JIRA_EMAIL'] = self.jira_config.get('email', '')
            env['JIRA_API_TOKEN'] = self.jira_config.get('token', '')
            env['JIRA_PROJECT_KEY'] = self.jira_config.get('project_key', '')
            env['JIRA_BOARD_ID'] = str(self.jira_config.get('board_id', '0'))
        
        if self.confluence_config:
            env['CONFLUENCE_URL'] = self.confluence_config.get('url', '')
            env['CONFLUENCE_EMAIL'] = self.confluence_config.get('email', '')
            env['CONFLUENCE_API_TOKEN'] = self.confluence_config.get('token', '')
            env['CONFLUENCE_SPACE'] = self.confluence_config.get('space', '')
        
        # Create stdio server parameters
        server_params = StdioServerParameters(
            command=sys.executable,
            args=[str(custom_mcp_path.absolute())],
            env=env
        )
        
        try:
            # Initialize MCP tools
            self.mcp_tools = MCPTools(server_params=server_params)
            await self.mcp_tools.connect()
            self._initialized = True
            logger.info("✅ Custom Atlassian MCP server connected successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize custom Atlassian MCP server: {e}")
            self._initialized = False
            raise
    
    async def close(self):
        """Close MCP connection"""
        if self.mcp_tools:
            try:
                await self.mcp_tools.close()
            except Exception as e:
                logger.error(f"Error closing MCP connection: {e}")
    
    def is_initialized(self) -> bool:
        """Check if MCP server is initialized"""
        return self._initialized
    
    async def call_tool(self, tool_name: str, arguments: Dict) -> Dict:
        """Call a tool on the MCP server"""
        if not self._initialized:
            raise RuntimeError("MCP server not initialized. Call initialize() first.")
        
        try:
            result = await self.mcp_tools.call_tool(tool_name, arguments)
            return result
        except Exception as e:
            logger.error(f"Error calling tool {tool_name}: {e}")
            raise
    
    def get_available_tools(self) -> List[str]:
        """Get list of available tool names"""
        if not self._initialized or not self.mcp_tools:
            return []
        
        try:
            # Get tools from MCP server
            # This would need to be implemented based on MCPTools API
            tools = []
            if self.jira_config:
                tools.extend([
                    "jira_create_story", "jira_create_epic", "jira_create_release",
                    "jira_get_issue", "jira_add_comment", "jira_update_issue",
                    "jira_search_issues", "jira_create_sprint"
                ])
            if self.confluence_config:
                tools.extend([
                    "confluence_create_page", "confluence_update_page", "confluence_get_page",
                    "confluence_search_pages", "confluence_get_comments", "confluence_add_comment"
                ])
            return tools
        except Exception as e:
            logger.error(f"Error getting available tools: {e}")
            return []


# Synchronous wrapper for use in Streamlit
class CustomAtlassianMCPWrapperSync:
    """
    Synchronous wrapper for CustomAtlassianMCPWrapper
    For use in non-async contexts like Streamlit
    """
    
    def __init__(self, jira_config: Optional[Dict] = None, confluence_config: Optional[Dict] = None):
        self._wrapper = CustomAtlassianMCPWrapper(jira_config, confluence_config)
        self._loop = None
    
    def _get_loop(self):
        """Get or create event loop"""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        return loop
    
    def initialize(self):
        """Initialize MCP server (synchronous)"""
        loop = self._get_loop()
        return loop.run_until_complete(self._wrapper.initialize())
    
    def close(self):
        """Close MCP connection (synchronous)"""
        if self._wrapper:
            loop = self._get_loop()
            loop.run_until_complete(self._wrapper.close())
    
    def is_initialized(self) -> bool:
        """Check if initialized"""
        return self._wrapper.is_initialized()
    
    def call_tool(self, tool_name: str, arguments: Dict) -> Dict:
        """Call a tool (synchronous)"""
        loop = self._get_loop()
        return loop.run_until_complete(self._wrapper.call_tool(tool_name, arguments))
    
    def get_available_tools(self) -> List[str]:
        """Get available tools"""
        return self._wrapper.get_available_tools()

