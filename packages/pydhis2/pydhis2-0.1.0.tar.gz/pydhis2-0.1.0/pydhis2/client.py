"""
DHIS2 Client module for API interactions
"""

import requests
from typing import Dict, Any, Optional


class DHIS2Client:
    """
    A client for interacting with DHIS2 APIs
    """
    
    def __init__(self, base_url: str, username: str, password: str):
        """
        Initialize DHIS2 client
        
        Args:
            base_url: The base URL of the DHIS2 instance
            username: Username for authentication
            password: Password for authentication
        """
        self.base_url = base_url.rstrip('/')
        self.auth = (username, password)
        self.session = requests.Session()
        self.session.auth = self.auth
        
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make a GET request to DHIS2 API
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            
        Returns:
            JSON response data
        """
        url = f"{self.base_url}/api/{endpoint.lstrip('/')}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()
        
    def post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make a POST request to DHIS2 API
        
        Args:
            endpoint: API endpoint
            data: Request data
            
        Returns:
            JSON response data
        """
        url = f"{self.base_url}/api/{endpoint.lstrip('/')}"
        response = self.session.post(url, json=data)
        response.raise_for_status()
        return response.json()
