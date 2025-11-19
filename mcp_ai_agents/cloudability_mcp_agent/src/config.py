"""
Configuration management for Cloudability MCP Server
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Configuration class for Cloudability MCP Server"""
    
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
    AUTH_TYPE: str = os.getenv("CLOUDABILITY_AUTH_TYPE", "basic")  # basic or bearer
    
    # Default values
    DEFAULT_LIMIT: int = 50
    MAX_LIMIT: int = 250
    DEFAULT_TIMEOUT: int = 30
    
    # MCP Protocol
    MCP_VERSION: str = "2024-11-05"
    
    @classmethod
    def validate(cls) -> None:
        """Validate configuration"""
        if not cls.API_KEY:
            raise ValueError(
                "CLOUDABILITY_API_KEY environment variable is required. "
                "Set it in your .env file or environment."
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

