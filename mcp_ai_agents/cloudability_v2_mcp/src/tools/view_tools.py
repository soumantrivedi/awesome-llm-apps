"""
View Tools
Tools for listing and managing Cloudability views
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
                "limit": {
                    "type": "integer",
                    "description": "Maximum views to return",
                    "minimum": 1,
                    "maximum": 250
                },
                "offset": {
                    "type": "integer",
                    "description": "Pagination offset",
                    "minimum": 0
                }
            }
        }
    
    async def execute(self, args: dict) -> dict:
        api = self.require_api_client()
        return api.list_views(
            limit=args.get("limit"),
            offset=args.get("offset")
        )


# Register tool
registry.register(ListViewsTool())

