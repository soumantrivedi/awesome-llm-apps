"""
View Filtering Examples
Demonstrates how to use view_name parameter for access control when generating cost reports.
Views ensure users only see data they have access to.
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


async def test_list_views_first():
    """First, list available views to see what the user has access to"""
    print("=" * 80)
    print("Step 1: List Available Views")
    print("=" * 80)
    print("\nThis shows all views the user has access to.")
    print("Always use a view_name when generating cost reports for proper access control.\n")
    
    server = CloudabilityV2MCPServer()
    
    result = await server.call_tool("list_views", {"limit": 10})
    
    if result.get("success"):
        views = result.get("views", [])
        print(f"✓ Found {len(views)} views (showing first 10):")
        print()
        for i, view in enumerate(views[:10], 1):
            view_id = view.get("id") or view.get("view_id", "N/A")
            view_name = view.get("title") or view.get("name") or view.get("displayName", "N/A")
            print(f"  {i}. ID: {view_id}, Name: {view_name}")
        
        if len(views) > 0:
            # Store first view for use in next test
            first_view = views[0]
            view_name = first_view.get("title") or first_view.get("name") or first_view.get("displayName")
            print(f"\n  → Using first view '{view_name}' for next example")
            return view_name
    else:
        print(f"✗ FAILED: {result.get('error')}")
    
    print()
    return None


async def test_amortized_costs_with_view(view_name: str):
    """Test generating amortized costs report with view filtering"""
    print("=" * 80)
    print("Step 2: Generate Cost Report with View Filtering")
    print("=" * 80)
    print("\nConfiguration:")
    print(f"  View Name: {view_name} (for access control)")
    print("  Time Range: last_month")
    print("  Dimensions: vendor, region")
    print("  Metric: total_amortized_cost")
    print("  Export Format: CSV")
    print()
    
    server = CloudabilityV2MCPServer()
    
    result = await server.call_tool("get_amortized_costs", {
        "view_name": view_name,  # IMPORTANT: Filter by view for access control
        "time_range": "last_month",
        "dimensions": ["vendor", "region"],
        "metrics": ["total_amortized_cost"],
        "granularity": "monthly",
        "export_format": "csv"
    })
    
    if result.get("success"):
        print("✓ SUCCESS: Report generated successfully!")
        print(f"  View used: {result.get('view_name', view_name)}")
        print(f"  Export path: {result.get('export_path')}")
        print(f"  Date range: {result.get('start_date')} to {result.get('end_date')}")
        print(f"  Currency: {result.get('currency', 'USD')}")
        print(f"  Note: {result.get('note', 'N/A')}")
        print(f"  Total records: {result.get('total_records', 'N/A')}")
    else:
        print(f"✗ FAILED: {result.get('error')}")
    print()


async def test_amortized_costs_with_view_and_filters(view_name: str):
    """Test generating report with view and additional filters"""
    print("=" * 80)
    print("Step 3: Cost Report with View + Cluster Filter")
    print("=" * 80)
    print("\nConfiguration:")
    print(f"  View Name: {view_name} (for access control)")
    print("  Time Range: last_month")
    print("  Dimensions: tag10, tag3, tag7")
    print("  Filters: container_cluster_name containing 'mvp01'")
    print("  Metric: total_amortized_cost")
    print("  Export Format: CSV")
    print()
    
    server = CloudabilityV2MCPServer()
    
    result = await server.call_tool("get_amortized_costs", {
        "view_name": view_name,  # IMPORTANT: Filter by view first
        "time_range": "last_month",
        "dimensions": ["tag10", "tag3", "tag7"],
        "filters": {
            "container_cluster_name": "=@mvp01"  # Additional filter
        },
        "metrics": ["total_amortized_cost"],
        "granularity": "monthly",
        "export_format": "csv"
    })
    
    if result.get("success"):
        print("✓ SUCCESS: Report generated successfully!")
        print(f"  View used: {result.get('view_name', view_name)}")
        print(f"  Export path: {result.get('export_path')}")
        print(f"  Date range: {result.get('start_date')} to {result.get('end_date')}")
        print(f"  Currency: {result.get('currency', 'USD')}")
        print(f"  Total records: {result.get('total_records', 'N/A')}")
    else:
        print(f"✗ FAILED: {result.get('error')}")
    print()


async def test_amortized_costs_without_view_warning():
    """Test what happens when view is not specified"""
    print("=" * 80)
    print("Step 4: Cost Report WITHOUT View (Not Recommended)")
    print("=" * 80)
    print("\nConfiguration:")
    print("  View Name: NOT SPECIFIED (not recommended)")
    print("  Time Range: last_month")
    print("  Dimensions: vendor")
    print("  Metric: total_amortized_cost")
    print("  Export Format: CSV")
    print()
    print("⚠️  WARNING: No view_name specified. This may:")
    print("    - Return data the user doesn't have access to")
    print("    - Cause permission errors")
    print("    - Return incomplete or incorrect data")
    print()
    
    server = CloudabilityV2MCPServer()
    
    result = await server.call_tool("get_amortized_costs", {
        # No view_name - not recommended
        "time_range": "last_month",
        "dimensions": ["vendor"],
        "metrics": ["total_amortized_cost"],
        "granularity": "monthly",
        "export_format": "csv"
    })
    
    if result.get("success"):
        print("✓ Report generated (but view filtering is recommended for access control)")
        print(f"  Export path: {result.get('export_path')}")
        print(f"  Date range: {result.get('start_date')} to {result.get('end_date')}")
    else:
        print(f"✗ FAILED: {result.get('error')}")
        print("  This may be due to missing view_name for access control.")
    print()


async def main():
    """Run all view filtering examples"""
    print("\n" + "=" * 80)
    print("View Filtering Examples - Access Control")
    print("=" * 80)
    print("\nThis example demonstrates:")
    print("  - Listing available views (to see what user has access to)")
    print("  - Using view_name parameter for access control")
    print("  - Combining view filtering with other filters")
    print("  - Why view filtering is important for multi-user environments")
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
        # Step 1: List views
        view_name = await test_list_views_first()
        
        if view_name:
            # Step 2: Use view for cost report
            await test_amortized_costs_with_view(view_name)
            
            # Step 3: Use view with additional filters
            await test_amortized_costs_with_view_and_filters(view_name)
        else:
            print("⚠️  Could not retrieve views. Skipping view-based examples.")
        
        # Step 4: Show what happens without view (warning)
        await test_amortized_costs_without_view_warning()
        
        print("=" * 80)
        print("All view filtering examples completed!")
        print("=" * 80)
        print("\nBest Practices:")
        print("  1. Always use 'list_views' first to see available views")
        print("  2. Always specify 'view_name' when generating cost reports")
        print("  3. Views ensure users only see data they have access to")
        print("  4. Views can be combined with additional filters")
        print()
        print("Conversational prompts in Cursor IDE:")
        print("  - 'List all views I have access to'")
        print("  - 'Get amortized costs for view [View Name] for last month'")
        print("  - 'Generate cost report for view [View Name] with cluster filter mvp01*'")
        
    except Exception as e:
        print(f"\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

