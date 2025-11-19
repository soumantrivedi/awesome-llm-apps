"""
Tag Explorer Tools
Tools for exploring costs by tags
"""

from ..framework.tool_base import get_registry
from .base_tool import CloudabilityTool

registry = get_registry()


class ListAvailableTagsTool(CloudabilityTool):
    """List available tags"""
    
    def get_name(self) -> str:
        return "list_available_tags"
    
    def get_description(self) -> str:
        return "List all available tag keys in your Cloudability account."
    
    def get_input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "description": "Maximum tag keys to return"}
            }
        }
    
    async def execute(self, args: dict) -> dict:
        from ..api_client_extended import ExtendedCloudabilityAPIClient
        api = self.require_api_client()
        if not isinstance(api, ExtendedCloudabilityAPIClient):
            api = ExtendedCloudabilityAPIClient(api_key=api.api_key, base_url=api.base_url)
        return api.list_available_tags(limit=args.get("limit"))


class ExploreTagsTool(CloudabilityTool):
    """Explore costs by tags"""
    
    def get_name(self) -> str:
        return "explore_tags"
    
    def get_description(self) -> str:
        return "Explore costs by tags. Analyze costs based on custom tags like Environment, Team, Project."
    
    def get_input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "tag_key": {"type": "string", "description": "Tag key to explore (e.g., 'Environment', 'Team')"},
                "tag_value": {"type": "string", "description": "Optional specific tag value"},
                "start_date": {"type": "string", "description": "Start date (YYYY-MM-DD)"},
                "end_date": {"type": "string", "description": "End date (YYYY-MM-DD)"},
                "additional_filters": {"type": "object", "description": "Additional filter conditions", "additionalProperties": {"type": "string"}},
                "export_format": {"type": "string", "enum": ["json", "csv"], "description": "Export format"}
            },
            "required": ["tag_key"]
        }
    
    async def execute(self, args: dict) -> dict:
        from ..api_client_extended import ExtendedCloudabilityAPIClient
        api = self.require_api_client()
        if not isinstance(api, ExtendedCloudabilityAPIClient):
            api = ExtendedCloudabilityAPIClient(api_key=api.api_key, base_url=api.base_url)
        return api.explore_tags(
            tag_key=args.get("tag_key"),
            tag_value=args.get("tag_value"),
            start_date=args.get("start_date"),
            end_date=args.get("end_date"),
            additional_filters=args.get("additional_filters"),
            export_format=args.get("export_format", "json")
        )


# Register tools
registry.register(ListAvailableTagsTool())
registry.register(ExploreTagsTool())

