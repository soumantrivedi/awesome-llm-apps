# Framework Guide

Guide for developers extending the Cloudability MCP Server.

## Architecture

The server uses a framework-based architecture with a tool registry pattern:

```
┌─────────────────────────────────────────┐
│         Framework Layer                 │
│  (tool_base.py)                         │
│  - BaseTool abstract class              │
│  - ToolRegistry for management          │
│  - Standard tool interface              │
└─────────────────┬───────────────────────┘
                  │
        ┌─────────┴─────────┐
        │                   │
┌───────▼────────┐  ┌───────▼────────┐
│  Tool Modules  │  │  API Client    │
│  (tools/*.py)  │  │  (api_client)  │
└────────────────┘  └────────────────┘
```

## Adding a New Tool

### Step 1: Create Tool Class

Create a new file in `src/tools/` or add to an existing module:

```python
# src/tools/my_new_tools.py

from ..framework.tool_base import get_registry
from .base_tool import CloudabilityTool

registry = get_registry()


class MyNewTool(CloudabilityTool):
    """My new tool description"""
    
    def get_name(self) -> str:
        return "my_new_tool"
    
    def get_description(self) -> str:
        return "Description of what this tool does"
    
    def get_input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "param1": {
                    "type": "string",
                    "description": "Parameter description"
                }
            },
            "required": ["param1"]
        }
    
    async def execute(self, args: dict) -> dict:
        api = self.require_api_client()
        
        # Your tool logic here
        result = api.some_api_method(
            param1=args.get("param1")
        )
        
        return result


# Register the tool
registry.register(MyNewTool())
```

### Step 2: Import in Tools Module

Add import to `src/tools/__init__.py`:

```python
from . import my_new_tools  # Add this line
```

### Step 3: Add API Method (if needed)

If you need a new API method, add it to `src/api_client_extended.py`:

```python
def my_new_api_method(self, param1: str) -> Dict:
    """New API method"""
    try:
        # API call logic
        response = self._make_request("GET", "/some/endpoint", params={"param": param1})
        return {"success": True, "data": response.json()}
    except Exception as e:
        return format_error_response(e)
```

## Tool Base Class

All tools inherit from `CloudabilityTool` which provides:

- **API Client Access**: `self.require_api_client()` - Gets the API client instance
- **Error Handling**: Automatic error formatting
- **Response Building**: Helper methods for consistent responses

## Tool Registry

Tools are automatically registered when imported. The registry:

- Manages all tool instances
- Provides tool lookup by name
- Generates tool definitions for MCP protocol

## Best Practices

1. **Use BaseTool**: Always inherit from `CloudabilityTool`
2. **Register Tools**: Call `registry.register()` at module level
3. **Error Handling**: Return structured error responses
4. **Documentation**: Provide clear descriptions and parameter docs
5. **Testing**: Add tests for new tools

## Example: Complete Tool

```python
from ..framework.tool_base import get_registry
from .base_tool import CloudabilityTool

registry = get_registry()


class ExampleTool(CloudabilityTool):
    """Example tool showing best practices"""
    
    def get_name(self) -> str:
        return "example_tool"
    
    def get_description(self) -> str:
        return "Example tool that demonstrates the framework"
    
    def get_input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "view_name": {
                    "type": "string",
                    "description": "Dashboard view name"
                },
                "start_date": {
                    "type": "string",
                    "description": "Start date (YYYY-MM-DD)"
                },
                "end_date": {
                    "type": "string",
                    "description": "End date (YYYY-MM-DD)"
                }
            },
            "required": ["view_name"]
        }
    
    async def execute(self, args: dict) -> dict:
        api = self.require_api_client()
        
        try:
            result = api.some_method(
                view_name=args.get("view_name"),
                start_date=args.get("start_date"),
                end_date=args.get("end_date")
            )
            return result
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


# Register tool
registry.register(ExampleTool())
```

## See Also

- [Tools Reference](TOOLS_REFERENCE.md) - See existing tools for examples
- [Usage Examples](USAGE_EXAMPLES.md) - See how tools are used
