"""
Example script to test Cloudability V2 MCP Server
Run this script to validate that the MCP server tools are working correctly
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# Load environment variables from .env if it exists
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)

# Add project root to path so we can import from src package
project_root = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, project_root)

from src.main import CloudabilityV2MCPServer
from src.config import Config


async def test_list_views():
    """Test list_views tool"""
    print("=" * 80)
    print("Test 1: List Views")
    print("=" * 80)
    
    server = CloudabilityV2MCPServer()
    result = await server.call_tool("list_views", {"limit": 5})
    
    print(f"Success: {result.get('success')}")
    if result.get("success"):
        print(f"Total views: {result.get('total_views')}")
        views = result.get("views", [])
        print(f"Returned {len(views)} views")
        if views:
            print("\nFirst view:")
            print(f"  ID: {views[0].get('id')}")
            print(f"  Name: {views[0].get('name')}")
    else:
        print(f"Error: {result.get('error')}")
    print()


async def test_list_budgets():
    """Test list_budgets tool"""
    print("=" * 80)
    print("Test 2: List Budgets")
    print("=" * 80)
    
    server = CloudabilityV2MCPServer()
    result = await server.call_tool("list_budgets", {})
    
    print(f"Success: {result.get('success')}")
    if result.get("success"):
        print(f"Total budgets: {result.get('total_budgets')}")
        budgets = result.get("budgets", [])
        print(f"Returned {len(budgets)} budgets")
        if budgets:
            print("\nFirst budget:")
            print(f"  ID: {budgets[0].get('id')}")
            print(f"  Name: {budgets[0].get('name')}")
    else:
        print(f"Error: {result.get('error')}")
    print()


async def test_get_amortized_costs():
    """Test get_amortized_costs tool"""
    print("=" * 80)
    print("Test 3: Get Amortized Costs")
    print("=" * 80)
    
    # Calculate date range (last 30 days)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    server = CloudabilityV2MCPServer()
    result = await server.call_tool("get_amortized_costs", {
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "dimensions": ["vendor"],
        "granularity": "monthly",
        "export_format": "json"
    })
    
    print(f"Success: {result.get('success')}")
    if result.get("success"):
        print(f"Total records: {result.get('total_records')}")
        print(f"Dimensions: {result.get('dimensions')}")
        print(f"Granularity: {result.get('granularity')}")
        data = result.get("data", [])
        if data:
            print(f"\nFirst record:")
            for key, value in list(data[0].items())[:5]:
                print(f"  {key}: {value}")
    else:
        print(f"Error: {result.get('error')}")
    print()


async def test_get_amortized_costs_csv():
    """Test get_amortized_costs tool with CSV export"""
    print("=" * 80)
    print("Test 4: Get Amortized Costs (CSV Export)")
    print("=" * 80)
    
    # Calculate date range (last 30 days)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    server = CloudabilityV2MCPServer()
    result = await server.call_tool("get_amortized_costs", {
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "dimensions": ["vendor"],
        "granularity": "monthly",
        "export_format": "csv"
    })
    
    print(f"Success: {result.get('success')}")
    if result.get("success"):
        print(f"Export format: {result.get('export_format')}")
        export_path = result.get("export_path")
        if export_path:
            print(f"CSV exported to: {export_path}")
            # Show first few lines
            with open(export_path, 'r') as f:
                lines = f.readlines()[:5]
                print("\nFirst few lines of CSV:")
                for line in lines:
                    print(f"  {line.strip()}")
    else:
        print(f"Error: {result.get('error')}")
    print()


async def test_invalid_dimension():
    """Test get_amortized_costs with invalid dimension"""
    print("=" * 80)
    print("Test 5: Get Amortized Costs (Invalid Dimension)")
    print("=" * 80)
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    server = CloudabilityV2MCPServer()
    result = await server.call_tool("get_amortized_costs", {
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "dimensions": ["cluster_name"],  # Invalid dimension
        "granularity": "monthly"
    })
    
    print(f"Success: {result.get('success')}")
    if not result.get("success"):
        print(f"Expected error: {result.get('error')}")
    else:
        print("WARNING: Should have failed with invalid dimension")
    print()


async def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("Cloudability V2 MCP Server - Test Suite")
    print("=" * 80 + "\n")
    
    # Check if credentials are available
    api_key = os.getenv("CLOUDABILITY_API_KEY")
    public_key = os.getenv("CLOUDABILITY_PUBLIC_KEY")
    private_key = os.getenv("CLOUDABILITY_PRIVATE_KEY")
    
    if not api_key and not (public_key and private_key):
        print("⚠️  No Cloudability credentials found!")
        print("   Set environment variables or create a .env file with:")
        print("   - CLOUDABILITY_API_KEY (for basic auth), or")
        print("   - CLOUDABILITY_PUBLIC_KEY and CLOUDABILITY_PRIVATE_KEY (for enhanced auth)")
        print("\n   You can also run 'make secrets' to create a .env file")
        print("   Or copy credentials from ~/.cursor/mcp.json to .env file")
        sys.exit(1)
    
    try:
        await test_list_views()
        await test_list_budgets()
        await test_get_amortized_costs()
        await test_get_amortized_costs_csv()
        await test_invalid_dimension()
        
        print("=" * 80)
        print("All tests completed!")
        print("=" * 80)
    except Exception as e:
        print(f"\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

