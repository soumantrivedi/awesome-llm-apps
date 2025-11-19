"""
Cost Reporting Tools
Tools for retrieving amortized cost data
"""

import logging
from ..framework.tool_base import get_registry
from .base_tool import CloudabilityTool
from ..config import Config
from ..utils import export_to_csv, export_to_json, export_to_markdown, generate_timestamped_filename
import csv as csv_module
from io import StringIO

logger = logging.getLogger(__name__)
registry = get_registry()


class GetAmortizedCostsTool(CloudabilityTool):
    """Get amortized costs"""
    
    def get_name(self) -> str:
        return "get_amortized_costs"
    
    def get_description(self) -> str:
        return (
            "Get amortized cost data from TrueCost Explorer. "
            "All costs are returned in USD (United States Dollars). "
            "IMPORTANT: Use 'view_name' parameter to filter by view for access control. "
            "Users may only have access to specific views - always specify a view_name to ensure proper data access. "
            "Use 'list_views' tool first to see available views. "
            "Supports relative time ranges: 'last_month' (previous calendar month) or 'last_2_months' (last 2 months). "
            "Supports validated dimensions that work with amortized costs API. "
            "Valid dimensions: vendor, service, service_name, enhanced_service_name, "
            "account_id, region, date, and tag dimensions (tag1-tag10). "
            "Note: K8s dimensions (cluster_name, namespace) do NOT work as dimensions with amortized costs. "
            "Supports filters with wildcard operators (=@ for contains/wildcard matching). "
            "Cluster name filters (container_cluster_name) can be used but may return empty results if no matching data. "
            "Supports JSON, CSV, and Markdown export formats. "
            "Cost columns in exports are labeled with '_usd' suffix to indicate USD currency."
        )
    
    def get_input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "time_range": {
                    "type": "string",
                    "enum": ["last_month", "last_2_months"],
                    "description": "Relative time range: 'last_month' (previous calendar month) or 'last_2_months' (last 2 months including current). Alternative to start_date/end_date."
                },
                "start_date": {
                    "type": "string",
                    "description": "Start date (YYYY-MM-DD). Required if time_range is not provided.",
                    "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
                },
                "end_date": {
                    "type": "string",
                    "description": "End date (YYYY-MM-DD). Required if time_range is not provided.",
                    "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
                },
                "dimensions": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": Config.VALID_AMORTIZED_DIMENSIONS
                    },
                    "description": (
                        f"Dimensions to group by. Valid options: {', '.join(Config.VALID_AMORTIZED_DIMENSIONS)}"
                    )
                },
                "metrics": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": ["total_amortized_cost", "amortized_cost", "total_cost", "cost"]
                    },
                    "description": "Metrics to retrieve (defaults to total_amortized_cost)"
                },
                "filters": {
                    "type": "object",
                    "description": (
                        "Filter conditions (e.g., {'vendor': 'AWS', 'cluster_name': 'mvp01*'}). "
                        "Supports wildcard patterns (*) and regex patterns for cluster_name. "
                        "Use '=@value' for contains/wildcard matching, or '*value*' for pattern matching."
                    ),
                    "additionalProperties": {"type": "string"}
                },
                "view_name": {
                    "type": "string",
                    "description": (
                        "View name to restrict data (RECOMMENDED for access control). "
                        "Users may only have access to specific views. "
                        "Use 'list_views' tool first to see available views. "
                        "If not provided, may return data the user doesn't have access to or cause errors."
                    )
                },
                "granularity": {
                    "type": "string",
                    "enum": ["daily", "monthly"],
                    "description": "Time granularity (default: monthly)",
                    "default": "monthly"
                },
                "export_format": {
                    "type": "string",
                    "enum": ["json", "csv", "markdown"],
                    "description": "Export format (default: json)",
                    "default": "json"
                },
                "file_name": {
                    "type": "string",
                    "description": "Optional: Custom file name (without extension)"
                }
            }
        }
    
    async def execute(self, args: dict) -> dict:
        api = self.require_api_client()
        
        # Check for view_name - recommend it for access control
        view_name = args.get("view_name")
        if not view_name:
            # Warn but don't fail - some users might have access to all data
            logger.warning(
                "No view_name specified. Users may only have access to specific views. "
                "Consider using 'list_views' to see available views and specify a view_name for proper access control."
            )
        
        # Handle time_range parameter (last_month, last_2_months)
        from ..utils import get_last_month_range, get_last_n_months_range
        
        time_range = args.get("time_range")
        if time_range:
            if time_range == "last_month":
                start_date, end_date = get_last_month_range()
            elif time_range == "last_2_months":
                start_date, end_date = get_last_n_months_range(months=2)
            else:
                return {
                    "success": False,
                    "error": f"Invalid time_range: {time_range}. Valid options: 'last_month', 'last_2_months'"
                }
        else:
            # Use explicit start_date and end_date
            start_date = args.get("start_date")
            end_date = args.get("end_date")
            
            if not start_date or not end_date:
                return {
                    "success": False,
                    "error": "Either 'time_range' (last_month, last_2_months) or both 'start_date' and 'end_date' must be provided"
                }
        
        # Validate dimensions
        dimensions = args.get("dimensions")
        if dimensions:
            invalid_dims = [d for d in dimensions if d not in Config.VALID_AMORTIZED_DIMENSIONS]
            if invalid_dims:
                # Provide helpful error message
                k8s_dims = ["cluster_name", "namespace", "pod_name", "container_name"]
                is_k8s_dim = any(d in invalid_dims for d in k8s_dims)
                
                error_msg = (
                    f"Invalid dimensions for amortized costs: {invalid_dims}. "
                    f"Valid dimensions: {', '.join(Config.VALID_AMORTIZED_DIMENSIONS)}"
                )
                
                if is_k8s_dim:
                    error_msg += (
                        "\n\nNote: Kubernetes dimensions (cluster_name, namespace, pod_name, container_name) "
                        "are NOT supported by the amortized costs API endpoint. "
                        "These dimensions will return 422 errors from the Cloudability API."
                    )
                
                return {
                    "success": False,
                    "error": error_msg
                }
        
        # Ensure metrics default to amortized cost if not provided
        metrics = args.get("metrics")
        if not metrics:
            metrics = ["total_amortized_cost"]
        
        # Get export format
        export_format = args.get("export_format", "json")
        file_name = args.get("file_name")
        
        # For CSV, let API handle it directly (it returns CSV text)
        # For JSON/Markdown, get JSON from API and export ourselves
        api_export_format = "csv" if export_format == "csv" else "json"
        
        # Call API
        result = api.get_amortized_costs(
            start_date=start_date,
            end_date=end_date,
            dimensions=dimensions,
            metrics=metrics,
            filters=args.get("filters"),
            view_name=view_name,  # Use the view_name we checked earlier
            granularity=args.get("granularity", "monthly"),
            export_format=api_export_format
        )
        
        # Add view information to result if view was used
        if view_name and result.get("success"):
            result["view_name"] = view_name
            result["note"] = "Data filtered by view for access control"
        
        # Handle export to file if successful
        if result.get("success"):
            start_date = result.get("start_date") or args.get("start_date")
            end_date = result.get("end_date") or args.get("end_date")
            
            # Generate filename
            if file_name:
                base_name = file_name
            else:
                base_name = "amortized_costs"
                if start_date and end_date:
                    base_name += f"_{start_date}_to_{end_date}"
            
            if export_format == "csv":
                # API already returned CSV data, parse and rewrite with USD indicators
                csv_data = result.get("csv_data", "")
                file_path = generate_timestamped_filename(base_name, "csv")
                
                if csv_data and csv_data.strip():
                    try:
                        # Parse CSV and rewrite with USD currency indicators
                        # Read the CSV data
                        reader = csv_module.DictReader(StringIO(csv_data))
                        rows = list(reader)
                        
                        # Export with USD indicators (even if empty rows, create file with header)
                        export_to_csv(rows, file_path)
                        result["export_path"] = file_path
                        result["export_format"] = "csv"
                        result["currency"] = "USD"
                    except Exception as e:
                        # If parsing fails, write raw CSV data and rename cost column
                        csv_lines = csv_data.strip().split('\n')
                        if csv_lines:
                            # Rename cost column in header
                            header = csv_lines[0].replace('total_amortized_cost', 'total_amortized_cost_usd')
                            with open(file_path, 'w', encoding='utf-8') as f:
                                f.write(header + '\n')
                                if len(csv_lines) > 1:
                                    f.write('\n'.join(csv_lines[1:]) + '\n')
                        else:
                            # Empty CSV, create with header
                            dimensions = result.get("dimensions", [])
                            header = ",".join(dimensions) + ",total_amortized_cost_usd\n"
                            with open(file_path, 'w', encoding='utf-8') as f:
                                f.write(header)
                        result["export_path"] = file_path
                        result["export_format"] = "csv"
                        result["currency"] = "USD"
                else:
                    # No CSV data returned, create empty file with header
                    dimensions = result.get("dimensions", [])
                    header = ",".join(dimensions) + ",total_amortized_cost_usd\n"
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(header)
                    result["export_path"] = file_path
                    result["export_format"] = "csv"
                    result["currency"] = "USD"
                    result["note"] = "No data returned from API - empty report created"
            elif export_format == "markdown":
                # Convert JSON data to Markdown
                data = result.get("data", [])
                if data:
                    file_path = generate_timestamped_filename(base_name, "md")
                    export_to_markdown(
                        data, 
                        file_path, 
                        title=f"Amortized Costs ({start_date} to {end_date})"
                    )
                    result["export_path"] = file_path
                    result["export_format"] = "markdown"
                    result["currency"] = "USD"
            else:  # json (default)
                # Export JSON data to file
                data = result.get("data", [])
                if data:
                    file_path = generate_timestamped_filename(base_name, "json")
                    export_to_json(data, file_path)
                    result["export_path"] = file_path
                    result["export_format"] = "json"
        
        return result


# Register tool
registry.register(GetAmortizedCostsTool())

