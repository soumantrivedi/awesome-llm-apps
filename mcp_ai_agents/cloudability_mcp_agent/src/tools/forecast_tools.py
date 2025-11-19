"""
Forecast & Estimate Tools
Tools for spending forecasts and estimates
"""

from ..framework.tool_base import get_registry
from .base_tool import CloudabilityTool

registry = get_registry()


class GetSpendingEstimateTool(CloudabilityTool):
    """Get spending estimate"""
    
    def get_name(self) -> str:
        return "get_spending_estimate"
    
    def get_description(self) -> str:
        return "Get current month spending estimate."
    
    def get_input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "view_id": {"type": "string", "description": "View ID (default: '0' for all)", "default": "0"},
                "basis": {"type": "string", "enum": ["cash", "adjusted", "amortized"], "description": "Estimate basis", "default": "cash"}
            }
        }
    
    async def execute(self, args: dict) -> dict:
        from ..api_client_extended import ExtendedCloudabilityAPIClient
        api = self.require_api_client()
        if not isinstance(api, ExtendedCloudabilityAPIClient):
            api = ExtendedCloudabilityAPIClient(api_key=api.api_key, base_url=api.base_url)
        return api.get_spending_estimate(
            view_id=args.get("view_id", "0"),
            basis=args.get("basis", "cash")
        )


class GetSpendingForecastTool(CloudabilityTool):
    """Get spending forecast"""
    
    def get_name(self) -> str:
        return "get_spending_forecast"
    
    def get_description(self) -> str:
        return "Generate spending forecast based on historical data."
    
    def get_input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "view_id": {"type": "string", "description": "View ID (default: '0')", "default": "0"},
                "basis": {"type": "string", "enum": ["cash", "adjusted", "amortized"], "default": "cash"},
                "months_back": {"type": "integer", "description": "Months of history to use", "default": 6},
                "months_forward": {"type": "integer", "description": "Months to forecast", "default": 12},
                "use_current_estimate": {"type": "boolean", "description": "Use current month estimate", "default": True},
                "remove_one_time_charges": {"type": "boolean", "description": "Remove one-time charges", "default": True}
            }
        }
    
    async def execute(self, args: dict) -> dict:
        from ..api_client_extended import ExtendedCloudabilityAPIClient
        api = self.require_api_client()
        if not isinstance(api, ExtendedCloudabilityAPIClient):
            api = ExtendedCloudabilityAPIClient(api_key=api.api_key, base_url=api.base_url)
        return api.get_spending_forecast(
            view_id=args.get("view_id", "0"),
            basis=args.get("basis", "cash"),
            months_back=args.get("months_back", 6),
            months_forward=args.get("months_forward", 12),
            use_current_estimate=args.get("use_current_estimate", True),
            remove_one_time_charges=args.get("remove_one_time_charges", True)
        )


# Register tools
registry.register(GetSpendingEstimateTool())
registry.register(GetSpendingForecastTool())

