#!/usr/bin/env python3
"""
Test API Parameter Combinations
Identifies which parameter combinations work with Cloudability API
"""

import sys
import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.main import CloudabilityMCPServer
from src.config import Config

class APITestResults:
    """Track test results"""
    def __init__(self):
        self.working = []
        self.failing = []
        self.errors = {}
    
    def add_result(self, test_name, success, error=None, params=None):
        result = {
            "test_name": test_name,
            "params": params or {},
            "success": success
        }
        if success:
            self.working.append(result)
        else:
            self.failing.append(result)
            if error:
                self.errors[test_name] = str(error)
    
    def print_summary(self):
        print("\n" + "="*80)
        print("API COMBINATION TEST RESULTS")
        print("="*80)
        print(f"\n✅ Working combinations: {len(self.working)}")
        print(f"❌ Failing combinations: {len(self.failing)}")
        
        if self.working:
            print("\n✅ WORKING COMBINATIONS:")
            for result in self.working:
                print(f"  - {result['test_name']}")
                if result.get('params'):
                    print(f"    Params: {json.dumps(result['params'], indent=6)}")
        
        if self.failing:
            print("\n❌ FAILING COMBINATIONS:")
            for result in self.failing:
                print(f"  - {result['test_name']}")
                error = self.errors.get(result['test_name'], 'Unknown error')
                print(f"    Error: {error[:100]}")
        
        print("\n" + "="*80)

async def test_list_views(results: APITestResults):
    """Test list_views tool"""
    server = CloudabilityMCPServer(api_key=Config.API_KEY)
    
    try:
        result = await server.call_tool("list_views", {"limit": 10})
        results.add_result("list_views", result.get("success"), 
                          error=None if result.get("success") else result.get("error"),
                          params={"limit": 10})
    except Exception as e:
        results.add_result("list_views", False, error=str(e))

async def test_get_amortized_costs_combinations(results: APITestResults):
    """Test various combinations for get_amortized_costs"""
    server = CloudabilityMCPServer(api_key=Config.API_KEY)
    
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    
    # Test 1: Basic call with defaults
    try:
        result = await server.call_tool("get_amortized_costs", {})
        results.add_result("get_amortized_costs (defaults)", result.get("success"),
                          error=None if result.get("success") else result.get("error"))
    except Exception as e:
        results.add_result("get_amortized_costs (defaults)", False, error=str(e))
    
    # Test 2: With date range only
    try:
        result = await server.call_tool("get_amortized_costs", {
            "start_date": start_date,
            "end_date": end_date
        })
        results.add_result("get_amortized_costs (dates only)", result.get("success"),
                          error=None if result.get("success") else result.get("error"),
                          params={"start_date": start_date, "end_date": end_date})
    except Exception as e:
        results.add_result("get_amortized_costs (dates only)", False, error=str(e))
    
    # Test 3: With product_id filter only
    try:
        result = await server.call_tool("get_amortized_costs", {
            "start_date": start_date,
            "end_date": end_date,
            "filters": {"product_id": "K8s"}
        })
        results.add_result("get_amortized_costs (product_id filter)", result.get("success"),
                          error=None if result.get("success") else result.get("error"),
                          params={"filters": {"product_id": "K8s"}})
    except Exception as e:
        results.add_result("get_amortized_costs (product_id filter)", False, error=str(e))
    
    # Test 4: With view only (no filters)
    try:
        views_result = await server.call_tool("list_views", {"limit": 5})
        if views_result.get("success") and views_result.get("views"):
            view_name = views_result["views"][0]["name"]
            result = await server.call_tool("get_amortized_costs", {
                "start_date": start_date,
                "end_date": end_date,
                "view_name": view_name
            })
            results.add_result("get_amortized_costs (view only)", result.get("success"),
                              error=None if result.get("success") else result.get("error"),
                              params={"view_name": view_name})
    except Exception as e:
        results.add_result("get_amortized_costs (view only)", False, error=str(e))
    
    # Test 5: With dimensions
    try:
        result = await server.call_tool("get_amortized_costs", {
            "start_date": start_date,
            "end_date": end_date,
            "dimensions": ["service", "vendor"]
        })
        results.add_result("get_amortized_costs (multiple dimensions)", result.get("success"),
                          error=None if result.get("success") else result.get("error"),
                          params={"dimensions": ["service", "vendor"]})
    except Exception as e:
        results.add_result("get_amortized_costs (multiple dimensions)", False, error=str(e))
    
    # Test 6: Daily granularity
    try:
        result = await server.call_tool("get_amortized_costs", {
            "start_date": start_date,
            "end_date": end_date,
            "granularity": "daily"
        })
        results.add_result("get_amortized_costs (daily granularity)", result.get("success"),
                          error=None if result.get("success") else result.get("error"),
                          params={"granularity": "daily"})
    except Exception as e:
        results.add_result("get_amortized_costs (daily granularity)", False, error=str(e))

async def test_get_cost_report_by_view(results: APITestResults):
    """Test get_cost_report_by_view"""
    server = CloudabilityMCPServer(api_key=Config.API_KEY)
    
    # Get a view first
    views_result = await server.call_tool("list_views", {"limit": 5})
    if not views_result.get("success") or not views_result.get("views"):
        results.add_result("get_cost_report_by_view", False, error="No views available")
        return
    
    view_name = views_result["views"][0]["name"]
    
    # Test 1: Basic call
    try:
        result = await server.call_tool("get_cost_report_by_view", {
            "view_name": view_name
        })
        results.add_result("get_cost_report_by_view (basic)", result.get("success"),
                          error=None if result.get("success") else result.get("error"),
                          params={"view_name": view_name})
    except Exception as e:
        results.add_result("get_cost_report_by_view (basic)", False, error=str(e))
    
    # Test 2: With limit
    try:
        result = await server.call_tool("get_cost_report_by_view", {
            "view_name": view_name,
            "limit": 10
        })
        results.add_result("get_cost_report_by_view (with limit)", result.get("success"),
                          error=None if result.get("success") else result.get("error"),
                          params={"view_name": view_name, "limit": 10})
    except Exception as e:
        results.add_result("get_cost_report_by_view (with limit)", False, error=str(e))

async def test_all_tools(results: APITestResults):
    """Test all available tools"""
    server = CloudabilityMCPServer(api_key=Config.API_KEY)
    tools = server.get_tools()
    
    print(f"\nTesting {len(tools)} tools...")
    
    for tool in tools:
        tool_name = tool["name"]
        print(f"  Testing {tool_name}...")
        
        # Get schema to understand required params
        schema = tool.get("inputSchema", {})
        required = schema.get("required", [])
        properties = schema.get("properties", {})
        
        # Build minimal params
        params = {}
        for prop_name, prop_def in properties.items():
            if prop_name in required:
                # Try to provide a default value based on type
                prop_type = prop_def.get("type")
                if prop_type == "string":
                    if "date" in prop_name.lower():
                        params[prop_name] = datetime.now().strftime("%Y-%m-%d")
                    else:
                        params[prop_name] = "test"
                elif prop_type == "integer":
                    params[prop_name] = 10
                elif prop_type == "array":
                    params[prop_name] = []
                elif prop_type == "object":
                    params[prop_name] = {}
        
        try:
            result = await server.call_tool(tool_name, params)
            success = result.get("success", False)
            error = None if success else result.get("error", "Unknown error")
            results.add_result(tool_name, success, error=error, params=params)
        except Exception as e:
            results.add_result(tool_name, False, error=str(e), params=params)

async def main():
    """Run all API combination tests"""
    print("="*80)
    print("Cloudability MCP Server - API Combination Tests")
    print("="*80)
    print(f"\nAPI Key: {'*' * 20}{Config.API_KEY[-4:] if Config.API_KEY else 'NOT SET'}")
    print(f"Base URL: {Config.BASE_URL}")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = APITestResults()
    
    # Run tests
    print("\n1. Testing list_views...")
    await test_list_views(results)
    
    print("\n2. Testing get_amortized_costs combinations...")
    await test_get_amortized_costs_combinations(results)
    
    print("\n3. Testing get_cost_report_by_view...")
    await test_get_cost_report_by_view(results)
    
    print("\n4. Testing all tools...")
    await test_all_tools(results)
    
    # Print summary
    results.print_summary()
    
    # Save results to file
    output_file = Path(__file__).parent / "api_test_results.json"
    with open(output_file, 'w') as f:
        json.dump({
            "working": results.working,
            "failing": results.failing,
            "errors": results.errors,
            "timestamp": datetime.now().isoformat()
        }, f, indent=2, default=str)
    
    print(f"\n📄 Results saved to: {output_file}")
    
    return len(results.failing) == 0

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)

