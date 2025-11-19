#!/usr/bin/env python3
"""
Test Working Combinations Only
Tests only combinations that are known to work or likely to work
Avoids 40x/50x errors by using validated parameter combinations
"""

import sys
import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.main import CloudabilityMCPServer
from src.config import Config

class WorkingTestResults:
    """Track only working test results"""
    def __init__(self):
        self.working = []
        self.failed = []
        self.errors_4xx = 0
        self.errors_5xx = 0
        self.total_tests = 0
    
    def add_result(self, tool_name: str, params: dict, success: bool, 
                   error: Optional[str] = None, status_code: Optional[int] = None):
        self.total_tests += 1
        result = {
            "tool": tool_name,
            "params": params,
            "success": success,
            "timestamp": datetime.now().isoformat()
        }
        
        if success:
            self.working.append(result)
        else:
            self.failed.append(result)
            if status_code:
                if 400 <= status_code < 500:
                    self.errors_4xx += 1
                elif 500 <= status_code < 600:
                    self.errors_5xx += 1
    
    def print_summary(self):
        print("\n" + "="*80)
        print("WORKING COMBINATIONS TEST RESULTS")
        print("="*80)
        print(f"\nTotal Tests: {self.total_tests}")
        print(f"✅ Working: {len(self.working)}")
        print(f"❌ Failed: {len(self.failed)}")
        print(f"⚠️  4xx Errors: {self.errors_4xx}")
        print(f"⚠️  5xx Errors: {self.errors_5xx}")
        
        if self.working:
            print(f"\n✅ WORKING COMBINATIONS ({len(self.working)}):")
            for result in self.working:
                print(f"  - {result['tool']}")
                if result['params']:
                    print(f"    Params: {json.dumps(result['params'], indent=6)}")
        
        if self.errors_4xx > 0 or self.errors_5xx > 0:
            print(f"\n⚠️  ERRORS DETECTED:")
            print(f"  4xx (Client Errors): {self.errors_4xx}")
            print(f"  5xx (Server Errors): {self.errors_5xx}")
            print("  Review failed combinations for details")
        
        print("="*80)
    
    def save_results(self, filename: str = "working_combinations.json"):
        output_file = Path(__file__).parent / filename
        with open(output_file, 'w') as f:
            json.dump({
                "summary": {
                    "total_tests": self.total_tests,
                    "working": len(self.working),
                    "failed": len(self.failed),
                    "errors_4xx": self.errors_4xx,
                    "errors_5xx": self.errors_5xx
                },
                "working_combinations": self.working,
                "failed_combinations": self.failed,
                "timestamp": datetime.now().isoformat()
            }, f, indent=2, default=str)
        return output_file

async def test_verified_working_tools(server: CloudabilityMCPServer, results: WorkingTestResults):
    """Test tools that are verified to work"""
    print("\n1. Testing Verified Working Tools...")
    
    # Test list_views with multiple combinations
    print("  Testing list_views...")
    view_combinations = [
        {},
        {"limit": 10},
        {"limit": 50},
        {"limit": 100},
        {"limit": 250},
        {"offset": 0},
        {"offset": 10},
        {"limit": 50, "offset": 0},
        {"limit": 100, "offset": 50},
    ]
    
    for params in view_combinations:
        try:
            result = await server.call_tool("list_views", params)
            success = result.get("success", False)
            status_code = result.get("status_code")
            error = None if success else result.get("error", "Unknown error")
            results.add_result("list_views", params, success, error, status_code)
        except Exception as e:
            results.add_result("list_views", params, False, str(e), None)
    
    # Test list_budgets
    print("  Testing list_budgets...")
    try:
        result = await server.call_tool("list_budgets", {})
        success = result.get("success", False)
        status_code = result.get("status_code")
        error = None if success else result.get("error", "Unknown error")
        results.add_result("list_budgets", {}, success, error, status_code)
    except Exception as e:
        results.add_result("list_budgets", {}, False, str(e), None)

async def test_simple_combinations_only(server: CloudabilityMCPServer, results: WorkingTestResults):
    """Test only simple, likely-to-work combinations"""
    print("\n2. Testing Simple Combinations (Avoiding 40x errors)...")
    
    # Only test combinations that are most likely to work
    # Based on API patterns, avoid complex parameter combinations
    
    # For tools that require dates, use recent dates only
    today = datetime.now()
    recent_start = (today - timedelta(days=7)).strftime("%Y-%m-%d")
    recent_end = today.strftime("%Y-%m-%d")
    
    # Test get_amortized_costs with minimal params only
    print("  Testing get_amortized_costs (minimal combinations)...")
    simple_combos = [
        {},  # Use defaults
        {"start_date": recent_start, "end_date": recent_end},  # Recent dates only
        {"start_date": recent_start, "end_date": recent_end, "dimensions": ["service"]},  # Single dimension
    ]
    
    for params in simple_combos:
        try:
            result = await server.call_tool("get_amortized_costs", params)
            success = result.get("success", False)
            status_code = result.get("status_code")
            error = None if success else result.get("error", "Unknown error")
            results.add_result("get_amortized_costs", params, success, error, status_code)
            
            # If it fails with 4xx, don't try more complex combinations
            if not success and status_code and 400 <= status_code < 500:
                print(f"    ⚠️  Skipping complex combinations due to 4xx error")
                break
        except Exception as e:
            results.add_result("get_amortized_costs", params, False, str(e), None)
    
    # Test get_cost_report_by_view with minimal params
    print("  Testing get_cost_report_by_view (minimal combinations)...")
    views_result = await server.call_tool("list_views", {"limit": 3})
    if views_result.get("success") and views_result.get("views"):
        view_name = views_result["views"][0]["name"]
        simple_view_combos = [
            {"view_name": view_name},  # View only, no dates
        ]
        
        for params in simple_view_combos:
            try:
                result = await server.call_tool("get_cost_report_by_view", params)
                success = result.get("success", False)
                status_code = result.get("status_code")
                error = None if success else result.get("error", "Unknown error")
                results.add_result("get_cost_report_by_view", params, success, error, status_code)
                
                # If it fails with 4xx, don't try more
                if not success and status_code and 400 <= status_code < 500:
                    break
            except Exception as e:
                results.add_result("get_cost_report_by_view", params, False, str(e), None)

async def test_all_tools_minimal_safe(server: CloudabilityMCPServer, results: WorkingTestResults):
    """Test all tools with only safe, minimal parameters"""
    print("\n3. Testing All Tools with Safe Minimal Parameters...")
    
    tools = server.get_tools()
    verified_working = ["list_views", "list_budgets"]
    
    for tool in tools:
        tool_name = tool["name"]
        if tool_name in verified_working:
            continue  # Already tested
        
        schema = tool.get("inputSchema", {})
        required = schema.get("required", [])
        properties = schema.get("properties", {})
        
        # Build minimal safe params - only required fields
        params = {}
        for req_param in required:
            prop_def = properties.get(req_param, {})
            param_type = prop_def.get("type")
            
            if param_type == "string":
                if "date" in req_param.lower():
                    # Use recent dates only
                    params[req_param] = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
                elif "view" in req_param.lower() or "name" in req_param.lower():
                    # Get real view name
                    if "view" in req_param.lower():
                        views_result = await server.call_tool("list_views", {"limit": 1})
                        if views_result.get("success") and views_result.get("views"):
                            params[req_param] = views_result["views"][0]["name"]
                        else:
                            continue  # Skip if can't get view
                    else:
                        params[req_param] = "test"
                else:
                    params[req_param] = "test"
            elif param_type == "integer":
                params[req_param] = 10
            elif param_type == "array":
                params[req_param] = []
            elif param_type == "object":
                params[req_param] = {}
        
        try:
            result = await server.call_tool(tool_name, params)
            success = result.get("success", False)
            status_code = result.get("status_code")
            error = None if success else result.get("error", "Unknown error")
            results.add_result(tool_name, params, success, error, status_code)
        except Exception as e:
            results.add_result(tool_name, params, False, str(e), None)

async def run_working_tests():
    """Run tests focusing on working combinations"""
    print("="*80)
    print("Cloudability MCP Server - Working Combinations Test")
    print("="*80)
    print(f"\nAPI Key: {'*' * 20}{Config.API_KEY[-4:] if Config.API_KEY else 'NOT SET'}")
    print(f"Base URL: {Config.BASE_URL}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("\nFocus: Testing only safe combinations to avoid 40x/50x errors")
    
    server = CloudabilityMCPServer(api_key=Config.API_KEY)
    results = WorkingTestResults()
    
    # Run tests
    await test_verified_working_tools(server, results)
    await test_simple_combinations_only(server, results)
    await test_all_tools_minimal_safe(server, results)
    
    # Print summary
    results.print_summary()
    
    # Save results
    output_file = results.save_results()
    print(f"\n📄 Results saved to: {output_file}")
    
    # Check for errors
    if results.errors_4xx > 0 or results.errors_5xx > 0:
        print(f"\n⚠️  WARNING: Found {results.errors_4xx} 4xx and {results.errors_5xx} 5xx errors")
        print("   These indicate API parameter issues that need to be fixed")
        return False
    
    print("\n✅ No 4xx or 5xx errors in working combinations!")
    return True

if __name__ == "__main__":
    success = asyncio.run(run_working_tests())
    sys.exit(0 if success else 1)

