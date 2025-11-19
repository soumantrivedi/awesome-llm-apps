"""
TrueCost Explorer Example - Tag Dimensions with Filters
Replicates the TrueCost Explorer UI configuration from:
https://app.apptio.com/cloudability#/truecost_explorer
?dimensions=tag10&dimensions=tag3&dimensions=tag7
&end_date=2025-11-19&filters=container_cluster_name%3D%40mvp01
&metric=total_amortized_cost&relative_period=this_month&start_date=2025-11-01

This example demonstrates:
1. Using tag dimensions (tag3, tag7, tag10)
2. Using filters with wildcard operator (=@)
3. Converting UI URL parameters to API calls
"""

import asyncio
import sys
import os
from datetime import datetime
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


async def test_tag_dimensions_with_filters():
    """
    Test matching the exact UI configuration with tag dimensions and filters.
    
    UI URL Parameters:
    - dimensions: tag10, tag3, tag7
    - filters: container_cluster_name=@mvp01 (wildcard filter)
    - metric: total_amortized_cost
    - start_date: 2025-11-01
    - end_date: 2025-11-19
    """
    print("=" * 80)
    print("TrueCost Explorer - Tag Dimensions with Filters")
    print("=" * 80)
    print("\nUI Configuration (from URL):")
    print("  Dimensions: tag10, tag3, tag7")
    print("  Filters: container_cluster_name=@mvp01 (wildcard)")
    print("  Metric: total_amortized_cost")
    print("  Date Range: 2025-11-01 to 2025-11-19 (this_month)")
    print("  Export Format: CSV")
    print()
    
    server = CloudabilityV2MCPServer()
    
    # Convert UI configuration to API call
    result = await server.call_tool("get_amortized_costs", {
        "view_name": Config.DEFAULT_VIEW,  # Use default view for testing
        "start_date": "2025-11-01",
        "end_date": "2025-11-19",
        "dimensions": ["tag10", "tag3", "tag7"],
        "metrics": ["total_amortized_cost"],
        "filters": {
            "container_cluster_name": "=@mvp01"  # Wildcard filter: contains "mvp01"
        },
        "granularity": "monthly",
        "export_format": "csv"
    })
    
    if result.get("success"):
        print("✓ SUCCESS: Report generated successfully!")
        print(f"  Export path: {result.get('export_path')}")
        print(f"  Export format: {result.get('export_format')}")
        print(f"  Currency: {result.get('currency', 'USD')}")
        print(f"  Dimensions used: {result.get('dimensions')}")
        print(f"  Total records: {result.get('total_records', 'N/A')}")
        
        # Show first few lines if CSV
        if result.get("export_format") == "csv" and result.get("export_path"):
            try:
                with open(result.get("export_path"), 'r') as f:
                    lines = f.readlines()[:5]
                    print("\n  First few lines of CSV:")
                    for line in lines:
                        print(f"    {line.strip()}")
            except Exception as e:
                print(f"  Could not read CSV file: {e}")
    else:
        error = result.get('error', '')
        print(f"✗ FAILED: {error}")
        print("\nNote: Tag dimensions may not be supported by the amortized costs API.")
        print("If this fails, try using validated dimensions like vendor, region, etc.")
    print()


async def test_tag_dimensions_json():
    """
    Test tag dimensions with JSON export format.
    """
    print("=" * 80)
    print("TrueCost Explorer - Tag Dimensions (JSON Export)")
    print("=" * 80)
    print("\nConfiguration:")
    print("  Dimensions: tag10, tag3, tag7")
    print("  Filters: container_cluster_name=@mvp01")
    print("  Metric: total_amortized_cost")
    print("  Date Range: 2025-11-01 to 2025-11-19")
    print("  Export Format: JSON")
    print()
    
    server = CloudabilityV2MCPServer()
    
    result = await server.call_tool("get_amortized_costs", {
        "view_name": Config.DEFAULT_VIEW,  # Use default view for testing
        "start_date": "2025-11-01",
        "end_date": "2025-11-19",
        "dimensions": ["tag10", "tag3", "tag7"],
        "metrics": ["total_amortized_cost"],
        "filters": {
            "container_cluster_name": "=@mvp01"
        },
        "granularity": "monthly",
        "export_format": "json"
    })
    
    if result.get("success"):
        print("✓ SUCCESS: Report generated successfully!")
        print(f"  Export path: {result.get('export_path')}")
        print(f"  Export format: {result.get('export_format')}")
        print(f"  Currency: {result.get('currency', 'USD')}")
        print(f"  Total records: {result.get('total_records', 'N/A')}")
        
        # Show sample data
        data = result.get("data", [])
        if isinstance(data, dict) and "data" in data:
            data = data["data"]
        if data and len(data) > 0:
            print(f"\n  Sample data (first record):")
            for key, value in list(data[0].items())[:5]:
                print(f"    {key}: {value}")
    else:
        error = result.get('error', '')
        print(f"✗ FAILED: {error}")
    print()


async def test_conversational_prompt_example():
    """
    Demonstrate how to use this configuration via conversational chatbot in Cursor.
    """
    print("=" * 80)
    print("Conversational Chatbot Usage Example")
    print("=" * 80)
    print("\nYou can use the following prompts in Cursor IDE chat:")
    print()
    print("Example 1:")
    print('  "Get amortized costs for November 2025 grouped by tag10, tag3, and tag7,')
    print('   filtered by container cluster name containing mvp01, export as CSV"')
    print()
    print("Example 2:")
    print('  "Generate a cost report for tag10, tag3, tag7 dimensions with')
    print('   container_cluster_name filter matching mvp01 for dates 2025-11-01 to 2025-11-19"')
    print()
    print("Example 3:")
    print('  "Show me amortized costs by tags (tag10, tag3, tag7) for clusters')
    print('   with mvp01 in the name, for this month, export as JSON"')
    print()
    print("The MCP server will automatically:")
    print("  - Convert natural language to API parameters")
    print("  - Apply filters with wildcard operators")
    print("  - Export reports with USD currency indicators")
    print("  - Save files to generated-contents/<timestamp>/")
    print()


async def main():
    """Run all tag dimension examples"""
    print("\n" + "=" * 80)
    print("TrueCost Explorer - Tag Dimensions Example")
    print("=" * 80)
    print("\nThis example demonstrates converting UI URL configurations to API calls")
    print("with tag dimensions and wildcard filters.\n")
    
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
        sys.exit(1)
    
    try:
        # Test 1: Tag dimensions with filters (CSV)
        await test_tag_dimensions_with_filters()
        
        # Test 2: Tag dimensions with filters (JSON)
        await test_tag_dimensions_json()
        
        # Test 3: Show conversational usage examples
        await test_conversational_prompt_example()
        
        print("=" * 80)
        print("All tag dimension examples completed!")
        print("=" * 80)
        print("\nNote: Check the generated-contents/ folder for exported reports.")
        print("Files are organized by timestamp in subfolders.")
        print("\nTip: Use conversational prompts in Cursor IDE to generate similar reports!")
        
    except Exception as e:
        print(f"\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

