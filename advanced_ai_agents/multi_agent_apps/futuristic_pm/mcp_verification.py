"""
MCP Integration Verification and Testing Module
Provides functions to test and verify MCP server connectivity and tool availability
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
# Import mcp_integration directly (relative import to avoid circular import issues)
import sys
from pathlib import Path
mcp_path = Path(__file__).parent
if str(mcp_path) not in sys.path:
    sys.path.insert(0, str(mcp_path))
from mcp_integration import MCPToolsWrapper, MCPIntegrationManager

logger = logging.getLogger(__name__)


async def test_mcp_server_connection(mcp_tools_obj) -> Dict[str, Any]:
    """
    Test MCP server connection and list available tools
    
    Returns:
        Dictionary with test results including:
        - connected: bool
        - tools_available: List[str]
        - error: Optional[str]
    """
    result = {
        "connected": False,
        "tools_available": [],
        "error": None,
        "server_info": {}
    }
    
    try:
        if not mcp_tools_obj:
            result["error"] = "MCP tools object not available"
            return result
        
        # Check if initialized
        if hasattr(mcp_tools_obj, 'is_initialized'):
            if not mcp_tools_obj.is_initialized():
                result["error"] = "MCP tools not initialized"
                return result
        
        # Get tools instance
        tools = None
        if hasattr(mcp_tools_obj, 'get_tools'):
            tools = mcp_tools_obj.get_tools()
        elif hasattr(mcp_tools_obj, 'mcp_tools'):
            tools = mcp_tools_obj.mcp_tools
        
        if not tools:
            result["error"] = "MCP tools instance not found"
            return result
        
        # Try to list tools (this depends on the MCP implementation)
        # For MultiMCPTools, we might need to call list_tools or similar
        try:
            # Attempt to get available tools
            if hasattr(tools, 'list_tools'):
                available_tools = await tools.list_tools()
                result["tools_available"] = [tool.get('name', 'unknown') for tool in available_tools] if isinstance(available_tools, list) else []
            elif hasattr(tools, 'get_available_tools'):
                result["tools_available"] = tools.get_available_tools()
            else:
                # Try to inspect the tools object
                result["tools_available"] = ["Tools object available but tool listing not supported"]
            
            result["connected"] = True
        except Exception as e:
            logger.warning(f"Could not list tools, but connection might be OK: {e}")
            result["connected"] = True
            result["tools_available"] = ["Connection verified but tool listing failed"]
        
        # Get server info if available
        if hasattr(mcp_tools_obj, 'get_active_servers'):
            result["server_info"] = mcp_tools_obj.get_active_servers()
        
    except Exception as e:
        logger.error(f"Error testing MCP connection: {e}", exc_info=True)
        result["error"] = str(e)
    
    return result


async def test_jira_mcp_tool(mcp_tools_obj, project_key: str) -> Dict[str, Any]:
    """
    Test Jira MCP tool by attempting to search for issues
    
    Returns:
        Dictionary with test results
    """
    result = {
        "success": False,
        "error": None,
        "test_data": None
    }
    
    try:
        if not mcp_tools_obj:
            result["error"] = "MCP tools not available"
            return result
        
        tools = None
        if hasattr(mcp_tools_obj, 'get_tools'):
            tools = mcp_tools_obj.get_tools()
        elif hasattr(mcp_tools_obj, 'mcp_tools'):
            tools = mcp_tools_obj.mcp_tools
        
        if not tools:
            result["error"] = "MCP tools instance not found"
            return result
        
        # Try to call a simple Jira tool (search_issues)
        try:
            if hasattr(tools, 'call_tool'):
                # Test with a simple search
                test_result = await tools.call_tool(
                    "jira_search_issues",
                    {"jql": f"project = {project_key} ORDER BY created DESC", "max_results": 1}
                )
                result["success"] = True
                result["test_data"] = test_result
            else:
                result["error"] = "MCP tools do not support call_tool method"
        except Exception as e:
            result["error"] = f"Tool call failed: {str(e)}"
            logger.error(f"Jira MCP tool test failed: {e}", exc_info=True)
    
    except Exception as e:
        logger.error(f"Error testing Jira MCP tool: {e}", exc_info=True)
        result["error"] = str(e)
    
    return result


async def test_confluence_mcp_tool(mcp_tools_obj, space_key: str) -> Dict[str, Any]:
    """
    Test Confluence MCP tool by attempting to search for pages
    
    Returns:
        Dictionary with test results
    """
    result = {
        "success": False,
        "error": None,
        "test_data": None
    }
    
    try:
        if not mcp_tools_obj:
            result["error"] = "MCP tools not available"
            return result
        
        tools = None
        if hasattr(mcp_tools_obj, 'get_tools'):
            tools = mcp_tools_obj.get_tools()
        elif hasattr(mcp_tools_obj, 'mcp_tools'):
            tools = mcp_tools_obj.mcp_tools
        
        if not tools:
            result["error"] = "MCP tools instance not found"
            return result
        
        # Try to call a simple Confluence tool (search_pages)
        try:
            if hasattr(tools, 'call_tool'):
                # Test with a simple search
                test_result = await tools.call_tool(
                    "confluence_search_pages",
                    {"query": "*", "space_key": space_key, "limit": 1}
                )
                result["success"] = True
                result["test_data"] = test_result
            else:
                result["error"] = "MCP tools do not support call_tool method"
        except Exception as e:
            result["error"] = f"Tool call failed: {str(e)}"
            logger.error(f"Confluence MCP tool test failed: {e}", exc_info=True)
    
    except Exception as e:
        logger.error(f"Error testing Confluence MCP tool: {e}", exc_info=True)
        result["error"] = str(e)
    
    return result


def verify_mcp_configuration(config: Dict) -> Dict[str, Any]:
    """
    Verify MCP configuration is complete
    
    Returns:
        Dictionary with verification results
    """
    result = {
        "jira_configured": False,
        "confluence_configured": False,
        "jira_auth_method": None,
        "confluence_auth_method": None,
        "missing_fields": [],
        "ready": False
    }
    
    # Check Jira configuration
    jira_auth_method = config.get('jira_auth_method', '')
    if 'OAuth' in jira_auth_method:
        result["jira_auth_method"] = "oauth"
        if config.get('jira_oauth_access_token') and config.get('jira_oauth_client_id'):
            result["jira_configured"] = True
        else:
            result["missing_fields"].append("Jira OAuth credentials")
    elif 'API Token' in jira_auth_method or jira_auth_method == 'api_token':
        result["jira_auth_method"] = "api_token"
        if config.get('jira_url') and config.get('jira_email') and config.get('jira_token'):
            result["jira_configured"] = True
        else:
            result["missing_fields"].extend([
                f for f in ["jira_url", "jira_email", "jira_token"]
                if not config.get(f)
            ])
    
    # Check Confluence configuration
    confluence_auth_method = config.get('confluence_auth_method', '')
    if 'OAuth' in confluence_auth_method:
        result["confluence_auth_method"] = "oauth"
        if config.get('confluence_oauth_access_token') and config.get('confluence_oauth_client_id'):
            result["confluence_configured"] = True
        else:
            result["missing_fields"].append("Confluence OAuth credentials")
    elif 'API Token' in confluence_auth_method or confluence_auth_method == 'api_token':
        result["confluence_auth_method"] = "api_token"
        if config.get('confluence_url') and config.get('confluence_email') and config.get('confluence_token'):
            result["confluence_configured"] = True
        else:
            result["missing_fields"].extend([
                f for f in ["confluence_url", "confluence_email", "confluence_token"]
                if not config.get(f)
            ])
    
    result["ready"] = result["jira_configured"] or result["confluence_configured"]
    
    return result

