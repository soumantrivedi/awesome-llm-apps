"""
Base Tool Implementation
Provides base class for Cloudability-specific tools
"""

from typing import Dict, Optional, Any
from ..framework.tool_base import BaseTool


class CloudabilityTool(BaseTool):
    """
    Base class for Cloudability MCP tools
    Provides common functionality and API client access
    """
    
    def __init__(self, api_client=None):
        """Initialize Cloudability tool"""
        super().__init__(api_client)
    
    def require_api_client(self):
        """Ensure API client is available"""
        if self.api_client is None:
            raise ValueError("API client is required but not set")
        return self.api_client
    
    def validate_date_range(self, start_date: Optional[str], end_date: Optional[str]) -> tuple:
        """
        Validate and set default date range
        
        Args:
            start_date: Start date (optional)
            end_date: End date (optional)
            
        Returns:
            Tuple of (start_date, end_date)
        """
        from datetime import datetime
        from ..utils import get_default_date_range
        
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
        if not start_date:
            start_date, _ = get_default_date_range(30)
        
        return start_date, end_date
    
    def build_success_response(
        self,
        data: Any,
        report_type: str,
        **kwargs
    ) -> Dict:
        """
        Build standardized success response
        
        Args:
            data: Response data
            report_type: Type of report
            **kwargs: Additional response fields
            
        Returns:
            Standardized response dictionary
        """
        response = {
            "success": True,
            "report_type": report_type,
            **kwargs
        }
        
        if isinstance(data, list):
            response["total_records"] = len(data)
            response["data"] = data
        elif isinstance(data, dict):
            response.update(data)
        else:
            response["data"] = data
        
        return response
    
    def build_error_response(
        self,
        error: Exception,
        status_code: Optional[int] = None
    ) -> Dict:
        """
        Build standardized error response
        
        Args:
            error: Exception that occurred
            status_code: HTTP status code if available
            
        Returns:
            Standardized error response
        """
        from ..utils import format_error_response
        return format_error_response(error, status_code=status_code)

