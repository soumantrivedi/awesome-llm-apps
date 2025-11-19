#!/usr/bin/env python3
"""
Cloudability MCP Server
A simple MCP server for extracting cost reports from IBM Cloudability API.

This server provides tools to:
- Get cost reports by dashboard view name
- Filter reports by product_id (e.g., Kubernetes/K8s)
- Retrieve cost data with various filters

MCP Protocol: stdio-based communication
"""

import json
import sys
import os
import asyncio
import logging
from typing import Dict, List, Optional, Any
from urllib.parse import urlencode
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# MCP Protocol Constants
MCP_VERSION = "2024-11-05"


class CloudabilityMCPServer:
    """
    MCP Server for IBM Cloudability API
    Implements MCP protocol over stdio following official MCP standards
    """
    
    def __init__(self, api_key: str, base_url: str = "https://api.cloudability.com/v3"):
        """
        Initialize Cloudability MCP Server
        
        Args:
            api_key: Cloudability API key for authentication
            base_url: Base URL for Cloudability API (default: https://api.cloudability.com/v3)
                     For EU: https://api-eu.cloudability.com/v3
                     For APAC: https://api-au.cloudability.com/v3
                     For ME: https://api-me.cloudability.com/v3
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.auth = HTTPBasicAuth(api_key, '')
        self.initialized = False
        
        if not api_key:
            raise ValueError("Cloudability API key is required")
    
    def get_tools(self) -> List[Dict]:
        """
        Return list of available MCP tools
        
        Returns:
            List of tool definitions following MCP protocol
        """
        return [
            {
                "name": "get_cost_report_by_view",
                "description": "Get cost report data for a specific dashboard view name. Returns cost data including metrics, dimensions, and time series data.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "view_name": {
                            "type": "string",
                            "description": "Name of the dashboard view to retrieve cost data from (e.g., 'AWS Cost Overview', 'Kubernetes Costs')"
                        },
                        "product_id": {
                            "type": "string",
                            "description": "Optional: Filter by product ID (e.g., 'K8s' for Kubernetes, 'EC2' for EC2 instances). Leave empty to get all products."
                        },
                        "start_date": {
                            "type": "string",
                            "description": "Optional: Start date for the report in YYYY-MM-DD format. Defaults to last 30 days if not provided."
                        },
                        "end_date": {
                            "type": "string",
                            "description": "Optional: End date for the report in YYYY-MM-DD format. Defaults to today if not provided."
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Optional: Maximum number of records to return (default: 50, max: 250)"
                        },
                        "offset": {
                            "type": "integer",
                            "description": "Optional: Offset for pagination (default: 0)"
                        }
                    },
                    "required": ["view_name"]
                }
            },
            {
                "name": "list_views",
                "description": "List all available dashboard views in Cloudability. Use this to discover view names before querying cost reports.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "Optional: Maximum number of views to return (default: 50)"
                        },
                        "offset": {
                            "type": "integer",
                            "description": "Optional: Offset for pagination (default: 0)"
                        }
                    }
                }
            },
            {
                "name": "get_cost_report_with_filters",
                "description": "Get cost report with advanced filtering options. Supports multiple filter conditions and custom dimensions.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "view_name": {
                            "type": "string",
                            "description": "Name of the dashboard view to retrieve cost data from"
                        },
                        "filters": {
                            "type": "object",
                            "description": "Filter conditions as key-value pairs. Common filters: product_id, vendor, service, account_id, etc.",
                            "additionalProperties": {
                                "type": "string"
                            }
                        },
                        "dimensions": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Optional: List of dimensions to group by (e.g., ['product_id', 'vendor', 'service'])"
                        },
                        "metrics": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Optional: List of metrics to retrieve (e.g., ['cost', 'usage'])"
                        },
                        "start_date": {
                            "type": "string",
                            "description": "Optional: Start date in YYYY-MM-DD format"
                        },
                        "end_date": {
                            "type": "string",
                            "description": "Optional: End date in YYYY-MM-DD format"
                        }
                    },
                    "required": ["view_name"]
                }
            },
            {
                "name": "get_amortized_costs",
                "description": "Get amortized cost data from TrueCost Explorer. Amortized costs spread upfront payments (like Reserved Instances) over their term, providing a more accurate view of daily/monthly costs. Use this to see true cost allocation over time.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "start_date": {
                            "type": "string",
                            "description": "Start date for the report in YYYY-MM-DD format (e.g., '2024-01-01'). Defaults to last 30 days if not provided."
                        },
                        "end_date": {
                            "type": "string",
                            "description": "End date for the report in YYYY-MM-DD format (e.g., '2024-01-31'). Defaults to today if not provided."
                        },
                        "filters": {
                            "type": "object",
                            "description": "Optional filter conditions as key-value pairs. Common filters: vendor (AWS/Azure/GCP), service (EC2/S3/etc), account_id, region, product_id. Example: {'vendor': 'AWS', 'service': 'EC2'}",
                            "additionalProperties": {
                                "type": "string"
                            }
                        },
                        "dimensions": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Optional: Dimensions to group by (e.g., ['vendor', 'service', 'account_id', 'region']). Defaults to ['vendor', 'service'] if not provided."
                        },
                        "export_format": {
                            "type": "string",
                            "enum": ["json", "csv"],
                            "description": "Export format for the report. Use 'json' for programmatic access or 'csv' for spreadsheet analysis. Default: 'json'"
                        }
                    }
                }
            },
            {
                "name": "get_container_costs",
                "description": "Get container-wise cost breakdown from TrueCost Explorer. This splits costs by container/pod level, showing Kubernetes or containerized workload costs. Perfect for understanding container resource consumption and cost allocation.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "start_date": {
                            "type": "string",
                            "description": "Start date for the report in YYYY-MM-DD format (e.g., '2024-01-01'). Defaults to last 30 days if not provided."
                        },
                        "end_date": {
                            "type": "string",
                            "description": "End date for the report in YYYY-MM-DD format (e.g., '2024-01-31'). Defaults to today if not provided."
                        },
                        "filters": {
                            "type": "object",
                            "description": "Optional filter conditions. Common filters: cluster_name, namespace, pod_name, container_name, product_id (e.g., 'K8s'). Example: {'cluster_name': 'prod-cluster', 'namespace': 'default'}",
                            "additionalProperties": {
                                "type": "string"
                            }
                        },
                        "group_by": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Optional: How to group container costs. Options: ['cluster', 'namespace', 'pod', 'container', 'service']. Default: ['cluster', 'namespace']"
                        },
                        "export_format": {
                            "type": "string",
                            "enum": ["json", "csv"],
                            "description": "Export format: 'json' or 'csv'. Default: 'json'"
                        }
                    }
                }
            },
            {
                "name": "explore_tags",
                "description": "Explore costs by tags from TrueCost Explorer. Tag explorer helps you analyze costs based on custom tags (like Environment, Team, Project, etc.). Use this to understand cost allocation by business dimensions.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "tag_key": {
                            "type": "string",
                            "description": "The tag key to explore (e.g., 'Environment', 'Team', 'Project', 'CostCenter'). Use list_available_tags first to see available tag keys."
                        },
                        "tag_value": {
                            "type": "string",
                            "description": "Optional: Specific tag value to filter by (e.g., 'Production', 'Development'). Leave empty to see all values for the tag key."
                        },
                        "start_date": {
                            "type": "string",
                            "description": "Start date in YYYY-MM-DD format. Defaults to last 30 days if not provided."
                        },
                        "end_date": {
                            "type": "string",
                            "description": "End date in YYYY-MM-DD format. Defaults to today if not provided."
                        },
                        "additional_filters": {
                            "type": "object",
                            "description": "Optional: Additional filters to combine with tag filter (e.g., {'vendor': 'AWS', 'service': 'EC2'})",
                            "additionalProperties": {
                                "type": "string"
                            }
                        },
                        "export_format": {
                            "type": "string",
                            "enum": ["json", "csv"],
                            "description": "Export format: 'json' or 'csv'. Default: 'json'"
                        }
                    },
                    "required": ["tag_key"]
                }
            },
            {
                "name": "get_anomaly_detection",
                "description": "Get anomaly detection results from TrueCost Explorer. Identifies unusual spending patterns, cost spikes, or unexpected changes in cloud costs. Helps detect billing issues, resource leaks, or optimization opportunities.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "start_date": {
                            "type": "string",
                            "description": "Start date for anomaly detection in YYYY-MM-DD format. Defaults to last 30 days if not provided."
                        },
                        "end_date": {
                            "type": "string",
                            "description": "End date in YYYY-MM-DD format. Defaults to today if not provided."
                        },
                        "severity": {
                            "type": "string",
                            "enum": ["low", "medium", "high", "all"],
                            "description": "Filter anomalies by severity level. 'all' returns all anomalies. Default: 'all'"
                        },
                        "filters": {
                            "type": "object",
                            "description": "Optional: Filter anomalies by specific dimensions (e.g., {'vendor': 'AWS', 'account_id': '123456789'})",
                            "additionalProperties": {
                                "type": "string"
                            }
                        },
                        "min_cost_change_percent": {
                            "type": "number",
                            "description": "Optional: Minimum cost change percentage to consider as anomaly (e.g., 20.0 for 20% change). Default: 10.0"
                        },
                        "export_format": {
                            "type": "string",
                            "enum": ["json", "csv"],
                            "description": "Export format: 'json' or 'csv'. Default: 'json'"
                        }
                    }
                }
            },
            {
                "name": "list_available_tags",
                "description": "List all available tag keys in your Cloudability account. Use this before exploring tags to see what tag keys are available for cost analysis.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of tag keys to return (default: 100)"
                        }
                    }
                }
            },
            {
                "name": "export_cost_report",
                "description": "Export cost report with custom filters to JSON or CSV format. This is a flexible tool that allows you to create custom cost reports by specifying any filter keys and values you know. Perfect for creating tailored reports for specific analysis needs.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "start_date": {
                            "type": "string",
                            "description": "Start date in YYYY-MM-DD format (required)"
                        },
                        "end_date": {
                            "type": "string",
                            "description": "End date in YYYY-MM-DD format (required)"
                        },
                        "filters": {
                            "type": "object",
                            "description": "Filter conditions as key-value pairs. You can use any valid Cloudability filter key. Common keys: vendor, service, account_id, region, product_id, instance_type, etc. Example: {'vendor': 'AWS', 'service': 'EC2', 'region': 'us-east-1'}",
                            "additionalProperties": {
                                "type": "string"
                            }
                        },
                        "dimensions": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Dimensions to group by (e.g., ['vendor', 'service', 'account_id', 'region', 'instance_type'])"
                        },
                        "metrics": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Metrics to include (e.g., ['cost', 'usage', 'amortized_cost']). Default: ['cost']"
                        },
                        "export_format": {
                            "type": "string",
                            "enum": ["json", "csv"],
                            "description": "Export format: 'json' for programmatic use, 'csv' for spreadsheet analysis. Default: 'json'"
                        },
                        "file_name": {
                            "type": "string",
                            "description": "Optional: Custom file name for the export (without extension). If not provided, auto-generated based on filters and date range."
                        }
                    },
                    "required": ["start_date", "end_date"]
                }
            }
        ]
    
    async def handle_request(self, request: Dict) -> Optional[Dict]:
        """
        Handle MCP protocol request
        
        Args:
            request: JSON-RPC 2.0 request object
            
        Returns:
            JSON-RPC 2.0 response object, or None for notifications
        """
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")
        
        # Handle notifications (requests without id) - no response needed
        is_notification = "id" not in request
        
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
                            "version": "1.0.0"
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
                    return None  # No response for unknown notifications
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
                return None  # No response for notifications with errors
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
        Call a specific tool with arguments
        
        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments
            
        Returns:
            Tool execution result
        """
        try:
            if tool_name == "get_cost_report_by_view":
                return await self._get_cost_report_by_view(arguments)
            
            elif tool_name == "list_views":
                return await self._list_views(arguments)
            
            elif tool_name == "get_cost_report_with_filters":
                return await self._get_cost_report_with_filters(arguments)
            
            elif tool_name == "get_amortized_costs":
                return await self._get_amortized_costs(arguments)
            
            elif tool_name == "get_container_costs":
                return await self._get_container_costs(arguments)
            
            elif tool_name == "explore_tags":
                return await self._explore_tags(arguments)
            
            elif tool_name == "get_anomaly_detection":
                return await self._get_anomaly_detection(arguments)
            
            elif tool_name == "list_available_tags":
                return await self._list_available_tags(arguments)
            
            elif tool_name == "export_cost_report":
                return await self._export_cost_report(arguments)
            
            else:
                raise ValueError(f"Unknown tool: {tool_name}")
        
        except Exception as e:
            logger.error(f"Error calling tool {tool_name}: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "tool": tool_name
            }
    
    async def _get_cost_report_by_view(self, args: Dict) -> Dict:
        """
        Get cost report by view name with optional product_id filter
        
        Args:
            args: Arguments containing view_name, product_id, dates, pagination
            
        Returns:
            Cost report data
        """
        view_name = args.get("view_name")
        if not view_name:
            raise ValueError("view_name is required")
        
        # Build query parameters
        params = {}
        
        # Add product_id filter if provided
        product_id = args.get("product_id")
        if product_id:
            params["filter"] = f"product_id=={product_id}"
        
        # Add date filters if provided
        start_date = args.get("start_date")
        end_date = args.get("end_date")
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        
        # Add pagination
        limit = args.get("limit", 50)
        offset = args.get("offset", 0)
        params["limit"] = limit
        params["offset"] = offset
        
        # Make API request
        # Note: Cloudability API endpoint structure may vary
        # This is a generic implementation - adjust endpoint as needed
        url = f"{self.base_url}/views"
        
        try:
            # First, try to get views to find the view ID
            views_response = requests.get(
                f"{self.base_url}/views",
                auth=self.auth,
                headers={"Accept": "application/json"},
                params={"limit": 250}  # Get all views to find by name
            )
            views_response.raise_for_status()
            views_data = views_response.json()
            
            # Find view by name
            view_id = None
            if "result" in views_data:
                views = views_data["result"] if isinstance(views_data["result"], list) else []
                for view in views:
                    # Check title first (actual API field), then name, then displayName
                    if (view.get("title") == view_name or 
                        view.get("name") == view_name or 
                        view.get("displayName") == view_name):
                        view_id = view.get("id") or view.get("viewId")
                        break
            
            if not view_id:
                return {
                    "success": False,
                    "error": f"View '{view_name}' not found",
                    "available_views": [v.get("name") or v.get("displayName", "Unknown") for v in views]
                }
            
            # Get cost data for the view
            # Adjust endpoint based on actual Cloudability API structure
            cost_url = f"{self.base_url}/views/{view_id}/data"
            
            response = requests.get(
                cost_url,
                auth=self.auth,
                headers={"Accept": "application/json"},
                params=params
            )
            response.raise_for_status()
            data = response.json()
            
            return {
                "success": True,
                "view_name": view_name,
                "view_id": view_id,
                "filters": {
                    "product_id": product_id,
                    "start_date": start_date,
                    "end_date": end_date
                },
                "data": data
            }
        
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            return {
                "success": False,
                "error": f"API request failed: {str(e)}",
                "status_code": getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None
            }
    
    async def _list_views(self, args: Dict) -> Dict:
        """
        List all available views
        
        Args:
            args: Arguments containing pagination parameters
            
        Returns:
            List of available views
        """
        limit = args.get("limit", 50)
        offset = args.get("offset", 0)
        
        params = {
            "limit": limit,
            "offset": offset
        }
        
        try:
            response = requests.get(
                f"{self.base_url}/views",
                auth=self.auth,
                headers={"Accept": "application/json"},
                params=params
            )
            response.raise_for_status()
            data = response.json()
            
            # Extract view names for easier reference
            views = data.get("result", [])
            view_names = []
            for view in views:
                view_info = {
                    "id": view.get("id") or view.get("viewId"),
                    "name": view.get("title") or view.get("name") or view.get("displayName", "Unknown"),
                    "description": view.get("description", ""),
                    "ownerEmail": view.get("ownerEmail", ""),
                    "viewSource": view.get("viewSource", "")
                }
                view_names.append(view_info)
            
            return {
                "success": True,
                "total_views": len(views),
                "views": view_names,
                "raw_data": data
            }
        
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            return {
                "success": False,
                "error": f"API request failed: {str(e)}",
                "status_code": getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None
            }
    
    async def _get_cost_report_with_filters(self, args: Dict) -> Dict:
        """
        Get cost report with advanced filtering
        
        Args:
            args: Arguments containing view_name, filters, dimensions, metrics, dates
            
        Returns:
            Filtered cost report data
        """
        view_name = args.get("view_name")
        if not view_name:
            raise ValueError("view_name is required")
        
        # Build filter string from filters object
        filters = args.get("filters", {})
        filter_parts = []
        for key, value in filters.items():
            filter_parts.append(f"{key}=={value}")
        
        params = {}
        if filter_parts:
            params["filter"] = ",".join(filter_parts)
        
        # Add dimensions if provided
        dimensions = args.get("dimensions")
        if dimensions:
            params["dimensions"] = ",".join(dimensions)
        
        # Add metrics if provided
        metrics = args.get("metrics")
        if metrics:
            params["metrics"] = ",".join(metrics)
        
        # Add dates
        start_date = args.get("start_date")
        end_date = args.get("end_date")
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        
        try:
            # Find view ID by name (similar to _get_cost_report_by_view)
            views_response = requests.get(
                f"{self.base_url}/views",
                auth=self.auth,
                headers={"Accept": "application/json"},
                params={"limit": 250}
            )
            views_response.raise_for_status()
            views_data = views_response.json()
            
            view_id = None
            if "result" in views_data:
                views = views_data["result"] if isinstance(views_data["result"], list) else []
                for view in views:
                    # Check title first (actual API field), then name, then displayName
                    if (view.get("title") == view_name or 
                        view.get("name") == view_name or 
                        view.get("displayName") == view_name):
                        view_id = view.get("id") or view.get("viewId")
                        break
            
            if not view_id:
                return {
                    "success": False,
                    "error": f"View '{view_name}' not found"
                }
            
            # Get cost data
            cost_url = f"{self.base_url}/views/{view_id}/data"
            
            response = requests.get(
                cost_url,
                auth=self.auth,
                headers={"Accept": "application/json"},
                params=params
            )
            response.raise_for_status()
            data = response.json()
            
            return {
                "success": True,
                "view_name": view_name,
                "view_id": view_id,
                "filters_applied": filters,
                "dimensions": dimensions,
                "metrics": metrics,
                "data": data
            }
        
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            error_detail = None
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                except:
                    error_detail = e.response.text[:500] if hasattr(e.response, 'text') else None
            return {
                "success": False,
                "error": f"API request failed: {str(e)}",
                "error_detail": error_detail,
                "status_code": getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None
            }
    
    def _build_filter_string(self, filters: Dict) -> str:
        """
        Build filter string for API requests
        Format: key1==value1&key2==value2
        """
        if not filters:
            return ""
        filter_parts = [f"{key}=={value}" for key, value in filters.items()]
        return "&".join(filter_parts)
    
    def _export_to_csv(self, data: List[Dict], file_path: str) -> str:
        """Export data to CSV file"""
        import csv
        if not data:
            return file_path
        
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            if isinstance(data[0], dict):
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
            else:
                writer = csv.writer(f)
                writer.writerows(data)
        return file_path
    
    async def _get_amortized_costs(self, args: Dict) -> Dict:
        """
        Get amortized cost data
        """
        from datetime import datetime, timedelta
        
        start_date = args.get("start_date")
        end_date = args.get("end_date")
        filters = args.get("filters", {})
        dimensions = args.get("dimensions", ["vendor", "service"])
        export_format = args.get("export_format", "json")
        
        # Set default dates if not provided
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        
        try:
            # Build API request
            params = {
                "start_date": start_date,
                "end_date": end_date,
                "dimensions": ",".join(dimensions) if dimensions else "vendor,service",
                "metrics": "amortized_cost,cost"
            }
            
            # Add filters
            filter_string = self._build_filter_string(filters)
            if filter_string:
                params["filter"] = filter_string
            
            # Make API request to reporting endpoint
            url = f"{self.base_url}/reporting/cost/run"
            response = requests.get(url, auth=self.auth, headers={"Accept": "application/json"}, params=params)
            response.raise_for_status()
            data = response.json()
            
            result_data = data.get("result", [])
            
            # Export if requested
            export_path = None
            if export_format == "csv" and result_data:
                file_name = args.get("file_name") or f"amortized_costs_{start_date}_to_{end_date}"
                export_path = self._export_to_csv(result_data, f"{file_name}.csv")
            
            return {
                "success": True,
                "report_type": "amortized_costs",
                "start_date": start_date,
                "end_date": end_date,
                "filters": filters,
                "dimensions": dimensions,
                "total_records": len(result_data),
                "data": result_data,
                "export_path": export_path,
                "export_format": export_format
            }
        
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            error_detail = None
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                except:
                    error_detail = e.response.text[:500] if hasattr(e.response, 'text') else None
            return {
                "success": False,
                "error": f"API request failed: {str(e)}",
                "error_detail": error_detail,
                "status_code": getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None
            }
    
    async def _get_container_costs(self, args: Dict) -> Dict:
        """
        Get container-wise cost breakdown
        """
        from datetime import datetime, timedelta
        
        start_date = args.get("start_date")
        end_date = args.get("end_date")
        filters = args.get("filters", {})
        group_by = args.get("group_by", ["cluster", "namespace"])
        export_format = args.get("export_format", "json")
        
        # Set default dates if not provided
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        
        try:
            # Map group_by to API dimensions
            dimension_map = {
                "cluster": "cluster_name",
                "namespace": "namespace",
                "pod": "pod_name",
                "container": "container_name",
                "service": "service_name"
            }
            dimensions = [dimension_map.get(gb, gb) for gb in group_by]
            
            params = {
                "start_date": start_date,
                "end_date": end_date,
                "dimensions": ",".join(dimensions),
                "metrics": "cost,usage"
            }
            
            # Add container-specific filters
            if not filters.get("product_id"):
                filters["product_id"] = "K8s"  # Default to Kubernetes
            
            filter_string = self._build_filter_string(filters)
            if filter_string:
                params["filter"] = filter_string
            
            url = f"{self.base_url}/reporting/cost/run"
            response = requests.get(url, auth=self.auth, headers={"Accept": "application/json"}, params=params)
            response.raise_for_status()
            data = response.json()
            
            result_data = data.get("result", [])
            
            # Export if requested
            export_path = None
            if export_format == "csv" and result_data:
                file_name = args.get("file_name") or f"container_costs_{start_date}_to_{end_date}"
                export_path = self._export_to_csv(result_data, f"{file_name}.csv")
            
            return {
                "success": True,
                "report_type": "container_costs",
                "start_date": start_date,
                "end_date": end_date,
                "filters": filters,
                "group_by": group_by,
                "total_records": len(result_data),
                "data": result_data,
                "export_path": export_path,
                "export_format": export_format
            }
        
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            error_detail = None
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                except:
                    error_detail = e.response.text[:500] if hasattr(e.response, 'text') else None
            return {
                "success": False,
                "error": f"API request failed: {str(e)}",
                "error_detail": error_detail,
                "status_code": getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None
            }
    
    async def _explore_tags(self, args: Dict) -> Dict:
        """
        Explore costs by tags
        """
        from datetime import datetime, timedelta
        
        tag_key = args.get("tag_key")
        tag_value = args.get("tag_value")
        start_date = args.get("start_date")
        end_date = args.get("end_date")
        additional_filters = args.get("additional_filters", {})
        export_format = args.get("export_format", "json")
        
        if not tag_key:
            return {
                "success": False,
                "error": "tag_key is required"
            }
        
        # Set default dates if not provided
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        
        try:
            # Build filters with tag
            filters = {f"tag:{tag_key}": tag_value} if tag_value else {f"tag:{tag_key}": "*"}
            filters.update(additional_filters)
            
            params = {
                "start_date": start_date,
                "end_date": end_date,
                "dimensions": f"tag:{tag_key},vendor,service",
                "metrics": "cost"
            }
            
            filter_string = self._build_filter_string(filters)
            if filter_string:
                params["filter"] = filter_string
            
            url = f"{self.base_url}/reporting/cost/run"
            response = requests.get(url, auth=self.auth, headers={"Accept": "application/json"}, params=params)
            response.raise_for_status()
            data = response.json()
            
            result_data = data.get("result", [])
            
            # Export if requested
            export_path = None
            if export_format == "csv" and result_data:
                file_name = args.get("file_name") or f"tag_explorer_{tag_key}_{start_date}_to_{end_date}"
                export_path = self._export_to_csv(result_data, f"{file_name}.csv")
            
            return {
                "success": True,
                "report_type": "tag_explorer",
                "tag_key": tag_key,
                "tag_value": tag_value,
                "start_date": start_date,
                "end_date": end_date,
                "total_records": len(result_data),
                "data": result_data,
                "export_path": export_path,
                "export_format": export_format
            }
        
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            error_detail = None
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                except:
                    error_detail = e.response.text[:500] if hasattr(e.response, 'text') else None
            return {
                "success": False,
                "error": f"API request failed: {str(e)}",
                "error_detail": error_detail,
                "status_code": getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None
            }
    
    async def _get_anomaly_detection(self, args: Dict) -> Dict:
        """
        Get anomaly detection results
        """
        from datetime import datetime, timedelta
        
        start_date = args.get("start_date")
        end_date = args.get("end_date")
        severity = args.get("severity", "all")
        filters = args.get("filters", {})
        min_cost_change_percent = args.get("min_cost_change_percent", 10.0)
        export_format = args.get("export_format", "json")
        
        # Set default dates if not provided
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        
        try:
            params = {
                "start_date": start_date,
                "end_date": end_date,
                "dimensions": "vendor,service,account_id",
                "metrics": "cost",
                "anomaly_detection": "true",
                "min_change_percent": str(min_cost_change_percent)
            }
            
            if severity != "all":
                params["severity"] = severity
            
            filter_string = self._build_filter_string(filters)
            if filter_string:
                params["filter"] = filter_string
            
            url = f"{self.base_url}/reporting/cost/run"
            response = requests.get(url, auth=self.auth, headers={"Accept": "application/json"}, params=params)
            response.raise_for_status()
            data = response.json()
            
            result_data = data.get("result", [])
            
            # Filter anomalies (if API doesn't do it)
            if severity != "all" and result_data:
                # This would need to be adjusted based on actual API response structure
                pass
            
            # Export if requested
            export_path = None
            if export_format == "csv" and result_data:
                file_name = args.get("file_name") or f"anomalies_{start_date}_to_{end_date}"
                export_path = self._export_to_csv(result_data, f"{file_name}.csv")
            
            return {
                "success": True,
                "report_type": "anomaly_detection",
                "start_date": start_date,
                "end_date": end_date,
                "severity": severity,
                "min_cost_change_percent": min_cost_change_percent,
                "total_anomalies": len(result_data),
                "data": result_data,
                "export_path": export_path,
                "export_format": export_format
            }
        
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            error_detail = None
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                except:
                    error_detail = e.response.text[:500] if hasattr(e.response, 'text') else None
            return {
                "success": False,
                "error": f"API request failed: {str(e)}",
                "error_detail": error_detail,
                "status_code": getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None
            }
    
    async def _list_available_tags(self, args: Dict) -> Dict:
        """
        List available tag keys
        """
        limit = args.get("limit", 100)
        
        try:
            # Try to get tag metadata from API
            url = f"{self.base_url}/reporting/dimensions"
            params = {"dimension_type": "tag", "limit": limit}
            
            response = requests.get(url, auth=self.auth, headers={"Accept": "application/json"}, params=params)
            response.raise_for_status()
            data = response.json()
            
            tag_keys = data.get("result", [])
            
            # If that endpoint doesn't work, try alternative approach
            if not tag_keys:
                # Fallback: try to get from a sample cost report
                from datetime import datetime, timedelta
                end_date = datetime.now().strftime("%Y-%m-%d")
                start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
                
                url = f"{self.base_url}/reporting/cost/run"
                params = {
                    "start_date": start_date,
                    "end_date": end_date,
                    "dimensions": "tag",
                    "limit": 1
                }
                response = requests.get(url, auth=self.auth, headers={"Accept": "application/json"}, params=params)
                if response.status_code == 200:
                    data = response.json()
                    # Extract tag keys from response metadata if available
                    tag_keys = data.get("meta", {}).get("available_tags", [])
            
            return {
                "success": True,
                "total_tags": len(tag_keys),
                "tag_keys": tag_keys if isinstance(tag_keys, list) else [tag_keys] if tag_keys else []
            }
        
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            return {
                "success": False,
                "error": f"API request failed: {str(e)}",
                "status_code": getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None,
                "note": "Tag listing may require different API endpoint. Check Cloudability API documentation."
            }
    
    async def _export_cost_report(self, args: Dict) -> Dict:
        """
        Export cost report with custom filters
        """
        start_date = args.get("start_date")
        end_date = args.get("end_date")
        filters = args.get("filters", {})
        dimensions = args.get("dimensions", ["vendor", "service"])
        metrics = args.get("metrics", ["cost"])
        export_format = args.get("export_format", "json")
        file_name = args.get("file_name")
        
        if not start_date or not end_date:
            return {
                "success": False,
                "error": "start_date and end_date are required"
            }
        
        try:
            params = {
                "start_date": start_date,
                "end_date": end_date,
                "dimensions": ",".join(dimensions) if dimensions else "vendor,service",
                "metrics": ",".join(metrics) if metrics else "cost"
            }
            
            filter_string = self._build_filter_string(filters)
            if filter_string:
                params["filter"] = filter_string
            
            url = f"{self.base_url}/reporting/cost/run"
            response = requests.get(url, auth=self.auth, headers={"Accept": "application/json"}, params=params)
            response.raise_for_status()
            data = response.json()
            
            result_data = data.get("result", [])
            
            # Generate file name if not provided
            if not file_name:
                filter_summary = "_".join([f"{k}_{v}" for k, v in list(filters.items())[:2]]) if filters else "all"
                file_name = f"cost_report_{filter_summary}_{start_date}_to_{end_date}"
            
            export_path = None
            if export_format == "csv" and result_data:
                export_path = self._export_to_csv(result_data, f"{file_name}.csv")
            elif export_format == "json" and result_data:
                import json
                with open(f"{file_name}.json", 'w', encoding='utf-8') as f:
                    json.dump(result_data, f, indent=2, default=str)
                export_path = f"{file_name}.json"
            
            return {
                "success": True,
                "report_type": "custom_export",
                "start_date": start_date,
                "end_date": end_date,
                "filters": filters,
                "dimensions": dimensions,
                "metrics": metrics,
                "total_records": len(result_data),
                "export_path": export_path,
                "export_format": export_format
            }
        
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            error_detail = None
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                except:
                    error_detail = e.response.text[:500] if hasattr(e.response, 'text') else None
            return {
                "success": False,
                "error": f"API request failed: {str(e)}",
                "error_detail": error_detail,
                "status_code": getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None
            }


async def main():
    """
    Main entry point for MCP server (stdio-based)
    Reads configuration from environment variables
    """
    # Read configuration from environment
    api_key = os.getenv("CLOUDABILITY_API_KEY")
    base_url = os.getenv("CLOUDABILITY_BASE_URL", "https://api.cloudability.com/v3")
    
    if not api_key:
        logger.error("CLOUDABILITY_API_KEY environment variable is required")
        sys.exit(1)
    
    # Initialize server
    server = CloudabilityMCPServer(api_key=api_key, base_url=base_url)
    logger.info(f"Cloudability MCP Server initialized with base URL: {base_url}")
    
    # Configure stdio for MCP protocol
    try:
        sys.stdin.reconfigure(encoding='utf-8')
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        # Python < 3.7 doesn't have reconfigure
        pass
    
    # Main loop: read from stdin, write to stdout
    loop = asyncio.get_event_loop()
    
    while True:
        try:
            # Read line from stdin (blocking) - use executor to avoid blocking event loop
            line = await loop.run_in_executor(None, sys.stdin.readline)
            if not line:
                break
            
            line = line.strip()
            if not line:
                continue
            
            # Parse JSON-RPC request
            request = json.loads(line)
            response = await server.handle_request(request)
            
            # Write response to stdout (only if not a notification)
            if response is not None:
                print(json.dumps(response, ensure_ascii=False))
                sys.stdout.flush()
        
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON: {e}")
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32700,
                    "message": "Parse error",
                    "data": str(e)
                }
            }
            print(json.dumps(error_response, ensure_ascii=False))
            sys.stdout.flush()
        
        except KeyboardInterrupt:
            logger.info("Server shutting down...")
            break
        
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32603,
                    "message": "Internal error",
                    "data": str(e)
                }
            }
            print(json.dumps(error_response, ensure_ascii=False))
            sys.stdout.flush()


if __name__ == "__main__":
    asyncio.run(main())

