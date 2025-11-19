"""
Cost Reporting Tools
Tools for various cost reporting capabilities
"""

from ..framework.tool_base import get_registry
from .base_tool import CloudabilityTool

registry = get_registry()


class GetCostReportByViewTool(CloudabilityTool):
    """Get cost report by view name"""
    
    def get_name(self) -> str:
        return "get_cost_report_by_view"
    
    def get_description(self) -> str:
        return "Get cost report data for a specific dashboard view with optional filtering by product_id. Supports JSON and CSV export formats."
    
    def get_input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "view_name": {"type": "string", "description": "Name of the dashboard view"},
                "product_id": {"type": "string", "description": "Optional: Filter by product ID"},
                "start_date": {"type": "string", "description": "Optional: Start date (YYYY-MM-DD)"},
                "end_date": {"type": "string", "description": "Optional: End date (YYYY-MM-DD)"},
                "limit": {"type": "integer", "description": "Optional: Maximum records (default: 50)"},
                "offset": {"type": "integer", "description": "Optional: Pagination offset"},
                "export_format": {"type": "string", "enum": ["json", "csv"], "description": "Export format (default: json)"}
            },
            "required": ["view_name"]
        }
    
    async def execute(self, args: dict) -> dict:
        from ..utils import data_to_csv_string
        api = self.require_api_client()
        export_format = args.get("export_format", "json")
        
        result = api.get_cost_report_by_view(
            view_name=args.get("view_name"),
            product_id=args.get("product_id"),
            start_date=args.get("start_date"),
            end_date=args.get("end_date"),
            limit=args.get("limit"),
            offset=args.get("offset")
        )
        
        # Add CSV export if requested
        if export_format == "csv" and result.get("success") and result.get("data"):
            result["csv_data"] = data_to_csv_string(result["data"])
            result["export_format"] = "csv"
        
        return result


class GetAmortizedCostsTool(CloudabilityTool):
    """Get amortized costs"""
    
    def get_name(self) -> str:
        return "get_amortized_costs"
    
    def get_description(self) -> str:
        return "Get amortized cost data from TrueCost Explorer. Supports view restrictions, namespace/product_id filters, and monthly granularity."
    
    def get_input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "start_date": {"type": "string", "description": "Start date (YYYY-MM-DD)"},
                "end_date": {"type": "string", "description": "End date (YYYY-MM-DD)"},
                "filters": {"type": "object", "description": "Filter conditions", "additionalProperties": {"type": "string"}},
                "dimensions": {"type": "array", "items": {"type": "string"}, "description": "Dimensions to group by"},
                "view_name": {"type": "string", "description": "Optional view name"},
                "granularity": {"type": "string", "enum": ["daily", "monthly"], "description": "Time granularity"},
                "export_format": {"type": "string", "enum": ["json", "csv"], "description": "Export format"}
            }
        }
    
    async def execute(self, args: dict) -> dict:
        api = self.require_api_client()
        return api.get_amortized_costs(
            start_date=args.get("start_date"),
            end_date=args.get("end_date"),
            filters=args.get("filters"),
            dimensions=args.get("dimensions"),
            view_name=args.get("view_name"),
            granularity=args.get("granularity", "monthly"),
            export_format=args.get("export_format", "json")
        )


class ExportCostReportTool(CloudabilityTool):
    """Export cost report"""
    
    def get_name(self) -> str:
        return "export_cost_report"
    
    def get_description(self) -> str:
        return "Export cost report with custom filters to JSON or CSV format."
    
    def get_input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "start_date": {"type": "string", "description": "Start date (YYYY-MM-DD)"},
                "end_date": {"type": "string", "description": "End date (YYYY-MM-DD)"},
                "filters": {"type": "object", "description": "Filter conditions", "additionalProperties": {"type": "string"}},
                "dimensions": {"type": "array", "items": {"type": "string"}, "description": "Dimensions to group by"},
                "metrics": {"type": "array", "items": {"type": "string"}, "description": "Metrics to include"},
                "export_format": {"type": "string", "enum": ["json", "csv"], "description": "Export format"},
                "file_name": {"type": "string", "description": "Optional file name"}
            },
            "required": ["start_date", "end_date"]
        }
    
    async def execute(self, args: dict) -> dict:
        api = self.require_api_client()
        return api.export_cost_report(
            start_date=args.get("start_date"),
            end_date=args.get("end_date"),
            filters=args.get("filters"),
            dimensions=args.get("dimensions"),
            metrics=args.get("metrics"),
            export_format=args.get("export_format", "json"),
            file_name=args.get("file_name")
        )


# Register tools
registry.register(GetCostReportByViewTool())
registry.register(GetAmortizedCostsTool())
registry.register(ExportCostReportTool())

