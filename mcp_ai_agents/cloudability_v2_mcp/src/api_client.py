"""
Cloudability API Client
Core business logic for interacting with Cloudability API
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import requests
from urllib.parse import urlencode, quote

from .config import Config
from .auth import CloudabilityAuth
from .utils import (
    build_filter_list,
    format_error_response,
)

logger = logging.getLogger(__name__)


class CloudabilityAPIClient:
    """Client for interacting with Cloudability API"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        auth_type: Optional[str] = None,
        public_key: Optional[str] = None,
        private_key: Optional[str] = None,
        environment_id: Optional[str] = None,
        frontdoor_url: Optional[str] = None
    ):
        """
        Initialize API client
        
        Args:
            api_key: API key or token (for basic/bearer auth)
            base_url: Base URL for API
            auth_type: 'basic', 'bearer', or 'opentoken'
            public_key: Public key (keyAccess) for Enhanced Access Administration
            private_key: Private key (keySecret) for Enhanced Access Administration
            environment_id: Environment ID for OpenToken auth
            frontdoor_url: Frontdoor URL for key pair authentication
        """
        self.config = Config
        self.config.validate()
        
        self.api_key = api_key or self.config.API_KEY
        self.base_url = (base_url or self.config.BASE_URL).rstrip('/')
        self.auth_type = auth_type or self.config.AUTH_TYPE
        self.public_key = public_key or self.config.PUBLIC_KEY
        self.private_key = private_key or self.config.PRIVATE_KEY
        self.environment_id = environment_id or self.config.ENVIRONMENT_ID
        self.frontdoor_url = frontdoor_url or self.config.FRONTDOOR_URL
        
        self.auth_manager = CloudabilityAuth(
            api_key=self.api_key,
            auth_type=self.auth_type,
            public_key=self.public_key,
            private_key=self.private_key,
            environment_id=self.environment_id,
            frontdoor_url=self.frontdoor_url
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
        
        # Handle filters list specially to ensure multiple filters= parameters
        # Cloudability API requires multiple filters= query parameters, not comma-separated
        filter_list = None
        other_params = {}
        if params:
            for key, value in params.items():
                if key == "filters" and isinstance(value, list):
                    filter_list = value
                elif value is not None:
                    other_params[key] = value
        
        # Build query string: first other params, then multiple filters=
        query_parts = []
        if other_params:
            query_parts.append(urlencode(other_params))
        
        if filter_list:
            # Manually add each filter as separate filters= parameter
            for f in filter_list:
                query_parts.append(f"filters={quote(f, safe='=')}")
        
        if query_parts:
            query_string = "&".join(query_parts)
            url = f"{url}?{query_string}"
            params = None  # Don't pass params since we built query string manually
        
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
        List all views
        
        Args:
            limit: Maximum views to return
            offset: Pagination offset
            
        Returns:
            Views data
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
            
            return {
                "success": True,
                "total_views": len(views),
                "views": views,
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
        Get view by name (searches in view list)
        
        Args:
            view_name: Name of the view to find
            
        Returns:
            View dictionary if found, None otherwise
        """
        try:
            # Get all views (with reasonable limit)
            views_result = self.list_views(limit=250)
            if not views_result.get("success"):
                return None
            
            views = views_result.get("views", [])
            for view in views:
                # Check multiple possible name fields
                if (view.get("title") == view_name or
                    view.get("name") == view_name or
                    view.get("displayName") == view_name or
                    str(view.get("id")) == view_name):
                    return view
            return None
        except Exception as e:
            logger.error(f"Failed to get view by name: {e}")
            return None
    
    # ========== Budget Operations ==========
    
    def list_budgets(self) -> Dict:
        """
        List all budgets
        
        Returns:
            Budgets data
        """
        try:
            response = self._make_request("GET", "/budgets")
            data = response.json()
            
            budgets = data.get("result", [])
            
            return {
                "success": True,
                "total_budgets": len(budgets),
                "budgets": budgets,
                "raw_data": data
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to list budgets: {e}")
            return format_error_response(
                e,
                status_code=getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None
            )
    
    # ========== Cost Report Operations ==========
    
    def get_amortized_costs(
        self,
        start_date: str,
        end_date: str,
        dimensions: Optional[List[str]] = None,
        metrics: Optional[List[str]] = None,
        filters: Optional[Dict[str, str]] = None,
        view_name: Optional[str] = None,
        granularity: str = "monthly",
        export_format: str = "json"
    ) -> Dict:
        """
        Get amortized cost data from TrueCost Explorer
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            dimensions: Dimensions to group by (must be from VALID_AMORTIZED_DIMENSIONS)
            metrics: Metrics to retrieve (defaults to total_amortized_cost)
            filters: Filter conditions
            view_name: Optional view name to restrict data
            granularity: Time granularity ('daily' or 'monthly')
            export_format: Export format ('json' or 'csv')
            
        Returns:
            Amortized cost data
        """
        try:
            # Validate dimensions
            if dimensions:
                invalid_dims = [d for d in dimensions if d not in self.config.VALID_AMORTIZED_DIMENSIONS]
                if invalid_dims:
                    return {
                        "success": False,
                        "error": f"Invalid dimensions for amortized costs: {invalid_dims}. "
                                f"Valid dimensions: {self.config.VALID_AMORTIZED_DIMENSIONS}"
                    }
            
            # Build parameters
            params = {
                "start_date": start_date,
                "end_date": end_date,
                "granularity": granularity
            }
            
            # Add dimensions
            if dimensions:
                params["dimensions"] = ",".join(dimensions)
            else:
                # Default to vendor if no dimensions specified
                params["dimensions"] = "vendor"
            
            # Add metrics
            if metrics:
                params["metrics"] = ",".join(metrics)
            else:
                params["metrics"] = "total_amortized_cost"
            
            # Add filters
            if filters:
                params["filters"] = build_filter_list(filters)
            
            # Add view restriction if provided
            if view_name:
                # Look up view by name to get view ID
                view = self.get_view_by_name(view_name)
                if view:
                    # Use view ID (preferred) or view name
                    view_id = view.get("id") or view.get("view_id") or view_name
                    params["view"] = str(view_id)
                else:
                    # If view not found, try using the name directly
                    # API might accept view name or ID
                    params["view"] = view_name
                    logger.warning(f"View '{view_name}' not found in view list, using name directly")
            
            # Set headers for CSV export
            headers = {}
            if export_format == "csv":
                headers["Accept"] = "text/csv"
            
            response = self._make_request(
                "GET",
                "/reporting/cost/run",
                params=params,
                headers=headers
            )
            
            if export_format == "csv":
                csv_data = response.text
                return {
                    "success": True,
                    "report_type": "amortized_costs",
                    "start_date": start_date,
                    "end_date": end_date,
                    "dimensions": dimensions or ["vendor"],
                    "granularity": granularity,
                    "currency": "USD",
                    "csv_data": csv_data,
                    "export_format": "csv"
                }
            else:
                data = response.json()
                result_data = data.get("result", [])
                
                return {
                    "success": True,
                    "report_type": "amortized_costs",
                    "start_date": start_date,
                    "end_date": end_date,
                    "dimensions": dimensions or ["vendor"],
                    "granularity": granularity,
                    "currency": "USD",
                    "total_records": len(result_data),
                    "data": result_data,
                    "export_format": "json"
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get amortized costs: {e}")
            return format_error_response(
                e,
                status_code=getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None
            )

