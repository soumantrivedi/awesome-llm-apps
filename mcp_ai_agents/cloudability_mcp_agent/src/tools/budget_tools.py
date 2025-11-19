"""
Budget Management Tools
Tools for budget creation, monitoring, and management
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
        return {"type": "object", "properties": {}}
    
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
        return api.list_budgets()


class GetBudgetTool(CloudabilityTool):
    """Get budget details"""
    
    def get_name(self) -> str:
        return "get_budget"
    
    def get_description(self) -> str:
        return "Get detailed information for a specific budget."
    
    def get_input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "budget_id": {"type": "string", "description": "Budget ID"}
            },
            "required": ["budget_id"]
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
        return api.get_budget(budget_id=args.get("budget_id"))


class CreateBudgetTool(CloudabilityTool):
    """Create a new budget"""
    
    def get_name(self) -> str:
        return "create_budget"
    
    def get_description(self) -> str:
        return "Create a new budget with monthly thresholds."
    
    def get_input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Budget name"},
                "basis": {"type": "string", "enum": ["cash", "adjusted", "amortized"], "description": "Budget basis"},
                "view_id": {"type": "string", "description": "View ID to apply budget to"},
                "months": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "month": {"type": "string", "description": "Month in YYYY-MM format"},
                            "threshold": {"type": "number", "description": "Budget threshold"}
                        }
                    },
                    "description": "List of month thresholds"
                }
            },
            "required": ["name", "basis", "view_id", "months"]
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
        return api.create_budget(
            name=args.get("name"),
            basis=args.get("basis"),
            view_id=args.get("view_id"),
            months=args.get("months")
        )


class UpdateBudgetTool(CloudabilityTool):
    """Update budget"""
    
    def get_name(self) -> str:
        return "update_budget"
    
    def get_description(self) -> str:
        return "Update an existing budget's thresholds or name."
    
    def get_input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "budget_id": {"type": "string", "description": "Budget ID"},
                "months": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "month": {"type": "string"},
                            "threshold": {"type": "number"}
                        }
                    },
                    "description": "Updated month thresholds"
                },
                "name": {"type": "string", "description": "Updated budget name"}
            },
            "required": ["budget_id"]
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
        return api.update_budget(
            budget_id=args.get("budget_id"),
            months=args.get("months"),
            name=args.get("name")
        )


# Register tools
registry.register(ListBudgetsTool())
registry.register(GetBudgetTool())
registry.register(CreateBudgetTool())
registry.register(UpdateBudgetTool())

