"""
API client for Darkfield CLI
Production-ready implementation with API key authentication only
"""

import os
import requests
from typing import Dict, Any, Optional
import keyring
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from .config import DARKFIELD_API_URL, get_api_key, get_user_email
from .errors import NetworkError, RateLimitError, AuthenticationError

class DarkfieldClient:
    """Client for interacting with Darkfield API using API keys"""
    
    def __init__(self):
        self.base_url = DARKFIELD_API_URL
        
        # Get API key from environment or keyring
        self.api_key = get_api_key()
        
        # Base headers for all requests
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "darkfield-cli/1.0.0"
        }
        
        # Add authentication header if API key is available
        if self.api_key:
            # Use standard Bearer token format
            self.headers["Authorization"] = f"Bearer {self.api_key}"
    
    def _check_auth(self):
        """Check if client is authenticated"""
        if not self.api_key:
            raise AuthenticationError(
                "Not authenticated. Please run 'darkfield auth login' or set DARKFIELD_API_KEY environment variable."
            )
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((requests.ConnectionError, requests.Timeout))
    )
    def get(self, path: str, params: Optional[Dict] = None, auth_required: bool = True) -> Dict[str, Any]:
        """
        Make GET request to API
        
        Args:
            path: API endpoint path
            params: Query parameters
            auth_required: Whether authentication is required (default: True)
        """
        if auth_required:
            self._check_auth()
        
        try:
            response = requests.get(
                f"{self.base_url}{path}",
                headers=self.headers,
                params=params,
                timeout=10,
            )
            
            # Handle rate limiting
            if response.status_code == 429:
                retry_after = response.headers.get('Retry-After', '60')
                raise RateLimitError(f"Rate limit exceeded. Retry after {retry_after} seconds.")
            
            # Handle authentication errors
            if response.status_code == 401:
                raise AuthenticationError("Invalid or expired API key. Please run 'darkfield auth login'.")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.ConnectionError as e:
            raise NetworkError(f"Failed to connect to API: {e}")
        except requests.exceptions.HTTPError as e:
            if e.response is not None:
                if e.response.status_code == 404:
                    raise NetworkError(f"Endpoint {path} not found.")
                elif e.response.status_code == 403:
                    raise AuthenticationError("Access denied. Your API key may not have permission for this resource.")
            raise
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((requests.ConnectionError, requests.Timeout))
    )
    def post(self, path: str, json: Optional[Dict[str, Any]] = None, params: Optional[Dict[str, Any]] = None, auth_required: bool = True) -> Dict[str, Any]:
        """
        Make POST request to API
        
        Args:
            path: API endpoint path
            json: Request body
            params: Query parameters
            auth_required: Whether authentication is required (default: True)
        """
        if auth_required:
            self._check_auth()
        
        try:
            response = requests.post(
                f"{self.base_url}{path}",
                headers=self.headers,
                json=json,
                params=params,
                timeout=30,
            )
            
            # Handle rate limiting
            if response.status_code == 429:
                retry_after = response.headers.get('Retry-After', '60')
                raise RateLimitError(f"Rate limit exceeded. Retry after {retry_after} seconds.")
            
            # Handle authentication errors
            if response.status_code == 401:
                raise AuthenticationError("Invalid or expired API key. Please run 'darkfield auth login'.")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.ConnectionError as e:
            raise NetworkError(f"Failed to connect to API: {e}")
        except requests.exceptions.HTTPError as e:
            if e.response is not None:
                if e.response.status_code == 404:
                    raise NetworkError(f"Endpoint {path} not found.")
                elif e.response.status_code == 403:
                    raise AuthenticationError("Access denied. Your API key may not have permission for this resource.")
            raise
    
    def delete(self, path: str, auth_required: bool = True) -> None:
        """
        Make DELETE request to API
        
        Args:
            path: API endpoint path
            auth_required: Whether authentication is required (default: True)
        """
        if auth_required:
            self._check_auth()
        
        try:
            response = requests.delete(
                f"{self.base_url}{path}",
                headers=self.headers,
                timeout=15,
            )
            
            # Handle rate limiting
            if response.status_code == 429:
                retry_after = response.headers.get('Retry-After', '60')
                raise RateLimitError(f"Rate limit exceeded. Retry after {retry_after} seconds.")
            
            # Handle authentication errors
            if response.status_code == 401:
                raise AuthenticationError("Invalid or expired API key. Please run 'darkfield auth login'.")
            
            response.raise_for_status()
            
        except requests.exceptions.ConnectionError as e:
            raise NetworkError(f"Failed to connect to API: {e}")
        except requests.exceptions.HTTPError as e:
            if e.response is not None:
                if e.response.status_code == 404:
                    raise NetworkError(f"Endpoint {path} not found.")
                elif e.response.status_code == 403:
                    raise AuthenticationError("Access denied. Your API key may not have permission for this resource.")
            raise
    
    def get_usage_summary(self) -> Dict[str, Any]:
        """Get current month usage summary"""
        return self.get("/api/v1/billing/usage")
    
    def get_account_info(self) -> Dict[str, Any]:
        """Get account information including tier and limits"""
        return self.get("/api/v1/account/info")
    
    def check_health(self) -> Dict[str, Any]:
        """Check API health status (no auth required)"""
        return self.get("/health", auth_required=False)