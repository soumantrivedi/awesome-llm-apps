"""
Container/Kubernetes Tools
Tools for container cost analysis and resource usage
"""

from ..framework.tool_base import get_registry
from .base_tool import CloudabilityTool

registry = get_registry()


class GetContainerCostsTool(CloudabilityTool):
    """Get container costs"""
    
    def get_name(self) -> str:
        return "get_container_costs"
    
    def get_description(self) -> str:
        return "Get container/Kubernetes cost breakdown. Groups costs by cluster, namespace, pod, container, or service."
    
    def get_input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "start_date": {"type": "string", "description": "Start date (YYYY-MM-DD)"},
                "end_date": {"type": "string", "description": "End date (YYYY-MM-DD)"},
                "filters": {"type": "object", "description": "Filter conditions (cluster_name, namespace, etc.)", "additionalProperties": {"type": "string"}},
                "group_by": {"type": "array", "items": {"type": "string", "enum": ["cluster", "namespace", "pod", "container", "service"]}, "description": "How to group costs"},
                "metrics": {"type": "array", "items": {"type": "string"}, "description": "Metrics to retrieve"},
                "export_format": {"type": "string", "enum": ["json", "csv"], "description": "Export format"}
            }
        }
    
    async def execute(self, args: dict) -> dict:
        from ..api_client_extended import ExtendedCloudabilityAPIClient
        api = self.require_api_client()
        if not isinstance(api, ExtendedCloudabilityAPIClient):
            api = ExtendedCloudabilityAPIClient(
                api_key=api.api_key,
                base_url=api.base_url,
                auth_type=api.auth_type,
                public_key=api.public_key,
                private_key=api.private_key,
                environment_id=api.environment_id,
                frontdoor_url=api.frontdoor_url
            )
        return api.get_container_costs(
            start_date=args.get("start_date"),
            end_date=args.get("end_date"),
            filters=args.get("filters"),
            group_by=args.get("group_by"),
            metrics=args.get("metrics"),
            export_format=args.get("export_format", "json")
        )


class GetContainerResourceUsageTool(CloudabilityTool):
    """Get container resource usage"""
    
    def get_name(self) -> str:
        return "get_container_resource_usage"
    
    def get_description(self) -> str:
        return "Get container resource usage metrics (CPU, memory, filesystem, network). Supports JSON and CSV export formats."
    
    def get_input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "start_date": {"type": "string", "description": "Start date (YYYY-MM-DD)"},
                "end_date": {"type": "string", "description": "End date (YYYY-MM-DD)"},
                "filters": {"type": "object", "description": "Filter conditions", "additionalProperties": {"type": "string"}},
                "metrics": {"type": "array", "items": {"type": "string"}, "description": "Resource metrics (cpu/reserved, memory/reserved_rss, etc.)"},
                "export_format": {"type": "string", "enum": ["json", "csv"], "description": "Export format (default: json)"}
            }
        }
    
    async def execute(self, args: dict) -> dict:
        from ..api_client_extended import ExtendedCloudabilityAPIClient
        from ..utils import data_to_csv_string
        api = self.require_api_client()
        if not isinstance(api, ExtendedCloudabilityAPIClient):
            api = ExtendedCloudabilityAPIClient(
                api_key=api.api_key,
                base_url=api.base_url,
                auth_type=api.auth_type,
                public_key=api.public_key,
                private_key=api.private_key,
                environment_id=api.environment_id,
                frontdoor_url=api.frontdoor_url
            )
        
        export_format = args.get("export_format", "json")
        result = api.get_container_resource_usage(
            start_date=args.get("start_date"),
            end_date=args.get("end_date"),
            filters=args.get("filters"),
            metrics=args.get("metrics")
        )
        
        # Add CSV export if requested
        if export_format == "csv" and result.get("success") and result.get("data"):
            result["csv_data"] = data_to_csv_string(result["data"])
            result["export_format"] = "csv"
        
        return result


# Register tools
registry.register(GetContainerCostsTool())
registry.register(GetContainerResourceUsageTool())

