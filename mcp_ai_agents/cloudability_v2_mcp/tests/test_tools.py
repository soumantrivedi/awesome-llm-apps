"""
Test suite for Cloudability V2 MCP Server tools
Validates that tools work correctly and don't throw 4xx or 5xx errors
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from main import CloudabilityV2MCPServer
from config import Config


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
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "dimensions": ["vendor"],
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


async def test_get_amortized_costs_service(results: TestResults):
    """Test get_amortized_costs with service dimension"""
    test_name = "get_amortized_costs (service dimension)"
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        server = CloudabilityV2MCPServer()
        result = await server.call_tool("get_amortized_costs", {
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "dimensions": ["service"],
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
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "dimensions": ["region"],
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
    """Test get_amortized_costs with invalid dimension (should fail gracefully)"""
    test_name = "get_amortized_costs (invalid dimension - should fail)"
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        server = CloudabilityV2MCPServer()
        result = await server.call_tool("get_amortized_costs", {
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "dimensions": ["cluster_name"],  # Invalid dimension
            "granularity": "monthly"
        })
        
        # This should fail with a validation error, not an HTTP error
        if result.get("success"):
            results.add_fail(test_name, "Should have failed with invalid dimension")
            return
        
        # Should have a validation error, not an HTTP error
        if result.get("status_code") and result.get("status_code") >= 400:
            # This is acceptable - API rejected it
            results.add_pass(test_name)
        elif "Invalid dimensions" in result.get("error", ""):
            # Validation error is also acceptable
            results.add_pass(test_name)
        else:
            results.add_fail(test_name, f"Unexpected error: {result.get('error')}")
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
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "dimensions": ["vendor"],
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
    
    results = TestResults()
    
    # Run tests
    await test_list_views(results)
    await test_list_budgets(results)
    await test_get_amortized_costs_vendor(results)
    await test_get_amortized_costs_service(results)
    await test_get_amortized_costs_region(results)
    await test_get_amortized_costs_invalid_dimension(results)
    await test_get_amortized_costs_csv(results)
    
    # Print summary
    success = results.summary()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())

