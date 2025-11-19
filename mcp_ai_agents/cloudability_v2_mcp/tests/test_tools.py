"""
Test suite for Cloudability V2 MCP Server tools
Validates that tools work correctly and don't throw 4xx or 5xx errors
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
import json
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


class TestResults:
    """Track test results"""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def add_pass(self, test_name: str):
        """Record a passing test"""
        self.passed += 1
        print(f"✓ PASS: {test_name}")
    
    def add_fail(self, test_name: str, error: str):
        """Record a failing test"""
        self.failed += 1
        self.errors.append(f"{test_name}: {error}")
        print(f"✗ FAIL: {test_name} - {error}")
    
    def summary(self):
        """Print test summary"""
        print("\n" + "=" * 80)
        print("Test Summary")
        print("=" * 80)
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")
        if self.errors:
            print("\nErrors:")
            for error in self.errors:
                print(f"  - {error}")
        print("=" * 80)
        
        return self.failed == 0


async def test_list_views(results: TestResults):
    """Test list_views tool"""
    test_name = "list_views"
    try:
        server = CloudabilityV2MCPServer()
        result = await server.call_tool("list_views", {"limit": 10})
        
        if not result.get("success"):
            results.add_fail(test_name, f"Tool returned success=False: {result.get('error')}")
            return
        
        # Check for HTTP errors
        if result.get("status_code") and result.get("status_code") >= 400:
            results.add_fail(test_name, f"HTTP {result.get('status_code')} error: {result.get('error')}")
            return
        
        # Validate response structure
        if "views" not in result:
            results.add_fail(test_name, "Response missing 'views' field")
            return
        
        results.add_pass(test_name)
    except Exception as e:
        results.add_fail(test_name, f"Exception: {str(e)}")


async def test_list_budgets(results: TestResults):
    """Test list_budgets tool"""
    test_name = "list_budgets"
    try:
        server = CloudabilityV2MCPServer()
        result = await server.call_tool("list_budgets", {})
        
        if not result.get("success"):
            results.add_fail(test_name, f"Tool returned success=False: {result.get('error')}")
            return
        
        # Check for HTTP errors
        if result.get("status_code") and result.get("status_code") >= 400:
            results.add_fail(test_name, f"HTTP {result.get('status_code')} error: {result.get('error')}")
            return
        
        # Validate response structure
        if "budgets" not in result:
            results.add_fail(test_name, "Response missing 'budgets' field")
            return
        
        results.add_pass(test_name)
    except Exception as e:
        results.add_fail(test_name, f"Exception: {str(e)}")


async def test_get_amortized_costs_vendor(results: TestResults):
    """Test get_amortized_costs with vendor dimension"""
    test_name = "get_amortized_costs (vendor dimension)"
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        server = CloudabilityV2MCPServer()
        result = await server.call_tool("get_amortized_costs", {
            "view_name": Config.DEFAULT_VIEW,  # Use default view for testing
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "dimensions": ["vendor"],
            "metrics": ["total_amortized_cost"],  # Explicitly use amortized cost
            "granularity": "monthly"
        })
        
        if not result.get("success"):
            results.add_fail(test_name, f"Tool returned success=False: {result.get('error')}")
            return
        
        # Check for HTTP errors
        if result.get("status_code") and result.get("status_code") >= 400:
            results.add_fail(test_name, f"HTTP {result.get('status_code')} error: {result.get('error')}")
            return
        
        results.add_pass(test_name)
    except Exception as e:
        results.add_fail(test_name, f"Exception: {str(e)}")


async def test_get_amortized_costs_multiple_dimensions(results: TestResults):
    """Test get_amortized_costs with multiple verified dimensions"""
    test_name = "get_amortized_costs (vendor + region dimensions)"
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        server = CloudabilityV2MCPServer()
        result = await server.call_tool("get_amortized_costs", {
            "view_name": Config.DEFAULT_VIEW,  # Use default view for testing
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "dimensions": ["vendor", "region"],  # Use verified working dimensions
            "metrics": ["total_amortized_cost"],  # Explicitly use amortized cost
            "granularity": "monthly"
        })
        
        if not result.get("success"):
            results.add_fail(test_name, f"Tool returned success=False: {result.get('error')}")
            return
        
        # Check for HTTP errors
        if result.get("status_code") and result.get("status_code") >= 400:
            results.add_fail(test_name, f"HTTP {result.get('status_code')} error: {result.get('error')}")
            return
        
        results.add_pass(test_name)
    except Exception as e:
        results.add_fail(test_name, f"Exception: {str(e)}")


async def test_get_amortized_costs_region(results: TestResults):
    """Test get_amortized_costs with region dimension"""
    test_name = "get_amortized_costs (region dimension)"
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        server = CloudabilityV2MCPServer()
        result = await server.call_tool("get_amortized_costs", {
            "view_name": Config.DEFAULT_VIEW,  # Use default view for testing
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "dimensions": ["region"],
            "metrics": ["total_amortized_cost"],  # Explicitly use amortized cost
            "granularity": "monthly"
        })
        
        if not result.get("success"):
            results.add_fail(test_name, f"Tool returned success=False: {result.get('error')}")
            return
        
        # Check for HTTP errors
        if result.get("status_code") and result.get("status_code") >= 400:
            results.add_fail(test_name, f"HTTP {result.get('status_code')} error: {result.get('error')}")
            return
        
        results.add_pass(test_name)
    except Exception as e:
        results.add_fail(test_name, f"Exception: {str(e)}")


async def test_get_amortized_costs_invalid_dimension(results: TestResults):
    """Test get_amortized_costs with invalid dimension (should fail with validation error)"""
    test_name = "get_amortized_costs (invalid dimension - validation)"
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        server = CloudabilityV2MCPServer()
        result = await server.call_tool("get_amortized_costs", {
            "view_name": Config.DEFAULT_VIEW,  # Use default view for testing
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "dimensions": ["cluster_name"],  # Invalid dimension - should be rejected
            "metrics": ["total_amortized_cost"],  # Explicitly use amortized cost
            "granularity": "monthly"
        })
        
        # This should fail with a validation error BEFORE making API call
        if result.get("success"):
            results.add_fail(test_name, "Should have failed with invalid dimension validation")
            return
        
        # Should have a validation error (not an HTTP error, since validation happens before API call)
        error_msg = result.get("error", "")
        if "Invalid dimensions" in error_msg or "cluster_name" in error_msg:
            # Validation error is correct - tool rejected it before API call
            results.add_pass(test_name)
        elif result.get("status_code") and result.get("status_code") >= 400:
            # API rejected it (less ideal but acceptable)
            results.add_pass(test_name)
        else:
            results.add_fail(test_name, f"Unexpected error: {error_msg}")
    except Exception as e:
        results.add_fail(test_name, f"Exception: {str(e)}")


async def test_get_amortized_costs_csv(results: TestResults):
    """Test get_amortized_costs with CSV export"""
    test_name = "get_amortized_costs (CSV export)"
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        server = CloudabilityV2MCPServer()
        result = await server.call_tool("get_amortized_costs", {
            "view_name": Config.DEFAULT_VIEW,  # Use default view for testing
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "dimensions": ["vendor"],
            "metrics": ["total_amortized_cost"],  # Explicitly use amortized cost
            "granularity": "monthly",
            "export_format": "csv"
        })
        
        if not result.get("success"):
            results.add_fail(test_name, f"Tool returned success=False: {result.get('error')}")
            return
        
        # Check for HTTP errors
        if result.get("status_code") and result.get("status_code") >= 400:
            results.add_fail(test_name, f"HTTP {result.get('status_code')} error: {result.get('error')}")
            return
        
        # Check for CSV export
        if result.get("export_format") != "csv":
            results.add_fail(test_name, "Export format is not CSV")
            return
        
        if not result.get("export_path") and not result.get("csv_data"):
            results.add_fail(test_name, "No CSV data or export path")
            return
        
        results.add_pass(test_name)
    except Exception as e:
        results.add_fail(test_name, f"Exception: {str(e)}")


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
    
    results = TestResults()
    
    # Run tests
    await test_list_views(results)
    await test_list_budgets(results)
    await test_get_amortized_costs_vendor(results)
    await test_get_amortized_costs_region(results)
    await test_get_amortized_costs_multiple_dimensions(results)
    await test_get_amortized_costs_invalid_dimension(results)
    await test_get_amortized_costs_csv(results)
    
    # Print summary
    success = results.summary()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())

