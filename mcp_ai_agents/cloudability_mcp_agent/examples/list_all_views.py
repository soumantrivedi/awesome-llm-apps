#!/usr/bin/env python3
"""
Script to list all Cloudability views in a readable format
"""

import os
import sys
import asyncio
import json
from dotenv import load_dotenv
from cloudability_mcp_server import CloudabilityMCPServer

# Load environment variables
load_dotenv()

async def list_all_views():
    """List all available Cloudability views"""
    # Get configuration
    api_key = os.getenv("CLOUDABILITY_API_KEY")
    base_url = os.getenv("CLOUDABILITY_BASE_URL", "https://api.cloudability.com/v3")
    
    if not api_key:
        print("❌ ERROR: CLOUDABILITY_API_KEY not found in environment")
        print("   Please set it in your .env file or environment variables")
        return
    
    try:
        # Initialize server
        server = CloudabilityMCPServer(api_key=api_key, base_url=base_url)
        
        # Get all views (with max limit)
        print("Fetching all available views from Cloudability...")
        print("=" * 80)
        
        all_views = []
        offset = 0
        limit = 250  # Max limit per request
        
        while True:
            views_result = await server._list_views({"limit": limit, "offset": offset})
            
            if not views_result.get("success"):
                print(f"❌ Error: {views_result.get('error', 'Unknown error')}")
                break
            
            views = views_result.get("views", [])
            if not views:
                break
            
            all_views.extend(views)
            print(f"Fetched {len(views)} views (total so far: {len(all_views)})...")
            
            # If we got fewer than the limit, we've reached the end
            if len(views) < limit:
                break
            
            offset += limit
        
        print("=" * 80)
        print(f"\nTotal views found: {len(all_views)}\n")
        
        # Check raw data structure for first view to understand available fields
        if all_views:
            print("\nSample raw API response structure:")
            views_result = await server._list_views({"limit": 1, "offset": 0})
            if views_result.get("success") and views_result.get("raw_data"):
                raw_data = views_result.get("raw_data")
                print(json.dumps(raw_data, indent=2)[:1000])  # First 1000 chars
            print()
        
        # Display all views
        print("All Available Views:")
        print("=" * 80)
        for i, view in enumerate(all_views, 1):
            view_id = view.get('id', 'N/A')
            view_name = view.get('name', 'Unknown')
            description = view.get('description', '')
            
            print(f"\n{i}. {view_name}")
            print(f"   ID: {view_id}")
            if description:
                print(f"   Description: {description}")
        
        print("\n" + "=" * 80)
        print(f"\nTotal: {len(all_views)} views")
        
        # Also save to a JSON file for reference
        output_file = "cloudability_views.json"
        with open(output_file, 'w') as f:
            json.dump({
                "total_views": len(all_views),
                "views": all_views
            }, f, indent=2)
        print(f"\n✓ Views saved to: {output_file}")
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(list_all_views())

