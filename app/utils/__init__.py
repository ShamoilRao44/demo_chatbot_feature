"""HTTP client for communicating with main backend"""
import httpx
from typing import Dict, Any, Optional
from app.config import get_settings

settings = get_settings()


class BackendClient:
    """Client for calling main restaurant backend APIs with authentication"""
    
    def __init__(self):
        self.base_url = settings.backend_url
        self.timeout = 30.0
        self._access_token: Optional[str] = None
    
    def set_access_token(self, token: str):
        """Set the access token for authenticated requests"""
        self._access_token = token
    
    def clear_access_token(self):
        """Clear the access token"""
        self._access_token = None
    
    def _get_headers(self) -> Dict[str, str]:
        """Build headers with authentication if token is set"""
        headers = {"Content-Type": "application/json"}
        if self._access_token:
            headers["Authorization"] = f"Bearer {self._access_token}"
        return headers
    
    async def call(
        self,
        endpoint: str,
        method: str = "POST",
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make HTTP call to main backend with authentication
        
        Args:
            endpoint: API endpoint (e.g., "/groups/create")
            method: HTTP method (GET, POST, PUT, DELETE)
            json_data: JSON body for POST/PUT
            params: Query parameters
            
        Returns:
            Response JSON
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            url = f"{self.base_url}{endpoint}"
            
            try:
                response = await client.request(
                    method=method,
                    url=url,
                    json=json_data,
                    params=params,
                    headers=self._get_headers()
                )
                response.raise_for_status()
                return response.json()
                
            except httpx.HTTPError as e:
                return {
                    "status": "error",
                    "msg": f"Backend API error: {str(e)}"
                }
            except Exception as e:
                return {
                    "status": "error",
                    "msg": f"Error calling backend: {str(e)}"
                }
    
    # Convenience methods for common operations
    
    async def get(self, endpoint: str, **params) -> Dict[str, Any]:
        """GET request with authentication"""
        return await self.call(endpoint, "GET", params=params)
    
    async def post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """POST request with authentication"""
        return await self.call(endpoint, "POST", json_data=data)
    
    async def put(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """PUT request with authentication"""
        return await self.call(endpoint, "PUT", json_data=data)
    
    async def delete(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """DELETE request with authentication"""
        return await self.call(endpoint, "DELETE", json_data=data)


# Global backend client instance
backend_client = BackendClient()


# ============================================================================
# Re-export utility functions
# ============================================================================

def format_price(cents: int) -> str:
    """
    Format price in cents to dollar string
    
    Args:
        cents: Price in cents
        
    Returns:
        Formatted price string (e.g., "$12.99")
    """
    dollars = cents / 100
    return f"${dollars:.2f}"


def parse_price(price_str: str) -> Optional[int]:
    """
    Parse price string to cents
    
    Args:
        price_str: Price string (e.g., "$12.99" or "12.99")
        
    Returns:
        Price in cents or None if invalid
    """
    try:
        # Remove $ and whitespace
        clean = price_str.strip().replace("$", "")
        # Convert to float then to cents
        dollars = float(clean)
        return int(dollars * 100)
    except (ValueError, AttributeError):
        return None


def format_business_hours(hours: Dict[str, str]) -> str:
    """
    Format business hours dict to readable string
    
    Args:
        hours: Dict with day: hours mapping
        
    Returns:
        Formatted string
    """
    if not hours:
        return "Not set"
    
    days_order = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    lines = []
    for day in days_order:
        if day in hours:
            lines.append(f"{day.capitalize()}: {hours[day]}")
    
    return "\n".join(lines) if lines else "Not set"


def validate_business_hours_format(hours_str: str) -> bool:
    """
    Validate business hours format (e.g., "9:00-17:00")
    
    Args:
        hours_str: Hours string to validate
        
    Returns:
        True if valid format
    """
    try:
        if "-" not in hours_str:
            return False
        start, end = hours_str.split("-")
        # Basic validation of time format
        for time in [start.strip(), end.strip()]:
            parts = time.split(":")
            if len(parts) != 2:
                return False
            hour, minute = int(parts[0]), int(parts[1])
            if not (0 <= hour < 24 and 0 <= minute < 60):
                return False
        return True
    except (ValueError, AttributeError):
        return False