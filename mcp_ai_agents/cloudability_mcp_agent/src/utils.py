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
    Build filter string for API requests (comma-separated format)
    Supports multiple formats:
    - Equality: key==value
    - Contains/wildcard: key=@value (for wildcard matching)
    - IN operator: key[]==value1,value2
    - Comparison: key>value, key<value, etc.
    
    Args:
        filters: Dictionary of filter key-value pairs
                 Values starting with '*' are treated as wildcards (converted to @)
                 Values containing ',' are treated as IN lists
                 Values starting with '>', '<', '>=' or '<=' are comparison operators
        
    Returns:
        Comma-separated filter string
    """
    if not filters:
        return ""
    
    filter_parts = []
    for key, value in filters.items():
        if not key or not value:
            continue
            
        # Handle wildcard patterns (e.g., "ici*" -> "namespace=@ici")
        # The @ operator in Cloudability means "contains" or "starts with"
        if '*' in value:
            # Convert wildcard to contains operator (remove * and use @)
            clean_value = value.replace('*', '')
            filter_parts.append(f"{key}=@{clean_value}")
        elif value.startswith('*'):
            # Ends with pattern - API doesn't directly support, use contains
            clean_value = value.replace('*', '')
            filter_parts.append(f"{key}=@{clean_value}")
        # Handle IN operator (comma-separated values)
        elif ',' in value:
            filter_parts.append(f"{key}[]=={value}")
        # Handle comparison operators
        elif value.startswith(('>', '<', '>=', '<=')):
            filter_parts.append(f"{key}{value}")
        # Default: equality
        else:
            filter_parts.append(f"{key}=={value}")
    
    return ",".join(filter_parts)


def build_filter_list(filters: Dict[str, str]) -> List[str]:
    """
    Build filter list for API requests (repeated query parameters format)
    Cloudability API v3 expects multiple filters= parameters, not comma-separated.
    
    Based on IBM Cloudability API v3 documentation:
    https://www.ibm.com/docs/en/cloudability-commercial/cloudability-essentials/saas?topic=api-getting-started-cloudability-v3
    
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
        # The =@ operator in Cloudability means "contains" (per IBM API documentation)
        if '*' in value:
            # Convert wildcard to contains operator (remove * and use =@)
            clean_value = value.replace('*', '')
            filter_list.append(f"{key}=@{clean_value}")
        elif value.startswith('*'):
            # Ends with pattern - API doesn't directly support, use contains
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


def data_to_markdown_table(data: List[Dict], title: str = "Cost Report") -> str:
    """
    Convert data to Markdown table format
    
    Args:
        data: List of dictionaries to convert
        title: Optional title for the report
        
    Returns:
        Markdown formatted string with table
    """
    if not data:
        return f"# {title}\n\nNo data available.\n"
    
    try:
        # Get all unique keys from all records
        all_keys = set()
        for record in data:
            all_keys.update(record.keys())
        
        # Sort keys for consistent output (put common ones first)
        common_keys = ['date', 'namespace', 'cluster_name', 'account_id', 'product_id', 
                      'vendor', 'service', 'total_amortized_cost', 'cost', 'amount']
        ordered_keys = []
        for key in common_keys:
            if key in all_keys:
                ordered_keys.append(key)
        for key in sorted(all_keys - set(ordered_keys)):
            ordered_keys.append(key)
        
        # Build markdown table
        lines = [f"# {title}\n"]
        
        # Table header
        header = "| " + " | ".join(str(k).replace('_', ' ').title() for k in ordered_keys) + " |"
        separator = "| " + " | ".join(["---"] * len(ordered_keys)) + " |"
        lines.append(header)
        lines.append(separator)
        
        # Table rows
        for record in data:
            row = "| " + " | ".join(
                str(record.get(k, "")).replace("|", "\\|") for k in ordered_keys
            ) + " |"
            lines.append(row)
        
        # Add summary if cost data is present
        cost_keys = [k for k in ordered_keys if 'cost' in k.lower() or 'amount' in k.lower()]
        if cost_keys:
            total = sum(
                float(str(record.get(k, 0)).replace(',', '').replace('$', '')) 
                for record in data 
                for k in cost_keys 
                if str(record.get(k, 0)).replace(',', '').replace('$', '').replace('-', '').replace('.', '').isdigit()
            )
            if total > 0:
                lines.append(f"\n**Total Cost:** ${total:,.2f}")
        
        return "\n".join(lines) + "\n"
    except Exception as e:
        logger.error(f"Error converting data to Markdown: {e}")
        return f"# {title}\n\nError generating table: {str(e)}\n"


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

