"""
API Parameter Validator
Validates parameters before making API calls to prevent 40x errors
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class APIParameterValidator:
    """Validates API parameters before making requests
    
    Based on IBM Cloudability API v3 documentation:
    https://www.ibm.com/docs/en/cloudability-commercial/cloudability-essentials/saas?topic=api-getting-started-cloudability-v3
    """
    
    # Valid dimensions based on Cloudability API v3 documentation
    # Core dimensions (always available)
    CORE_DIMENSIONS = [
        "vendor",           # Cloud provider (AWS, Azure, GCP)
        "service",          # Service name (e.g., AmazonEC2)
        "service_name",     # Alternative service name field
        "enhanced_service_name",  # Enhanced service name with details
        "account_id",       # Cloud account ID
        "region",           # Geographic region
        "date",             # Date dimension for time-series data
    ]
    
    # Resource-level dimensions
    RESOURCE_DIMENSIONS = [
        "resource_identifier",  # Unique resource ID
        "product_id",       # Product/service identifier
        "usage_type",       # Usage type classification
        "operation",        # Operation type
        "availability_zone", # Availability zone
    ]
    
    # Kubernetes/Container dimensions
    K8S_DIMENSIONS = [
        "cluster_name",     # Kubernetes cluster name
        "namespace",        # Kubernetes namespace
        "pod_name",         # Kubernetes pod name
        "container_name",   # Container name
    ]
    
    # Cost allocation dimensions
    COST_DIMENSIONS = [
        "lease_type",      # Lease type (On-Demand, Reserved, etc.)
        "transaction_type", # Transaction type
        "usage_family",    # Usage family classification
        "billing_period",  # Billing period
        "cost_category",   # Cost category
    ]
    
    # Combined list of all valid dimensions
    VALID_DIMENSIONS = (
        CORE_DIMENSIONS + 
        RESOURCE_DIMENSIONS + 
        K8S_DIMENSIONS + 
        COST_DIMENSIONS
    )
    
    # Valid metrics based on Cloudability API v3 documentation
    # Cost metrics
    COST_METRICS = [
        "cost",                    # Basic cost
        "total_cost",              # Total cost
        "unblended_cost",          # Unblended cost (raw cost)
        "blended_cost",            # Blended cost
        "amortized_cost",          # Amortized cost (single metric)
        "total_amortized_cost",    # Total amortized cost (recommended)
    ]
    
    # Usage metrics
    USAGE_METRICS = [
        "usage",                   # General usage
        "usage_quantity",          # Usage quantity
        "usage_hours",             # Usage hours
        "usage_amount",            # Usage amount
    ]
    
    # Combined list of all valid metrics
    VALID_METRICS = COST_METRICS + USAGE_METRICS
    
    # Valid filter operators per IBM Cloudability API v3 documentation
    # Reference: https://www.ibm.com/docs/en/cloudability-commercial/cloudability-essentials/saas?topic=api-getting-started-cloudability-v3
    VALID_FILTER_OPERATORS = [
        "==",    # Equals
        "!=",    # Does not equal
        ">",     # Greater than
        "<",     # Less than
        ">=",    # Greater than or equal to
        "<=",    # Less than or equal to
        "=@",    # Contains (for wildcard/pattern matching)
        "!=@",   # Does not contain
    ]
    
    @staticmethod
    def validate_date_range(start_date: Optional[str], end_date: Optional[str]) -> Tuple[bool, Optional[str]]:
        """Validate date range"""
        if not start_date or not end_date:
            return True, None
        
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            
            if start > end:
                return False, "Start date must be before end date"
            
            # Check if dates are too far in the future (allow up to 1 day for timezone differences)
            today = datetime.now()
            if end > today + timedelta(days=2):
                return False, "End date cannot be more than 1 day in the future"
            
            # Check if date range is too large (some APIs have limits)
            days_diff = (end - start).days
            if days_diff > 365:
                return False, "Date range cannot exceed 365 days"
            
            return True, None
        except ValueError:
            return False, "Invalid date format. Use YYYY-MM-DD"
    
    @staticmethod
    def validate_dimensions(dimensions: Optional[List[str]]) -> Tuple[bool, Optional[str], List[str]]:
        """Validate and filter dimensions
        
        Returns valid dimensions, warning about invalid ones but continuing with valid ones.
        Defaults to 'vendor' if none provided (more universal than 'service').
        """
        if not dimensions:
            return True, None, ["vendor"]  # Default dimension (more universal)
        
        valid_dims = []
        invalid_dims = []
        
        for dim in dimensions:
            # Check if dimension is valid or looks valid
            if dim in APIParameterValidator.VALID_DIMENSIONS:
                valid_dims.append(dim)
            elif any(valid in dim for valid in APIParameterValidator.VALID_DIMENSIONS):
                # Partial match (e.g., "cluster_name" contains "cluster")
                valid_dims.append(dim)
            else:
                invalid_dims.append(dim)
        
        if invalid_dims:
            logger.warning(f"Invalid dimensions: {invalid_dims}. Using only valid ones.")
        
        if not valid_dims:
            return False, "No valid dimensions provided", ["vendor"]
        
        return True, None, valid_dims
    
    @staticmethod
    def validate_metrics(metrics: Optional[List[str]]) -> Tuple[bool, Optional[str], str]:
        """Validate metrics
        
        Returns the first valid metric, or defaults to 'total_amortized_cost' 
        (recommended per API documentation).
        """
        if not metrics:
            return True, None, "total_amortized_cost"  # Default metric (recommended)
        
        # For single metric
        if isinstance(metrics, list) and len(metrics) == 1:
            metric = metrics[0]
            if metric in APIParameterValidator.VALID_METRICS:
                return True, None, metric
        
        # Try first metric
        metric = metrics[0] if metrics else "total_amortized_cost"
        # Validate it's in the list
        if metric not in APIParameterValidator.VALID_METRICS:
            logger.warning(f"Metric '{metric}' not in known valid metrics, but proceeding")
        return True, None, metric
    
    @staticmethod
    def validate_filters(filters: Optional[Dict[str, str]], dimensions: Optional[List[str]] = None) -> Tuple[bool, Optional[str], Optional[Dict[str, str]]]:
        """Validate filters"""
        if not filters:
            return True, None, None
        
        # Some filter combinations may not work with certain dimensions
        # For now, just validate filter keys are reasonable
        valid_filters = {}
        for key, value in filters.items():
            if key and value:
                valid_filters[key] = value
        
        return True, None, valid_filters if valid_filters else None
    
    @staticmethod
    def validate_view_parameters(view_name: Optional[str], filters: Optional[Dict] = None) -> Tuple[bool, Optional[str]]:
        """Validate view-related parameters"""
        # API supports filters with views - they can be combined
        # Views provide base filtering, additional filters refine the results
        return True, None
    
    @staticmethod
    def validate_amortized_costs_params(
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        filters: Optional[Dict[str, str]] = None,
        dimensions: Optional[List[str]] = None,
        view_name: Optional[str] = None,
        granularity: str = "monthly"
    ) -> Tuple[bool, Optional[str], Dict]:
        """Validate parameters for get_amortized_costs"""
        errors = []
        validated_params = {}
        
        # Validate dates
        if start_date and end_date:
            valid, error = APIParameterValidator.validate_date_range(start_date, end_date)
            if not valid:
                errors.append(error)
            else:
                validated_params["start_date"] = start_date
                validated_params["end_date"] = end_date
        
        # Validate dimensions
        valid, error, valid_dims = APIParameterValidator.validate_dimensions(dimensions)
        if not valid:
            errors.append(error)
        validated_params["dimensions"] = valid_dims
        
        # Validate view vs filters
        if view_name:
            valid, warning = APIParameterValidator.validate_view_parameters(view_name, filters)
            if warning:
                logger.warning(warning)
            validated_params["view_name"] = view_name
            # Filters CAN be combined with views in Cloudability API v3
            # Validate filters even when view is specified
            valid, error, valid_filters = APIParameterValidator.validate_filters(filters, valid_dims)
            if not valid:
                errors.append(error)
            validated_params["filters"] = valid_filters
        else:
            # Validate filters
            valid, error, valid_filters = APIParameterValidator.validate_filters(filters, valid_dims)
            if not valid:
                errors.append(error)
            validated_params["filters"] = valid_filters
        
        # Validate granularity
        if granularity not in ["daily", "monthly"]:
            errors.append(f"Invalid granularity: {granularity}. Must be 'daily' or 'monthly'")
        validated_params["granularity"] = granularity
        
        if errors:
            return False, "; ".join(errors), validated_params
        
        return True, None, validated_params

