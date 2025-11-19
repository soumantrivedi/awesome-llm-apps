# Cloudability MCP Server - Architecture

## Overview

The Cloudability MCP Server has been refactored into a modular architecture for better maintainability, testability, and concurrent development. The new structure separates concerns and follows best practices from modern Python projects.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    MCP Protocol Layer                        │
│                    (src/main.py)                            │
│  - Tool definitions                                          │
│  - Request/Response handling                                 │
│  - MCP protocol implementation                               │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    API Client Layer                          │
│                    (src/api_client.py)                       │
│  - Cloudability API interactions                              │
│  - Business logic                                            │
│  - Data transformation                                       │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│   Config    │ │    Auth     │ │   Utils     │
│ (config.py) │ │  (auth.py)  │ │ (utils.py)  │
└─────────────┘ └─────────────┘ └─────────────┘
```

## Module Structure

### `src/config.py`
**Purpose**: Configuration management

- Environment variable loading
- Configuration validation
- Regional endpoint management
- Default values and constants

**Key Features**:
- Centralized configuration
- Environment-based settings
- Regional endpoint support (US, EU, APAC, ME)

### `src/auth.py`
**Purpose**: Authentication handling

- Basic authentication (API key)
- Bearer token authentication
- Header management

**Key Features**:
- Support for multiple auth types
- Flexible authentication mechanism
- Header generation

### `src/utils.py`
**Purpose**: Utility functions

- Filter string building
- CSV/JSON export
- Date range utilities
- Error formatting
- View lookup helpers

**Key Features**:
- Reusable utility functions
- Consistent error handling
- Export functionality

### `src/api_client.py`
**Purpose**: Core API business logic

- View operations (list, get by name)
- Cost report operations
- Amortized costs
- Export operations

**Key Features**:
- Clean separation of API logic
- Consistent error handling
- Type hints throughout
- Comprehensive API coverage

### `src/main.py`
**Purpose**: MCP server implementation

- MCP protocol handling
- Tool definitions
- Request routing
- Response formatting

**Key Features**:
- MCP protocol compliance
- Tool registration
- Async request handling
- Error management

## Benefits of Modular Architecture

### 1. **Separation of Concerns**
- Each module has a single, well-defined responsibility
- Easy to understand and maintain
- Changes in one area don't affect others

### 2. **Testability**
- Each module can be tested independently
- Mock dependencies easily
- Unit tests for individual components

### 3. **Concurrent Development**
- Multiple developers can work on different modules
- Clear interfaces between modules
- Reduced merge conflicts

### 4. **Reusability**
- Utility functions can be reused
- API client can be used outside MCP context
- Configuration can be shared

### 5. **Maintainability**
- Easier to locate and fix bugs
- Clear code organization
- Better documentation structure

## Development Workflow

### Adding a New Feature

1. **Identify the module**: Determine which module(s) need changes
2. **Update API client**: Add new methods to `api_client.py` if needed
3. **Add tool definition**: Update `main.py` with new tool schema
4. **Add tests**: Create tests for new functionality
5. **Update docs**: Document the new feature

### Example: Adding Container Costs

```python
# 1. Add to api_client.py
def get_container_costs(self, ...):
    # Implementation

# 2. Add tool to main.py
{
    "name": "get_container_costs",
    "description": "...",
    "inputSchema": {...}
}

# 3. Add handler
async def _get_container_costs(self, args):
    return self.api_client.get_container_costs(...)
```

## Migration from Monolithic Structure

The old `cloudability_mcp_server.py` is now a thin wrapper that imports from the modular structure, ensuring backward compatibility.

### Old Usage (Still Works)
```python
from cloudability_mcp_server import CloudabilityMCPServer
```

### New Usage (Recommended)
```python
from src.main import CloudabilityMCPServer
from src.api_client import CloudabilityAPIClient
from src.config import Config
```

## Testing Strategy

### Unit Tests
- Test each module independently
- Mock external dependencies
- Test error cases

### Integration Tests
- Test API client with real API (optional)
- Test MCP protocol handling
- Test end-to-end workflows

### Example Test Structure
```
tests/
├── test_config.py
├── test_auth.py
├── test_utils.py
├── test_api_client.py
└── test_main.py
```

## Future Enhancements

Based on the reference implementation, potential enhancements:

1. **Container Cost Analysis**: Detailed Kubernetes cost breakdown
2. **Budget Management**: Budget creation and monitoring
3. **Spending Forecasts**: Predictive cost analysis
4. **Tag Explorer**: Cost analysis by tags
5. **Anomaly Detection**: Unusual spending pattern detection
6. **Async Reporting**: Large dataset handling
7. **Measure Discovery**: Dynamic dimension/metric discovery

## Contributing

When contributing:

1. Follow the modular structure
2. Add type hints
3. Write tests
4. Update documentation
5. Maintain backward compatibility

## References

- [Reference Implementation](https://github.com/eelzinaty/cloudability-mcp-server)
- [MCP Protocol Specification](https://modelcontextprotocol.io)
- [Cloudability API Documentation](https://www.ibm.com/docs/en/cloudability-commercial)

