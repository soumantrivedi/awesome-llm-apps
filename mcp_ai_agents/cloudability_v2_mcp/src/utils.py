"""
Utility functions for Cloudability V2 MCP Server
"""

import csv
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


def build_filter_list(filters: Dict[str, str]) -> List[str]:
    """
    Build filter list for API requests (repeated query parameters format)
    Cloudability API v3 expects multiple filters= parameters, not comma-separated.
    
    Filter operators supported:
    - == (equals)
    - != (does not equal)
    - > (greater than)
    - < (less than)
    - >= (greater than or equal to)
    - <= (less than or equal to)
    - =@ (contains/wildcard matching)
    - !=@ (does not contain)
    
    Example: filters=namespace=@ici&filters=product_id==K8s
    
    Args:
        filters: Dictionary of filter key-value pairs
                 Values starting with '*' are treated as wildcards (converted to =@)
                 Values containing ',' are treated as IN lists
                 Values starting with '>', '<', '>=' or '<=' are comparison operators
        
    Returns:
        List of filter strings, one per filter condition
    """
    if not filters:
        return []
    
    filter_list = []
    for key, value in filters.items():
        if not key or not value:
            continue
            
        # Handle wildcard patterns (e.g., "ici*" -> "namespace=@ici")
        if '*' in value:
            clean_value = value.replace('*', '')
            filter_list.append(f"{key}=@{clean_value}")
        elif value.startswith('*'):
            clean_value = value.replace('*', '')
            filter_list.append(f"{key}=@{clean_value}")
        # Handle IN operator (comma-separated values)
        elif ',' in value:
            filter_list.append(f"{key}[]=={value}")
        # Handle comparison operators
        elif value.startswith(('>', '<', '>=', '<=')):
            filter_list.append(f"{key}{value}")
        # Default: equality
        else:
            filter_list.append(f"{key}=={value}")
    
    return filter_list


def get_default_date_range(days: int = 30) -> tuple:
    """
    Get default date range (last N days)
    
    Args:
        days: Number of days to go back
        
    Returns:
        Tuple of (start_date, end_date) in YYYY-MM-DD format
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")


def format_error_response(error: Exception, status_code: Optional[int] = None) -> Dict:
    """
    Format error response in standard format
    
    Args:
        error: Exception that occurred
        status_code: HTTP status code if available
        
    Returns:
        Standardized error response dictionary
    """
    error_msg = str(error)
    
    # Try to extract more details from requests exceptions
    if hasattr(error, 'response') and error.response is not None:
        try:
            error_detail = error.response.json()
            if isinstance(error_detail, dict) and 'error' in error_detail:
                error_msg = error_detail['error'].get('messages', [error_msg])[0]
        except (ValueError, KeyError):
            pass
        
        if status_code is None:
            status_code = error.response.status_code
    
    return {
        "success": False,
        "error": error_msg,
        "status_code": status_code
    }


def data_to_csv_string(data: List[Dict]) -> str:
    """
    Convert list of dictionaries to CSV string
    
    Args:
        data: List of dictionaries
        
    Returns:
        CSV string
    """
    if not data:
        return ""
    
    # Get all unique keys from all dictionaries
    fieldnames = set()
    for item in data:
        fieldnames.update(item.keys())
    fieldnames = sorted(list(fieldnames))
    
    # Write to string
    output = []
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(data)
    
    return "\n".join(output)


def export_to_csv(data: List[Dict], file_path: str) -> str:
    """
    Export data to CSV file
    
    Args:
        data: List of dictionaries
        file_path: Output file path
        
    Returns:
        File path where data was written
    """
    if not data:
        return file_path
    
    # Get all unique keys from all dictionaries
    fieldnames = set()
    for item in data:
        fieldnames.update(item.keys())
    fieldnames = sorted(list(fieldnames))
    
    with open(file_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    
    return file_path


def export_to_json(data: Any, file_path: str) -> str:
    """
    Export data to JSON file
    
    Args:
        data: Data to export
        file_path: Output file path
        
    Returns:
        File path where data was written
    """
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, default=str)
    
    return file_path

