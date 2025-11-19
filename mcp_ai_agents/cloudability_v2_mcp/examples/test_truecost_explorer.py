"""
TrueCost Explorer Test Example
Replicates the TrueCost Explorer UI configuration from:
https://app.apptio.com/cloudability#/truecost_explorer

This example demonstrates how to generate reports matching the UI configuration.
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


async def test_truecost_explorer_ui_match():
    """
    Test matching the exact UI configuration from:
    https://app.apptio.com/cloudability#/truecost_explorer
    ?dimensions=lease_type&dimensions=enhanced_service_name
    &dimensions=transaction_type&dimensions=usage_family
    &end_date=2025-11-19&metric=total_amortized_cost
    &relative_period=this_month&start_date=2025-11-01
    
    Note: Some dimensions (lease_type, transaction_type, usage_family) may not
    be supported by the amortized costs API endpoint. This test will validate
    which dimensions actually work.
    """
    print("=" * 80)
    print("TrueCost Explorer Test - UI Configuration Match")
    print("=" * 80)
    print("\nUI Configuration:")
    print("  Dimensions: lease_type, enhanced_service_name, transaction_type, usage_family")
    print("  Metric: total_amortized_cost")
    print("  Date Range: 2025-11-01 to 2025-11-19 (this_month)")
    print("  Export Format: CSV")
    print()
    
    server = CloudabilityV2MCPServer()
    
    # Try the exact UI configuration
    # Note: Some dimensions may not be supported by the API
    result = await server.call_tool("get_amortized_costs", {
        "view_name": Config.DEFAULT_VIEW,  # Use default view for testing
        "start_date": "2025-11-01",
        "end_date": "2025-11-19",
        "dimensions": [
            "lease_type",
            "enhanced_service_name",
            "transaction_type",
            "usage_family"
        ],
        "metrics": ["total_amortized_cost"],
        "granularity": "monthly",
        "export_format": "csv"
    })
    
    if result.get("success"):
        print("✓ SUCCESS: Report generated successfully!")
        print(f"  Export path: {result.get('export_path')}")
        print(f"  Export format: {result.get('export_format')}")
        print(f"  Dimensions used: {result.get('dimensions')}")
        print(f"  Total records: {result.get('total_records', 'N/A')}")
    else:
        error = result.get('error', '')
        print(f"✗ FAILED: {error}")
        print("\nNote: Some dimensions from the UI may not be supported by the API.")
        print("The API may reject cost allocation dimensions (lease_type, transaction_type, usage_family)")
        print("when used with amortized costs.")
    print()


async def test_truecost_explorer_validated_dimensions():
    """
    Test using only validated dimensions that are known to work with amortized costs.
    This version uses enhanced_service_name (which is supported) and other core dimensions.
    """
    print("=" * 80)
    print("TrueCost Explorer Test - Validated Dimensions")
    print("=" * 80)
    print("\nConfiguration (using validated dimensions):")
    print("  Dimensions: enhanced_service_name, vendor, region")
    print("  Metric: total_amortized_cost")
    print("  Date Range: 2025-11-01 to 2025-11-19")
    print("  Export Format: CSV")
    print()
    
    server = CloudabilityV2MCPServer()
    
    # Use validated dimensions that are known to work
    result = await server.call_tool("get_amortized_costs", {
        "view_name": Config.DEFAULT_VIEW,  # Use default view for testing
        "start_date": "2025-11-01",
        "end_date": "2025-11-19",
        "dimensions": [
            "enhanced_service_name",  # From UI - this one works!
            "vendor",                 # Additional dimension for grouping
            "region"                  # Additional dimension for geographic breakdown
        ],
        "metrics": ["total_amortized_cost"],
        "granularity": "monthly",
        "export_format": "csv"
    })
    
    if result.get("success"):
        print("✓ SUCCESS: Report generated successfully!")
        print(f"  Export path: {result.get('export_path')}")
        print(f"  Export format: {result.get('export_format')}")
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
    print()


async def test_truecost_explorer_json_export():
    """
    Test generating the same report but with JSON export format.
    """
    print("=" * 80)
    print("TrueCost Explorer Test - JSON Export")
    print("=" * 80)
    print("\nConfiguration:")
    print("  Dimensions: enhanced_service_name, vendor")
    print("  Metric: total_amortized_cost")
    print("  Date Range: 2025-11-01 to 2025-11-19")
    print("  Export Format: JSON")
    print()
    
    server = CloudabilityV2MCPServer()
    
    result = await server.call_tool("get_amortized_costs", {
        "view_name": Config.DEFAULT_VIEW,  # Use default view for testing
        "start_date": "2025-11-01",
        "end_date": "2025-11-19",
        "dimensions": ["enhanced_service_name", "vendor"],
        "metrics": ["total_amortized_cost"],
        "granularity": "monthly",
        "export_format": "json"
    })
    
    if result.get("success"):
        print("✓ SUCCESS: Report generated successfully!")
        print(f"  Export path: {result.get('export_path')}")
        print(f"  Export format: {result.get('export_format')}")
        print(f"  Total records: {result.get('total_records', 'N/A')}")
        
        # Show sample data
        data = result.get("data", [])
        if data:
            print(f"\n  Sample data (first record):")
            for key, value in list(data[0].items())[:5]:
                print(f"    {key}: {value}")
    else:
        error = result.get('error', '')
        print(f"✗ FAILED: {error}")
    print()


async def test_truecost_explorer_markdown_export():
    """
    Test generating the same report with Markdown export format.
    """
    print("=" * 80)
    print("TrueCost Explorer Test - Markdown Export")
    print("=" * 80)
    print("\nConfiguration:")
    print("  Dimensions: enhanced_service_name")
    print("  Metric: total_amortized_cost")
    print("  Date Range: 2025-11-01 to 2025-11-19")
    print("  Export Format: Markdown")
    print()
    
    server = CloudabilityV2MCPServer()
    
    result = await server.call_tool("get_amortized_costs", {
        "view_name": Config.DEFAULT_VIEW,  # Use default view for testing
        "start_date": "2025-11-01",
        "end_date": "2025-11-19",
        "dimensions": ["enhanced_service_name"],
        "metrics": ["total_amortized_cost"],
        "granularity": "monthly",
        "export_format": "markdown"
    })
    
    if result.get("success"):
        print("✓ SUCCESS: Report generated successfully!")
        print(f"  Export path: {result.get('export_path')}")
        print(f"  Export format: {result.get('export_format')}")
        print(f"  Total records: {result.get('total_records', 'N/A')}")
    else:
        error = result.get('error', '')
        print(f"✗ FAILED: {error}")
    print()


async def main():
    """Run all TrueCost Explorer tests"""
    print("\n" + "=" * 80)
    print("TrueCost Explorer - Test Suite")
    print("=" * 80)
    print("\nThis test suite replicates TrueCost Explorer UI configurations")
    print("and demonstrates various export formats.\n")
    
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
        # Test 1: Try to match exact UI configuration
        await test_truecost_explorer_ui_match()
        
        # Test 2: Use validated dimensions (guaranteed to work)
        await test_truecost_explorer_validated_dimensions()
        
        # Test 3: JSON export
        await test_truecost_explorer_json_export()
        
        # Test 4: Markdown export
        await test_truecost_explorer_markdown_export()
        
        print("=" * 80)
        print("All TrueCost Explorer tests completed!")
        print("=" * 80)
        print("\nNote: Check the generated-contents/ folder for exported reports.")
        print("Files are organized by timestamp in subfolders.")
        
    except Exception as e:
        print(f"\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

