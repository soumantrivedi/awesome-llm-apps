"""
View Tools
Tools for listing and managing Cloudability views
"""

from ..framework.tool_base import get_registry
from .base_tool import CloudabilityTool
from ..utils import export_to_csv, export_to_json, export_to_markdown, generate_timestamped_filename

registry = get_registry()


class ListViewsTool(CloudabilityTool):
    """List all views"""
    
    def get_name(self) -> str:
        return "list_views"
    
    def get_description(self) -> str:
        return "List all available dashboard views in your Cloudability account. Supports exporting to CSV, Markdown, or JSON (default) format with timestamp."
    
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
                },
                "export_format": {
                    "type": "string",
                    "enum": ["json", "csv", "markdown"],
                    "description": "Export format (default: json)",
                    "default": "json"
                }
            }
        }
    
    async def execute(self, args: dict) -> dict:
        api = self.require_api_client()
        result = api.list_views(
            limit=args.get("limit"),
            offset=args.get("offset")
        )
        
        # Handle export if requested
        export_format = args.get("export_format", "json")
        if result.get("success") and result.get("views"):
            views = result.get("views", [])
            
            if export_format == "csv":
                file_path = generate_timestamped_filename("views", "csv")
                from ..utils import export_to_csv
                export_to_csv(views, file_path)
                result["export_path"] = file_path
                result["export_format"] = "csv"
            elif export_format == "markdown":
                file_path = generate_timestamped_filename("views", "md")
                export_to_markdown(views, file_path, title="Cloudability Views")
                result["export_path"] = file_path
                result["export_format"] = "markdown"
            else:  # json (default)
                file_path = generate_timestamped_filename("views", "json")
                export_to_json(views, file_path)
                result["export_path"] = file_path
                result["export_format"] = "json"
        
        return result


# Register tool
registry.register(ListViewsTool())

