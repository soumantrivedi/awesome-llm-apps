"""
Cost Allocation Tools
Tools for cost allocation and rightsizing
"""

from ..framework.tool_base import get_registry
from .base_tool import CloudabilityTool

registry = get_registry()


class AnalyzeContainerCostAllocationTool(CloudabilityTool):
    """Analyze container cost allocation"""
    
    def get_name(self) -> str:
        return "analyze_container_cost_allocation"
    
    def get_description(self) -> str:
        return "Analyze container cost allocation by namespace, pod, service, or labels. Supports JSON and CSV export formats."
    
    def get_input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "start_date": {"type": "string", "description": "Start date (YYYY-MM-DD)"},
                "end_date": {"type": "string", "description": "End date (YYYY-MM-DD)"},
                "group": {"type": "array", "items": {"type": "string"}, "description": "Group by (namespace, pod, service, labels)"},
                "metrics": {"type": "array", "items": {"type": "string"}, "description": "Metrics to analyze"},
                "filters": {"type": "array", "items": {"type": "string"}, "description": "Filter conditions"},
                "cost_type": {"type": "string", "enum": ["total_cost", "adjusted_amortized_cost"], "description": "Cost type"},
                "export_format": {"type": "string", "enum": ["json", "csv"], "description": "Export format (default: json)"}
            }
        }
    
    async def execute(self, args: dict) -> dict:
        from ..api_client_extended import ExtendedCloudabilityAPIClient
        api = self.require_api_client()
        if not isinstance(api, ExtendedCloudabilityAPIClient):
            api = ExtendedCloudabilityAPIClient(api_key=api.api_key, base_url=api.base_url)
        
        # Build filters from array
        filters = {}
        if args.get("filters"):
            for f in args.get("filters", []):
                if "==" in f:
                    key, value = f.split("==", 1)
                    filters[key.strip()] = value.strip()
        
        export_format = args.get("export_format", "json")
        return api.get_container_costs(
            start_date=args.get("start_date"),
            end_date=args.get("end_date"),
            filters=filters,
            group_by=args.get("group"),
            metrics=args.get("metrics"),
            export_format=export_format
        )


# Register tools
registry.register(AnalyzeContainerCostAllocationTool())

