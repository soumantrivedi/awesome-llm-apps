"""
Cost Reporting Tools
Tools for retrieving amortized cost data
"""

from ..framework.tool_base import get_registry
from .base_tool import CloudabilityTool
from ..config import Config
from ..utils import export_to_csv, export_to_json, export_to_markdown, generate_timestamped_filename

registry = get_registry()


class GetAmortizedCostsTool(CloudabilityTool):
    """Get amortized costs"""
    
    def get_name(self) -> str:
        return "get_amortized_costs"
    
    def get_description(self) -> str:
        return (
            "Get amortized cost data from TrueCost Explorer. "
            "Supports validated dimensions that work with amortized costs API. "
            "Valid dimensions: vendor, service, service_name, enhanced_service_name, "
            "account_id, region, date. "
            "Note: K8s dimensions (cluster_name, namespace) do NOT work with amortized costs. "
            "Supports JSON and CSV export formats."
        )
    
    def get_input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "start_date": {
                    "type": "string",
                    "description": "Start date (YYYY-MM-DD)",
                    "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
                },
                "end_date": {
                    "type": "string",
                    "description": "End date (YYYY-MM-DD)",
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
                    "description": "Filter conditions (e.g., {'vendor': 'AWS', 'service': 'EC2'})",
                    "additionalProperties": {"type": "string"}
                },
                "view_name": {
                    "type": "string",
                    "description": "Optional view name to restrict data"
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
            },
            "required": ["start_date", "end_date"]
        }
    
    async def execute(self, args: dict) -> dict:
        api = self.require_api_client()
        
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
            start_date=args.get("start_date"),
            end_date=args.get("end_date"),
            dimensions=dimensions,
            metrics=metrics,
            filters=args.get("filters"),
            view_name=args.get("view_name"),
            granularity=args.get("granularity", "monthly"),
            export_format=api_export_format
        )
        
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
                # API already returned CSV data, just write it to file
                csv_data = result.get("csv_data", "")
                if csv_data:
                    file_path = generate_timestamped_filename(base_name, "csv")
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(csv_data)
                    result["export_path"] = file_path
                    result["export_format"] = "csv"
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

