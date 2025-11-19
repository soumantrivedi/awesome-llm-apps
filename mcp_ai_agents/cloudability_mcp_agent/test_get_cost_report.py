#!/usr/bin/env python3
"""
Test script to verify get_cost_report_with_filters works with the fixed code
"""

import os
import sys
import asyncio
import json
from dotenv import load_dotenv
from cloudability_mcp_server import CloudabilityMCPServer

# Load environment variables
load_dotenv()

async def test_get_cost_report():
    """Test getting cost report with filters"""
    # Get configuration
    api_key = os.getenv("CLOUDABILITY_API_KEY")
    base_url = os.getenv("CLOUDABILITY_BASE_URL", "https://api.cloudability.com/v3")
    
    if not api_key:
        print("❌ ERROR: CLOUDABILITY_API_KEY not found in environment")
        return
    
    try:
        # Initialize server
        server = CloudabilityMCPServer(api_key=api_key, base_url=base_url)
        
        view_name = "Product-12284-OFT - self-managed Kubernetes"
        print(f"Testing get_cost_report_with_filters for view: {view_name}")
        print("=" * 80)
        
        # Test with filters and date range (last 30 days)
        from datetime import datetime, timedelta
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        
        result = await server._get_cost_report_with_filters({
            "view_name": view_name,
            "start_date": start_date,
            "end_date": end_date
        })
        
        if result.get("success"):
            print("✓ Success!")
            print(f"View ID: {result.get('view_id')}")
            print(f"View Name: {result.get('view_name')}")
            data = result.get("data", {})
            print(f"\nData keys: {list(data.keys())}")
            if "result" in data:
                print(f"Number of records: {len(data.get('result', []))}")
                if data.get("result"):
                    print("\nFirst record sample:")
                    print(json.dumps(data["result"][0], indent=2)[:500])
        else:
            print(f"❌ Error: {result.get('error')}")
            if result.get('error_detail'):
                print(f"Error details: {json.dumps(result.get('error_detail'), indent=2)}")
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        # Try to get more error details
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_detail = e.response.json()
                print(f"Error details: {json.dumps(error_detail, indent=2)}")
            except:
                print(f"Error text: {e.response.text[:500]}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_get_cost_report())

