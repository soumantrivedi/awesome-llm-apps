"""
API Discovery Module
Attempts to discover valid dimensions/metrics and endpoint patterns
"""

import logging
import requests
from typing import Dict, List, Optional, Set
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class APIDiscovery:
    """Discover valid API parameters through testing"""
    
    # Common dimension names to try (based on cloud cost reporting patterns)
    COMMON_DIMENSIONS = [
        "vendor",
        "service_name", 
        "service",
        "account",
        "account_id",
        "region",
        "product",
        "product_id",
        "resource_id",
        "usage_type",
        "operation",
        "availability_zone",
    ]
    
    # Common metric names to try (based on Cloudability API v3 documentation)
    COMMON_METRICS = [
        "total_amortized_cost",  # Recommended per API documentation
        "amortized_cost",
        "total_cost",
        "cost",
        "unblended_cost",
        "blended_cost",
        "usage",
        "usage_quantity",
        "usage_hours",
    ]
    
    def __init__(self, api_client):
        """Initialize discovery with API client"""
        self.api_client = api_client
        self.valid_dimensions: Set[str] = set()
        self.valid_metrics: Set[str] = set()
        self.discovered = False
    
    def discover_valid_parameters(self) -> Dict[str, List[str]]:
        """
        Attempt to discover valid dimensions and metrics
        
        Returns:
            Dictionary with 'dimensions' and 'metrics' lists
        """
        if self.discovered:
            return {
                "dimensions": list(self.valid_dimensions),
                "metrics": list(self.valid_metrics)
            }
        
        logger.info("Starting API parameter discovery...")
        
        # Try combinations to find what works
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        
        # Test dimension/metric combinations
        for dim in self.COMMON_DIMENSIONS[:5]:  # Limit to avoid too many requests
            for metric in self.COMMON_METRICS[:3]:
                try:
                    params = {
                        "start": start_date,
                        "end": end_date,
                        "dimensions": dim,
                        "metrics": metric
                    }
                    
                    response = self.api_client._make_request(
                        "GET",
                        "/reporting/cost/run",
                        params=params
                    )
                    
                    # If successful, record valid values
                    if response.status_code == 200:
                        self.valid_dimensions.add(dim)
                        self.valid_metrics.add(metric)
                        logger.info(f"✅ Discovered valid: dimension={dim}, metric={metric}")
                        break  # Found at least one working combination
                        
                except requests.exceptions.HTTPError as e:
                    # Check if it's a different error (not invalid dimension/metric)
                    if hasattr(e, 'response') and e.response is not None:
                        if e.response.status_code == 422:
                            error_text = str(e.response.text)
                            # If error doesn't mention invalid dimensions/metrics, might be valid
                            if "Invalid dimensions" not in error_text and "Invalid metrics" not in error_text:
                                self.valid_dimensions.add(dim)
                                self.valid_metrics.add(metric)
                                logger.info(f"⚠️  Possible valid: dimension={dim}, metric={metric} (different error)")
                    continue
                except Exception:
                    continue
        
        self.discovered = True
        
        result = {
            "dimensions": list(self.valid_dimensions) if self.valid_dimensions else self.COMMON_DIMENSIONS[:3],
            "metrics": list(self.valid_metrics) if self.valid_metrics else self.COMMON_METRICS[:2]
        }
        
        logger.info(f"Discovery complete. Found {len(self.valid_dimensions)} dimensions, {len(self.valid_metrics)} metrics")
        return result

