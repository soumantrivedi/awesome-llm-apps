"""
Atlassian OAuth 2.0 Helper for Remote MCP Server
Handles OAuth flow for Atlassian Remote MCP Server (https://mcp.atlassian.com/v1/sse)
"""

import os
import json
import logging
import webbrowser
from typing import Dict, Optional
from urllib.parse import urlencode, parse_qs, urlparse

logger = logging.getLogger(__name__)

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False
    httpx = None
    logger.warning("httpx not available. Install: pip install httpx")


class AtlassianOAuthHelper:
    """Helper class for Atlassian OAuth 2.0 authentication"""
    
    # Official Atlassian OAuth endpoints
    AUTHORIZATION_URL = "https://auth.atlassian.com/authorize"
    TOKEN_URL = "https://auth.atlassian.com/oauth/token"
    MCP_ENDPOINT = "https://mcp.atlassian.com/v1/sse"
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str = "http://localhost:8080/callback"):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.scopes = [
            "read:jira-work",
            "write:jira-work",
            "read:confluence-content.all",
            "write:confluence-content.all",
            "read:confluence-space.summary"
        ]
    
    def get_authorization_url(self, state: Optional[str] = None) -> str:
        """
        Generate OAuth 2.0 authorization URL
        
        Args:
            state: Optional state parameter for CSRF protection
        
        Returns:
            Authorization URL
        """
        params = {
            "audience": "api.atlassian.com",
            "client_id": self.client_id,
            "scope": " ".join(self.scopes),
            "redirect_uri": self.redirect_uri,
            "state": state or "futuristic_pm",
            "response_type": "code",
            "prompt": "consent"
        }
        
        url = f"{self.AUTHORIZATION_URL}?{urlencode(params)}"
        return url
    
    def exchange_code_for_token(self, authorization_code: str) -> Dict:
        """
        Exchange authorization code for access token
        
        Args:
            authorization_code: Authorization code from OAuth callback
        
        Returns:
            Token response with access_token, refresh_token, etc.
        """
        if not HTTPX_AVAILABLE:
            raise ImportError("httpx required for OAuth token exchange")
        
        data = {
            "grant_type": "authorization_code",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": authorization_code,
            "redirect_uri": self.redirect_uri
        }
        
        try:
            response = httpx.post(self.TOKEN_URL, data=data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error exchanging code for token: {e}")
            raise
    
    def refresh_access_token(self, refresh_token: str) -> Dict:
        """
        Refresh access token using refresh token
        
        Args:
            refresh_token: Refresh token from previous OAuth flow
        
        Returns:
            New token response
        """
        if not HTTPX_AVAILABLE:
            raise ImportError("httpx required for token refresh")
        
        data = {
            "grant_type": "refresh_token",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": refresh_token
        }
        
        try:
            response = httpx.post(self.TOKEN_URL, data=data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error refreshing token: {e}")
            raise
    
    def get_mcp_connection_info(self, access_token: str, site_url: str) -> Dict:
        """
        Get MCP connection information for Atlassian Remote MCP Server
        
        Args:
            access_token: OAuth access token
            site_url: Atlassian site URL (e.g., "yourcompany.atlassian.net")
        
        Returns:
            MCP connection configuration
        """
        return {
            "type": "sse",
            "endpoint": self.MCP_ENDPOINT,
            "headers": {
                "Authorization": f"Bearer {access_token}",
                "X-Atlassian-Site": site_url
            },
            "site_url": site_url
        }


def initiate_oauth_flow(client_id: str, client_secret: str) -> Dict:
    """
    Initiate OAuth 2.0 flow for Atlassian
    
    This is a helper function that can be called from Streamlit UI
    
    Args:
        client_id: OAuth client ID
        client_secret: OAuth client secret
    
    Returns:
        Authorization URL and instructions
    """
    helper = AtlassianOAuthHelper(client_id, client_secret)
    auth_url = helper.get_authorization_url()
    
    return {
        "authorization_url": auth_url,
        "instructions": """
        1. Click the authorization URL to open Atlassian login
        2. Log in and authorize the application
        3. You will be redirected to a callback URL
        4. Copy the authorization code from the callback URL
        5. Enter the code in the application to complete authentication
        """
    }

