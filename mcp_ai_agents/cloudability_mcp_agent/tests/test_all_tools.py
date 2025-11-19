#!/usr/bin/env python3
"""
Comprehensive Test Suite for All Cloudability MCP Tools
Tests each tool with valid parameters and documents working combinations
"""

import sys
import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.main import CloudabilityMCPServer
from src.config import Config

class ToolTestResult:
    """Test result for a single tool"""
    def __init__(self, tool_name: str):
        self.tool_name = tool_name
        self.success = False
        self.error = None
        self.params_used = {}
        self.response = None
        self.status_code = None
    
    def to_dict(self):
        return {
            "tool_name": self.tool_name,
            "success": self.success,
            "error": self.error,
            "params_used": self.params_used,
            "status_code": self.status_code
        }

async def test_tool(server: CloudabilityMCPServer, tool_name: str, params: dict) -> ToolTestResult:
    """Test a single tool with given parameters"""
    result = ToolTestResult(tool_name)
    result.params_used = params
    
    try:
        response = await server.call_tool(tool_name, params)
        result.response = response
        result.success = response.get("success", False)
        
        if not result.success:
            result.error = response.get("error", "Unknown error")
            result.status_code = response.get("status_code")
            
            # Extract error details
            error_detail = response.get("error_detail", {})
            if isinstance(error_detail, dict):
                error_obj = error_detail.get("error", {})
                if isinstance(error_obj, dict):
                    result.status_code = error_obj.get("status") or result.status_code
    except Exception as e:
        result.success = False
        result.error = str(e)
    
    return result

async def test_list_views(server: CloudabilityMCPServer) -> ToolTestResult:
    """Test list_views tool"""
    return await test_tool(server, "list_views", {"limit": 10})

async def test_list_budgets(server: CloudabilityMCPServer) -> ToolTestResult:
    """Test list_budgets tool"""
    return await test_tool(server, "list_budgets", {})

async def test_get_amortized_costs(server: CloudabilityMCPServer) -> list[ToolTestResult]:
    """Test get_amortized_costs with various combinations"""
    results = []
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    
    # Test 1: Minimal params (should use defaults)
    results.append(await test_tool(server, "get_amortized_costs", {}))
    
    # Test 2: With explicit dates
    results.append(await test_tool(server, "get_amortized_costs", {
        "start_date": start_date,
        "end_date": end_date
    }))
    
    # Test 3: With dimensions only
    results.append(await test_tool(server, "get_amortized_costs", {
        "start_date": start_date,
        "end_date": end_date,
        "dimensions": ["service"]
    }))
    
    return results

async def test_get_cost_report_by_view(server: CloudabilityMCPServer) -> list[ToolTestResult]:
    """Test get_cost_report_by_view"""
    results = []
    
    # First get a view
    views_result = await server.call_tool("list_views", {"limit": 5})
    if views_result.get("success") and views_result.get("views"):
        view_name = views_result["views"][0]["name"]
        
        # Test basic call
        results.append(await test_tool(server, "get_cost_report_by_view", {
            "view_name": view_name
        }))
    
    return results

async def run_all_tests():
    """Run comprehensive test suite"""
    print("="*80)
    print("Cloudability MCP Server - Comprehensive Tool Tests")
    print("="*80)
    print(f"\nAPI Key: {'*' * 20}{Config.API_KEY[-4:] if Config.API_KEY else 'NOT SET'}")
    print(f"Base URL: {Config.BASE_URL}")
    print(f"Timestamp: {datetime.now().isoformat()}\n")
    
    server = CloudabilityMCPServer(api_key=Config.API_KEY)
    all_results = []
    
    # Test each tool category
    print("1. Testing Discovery Tools...")
    all_results.append(await test_list_views(server))
    all_results.append(await test_list_budgets(server))
    
    print("2. Testing Cost Reporting Tools...")
    all_results.extend(await test_get_amortized_costs(server))
    all_results.extend(await test_get_cost_report_by_view(server))
    
    # Test all tools with minimal params
    print("3. Testing All Tools with Minimal Parameters...")
    tools = server.get_tools()
    for tool in tools:
        tool_name = tool["name"]
        if tool_name not in ["list_views", "list_budgets"]:  # Already tested
            print(f"   Testing {tool_name}...")
            schema = tool.get("inputSchema", {})
            required = schema.get("required", [])
            
            # Build minimal params
            params = {}
            for req_param in required:
                params[req_param] = "test"  # Default test value
            
            result = await test_tool(server, tool_name, params)
            all_results.append(result)
    
    # Print summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    successful = [r for r in all_results if r.success]
    failed = [r for r in all_results if not r.success]
    
    print(f"\n✅ Successful: {len(successful)}")
    print(f"❌ Failed: {len(failed)}")
    
    if successful:
        print("\n✅ WORKING TOOLS:")
        for result in successful:
            print(f"  - {result.tool_name}")
            if result.params_used:
                print(f"    Params: {json.dumps(result.params_used, indent=4)}")
    
    if failed:
        print("\n❌ FAILED TOOLS:")
        for result in failed:
            print(f"  - {result.tool_name}")
            if result.error:
                error_msg = result.error[:100] if len(result.error) > 100 else result.error
                print(f"    Error: {error_msg}")
            if result.status_code:
                print(f"    Status: {result.status_code}")
    
    # Save results
    output_file = Path(__file__).parent / "test_results.json"
    with open(output_file, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "total_tests": len(all_results),
            "successful": len(successful),
            "failed": len(failed),
            "results": [r.to_dict() for r in all_results]
        }, f, indent=2, default=str)
    
    print(f"\n📄 Results saved to: {output_file}")
    print("="*80)
    
    return len(failed) == 0

if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)

