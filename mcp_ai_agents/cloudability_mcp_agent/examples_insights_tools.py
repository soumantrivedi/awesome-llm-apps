#!/usr/bin/env python3
"""
Example scripts demonstrating how to use the new TrueCost Explorer Insights MCP tools.
These examples show how to call each tool with various filters and export options.
"""

import os
import sys
import asyncio
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
from cloudability_mcp_server import CloudabilityMCPServer

# Load environment variables
load_dotenv()

async def example_amortized_costs():
    """Example: Get amortized costs for AWS EC2 services"""
    print("=" * 80)
    print("Example 1: Get Amortized Costs")
    print("=" * 80)
    
    api_key = os.getenv("CLOUDABILITY_API_KEY")
    base_url = os.getenv("CLOUDABILITY_BASE_URL", "https://api.cloudability.com/v3")
    
    server = CloudabilityMCPServer(api_key=api_key, base_url=base_url)
    
    result = await server._get_amortized_costs({
        "start_date": "2024-01-01",
        "end_date": "2024-01-31",
        "filters": {
            "vendor": "AWS",
            "service": "EC2"
        },
        "dimensions": ["vendor", "service", "account_id"],
        "export_format": "json"
    })
    
    print(f"Success: {result.get('success')}")
    if result.get("success"):
        print(f"Total records: {result.get('total_records')}")
        print(f"Export format: {result.get('export_format')}")
        if result.get("data"):
            print(f"\nSample data (first record):")
            print(json.dumps(result["data"][0], indent=2)[:500])
    else:
        print(f"Error: {result.get('error')}")
    print()


async def example_container_costs():
    """Example: Get container costs grouped by cluster and namespace"""
    print("=" * 80)
    print("Example 2: Get Container Costs")
    print("=" * 80)
    
    api_key = os.getenv("CLOUDABILITY_API_KEY")
    base_url = os.getenv("CLOUDABILITY_BASE_URL", "https://api.cloudability.com/v3")
    
    server = CloudabilityMCPServer(api_key=api_key, base_url=base_url)
    
    result = await server._get_container_costs({
        "start_date": "2024-01-01",
        "end_date": "2024-01-31",
        "filters": {
            "cluster_name": "prod-cluster",
            "namespace": "default"
        },
        "group_by": ["cluster", "namespace", "pod"],
        "export_format": "csv"
    })
    
    print(f"Success: {result.get('success')}")
    if result.get("success"):
        print(f"Total records: {result.get('total_records')}")
        print(f"Export path: {result.get('export_path')}")
        print(f"Grouped by: {result.get('group_by')}")
    else:
        print(f"Error: {result.get('error')}")
    print()


async def example_tag_explorer():
    """Example: Explore costs by Environment tag"""
    print("=" * 80)
    print("Example 3: Explore Costs by Tags")
    print("=" * 80)
    
    api_key = os.getenv("CLOUDABILITY_API_KEY")
    base_url = os.getenv("CLOUDABILITY_BASE_URL", "https://api.cloudability.com/v3")
    
    server = CloudabilityMCPServer(api_key=api_key, base_url=base_url)
    
    # First, list available tags
    print("Step 1: Listing available tags...")
    tags_result = await server._list_available_tags({})
    if tags_result.get("success"):
        print(f"Available tag keys: {tags_result.get('tag_keys', [])[:5]}")
    print()
    
    # Then explore a specific tag
    print("Step 2: Exploring costs by 'Environment' tag...")
    result = await server._explore_tags({
        "tag_key": "Environment",
        "tag_value": "Production",  # Optional: leave empty to see all values
        "start_date": "2024-01-01",
        "end_date": "2024-01-31",
        "additional_filters": {
            "vendor": "AWS"
        },
        "export_format": "csv"
    })
    
    print(f"Success: {result.get('success')}")
    if result.get("success"):
        print(f"Tag key: {result.get('tag_key')}")
        print(f"Tag value: {result.get('tag_value')}")
        print(f"Total records: {result.get('total_records')}")
        print(f"Export path: {result.get('export_path')}")
    else:
        print(f"Error: {result.get('error')}")
    print()


async def example_anomaly_detection():
    """Example: Detect cost anomalies"""
    print("=" * 80)
    print("Example 4: Anomaly Detection")
    print("=" * 80)
    
    api_key = os.getenv("CLOUDABILITY_API_KEY")
    base_url = os.getenv("CLOUDABILITY_BASE_URL", "https://api.cloudability.com/v3")
    
    server = CloudabilityMCPServer(api_key=api_key, base_url=base_url)
    
    result = await server._get_anomaly_detection({
        "start_date": "2024-01-01",
        "end_date": "2024-01-31",
        "severity": "high",  # Options: low, medium, high, all
        "filters": {
            "vendor": "AWS"
        },
        "min_cost_change_percent": 20.0,  # Minimum 20% change to be considered anomaly
        "export_format": "json"
    })
    
    print(f"Success: {result.get('success')}")
    if result.get("success"):
        print(f"Total anomalies found: {result.get('total_anomalies')}")
        print(f"Severity filter: {result.get('severity')}")
        print(f"Min cost change: {result.get('min_cost_change_percent')}%")
        if result.get("data"):
            print(f"\nSample anomaly (first record):")
            print(json.dumps(result["data"][0], indent=2)[:500])
    else:
        print(f"Error: {result.get('error')}")
    print()


async def example_export_cost_report():
    """Example: Export custom cost report with filters"""
    print("=" * 80)
    print("Example 5: Export Custom Cost Report")
    print("=" * 80)
    
    api_key = os.getenv("CLOUDABILITY_API_KEY")
    base_url = os.getenv("CLOUDABILITY_BASE_URL", "https://api.cloudability.com/v3")
    
    server = CloudabilityMCPServer(api_key=api_key, base_url=base_url)
    
    result = await server._export_cost_report({
        "start_date": "2024-01-01",
        "end_date": "2024-01-31",
        "filters": {
            "vendor": "AWS",
            "service": "EC2",
            "region": "us-east-1",
            "instance_type": "t3.medium"
        },
        "dimensions": ["vendor", "service", "account_id", "region", "instance_type"],
        "metrics": ["cost", "usage"],
        "export_format": "csv",
        "file_name": "aws_ec2_t3_medium_costs"
    })
    
    print(f"Success: {result.get('success')}")
    if result.get("success"):
        print(f"Export path: {result.get('export_path')}")
        print(f"Total records: {result.get('total_records')}")
        print(f"Filters applied: {result.get('filters')}")
        print(f"Dimensions: {result.get('dimensions')}")
        print(f"Metrics: {result.get('metrics')}")
    else:
        print(f"Error: {result.get('error')}")
    print()


async def run_all_examples():
    """Run all examples"""
    print("\n" + "=" * 80)
    print("Cloudability TrueCost Explorer Insights - Example Scripts")
    print("=" * 80)
    print()
    
    if not os.getenv("CLOUDABILITY_API_KEY"):
        print("❌ ERROR: CLOUDABILITY_API_KEY not found in environment")
        print("   Please set it in your .env file")
        return
    
    try:
        await example_amortized_costs()
        await example_container_costs()
        await example_tag_explorer()
        await example_anomaly_detection()
        await example_export_cost_report()
        
        print("=" * 80)
        print("✓ All examples completed!")
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(run_all_examples())

