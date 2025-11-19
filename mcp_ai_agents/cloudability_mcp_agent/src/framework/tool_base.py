"""
Base Tool Framework
Provides base classes and registry pattern for MCP tools
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Callable
import logging

logger = logging.getLogger(__name__)


class BaseTool(ABC):
    """
    Base class for all MCP tools
    Provides standard interface and common functionality
    """
    
    def __init__(self, api_client=None):
        """
        Initialize tool
        
        Args:
            api_client: API client instance (optional, can be set later)
        """
        self.api_client = api_client
        self._name = None
        self._description = None
        self._input_schema = None
    
    @property
    def name(self) -> str:
        """Tool name"""
        if self._name is None:
            self._name = self.get_name()
        return self._name
    
    @property
    def description(self) -> str:
        """Tool description"""
        if self._description is None:
            self._description = self.get_description()
        return self._description
    
    @property
    def input_schema(self) -> Dict:
        """Tool input schema"""
        if self._input_schema is None:
            self._input_schema = self.get_input_schema()
        return self._input_schema
    
    def get_definition(self) -> Dict:
        """
        Get complete tool definition for MCP
        
        Returns:
            Tool definition dictionary
        """
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.input_schema
        }
    
    @abstractmethod
    def get_name(self) -> str:
        """Get tool name - must be implemented by subclasses"""
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """Get tool description - must be implemented by subclasses"""
        pass
    
    @abstractmethod
    def get_input_schema(self) -> Dict:
        """Get input schema - must be implemented by subclasses"""
        pass
    
    @abstractmethod
    async def execute(self, args: Dict) -> Dict:
        """
        Execute tool with given arguments
        
        Args:
            args: Tool arguments
            
        Returns:
            Tool execution result
        """
        pass
    
    def validate_args(self, args: Dict) -> Optional[str]:
        """
        Validate tool arguments
        
        Args:
            args: Tool arguments
            
        Returns:
            Error message if validation fails, None otherwise
        """
        schema = self.input_schema
        required = schema.get("required", [])
        
        for field in required:
            if field not in args:
                return f"Required field '{field}' is missing"
        
        return None
    
    def set_api_client(self, api_client):
        """Set API client for tool"""
        self.api_client = api_client


class ToolRegistry:
    """
    Registry for managing MCP tools
    Provides registration and lookup functionality
    """
    
    def __init__(self):
        """Initialize tool registry"""
        self._tools: Dict[str, BaseTool] = {}
        self._tool_factories: Dict[str, Callable] = {}
    
    def register(self, tool: BaseTool):
        """
        Register a tool instance
        
        Args:
            tool: Tool instance to register
        """
        name = tool.name
        if name in self._tools:
            logger.warning(f"Tool '{name}' already registered, overwriting")
        self._tools[name] = tool
        logger.info(f"Registered tool: {name}")
    
    def register_factory(self, name: str, factory: Callable[[], BaseTool]):
        """
        Register a tool factory (lazy loading)
        
        Args:
            name: Tool name
            factory: Factory function that creates tool instance
        """
        self._tool_factories[name] = factory
        logger.info(f"Registered tool factory: {name}")
    
    def get_tool(self, name: str) -> Optional[BaseTool]:
        """
        Get tool by name
        
        Args:
            name: Tool name
            
        Returns:
            Tool instance or None if not found
        """
        # Check direct registration
        if name in self._tools:
            return self._tools[name]
        
        # Check factory registration
        if name in self._tool_factories:
            tool = self._tool_factories[name]()
            self._tools[name] = tool  # Cache for future use
            return tool
        
        return None
    
    def list_tools(self) -> List[str]:
        """
        List all registered tool names
        
        Returns:
            List of tool names
        """
        all_names = set(self._tools.keys()) | set(self._tool_factories.keys())
        return sorted(list(all_names))
    
    def get_all_definitions(self) -> List[Dict]:
        """
        Get definitions for all registered tools
        
        Returns:
            List of tool definitions
        """
        definitions = []
        for name in self.list_tools():
            tool = self.get_tool(name)
            if tool:
                definitions.append(tool.get_definition())
        return definitions
    
    def unregister(self, name: str):
        """
        Unregister a tool
        
        Args:
            name: Tool name to unregister
        """
        if name in self._tools:
            del self._tools[name]
        if name in self._tool_factories:
            del self._tool_factories[name]
        logger.info(f"Unregistered tool: {name}")
    
    def clear(self):
        """Clear all registered tools"""
        self._tools.clear()
        self._tool_factories.clear()
        logger.info("Cleared all tools from registry")


# Global registry instance
_default_registry = ToolRegistry()


def get_registry() -> ToolRegistry:
    """Get default tool registry"""
    return _default_registry

