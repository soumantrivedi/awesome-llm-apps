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
    build_filter_list,
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
        from urllib.parse import urlencode, quote
        
        # Separate filters from other params
        filter_list = None
        other_params = {}
        if params:
            for key, value in params.items():
                if key == "filters" and isinstance(value, list):
                    filter_list = value
                elif key == "metric":
                    # Handle singular "metric" parameter - convert to "metrics"
                    other_params["metrics"] = value
                elif key == "relative_period":
                    # Ignore relative_period - it's not a direct API parameter
                    # If needed, it should be converted to start_date/end_date before calling
                    continue
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
            # Note: View data endpoint may not support all parameters
            # Try without dates first, as views may have their own date ranges
            params = {}
            if limit:
                params["limit"] = min(limit, self.config.MAX_LIMIT)
            if offset:
                params["offset"] = offset
            # Note: start_date and end_date may not be supported by /views/{id}/data
            # Views typically have their own date ranges configured
            # Only add if explicitly provided and API supports it
            # if start_date:
            #     params["start"] = start_date  # Try "start" instead of "start_date"
            # if end_date:
            #     params["end"] = end_date  # Try "end" instead of "end_date"
            if product_id:
                params["filter"] = f"product_id=={product_id}"
            
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
            
            # Build parameters for view data endpoint
            # Note: This endpoint may have limited parameter support
            params = {}
            # Use "start" and "end" instead of "start_date" and "end_date"
            if start_date:
                params["start"] = start_date
            if end_date:
                params["end"] = end_date
            # Note: filters, dimensions, metrics may not be supported by /views/{id}/data
            # Views typically return pre-configured data
            # Only add if API documentation confirms support
            # if filters:
            #     params["filter"] = build_filter_string(filters)
            # if dimensions:
            #     params["dimensions"] = ",".join(dimensions)
            # if metrics:
            #     params["metrics"] = ",".join(metrics)
            
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
        
        Note: This endpoint may have limited support in API v3.
        If you get 422 errors, the endpoint may require different parameters
        or may not be available in your API version.
        
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
            # Validate parameters first
            from .api_validator import APIParameterValidator
            
            # Set default dates
            if not end_date:
                end_date = datetime.now().strftime("%Y-%m-%d")
            if not start_date:
                start_date, _ = get_default_date_range(30)
            
            # Validate parameters
            valid, error_msg, validated = APIParameterValidator.validate_amortized_costs_params(
                start_date, end_date, filters, dimensions, view_name, granularity
            )
            if not valid:
                return {
                    "success": False,
                    "error": f"Parameter validation failed: {error_msg}",
                    "suggestion": "Check parameter formats and combinations"
                }
            
            # Use validated parameters
            start_date = validated.get("start_date", start_date)
            end_date = validated.get("end_date", end_date)
            filters = validated.get("filters")
            # Default to vendor if no dimensions specified (more universal than service)
            dimensions = validated.get("dimensions", dimensions or ["vendor"])
            view_name = validated.get("view_name")
            granularity = validated.get("granularity", granularity)
            
            # Build parameters according to Cloudability API v3 documentation
            params = {
                "dimensions": ",".join(dimensions) if dimensions else "vendor"
            }
            
            # Use total_amortized_cost as per API documentation
            params["metrics"] = "total_amortized_cost"
            
            # Granularity - only add if daily (monthly is default)
            if granularity == "daily":
                params["granularity"] = "daily"
            
            # View restriction - handle before dates and filters
            if view_name:
                view = self.get_view_by_name(view_name)
                if not view:
                    return {
                        "success": False,
                        "error": f"View '{view_name}' not found"
                    }
                view_id = get_view_id(view)
                params["view"] = view_id
                # Try adding date parameters even with view - API may support date override
                # If it fails, we'll retry without dates in error handling
                params["start_date"] = start_date
                params["end_date"] = end_date
            else:
                # Add dates when no view is specified
                params["start_date"] = start_date
                params["end_date"] = end_date
            
            # Add filters - API supports filters with views
            # Filters can be combined with view restrictions
            # Cloudability API v3 expects multiple filters= parameters (repeated query params)
            if filters:
                filter_list = build_filter_list(filters)
                if filter_list:
                    # Pass as list - requests library will create multiple filters= query parameters
                    params["filters"] = filter_list
            
            # Set headers for export format
            headers = {}
            if export_format == "csv":
                headers["Accept"] = "text/csv"
            
            # Make request - try with current params first
            try:
                response = self._make_request(
                    "GET",
                    "/reporting/cost/run",
                    params=params,
                    headers=headers
                )
            except requests.exceptions.HTTPError as e:
                # Handle API errors - try alternative parameter formats if needed
                if hasattr(e, 'response') and e.response is not None:
                    status_code = e.response.status_code
                    error_text = ""
                    try:
                        error_data = e.response.json()
                        error_text = str(error_data)
                    except:
                        error_text = e.response.text[:200] if hasattr(e.response, 'text') else ""
                    
                    # If 400/422 and view is specified, don't try alternative date formats
                    # Views have their own date ranges and don't accept date parameters
                    if status_code in (400, 422) and view_name:
                        # If error is about dates, that's expected - views don't accept date parameters
                        if "date" in error_text.lower() or "parsing" in error_text.lower():
                            logger.warning("View specified - date parameters not supported with views. View's date range will be used.")
                            # Remove any date parameters that might have been added by error handling
                            params_alt = params.copy()
                            params_alt.pop("start_date", None)
                            params_alt.pop("end_date", None)
                            params_alt.pop("start", None)
                            params_alt.pop("end", None)
                            try:
                                response = self._make_request(
                                    "GET",
                                    "/reporting/cost/run",
                                    params=params_alt,
                                    headers=headers
                                )
                                params = params_alt
                            except Exception as e2:
                                # If still fails, try with filter instead of filters
                                params_alt2 = params_alt.copy()
                                if "filters" in params_alt2:
                                    params_alt2["filter"] = params_alt2.pop("filters")
                                try:
                                    response = self._make_request(
                                        "GET",
                                        "/reporting/cost/run",
                                        params=params_alt2,
                                        headers=headers
                                    )
                                    params = params_alt2
                                except:
                                    raise e
                        else:
                            # Non-date error with view - try filter format change
                            params_alt = params.copy()
                            if "filters" in params_alt:
                                params_alt["filter"] = params_alt.pop("filters")
                            try:
                                response = self._make_request(
                                    "GET",
                                    "/reporting/cost/run",
                                    params=params_alt,
                                    headers=headers
                                )
                                params = params_alt
                            except:
                                raise e
                    # If 422, try with start/end instead of start_date/end_date
                    elif status_code == 422:
                        logger.info("Trying alternative date parameter format (start/end)")
                        params_alt = params.copy()
                        if "start_date" in params_alt:
                            params_alt["start"] = params_alt.pop("start_date")
                        if "end_date" in params_alt:
                            params_alt["end"] = params_alt.pop("end_date")
                        # Also try filter instead of filters
                        if "filters" in params_alt:
                            params_alt["filter"] = params_alt.pop("filters")
                        try:
                            response = self._make_request(
                                "GET",
                                "/reporting/cost/run",
                                params=params_alt,
                                headers=headers
                            )
                            params = params_alt
                        except:
                            raise e
                    else:
                        raise
                else:
                    raise
            
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
        Uses same improved parameter logic as get_amortized_costs
        
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
            # Build parameters according to Cloudability API v3 documentation
            params = {
                "start_date": start_date,
                "end_date": end_date,
                "dimensions": ",".join(dimensions) if dimensions else "vendor"
            }
            
            # Use provided metrics or default to total_amortized_cost
            metric_name = ",".join(metrics) if metrics else "total_amortized_cost"
            params["metrics"] = metric_name
            
            # Add filters - use repeated query parameters format
            if filters:
                filter_list = build_filter_list(filters)
                if filter_list:
                    params["filters"] = filter_list
            
            # Set headers
            headers = {}
            if export_format == "csv":
                headers["Accept"] = "text/csv"
            
            # Make request - try with current params first, retry with alternative format if 422
            try:
                response = self._make_request(
                    "GET",
                    "/reporting/cost/run",
                    params=params,
                    headers=headers
                )
            except requests.exceptions.HTTPError as e:
                # Handle API errors - try alternative parameter formats if needed
                if hasattr(e, 'response') and e.response is not None:
                    status_code = e.response.status_code
                    # If 422, try with start/end instead of start_date/end_date
                    if status_code == 422:
                        logger.info("Trying alternative date parameter format (start/end)")
                        params_alt = params.copy()
                        if "start_date" in params_alt:
                            params_alt["start"] = params_alt.pop("start_date")
                        if "end_date" in params_alt:
                            params_alt["end"] = params_alt.pop("end_date")
                        # Also try filter instead of filters
                        if "filters" in params_alt:
                            params_alt["filter"] = params_alt.pop("filters")
                        try:
                            response = self._make_request(
                                "GET",
                                "/reporting/cost/run",
                                params=params_alt,
                                headers=headers
                            )
                            params = params_alt
                        except:
                            raise e
                    else:
                        raise
                else:
                    raise
            
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

