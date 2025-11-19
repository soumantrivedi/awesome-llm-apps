"""
Cloudability MCP Server - Main Entry Point
Framework-based MCP server with extensible tool registry
"""

import json
import sys
import asyncio
import logging
from typing import Dict, List, Optional, Any

from .config import Config
from .api_client import CloudabilityAPIClient
from .api_client_extended import ExtendedCloudabilityAPIClient
from .framework.tool_base import get_registry
from .utils import export_to_csv, export_to_json, get_default_date_range
from .tool_status import get_tool_status, ToolStatus

# Import all tools to trigger registration
from . import tools  # noqa: F401

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# MCP Protocol Constants
MCP_VERSION = Config.MCP_VERSION


class CloudabilityMCPServer:
    """
    MCP Server for IBM Cloudability API
    Framework-based implementation with tool registry pattern
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        auth_type: Optional[str] = None,
        public_key: Optional[str] = None,
        private_key: Optional[str] = None,
        environment_id: Optional[str] = None,
        frontdoor_url: Optional[str] = None
    ):
        """
        Initialize Cloudability MCP Server
        
        Args:
            api_key: Cloudability API key (for basic/bearer auth)
            base_url: Base URL for API
            auth_type: Authentication type ('basic', 'bearer', or 'opentoken')
            public_key: Public key (keyAccess) for Enhanced Access Administration
            private_key: Private key (keySecret) for Enhanced Access Administration
            environment_id: Environment ID for OpenToken auth
            frontdoor_url: Frontdoor URL for key pair authentication
        """
        Config.validate()
        
        # Use extended API client for comprehensive features
        self.api_client = ExtendedCloudabilityAPIClient(
            api_key=api_key,
            base_url=base_url,
            auth_type=auth_type,
            public_key=public_key,
            private_key=private_key,
            environment_id=environment_id,
            frontdoor_url=frontdoor_url
        )
        
        # Get tool registry and set API client for all tools
        self.registry = get_registry()
        self._initialize_tools()
        
        self.initialized = False
    
    def _initialize_tools(self):
        """Initialize all tools with API client"""
        for tool_name in self.registry.list_tools():
            tool = self.registry.get_tool(tool_name)
            if tool:
                tool.set_api_client(self.api_client)
    
    def get_tools(self) -> List[Dict]:
        """
        Get list of available MCP tools from registry
        
        Returns:
            List of tool definitions
        """
        # Get all tool definitions from registry
        return self.registry.get_all_definitions()
    
    async def handle_request(self, request: Dict) -> Optional[Dict]:
        """
        Handle MCP protocol request
        
        Args:
            request: JSON-RPC request dictionary
            
        Returns:
            JSON-RPC response or None for notifications
        """
        request_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})
        is_notification = request_id is None
        
        try:
            if method == "initialize":
                self.initialized = True
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": MCP_VERSION,
                        "capabilities": {
                            "tools": {}
                        },
                        "serverInfo": {
                            "name": "cloudability-mcp-server",
                            "version": "3.0.0",
                            "tools_count": len(self.registry.list_tools())
                        }
                    }
                }
            
            elif method == "tools/list":
                tools = self.get_tools()
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "tools": tools
                    }
                }
            
            elif method == "tools/call":
                tool_name = params.get("name")
                if not tool_name:
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {
                            "code": -32602,
                            "message": "Invalid params: tool name is required"
                        }
                    }
                
                arguments = params.get("arguments", {})
                result = await self.call_tool(tool_name, arguments)
                
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(result, indent=2, default=str)
                            }
                        ]
                    }
                }
            
            else:
                if is_notification:
                    return None
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
        
        except Exception as e:
            logger.error(f"Error handling request: {e}", exc_info=True)
            if is_notification:
                return None
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": "Internal error",
                    "data": str(e)
                }
            }
    
    async def call_tool(self, tool_name: str, arguments: Dict) -> Dict:
        """
        Call a specific tool with arguments using registry
        
        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments
            
        Returns:
            Tool execution result
        """
        try:
            # Check tool status
            tool_status = get_tool_status(tool_name)
            
            if tool_status == ToolStatus.NOT_AVAILABLE:
                return {
                    "success": False,
                    "error": f"Tool '{tool_name}' is not available. The API endpoint may not exist in Cloudability API v3.",
                    "status": "not_available",
                    "tool": tool_name,
                    "suggestion": "Check Cloudability API v3 documentation for alternative endpoints. Use 'list_views' or 'list_budgets' for verified working tools."
                }
            
            if tool_status == ToolStatus.EXPERIMENTAL:
                logger.info(f"Tool '{tool_name}' is experimental - attempting API call with current parameters.")
            
            # Get tool from registry
            tool = self.registry.get_tool(tool_name)
            if not tool:
                raise ValueError(f"Unknown tool: {tool_name}")
            
            # Validate arguments
            validation_error = tool.validate_args(arguments)
            if validation_error:
                return {
                    "success": False,
                    "error": validation_error,
                    "tool": tool_name
                }
            
            # Execute tool
            result = await tool.execute(arguments)
            
            # Add tool status to result for transparency
            if "status" not in result:
                result["tool_status"] = tool_status.value
            
            # Handle CSV export if needed
            export_format = arguments.get("export_format") or result.get("export_format")
            if result.get("success") and export_format == "csv":
                csv_data = result.get("csv_data")
                if csv_data:
                    file_name = arguments.get("file_name")
                    if not file_name:
                        # Generate default file name
                        report_type = result.get("report_type", tool_name)
                        start_date = result.get("start_date") or arguments.get("start_date", "unknown")
                        end_date = result.get("end_date") or arguments.get("end_date", "unknown")
                        file_name = f"{report_type}_{start_date}_to_{end_date}"
                    
                    file_path = f"{file_name}.csv"
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(csv_data)
                    result["export_path"] = file_path
                    result["export_format"] = "csv"
                    logger.info(f"Exported CSV to {file_path}")
            
            # Handle JSON export if requested
            if result.get("success") and export_format == "json" and arguments.get("file_name"):
                from .utils import export_to_json
                data = result.get("data", [])
                if data:
                    file_path = export_to_json(data, f"{arguments.get('file_name')}.json")
                    result["export_path"] = file_path
                    result["export_format"] = "json"
                    logger.info(f"Exported JSON to {file_path}")
            
            return result
        
        except Exception as e:
            logger.error(f"Error calling tool {tool_name}: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "tool": tool_name
            }


async def main():
    """Main entry point for MCP server"""
    # Get authentication credentials from environment
    # Support both legacy API key and Enhanced Access Administration (public/private key)
    api_key = Config.API_KEY
    public_key = Config.PUBLIC_KEY
    private_key = Config.PRIVATE_KEY
    base_url = Config.BASE_URL
    auth_type = Config.AUTH_TYPE
    environment_id = Config.ENVIRONMENT_ID
    frontdoor_url = Config.FRONTDOOR_URL
    
    # Validate configuration - Config.validate() will check for required credentials
    try:
        Config.validate()
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)
    
    # Initialize server with appropriate authentication
    server = CloudabilityMCPServer(
        api_key=api_key,
        base_url=base_url,
        auth_type=auth_type,
        public_key=public_key,
        private_key=private_key,
        environment_id=environment_id,
        frontdoor_url=frontdoor_url
    )
    
    # Read from stdin, write to stdout
    for line in sys.stdin:
        try:
            request = json.loads(line.strip())
            response = await server.handle_request(request)
            if response:
                print(json.dumps(response))
                sys.stdout.flush()
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON: {e}")
        except Exception as e:
            logger.error(f"Error: {e}", exc_info=True)


if __name__ == "__main__":
    asyncio.run(main())

