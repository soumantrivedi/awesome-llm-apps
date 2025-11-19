"""
Comprehensive Cost Reporting Tool
Supports view-based reports with multiple filters, formats, and report types
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
from ..framework.tool_base import get_registry
from .base_tool import CloudabilityTool
from ..utils import data_to_csv_string, data_to_markdown_table, get_default_date_range

logger = logging.getLogger(__name__)

registry = get_registry()


class GenerateCostReportTool(CloudabilityTool):
    """
    Generate comprehensive cost reports with view restrictions, filters, and multiple export formats.
    Supports amortized costs, condensed/detailed reports, and flexible time ranges.
    """
    
    def get_name(self) -> str:
        return "generate_cost_report"
    
    def get_description(self) -> str:
        return """Generate comprehensive amortized cost reports for a given view with flexible filtering.
        
Supports:
- Filtering by: AWS account (account_id), K8s cluster name (cluster_name), K8s namespace, K8s product_id
- Export formats: JSON, CSV, Markdown (with tables)
- Report types: Condensed (all namespaces summary) or Detailed (specific namespace/filters)
- Time ranges: Last 1 month, given month (YYYY-MM), or custom date range (YYYY-MM-DD to YYYY-MM-DD)
- Always uses amortized costs"""
    
    def get_input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "view_name": {
                    "type": "string",
                    "description": "Name of the dashboard view to restrict data to (required)"
                },
                "report_type": {
                    "type": "string",
                    "enum": ["condensed", "detailed"],
                    "description": "Report type: 'condensed' for all namespaces summary, 'detailed' for specific namespace/filters breakdown",
                    "default": "condensed"
                },
                "time_range": {
                    "type": "string",
                    "description": "Time range: 'last_month' for last 30 days, 'YYYY-MM' for specific month, or 'YYYY-MM-DD,YYYY-MM-DD' for custom range",
                    "default": "last_month"
                },
                "account_id": {
                    "type": "string",
                    "description": "Optional: Filter by AWS account ID"
                },
                "cluster_name": {
                    "type": "string",
                    "description": "Optional: Filter by Kubernetes cluster name (supports wildcards like 'prod*')"
                },
                "namespace": {
                    "type": "string",
                    "description": "Optional: Filter by Kubernetes namespace (supports wildcards like 'ici*'). Required for detailed reports."
                },
                "product_id": {
                    "type": "string",
                    "description": "Optional: Filter by product ID (e.g., 'K8s' for Kubernetes)"
                },
                "export_format": {
                    "type": "string",
                    "enum": ["json", "csv", "markdown"],
                    "description": "Export format: json, csv, or markdown (with tables)",
                    "default": "json"
                },
                "granularity": {
                    "type": "string",
                    "enum": ["daily", "monthly"],
                    "description": "Time granularity: daily or monthly",
                    "default": "daily"
                },
                "dimensions": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Optional: Custom dimensions to group by (overrides automatic dimension selection). Examples: lease_type, enhanced_service_name, transaction_type, usage_family, namespace, cluster_name, account_id, vendor, service"
                }
            },
            "required": ["view_name"]
        }
    
    def _parse_time_range(self, time_range: str) -> Tuple[str, str]:
        """
        Parse time range string into start_date and end_date
        
        Args:
            time_range: 'last_month', 'YYYY-MM', or 'YYYY-MM-DD,YYYY-MM-DD'
        
        Returns:
            Tuple of (start_date, end_date) in YYYY-MM-DD format
        """
        if time_range == "last_month":
            # Last 30 days
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")
        elif ',' in time_range:
            # Custom range: YYYY-MM-DD,YYYY-MM-DD
            parts = time_range.split(',')
            if len(parts) == 2:
                return parts[0].strip(), parts[1].strip()
            else:
                raise ValueError(f"Invalid time range format: {time_range}. Expected 'YYYY-MM-DD,YYYY-MM-DD'")
        elif len(time_range) == 7 and time_range[4] == '-':
            # Specific month: YYYY-MM
            year, month = map(int, time_range.split('-'))
            start_date = datetime(year, month, 1)
            # Get last day of month
            if month == 12:
                end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
            else:
                end_date = datetime(year, month + 1, 1) - timedelta(days=1)
            return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")
        else:
            raise ValueError(f"Invalid time range format: {time_range}")
    
    def _build_filters(self, account_id: Optional[str] = None,
                      cluster_name: Optional[str] = None,
                      namespace: Optional[str] = None,
                      product_id: Optional[str] = None) -> Dict[str, str]:
        """
        Build filters dictionary from individual filter parameters
        
        Returns:
            Dictionary of filters
        """
        filters = {}
        if account_id:
            filters["account_id"] = account_id
        if cluster_name:
            filters["cluster_name"] = cluster_name
        if namespace:
            filters["namespace"] = namespace
        if product_id:
            filters["product_id"] = product_id
        return filters
    
    def _determine_dimensions(self, report_type: str, filters: Dict[str, str]) -> List[str]:
        """
        Determine dimensions based on report type and filters
        Note: Amortized costs endpoint has limited dimension support.
        Uses vendor/service dimensions that are more universally supported.
        
        Args:
            report_type: 'condensed' or 'detailed'
            filters: Dictionary of active filters
        
        Returns:
            List of dimension names
        """
        # Use minimal dimensions that are most likely to work
        # When using views, the API has very limited dimension support
        # Start with just vendor as it's most universally supported
        dimensions = ["vendor"]
        
        # Note: Many dimensions (service, account_id, namespace, etc.) may not be
        # supported when using views. The API will reject invalid dimensions.
        # We'll let the API error handling deal with this.
        
        return dimensions
    
    async def execute(self, args: dict) -> dict:
        """
        Execute the comprehensive cost report generation
        """
        api = self.require_api_client()
        
        # Extract parameters
        view_name = args.get("view_name")
        report_type = args.get("report_type", "condensed")
        time_range = args.get("time_range", "last_month")
        account_id = args.get("account_id")
        cluster_name = args.get("cluster_name")
        namespace = args.get("namespace")
        product_id = args.get("product_id")
        export_format = args.get("export_format", "json")
        granularity = args.get("granularity", "daily")
        custom_dimensions = args.get("dimensions")
        
        # Validate detailed report requires namespace
        if report_type == "detailed" and not namespace:
            return {
                "success": False,
                "error": "Detailed reports require a namespace filter. Please specify 'namespace' parameter."
            }
        
        try:
            # Parse time range
            start_date, end_date = self._parse_time_range(time_range)
        except ValueError as e:
            return {
                "success": False,
                "error": f"Invalid time range: {str(e)}"
            }
        
        # Build filters
        # Note: When using views, some filters may not be supported
        # The API will reject invalid filters, and we'll handle that in error handling
        filters = self._build_filters(
            account_id=account_id,
            cluster_name=cluster_name,
            namespace=namespace,
            product_id=product_id
        )
        
        # If using a view, some filters might not work
        # Try without filters first if they fail
        
        # Determine dimensions based on report type, or use custom dimensions if provided
        if custom_dimensions:
            dimensions = custom_dimensions
        else:
            dimensions = self._determine_dimensions(report_type, filters)
        
        # Log dimensions being used for debugging
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Using dimensions: {dimensions}")
        
        # Generate report using amortized costs
        # Try amortized costs first, fallback to container costs if namespace filtering fails
        result = api.get_amortized_costs(
            start_date=start_date,
            end_date=end_date,
            view_name=view_name,
            filters=filters if filters else None,
            dimensions=dimensions,
            granularity=granularity,
            export_format="json"  # Always get JSON first, then convert to requested format
        )
        
        # Store the dimensions we requested (before any API fallback)
        result["requested_dimensions"] = dimensions
        
        # If amortized costs fails, try with minimal dimensions first, then container costs
        if not result.get("success"):
            error_msg = result.get("error", "").lower()
            
            # First, try retrying with just vendor dimension if dimensions are invalid
            if "invalid dimensions" in error_msg and dimensions != ["vendor"]:
                logger.info("Retrying with minimal dimensions (vendor only)")
                result = api.get_amortized_costs(
                    start_date=start_date,
                    end_date=end_date,
                    view_name=view_name,
                    filters=filters if filters else None,
                    dimensions=["vendor"],  # Minimal dimension set
                    granularity=granularity,
                    export_format="json"
                )
            
            # If still failing, check if error is related to invalid dimensions or filters (common with K8s)
            if not result.get("success"):
                error_msg = result.get("error", "").lower()
                if any(keyword in error_msg for keyword in ["invalid dimensions", "invalid filters", "namespace", "cluster_name"]):
                    # Amortized costs endpoint doesn't support K8s-specific dimensions/filters
                    # Fallback to container costs which supports K8s dimensions
                    # Check if we have extended API client capabilities
                    if hasattr(api, 'get_container_costs'):
                        # Use K8s-compatible dimensions for container costs
                        container_dimensions = []
                        if "namespace" in filters or report_type == "condensed":
                            container_dimensions.append("namespace")
                        if "cluster_name" not in filters:
                            container_dimensions.append("cluster_name")
                        if not container_dimensions:
                            container_dimensions = ["namespace", "cluster_name"]
                        
                        # Try container costs as fallback
                        # Note: Container costs endpoint may not support view restrictions
                        # So we'll try without view first, but keep the filters
                        container_result = api.get_container_costs(
                            start_date=start_date,
                            end_date=end_date,
                            filters=filters if filters else None,
                            group_by=container_dimensions,
                            metrics=["total_cost"],  # Container costs uses total_cost, not amortized
                            export_format="json"
                        )
                        if container_result.get("success"):
                            result = container_result
                            result["warning"] = "Amortized costs endpoint doesn't support the requested K8s dimensions/filters. Showing total costs from container costs endpoint instead."
                            result["note"] = "For true amortized costs with K8s filtering, you may need to use a different view or remove K8s-specific filters."
                        else:
                            return {
                                "success": False,
                                "error": f"Amortized costs failed: {result.get('error')}. Container costs fallback also failed: {container_result.get('error')}",
                                "suggestion": "The amortized costs endpoint may not support K8s-specific filters. Try removing namespace/cluster filters or use a view that supports these filters."
                            }
                    else:
                        return {
                            "success": False,
                            "error": result.get("error"),
                            "suggestion": "K8s-specific dimensions/filters may not be supported for amortized costs. Try removing namespace/cluster filters or use container costs endpoint."
                        }
                else:
                    # Error is not related to K8s dimensions/filters, return the original error
                    return result
        
        # Extract data
        data = result.get("data", [])
        if isinstance(data, dict) and "result" in data:
            data = data["result"]
        elif not isinstance(data, list):
            data = []
        
        # Convert to requested format
        if export_format == "csv":
            csv_data = data_to_csv_string(data)
            result["csv_data"] = csv_data
            result["export_format"] = "csv"
        elif export_format == "markdown":
            # Generate markdown table
            report_title = f"Cost Report - {view_name}"
            if namespace:
                report_title += f" - {namespace}"
            if time_range != "last_month":
                report_title += f" ({time_range})"
            
            markdown_data = data_to_markdown_table(data, title=report_title)
            result["markdown_data"] = markdown_data
            result["export_format"] = "markdown"
        
        # Add metadata
        result["report_type"] = report_type
        result["time_range"] = time_range
        result["start_date"] = start_date
        result["end_date"] = end_date
        result["filters_applied"] = filters
        result["total_records"] = len(data)
        
        return result


# Register tool
registry.register(GenerateCostReportTool())

