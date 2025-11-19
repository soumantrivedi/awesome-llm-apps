"""
Authentication handling for Cloudability API
Supports Basic, Bearer token, and Enhanced Access Administration (public/private key) authentication
"""

from typing import Optional
from requests.auth import HTTPBasicAuth, AuthBase
import requests
import logging
from .config import Config

logger = logging.getLogger(__name__)


class BearerAuth(AuthBase):
    """Bearer token authentication"""
    
    def __init__(self, token: str):
        self.token = token
    
    def __call__(self, r: requests.Request) -> requests.Request:
        r.headers["Authorization"] = f"Bearer {self.token}"
        return r


class OpenTokenAuth(AuthBase):
    """Apptio OpenToken authentication with environment ID"""
    
    def __init__(self, token: str, environment_id: Optional[str] = None):
        self.token = token
        self.environment_id = environment_id
    
    def __call__(self, r: requests.Request) -> requests.Request:
        r.headers["apptio-opentoken"] = self.token
        if self.environment_id:
            r.headers["apptio-environmentid"] = self.environment_id
        return r


class CloudabilityAuth:
    """Authentication manager for Cloudability API"""
    
    def __init__(
        self, 
        api_key: Optional[str] = None,
        auth_type: Optional[str] = None,
        public_key: Optional[str] = None,
        private_key: Optional[str] = None,
        environment_id: Optional[str] = None,
        frontdoor_url: Optional[str] = None
    ):
        """
        Initialize authentication
        
        Args:
            api_key: API key for basic/bearer auth (legacy)
            auth_type: 'basic', 'bearer', or 'opentoken' (defaults to Config.AUTH_TYPE)
            public_key: Public key (keyAccess) for Enhanced Access Administration
            private_key: Private key (keySecret) for Enhanced Access Administration
            environment_id: Environment ID for OpenToken auth
            frontdoor_url: Frontdoor URL for key pair authentication (defaults to US)
        """
        self.auth_type = auth_type or Config.AUTH_TYPE
        
        # Enhanced Access Administration (public/private key pair)
        if public_key and private_key:
            self.public_key = public_key
            self.private_key = private_key
            self.environment_id = environment_id or Config.ENVIRONMENT_ID
            self.frontdoor_url = frontdoor_url or Config.FRONTDOOR_URL
            self.auth_type = "opentoken"
            self._opentoken = None
            self._auth = None  # Will be created after token exchange
        else:
            # Legacy authentication (API key)
            self.api_key = api_key or Config.API_KEY
            if not self.api_key:
                raise ValueError("API key is required for basic/bearer authentication")
            self._auth = self._create_auth()
    
    def _get_opentoken(self) -> str:
        """
        Authenticate with public/private key pair to get OpenToken
        
        Returns:
            OpenToken string
        """
        if self._opentoken:
            return self._opentoken
        
        try:
            # Authenticate to get OpenToken
            auth_url = f"{self.frontdoor_url}/service/apikeylogin"
            payload = {
                "keyAccess": self.public_key,
                "keySecret": self.private_key
            }
            
            response = requests.post(
                auth_url,
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                },
                timeout=30
            )
            response.raise_for_status()
            
            # Extract OpenToken from response headers
            self._opentoken = response.headers.get("apptio-opentoken")
            if not self._opentoken:
                # Try to get from response body if not in headers
                data = response.json()
                self._opentoken = data.get("apptio-opentoken") or data.get("token")
            
            if not self._opentoken:
                raise ValueError("OpenToken not found in authentication response")
            
            logger.info("Successfully authenticated with Enhanced Access Administration API")
            return self._opentoken
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to authenticate with key pair: {e}")
            raise ValueError(f"Authentication failed: {e}")
    
    def _create_auth(self) -> AuthBase:
        """Create appropriate auth object"""
        if self.auth_type.lower() == "opentoken":
            # Get OpenToken if using key pair authentication
            if self.public_key and self.private_key:
                token = self._get_opentoken()
                return OpenTokenAuth(token, self.environment_id)
            else:
                # Direct OpenToken provided
                return OpenTokenAuth(self.api_key, self.environment_id)
        elif self.auth_type.lower() == "bearer":
            return BearerAuth(self.api_key)
        else:
            # Basic auth: username=api_key, password=''
            return HTTPBasicAuth(self.api_key, '')
    
    @property
    def auth(self) -> AuthBase:
        """Get authentication object"""
        if self.auth_type.lower() == "opentoken" and not self._auth:
            # Lazy initialization for OpenToken auth
            self._auth = self._create_auth()
        return self._auth
    
    def get_headers(self) -> dict:
        """Get default headers"""
        headers = {"Accept": "application/json"}
        
        if self.auth_type.lower() == "opentoken":
            if self.public_key and self.private_key:
                token = self._get_opentoken()
                headers["apptio-opentoken"] = token
            else:
                headers["apptio-opentoken"] = self.api_key
            
            if self.environment_id:
                headers["apptio-environmentid"] = self.environment_id
        elif self.auth_type.lower() == "bearer":
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        return headers

