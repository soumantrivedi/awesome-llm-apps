"""
Configuration management for Cloudability V2 MCP Server
"""

import os
import logging
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class Config:
    """Configuration class for Cloudability V2 MCP Server"""
    
    # API Configuration
    API_KEY: Optional[str] = os.getenv("CLOUDABILITY_API_KEY")
    BASE_URL: str = os.getenv(
        "CLOUDABILITY_BASE_URL", 
        "https://api.cloudability.com/v3"
    )
    
    # Regional endpoints
    EU_BASE_URL: str = "https://api-eu.cloudability.com/v3"
    APAC_BASE_URL: str = "https://api-au.cloudability.com/v3"
    ME_BASE_URL: str = "https://api-me.cloudability.com/v3"
    
    # Authentication
    AUTH_TYPE: str = os.getenv("CLOUDABILITY_AUTH_TYPE", "basic")  # basic, bearer, or opentoken
    
    # Enhanced Access Administration (public/private key pair)
    PUBLIC_KEY: Optional[str] = os.getenv("CLOUDABILITY_PUBLIC_KEY")  # keyAccess
    PRIVATE_KEY: Optional[str] = os.getenv("CLOUDABILITY_PRIVATE_KEY")  # keySecret
    ENVIRONMENT_ID: Optional[str] = os.getenv("CLOUDABILITY_ENVIRONMENT_ID")
    
    # Frontdoor URLs for key pair authentication
    FRONTDOOR_URL: str = os.getenv(
        "CLOUDABILITY_FRONTDOOR_URL",
        "https://frontdoor.apptio.com"
    )
    FRONTDOOR_EU_URL: str = "https://frontdoor-eu.apptio.com"
    FRONTDOOR_APAC_URL: str = "https://frontdoor-au.apptio.com"
    
    # Default values
    DEFAULT_LIMIT: int = 50
    MAX_LIMIT: int = 250
    DEFAULT_TIMEOUT: int = 30
    
    # MCP Protocol
    MCP_VERSION: str = "2024-11-05"
    
    # Valid dimensions for amortized costs (based on API documentation and testing)
    # IMPORTANT: Not all dimensions work with the amortized costs endpoint.
    # Only these "Core Dimensions" are supported by the /v3/reporting/cost/run endpoint
    # when using total_amortized_cost metric.
    # 
    # Dimensions that DO NOT work with amortized costs (will return 422 errors):
    # - cluster_name, namespace, pod_name, container_name (K8s dimensions)
    # - resource_identifier, usage_type, operation, availability_zone (resource dimensions)
    # - lease_type, transaction_type, usage_family, billing_period, cost_category (cost allocation)
    #
    # These dimensions may work with other metrics (like total_cost) but not with amortized costs.
    VALID_AMORTIZED_DIMENSIONS = [
        "vendor",                    # Cloud provider (AWS, Azure, GCP) - ✅ Works
        "service",                   # Service name (AmazonEC2, etc.) - ✅ Works
        "service_name",              # Alternative service name - ✅ Works
        "enhanced_service_name",     # Enhanced service name with details - ✅ Works
        "account_id",                # Cloud account identifier - ✅ Works
        "region",                    # Geographic region (us-east-1, etc.) - ✅ Works
        "date"                       # Date dimension for time-series - ✅ Works
    ]
    
    @classmethod
    def validate(cls) -> None:
        """Validate configuration"""
        # Check if using Enhanced Access Administration (public/private key)
        if cls.PUBLIC_KEY and cls.PRIVATE_KEY:
            if not cls.PUBLIC_KEY or not cls.PRIVATE_KEY:
                raise ValueError(
                    "Both CLOUDABILITY_PUBLIC_KEY and CLOUDABILITY_PRIVATE_KEY "
                    "are required for Enhanced Access Administration authentication."
                )
            # Environment ID is recommended but not always required
            if not cls.ENVIRONMENT_ID:
                logger.warning(
                    "CLOUDABILITY_ENVIRONMENT_ID not set. Some operations may require it."
                )
        # Otherwise, check for legacy API key
        elif not cls.API_KEY:
            raise ValueError(
                "Authentication credentials required. Set either:\n"
                "  - CLOUDABILITY_API_KEY (for basic/bearer auth), or\n"
                "  - CLOUDABILITY_PUBLIC_KEY and CLOUDABILITY_PRIVATE_KEY (for Enhanced Access Administration)"
            )
    
    @classmethod
    def get_base_url(cls, region: Optional[str] = None) -> str:
        """Get base URL for specified region"""
        if region:
            region_map = {
                "eu": cls.EU_BASE_URL,
                "apac": cls.APAC_BASE_URL,
                "au": cls.APAC_BASE_URL,
                "me": cls.ME_BASE_URL,
            }
            return region_map.get(region.lower(), cls.BASE_URL)
        return cls.BASE_URL

