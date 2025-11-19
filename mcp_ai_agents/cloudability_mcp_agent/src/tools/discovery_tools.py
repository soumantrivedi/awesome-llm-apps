"""
Discovery Tools
Tools for discovering available measures, dimensions, and operators
"""

from ..framework.tool_base import get_registry
from .base_tool import CloudabilityTool

registry = get_registry()


class ListViewsTool(CloudabilityTool):
    """List all views"""
    
    def get_name(self) -> str:
        return "list_views"
    
    def get_description(self) -> str:
        return "List all available dashboard views in your Cloudability account."
    
    def get_input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "description": "Maximum views to return"},
                "offset": {"type": "integer", "description": "Pagination offset"}
            }
        }
    
    async def execute(self, args: dict) -> dict:
        api = self.require_api_client()
        return api.list_views(limit=args.get("limit"), offset=args.get("offset"))


class GetCostReportWithFiltersTool(CloudabilityTool):
    """Get cost report with filters"""
    
    def get_name(self) -> str:
        return "get_cost_report_with_filters"
    
    def get_description(self) -> str:
        return "Get cost report with advanced filtering options. Supports JSON and CSV export formats."
    
    def get_input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "view_name": {"type": "string", "description": "Name of the dashboard view"},
                "filters": {"type": "object", "description": "Filter conditions", "additionalProperties": {"type": "string"}},
                "dimensions": {"type": "array", "items": {"type": "string"}, "description": "Dimensions to group by"},
                "metrics": {"type": "array", "items": {"type": "string"}, "description": "Metrics to retrieve"},
                "start_date": {"type": "string", "description": "Start date (YYYY-MM-DD)"},
                "end_date": {"type": "string", "description": "End date (YYYY-MM-DD)"},
                "export_format": {"type": "string", "enum": ["json", "csv"], "description": "Export format (default: json)"}
            },
            "required": ["view_name"]
        }
    
    async def execute(self, args: dict) -> dict:
        from ..utils import data_to_csv_string
        api = self.require_api_client()
        export_format = args.get("export_format", "json")
        
        result = api.get_cost_report_with_filters(
            view_name=args.get("view_name"),
            filters=args.get("filters"),
            dimensions=args.get("dimensions"),
            metrics=args.get("metrics"),
            start_date=args.get("start_date"),
            end_date=args.get("end_date")
        )
        
        # Add CSV export if requested
        if export_format == "csv" and result.get("success") and result.get("data"):
            result["csv_data"] = data_to_csv_string(result["data"])
            result["export_format"] = "csv"
        
        return result


class GetAvailableMeasuresTool(CloudabilityTool):
    """Get available measures"""
    
    def get_name(self) -> str:
        return "get_available_measures"
    
    def get_description(self) -> str:
        return "Discover available dimensions and metrics for cost reports."
    
    def get_input_schema(self) -> dict:
        return {"type": "object", "properties": {}}
    
    async def execute(self, args: dict) -> dict:
        from ..api_client_extended import ExtendedCloudabilityAPIClient
        api = self.require_api_client()
        if not isinstance(api, ExtendedCloudabilityAPIClient):
            api = ExtendedCloudabilityAPIClient(api_key=api.api_key, base_url=api.base_url)
        return api.get_available_measures()


class GetFilterOperatorsTool(CloudabilityTool):
    """Get filter operators"""
    
    def get_name(self) -> str:
        return "get_filter_operators"
    
    def get_description(self) -> str:
        return "Get available filter operators for building filter expressions."
    
    def get_input_schema(self) -> dict:
        return {"type": "object", "properties": {}}
    
    async def execute(self, args: dict) -> dict:
        from ..api_client_extended import ExtendedCloudabilityAPIClient
        api = self.require_api_client()
        if not isinstance(api, ExtendedCloudabilityAPIClient):
            api = ExtendedCloudabilityAPIClient(api_key=api.api_key, base_url=api.base_url)
        return api.get_filter_operators()


# Register tools
registry.register(ListViewsTool())
registry.register(GetCostReportWithFiltersTool())
registry.register(GetAvailableMeasuresTool())
registry.register(GetFilterOperatorsTool())

