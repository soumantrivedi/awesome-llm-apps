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
        return "Discover available dimensions and metrics for cost reports. Returns documented dimensions and metrics based on IBM Cloudability API v3 documentation."
    
    def get_input_schema(self) -> dict:
        return {"type": "object", "properties": {}}
    
    async def execute(self, args: dict) -> dict:
        from ..api_validator import APIParameterValidator
        from ..api_client_extended import ExtendedCloudabilityAPIClient
        
        # First, try to get from API if available
        api = self.require_api_client()
        if isinstance(api, ExtendedCloudabilityAPIClient):
            try:
                api_result = api.get_available_measures()
                if api_result.get("success") and api_result.get("measures"):
                    return api_result
            except Exception:
                pass  # Fall through to documented values
        
        # Return documented dimensions and metrics from API validator
        # Based on IBM Cloudability API v3 documentation
        return {
            "success": True,
            "source": "documented",
            "measures": {
                "dimensions": {
                    "core": APIParameterValidator.CORE_DIMENSIONS,
                    "resource": APIParameterValidator.RESOURCE_DIMENSIONS,
                    "kubernetes": APIParameterValidator.K8S_DIMENSIONS,
                    "cost_allocation": APIParameterValidator.COST_DIMENSIONS,
                    "all": APIParameterValidator.VALID_DIMENSIONS
                },
                "metrics": {
                    "cost": APIParameterValidator.COST_METRICS,
                    "usage": APIParameterValidator.USAGE_METRICS,
                    "all": APIParameterValidator.VALID_METRICS
                },
                "recommended": {
                    "default_dimension": "vendor",
                    "default_metric": "total_amortized_cost",
                    "note": "Based on IBM Cloudability API v3 documentation"
                }
            }
        }


class GetFilterOperatorsTool(CloudabilityTool):
    """Get filter operators"""
    
    def get_name(self) -> str:
        return "get_filter_operators"
    
    def get_description(self) -> str:
        return "Get available filter operators for building filter expressions. Returns documented operators based on IBM Cloudability API v3 documentation."
    
    def get_input_schema(self) -> dict:
        return {"type": "object", "properties": {}}
    
    async def execute(self, args: dict) -> dict:
        from ..api_validator import APIParameterValidator
        from ..api_client_extended import ExtendedCloudabilityAPIClient
        
        # First, try to get from API if available
        api = self.require_api_client()
        if isinstance(api, ExtendedCloudabilityAPIClient):
            try:
                api_result = api.get_filter_operators()
                if api_result.get("success") and api_result.get("operators"):
                    return api_result
            except Exception:
                pass  # Fall through to documented values
        
        # Return documented filter operators from API validator
        # Based on IBM Cloudability API v3 documentation
        operators = APIParameterValidator.VALID_FILTER_OPERATORS
        operator_descriptions = {
            "==": "Equals - exact match",
            "!=": "Does not equal - exclude exact match",
            ">": "Greater than - numeric comparison",
            "<": "Less than - numeric comparison",
            ">=": "Greater than or equal to - numeric comparison",
            "<=": "Less than or equal to - numeric comparison",
            "=@": "Contains - wildcard/pattern matching (e.g., region=@us-east-)",
            "!=@": "Does not contain - exclude pattern match"
        }
        
        return {
            "success": True,
            "source": "documented",
            "operators": [
                {
                    "operator": op,
                    "description": operator_descriptions.get(op, "Filter operator"),
                    "example": self._get_operator_example(op)
                }
                for op in operators
            ],
            "note": "Based on IBM Cloudability API v3 documentation. Multiple filters can be applied using multiple 'filters=' query parameters."
        }
    
    def _get_operator_example(self, operator: str) -> str:
        """Get example usage for an operator"""
        examples = {
            "==": "service==AmazonEC2",
            "!=": "vendor!=Azure",
            ">": "total_amortized_cost>100",
            "<": "total_amortized_cost<50",
            ">=": "total_amortized_cost>=100",
            "<=": "total_amortized_cost<=1000",
            "=@": "region=@us-east-",
            "!=@": "service!=@EC2"
        }
        return examples.get(operator, f"dimension{operator}value")


# Register tools
registry.register(ListViewsTool())
registry.register(GetCostReportWithFiltersTool())
registry.register(GetAvailableMeasuresTool())
registry.register(GetFilterOperatorsTool())

