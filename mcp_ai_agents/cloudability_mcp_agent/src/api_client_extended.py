"""
Extended Cloudability API Client
Comprehensive API methods covering 80% of Cloudability features
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import requests

from .api_client import CloudabilityAPIClient
from .utils import (
    build_filter_string,
    get_default_date_range,
    format_error_response,
)

logger = logging.getLogger(__name__)


class ExtendedCloudabilityAPIClient(CloudabilityAPIClient):
    """
    Extended API client with comprehensive Cloudability features
    Inherits from base CloudabilityAPIClient
    """
    
    # ========== Container/Kubernetes Operations ==========
    
    def get_container_costs(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        filters: Optional[Dict[str, str]] = None,
        group_by: Optional[List[str]] = None,
        metrics: Optional[List[str]] = None,
        export_format: str = "json"
    ) -> Dict:
        """Get container/Kubernetes cost breakdown"""
        try:
            if not end_date:
                end_date = datetime.now().strftime("%Y-%m-%d")
            if not start_date:
                start_date, _ = get_default_date_range(30)
            
            dimension_map = {
                "cluster": "cluster_name",
                "namespace": "namespace",
                "pod": "pod_name",
                "container": "container_name",
                "service": "service_name"
            }
            
            dimensions = [dimension_map.get(g, g) for g in (group_by or ["cluster", "namespace"])]
            
            params = {
                "start": start_date,
                "end": end_date,
                "dimensions": ",".join(dimensions),
                "metrics": ",".join(metrics) if metrics else "total_cost"
            }
            
            if filters:
                params["filter"] = build_filter_string(filters)
            else:
                params["filter"] = "product_id==K8s"
            
            headers = {"Accept": "text/csv"} if export_format == "csv" else {}
            
            response = self._make_request("GET", "/reporting/cost/run", params=params, headers=headers)
            
            if export_format == "csv":
                return {
                    "success": True,
                    "report_type": "container_costs",
                    "start_date": start_date,
                    "end_date": end_date,
                    "group_by": group_by,
                    "csv_data": response.text,
                    "export_format": export_format
                }
            else:
                data = response.json()
                return {
                    "success": True,
                    "report_type": "container_costs",
                    "start_date": start_date,
                    "end_date": end_date,
                    "group_by": group_by,
                    "total_records": len(data.get("result", [])),
                    "data": data.get("result", []),
                    "export_format": export_format
                }
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get container costs: {e}")
            return format_error_response(e, status_code=getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None)
    
    def get_container_resource_usage(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        filters: Optional[Dict[str, str]] = None,
        metrics: Optional[List[str]] = None
    ) -> Dict:
        """Get container resource usage metrics"""
        try:
            if not end_date:
                end_date = datetime.now().strftime("%Y-%m-%d")
            if not start_date:
                start_date, _ = get_default_date_range(30)
            
            params = {
                "start": start_date,
                "end": end_date,
                "metrics": ",".join(metrics) if metrics else "cpu/reserved,memory/reserved_rss"
            }
            
            if filters:
                params["filter"] = build_filter_string(filters)
            
            response = self._make_request("GET", "/reporting/cost/run", params=params)
            data = response.json()
            return {
                "success": True,
                "report_type": "container_resource_usage",
                "start_date": start_date,
                "end_date": end_date,
                "metrics": metrics,
                "data": data.get("result", [])
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get container resource usage: {e}")
            return format_error_response(e, status_code=getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None)
    
    # ========== Budget Operations ==========
    
    def list_budgets(self) -> Dict:
        """List all budgets"""
        try:
            response = self._make_request("GET", "/budgets")
            data = response.json()
            return {"success": True, "budgets": data.get("result", []), "total": len(data.get("result", []))}
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to list budgets: {e}")
            return format_error_response(e, status_code=getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None)
    
    def get_budget(self, budget_id: str) -> Dict:
        """Get budget details"""
        try:
            response = self._make_request("GET", f"/budgets/{budget_id}")
            data = response.json()
            return {"success": True, "budget": data.get("result", data)}
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get budget: {e}")
            return format_error_response(e, status_code=getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None)
    
    def create_budget(self, name: str, basis: str, view_id: str, months: List[Dict[str, Any]]) -> Dict:
        """Create a new budget"""
        try:
            payload = {"name": name, "basis": basis, "view_id": view_id, "months": months}
            response = self._make_request("POST", "/budgets", json=payload)
            data = response.json()
            return {"success": True, "budget": data.get("result", data)}
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to create budget: {e}")
            return format_error_response(e, status_code=getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None)
    
    def update_budget(self, budget_id: str, months: Optional[List[Dict[str, Any]]] = None, name: Optional[str] = None) -> Dict:
        """Update budget"""
        try:
            payload = {}
            if months:
                payload["months"] = months
            if name:
                payload["name"] = name
            response = self._make_request("PUT", f"/budgets/{budget_id}", json=payload)
            data = response.json()
            return {"success": True, "budget": data.get("result", data)}
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to update budget: {e}")
            return format_error_response(e, status_code=getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None)
    
    # ========== Spending Forecasts & Estimates ==========
    
    def get_spending_estimate(self, view_id: str = "0", basis: str = "cash") -> Dict:
        """Get current month spending estimate"""
        try:
            params = {"view_id": view_id, "basis": basis}
            response = self._make_request("GET", "/forecast/estimate", params=params)
            data = response.json()
            return {"success": True, "estimate": data.get("result", data)}
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get spending estimate: {e}")
            return format_error_response(e, status_code=getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None)
    
    def get_spending_forecast(
        self,
        view_id: str = "0",
        basis: str = "cash",
        months_back: int = 6,
        months_forward: int = 12,
        use_current_estimate: bool = True,
        remove_one_time_charges: bool = True
    ) -> Dict:
        """Get spending forecast"""
        try:
            params = {
                "view_id": view_id,
                "basis": basis,
                "months_back": months_back,
                "months_forward": months_forward,
                "use_current_estimate": use_current_estimate,
                "remove_one_time_charges": remove_one_time_charges
            }
            response = self._make_request("GET", "/forecast/forecast", params=params)
            data = response.json()
            return {"success": True, "forecast": data.get("result", data)}
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get spending forecast: {e}")
            return format_error_response(e, status_code=getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None)
    
    # ========== Tag Explorer ==========
    
    def list_available_tags(self, limit: Optional[int] = None) -> Dict:
        """List available tag keys"""
        try:
            params = {"dimension_type": "tag"}
            if limit:
                params["limit"] = limit
            response = self._make_request("GET", "/reporting/dimensions", params=params)
            data = response.json()
            tag_keys = data.get("result", [])
            return {"success": True, "tag_keys": tag_keys, "total": len(tag_keys)}
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to list tags: {e}")
            return {"success": False, "error": str(e), "note": "Tag listing may require different API endpoint"}
    
    def explore_tags(
        self,
        tag_key: str,
        tag_value: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        additional_filters: Optional[Dict[str, str]] = None,
        export_format: str = "json"
    ) -> Dict:
        """Explore costs by tags"""
        try:
            if not end_date:
                end_date = datetime.now().strftime("%Y-%m-%d")
            if not start_date:
                start_date, _ = get_default_date_range(30)
            
            filters = {}
            if tag_value:
                filters[f"tag:{tag_key}"] = tag_value
            else:
                filters[f"tag:{tag_key}"] = "*"
            
            if additional_filters:
                filters.update(additional_filters)
            
            params = {
                "start": start_date,
                "end": end_date,
                "dimensions": f"tag:{tag_key},vendor,service",
                "metrics": "total_amortized_cost"
            }
            
            if filters:
                params["filter"] = build_filter_string(filters)
            
            headers = {"Accept": "text/csv"} if export_format == "csv" else {}
            response = self._make_request("GET", "/reporting/cost/run", params=params, headers=headers)
            
            if export_format == "csv":
                return {
                    "success": True,
                    "report_type": "tag_explorer",
                    "tag_key": tag_key,
                    "tag_value": tag_value,
                    "csv_data": response.text,
                    "export_format": export_format
                }
            else:
                data = response.json()
                return {
                    "success": True,
                    "report_type": "tag_explorer",
                    "tag_key": tag_key,
                    "tag_value": tag_value,
                    "total_records": len(data.get("result", [])),
                    "data": data.get("result", []),
                    "export_format": export_format
                }
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to explore tags: {e}")
            return format_error_response(e, status_code=getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None)
    
    # ========== Anomaly Detection ==========
    
    def get_anomaly_detection(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        filters: Optional[Dict[str, str]] = None,
        severity: str = "all",
        min_cost_change_percent: float = 10.0,
        export_format: str = "json"
    ) -> Dict:
        """Get cost anomaly detection results"""
        try:
            if not end_date:
                end_date = datetime.now().strftime("%Y-%m-%d")
            if not start_date:
                start_date, _ = get_default_date_range(30)
            
            params = {
                "start": start_date,
                "end": end_date,
                "dimensions": "vendor,service,account_id",
                "metrics": "total_amortized_cost",
                "anomaly_detection": "true",
                "min_change_percent": str(min_cost_change_percent)
            }
            
            if severity != "all":
                params["severity"] = severity
            
            if filters:
                params["filter"] = build_filter_string(filters)
            
            headers = {"Accept": "text/csv"} if export_format == "csv" else {}
            response = self._make_request("GET", "/reporting/cost/run", params=params, headers=headers)
            
            if export_format == "csv":
                return {
                    "success": True,
                    "report_type": "anomaly_detection",
                    "severity": severity,
                    "min_cost_change_percent": min_cost_change_percent,
                    "csv_data": response.text,
                    "export_format": export_format
                }
            else:
                data = response.json()
                anomalies = data.get("result", [])
                return {
                    "success": True,
                    "report_type": "anomaly_detection",
                    "severity": severity,
                    "min_cost_change_percent": min_cost_change_percent,
                    "total_anomalies": len(anomalies),
                    "data": anomalies,
                    "export_format": export_format
                }
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get anomaly detection: {e}")
            return format_error_response(e, status_code=getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None)
    
    # ========== Measure & Dimension Discovery ==========
    
    def get_available_measures(self) -> Dict:
        """Get available measures (metrics and dimensions)"""
        try:
            response = self._make_request("GET", "/reporting/measures")
            data = response.json()
            return {"success": True, "measures": data.get("result", data)}
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get available measures: {e}")
            return format_error_response(e, status_code=getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None)
    
    def get_filter_operators(self) -> Dict:
        """Get available filter operators"""
        try:
            response = self._make_request("GET", "/reporting/operators")
            data = response.json()
            return {"success": True, "operators": data.get("result", data)}
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get filter operators: {e}")
            return format_error_response(e, status_code=getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None)

