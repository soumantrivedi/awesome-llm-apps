"""
Budget Tools
Tools for listing and managing Cloudability budgets
"""

from ..framework.tool_base import get_registry
from .base_tool import CloudabilityTool

registry = get_registry()


class ListBudgetsTool(CloudabilityTool):
    """List all budgets"""
    
    def get_name(self) -> str:
        return "list_budgets"
    
    def get_description(self) -> str:
        return "List all budgets in your Cloudability account."
    
    def get_input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {}
        }
    
    async def execute(self, args: dict) -> dict:
        api = self.require_api_client()
        return api.list_budgets()


# Register tool
registry.register(ListBudgetsTool())

