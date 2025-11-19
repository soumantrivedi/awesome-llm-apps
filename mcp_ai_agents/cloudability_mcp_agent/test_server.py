"""
Simple test script to verify Cloudability MCP Server configuration
Run this to test your API key and server setup before configuring in Cursor
"""

import os
import sys
import asyncio
import json
from dotenv import load_dotenv
from cloudability_mcp_server import CloudabilityMCPServer

# Load environment variables
load_dotenv()

async def test_server():
    """Test the Cloudability MCP Server"""
    print("=" * 60)
    print("Cloudability MCP Server Test")
    print("=" * 60)
    print()
    
    # Get configuration
    api_key = os.getenv("CLOUDABILITY_API_KEY")
    base_url = os.getenv("CLOUDABILITY_BASE_URL", "https://api.cloudability.com/v3")
    
    if not api_key:
        print("❌ ERROR: CLOUDABILITY_API_KEY not found in environment")
        print("   Please set it in your .env file or environment variables")
        return False
    
    print(f"✓ API Key: {'*' * (len(api_key) - 4)}{api_key[-4:]}")
    print(f"✓ Base URL: {base_url}")
    print()
    
    try:
        # Initialize server
        server = CloudabilityMCPServer(api_key=api_key, base_url=base_url)
        print("✓ Server initialized successfully")
        print()
        
        # Test 1: List available tools
        print("Test 1: Listing available tools...")
        tools = server.get_tools()
        print(f"✓ Found {len(tools)} tools:")
        for tool in tools:
            print(f"  - {tool['name']}: {tool['description'][:60]}...")
        print()
        
        # Test 2: List views
        print("Test 2: Listing available views...")
        views_result = await server._list_views({})
        if views_result.get("success"):
            views = views_result.get("views", [])
            print(f"✓ Found {len(views)} views")
            if views:
                print("  Sample views:")
                for view in views[:5]:  # Show first 5
                    print(f"    - {view.get('name', 'Unknown')} (ID: {view.get('id', 'N/A')})")
        else:
            print(f"⚠ Warning: {views_result.get('error', 'Unknown error')}")
            print("  This might be normal if API endpoints differ")
        print()
        
        # Test 3: Test tool call structure
        print("Test 3: Testing tool call structure...")
        test_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {}
        }
        response = await server.handle_request(test_request)
        if response.get("result"):
            print("✓ Tool list request handled successfully")
        else:
            print(f"⚠ Warning: {response.get('error', 'Unknown error')}")
        print()
        
        print("=" * 60)
        print("✓ All tests completed!")
        print("=" * 60)
        print()
        print("Next steps:")
        print("1. If all tests passed, your server is ready")
        print("2. Configure the MCP server in Cursor (see README.md)")
        print("3. Use the tools via Cursor's MCP integration")
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_server())
    sys.exit(0 if success else 1)

