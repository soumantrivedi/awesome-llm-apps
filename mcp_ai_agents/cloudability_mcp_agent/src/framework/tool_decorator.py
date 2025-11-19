"""
Tool Decorator
Provides decorator-based tool registration
"""

from typing import Callable, Dict
from .tool_base import ToolRegistry, get_registry


def tool(
    name: str,
    description: str,
    input_schema: Dict,
    registry: ToolRegistry = None
):
    """
    Decorator for registering tools
    
    Usage:
        @tool(
            name="my_tool",
            description="Does something",
            input_schema={"type": "object", "properties": {...}}
        )
        async def my_tool_handler(args: Dict) -> Dict:
            return {"success": True}
    
    Args:
        name: Tool name
        description: Tool description
        input_schema: Input schema dictionary
        registry: Tool registry (defaults to global registry)
    """
    if registry is None:
        registry = get_registry()
    
    def decorator(func: Callable):
        """Decorator function"""
        from .tool_base import BaseTool
        
        class DecoratedTool(BaseTool):
            """Tool created from decorated function"""
            
            def get_name(self):
                return name
            
            def get_description(self):
                return description
            
            def get_input_schema(self):
                return input_schema
            
            async def execute(self, args: Dict) -> Dict:
                """Execute the decorated function"""
                return await func(args)
        
        # Register the tool
        tool_instance = DecoratedTool()
        registry.register(tool_instance)
        
        # Return original function for chaining
        return func
    
    return decorator

