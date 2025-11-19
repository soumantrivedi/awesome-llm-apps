"""
Cloudability API Client
Core business logic for interacting with Cloudability API
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import requests

from .config import Config
from .auth import CloudabilityAuth
from .utils import (
    build_filter_string,
    find_view_by_name,
    get_view_id,
    get_default_date_range,
    format_error_response,
)

logger = logging.getLogger(__name__)


class CloudabilityAPIClient:
    """Client for interacting with Cloudability API"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        auth_type: Optional[str] = None
    ):
        """
        Initialize API client
        
        Args:
            api_key: API key or token
            base_url: Base URL for API
            auth_type: 'basic' or 'bearer'
        """
        self.config = Config
        self.config.validate()
        
        self.api_key = api_key or self.config.API_KEY
        self.base_url = (base_url or self.config.BASE_URL).rstrip('/')
        self.auth_manager = CloudabilityAuth(
            api_key=self.api_key,
            auth_type=auth_type or self.config.AUTH_TYPE
        )
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        **kwargs
    ) -> requests.Response:
        """
        Make HTTP request to API
        
        Args:
            method: HTTP method
            endpoint: API endpoint (relative to base_url)
            params: Query parameters
            headers: Additional headers
            **kwargs: Additional request arguments
            
        Returns:
            Response object
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        request_headers = self.auth_manager.get_headers()
        if headers:
            request_headers.update(headers)
        
        response = requests.request(
            method=method,
            url=url,
            auth=self.auth_manager.auth,
            headers=request_headers,
            params=params,
            timeout=self.config.DEFAULT_TIMEOUT,
            **kwargs
        )
        response.raise_for_status()
        return response
    
    # ========== View Operations ==========
    
    def list_views(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> Dict:
        """
        List all available views
        
        Args:
            limit: Maximum views to return
            offset: Pagination offset
            
        Returns:
            Dictionary with views list
        """
        try:
            params = {}
            if limit:
                params["limit"] = min(limit, self.config.MAX_LIMIT)
            if offset:
                params["offset"] = offset
            
            response = self._make_request("GET", "/views", params=params)
            data = response.json()
            
            views = data.get("result", [])
            view_list = []
            for view in views:
                view_list.append({
                    "id": get_view_id(view),
                    "name": view.get("title") or view.get("name") or view.get("displayName", "Unknown"),
                    "description": view.get("description", ""),
                    "ownerEmail": view.get("ownerEmail", ""),
                    "viewSource": view.get("viewSource", "")
                })
            
            return {
                "success": True,
                "total_views": len(views),
                "views": view_list,
                "raw_data": data
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to list views: {e}")
            return format_error_response(
                e,
                status_code=getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None
            )
    
    def get_view_by_name(self, view_name: str) -> Optional[Dict]:
        """
        Get view by name
        
        Args:
            view_name: Name of the view
            
        Returns:
            View dictionary if found, None otherwise
        """
        result = self.list_views(limit=self.config.MAX_LIMIT)
        if not result.get("success"):
            return None
        
        views = result.get("raw_data", {}).get("result", [])
        return find_view_by_name(views, view_name)
    
    # ========== Cost Report Operations ==========
    
    def get_cost_report_by_view(
        self,
        view_name: str,
        product_id: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> Dict:
        """
        Get cost report by view name
        
        Args:
            view_name: Name of the view
            product_id: Optional product ID filter
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            limit: Maximum records
            offset: Pagination offset
            
        Returns:
            Cost report data
        """
        try:
            # Find view
            view = self.get_view_by_name(view_name)
            if not view:
                return {
                    "success": False,
                    "error": f"View '{view_name}' not found"
                }
            
            view_id = get_view_id(view)
            
            # Build parameters
            params = {}
            if product_id:
                params["filter"] = f"product_id=={product_id}"
            if start_date:
                params["start_date"] = start_date
            if end_date:
                params["end_date"] = end_date
            if limit:
                params["limit"] = limit
            if offset:
                params["offset"] = offset
            
            # Get cost data
            response = self._make_request(
                "GET",
                f"/views/{view_id}/data",
                params=params
            )
            data = response.json()
            
            return {
                "success": True,
                "view_name": view_name,
                "view_id": view_id,
                "filters": {
                    "product_id": product_id,
                    "start_date": start_date,
                    "end_date": end_date
                },
                "data": data
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get cost report: {e}")
            return format_error_response(
                e,
                status_code=getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None
            )
    
    def get_cost_report_with_filters(
        self,
        view_name: str,
        filters: Optional[Dict[str, str]] = None,
        dimensions: Optional[List[str]] = None,
        metrics: Optional[List[str]] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict:
        """
        Get cost report with advanced filtering
        
        Args:
            view_name: Name of the view
            filters: Filter conditions
            dimensions: Dimensions to group by
            metrics: Metrics to retrieve
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            Filtered cost report data
        """
        try:
            # Find view
            view = self.get_view_by_name(view_name)
            if not view:
                return {
                    "success": False,
                    "error": f"View '{view_name}' not found"
                }
            
            view_id = get_view_id(view)
            
            # Build parameters
            params = {}
            if filters:
                params["filter"] = build_filter_string(filters)
            if dimensions:
                params["dimensions"] = ",".join(dimensions)
            if metrics:
                params["metrics"] = ",".join(metrics)
            if start_date:
                params["start_date"] = start_date
            if end_date:
                params["end_date"] = end_date
            
            # Get cost data
            response = self._make_request(
                "GET",
                f"/views/{view_id}/data",
                params=params
            )
            data = response.json()
            
            return {
                "success": True,
                "view_name": view_name,
                "view_id": view_id,
                "filters_applied": filters,
                "dimensions": dimensions,
                "metrics": metrics,
                "data": data
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get cost report with filters: {e}")
            error_detail = None
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                except:
                    error_detail = e.response.text[:500] if hasattr(e.response, 'text') else None
            return format_error_response(
                e,
                status_code=getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None,
                additional_info={"error_detail": error_detail}
            )
    
    # ========== Amortized Costs ==========
    
    def get_amortized_costs(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        filters: Optional[Dict[str, str]] = None,
        dimensions: Optional[List[str]] = None,
        view_name: Optional[str] = None,
        granularity: str = "monthly",
        export_format: str = "json"
    ) -> Dict:
        """
        Get amortized cost data from TrueCost Explorer
        
        Args:
            start_date: Start date (YYYY-MM-DD), defaults to 30 days ago
            end_date: End date (YYYY-MM-DD), defaults to today
            filters: Filter conditions (namespace, product_id, etc.)
            dimensions: Dimensions to group by (default: ['service'])
            view_name: Optional view name to restrict data
            granularity: 'daily' or 'monthly' (default: 'monthly')
            export_format: 'json' or 'csv'
            
        Returns:
            Amortized cost data
        """
        try:
            # Set default dates
            if not end_date:
                end_date = datetime.now().strftime("%Y-%m-%d")
            if not start_date:
                start_date, _ = get_default_date_range(30)
            
            # Build parameters
            params = {
                "start": start_date,
                "end": end_date,
                "dimensions": ",".join(dimensions) if dimensions else "service",
                "metrics": "total_amortized_cost"
            }
            
            # Add granularity
            if granularity == "monthly":
                params["granularity"] = "monthly"
            
            # Add filters
            if filters:
                params["filter"] = build_filter_string(filters)
            
            # Add view restriction
            if view_name:
                view = self.get_view_by_name(view_name)
                if not view:
                    return {
                        "success": False,
                        "error": f"View '{view_name}' not found"
                    }
                params["view"] = get_view_id(view)
            
            # Set headers for export format
            headers = {}
            if export_format == "csv":
                headers["Accept"] = "text/csv"
            
            # Make request
            response = self._make_request(
                "GET",
                "/reporting/cost/run",
                params=params,
                headers=headers
            )
            
            # Handle CSV response
            if export_format == "csv":
                result_data = response.text
                return {
                    "success": True,
                    "report_type": "amortized_costs",
                    "start_date": start_date,
                    "end_date": end_date,
                    "filters": filters,
                    "dimensions": dimensions,
                    "view_name": view_name,
                    "granularity": granularity,
                    "csv_data": result_data,
                    "export_format": export_format
                }
            else:
                # Handle JSON response
                data = response.json()
                result_data = data.get("result", [])
                
                return {
                    "success": True,
                    "report_type": "amortized_costs",
                    "start_date": start_date,
                    "end_date": end_date,
                    "filters": filters,
                    "dimensions": dimensions,
                    "view_name": view_name,
                    "granularity": granularity,
                    "total_records": len(result_data),
                    "data": result_data,
                    "export_format": export_format
                }
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get amortized costs: {e}")
            error_detail = None
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                except:
                    error_detail = e.response.text[:500] if hasattr(e.response, 'text') else None
            return format_error_response(
                e,
                status_code=getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None,
                additional_info={"error_detail": error_detail}
            )
    
    # ========== Export Operations ==========
    
    def export_cost_report(
        self,
        start_date: str,
        end_date: str,
        filters: Optional[Dict[str, str]] = None,
        dimensions: Optional[List[str]] = None,
        metrics: Optional[List[str]] = None,
        export_format: str = "json",
        file_name: Optional[str] = None
    ) -> Dict:
        """
        Export cost report with custom filters
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            filters: Filter conditions
            dimensions: Dimensions to group by
            metrics: Metrics to include
            export_format: 'json' or 'csv'
            file_name: Custom file name (without extension)
            
        Returns:
            Export result with file path
        """
        try:
            # Build parameters
            params = {
                "start": start_date,
                "end": end_date,
                "dimensions": ",".join(dimensions) if dimensions else "service",
                "metrics": ",".join(metrics) if metrics else "total_amortized_cost"
            }
            
            if filters:
                params["filter"] = build_filter_string(filters)
            
            # Set headers
            headers = {}
            if export_format == "csv":
                headers["Accept"] = "text/csv"
            
            # Make request
            response = self._make_request(
                "GET",
                "/reporting/cost/run",
                params=params,
                headers=headers
            )
            
            # Handle response
            if export_format == "csv":
                result_data = response.text
                return {
                    "success": True,
                    "report_type": "custom_export",
                    "start_date": start_date,
                    "end_date": end_date,
                    "filters": filters,
                    "dimensions": dimensions,
                    "metrics": metrics,
                    "csv_data": result_data,
                    "export_format": export_format
                }
            else:
                data = response.json()
                result_data = data.get("result", [])
                
                return {
                    "success": True,
                    "report_type": "custom_export",
                    "start_date": start_date,
                    "end_date": end_date,
                    "filters": filters,
                    "dimensions": dimensions,
                    "metrics": metrics,
                    "total_records": len(result_data),
                    "data": result_data,
                    "export_format": export_format
                }
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to export cost report: {e}")
            error_detail = None
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                except:
                    error_detail = e.response.text[:500] if hasattr(e.response, 'text') else None
            return format_error_response(
                e,
                status_code=getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None,
                additional_info={"error_detail": error_detail}
            )

