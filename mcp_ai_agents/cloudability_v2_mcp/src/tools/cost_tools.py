"""
Cost Reporting Tools
Tools for retrieving amortized cost data
"""

from ..framework.tool_base import get_registry
from .base_tool import CloudabilityTool
from ..config import Config

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
                    "enum": ["json", "csv"],
                    "description": "Export format (default: json)",
                    "default": "json"
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
        
        result = api.get_amortized_costs(
            start_date=args.get("start_date"),
            end_date=args.get("end_date"),
            dimensions=dimensions,
            metrics=args.get("metrics"),
            filters=args.get("filters"),
            view_name=args.get("view_name"),
            granularity=args.get("granularity", "monthly"),
            export_format=args.get("export_format", "json")
        )
        
        # CSV export is handled in main.py
        # Just return the result as-is
        
        return result


# Register tool
registry.register(GetAmortizedCostsTool())

