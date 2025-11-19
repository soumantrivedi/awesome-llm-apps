"""
Tool Status Management
Tracks which tools are verified working vs experimental
"""

from typing import Dict, List
from enum import Enum

class ToolStatus(Enum):
    """Tool status enumeration"""
    WORKING = "working"  # Verified to work
    EXPERIMENTAL = "experimental"  # May work, needs testing
    NOT_AVAILABLE = "not_available"  # API endpoint doesn't exist

# Tool status registry
TOOL_STATUS: Dict[str, ToolStatus] = {
    # Verified working tools
    "list_views": ToolStatus.WORKING,
    "list_budgets": ToolStatus.WORKING,
    
    # Experimental tools - endpoints exist but require correct parameter formats
    # These tools will attempt API calls and provide detailed error messages
    # Status will be updated to WORKING once valid parameters are discovered
    "get_amortized_costs": ToolStatus.EXPERIMENTAL,  # /reporting/cost/run - needs valid dimensions/metrics
    "get_cost_report_by_view": ToolStatus.EXPERIMENTAL,  # /views/{id}/data - may need different parameters
    "get_cost_report_with_filters": ToolStatus.EXPERIMENTAL,  # Uses /views/{id}/data
    "export_cost_report": ToolStatus.EXPERIMENTAL,  # Uses /reporting/cost/run
    "get_container_costs": ToolStatus.EXPERIMENTAL,  # Uses /reporting/cost/run
    "get_container_resource_usage": ToolStatus.EXPERIMENTAL,  # Uses /reporting/cost/run
    "analyze_container_cost_allocation": ToolStatus.EXPERIMENTAL,  # Uses /reporting/cost/run
    "explore_tags": ToolStatus.EXPERIMENTAL,  # Uses /reporting/cost/run
    "get_anomaly_detection": ToolStatus.EXPERIMENTAL,  # Uses /reporting/cost/run
    
    # Experimental tools - endpoints may exist with different paths or parameters
    "get_budget": ToolStatus.EXPERIMENTAL,  # /budgets/{id} - may need different ID format
    "create_budget": ToolStatus.EXPERIMENTAL,  # /budgets POST - may need different payload format
    "update_budget": ToolStatus.EXPERIMENTAL,  # /budgets/{id} PUT - may need different payload format
    "get_spending_estimate": ToolStatus.EXPERIMENTAL,  # /forecast/estimate - may need different path
    "get_spending_forecast": ToolStatus.EXPERIMENTAL,  # /forecast/forecast - may need different path
    "list_available_tags": ToolStatus.EXPERIMENTAL,  # /reporting/dimensions - may need different parameters
    "get_available_measures": ToolStatus.EXPERIMENTAL,  # /reporting/measures - may need different path
    "get_filter_operators": ToolStatus.EXPERIMENTAL,  # /reporting/operators - may need different path
}

def get_tool_status(tool_name: str) -> ToolStatus:
    """Get status for a tool"""
    return TOOL_STATUS.get(tool_name, ToolStatus.EXPERIMENTAL)

def is_tool_working(tool_name: str) -> bool:
    """Check if tool is verified working"""
    return get_tool_status(tool_name) == ToolStatus.WORKING

def get_working_tools() -> List[str]:
    """Get list of verified working tools"""
    return [name for name, status in TOOL_STATUS.items() if status == ToolStatus.WORKING]

def get_experimental_tools() -> List[str]:
    """Get list of experimental tools"""
    return [name for name, status in TOOL_STATUS.items() if status == ToolStatus.EXPERIMENTAL]

def get_unavailable_tools() -> List[str]:
    """Get list of unavailable tools"""
    return [name for name, status in TOOL_STATUS.items() if status == ToolStatus.NOT_AVAILABLE]

