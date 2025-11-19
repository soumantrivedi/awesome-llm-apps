"""
Authentication handling for Cloudability API
Supports both Basic and Bearer token authentication
"""

from typing import Optional
from requests.auth import HTTPBasicAuth, AuthBase
import requests
from .config import Config


class BearerAuth(AuthBase):
    """Bearer token authentication"""
    
    def __init__(self, token: str):
        self.token = token
    
    def __call__(self, r: requests.Request) -> requests.Request:
        r.headers["Authorization"] = f"Bearer {self.token}"
        return r


class CloudabilityAuth:
    """Authentication manager for Cloudability API"""
    
    def __init__(
        self, 
        api_key: Optional[str] = None,
        auth_type: Optional[str] = None
    ):
        """
        Initialize authentication
        
        Args:
            api_key: API key or token
            auth_type: 'basic' or 'bearer' (defaults to Config.AUTH_TYPE)
        """
        self.api_key = api_key or Config.API_KEY
        self.auth_type = auth_type or Config.AUTH_TYPE
        
        if not self.api_key:
            raise ValueError("API key is required")
        
        self._auth = self._create_auth()
    
    def _create_auth(self) -> AuthBase:
        """Create appropriate auth object"""
        if self.auth_type.lower() == "bearer":
            return BearerAuth(self.api_key)
        else:
            # Basic auth: username=api_key, password=''
            return HTTPBasicAuth(self.api_key, '')
    
    @property
    def auth(self) -> AuthBase:
        """Get authentication object"""
        return self._auth
    
    def get_headers(self) -> dict:
        """Get default headers"""
        headers = {"Accept": "application/json"}
        if self.auth_type.lower() == "bearer":
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

