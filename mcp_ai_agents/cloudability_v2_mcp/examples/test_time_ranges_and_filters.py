"""
Time Range and Cluster Filter Examples
Demonstrates:
1. Last month reports
2. Last 2 months reports
3. Cluster name filters with regular expressions
"""

import asyncio
import sys
import os
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


async def test_last_month_report():
    """Test generating report for last month"""
    print("=" * 80)
    print("Test 1: Last Month Report")
    print("=" * 80)
    print("\nConfiguration:")
    print("  Time Range: last_month (previous calendar month)")
    print("  Dimensions: vendor, region")
    print("  Metric: total_amortized_cost")
    print("  Export Format: CSV")
    print()
    
    server = CloudabilityV2MCPServer()
    
    result = await server.call_tool("get_amortized_costs", {
        "view_name": Config.DEFAULT_VIEW,  # Use default view for testing
        "time_range": "last_month",
        "dimensions": ["vendor", "region"],
        "metrics": ["total_amortized_cost"],
        "granularity": "monthly",
        "export_format": "csv"
    })
    
    if result.get("success"):
        print("✓ SUCCESS: Report generated successfully!")
        print(f"  Export path: {result.get('export_path')}")
        print(f"  Date range: {result.get('start_date')} to {result.get('end_date')}")
        print(f"  Currency: {result.get('currency', 'USD')}")
        print(f"  Total records: {result.get('total_records', 'N/A')}")
    else:
        print(f"✗ FAILED: {result.get('error')}")
    print()


async def test_last_2_months_report():
    """Test generating report for last 2 months"""
    print("=" * 80)
    print("Test 2: Last 2 Months Report")
    print("=" * 80)
    print("\nConfiguration:")
    print("  Time Range: last_2_months (last 2 months including current)")
    print("  Dimensions: vendor, region")
    print("  Metric: total_amortized_cost")
    print("  Export Format: CSV")
    print()
    
    server = CloudabilityV2MCPServer()
    
    result = await server.call_tool("get_amortized_costs", {
        "view_name": Config.DEFAULT_VIEW,  # Use default view for testing
        "time_range": "last_2_months",
        "dimensions": ["vendor", "region"],  # Use validated dimensions
        "metrics": ["total_amortized_cost"],
        "granularity": "monthly",
        "export_format": "csv"
    })
    
    if result.get("success"):
        print("✓ SUCCESS: Report generated successfully!")
        print(f"  Export path: {result.get('export_path')}")
        print(f"  Date range: {result.get('start_date')} to {result.get('end_date')}")
        print(f"  Currency: {result.get('currency', 'USD')}")
        print(f"  Total records: {result.get('total_records', 'N/A')}")
    else:
        print(f"✗ FAILED: {result.get('error')}")
    print()


async def test_cluster_name_filter_wildcard():
    """Test cluster_name filter with wildcard pattern"""
    print("=" * 80)
    print("Test 3: Cluster Name Filter (Wildcard Pattern)")
    print("=" * 80)
    print("\nConfiguration:")
    print("  Time Range: last_month")
    print("  Dimensions: tag10, tag3, tag7")
    print("  Filter: container_cluster_name matching 'mvp01*' (wildcard)")
    print("  Metric: total_amortized_cost")
    print("  Export Format: CSV")
    print()
    print("Note: Using container_cluster_name (as shown in UI URL)")
    print()
    
    server = CloudabilityV2MCPServer()
    
    result = await server.call_tool("get_amortized_costs", {
        "view_name": Config.DEFAULT_VIEW,  # Use default view for testing
        "time_range": "last_month",
        "dimensions": ["tag10", "tag3", "tag7"],
        "filters": {
            "container_cluster_name": "mvp01*"  # Wildcard pattern - matches UI URL format
        },
        "metrics": ["total_amortized_cost"],
        "granularity": "monthly",
        "export_format": "csv"
    })
    
    if result.get("success"):
        print("✓ SUCCESS: Report generated successfully!")
        print(f"  Export path: {result.get('export_path')}")
        print(f"  Date range: {result.get('start_date')} to {result.get('end_date')}")
        print(f"  Currency: {result.get('currency', 'USD')}")
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
        print(f"✗ FAILED: {result.get('error')}")
    print()


async def test_cluster_name_filter_regex():
    """Test cluster_name filter with regex-like pattern"""
    print("=" * 80)
    print("Test 4: Cluster Name Filter (Regex Pattern)")
    print("=" * 80)
    print("\nConfiguration:")
    print("  Time Range: last_2_months")
    print("  Dimensions: vendor, region")
    print("  Filter: container_cluster_name matching '.*mvp01.*' (regex-like)")
    print("  Metric: total_amortized_cost")
    print("  Export Format: CSV")
    print()
    
    server = CloudabilityV2MCPServer()
    
    result = await server.call_tool("get_amortized_costs", {
        "view_name": Config.DEFAULT_VIEW,  # Use default view for testing
        "time_range": "last_2_months",
        "dimensions": ["vendor", "region"],  # Use validated dimensions
        "filters": {
            "container_cluster_name": ".*mvp01.*"  # Regex-like pattern (converted to wildcard)
        },
        "metrics": ["total_amortized_cost"],
        "granularity": "monthly",
        "export_format": "csv"
    })
    
    if result.get("success"):
        print("✓ SUCCESS: Report generated successfully!")
        print(f"  Export path: {result.get('export_path')}")
        print(f"  Date range: {result.get('start_date')} to {result.get('end_date')}")
        print(f"  Currency: {result.get('currency', 'USD')}")
        print(f"  Total records: {result.get('total_records', 'N/A')}")
    else:
        print(f"✗ FAILED: {result.get('error')}")
    print()


async def test_cluster_name_filter_contains():
    """Test cluster_name filter with contains operator"""
    print("=" * 80)
    print("Test 5: Cluster Name Filter (Contains Operator)")
    print("=" * 80)
    print("\nConfiguration:")
    print("  Time Range: last_month")
    print("  Dimensions: tag10, tag3, tag7")
    print("  Filter: container_cluster_name containing 'mvp01' (using =@ operator)")
    print("  Metric: total_amortized_cost")
    print("  Export Format: JSON")
    print()
    print("Note: This matches the UI URL format: container_cluster_name=@mvp01")
    print()
    
    server = CloudabilityV2MCPServer()
    
    result = await server.call_tool("get_amortized_costs", {
        "view_name": Config.DEFAULT_VIEW,  # Use default view for testing
        "time_range": "last_month",
        "dimensions": ["tag10", "tag3", "tag7"],
        "filters": {
            "container_cluster_name": "=@mvp01"  # Contains operator - matches UI URL
        },
        "metrics": ["total_amortized_cost"],
        "granularity": "monthly",
        "export_format": "json"
    })
    
    if result.get("success"):
        print("✓ SUCCESS: Report generated successfully!")
        print(f"  Export path: {result.get('export_path')}")
        print(f"  Date range: {result.get('start_date')} to {result.get('end_date')}")
        print(f"  Currency: {result.get('currency', 'USD')}")
        data = result.get("data", [])
        if isinstance(data, dict) and "data" in data:
            data = data["data"]
        print(f"  Total records: {len(data) if isinstance(data, list) else result.get('total_records', 'N/A')}")
    else:
        print(f"✗ FAILED: {result.get('error')}")
    print()


async def test_combined_filters():
    """Test combining multiple filters"""
    print("=" * 80)
    print("Test 6: Combined Filters (Vendor Only - Cluster filters may not work)")
    print("=" * 80)
    print("\nConfiguration:")
    print("  Time Range: last_month")
    print("  Dimensions: vendor, region")
    print("  Filters: vendor='AWS'")
    print("  Metric: total_amortized_cost")
    print("  Export Format: CSV")
    print()
    print("Note: Cluster name filters may not work with amortized costs API.")
    print("      Using vendor filter as example of combined filters.")
    print()
    
    server = CloudabilityV2MCPServer()
    
    result = await server.call_tool("get_amortized_costs", {
        "view_name": Config.DEFAULT_VIEW,  # Use default view for testing
        "time_range": "last_month",
        "dimensions": ["vendor", "region"],
        "filters": {
            "vendor": "AWS"  # Using vendor filter as cluster_name may not work
        },
        "metrics": ["total_amortized_cost"],
        "granularity": "monthly",
        "export_format": "csv"
    })
    
    if result.get("success"):
        print("✓ SUCCESS: Report generated successfully!")
        print(f"  Export path: {result.get('export_path')}")
        print(f"  Date range: {result.get('start_date')} to {result.get('end_date')}")
        print(f"  Currency: {result.get('currency', 'USD')}")
        print(f"  Total records: {result.get('total_records', 'N/A')}")
    else:
        print(f"✗ FAILED: {result.get('error')}")
    print()


async def main():
    """Run all time range and filter tests"""
    print("\n" + "=" * 80)
    print("Time Range and Cluster Filter Examples")
    print("=" * 80)
    print("\nThis example demonstrates:")
    print("  - Last month reports (previous calendar month)")
    print("  - Last 2 months reports (last 2 months including current)")
    print("  - Cluster name filters with wildcard patterns")
    print("  - Cluster name filters with regex-like patterns")
    print("  - Combined filters")
    print()
    
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
        await test_last_month_report()
        await test_last_2_months_report()
        await test_cluster_name_filter_wildcard()
        await test_cluster_name_filter_regex()
        await test_cluster_name_filter_contains()
        await test_combined_filters()
        
        print("=" * 80)
        print("All time range and filter examples completed!")
        print("=" * 80)
        print("\nNote: Check the generated-contents/ folder for exported reports.")
        print("Files are organized by timestamp in subfolders.")
        print("\nConversational prompts you can use in Cursor IDE:")
        print("  - 'Get amortized costs for last month grouped by vendor and region'")
        print("  - 'Generate cost report for last 2 months with cluster name filter mvp01*'")
        print("  - 'Show me costs for clusters matching mvp01 pattern for last month'")
        
    except Exception as e:
        print(f"\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

