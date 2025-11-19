"""
Utility functions for Cloudability MCP Server
"""

import csv
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


def build_filter_string(filters: Dict[str, str]) -> str:
    """
    Build filter string for API requests
    Format: key1==value1,key2==value2
    
    Args:
        filters: Dictionary of filter key-value pairs
        
    Returns:
        Comma-separated filter string
    """
    if not filters:
        return ""
    filter_parts = [f"{key}=={value}" for key, value in filters.items()]
    return ",".join(filter_parts)


def data_to_csv_string(data: List[Dict]) -> str:
    """
    Convert data to CSV string (for returning in API responses)
    
    Args:
        data: List of dictionaries to convert
        
    Returns:
        CSV string
    """
    if not data:
        return ""
    
    try:
        import io
        output = io.StringIO()
        
        if isinstance(data[0], dict):
            writer = csv.DictWriter(output, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        else:
            writer = csv.writer(output)
            writer.writerows(data)
        
        return output.getvalue()
    except Exception as e:
        logger.error(f"Error converting data to CSV string: {e}")
        raise


def export_to_csv(data: List[Dict], file_path: str) -> str:
    """
    Export data to CSV file
    
    Args:
        data: List of dictionaries to export
        file_path: Output file path
        
    Returns:
        Path to exported file
    """
    if not data:
        logger.warning(f"No data to export to {file_path}")
        return file_path
    
    try:
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            if isinstance(data[0], dict):
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
            else:
                writer = csv.writer(f)
                writer.writerows(data)
        logger.info(f"Exported {len(data)} records to {file_path}")
        return file_path
    except Exception as e:
        logger.error(f"Error exporting to CSV: {e}")
        raise


def export_to_json(data: Any, file_path: str) -> str:
    """
    Export data to JSON file
    
    Args:
        data: Data to export
        file_path: Output file path
        
    Returns:
        Path to exported file
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
        logger.info(f"Exported data to {file_path}")
        return file_path
    except Exception as e:
        logger.error(f"Error exporting to JSON: {e}")
        raise


def get_default_date_range(days: int = 30) -> tuple[str, str]:
    """
    Get default date range (last N days)
    
    Args:
        days: Number of days to look back
        
    Returns:
        Tuple of (start_date, end_date) in YYYY-MM-DD format
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")


def format_error_response(
    error: Exception,
    status_code: Optional[int] = None,
    additional_info: Optional[Dict] = None
) -> Dict:
    """
    Format error response in consistent format
    
    Args:
        error: Exception that occurred
        status_code: HTTP status code if available
        additional_info: Additional error information
        
    Returns:
        Formatted error dictionary
    """
    response = {
        "success": False,
        "error": str(error),
    }
    
    if status_code:
        response["status_code"] = status_code
    
    if additional_info:
        response.update(additional_info)
    
    return response


def find_view_by_name(
    views: List[Dict],
    view_name: str
) -> Optional[Dict]:
    """
    Find view by name (checks multiple name fields)
    
    Args:
        views: List of view dictionaries
        view_name: Name to search for
        
    Returns:
        View dictionary if found, None otherwise
    """
    for view in views:
        # Check multiple possible name fields
        if (view.get("title") == view_name or
            view.get("name") == view_name or
            view.get("displayName") == view_name):
            return view
    return None


def get_view_id(view: Dict) -> Optional[str]:
    """
    Extract view ID from view dictionary
    
    Args:
        view: View dictionary
        
    Returns:
        View ID if found
    """
    return view.get("id") or view.get("viewId")

