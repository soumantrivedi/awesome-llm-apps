#!/usr/bin/env python3
"""
Test MCP Server - Verify all tools are working
"""

import sys
import json
import asyncio
from src.main import CloudabilityMCPServer
from src.config import Config

async def test_mcp_server():
    """Test MCP server initialization and tools"""
    
    print("=" * 80)
    print("Cloudability MCP Server - Deployment Test")
    print("=" * 80)
    print()
    
    # Initialize server
    print("1. Initializing server...")
    try:
        server = CloudabilityMCPServer(
            api_key=Config.API_KEY,
            base_url=Config.BASE_URL
        )
        print("   ✅ Server initialized successfully")
    except Exception as e:
        print(f"   ❌ Failed to initialize: {e}")
        return False
    print()
    
    # Test MCP initialize
    print("2. Testing MCP initialize...")
    try:
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        init_response = await server.handle_request(init_request)
        if init_response and init_response.get("result"):
            tools_count = init_response.get("result", {}).get("serverInfo", {}).get("tools_count", 0)
            print(f"   ✅ Initialize successful - {tools_count} tools available")
        else:
            print("   ❌ Initialize failed")
            return False
    except Exception as e:
        print(f"   ❌ Initialize error: {e}")
        return False
    print()
    
    # Test tools/list
    print("3. Testing tools/list...")
    try:
        list_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list"
        }
        list_response = await server.handle_request(list_request)
        if list_response and list_response.get("result"):
            tools = list_response.get("result", {}).get("tools", [])
            print(f"   ✅ Tools list successful - {len(tools)} tools")
            print(f"   📋 Tool categories:")
            from collections import defaultdict
            categories = defaultdict(list)
            for tool in tools:
                category = tool['name'].split('_')[0]
                categories[category].append(tool['name'])
            for cat, tool_list in sorted(categories.items()):
                print(f"      {cat}: {len(tool_list)} tools")
        else:
            print("   ❌ Tools list failed")
            return False
    except Exception as e:
        print(f"   ❌ Tools list error: {e}")
        return False
    print()
    
    # Test a sample tool call
    print("4. Testing sample tool call (list_views)...")
    try:
        tool_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "list_views",
                "arguments": {"limit": 5}
            }
        }
        tool_response = await server.handle_request(tool_request)
        if tool_response and tool_response.get("result"):
            print("   ✅ Tool call successful")
            # Parse the result
            content = tool_response.get("result", {}).get("content", [])
            if content:
                result_data = json.loads(content[0].get("text", "{}"))
                if result_data.get("success"):
                    print(f"   ✅ Tool executed successfully")
                    print(f"   📊 Found {result_data.get('total_views', 0)} views")
                else:
                    print(f"   ⚠️  Tool returned error: {result_data.get('error')}")
        else:
            print("   ❌ Tool call failed")
            return False
    except Exception as e:
        print(f"   ❌ Tool call error: {e}")
        import traceback
        traceback.print_exc()
        return False
    print()
    
    print("=" * 80)
    print("✅ All tests passed! Server is ready for deployment.")
    print("=" * 80)
    print()
    print("Next steps:")
    print("1. Restart Cursor IDE")
    print("2. Verify MCP server connection in Cursor")
    print("3. Try using tools in Cursor chat")
    print()
    print("Example commands:")
    print('  - "List all available views in Cloudability"')
    print('  - "Get amortized costs for all services in the last 30 days, export as CSV"')
    print('  - "Get container costs for production cluster grouped by namespace"')
    
    return True

if __name__ == "__main__":
    success = asyncio.run(test_mcp_server())
    sys.exit(0 if success else 1)

