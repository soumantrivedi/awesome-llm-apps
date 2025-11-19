# Cloudability MCP Server - Framework Guide

## Overview

The Cloudability MCP Server uses a **framework-based architecture** with a **tool registry pattern** that makes it easy to add new tools and features without modifying core code.

## Architecture

```
┌─────────────────────────────────────────┐
│         Framework Layer                 │
│  (tool_base.py, tool_registry.py)      │
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
                },
                "param2": {
                    "type": "integer",
                    "description": "Another parameter"
                }
            },
            "required": ["param1"]
        }
    
    async def execute(self, args: dict) -> dict:
        api = self.require_api_client()
        
        # Your tool logic here
        result = api.some_api_method(
            param1=args.get("param1"),
            param2=args.get("param2")
        )
        
        return self.build_success_response(
            result,
            report_type="my_new_tool",
            param1=args.get("param1")
        )


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
def my_new_api_method(self, param1: str, param2: int) -> Dict:
    """New API method"""
    try:
        # API call logic
        response = self._make_request("GET", "/some/endpoint", params={...})
        data = response.json()
        return {"success": True, "data": data.get("result", [])}
    except requests.exceptions.RequestException as e:
        return format_error_response(e, ...)
```

### Step 4: Test Your Tool

```python
# test_my_tool.py
from src.main import CloudabilityMCPServer
import asyncio

async def test():
    server = CloudabilityMCPServer(api_key="your_key")
    result = await server.call_tool("my_new_tool", {
        "param1": "value1",
        "param2": 123
    })
    print(result)

asyncio.run(test())
```

## Tool Registration Patterns

### Pattern 1: Direct Registration (Recommended)

```python
class MyTool(CloudabilityTool):
    # ... implementation ...

registry.register(MyTool())
```

### Pattern 2: Factory Registration (Lazy Loading)

```python
def create_my_tool():
    return MyTool()

registry.register_factory("my_tool", create_my_tool)
```

### Pattern 3: Decorator Pattern (Future Enhancement)

```python
@tool(
    name="my_tool",
    description="Tool description",
    input_schema={...}
)
async def my_tool_handler(args: dict) -> dict:
    return {"success": True}
```

## Tool Base Class Methods

### Required Methods

- `get_name()` - Return tool name
- `get_description()` - Return tool description
- `get_input_schema()` - Return JSON schema
- `execute(args)` - Execute tool logic

### Helper Methods (from CloudabilityTool)

- `require_api_client()` - Ensure API client is available
- `validate_date_range()` - Validate and set default dates
- `build_success_response()` - Build standardized success response
- `build_error_response()` - Build standardized error response

## Best Practices

### 1. Error Handling

Always use try/except and return standardized error responses:

```python
async def execute(self, args: dict) -> dict:
    try:
        api = self.require_api_client()
        result = api.some_method(...)
        return self.build_success_response(result, ...)
    except Exception as e:
        return self.build_error_response(e)
```

### 2. Input Validation

Use the built-in validation:

```python
# Validation happens automatically in call_tool()
# But you can add custom validation:

async def execute(self, args: dict) -> dict:
    if args.get("param1") == "invalid":
        return {
            "success": False,
            "error": "Invalid param1 value"
        }
    # ... rest of logic
```

### 3. Date Handling

Use the helper method:

```python
start_date, end_date = self.validate_date_range(
    args.get("start_date"),
    args.get("end_date")
)
```

### 4. Response Formatting

Use helper methods for consistency:

```python
return self.build_success_response(
    data=result_data,
    report_type="my_tool",
    start_date=start_date,
    end_date=end_date,
    custom_field="value"
)
```

## Module Organization

Organize tools by feature area:

```
src/tools/
├── __init__.py              # Imports all tool modules
├── base_tool.py             # Base CloudabilityTool class
├── cost_reporting_tools.py # Cost reporting tools
├── container_tools.py       # Container/K8s tools
├── budget_tools.py          # Budget management
├── forecast_tools.py        # Forecasts & estimates
├── tag_tools.py             # Tag explorer
├── anomaly_tools.py         # Anomaly detection
├── discovery_tools.py       # Discovery tools
└── allocation_tools.py      # Cost allocation
```

## Example: Adding a Rightsizing Tool

```python
# src/tools/optimization_tools.py

from ..framework.tool_base import get_registry
from .base_tool import CloudabilityTool

registry = get_registry()


class GetRightsizingRecommendationsTool(CloudabilityTool):
    """Get rightsizing recommendations"""
    
    def get_name(self) -> str:
        return "get_rightsizing_recommendations"
    
    def get_description(self) -> str:
        return "Get rightsizing recommendations for EC2 instances or other resources."
    
    def get_input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "resource_type": {
                    "type": "string",
                    "enum": ["EC2", "RDS", "EBS"],
                    "description": "Resource type"
                },
                "filters": {
                    "type": "object",
                    "description": "Filter conditions",
                    "additionalProperties": {"type": "string"}
                }
            },
            "required": ["resource_type"]
        }
    
    async def execute(self, args: dict) -> dict:
        from ..api_client_extended import ExtendedCloudabilityAPIClient
        api = self.require_api_client()
        if not isinstance(api, ExtendedCloudabilityAPIClient):
            api = ExtendedCloudabilityAPIClient(api_key=api.api_key, base_url=api.base_url)
        
        # Add API method to ExtendedCloudabilityAPIClient first
        result = api.get_rightsizing_recommendations(
            resource_type=args.get("resource_type"),
            filters=args.get("filters")
        )
        
        return self.build_success_response(
            result,
            report_type="rightsizing_recommendations"
        )


registry.register(GetRightsizingRecommendationsTool())
```

## Testing New Tools

### Unit Test Example

```python
# tests/test_my_tool.py

import pytest
from src.tools.my_new_tools import MyNewTool
from src.api_client_extended import ExtendedCloudabilityAPIClient

@pytest.fixture
def mock_api_client():
    # Create mock API client
    pass

def test_my_tool_execution(mock_api_client):
    tool = MyNewTool()
    tool.set_api_client(mock_api_client)
    
    result = await tool.execute({
        "param1": "value1",
        "param2": 123
    })
    
    assert result["success"] == True
    assert "data" in result
```

## Registry API

### Get All Tools

```python
from src.framework.tool_base import get_registry

registry = get_registry()
tools = registry.list_tools()
print(f"Total tools: {len(tools)}")
```

### Get Tool Definition

```python
tool = registry.get_tool("my_tool")
definition = tool.get_definition()
print(definition)
```

### Unregister Tool

```python
registry.unregister("my_tool")
```

## Benefits of This Framework

1. **Modularity** - Each tool is self-contained
2. **Extensibility** - Add tools without modifying core code
3. **Testability** - Test tools independently
4. **Consistency** - Standard interface for all tools
5. **Maintainability** - Clear separation of concerns
6. **Concurrent Development** - Multiple developers can add tools simultaneously

## Migration from Old Pattern

If you have old tool implementations:

1. Create new tool class extending `CloudabilityTool`
2. Move logic to `execute()` method
3. Register tool in module
4. Remove old implementation from `main.py`

The framework handles the rest automatically!

