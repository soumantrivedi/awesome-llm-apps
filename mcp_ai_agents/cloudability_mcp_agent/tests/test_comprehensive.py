#!/usr/bin/env python3
"""
Comprehensive Test Suite with 30+ Parameter Combinations
Tests all tools with multiple parameter combinations and validates results
"""

import sys
import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path
from itertools import product
from typing import Dict, List, Any, Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.main import CloudabilityMCPServer
from src.config import Config

class ComprehensiveTestResult:
    """Comprehensive test result tracking"""
    def __init__(self):
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0
        self.errors_4xx = 0
        self.errors_5xx = 0
        self.working_combinations = []
        self.failing_combinations = []
        self.error_details = {}
    
    def add_result(self, tool_name: str, params: dict, success: bool, 
                   error: Optional[str] = None, status_code: Optional[int] = None):
        self.tests_run += 1
        result = {
            "tool": tool_name,
            "params": params,
            "success": success,
            "error": error,
            "status_code": status_code,
            "timestamp": datetime.now().isoformat()
        }
        
        if success:
            self.tests_passed += 1
            self.working_combinations.append(result)
        else:
            self.tests_failed += 1
            self.failing_combinations.append(result)
            
            if status_code:
                if 400 <= status_code < 500:
                    self.errors_4xx += 1
                elif 500 <= status_code < 600:
                    self.errors_5xx += 1
            
            if error:
                key = f"{tool_name}_{hash(str(params))}"
                self.error_details[key] = {
                    "tool": tool_name,
                    "params": params,
                    "error": error,
                    "status_code": status_code
                }
    
    def print_summary(self):
        print("\n" + "="*80)
        print("COMPREHENSIVE TEST SUMMARY")
        print("="*80)
        print(f"\nTotal Tests Run: {self.tests_run}")
        print(f"✅ Passed: {self.tests_passed}")
        print(f"❌ Failed: {self.tests_failed}")
        print(f"⚠️  4xx Errors: {self.errors_4xx}")
        print(f"⚠️  5xx Errors: {self.errors_5xx}")
        print(f"\nSuccess Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        if self.working_combinations:
            print(f"\n✅ WORKING COMBINATIONS ({len(self.working_combinations)}):")
            for result in self.working_combinations[:10]:  # Show first 10
                print(f"  - {result['tool']}")
                if result['params']:
                    print(f"    Params: {json.dumps(result['params'], indent=6)}")
            if len(self.working_combinations) > 10:
                print(f"  ... and {len(self.working_combinations) - 10} more")
        
        if self.errors_4xx > 0 or self.errors_5xx > 0:
            print(f"\n⚠️  ERRORS BY STATUS CODE:")
            print(f"  4xx (Client Errors): {self.errors_4xx}")
            print(f"  5xx (Server Errors): {self.errors_5xx}")
        
        print("="*80)
    
    def save_results(self, filename: str = "comprehensive_test_results.json"):
        output_file = Path(__file__).parent / filename
        with open(output_file, 'w') as f:
            json.dump({
                "summary": {
                    "total_tests": self.tests_run,
                    "passed": self.tests_passed,
                    "failed": self.tests_failed,
                    "errors_4xx": self.errors_4xx,
                    "errors_5xx": self.errors_5xx,
                    "success_rate": self.tests_passed/self.tests_run*100 if self.tests_run > 0 else 0
                },
                "working_combinations": self.working_combinations,
                "failing_combinations": self.failing_combinations,
                "error_details": self.error_details,
                "timestamp": datetime.now().isoformat()
            }, f, indent=2, default=str)
        return output_file

def validate_result(result: Dict) -> tuple[bool, Optional[str], Optional[int]]:
    """Validate API result and extract error information"""
    if not isinstance(result, dict):
        return False, "Result is not a dictionary", None
    
    success = result.get("success", False)
    if success:
        # Validate successful response structure
        if "data" in result or "views" in result or "budgets" in result:
            return True, None, None
        else:
            return False, "Success but no data in response", None
    
    # Extract error information
    error = result.get("error", "Unknown error")
    status_code = result.get("status_code")
    
    # Check for 4xx/5xx errors
    if status_code:
        if 400 <= status_code < 500:
            return False, f"4xx Client Error: {error}", status_code
        elif 500 <= status_code < 600:
            return False, f"5xx Server Error: {error}", status_code
    
    return False, error, status_code

async def test_tool_combinations(server: CloudabilityMCPServer, tool_name: str, 
                                  param_combinations: List[Dict], results: ComprehensiveTestResult):
    """Test a tool with multiple parameter combinations"""
    print(f"\n  Testing {tool_name} with {len(param_combinations)} combinations...")
    
    for i, params in enumerate(param_combinations, 1):
        try:
            response = await server.call_tool(tool_name, params)
            success, error, status_code = validate_result(response)
            results.add_result(tool_name, params, success, error, status_code)
            
            if i % 10 == 0:
                print(f"    Progress: {i}/{len(param_combinations)}")
        except Exception as e:
            results.add_result(tool_name, params, False, str(e), None)

def generate_date_combinations() -> List[Dict]:
    """Generate various date range combinations"""
    today = datetime.now()
    combinations = []
    
    # Last N days
    for days in [7, 14, 30, 60, 90]:
        end_date = today.strftime("%Y-%m-%d")
        start_date = (today - timedelta(days=days)).strftime("%Y-%m-%d")
        combinations.append({
            "start_date": start_date,
            "end_date": end_date
        })
    
    # Specific months
    for month_offset in range(-6, 1):  # Last 6 months to current
        month_date = today.replace(day=1) + timedelta(days=32*month_offset)
        start_date = month_date.replace(day=1).strftime("%Y-%m-%d")
        if month_offset == 0:
            end_date = today.strftime("%Y-%m-%d")
        else:
            next_month = month_date.replace(day=28) + timedelta(days=4)
            end_date = (next_month.replace(day=1) - timedelta(days=1)).strftime("%Y-%m-%d")
        combinations.append({
            "start_date": start_date,
            "end_date": end_date
        })
    
    return combinations

def generate_filter_combinations() -> List[Dict]:
    """Generate filter combinations"""
    filters = [
        {},
        {"product_id": "K8s"},
        {"vendor": "AWS"},
        {"vendor": "Azure"},
        {"vendor": "GCP"},
        {"product_id": "K8s", "vendor": "AWS"},
        {"service": "EC2"},
        {"service": "S3"},
    ]
    return [{"filters": f} for f in filters if f]

def generate_dimension_combinations() -> List[List[str]]:
    """Generate dimension combinations"""
    dimensions = [
        ["service"],
        ["vendor"],
        ["service", "vendor"],
        ["account_id"],
        ["region"],
        ["service", "account_id"],
        ["vendor", "service", "region"],
    ]
    return dimensions

def generate_export_format_combinations() -> List[str]:
    """Generate export format combinations"""
    return ["json", "csv"]

async def test_list_views_comprehensive(server: CloudabilityMCPServer, results: ComprehensiveTestResult):
    """Test list_views with multiple combinations"""
    combinations = [
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
    await test_tool_combinations(server, "list_views", combinations, results)

async def test_list_budgets_comprehensive(server: CloudabilityMCPServer, results: ComprehensiveTestResult):
    """Test list_budgets"""
    combinations = [{}]
    await test_tool_combinations(server, "list_budgets", combinations, results)

async def test_get_amortized_costs_comprehensive(server: CloudabilityMCPServer, results: ComprehensiveTestResult):
    """Test get_amortized_costs with 30+ combinations"""
    date_combos = generate_date_combinations()
    filter_combos = generate_filter_combinations()
    dimension_combos = generate_dimension_combinations()
    granularity_combos = ["daily", "monthly"]
    export_combos = generate_export_format_combinations()
    
    # Get a view for view-based tests
    views_result = await server.call_tool("list_views", {"limit": 5})
    view_names = []
    if views_result.get("success") and views_result.get("views"):
        view_names = [v["name"] for v in views_result["views"][:3]]
    
    combinations = []
    
    # Base combinations (date + dimensions)
    for date_combo, dim_combo in product(date_combos[:5], dimension_combos[:3]):
        combo = {**date_combo, "dimensions": dim_combo}
        combinations.append(combo)
    
    # Add filters
    for combo, filter_combo in product(combinations[:10], filter_combos[:3]):
        new_combo = {**combo, **filter_combo}
        combinations.append(new_combo)
    
    # Add granularity
    for combo in combinations[:10]:
        for granularity in granularity_combos:
            new_combo = {**combo, "granularity": granularity}
            combinations.append(new_combo)
    
    # Add export format
    for combo in combinations[:10]:
        for export_format in export_combos:
            new_combo = {**combo, "export_format": export_format}
            combinations.append(new_combo)
    
    # Add view restrictions (without filters to avoid conflicts)
    for date_combo, view_name in product(date_combos[:3], view_names[:2]):
        combo = {**date_combo, "view_name": view_name, "dimensions": ["service"]}
        combinations.append(combo)
    
    # Remove duplicates
    unique_combinations = []
    seen = set()
    for combo in combinations:
        key = json.dumps(combo, sort_keys=True)
        if key not in seen:
            seen.add(key)
            unique_combinations.append(combo)
    
    print(f"  Generated {len(unique_combinations)} unique combinations")
    await test_tool_combinations(server, "get_amortized_costs", unique_combinations[:30], results)

async def test_get_cost_report_by_view_comprehensive(server: CloudabilityMCPServer, results: ComprehensiveTestResult):
    """Test get_cost_report_by_view with multiple combinations"""
    views_result = await server.call_tool("list_views", {"limit": 5})
    if not views_result.get("success") or not views_result.get("views"):
        return
    
    view_names = [v["name"] for v in views_result["views"][:3]]
    date_combos = generate_date_combinations()[:5]
    export_combos = generate_export_format_combinations()
    
    combinations = []
    
    # Base: view only
    for view_name in view_names:
        combinations.append({"view_name": view_name})
    
    # View + limit
    for view_name in view_names:
        for limit in [10, 50, 100]:
            combinations.append({"view_name": view_name, "limit": limit})
    
    # View + dates
    for view_name, date_combo in product(view_names[:2], date_combos[:3]):
        combinations.append({**date_combo, "view_name": view_name})
    
    # View + export format
    for view_name, export_format in product(view_names[:2], export_combos):
        combinations.append({"view_name": view_name, "export_format": export_format})
    
    await test_tool_combinations(server, "get_cost_report_by_view", combinations, results)

async def test_export_cost_report_comprehensive(server: CloudabilityMCPServer, results: ComprehensiveTestResult):
    """Test export_cost_report with multiple combinations"""
    date_combos = generate_date_combinations()[:5]
    filter_combos = generate_filter_combinations()[:4]
    dimension_combos = generate_dimension_combinations()[:4]
    export_combos = generate_export_format_combinations()
    
    combinations = []
    
    # Base: dates required
    for date_combo in date_combos:
        combinations.append(date_combo)
    
    # Add filters
    for combo, filter_combo in product(combinations[:5], filter_combos):
        new_combo = {**combo, **filter_combo}
        combinations.append(new_combo)
    
    # Add dimensions
    for combo in combinations[:10]:
        for dim_combo in dimension_combos[:2]:
            new_combo = {**combo, "dimensions": dim_combo}
            combinations.append(new_combo)
    
    # Add export format
    for combo in combinations[:10]:
        for export_format in export_combos:
            new_combo = {**combo, "export_format": export_format}
            combinations.append(new_combo)
    
    await test_tool_combinations(server, "export_cost_report", combinations[:20], results)

async def test_all_tools_minimal(server: CloudabilityMCPServer, results: ComprehensiveTestResult):
    """Test all tools with minimal valid parameters"""
    tools = server.get_tools()
    
    for tool in tools:
        tool_name = tool["name"]
        schema = tool.get("inputSchema", {})
        required = schema.get("required", [])
        properties = schema.get("properties", {})
        
        # Build minimal valid params
        params = {}
        for req_param in required:
            prop_def = properties.get(req_param, {})
            param_type = prop_def.get("type")
            
            if param_type == "string":
                if "date" in req_param.lower():
                    params[req_param] = datetime.now().strftime("%Y-%m-%d")
                elif "view" in req_param.lower() or "name" in req_param.lower():
                    # Try to get a real value
                    if "view" in req_param.lower():
                        views_result = await server.call_tool("list_views", {"limit": 1})
                        if views_result.get("success") and views_result.get("views"):
                            params[req_param] = views_result["views"][0]["name"]
                        else:
                            params[req_param] = "test_view"
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
        
        await test_tool_combinations(server, tool_name, [params], results)

async def run_comprehensive_tests():
    """Run comprehensive test suite"""
    print("="*80)
    print("Cloudability MCP Server - Comprehensive Test Suite")
    print("="*80)
    print(f"\nAPI Key: {'*' * 20}{Config.API_KEY[-4:] if Config.API_KEY else 'NOT SET'}")
    print(f"Base URL: {Config.BASE_URL}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"\nTesting 30+ parameter combinations per tool...")
    
    server = CloudabilityMCPServer(api_key=Config.API_KEY)
    results = ComprehensiveTestResult()
    
    # Test each tool category comprehensively
    print("\n1. Testing Discovery Tools...")
    await test_list_views_comprehensive(server, results)
    await test_list_budgets_comprehensive(server, results)
    
    print("\n2. Testing Cost Reporting Tools...")
    await test_get_amortized_costs_comprehensive(server, results)
    await test_get_cost_report_by_view_comprehensive(server, results)
    await test_export_cost_report_comprehensive(server, results)
    
    print("\n3. Testing All Tools with Minimal Parameters...")
    await test_all_tools_minimal(server, results)
    
    # Print summary
    results.print_summary()
    
    # Save results
    output_file = results.save_results()
    print(f"\n📄 Detailed results saved to: {output_file}")
    
    # Check for 4xx/5xx errors
    if results.errors_4xx > 0 or results.errors_5xx > 0:
        print(f"\n⚠️  WARNING: Found {results.errors_4xx} 4xx errors and {results.errors_5xx} 5xx errors")
        print("   Review error_details in results file for more information")
        return False
    
    print("\n✅ No 4xx or 5xx errors found!")
    return True

if __name__ == "__main__":
    success = asyncio.run(run_comprehensive_tests())
    sys.exit(0 if success else 1)

